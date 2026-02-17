"""Сервис для преобразования TSX/JSX файлов в HTML плагины.
Использует esbuild для компиляции TypeScript/JSX в JavaScript."""

from __future__ import annotations

import subprocess
import tempfile
import os
import re
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def _resolve_esbuild_path() -> str | None:
    """Находит бинарник esbuild без зависимости от npx."""
    backend_dir = Path(__file__).resolve().parents[2]
    project_dir = backend_dir.parent

    candidates = [
        backend_dir / "node_modules" / ".bin" / "esbuild",
        backend_dir / "node_modules" / "esbuild" / "bin" / "esbuild",
        project_dir / "node_modules" / ".bin" / "esbuild",
        project_dir / "node_modules" / "esbuild" / "bin" / "esbuild",
    ]

    if os.name == "nt":
        windows_candidates = [path.with_suffix(".cmd") for path in candidates]
        candidates = windows_candidates + candidates

    for candidate in candidates:
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)

    return shutil.which("esbuild")


def fix_invalid_function_syntax(tsx_code: str) -> str:
    """Исправляет неправильный синтаксис функций, сгенерированный AI.
    
    AI модели иногда генерируют невалидный синтаксис:
        ComponentName() { ... }
    
    Вместо правильного:
        function ComponentName() { ... }
    
    Эта функция автоматически исправляет такие ошибки.
    
    Args:
        tsx_code: Исходный TSX/JSX код
        
    Returns:
        Исправленный код
    """
    # Паттерн: в начале строки (с возможными пробелами) идёт имя функции,
    # потом круглые скобки, потом открывающая фигурная скобка
    # Но это НЕ внутри класса (не метод) и НЕ после "function" или "const" или "=>"
    
    # Разбиваем код на строки для анализа
    lines = tsx_code.split('\n')
    fixed_lines = []
    
    # Паттерн для невалидного синтаксиса (имя функции в начале строки)
    # Ищем: [пробелы]ИмяКомпонента([параметры]) {
    # Но НЕ если перед ним есть function, const, let, var, class, или это метод класса
    invalid_pattern = re.compile(
        r'^(\s*)([A-Z][a-zA-Z0-9_]*)\s*\(([^)]*)\)\s*\{',
        re.MULTILINE
    )
    
    # Проверяем каждую строку
    for i, line in enumerate(lines):
        match = invalid_pattern.match(line)
        if match:
            indent = match.group(1)
            func_name = match.group(2)
            params = match.group(3)
            
            # Проверяем, что это не метод класса (предыдущая строка не содержит class или {)
            # и что строка не начинается с ключевых слов
            prev_lines_text = '\n'.join(lines[max(0, i-5):i])
            
            # Проверяем контекст - если мы внутри класса, не трогаем
            # Подсчитываем баланс фигурных скобок
            open_braces = prev_lines_text.count('{') - prev_lines_text.count('}')
            
            # Если мы НЕ внутри класса (open_braces == 0 или строка на верхнем уровне),
            # и это выглядит как компонент React (начинается с заглавной)
            if open_braces == 0:
                # Это невалидный синтаксис на верхнем уровне - исправляем
                fixed_line = f"{indent}function {func_name}({params}) {{"
                fixed_lines.append(fixed_line)
                logger.info(f"Auto-fixed invalid syntax at line {i+1}: '{line.strip()}' -> '{fixed_line.strip()}'")
                continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def compile_with_esbuild(tsx_code: str) -> str:
    """Компилирует TSX/JSX код в JavaScript через esbuild.
    
    Убирает TypeScript синтаксис и компилирует JSX в React.createElement().
    
    Args:
        tsx_code: Исходный TSX/JSX код (с уже преобразованными импортами)
        
    Returns:
        Скомпилированный JavaScript код
        
    Raises:
        RuntimeError: Если компиляция не удалась
    """
    # Находим путь к esbuild без fallback на npx (он может отсутствовать в runtime)
    esbuild_path = _resolve_esbuild_path()
    if not esbuild_path:
        raise RuntimeError(
            "esbuild binary not found. Install Node dependencies "
            "(npm install in backend/ or project root) or add esbuild to PATH."
        )
    
    # Создаем временный файл с кодом
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tsx', delete=False, encoding='utf-8') as f:
        f.write(tsx_code)
        temp_file = f.name
    
    try:
        # Вызываем esbuild - только трансформация, без bundling
        cmd = [esbuild_path] + [
            temp_file,
            '--loader:.tsx=tsx',
            '--jsx=transform',
            '--jsx-factory=React.createElement',
            '--jsx-fragment=React.Fragment',
            '--target=es2020',
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"esbuild compilation failed: {result.stderr}")
        
        return result.stdout
        
    finally:
        # Удаляем временный файл
        try:
            os.unlink(temp_file)
        except:
            pass


def _normalize_default_export(code: str) -> tuple[str, str]:
    """Нормализует export default и возвращает имя компонента."""
    fallback_name = "App"

    # export default function Component() {}
    match = re.search(r'export\s+default\s+function\s+([A-Za-z_]\w*)', code)
    if match:
        component_name = match.group(1)
        code = re.sub(
            r'export\s+default\s+function\s+([A-Za-z_]\w*)',
            r'function \1',
            code,
            count=1
        )
        return code, component_name

    # export default class Component {}
    match = re.search(r'export\s+default\s+class\s+([A-Za-z_]\w*)', code)
    if match:
        component_name = match.group(1)
        code = re.sub(
            r'export\s+default\s+class\s+([A-Za-z_]\w*)',
            r'class \1',
            code,
            count=1
        )
        return code, component_name

    # export default Component;
    match = re.search(r'export\s+default\s+([A-Za-z_]\w*)\s*;?', code)
    if match:
        component_name = match.group(1)
        code = re.sub(
            r'export\s+default\s+([A-Za-z_]\w*)\s*;?',
            '',
            code,
            count=1
        )
        return code, component_name

    # export default function() {}
    if re.search(r'export\s+default\s+function\s*\(', code):
        code = re.sub(
            r'export\s+default\s+function\s*\(',
            f'function {fallback_name}(',
            code,
            count=1
        )
        return code, fallback_name

    # export default class {}
    if re.search(r'export\s+default\s+class\b', code):
        code = re.sub(
            r'export\s+default\s+class\b',
            f'class {fallback_name}',
            code,
            count=1
        )
        return code, fallback_name

    # export default <expression>
    if re.search(r'export\s+default\s+', code):
        code = re.sub(
            r'export\s+default\s+',
            f'const {fallback_name} = ',
            code,
            count=1
        )
        return code, fallback_name

    return code, fallback_name


def transform_tsx_to_html(tsx_code: str, plugin_name: str = "TSX Plugin") -> str:
    """Преобразует TSX/JSX код в HTML плагин с использованием esbuild.
    
    Args:
        tsx_code: Исходный TSX/JSX код
        plugin_name: Название плагина
        
    Returns:
        HTML код плагина
    """
    # Автоисправление неправильного синтаксиса функций (AI иногда генерирует невалидный код)
    tsx_code = fix_invalid_function_syntax(tsx_code)
    
    # Lucide icons wrapper - создает React компоненты из lucide UMD
    LUCIDE_WRAPPER = '''
      window.lucideReact = new Proxy({}, {
        get(_, name) {
          const toKebab = s => s.replace(/([A-Z])/g, '-$1').toLowerCase().replace(/^-/, '');
          return ({ size = 24, color, strokeWidth = 2, fill = 'none', className, ...props }) => {
            const ref = React.useRef();
            React.useEffect(() => {
              if (ref.current && lucide[toKebab(name)]) {
                ref.current.innerHTML = '';
                const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                const iconData = lucide[toKebab(name)];
                svg.setAttribute('width', size);
                svg.setAttribute('height', size);
                svg.setAttribute('viewBox', '0 0 24 24');
                svg.setAttribute('fill', fill);
                svg.setAttribute('stroke', color || 'currentColor');
                svg.setAttribute('stroke-width', strokeWidth);
                svg.setAttribute('stroke-linecap', 'round');
                svg.setAttribute('stroke-linejoin', 'round');
                if (className) svg.setAttribute('class', className);
                iconData[2].forEach(el => {
                  const node = document.createElementNS('http://www.w3.org/2000/svg', el[0]);
                  Object.entries(el[1] || {}).forEach(([k,v]) => node.setAttribute(k, v));
                  svg.appendChild(node);
                });
                ref.current.appendChild(svg);
              }
            }, [size, color, strokeWidth, fill, className]);
            return React.createElement('span', { ref, style: { display: 'inline-flex' }, ...props });
          };
        }
      });
    '''
    
    # Преобразуем импорты для работы с глобальными переменными (CDN)
    code = tsx_code
    
    # React импорты -> используем глобальный React
    code = re.sub(
        r'import\s+React\s*,?\s*\{([^}]*)\}\s*from\s*[\'"]react[\'"];?',
        lambda m: f'const {{{m.group(1)}}} = React;',
        code
    )
    code = re.sub(r'import\s+React\s+from\s*[\'"]react[\'"];?', '', code)
    code = re.sub(
        r'import\s*\{([^}]*)\}\s*from\s*[\'"]react[\'"];?',
        lambda m: f'const {{{m.group(1)}}} = React;',
        code
    )
    
    # lucide-react импорты -> используем наш wrapper
    code = re.sub(
        r'import\s*\{([^}]*)\}\s*from\s*[\'"]lucide-react[\'"];?',
        lambda m: f'const {{{m.group(1)}}} = window.lucideReact;',
        code
    )

    # Нормализуем export default и определяем имя компонента
    code, component_name = _normalize_default_export(code)
    
    # Логируем код перед компиляцией для отладки
    logger.info(f"Code before esbuild (first 500 chars): {code[:500]}")
    logger.info(f"Code before esbuild (lines 60-75): {chr(10).join(code.split(chr(10))[59:75])}")
    
    # Компилируем через esbuild (убирает TypeScript, компилирует JSX)
    try:
        js_code = compile_with_esbuild(code)
        logger.info(f"esbuild compilation successful: {len(js_code)} bytes")
    except Exception as e:
        # Fallback: если esbuild не сработал, логируем ошибку
        logger.error(f"esbuild compilation failed: {e}")
        raise RuntimeError(f"Failed to compile TSX: {e}")
    
    # Создаем HTML обертку
    # Теперь НЕ используем Babel в браузере - код уже скомпилирован esbuild!
    html_template = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{plugin_name}</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: system-ui, -apple-system, sans-serif;
        }}
        body.embed {{
            padding: 0;
            background: transparent;
        }}
    </style>
</head>
<body>
    <div id="root"></div>
    <script>{LUCIDE_WRAPPER}</script>
    <script>
        (function() {{
            const embedMode = /[?&]embed=1/i.test(window.location.search);
            if (embedMode) {{
                document.body.classList.add('embed');
            }}
            
            {js_code}
            
            // Рендерим компонент
            ReactDOM.createRoot(document.getElementById('root')).render(React.createElement({component_name}));
            
            // Отправляем INIT сообщение
            if (embedMode && window.parent) {{
                window.parent.postMessage({{ type: 'INIT', status: 'ready' }}, '*');
            }}
        }})();
    </script>
</body>
</html>'''
    
    return html_template


def _simple_hash(text: str) -> int:
    """Простая хеш-функция для генерации ID."""
    h = 0
    for char in text:
        h = (h * 31 + ord(char)) & 0xFFFFFFFF
    return abs(h) % 1000000

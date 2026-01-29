"""Сервис для преобразования TSX/JSX файлов в HTML плагины.
Использует esbuild для компиляции TypeScript/JSX в JavaScript."""

from __future__ import annotations

import subprocess
import tempfile
import os
import re
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


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
    # Находим путь к esbuild
    backend_dir = Path(__file__).parent.parent.parent
    esbuild_path = backend_dir / "node_modules" / ".bin" / "esbuild"
    
    if not esbuild_path.exists():
        # Попробуем глобальный esbuild через npx
        esbuild_path = "npx"
        esbuild_args = ["esbuild"]
    else:
        esbuild_args = []
    
    # Создаем временный файл с кодом
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tsx', delete=False, encoding='utf-8') as f:
        f.write(tsx_code)
        temp_file = f.name
    
    try:
        # Вызываем esbuild - только трансформация, без bundling
        cmd = [str(esbuild_path)] + esbuild_args + [
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


def transform_tsx_to_html(tsx_code: str, plugin_name: str = "TSX Plugin") -> str:
    """Преобразует TSX/JSX код в HTML плагин с использованием esbuild.
    
    Args:
        tsx_code: Исходный TSX/JSX код
        plugin_name: Название плагина
        
    Returns:
        HTML код плагина
    """
    # Извлекаем имя компонента
    export_match = re.search(r'export\s+default\s+(\w+)', tsx_code)
    component_name = export_match.group(1) if export_match else 'App'
    
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
    
    # Удаляем export default
    code = re.sub(r'export\s+default\s+\w+;?', '', code)
    
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

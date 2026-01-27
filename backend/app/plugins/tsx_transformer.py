"""Сервис для преобразования TSX файлов в HTML плагины.
Использует тот же подход, что и miniapp 2 для максимальной совместимости."""

from __future__ import annotations

import re
from pathlib import Path


def transform_tsx_to_html(tsx_code: str, plugin_name: str = "TSX Plugin") -> str:
    """Преобразует TSX код в HTML плагин, используя тот же подход, что и miniapp 2.
    
    Args:
        tsx_code: Исходный TSX код
        plugin_name: Название плагина
        
    Returns:
        HTML код плагина
    """
    # Извлекаем имя компонента
    export_match = re.search(r'export\s+default\s+(\w+)', tsx_code)
    component_name = export_match.group(1) if export_match else 'App'
    
    # Lucide icons wrapper - создает React компоненты из lucide UMD
    # Точная копия из miniapp 2
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
    
    # Преобразуем импорты React (точно как в miniapp 2)
    code = tsx_code
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
    
    # Преобразуем импорты lucide-react (точно как в miniapp 2)
    code = re.sub(
        r'import\s*\{([^}]*)\}\s*from\s*[\'"]lucide-react[\'"];?',
        lambda m: f'const {{{m.group(1)}}} = window.lucideReact;',
        code
    )
    
    # Удаляем export default
    code = re.sub(r'export\s+default\s+\w+;?', '', code)
    
    # Добавляем поддержку embed режима и postMessage (точно как в miniapp 2)
    # Генерируем taskId на основе кода
    task_id = f"tsx-exercise-{_simple_hash(tsx_code)}"
    
    # Ищем handleSubmit и добавляем postMessage (точно как в miniapp 2)
    # Паттерн из miniapp 2: ищем setShowResult(true) и добавляем postMessage после него
    # Используем универсальную логику определения isCorrect
    def add_postmessage(match):
        before = match.group(1)
        set_show = match.group(2)
        
        # Универсальная логика определения isCorrect (как в miniapp 2)
        # Пытаемся найти паттерн сравнения в коде перед setShowResult
        context_before = before[-200:] if len(before) > 200 else before  # Последние 200 символов для контекста
        
        # Определяем, как вычисляется isCorrect
        is_correct_logic = None
        if "userAnswer === problems[currentIndex].correctAnswer" in context_before:
            is_correct_logic = "userAnswer === problems[currentIndex].correctAnswer"
        elif "userAnswer === currentProblem.correctAnswer" in context_before:
            is_correct_logic = "userAnswer === currentProblem.correctAnswer"
        elif "userAnswer === problem.correctAnswer" in context_before:
            is_correct_logic = "userAnswer === problem.correctAnswer"
        elif "userAnswer === currentProblem?.correctAnswer" in context_before:
            is_correct_logic = "userAnswer === currentProblem?.correctAnswer"
        else:
            # Универсальная логика - пытаемся найти правильный ответ из доступных переменных
            is_correct_logic = "(userAnswer === problems[currentIndex]?.correctAnswer || userAnswer === currentProblem?.correctAnswer || userAnswer === problem?.correctAnswer)"
        
        postmessage_code = f'''
    // Отправляем результат в родительское окно (как в miniapp 2)
    const embedMode = /[?&]embed=1/i.test(window.location.search);
    if (embedMode && window.parent) {{
      const __correct = {is_correct_logic};
      const __correctAnswer = problems[currentIndex]?.correctAnswer || currentProblem?.correctAnswer || problem?.correctAnswer || "";
      window.parent.postMessage({{ 
        type: "SUBMIT", 
        taskId: "{task_id}",
        userAnswer: {{ 
          isCorrect: __correct, 
          userAnswer: userAnswer, 
          correctAnswer: __correctAnswer
        }}
      }}, "*");
    }}'''
        return before + set_show + postmessage_code
    
    # Пытаемся найти handleSubmit и добавить postMessage (точно как в miniapp 2)
    code = re.sub(
        r'(const\s+handleSubmit\s*=\s*\([^)]*\)\s*=>\s*\{[\s\S]*?)(setShowResult\s*\(\s*true\s*\)\s*;?)',
        add_postmessage,
        code
    )
    
    # Если не нашли handleSubmit, пытаемся найти другой паттерн
    if 'window.parent.postMessage' not in code or 'type: "SUBMIT"' not in code:
        # Ищем место после setShowResult(true) в любом месте
        def add_postmessage_simple(match):
            set_show = match.group(1)
            # Универсальная логика для определения isCorrect
            is_correct_logic = "(userAnswer === problems[currentIndex]?.correctAnswer || userAnswer === currentProblem?.correctAnswer || userAnswer === problem?.correctAnswer)"
            postmessage_code = f'''
    // Отправляем результат в родительское окно
    const embedMode = /[?&]embed=1/i.test(window.location.search);
    if (embedMode && window.parent) {{
      const __correct = {is_correct_logic};
      const __correctAnswer = problems[currentIndex]?.correctAnswer || currentProblem?.correctAnswer || problem?.correctAnswer || "";
      window.parent.postMessage({{ 
        type: "SUBMIT", 
        taskId: "{task_id}",
        userAnswer: {{ 
          isCorrect: __correct, 
          userAnswer: userAnswer, 
          correctAnswer: __correctAnswer
        }}
      }}, "*");
    }}'''
            return set_show + postmessage_code
        
        code = re.sub(
            r'(setShowResult\s*\(\s*true\s*\)\s*;?\s*)',
            add_postmessage_simple,
            code,
            count=1
        )
    
    # Создаем HTML обертку (точно как в miniapp 2)
    # Используем development версию React для лучшей отладки (как в miniapp 2)
    html_template = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{plugin_name}</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
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
    <script type="text/babel">
        const embedMode = /[?&]embed=1/i.test(window.location.search);
        if (embedMode) {{
            document.body.classList.add('embed');
        }}
        
        {code}
        
        ReactDOM.createRoot(document.getElementById('root')).render(React.createElement({component_name}));
        
        // Отправляем INIT сообщение
        if (embedMode && window.parent) {{
            window.parent.postMessage({{ type: 'INIT', status: 'ready' }}, '*');
        }}
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

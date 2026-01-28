// TSX Transformer для загрузки упражнений из miniapp-v2
// Адаптировано из miniapp-v2/index.html

// Lucide icons wrapper - создает React компоненты из lucide UMD
export const LUCIDE_WRAPPER = `
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
`

export interface TransformResult {
  code: string
  componentName: string
}

/**
 * Трансформирует TSX код из Claude Artifacts в браузер-готовый код
 */
export function transformTsx(tsxCode: string): TransformResult {
  // Извлекаем имя компонента
  const exportMatch = tsxCode.match(/export\s+default\s+(\w+)/)
  const componentName = exportMatch ? exportMatch[1] : 'App'

  let code = tsxCode

  // Трансформируем импорты
  code = code.replace(/import\s+React\s*,?\s*\{([^}]*)\}\s*from\s*['"]react['"];?/g, (_, h) => 'const {' + h + '} = React;')
  code = code.replace(/import\s+React\s+from\s*['"]react['"];?/g, '')
  code = code.replace(/import\s*\{([^}]*)\}\s*from\s*['"]react['"];?/g, (_, h) => 'const {' + h + '} = React;')
  code = code.replace(/import\s*\{([^}]*)\}\s*from\s*['"]lucide-react['"];?/g, (_, i) => 'const {' + i + '} = window.lucideReact;')
  code = code.replace(/export\s+default\s+\w+;?/g, '')

  // Удаляем TypeScript синтаксис для совместимости с Babel
  // Порядок важен - сначала более специфичные паттерны, потом общие
  
  // 1. Удаляем interface declarations (многострочные)
  code = code.replace(/interface\s+\w+[^{]*\{[^}]*\}/gs, '')
  
  // 2. Удаляем type declarations
  code = code.replace(/type\s+\w+\s*=\s*[^;]+;/g, '')
  
  // 3. КРИТИЧНО: Удаляем ВСЕ generic типы ПЕРЕД обработкой конструкторов и hooks
  // Это должно обработать случаи типа: useState(new Set<string>())
  // Обрабатываем в два прохода для надежности
  
  // 3.1. Первый проход: удаляем generic типы в известных конструкторах и типах
  code = code.replace(/(Set|Map|Array|Record|Promise|React|HTMLElement|Element|useState|useRef|useEffect|useCallback|useMemo|useReducer)<[^<>()]+>/g, '$1')
  
  // 3.2. Второй проход: удаляем generic типы в конструкторах new Type<...>()
  code = code.replace(/new\s+(\w+)<[^<>()]+>\(/g, 'new $1(')
  
  // 3.3. Третий проход: удаляем оставшиеся generic типы (но сохраняем возможные JSX)
  code = code.replace(/(\w+)<([^<>()]+)>/g, (match, name, content) => {
    // Если это известные generic типы - уже обработано выше, но на всякий случай
    const genericTypes = ['Set', 'Map', 'Array', 'Record', 'Promise', 'React', 'HTMLElement', 'Element']
    if (genericTypes.includes(name)) {
      return name
    }
    // Если это React hook - уже обработано выше
    if (['useState', 'useRef', 'useEffect', 'useCallback', 'useMemo', 'useReducer'].includes(name)) {
      return name
    }
    // Если имя начинается с заглавной буквы и content простой (без запятых, типов) - возможно JSX
    if (/^[A-Z]/.test(name) && !/[,\|&]/.test(content) && content.length < 20 && /^[a-zA-Z0-9.]+$/.test(content)) {
      return match // Оставляем как есть (возможно JSX компонент)
    }
    // Для всех остальных - удаляем generic
    return name
  })
  
  // 4. Удаляем generic типы в React hooks: useState<string>() -> useState()
  // (Это уже обработано выше, но оставляем для совместимости)
  code = code.replace(/(useState|useRef|useEffect|useCallback|useMemo|useReducer)<[^<>()]+>/g, '$1')
  
  // 4.1. Удаляем generic типы в useCallback: useCallback<...>()
  code = code.replace(/useCallback<[^<>()]+>/g, 'useCallback')
  
  // 5. Удаляем generic типы в React.createElement (но сохраняем JSX теги)
  code = code.replace(/React\.createElement<[^<>]+>/g, 'React.createElement')
  
  // 6. Удаляем type annotations в объявлениях переменных: const x: string = -> const x =
  // Используем более точный паттерн, который не ломает тернарные операторы и JSX
  code = code.replace(/:\s*(string|number|boolean|any|void|null|undefined|object|Array|Set|Map|Record|Function|Promise|\w+)(<[^>]*>)?\s*(?==|,|;|\)|\||&|\?|$)/g, '')
  
  // 7. Удаляем type assertions: as string, as number и т.д.
  code = code.replace(/\s+as\s+(string|number|boolean|any|void|null|undefined|object|Array|Set|Map|Record|Function|Promise|\w+)(<[^>]*>)?/g, '')
  
  // 8. КРИТИЧНО: Удаляем объектные типы в параметрах функций: (data: { id: string; ... }) -> (data)
  // Это должно обработать многострочные объектные типы
  // Используем более агрессивный подход: удаляем все типы параметров, включая объектные
  // Обрабатываем многострочные объекты с учетом вложенности скобок и переносов строк
  let maxIterations = 10
  let iteration = 0
  while (iteration < maxIterations) {
    const before = code
    // Удаляем объектные типы в параметрах: (param: { ... }) -> (param)
    // Используем [\s\S] для обработки многострочных объектов (включая переносы строк)
    // Ищем паттерн: (param: { ... }) где ... может быть многострочным
    code = code.replace(/\((\w+):\s*\{[\s\S]*?\}\)/g, (match, paramName, offset) => {
      // Проверяем, что это действительно параметр функции, а не JSX
      // Ищем открывающую скобку функции перед match
      const beforeMatch = code.substring(0, offset)
      // Если перед match есть = или => или function, это параметр функции
      if (beforeMatch.match(/[=\(]\s*$/) || beforeMatch.endsWith('function ') || beforeMatch.endsWith('=>')) {
        return `(${paramName})`
      }
      return match
    })
    // Также обрабатываем случаи с несколькими параметрами: (param1: type1, param2: { ... })
    code = code.replace(/(\w+):\s*\{[\s\S]*?\}/g, '$1')
    if (before === code) break
    iteration++
  }
  
  // 8.1. Удаляем generic типы в параметрах функций: (x: Set<string>) -> (x)
  // Сначала удаляем весь тип параметра, если он содержит generic
  code = code.replace(/\(([^)]*):\s*\w+<[^>]+>([^)]*)\)/g, '($1$2)')
  
  // 9. Удаляем оставшиеся type annotations в параметрах: (x: string) -> (x)
  code = code.replace(/\(([^)]*):\s*\w+([^)]*)\)/g, '($1$2)')
  
  // 10. КРИТИЧНО: Удаляем ВСЕ оставшиеся generic типы в любом контексте
  // Это должно обработать случаи типа: useState(new Set<string>())
  // Используем более агрессивный паттерн, который удаляет <...> везде, кроме JSX
  // JSX теги обычно имеют вид: <Component> или <div>, и они обычно в начале строки или после return/(
  // Generic типы обычно имеют вид: Set<string>, Map<string, number>, и они внутри выражений
  
  // Сначала обрабатываем случаи внутри вызовов функций: useState(new Set<string>())
  code = code.replace(/(\w+)<([^<>]+)>/g, (match, name, content) => {
    // Если это похоже на JSX компонент (начинается с заглавной буквы и содержит только буквы/точки)
    if (/^[A-Z][a-zA-Z0-9.]*$/.test(name) && !content.includes(',')) {
      // Возможно это JSX, но если content содержит запятую или другие символы типов, это точно generic
      if (/[,\|&]/.test(content)) {
        return name // Удаляем generic
      }
      // Если это Set, Map, Array и т.д. - это точно generic
      if (['Set', 'Map', 'Array', 'Record', 'Promise', 'React'].includes(name)) {
        return name // Удаляем generic
      }
      // Для других случаев с заглавной буквы - возможно JSX, оставляем
      return match
    }
    // Для всех остальных - удаляем generic
    return name
  })

  // Инжектируем postMessage в handleSubmit для отслеживания результатов
  // Паттерн 1: handleSubmit с problems[currentIndex].correctAnswer
  code = code.replace(
    /(const\s+handleSubmit\s*=\s*\([^)]*\)\s*=>\s*\{[\s\S]*?)(setShowResult\s*\(\s*true\s*\)\s*;?)/,
    (m, before, setShow) => {
      // Проверяем, есть ли в коде problems[currentIndex].correctAnswer
      if (m.includes('problems[currentIndex].correctAnswer')) {
        return before + setShow + '\n    const __isCorrect = userAnswer === problems[currentIndex].correctAnswer;\n    window.parent.postMessage({ type: "exercise-result", id: null, correctAnswer: problems[currentIndex].correctAnswer, studentAnswer: userAnswer, isCorrect: __isCorrect }, "*");'
      }
      // Если нет, ищем правильный ответ в других местах
      const correctMatch = m.match(/(\w+)\[currentIndex\]\.correctAnswer/) || m.match(/(\w+)\.correctAnswer/)
      if (correctMatch) {
        const varName = correctMatch[1]
        return before + setShow + `\n    const __isCorrect = userAnswer === ${varName}[currentIndex].correctAnswer;\n    window.parent.postMessage({ type: "exercise-result", id: null, correctAnswer: ${varName}[currentIndex].correctAnswer, studentAnswer: userAnswer, isCorrect: __isCorrect }, "*");`
      }
      // Если не нашли, используем общий паттерн
      return before + setShow + '\n    const __isCorrect = userAnswer === correctAnswer;\n    window.parent.postMessage({ type: "exercise-result", id: null, correctAnswer: correctAnswer, studentAnswer: userAnswer, isCorrect: __isCorrect }, "*");'
    }
  )

  // Паттерн 2: Если postMessage уже есть, не добавляем повторно
  if (!code.includes('postMessage')) {
    // Пытаемся найти место после проверки правильности ответа
    code = code.replace(
      /(if\s*\(userAnswer\s*===\s*([^)]+)\)\s*\{[\s\S]*?setScore[\s\S]*?\})/,
      (m, fullMatch, correctAnswer) => {
        if (m.includes('postMessage')) return m
        return fullMatch + '\n    window.parent.postMessage({ type: "exercise-result", id: null, correctAnswer: ' + correctAnswer + ', studentAnswer: userAnswer, isCorrect: userAnswer === ' + correctAnswer + ' }, "*");'
      }
    )
  }

  return { code, componentName }
}

/**
 * Создает HTML для iframe с трансформированным TSX кодом
 */
export function createTsxIframeHtml(tsxCode: string): string {
  const { code, componentName } = transformTsx(tsxCode)

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
  <div id="root"></div>
  <script>${LUCIDE_WRAPPER}</script>
  <script type="text/babel">
${code}
ReactDOM.createRoot(document.getElementById("root")).render(React.createElement(${componentName}));
  </script>
</body>
</html>`
}

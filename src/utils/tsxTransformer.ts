// TSX Transformer для загрузки интерактивных упражнений
// Упрощенный трансформер для интерактивных вопросов (ученики/учителя)

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
 * Трансформирует TSX код в браузер-готовый код
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

  // Удаляем TypeScript синтаксис
  code = code.replace(/interface\s+\w+[^{]*\{[^}]*\}/gs, '')
  code = code.replace(/type\s+\w+\s*=\s*[^;]+;/g, '')
  code = code.replace(/(Set|Map|Array|Record|Promise|React|HTMLElement|Element|useState|useRef|useEffect|useCallback|useMemo|useReducer)<[^<>()]+>/g, '$1')
  code = code.replace(/new\s+(\w+)<[^<>()]+>\(/g, 'new $1(')

  return { code, componentName }
}

/**
 * Создает HTML для iframe с трансформированным TSX кодом
 */
export function createTsxIframeHtml(tsxCode: string, reviewData?: Record<string, unknown> | null): string {
  const { code, componentName } = transformTsx(tsxCode)

  const injectScript = reviewData 
    ? `<script>window.reviewMode = ${JSON.stringify(reviewData)};</script>` 
    : ''

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
  ${injectScript}
  <script>${LUCIDE_WRAPPER}</script>
  <script type="text/babel">
${code}
ReactDOM.createRoot(document.getElementById("root")).render(React.createElement(${componentName}));
  </script>
</body>
</html>`
}

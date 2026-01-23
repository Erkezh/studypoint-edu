<template>
  <div class="interactive-question">
    <!-- Используем iframe для безопасного выполнения React кода -->
    <iframe
      v-if="iframeSrc"
      ref="questionFrame"
      :src="iframeSrc"
      class="w-full border-0 min-h-[600px] rounded-lg"
      sandbox="allow-scripts allow-same-origin allow-forms"
      @load="onIframeLoad"
    ></iframe>
    <div v-else class="text-center py-8 text-gray-500">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      <p class="mt-4">Интерактивное задание загружается...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'

interface Props {
  componentCode: string
  questionData?: Record<string, any>
  disabled?: boolean
}

interface Emits {
  (e: 'answer', answer: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const questionFrame = ref<HTMLIFrameElement | null>(null)
const iframeSrc = ref<string>('')

// Создаем HTML страницу с React компонентом
const createIframeContent = () => {
  // Экранируем код для безопасной вставки в HTML
  const escapedCode = props.componentCode
    .replace(/\\/g, '\\\\')
    .replace(/`/g, '\\`')
    .replace(/\${/g, '\\${')
  
  const html = `
<!DOCTYPE html>
<html lang="kk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Интерактивное задание</title>
  
  <!-- React и ReactDOM -->
  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"><\/script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"><\/script>
  
  <!-- Babel Standalone для трансформации JSX -->
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"><\/script>
  
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"><\/script>
  
  <!-- Lucide React Icons (если используются) -->
  <script>
    // Простая заглушка для lucide-react, если используется
    window.lucideReact = {
      RefreshCw: () => null,
      CheckCircle: () => null,
      XCircle: () => null,
      Brain: () => null,
      Award: () => null,
      Trophy: () => null,
      BookOpen: () => null,
      Calculator: () => null,
      Clock: () => null,
      Target: () => null,
      BarChart3: () => null,
      RotateCcw: () => null,
    };
  <\/script>
  
  <style>
    * { box-sizing: border-box; }
    body { 
      margin: 0; 
      padding: 16px; 
      font-family: system-ui, -apple-system, sans-serif;
      background: #f9fafb;
    }
    #root { width: 100%; }
  </style>
</head>
<body>
  <div id="root"></div>
  
  <script type="text/babel">
    const { useState, useEffect, useCallback, useRef } = React;
    
    // Функция для отправки ответа родительскому окну
    const sendAnswer = (answer) => {
      if (window.parent && window.parent !== window) {
        window.parent.postMessage({
          type: 'interactive-question-answer',
          answer: answer
        }, '*');
      }
    };
    
    // Данные вопроса (если нужны)
    const questionData = ${JSON.stringify(props.questionData || {})};
    const disabled = ${props.disabled || false};
    
    try {
      // Создаем модуль для экспорта
      const module = { exports: {} };
      const exports = module.exports;
      
      // Выполняем код компонента в изолированном контексте
      (function() {
        ${escapedCode}
      })();
      
      // Ищем экспортированный компонент
      let ComponentToRender = null;
      
      // Проверяем module.exports
      if (module.exports && module.exports.default) {
        ComponentToRender = module.exports.default;
      } else if (module.exports && typeof module.exports === 'function') {
        ComponentToRender = module.exports;
      } else if (module.exports && Object.keys(module.exports).length > 0) {
        // Берем первый экспорт
        ComponentToRender = Object.values(module.exports)[0];
      }
      
      // Если не найден в module.exports, ищем в глобальной области
      if (!ComponentToRender) {
        const componentNames = [
          'KazakhPlaceValueGenerator', 'KazakhPlaceValueQuiz', 'KazakhMathGenerator',
          'PlaceValueApp', 'KazakhPlaceValueApp', 'PlaceValueGenerator',
          'KazakhNumberQuestions', 'KazakhNumberWordsApp', 'KazakhNumberPractice'
        ];
        
        for (const name of componentNames) {
          if (typeof window[name] === 'function') {
            ComponentToRender = window[name];
            break;
          }
        }
      }
      
      // Если все еще не найден, ищем последнюю определенную функцию/компонент
      if (!ComponentToRender) {
        try {
          // Пытаемся найти компонент через анализ кода
          const codeStr = \`${escapedCode}\`;
          const matches = codeStr.match(/(?:const|function|class|export\\s+default\\s+)([A-Z]\\w+)\\s*[=({]/g);
          if (matches && matches.length > 0) {
            const lastMatch = matches[matches.length - 1];
            const componentName = lastMatch.match(/(?:const|function|class|export\\s+default\\s+)([A-Z]\\w+)/)?.[1];
            if (componentName) {
              // Выполняем код и ищем компонент
              eval(codeStr);
              if (typeof window[componentName] === 'function') {
                ComponentToRender = window[componentName];
              } else if (typeof eval(componentName) === 'function') {
                ComponentToRender = eval(componentName);
              }
            }
          }
        } catch (e) {
          console.warn('Could not auto-detect component:', e);
        }
      }
      
      // Рендерим компонент
      if (ComponentToRender && typeof ComponentToRender === 'function') {
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(React.createElement(ComponentToRender));
      } else {
        // Если компонент не найден, показываем ошибку с инструкцией
        document.getElementById('root').innerHTML = 
          '<div style="padding: 20px; max-width: 600px; margin: 0 auto;">' +
          '<h2 style="color: #dc2626; margin-bottom: 16px;">⚠️ Компонент не найден</h2>' +
          '<p style="color: #6b7280; margin-bottom: 12px;">Убедитесь, что код экспортирует компонент одним из способов:</p>' +
          '<ul style="color: #6b7280; list-style: disc; padding-left: 24px; margin-bottom: 12px;">' +
          '<li><code>export default ComponentName</code></li>' +
          '<li><code>const ComponentName = () => { ... }</code></li>' +
          '<li><code>function ComponentName() { ... }</code></li>' +
          '</ul>' +
          '<p style="color: #6b7280; font-size: 12px;">Проверьте консоль браузера для подробностей.</p>' +
          '</div>';
        console.error('Component not found. Available globals:', Object.keys(window).filter(k => typeof window[k] === 'function' && k.match(/^[A-Z]/)));
      }
    } catch (error) {
      console.error('Error loading interactive question:', error);
      document.getElementById('root').innerHTML = 
        '<div style="padding: 20px; color: #dc2626;">' +
        '<h3 style="margin-bottom: 12px;">❌ Ошибка загрузки компонента</h3>' +
        '<p style="margin-bottom: 8px;"><strong>Сообщение:</strong> ' + error.message + '</p>' +
        '<details style="margin-top: 12px;"><summary style="cursor: pointer; color: #6b7280;">Подробности</summary>' +
        '<pre style="background: #f3f4f6; padding: 12px; border-radius: 4px; overflow-x: auto; margin-top: 8px; font-size: 12px;">' + 
        error.stack + '</pre></details>' +
        '</div>';
    }
  <\/script>
</body>
</html>
  `
  
  // Создаем blob URL
  const blob = new Blob([html], { type: 'text/html' })
  return URL.createObjectURL(blob)
}

// Слушаем сообщения от iframe
const handleMessage = (event: MessageEvent) => {
  // Проверяем, что сообщение от нашего iframe
  if (event.data?.type === 'interactive-question-answer') {
    emit('answer', event.data.answer)
  }
}

const onIframeLoad = () => {
  // После загрузки iframe можно выполнить дополнительные действия
  if (questionFrame.value?.contentWindow) {
    // Можно установить связь с iframe
  }
}

onMounted(() => {
  iframeSrc.value = createIframeContent()
  window.addEventListener('message', handleMessage)
})

watch(() => props.componentCode, () => {
  if (iframeSrc.value) {
    URL.revokeObjectURL(iframeSrc.value)
  }
  iframeSrc.value = createIframeContent()
})

onUnmounted(() => {
  if (iframeSrc.value) {
    URL.revokeObjectURL(iframeSrc.value)
  }
  window.removeEventListener('message', handleMessage)
})
</script>

export const PLUGIN_PROMPT_TEMPLATE = `# Промт для генерации интерактивных плагинов (StudyPoint IXL Contract)

**Тема:** [ОПИШИ ТЕМУ]  
**Тип:** [текстовый ввод / выбор / drag-drop / сетка]

---

## 🚨 КРИТИЧЕСКИЕ ПРАВИЛА (СТРОГИЙ РЕГЛАМЕНТ - ОБЯЗАТЕЛЬНО К ИСПОЛНЕНИЮ)

### 1. 🔐 ДЕТЕРМИНИРОВАННЫЙ SEED И PRNG (100% СОВПАДЕНИЕ У УЧЕНИКА И УЧИТЕЛЯ)
- В URL передаётся \`?seed=12345\`.
- **Генератор условий \`generateProblem(level, seed)\` ОБЯЗАН быть 100% чистой функцией**, создающей собственный экземпляр \`createSeededRandom(seed)\` внутри себя!
- **НЕ ИСПОЛЬЗУЙ \`Math.random()\`!** Все рандомные числа, выбор имён, перетасовка вариантов должны браться ТОЛЬКО из \`rng()\`.
- **НЕ ИСПОЛЬЗУЙ mutable \`useRef\` для сохранения PRNG между рендерами React!**

\`\`\`tsx
function createSeededRandom(s: number): () => number {
  let state = s % 2147483647;
  if (state <= 0) state += 2147483646;
  return () => {
    state = (state * 16807) % 2147483647;
    return (state - 1) / 2147483646;
  };
}

// ✅ ПРАВИЛЬНО: генератор создаёт свежий PRNG от seed при каждом вызове
const generateProblem = (level: number, seed: number, depth = 0): Problem => {
  const random = createSeededRandom(seed + depth * 10007);
  // ... генерация задачи через random() ...
  return { ... };
};
\`\`\`

---

### 2. 🎯 5 УРОВНЕЙ СЛОЖНОСТИ (\`?level=1..5\`)
Плагин **ОБЯЗАН** поддерживать 5 уровней сложности:
\`\`\`tsx
const levelParam = urlParams.get('level');
const level = levelParam ? Math.min(5, Math.max(1, parseInt(levelParam, 10))) : 1;
\`\`\`
- **1-деңгей (Бастапқы):** Простейшие наглядные примеры, маленькие числа (1-10).
- **2-деңгей (Оңай):** Базовые задачи с небольшим усложнением.
- **3-деңгей (Орташа):** Стандартные задачи по теме.
- **4-деңгей (Күрделі):** Продвинутые задачи повышенной сложности.
- **5-деңгей (Жоғары):** Олимпиадный/мастер уровень.

---

### 3. 🖼️ ВНУТРЕННИЙ ИНТЕРФЕЙС РЕЗУЛЬТАТА И ТҮСІНДІРМЕ (EXPLANATION)
- **Плагин САМ показывает вердикт (Дұрыс! / Қате!) и ПОШАГОВОЕ ОБЪЯСНЕНИЕ (Түсіндірме / Шешуі) внутри iframe.**
- При нажатии "Тексеру" / "Жіберу" или при получении \`SERVER_RESULT\` плагин НЕ очищает экран, а показывает:
  1. Зелёную плашку "Дұрыс! 🎉" или красную плашку "Қате! ❌".
  2. Если отвечено неправильно: показывает введенный ответ ученика (красным) и правильный ответ (зеленым).
  3. **Блок с пошаговым объяснением решения на казахском языке (\`Түсіндірме\` / \`Шешуі\`).**

---

### 4. 📊 АНАЛИТИКА И РЕЖИМ РЕЦЕНЗИРОВАНИЯ (\`mode=review\` & \`studentAnswer\`)
При открытии аналитики у учителя или в журнале ответов (\`?mode=review\` или \`?studentAnswer=...\`):
- Считывай ответ ученика из URL: \`const studentAnsParam = urlParams.get('studentAnswer') || urlParams.get('userAnswer');\`
- Ответ ученика может прийти как строка, так и JSON-строка объекта. Обязательно парси его:
  \`\`\`tsx
  let parsedAnswer = studentAnsParam;
  try {
    if (studentAnsParam && (studentAnsParam.startsWith('{') || studentAnsParam.startsWith('['))) {
      const parsed = JSON.parse(studentAnsParam);
      parsedAnswer = parsed.userAnswer ?? parsed.studentAnswer ?? parsed.value ?? parsed.answer ?? parsed;
    }
  } catch (e) {
    console.warn(e);
  }
  \`\`\`
- **Считывание \`questionData\` из URL (КРИТИЧЕСКИ ВАЖНО):**
  В URL передаётся \`?questionData=...\` с JSON-строкой параметров вопроса.
  Плагин **ОБЯЗАН** считать его и использовать для восстановления условия:
  \`\`\`tsx
  const qDataParam = urlParams.get('questionData');
  let urlQuestionData = null;
  try {
    if (qDataParam) {
      urlQuestionData = JSON.parse(qDataParam);
    }
  } catch (e) {
    console.warn("Failed to parse questionData:", e);
  }
  \`\`\`

---

### 5. 🧊 FROZEN РЕЖИМ (ПРЕВЬЮ В КОНСТРУКТОРЕ)
URL содержит \`?frozen=1\`.
- **Сохранять 100% оригинальные яркие цвета (\`opacity: 1\`, БЕЗ серых фильтров!)**
- **Отключить клики и интерактивность:** \`pointer-events: none\` на контейнере.
- **Поля ввода и кнопки:** \`disabled\`.

---

### 6. ⚡ РЕАКТИВНЫЕ ЗАВИСИМОСТИ В EFFECT (КРИТИЧЕСКИ ВАЖНО)
Массив зависимостей React \`useEffect\` **ОБЯЗАТЕЛЬНО** должен содержать \`[level, seed, qDataParam]\`!

---

### 7. 📤 ОТПРАВКА ДАННЫХ В РОДИТЕЛЬСКОЕ ОКНО (\`window.parent.postMessage\`)
При каждом действии или проверке отправляй сообщение:
\`\`\`tsx
window.parent.postMessage({
  type: 'exercise-result',
  isCorrect: boolean,
  userAnswer: string | object,
  correctAnswer: string | object,
  questionData: object // параметры условия
}, '*');
\`\`\`
`

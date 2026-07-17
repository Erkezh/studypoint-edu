# Промт для генерации интерактивных тестов

**Тема:** [ОПИШИ ТЕМУ]  
**Тип:** [текстовый ввод / выбор / drag-drop / сетка]

---

## ⚠️ ГЛАВНОЕ ПРАВИЛО

**Если в вопросе есть картинка → передай её в `questionData`!**

Иначе в аналитике вопрос "Қай бөлшек көрсетілген?" без картинки не имеет смысла.

---

## 🚨 КРИТИЧНО: СИНТАКСИС КОМПОНЕНТА

**ОБЯЗАТЕЛЬНО используй один из этих форматов:**

```tsx
// ✅ Вариант 1: Arrow function (рекомендуется)
const ComponentName: React.FC = () => {
  // ...
};
export default ComponentName;

// ✅ Вариант 2: Function declaration
function ComponentName() {
  // ...
}
export default ComponentName;
```

**❌ НИКОГДА не пиши так — это вызовет ошибку компиляции:**
```tsx
ComponentName() {   // ❌ НЕПРАВИЛЬНО!
  // ...
}
```

---

## 🔐 SEED РЕЖИМ (ОБЯЗАТЕЛЬНО!)

Плагин **ОБЯЗАН** поддерживать детерминированную генерацию вопросов через `seed`.

Когда учитель создаёт квиз, система передаёт в URL плагина параметр `?seed=12345`.
Плагин должен использовать этот seed вместо `Math.random()`, чтобы:
- **Учитель и ученик видели одинаковый вопрос**
- **При перезагрузке страницы вопрос не менялся**

```tsx
// ⚠️ Читаем seed из URL
const urlParams = new URLSearchParams(window.location.search);
const seedParam = urlParams.get('seed');
const seed = seedParam ? parseInt(seedParam, 10) : Date.now();

// ⚠️ Детерминированный генератор случайных чисел (ОБЯЗАТЕЛЬНО!)
function createSeededRandom(s: number): () => number {
  let state = s;
  return () => {
    state = (state * 1664525 + 1013904223) & 0x7fffffff;
    return state / 0x7fffffff;
  };
}

const random = createSeededRandom(seed);

// ✅ ИСПОЛЬЗУЙ random() ВМЕСТО Math.random() ВЕЗДЕ!
// Примеры:
const pos = Math.floor(random() * 9) + 1;       // вместо Math.floor(Math.random() * 9) + 1
const idx = Math.floor(random() * arr.length);   // вместо Math.floor(Math.random() * arr.length)
```

**❌ ЗАПРЕЩЕНО использовать `Math.random()` напрямую!** Используй только `random()`.

---

## 🧊 FROZEN РЕЖИМ (ОБЯЗАТЕЛЬНО!)

При создании квиза учитель видит превью вопроса. Это превью должно быть **замороженным** — как скриншот, без интерактивности.

URL будет содержать параметр `?frozen=1`. Если этот параметр установлен:
- **Все кнопки**: `disabled`, `pointer-events: none`
- **Все input**: `disabled`
- **Drag-drop**: отключен
- **Кнопки "Тексеру" / "Келесі сұрақ"**: скрыты
- **Показывать ТОЛЬКО визуальную часть вопроса** (текст, картинки, фигуры)

```tsx
// ⚠️ Frozen mode (замороженный вид)
const isFrozen = urlParams.get('frozen') === '1';

// В рендере:
<button 
  disabled={isFrozen || isReview}
  style={isFrozen ? { pointerEvents: 'none', opacity: 0.7 } : {}}
>
  ...
</button>

// Скрывать кнопки "Тексеру" и "Келесі сұрақ" в frozen режиме:
{!isFrozen && (
  <button onClick={handleSubmit}>Тексеру</button>
)}
```

---

## 📝 QUIZ РЕЖИМ (ОБЯЗАТЕЛЬНО!)

При прохождении квиза/теста (параметр `?mode=quiz`) плагин **должен самостоятельно проверять ответ**, показывать правильный/неправильный ответ ученику и **выводить объяснение решения** (если ответ неверный).

URL будет содержать параметр `?mode=quiz`. Если этот параметр установлен:

### Поведение после отправки ответа:
1. При клике на кнопку отправки ответа («Тексеру» / «Submit») плагин проверяет ответ, отправляет результат родителю через `postMessage` и **сразу показывает правильный/неправильный ответ, а также объяснение решения** (если ответ неверный) с помощью `setShowResult(true)`.
2. **После отправки плагин ПОЛНОСТЬЮ БЛОКИРУЕТ свой UI** — все кнопки (`disabled`), все `input` (`disabled`), `pointer-events: none`. Ученик видит свой ответ, результат и объяснение решения, но не может изменить выбор.
3. **Кнопка «Келесі сұрақ» в режиме квиза скрывается** (так как навигацию между вопросами в квизе контролирует само родительское приложение с помощью кнопок снаружи iframe).

### Сброс состояния:
- Если ученик переключается между вопросами или сбрасывает ответ, родительское приложение перезагружает iframe. Плагин всегда инициализируется в чистом состоянии (пустой ввод, разблокированный UI).

```tsx
// ⚠️ Quiz mode (режим квиза)
const isQuiz = urlParams.get('mode') === 'quiz';
const [isSubmitted, setIsSubmitted] = useState(false);

const handleSubmit = () => {
  if (isReview || isFrozen || isSubmitted || !userAnswer || !problem) return;
  const isCorrect = userAnswer === problem.correctAnswer;
  
  window.parent.postMessage({
    type: 'exercise-result',
    isCorrect,
    question: problem.question,
    userAnswer,
    correctAnswer: problem.correctAnswer,
    questionData: problem.visualData,
  }, '*');
  
  // В режиме квиза: блокируем UI и сразу ПОКАЗЫВАЕМ результат и объяснение
  setIsSubmitted(true);
  setShowResult(true);
};

// В рендере — блокируем все input и кнопки после отправки:
<input 
  disabled={isReview || isFrozen || isSubmitted}
  value={userAnswer}
  onChange={e => setUserAnswer(e.target.value)}
/>
{!isFrozen && !isSubmitted && (
  <button onClick={handleSubmit} disabled={!userAnswer}>
    Тексеру
  </button>
)}
{isSubmitted && (
  <div className="mt-4">
    <p style={{ color: isCorrect ? '#10B981' : '#EF4444', fontWeight: 600 }}>
      {isCorrect ? '✓ Жауап дұрыс!' : '❌ Жауап қате'}
    </p>
    {!isCorrect && problem.explanation && (
      <div className="mt-2 p-3 bg-red-50 text-red-800 text-sm border-l-4 border-red-500">
        <p className="font-semibold">Түсіндірме:</p>
        <p>{problem.explanation}</p>
      </div>
    )}
  </div>
)}
```

---

## 1. СТРУКТУРА

```tsx
import React, { useState, useEffect, useRef } from 'react';

interface Problem {
  id: number;
  question: string;
  correctAnswer: string;
  visualData?: any;  // Данные для аналитики (тип вопроса)
}

const Component: React.FC = () => {
  const [problem, setProblem] = useState<Problem | null>(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);  // ⚠️ Блокировка после отправки в quiz mode
  const containerRef = useRef<HTMLDivElement>(null);

  // ⚠️ URL параметры
  const urlParams = new URLSearchParams(window.location.search);
  const seedParam = urlParams.get('seed');
  const seed = seedParam ? parseInt(seedParam, 10) : Date.now();
  const isFrozen = urlParams.get('frozen') === '1';
  const isQuiz = urlParams.get('mode') === 'quiz';  // ⚠️ Quiz mode

  // ⚠️ Режим просмотра ошибок (аналитика для учителя/ученика)
  const reviewMode = (window as any).reviewMode || null;
  const isReview = !!reviewMode;

  // ⚠️ Детерминированный PRNG
  function createSeededRandom(s: number): () => number {
    let state = s;
    return () => {
      state = (state * 1664525 + 1013904223) & 0x7fffffff;
      return state / 0x7fffffff;
    };
  }
  const random = createSeededRandom(seed);

  const generateProblem = (): Problem => ({
    id: seed,  // Используем seed как ID
    question: 'Сұрақ мәтіні',
    correctAnswer: '3/4',
    visualData: { type: 'fractionbar', fractionBar: { total: 4, filled: 3 } },
  });

  const sendHeight = () => {
    if (window.parent !== window && containerRef.current) {
      window.parent.postMessage({ type: 'resize', height: containerRef.current.scrollHeight + 20 }, '*');
    }
  };

  useEffect(() => {
    if (isReview) {
      // ⚠️ Восстанавливаем сохраненное состояние для аналитики
      setProblem({
        id: seed,
        question: 'Сұрақ мәтіні',
        correctAnswer: reviewMode.correctAnswer,
        visualData: reviewMode.questionData
      });
      setUserAnswer(reviewMode.studentAnswer);
      setShowResult(true);
    } else {
      setProblem(generateProblem());
    }
  }, []);

  useEffect(() => { sendHeight(); setTimeout(sendHeight, 100); }, [problem, showResult, isSubmitted]);

  const handleSubmit = () => {
    if (isReview || isFrozen || isSubmitted || !userAnswer || !problem) return;
    const isCorrect = userAnswer === problem.correctAnswer;
    
    window.parent.postMessage({
      type: 'exercise-result',
      isCorrect,
      question: problem.question,
      userAnswer,
      correctAnswer: problem.correctAnswer,
      questionData: problem.visualData,  // ⚠️ Передаём картинку!
    }, '*');
    
    if (isQuiz) {
      // ⚠️ В quiz mode: блокируем UI, НЕ показываем правильный ответ
      // Родительское приложение покажет "Жауап берілді" и кнопку "Жауапты өзгерту"
      // Если ученик хочет изменить ответ — родитель перезагрузит iframe
      setIsSubmitted(true);
      return;
    }
    
    setShowResult(true);
  };

  const handleNext = () => {
    if (isFrozen || isQuiz) return;  // ⚠️ В frozen и quiz режимах "Келесі сұрақ" не работает
    setProblem(generateProblem());
    setUserAnswer('');
    setShowResult(false);
  };

  return (
    <div ref={containerRef} className="p-4 bg-white rounded-xl">
      {/* ⚠️ В режиме isReview, isFrozen или isSubmitted отключайте любые клики и ввод */}
      {/* disabled={isReview || isFrozen || isSubmitted} */}
      {/* ⚠️ В frozen и quiz(submitted) режимах скрывайте кнопки "Тексеру" и "Келесі сұрақ" */}
      {/* ⚠️ При неверном ответе в isReview покажите верное решение зеленым, а неверное - красным */}
    </div>
  );
};

export default Component;
```

---

## 2. ТИПЫ ВИЗУАЛЬНЫХ ЗАДАНИЙ

### ТИП A: Картинка в ВОПРОСЕ → `questionData`
Ученик видит картинку, пишет текстовый ответ.

```tsx
postMessage({
  type: 'exercise-result',
  question: 'Сан түзуінде көрсетілген бөлшек?',
  userAnswer: '1/3',
  correctAnswer: '3/11',
  questionData: { type: 'numberline', numberline: { min: 0, max: 1, divisions: 11, markedPosition: 3 } },
});
```

### ТИП B: Картинка в ОТВЕТЕ → `answerData`
Вопрос текстовый, ученик рисует/выбирает.

```tsx
postMessage({
  type: 'exercise-result',
  question: '4 шаршы бірлік сыз',
  userAnswer: '2 клетки',
  correctAnswer: '4 клетки',
  answerData: {
    type: 'grid',
    correctDisplay: { grids: [{ rows: 8, cols: 8, filled: ['0-0','0-1','1-0','1-1'] }], text: '4' },
    userDisplay: { grids: [{ rows: 8, cols: 8, filled: ['0-0','0-1'] }], text: '2' },
  },
});
```

---

## 3. ФОРМАТЫ questionData

| Тип | visualData | Пример вопроса |
|-----|------------|----------------|
| Числовая прямая | `{ type: 'numberline', numberline: { min, max, divisions, markedPosition } }` | Сан түзуіндегі бөлшек? |
| Дробная полоска | `{ type: 'fractionbar', fractionBar: { total, filled } }` | Боялған бөлік қандай? |
| Сетка | `{ type: 'grid', grid: { rows, cols, filled: ['0-0','0-1'] } }` | Аудан қанша? |
| Фигуры | `{ type: 'shapes', shapes: { items: [{type, color}], targetType, targetCount, totalCount } }` | Жұлдыздар қанша? |

### Примеры генерации (с seed!):

```tsx
// ⚠️ ВАЖНО: используем random() вместо Math.random()

// Числовая прямая
const generateNumberLine = () => {
  const pos = Math.floor(random() * 9) + 1;
  return {
    question: 'Сан түзуінде көрсетілген бөлшек қандай?',
    correctAnswer: `${pos}/10`,
    visualData: { type: 'numberline', numberline: { min: 0, max: 1, divisions: 11, markedPosition: pos } },
  };
};

// Дробная полоска
const generateFractionBar = () => {
  const totals = [3,4,5,6,8];
  const total = totals[Math.floor(random() * totals.length)];
  const filled = Math.floor(random() * total) + 1;
  return {
    question: 'Боялған бөлігі қай бөлшекке тең?',
    correctAnswer: `${filled}/${total}`,
    visualData: { type: 'fractionbar', fractionBar: { total, filled } },
  };
};

// Фигуры (звёзды, круги и т.д.)
const generateShapes = () => {
  const types = [
    { name: 'шеңберлер', color: '#3b82f6' },
    { name: 'жұлдыздар', color: '#f59e0b' },
  ];
  const shapes = [0, 1, 1, 0, 1]; // 2 круга, 3 звезды
  return {
    question: 'Фигуралардың қандай бөлшегі жұлдыздар?',
    correctAnswer: '3/5',
    visualData: {
      type: 'shapes',
      shapes: {
        items: shapes.map(i => ({ type: types[i].name, color: types[i].color })),
        targetType: 'жұлдыздар',
        targetCount: 3,
        totalCount: 5,
      },
    },
  };
};
```

---

## 3.5. РЕЖИМ ПРОСМОТРА ОШИБОК (АНАЛИТИКА / REVIEW MODE)

Для того чтобы учитель или ученик в аналитике могли увидеть, какую ошибку совершил ученик:
1. **Проверьте наличие `window.reviewMode`** при старте плагина.
2. **Отключите интерактивность:** если `isReview` равен `true`, пользователь не должен иметь возможности кликать по кнопкам, менять значения, перетаскивать элементы или вводить данные (`disabled={isReview}`).
3. **Общие визуальные требования:**
   - **Фон задачи** должен быть строго белым (`#ffffff`).
   - Используйте фирменные цвета сайта в кодах:
     - Зеленый (основной бренд): `#38B000`
     - Голубой (окружение ученика): `#0ea5e9`
     - Синий/Бирюзовый (окружение учителя): `#00ACC1`
     - Оранжевый (акценты): `#f97316`
     - Светло-серый (фоны блоков): `#f8f9fa`
     - Успех (зеленый): `#10B981`
     - Ошибка (красный): `#EF4444`

4. **Отображение ответа ученика и правильного ответа в `isReview`:**

   ### Вариант 1: Если вопрос имеет ПОЛЕ ВВОДА ОТВЕТА (текстовое/числовое поле ввода):
   Плагин должен отображать три отдельных блока друг под другом:
   - **Картинка/Контейнер вопроса:** Показывает только сам вопрос и визуальные условия (без ответов).
   - **Ответ ученика:** Показывает *только* поле ввода с ответом, который ввёл ученик. Если ответ неверный — обвести поле рамкой цвета Ошибки (`#EF4444`), если верный — рамкой цвета Успеха (`#10B981`).
   - **Правильный ответ:** Показывает *только* поле ввода с правильным ответом, обведенное зеленой рамкой Успеха (`#10B981`).

   ### Вариант 2: Если вопрос ИНТЕРАКТИВНЫЙ (drag-and-drop, перетаскивание, закрашивание клеток, выбор на числовой прямой и т.д.):
   Плагин должен предоставить полную визуализацию ответов:
   - **Полный вопрос:** Стартовое/чистое состояние задачи.
   - **Ответ ученика (полная картинка):** Полное визуальное состояние задачи, как её решил ученик (с расставленными им объектами, закрашенными им клетками и т.д.), обведенное рамкой цвета Успеха (`#10B981`) или Ошибки (`#EF4444`).
   - **Правильный ответ (полная картинка):** Полное визуальное состояние задачи с правильным решением (правильно расставленные объекты, правильно закрашенные клетки и т.д.), обведенное рамкой цвета Успеха (`#10B981`).

Пример разметки интерактивной сетки в режиме просмотра:
```tsx
const isSelected = selectedCells.has(cellId);
const isCorrectAnswerCell = isReview && correctCells.has(cellId);

let cellClass = "w-8 h-8 border ";
if (isReview) {
  if (isSelected) {
    cellClass += isCorrect ? "bg-green-400 border-green-500" : "bg-red-400 border-red-500";
  } else if (isCorrectAnswerCell) {
    cellClass += "bg-green-200 border-green-300"; // Показываем правильный ответ
  } else {
    cellClass += "bg-white border-gray-200";
  }
}
```

---

## 4. ПРАВИЛА

✅ **Разрешено:**
- React + TypeScript (.tsx)
- Tailwind CSS
- lucide-react иконки
- Один вопрос за раз

❌ **Запрещено:**
- Внешние зависимости
- Прогресс-бары, счётчики ("Вопрос 3 из 10")
- Score, статистика
- Кнопки навигации, «На главную», «Выйти», «Назад» и т.д. (плагин должен содержать ТОЛЬКО саму интерактивную задачу и её элементы ввода)
- Менять структуру postMessage
- **Использовать `Math.random()` напрямую — ТОЛЬКО `random()` из seed!**

---

## ЧЕКЛИСТ

- [ ] Есть картинка в вопросе? → `visualData` в Problem + `questionData` в postMessage
- [ ] `question` заполнен
- [ ] `handleSubmit` отправляет postMessage
- [ ] `sendHeight()` вызывается
- [ ] UI на казахском
- [ ] НЕТ прогресс-баров и счётчиков
- [ ] НЕТ кнопок навигации («На главную», «Назад» и т.д.)
- [ ] **Используется `createSeededRandom(seed)` вместо `Math.random()`**
- [ ] **Поддержан `frozen` режим (`isFrozen`) — кнопки скрыты/отключены**
- [ ] **`Math.random()` НЕ используется нигде в коде**

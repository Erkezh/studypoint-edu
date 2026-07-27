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
  const containerRef = useRef<HTMLDivElement>(null);

  // ⚠️ Режим просмотра ошибок (аналитика для учителя/ученика)
  const reviewMode = (window as any).reviewMode || null;
  const isReview = !!reviewMode;

  const generateProblem = (): Problem => ({
    id: Date.now(),
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
        id: Date.now(),
        question: 'Сұрақ мәтіні',
        correctAnswer: reviewMode.correctAnswer,
        // Если visualData нужна для отрисовки, родитель может передать ее в reviewMode.questionData
        visualData: reviewMode.questionData
      });
      setUserAnswer(reviewMode.studentAnswer);
      
      // Восстановите внутреннее состояние (например, закрашенные ячейки, выбранные кнопки)
      // на основе reviewMode.studentAnswer!
      
      setShowResult(true);
    } else {
      setProblem(generateProblem());
    }
  }, []);

  useEffect(() => { sendHeight(); setTimeout(sendHeight, 100); }, [problem, showResult]);

  const handleSubmit = () => {
    if (isReview || !userAnswer || !problem) return;
    const isCorrect = userAnswer === problem.correctAnswer;
    
    window.parent.postMessage({
      type: 'exercise-result',
      isCorrect,
      question: problem.question,
      userAnswer,
      correctAnswer: problem.correctAnswer,
      questionData: problem.visualData,  // ⚠️ Передаём картинку!
    }, '*');
    
    setShowResult(true);
  };

  const handleNext = () => {
    setProblem(generateProblem());
    setUserAnswer('');
    setShowResult(false);
  };

  return (
    <div ref={containerRef} className="p-4 bg-white rounded-xl">
      {/* ⚠️ В режиме isReview отключайте любые клики и ввод: disabled={isReview} */}
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

### Примеры генерации:

```tsx
// Числовая прямая
const generateNumberLine = () => {
  const pos = Math.floor(Math.random() * 9) + 1;
  return {
    question: 'Сан түзуінде көрсетілген бөлшек қандай?',
    correctAnswer: `${pos}/10`,
    visualData: { type: 'numberline', numberline: { min: 0, max: 1, divisions: 11, markedPosition: pos } },
  };
};

// Дробная полоска
const generateFractionBar = () => {
  const total = [3,4,5,6,8][Math.floor(Math.random() * 5)];
  const filled = Math.floor(Math.random() * total) + 1;
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
3. **Восстановите состояние ученика:** распарсите ответ ученика из `window.reviewMode.studentAnswer` (например, отметьте те же клетки сетки, выберите ту же опцию или покажите число на прямой) и покажите его.
4. **Покажите правильный ответ:**
   - Если ответ ученика верный (`reviewMode.isCorrect === true`), выделите его зеленым цветом (рамка, заливка).
   - Если ответ неверный, выделите неверный ответ ученика красной рамкой/заливкой, а правильный ответ из `reviewMode.correctAnswer` подсветите зеленой рамкой/заливкой.

Пример разметки сетки:
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
- Менять структуру postMessage

---

## ЧЕКЛИСТ

- [ ] Есть картинка в вопросе? → `visualData` в Problem + `questionData` в postMessage
- [ ] `question` заполнен
- [ ] `handleSubmit` отправляет postMessage
- [ ] `sendHeight()` вызывается
- [ ] UI на казахском
- [ ] НЕТ прогресс-баров и счётчиков

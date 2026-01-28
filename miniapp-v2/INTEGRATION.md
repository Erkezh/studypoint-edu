# Интеграция miniapp-v2 с PracticeSession

Эта документация описывает, как использовать упражнения из папки `miniapp-v2` в вопросах типа PLUGIN в PracticeSession.

## Как это работает

PracticeSession.vue теперь поддерживает два типа PLUGIN вопросов:

1. **Обычные плагины** - загружаются из `/static/plugins/${id}/${ver}/${entry}`
2. **TSX плагины из miniapp-v2** - загружаются из папки `miniapp-v2/exercieses/` и трансформируются в браузер-готовый код

## Настройка вопроса для использования TSX плагина

Чтобы использовать TSX упражнение из miniapp-v2, в данных вопроса (question.data) нужно указать один из следующих параметров:

### Вариант 1: Использовать поле `tsx_file`
```json
{
  "type": "PLUGIN",
  "data": {
    "tsx_file": "/miniapp-v2/exercieses/fraction_comparison_app.tsx"
  }
}
```

### Вариант 2: Использовать поле `miniapp_file`
```json
{
  "type": "PLUGIN",
  "data": {
    "miniapp_file": "exercieses/fraction_comparison_app.tsx"
  }
}
```

### Вариант 3: Использовать `entry` с расширением `.tsx`
```json
{
  "type": "PLUGIN",
  "data": {
    "plugin_id": "fraction-comparison",
    "entry": "fraction_comparison_app.tsx"
  }
}
```

В этом случае путь будет автоматически сформирован как `/miniapp-v2/exercieses/${entry}`

## Формат TSX файлов

TSX файлы должны быть в формате React компонентов, как в Claude Artifacts:

```tsx
import React, { useState } from 'react';
import { Check, X } from 'lucide-react';

const MyExercise = () => {
  const [userAnswer, setUserAnswer] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const correctAnswer = '>';

  const handleSubmit = () => {
    if (!userAnswer) return;
    setShowResult(true);
    // postMessage будет автоматически добавлен трансформатором
  };

  return (
    <div>
      {/* Ваш UI */}
    </div>
  );
};

export default MyExercise;
```

## Автоматическая инъекция postMessage

Трансформатор автоматически добавляет `postMessage` в функцию `handleSubmit` для отправки результатов в PracticeSession:

```javascript
window.parent.postMessage({
  type: "exercise-result",
  id: null,
  correctAnswer: problems[currentIndex].correctAnswer,
  studentAnswer: userAnswer,
  isCorrect: __isCorrect
}, "*");
```

## Поддерживаемые импорты

Трансформатор автоматически обрабатывает следующие импорты:

- `import React, { useState, useEffect } from 'react'` → `const { useState, useEffect } = React`
- `import { Check, X } from 'lucide-react'` → `const { Check, X } = window.lucideReact`

## Отправка ответа

TSX плагины автоматически отправляют ответ через `postMessage` при вызове `handleSubmit`. Кнопка "Жіберу" не отображается для TSX плагинов, так как отправка происходит автоматически.

## Пример полного вопроса

```json
{
  "id": 123,
  "type": "PLUGIN",
  "prompt": "Сравните дроби",
  "level": 1,
  "data": {
    "tsx_file": "/miniapp-v2/exercieses/fraction_comparison_app.tsx",
    "height": 400
  }
}
```

## Отладка

В режиме разработки (`import.meta.env.DEV`) в консоль выводятся логи:
- Загрузка TSX файла
- Трансформация кода
- Получение сообщений от плагина

## Ограничения

1. TSX файлы должны быть самодостаточными React компонентами
2. Используются только UMD версии библиотек (React, Tailwind, Lucide)
3. Все иконки должны быть из lucide-react
4. Файлы должны быть доступны через HTTP (не требуют сборки)

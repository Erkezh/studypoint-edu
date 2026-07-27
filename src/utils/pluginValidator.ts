export interface PluginCheckIssue {
  code: string
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
  title: string
  description: string
  fix_prompt: string
}

export interface PluginCheckResult {
  isValid: boolean
  issues: PluginCheckIssue[]
  warnings: PluginCheckIssue[]
  passed: string[]
  aiPrompt: string
}

export const validatePluginCode = (code: string): PluginCheckResult => {
  const issues: PluginCheckIssue[] = []
  const warnings: PluginCheckIssue[] = []
  const passed: string[] = []

  // 1. Check Seed & PRNG (CRITICAL FOR TEACHER/STUDENT CONSISTENCY)
  const hasSeedParam = /urlParams\.(get|has)\(['"]seed['"]|searchParams\.(get|has)\(['"]seed['"]|seed/i.test(code)
  const hasSeededPrng = /createSeededRandom|Mulberry32|lcg|seededRandom|seedRandom|alea|pseudoRandom/i.test(code)
  const usesRawMathRandom = /Math\.random\s*\(\s*\)/.test(code)

  if (usesRawMathRandom) {
    issues.push({
      code: 'USES_MATH_RANDOM_CRITICAL',
      severity: 'CRITICAL',
      title: 'Обнаружен прямой вызов Math.random() (Оқушы мұғалім таңдаған сұрақты көрмейді!)',
      description: 'В коде присутствует Math.random(). Вызов Math.random() приводит к тому, что у ученика генерируется ДРУГОЙ вопрос, отличающийся от вопроса учителя!',
      fix_prompt: 'Замени ВСЕ вызовы `Math.random()` в генераторе условий задачи на вызовы детерминированного PRNG `rng()` (созданного через `createSeededRandom(seed)`).'
    })
  }

  if (!hasSeedParam) {
    issues.push({
      code: 'MISSING_SEED_PARAM',
      severity: 'CRITICAL',
      title: 'Параметр `seed` не считывается из URL',
      description: 'Плагин не считывает параметр `?seed=...` из URL. Из-за этого у ученика выводится случайный вопрос, а не тот, который выбыл/выбрал учитель!',
      fix_prompt: 'Добавь считывание параметра `seed`: `const seedParam = urlParams.get("seed"); const seed = seedParam ? parseInt(seedParam, 10) : 12345;`'
    })
  } else if (!hasSeededPrng) {
    issues.push({
      code: 'MISSING_SEEDED_PRNG',
      severity: 'CRITICAL',
      title: 'Отсутствует детерминированный генератор PRNG на основе seed',
      description: 'В коде нет функции `createSeededRandom(seed)` (или Mulberry32). Использование чистой `Math.random()` приводит к генерации разных вопросов у учителя и ученика!',
      fix_prompt: 'Добавь детерминированный PRNG (например Mulberry32) и создай генератор `const rng = createSeededRandom(seed);`. Используй `rng()` для ВСЕХ случайных чисел задачи вместо `Math.random()`:\n```js\nfunction createSeededRandom(seed) {\n  let s = seed % 2147483647;\n  if (s <= 0) s += 2147483646;\n  return function() {\n    s = (s * 16807) % 2147483647;\n    return (s - 1) / 2147483646;\n  };\n}\n```'
    })
  } else {
    passed.push('Детерминированная генерация по `seed` и PRNG реализованы правильно.')
  }

  // 2. Check 5 Difficulty Levels (level=1..5)
  const hasLevelParam = /urlParams\.(get|has)\(['"]level['"]|searchParams\.(get|has)\(['"]level['"]|level/i.test(code)

  if (!hasLevelParam) {
    issues.push({
      code: 'MISSING_LEVEL_PARAM',
      severity: 'HIGH',
      title: 'Параметр `level` не считывается из URL',
      description: 'Плагин не получает параметр уровня сложности `?level=1..5`.',
      fix_prompt: 'Добавь получение уровня сложности: `const level = parseInt(urlParams.get("level") || "1", 10);` и реализуй 5 уровней сложности генерируемых чисел/задач от 1 (базовый) до 5 (олимпиадный).'
    })
  } else {
    passed.push('Поддержка 5 уровней сложности `?level=1..5` присутствует.')
  }

  // 3. Check Frozen Mode
  const hasFrozenCheck = /frozen/i.test(code)
  if (!hasFrozenCheck) {
    issues.push({
      code: 'MISSING_FROZEN_MODE',
      severity: 'HIGH',
      title: 'Отсутствует поддержка режима `frozen` (замороженное превью)',
      description: 'При создании квиза в конструкторе плагин должен отключать кнопкам/полям ввода интерактивность (`pointer-events: none`).',
      fix_prompt: 'Добавь обработку `frozen`: `const isFrozen = urlParams.get("frozen") === "1";`. Если `isFrozen === true`, отключи все поля ввода (`disabled`) и добавь `pointer-events: none` к интерактивным контейнерам. Сохраняй 100% оригинальную яркость цвета (opacity: 1).'
    })
  } else {
    passed.push('Режим замороженного превью `?frozen=1` поддерживается.')
  }

  // 4. Check Mode (quiz, review)
  const hasModeCheck = /mode/i.test(code)
  if (!hasModeCheck) {
    warnings.push({
      code: 'MISSING_MODE_PARAM',
      severity: 'LOW',
      title: 'Не найдено считывание параметра `mode`',
      description: 'Рекомендуется считывать `const mode = urlParams.get("mode");` ("quiz" или "review").',
      fix_prompt: 'Считывай `const mode = urlParams.get("mode") || "quiz";`. В режиме `mode=quiz` не показывай вердикт до отправки.'
    })
  } else {
    passed.push('Обработка параметра `mode` присутствует.')
  }

  // 5. Check postMessage API & SERVER_RESULT
  const hasStudentAnswer = /STUDENT_ANSWER/.test(code)
  const hasHeightChange = /HEIGHT_CHANGE/.test(code)
  const hasMessageListener = /addEventListener\s*\(\s*['"]message['"]|window\.onmessage/.test(code)
  const hasUnsafeServerResult = /setIsCorrect\s*\(\s*!!\s*serverIsCorrect\s*\)/.test(code)
  const readsStudentAnswer = /studentAnswer/.test(code)

  if (!readsStudentAnswer) {
    warnings.push({
      code: 'MISSING_STUDENT_ANSWER_READ',
      severity: 'MEDIUM',
      title: 'Параметр `studentAnswer` не считывается из URL в режиме аналитики',
      description: 'При просмотре аналитики в `mode=review` плагин должен показывать ответ ученика из `urlParams.get("studentAnswer")`.',
      fix_prompt: 'Добавь считывание ответа ученика: `const studentAns = urlParams.get("studentAnswer");`. Если он передан в `mode=review`, выводи сохраненный ответ ученика.'
    })
  } else {
    passed.push('Считывание `studentAnswer` для режима аналитики настроено.')
  }

  if (hasUnsafeServerResult) {
    issues.push({
      code: 'UNSAFE_SERVER_RESULT',
      severity: 'HIGH',
      title: 'Опасное приведение `!!serverIsCorrect` в обработчике SERVER_RESULT',
      description: 'Приведение `!!undefined` ошибочно превращает правильный ответ ученика в "Қате" внутри iFrame!',
      fix_prompt: 'Проверяй тип перед обновлением состояния: `if (typeof serverIsCorrect === "boolean") { setIsCorrect(serverIsCorrect); }`.'
    })
  }

  if (!hasStudentAnswer) {
    issues.push({
      code: 'MISSING_STUDENT_ANSWER_POSTMESSAGE',
      severity: 'CRITICAL',
      title: 'Отсутствует отправка postMessage `STUDENT_ANSWER`',
      description: 'Платформа не получает ответ ученика и не может сохранить его!',
      fix_prompt: 'При каждом изменении/вводе ответа отправляй событие родителю:\n```js\nwindow.parent.postMessage({\n  type: "STUDENT_ANSWER",\n  answer: { value: currentAnswer },\n  isComplete: true\n}, "*");\n```'
    })
  } else {
    passed.push('Отправка `STUDENT_ANSWER` postMessage настроена.')
  }

  if (!hasHeightChange) {
    warnings.push({
      code: 'MISSING_HEIGHT_CHANGE',
      severity: 'LOW',
      title: 'Отсутствует отправка `HEIGHT_CHANGE`',
      description: 'Рекомендуется отправлять измеряемую высоту iFrame родителю, чтобы убрать полосу прокрутки.',
      fix_prompt: 'Отправляй высоту iframe: `window.parent.postMessage({ type: "HEIGHT_CHANGE", height: document.body.scrollHeight }, "*");`'
    })
  }

  if (!hasMessageListener) {
    warnings.push({
      code: 'MISSING_MESSAGE_LISTENER',
      severity: 'MEDIUM',
      title: 'Отсутствует слушатель `window.addEventListener("message")`',
      description: 'Плагин должен слушать сообщения `SERVER_RESULT` и `SHOW_ANSWER` от платформы.',
      fix_prompt: 'Добавь слушатель сообщений:\n```js\nwindow.addEventListener("message", (event) => {\n  const { type, correctAnswer, showCorrectAnswer } = event.data || {};\n  if (type === "SHOW_ANSWER" || showCorrectAnswer) {\n    // Показать решение\n  }\n});\n```'
    })
  }

  const isValid = issues.length === 0

  // Build AI Prompt
  let aiPrompt = ''
  if (!isValid || warnings.length > 0) {
    const lines = [
      '# 🚨 ИСПРАВЛЕНИЕ ОШИБОК ПЛАГИНА (STUDYPOINT IXL CONTRACT)',
      '',
      'Пожалуйста, исправь HTML/JS код плагина в соответствии с регламентом PLUGIN_PROMPT_TEMPLATE.md.',
      'Ниже перечислены конкретные критические ошибки и предупреждения, обнаруженные автоматическим чекером:',
      ''
    ]
    let count = 1
    if (issues.length > 0) {
      lines.push('### 🔴 КРИТИЧЕСКИЕ ОШИБКИ (ОБЯЗАТЕЛЬНО К ИСПРАВЛЕНИЮ):')
      issues.forEach(i => {
        lines.push(`#### ${count}. ${i.title} (\`${i.code}\`)`)
        lines.push(`**Описание:** ${i.description}`)
        lines.push(`**Инструкция по исправлению:**\n${i.fix_prompt}\n`)
        count++
      })
    }
    if (warnings.length > 0) {
      lines.push('### ⚠️ РЕКОМЕНДАЦИИ И ПРЕДУПРЕЖДЕНИЯ:')
      warnings.forEach(w => {
        lines.push(`#### ${count}. ${w.title} (\`${w.code}\`)`)
        lines.push(`**Описание:** ${w.description}`)
        lines.push(`**Инструкция по исправлению:**\n${w.fix_prompt}\n`)
        count++
      })
    }
    lines.push('---')
    lines.push('ПОЖАЛУЙСТА, ПРЕДОСТАВЬ ПОЛНОСТЬЮ ИСПРАВЛЕННЫЙ HTML ФАЙЛ ПЛАГИНА СО ВСЕМИ ПРАВКАМИ.')
    aiPrompt = lines.join('\n')
  }

  return {
    isValid,
    issues,
    warnings,
    passed,
    aiPrompt
  }
}

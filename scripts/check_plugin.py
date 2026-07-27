#!/usr/bin/env python3
"""
StudyPoint IXL Plugin Checker & Validator
Validates plugin index.html files against PLUGIN_PROMPT_TEMPLATE.md rules.
Generates an audit report and a copyable AI prompt to automatically fix issues.
"""

import sys
import os
import re
import json

def find_use_effects_with_empty_deps(code: str) -> list[str]:
    # Find all occurrences of "useEffect"
    results = []
    for match in re.finditer(r"\buseEffect\b", code):
        start_idx = match.start()
        # Find the opening parenthesis of useEffect(
        paren_start = code.find("(", start_idx)
        if paren_start == -1 or paren_start - start_idx > 20:
            continue
        
        # Parse matching parenthesis and brackets to extract the second argument
        # We search for the end of the first argument (which is a callback function)
        # and see if the second argument is []
        depth = 0
        in_string = None
        escape = False
        callback_end = -1
        
        for i in range(paren_start + 1, len(code)):
            char = code[i]
            if escape:
                escape = False
                continue
            if char == "\\":
                escape = True
                continue
            if in_string:
                if char == in_string:
                    in_string = None
                continue
            if char in ('"', "'", "`"):
                in_string = char
                continue
            
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    callback_end = i
                    break
                depth -= 1
        
        if callback_end != -1:
            # Parse from paren_start to callback_end with depth
            comma_idx = -1
            bracket_depth = 0
            paren_depth = 0
            in_str = None
            esc = False
            for j in range(paren_start + 1, callback_end):
                c = code[j]
                if esc:
                    esc = False
                    continue
                if c == "\\":
                    esc = True
                    continue
                if in_str:
                    if c == in_str:
                        in_str = None
                    continue
                if c in ('"', "'", "`"):
                    in_str = c
                    continue
                if c == "(":
                    paren_depth += 1
                elif c == ")":
                    paren_depth -= 1
                elif c == "[":
                    bracket_depth += 1
                elif c == "]":
                    bracket_depth -= 1
                elif c == "," and paren_depth == 0 and bracket_depth == 0:
                    comma_idx = j
            
            if comma_idx != -1:
                second_arg = code[comma_idx+1:callback_end].strip()
                if second_arg in ("[]", "[\n]", "[ ]"):
                    callback_body = code[paren_start+1:comma_idx]
                    results.append(callback_body)
    return results


def analyze_plugin_code(html_code: str):
    issues = []
    warnings = []
    passed = []

    # 1. Check Seed & PRNG (CRITICAL FOR STUDENT/TEACHER QUESTION CONSISTENCY)
    has_seed_param = bool(re.search(r"urlParams\.(get|has)\(['\"]seed['\"]", html_code) or re.search(r"searchParams\.(get|has)\(['\"]seed['\"]", html_code) or re.search(r"seed", html_code, re.IGNORECASE))
    has_seeded_prng = bool(re.search(r"createSeededRandom|Mulberry32|lcg|seededRandom|seedRandom|alea|pseudoRandom", html_code, re.IGNORECASE))
    uses_raw_math_random = bool(re.search(r"Math\.random\s*\(\s*\)", html_code))

    if uses_raw_math_random:
        issues.append({
            "code": "USES_MATH_RANDOM_CRITICAL",
            "severity": "CRITICAL",
            "title": "Обнаружен прямой вызов Math.random() (Оқушы мұғалім таңдаған сұрақты көрмейді!)",
            "description": "В коде присутствует Math.random(). Вызов Math.random() приводит к тому, что у ученика сгенерируется ДРУГОЙ вопрос, отличающийся от вопроса учителя!",
            "fix_prompt": "Замени ВСЕ вызовы `Math.random()` в генераторе условий задачи на вызовы детерминированного PRNG `rng()` (созданного через `createSeededRandom(seed)`)."
        })

    if not has_seed_param:
        issues.append({
            "code": "MISSING_SEED_PARAM",
            "severity": "CRITICAL",
            "title": "Параметр `seed` не считывается из URL",
            "description": "Плагин не считывает параметр `?seed=...` из URL. Из-за этого у ученика открывается случайный вопрос, а не тот, который выбрал/сгенерировал учитель!",
            "fix_prompt": "Добавь считывание параметра `seed`: `const seedParam = urlParams.get('seed'); const seed = seedParam ? parseInt(seedParam, 10) : 12345;`"
        })
    elif not has_seeded_prng:
        issues.append({
            "code": "MISSING_SEEDED_PRNG",
            "severity": "CRITICAL",
            "title": "Отсутствует детерминированный генератор PRNG на основе seed",
            "description": "В коде нет функции `createSeededRandom(seed)` (или Mulberry32). Использование обычной `Math.random()` приводит к генерации РАЗНЫХ вопросов у учителя и ученика!",
            "fix_prompt": "Добавь детерминированный PRNG (например Mulberry32) и создай генератор `const rng = createSeededRandom(seed);`. Используй `rng()` для ВСЕХ случайных чисел задачи вместо `Math.random()`:\n```js\nfunction createSeededRandom(seed) {\n  let s = seed % 2147483647;\n  if (s <= 0) s += 2147483646;\n  return function() {\n    s = (s * 16807) % 2147483647;\n    return (s - 1) / 2147483646;\n  };\n}\n```"
        })
    else:
        passed.append("Детерминированная генерация по `seed` и PRNG реализованы правильно.")

    # 2. Check 5 Difficulty Levels (level=1..5)
    has_level_param = bool(re.search(r"urlParams\.(get|has)\(['\"]level['\"]", html_code) or re.search(r"searchParams\.(get|has)\(['\"]level['\"]", html_code))

    if not has_level_param:
        issues.append({
            "code": "MISSING_LEVEL_PARAM",
            "severity": "HIGH",
            "title": "Параметр `level` не считывается из URL",
            "description": "Плагин не получает параметр уровня сложности `?level=1..5`.",
            "fix_prompt": "Добавь получение уровня сложности: `const level = parseInt(urlParams.get('level') || '1', 10);` и реализуй 5 уровней сложности генерируемых чисел/задач от 1 (базовый) до 5 (олимпиадный)."
        })
    else:
        passed.append("Поддержка уровня сложности `?level=1..5` присутствует.")

    # 3. Check Frozen Mode
    has_frozen_check = bool(re.search(r"frozen", html_code, re.IGNORECASE))
    if not has_frozen_check:
        issues.append({
            "code": "MISSING_FROZEN_MODE",
            "severity": "HIGH",
            "title": "Отсутствует поддержка режима `frozen` (замороженное превью)",
            "description": "При создании квиза в конструкторе плагин должен отключать кнопкам/полям ввода интерактивность (`pointer-events: none`).",
            "fix_prompt": "Добавь обработку `frozen`: `const isFrozen = urlParams.get('frozen') === '1';`. Если `isFrozen === true`, отключи все поля ввода (`disabled`) и добавь `pointer-events: none` к интерактивным контейнерам. Сохраняй 100% оригинальную яркость цвета (opacity: 1)."
        })
    else:
        passed.append("Режим замороженного превью `?frozen=1` поддерживается.")

    # 4. Check Mode (quiz, review)
    has_mode_check = bool(re.search(r"mode", html_code, re.IGNORECASE))
    if not has_mode_check:
        warnings.append({
            "code": "MISSING_MODE_PARAM",
            "title": "Не найдено считывание параметра `mode`",
            "description": "Рекомендуется считывать `const mode = urlParams.get('mode');` ('quiz' или 'review').",
            "fix_prompt": "Считывай `const mode = urlParams.get('mode') || 'quiz';`. В режиме `mode=quiz` не показывай вердикт до отправки."
        })
    else:
        passed.append("Обработка параметра `mode` присутствует.")

    # 5. Check React useEffect dependencies for seed/level (CRITICAL)
    empty_deps_effects = find_use_effects_with_empty_deps(html_code)
    has_empty_deps_generating_problem = False
    for effect_body in empty_deps_effects:
        if "generateProblem" in effect_body or "problem" in effect_body or "seed" in effect_body:
            has_empty_deps_generating_problem = True
            break
            
    if has_empty_deps_generating_problem:
        issues.append({
            "code": "MISSING_REACT_EFFECT_DEPENDENCIES",
            "severity": "CRITICAL",
            "title": "Пустой массив зависимостей [] в React useEffect для генерации задачи",
            "description": "Массив зависимостей в useEffect для генерации задачи пуст []. Из-за этого при изменении уровня (level) или сида (seed) плагин не перегенерирует задачу, оқушы бір сұрақта қалып қояды!",
            "fix_prompt": "Укажите правильные зависимости в массиве React useEffect: `}, [level, seed]);` вместо `}, []);`."
        })
    else:
        passed.append("Зависимости в массиве React `useEffect` указаны правильно.")

    # 6. Check postMessage API & SERVER_RESULT
    has_student_answer = bool(re.search(r"STUDENT_ANSWER", html_code))
    has_height_change = bool(re.search(r"HEIGHT_CHANGE", html_code))
    has_message_listener = bool(re.search(r"addEventListener\s*\(\s*['\"]message['\"]|window\.onmessage", html_code))
    has_unsafe_server_result = bool(re.search(r"setIsCorrect\s*\(\s*!!\s*serverIsCorrect\s*\)", html_code))
    reads_student_answer = bool(re.search(r"studentAnswer", html_code) or re.search(r"userAnswer", html_code))
    reads_question_data = bool(re.search(r"questionData", html_code) and (re.search(r"urlParams\.(get|has)\(['\"]questionData['\"]", html_code) or re.search(r"searchParams\.(get|has)\(['\"]questionData['\"]", html_code)))
    has_exercise_result = bool(re.search(r"exercise-result", html_code))
    has_exercise_result_user_answer = bool(re.search(r"userAnswer\s*:", html_code) or re.search(r"user_answer\s*:", html_code))
    has_explanation_ui = bool(re.search(r"Түсіндірме|Шешуі|explanation|solution", html_code, re.IGNORECASE))

    if not reads_student_answer:
        issues.append({
            "code": "MISSING_STUDENT_ANSWER_READ",
            "severity": "CRITICAL",
            "title": "Параметр `studentAnswer` не считывается из URL в режиме аналитики",
            "description": "При просмотре аналитики в `mode=review` плагин должен показывать ответ ученика из `urlParams.get('studentAnswer')`. Из-за этого при ошибочном ответе аналитика не видит ответ ученика!",
            "fix_prompt": "Добавь считывание ответа ученика: `const studentAns = urlParams.get('studentAnswer') || urlParams.get('userAnswer');`. Если он передан в `mode=review`, выводи сохраненный ответ ученика."
        })
    else:
        passed.append("Считывание `studentAnswer` для режима аналитики настроено.")

    if not has_exercise_result:
        issues.append({
            "code": "MISSING_EXERCISE_RESULT",
            "severity": "CRITICAL",
            "title": "Отсутствует событие postMessage `exercise-result`",
            "description": "При проверке ответа плагин должен отправлять `exercise-result` с `userAnswer`, `isCorrect`, `correctAnswer`, `questionData`.",
            "fix_prompt": "Добавь отправку результата: `window.parent.postMessage({ type: 'exercise-result', isCorrect, userAnswer, correctAnswer, questionData }, '*');`."
        })
    elif not has_exercise_result_user_answer:
        issues.append({
            "code": "MISSING_EXERCISE_RESULT_USER_ANSWER",
            "severity": "CRITICAL",
            "title": "В `exercise-result` не передаётся поле `userAnswer`",
            "description": "Без поля `userAnswer` система не сохраняет ответ ученика при ошибке!",
            "fix_prompt": "Обязательно добавь `userAnswer: currentAnswer` в объект сообщения `exercise-result`."
        })

    if not has_explanation_ui:
        warnings.append({
            "code": "MISSING_INLINE_EXPLANATION_UI",
            "title": "В плагине не найден текст пошагового объяснения ('Түсіндірме' / 'Шешуі')",
            "description": "Плагин должен сам показывать пошаговое решение ('Түсіндірме') на казахском языке внутри iFrame при проверке ответа.",
            "fix_prompt": "Добавь блок с объяснением решения задач на казахском языке: `<div className=\"explanation\"><strong>Түсіндірме:</strong> ...</div>`."
        })
    else:
        passed.append("Внутренний блок объяснения решения (Түсіндірме) присутствует.")

    if not reads_question_data:
        issues.append({
            "code": "MISSING_QUESTION_DATA_READ",
            "severity": "CRITICAL",
            "title": "Отсутствует считывание `questionData` из URL для восстановления вопроса",
            "description": "Плагин не считывает параметр `?questionData=...` из URL. Без этого в режиме аналитики (review) невозможно восстановить точное условие вопроса, на который отвечал ученик, если отсутствует или сбросился seed!",
            "fix_prompt": "Добавь получение данных вопроса из URL: `const qDataParam = urlParams.get('questionData');` и при наличии распарсенного объекта восстанови условие задачи напрямую из него в `useEffect(() => { ... }, [level, seed, qDataParam])`."
        })
    else:
        passed.append("Считывание `questionData` для режима аналитики настроено.")

    if has_unsafe_server_result:
        issues.append({
            "code": "UNSAFE_SERVER_RESULT",
            "severity": "HIGH",
            "title": "Опасное приведение `!!serverIsCorrect` в обработчике SERVER_RESULT",
            "description": "Приведение `!!undefined` ошибочно превращает правильный ответ ученика в 'Қате' внутри iFrame!",
            "fix_prompt": "Проверяй тип перед обновлением состояния: `if (typeof serverIsCorrect === 'boolean') { setIsCorrect(serverIsCorrect); }`."
        })

    if not has_student_answer:
        issues.append({
            "code": "MISSING_STUDENT_ANSWER_POSTMESSAGE",
            "severity": "CRITICAL",
            "title": "Отсутствует отправка postMessage `STUDENT_ANSWER`",
            "description": "Платформа не получает ответ ученика и не может сохранить его!",
            "fix_prompt": "При каждом изменении/вводе ответа отправляй событие родителю:\n```js\nwindow.parent.postMessage({\n  type: 'STUDENT_ANSWER',\n  answer: { value: currentAnswer },\n  isComplete: true\n}, '*');\n```"
        })
    else:
        passed.append("Отправка `STUDENT_ANSWER` postMessage настроена.")

    if not has_height_change:
        warnings.append({
            "code": "MISSING_HEIGHT_CHANGE",
            "title": "Отсутствует отправка `HEIGHT_CHANGE`",
            "description": "Рекомендуется отправлять измеряемую высоту iFrame родителю, чтобы убрать полосу прокрутки.",
            "fix_prompt": "Отправляй высоту iframe: `window.parent.postMessage({ type: 'HEIGHT_CHANGE', height: document.body.scrollHeight }, '*');`"
        })

    if not has_message_listener:
        warnings.append({
            "code": "MISSING_MESSAGE_LISTENER",
            "title": "Отсутствует слушатель `window.addEventListener('message')`",
            "description": "Плагин должен слушать сообщения `SERVER_RESULT` и `SHOW_ANSWER` от платформы.",
            "fix_prompt": "Добавь слушатель сообщений:\n```js\nwindow.addEventListener('message', (event) => {\n  const { type, correctAnswer, showCorrectAnswer } = event.data || {};\n  if (type === 'SHOW_ANSWER' || showCorrectAnswer) {\n    // Показать решение\n  }\n});\n```"
        })

    return {
        "issues": issues,
        "warnings": warnings,
        "passed": passed
    }

def generate_ai_prompt(analysis: dict, file_name: str = "index.html") -> str:
    issues = analysis["issues"]
    warnings = analysis["warnings"]

    if not issues and not warnings:
        return "✅ Плагин полностью соответствует всем требованиям регламента PLUGIN_PROMPT_TEMPLATE.md! Ошибок не обнаружено."

    prompt_lines = [
        f"# 🚨 ИСПРАВЛЕНИЕ ОШИБОК ПЛАГИНА `{file_name}` (STUDYPOINT IXL CONTRACT)",
        "",
        "Пожалуйста, исправь HTML/JS код плагина в соответствии с регламентом `PLUGIN_PROMPT_TEMPLATE.md`.",
        "Ниже перечислены конкретные критические ошибки и предупреждения, обнаруженные автоматическим чекером:",
        ""
    ]

    count = 1
    if issues:
        prompt_lines.append("### 🔴 КРИТИЧЕСКИЕ ОШИБКИ (ОБЯЗАТЕЛЬНО К ИСПРАВЛЕНИЮ):")
        for issue in issues:
            prompt_lines.append(f"#### {count}. {issue['title']} (`{issue['code']}`)")
            prompt_lines.append(f"**Описание:** {issue['description']}")
            prompt_lines.append(f"**Инструкция по исправлению:**\n{issue['fix_prompt']}\n")
            count += 1

    if warnings:
        prompt_lines.append("### ⚠️ РЕКОМЕНДАЦИИ И ПРЕДУПРЕЖДЕНИЯ:")
        for warn in warnings:
            prompt_lines.append(f"#### {count}. {warn['title']} (`{warn['code']}`)")
            prompt_lines.append(f"**Описание:** {warn['description']}")
            prompt_lines.append(f"**Инструкция по исправлению:**\n{warn['fix_prompt']}\n")
            count += 1

    prompt_lines.append("---")
    prompt_lines.append("ПОЖАЛУЙСТА, ПРЕДОСТАВЬ ПОЛНОСТЬЮ ИСПРАВЛЕННЫЙ HTML ФАЙЛ ПЛАГИНА СО ВСЕМИ ПРАВКАМИ.")

    return "\n".join(prompt_lines)

def main():
    if len(sys.argv) < 2:
        print("Использование: python scripts/check_plugin.py <путь_к_index.html> [--json]")
        sys.exit(1)

    file_path = sys.argv[1]
    output_json = "--json" in sys.argv

    if not os.path.exists(file_path):
        print(f"❌ Ошибка: Файл не найден по пути: {file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html_code = f.read()

    analysis = analyze_plugin_code(html_code)
    ai_prompt = generate_ai_prompt(analysis, os.path.basename(file_path))

    if output_json:
        result = {
            "file": file_path,
            "analysis": analysis,
            "ai_prompt": ai_prompt
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n=======================================================")
        print(f" 🔍 ПРОВЕРКА ПЛАГИНА: {file_path}")
        print("=======================================================\n")
        
        print("✅ ПРОЙДЕННЫЕ ПРОВЕРКИ:")
        for p in analysis["passed"]:
            print(f"  • {p}")

        if analysis["issues"]:
            print("\n🔴 КРИТИЧЕСКИЕ ОШИБКИ:")
            for issue in analysis["issues"]:
                print(f"  ❌ [{issue['code']}] {issue['title']}")

        if analysis["warnings"]:
            print("\n⚠️ ПРЕДУПРЕЖДЕНИЯ:")
            for warn in analysis["warnings"]:
                print(f"  ⚠️ [{warn['code']}] {warn['title']}")

        print("\n=======================================================")
        print(" 📋 ГОТОВЫЙ ПРОМТ ДЛЯ ИИ ДЛЯ ИСПРАВЛЕНИЯ ПЛАГИНА:")
        print("=======================================================\n")
        print(ai_prompt)
        print("\n=======================================================\n")

if __name__ == "__main__":
    main()

# Примеры базы данных: Темы (Skills) и Вопросы (Questions)

## 📊 Общая статистика

- **Предметов (Subjects)**: 5
- **Классов (Grades)**: 14 (от Pre-K до 12 класса)
- **Навыков (Skills)**: 17 опубликованных
- **Вопросов (Questions)**: 303

---

## 📚 Структура: Предметы (Subjects)

```sql
SELECT id, slug, title FROM subjects;
```

| ID | Slug           | Title           |
|----|----------------|-----------------|
| 1  | math           | Math            |
| 2  | language-arts  | Language Arts   |
| 3  | science        | Science         |
| 4  | social-studies | Social Studies  |
| 5  | spanish        | Spanish         |

---

## 🎓 Структура: Классы (Grades)

```sql
SELECT id, number, title FROM grades ORDER BY number;
```

| ID | Number | Title |
|----|--------|-------|
| 1  | -1     | Pre-K |
| 2  | 0      | K     |
| 3  | 1      | 1     |
| 4  | 2      | 2     |
| ... | ...   | ...   |
| 14 | 12     | 12    |

---

## 🎯 Примеры Навыков (Skills)

### Пример 1: Математика, 5 класс

```json
{
  "id": 1,
  "code": "A.1",
  "title": "Multiply whole numbers",
  "subject": "Math",
  "grade": 5,
  "difficulty": 2,
  "tags": ["multiplication"],
  "description": "Multiply two whole numbers.",
  "is_published": true
}
```

### Пример 2: Математика, 1 класс

```json
{
  "id": 100,
  "code": "A.1",
  "title": "Addition up to 20",
  "subject": "Math",
  "grade": 1,
  "difficulty": 2,
  "tags": ["addition"],
  "description": "Practice adding numbers up to 20",
  "is_published": true
}
```

### Пример 3: Математика, 2 класс

```json
{
  "id": 107,
  "code": "B.1",
  "title": "Multiplication tables 2-5",
  "subject": "Math",
  "grade": 2,
  "difficulty": 3,
  "tags": ["multiplication"],
  "description": "Learn multiplication tables for 2, 3, 4, and 5",
  "is_published": true
}
```

### Пример 4: Математика, 3 класс

```json
{
  "id": 112,
  "code": "B.1",
  "title": "Fractions basics",
  "subject": "Math",
  "grade": 3,
  "difficulty": 3,
  "tags": ["fractions"],
  "description": "Understand and work with fractions",
  "is_published": true
}
```

---

## ❓ Примеры Вопросов (Questions)

### Тип 1: MCQ (Multiple Choice Question) - Выбор одного ответа

**Вопрос ID: 1** (Навык: "Multiply whole numbers")

```json
{
  "id": 1,
  "skill_id": 1,
  "type": "MCQ",
  "prompt": "What is 7 × 8?",
  "level": 2,
  "data": {
    "choices": [
      {"id": "A", "text": "54"},
      {"id": "B", "text": "56"},
      {"id": "C", "text": "64"}
    ]
  },
  "correct_answer": {
    "choice": "B"
  },
  "explanation": "7 × 8 = 56."
}
```

**Вопрос ID: 1000** (Навык: "Addition up to 20")

```json
{
  "id": 1000,
  "skill_id": 100,
  "type": "MCQ",
  "prompt": "What is the last digit of 37?",
  "level": 1,
  "data": {
    "choices": [
      {"id": "A", "text": "9"},
      {"id": "B", "text": "7"},
      {"id": "C", "text": "6"}
    ]
  },
  "correct_answer": {
    "choice": "B"
  },
  "explanation": "The last digit of 37 is 7"
}
```

---

### Тип 2: NUMERIC - Числовой ответ

**Вопрос ID: 2** (Навык: "Multiply whole numbers")

```json
{
  "id": 2,
  "skill_id": 1,
  "type": "NUMERIC",
  "prompt": "Compute 12 × 9.",
  "level": 2,
  "data": {
    "min": 0,
    "max": 1000
  },
  "correct_answer": {
    "value": 108
  },
  "explanation": "12 × 9 = 108."
}
```

**Вопрос ID: 1008** (Навык: "Addition up to 20", уровень 3)

```json
{
  "id": 1008,
  "skill_id": 100,
  "type": "NUMERIC",
  "prompt": "If you have 74 and add 8 groups of 1, what do you get?",
  "level": 3,
  "data": {
    "min": 0,
    "max": 1000
  },
  "correct_answer": {
    "value": 82
  },
  "explanation": "74 + (8 × 1) = 82"
}
```

**Вопрос ID: 1016** (Навык: "Addition up to 20", уровень 5 - самый сложный)

```json
{
  "id": 1016,
  "skill_id": 100,
  "type": "NUMERIC",
  "prompt": "If you have 10 and add 5 groups of 3, what do you get?",
  "level": 5,
  "data": {
    "min": 0,
    "max": 1000
  },
  "correct_answer": {
    "value": 25
  },
  "explanation": "10 + (5 × 3) = 25"
}
```

---

## 📋 Полная структура таблиц

### Таблица `subjects`
```sql
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY,
    slug VARCHAR(64) UNIQUE NOT NULL,
    title VARCHAR(128) NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Таблица `grades`
```sql
CREATE TABLE grades (
    id INTEGER PRIMARY KEY,
    number INTEGER UNIQUE NOT NULL,  -- -1 для Pre-K, 0 для K, 1-12 для классов
    title VARCHAR(64) NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Таблица `skills`
```sql
CREATE TABLE skills (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER REFERENCES subjects(id),
    grade_id INTEGER REFERENCES grades(id),
    code VARCHAR(16) NOT NULL,  -- например "A.1", "B.2"
    title VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    tags TEXT[] DEFAULT '{}',
    difficulty INTEGER DEFAULT 1,  -- 1-5
    example_url VARCHAR(1024),
    video_url VARCHAR(1024),
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(subject_id, grade_id, code)
);
```

### Таблица `questions`
```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,  -- MCQ, NUMERIC, TEXT, MULTI_SELECT
    prompt TEXT NOT NULL,
    data JSONB DEFAULT '{}',  -- Структура зависит от типа вопроса
    correct_answer JSONB DEFAULT '{}',  -- Правильный ответ в JSON формате
    explanation TEXT DEFAULT '',
    level INTEGER DEFAULT 1,  -- 1-5 (сложность вопроса)
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## 🔍 Примеры SQL запросов

### Получить все навыки по математике для 1 класса:
```sql
SELECT s.id, s.code, s.title, s.difficulty
FROM skills s
JOIN subjects sub ON s.subject_id = sub.id
JOIN grades g ON s.grade_id = g.id
WHERE sub.slug = 'math' AND g.number = 1
  AND s.is_published = true;
```

### Получить вопросы для навыка с уровнями сложности:
```sql
SELECT 
    q.id,
    q.type,
    q.prompt,
    q.level,
    q.data,
    q.correct_answer,
    q.explanation
FROM questions q
WHERE q.skill_id = 100
ORDER BY q.level;
```

### Подсчитать вопросы по типам:
```sql
SELECT 
    type,
    COUNT(*) as count,
    COUNT(DISTINCT skill_id) as skills_count
FROM questions
GROUP BY type;
```

Результат:
| Type     | Count | Skills Count |
|----------|-------|--------------|
| MCQ      | ~200  | ~15          |
| NUMERIC  | ~100  | ~12          |
| TEXT     | ~3    | ~2           |

---

## 🎮 Пример использования в API

### Получить навык с вопросами:
```bash
GET /api/v1/catalog/skills/100
```

Ответ:
```json
{
  "data": {
    "id": 100,
    "code": "A.1",
    "title": "Addition up to 20",
    "subject_id": 1,
    "grade_id": 3,
    "difficulty": 2,
    "tags": ["addition"],
    "description": "Practice adding numbers up to 20",
    "is_published": true
  }
}
```

### Начать практику и получить вопрос:
```bash
POST /api/v1/practice/sessions
{
  "skill_id": 100
}
```

Система автоматически выберет вопрос соответствующего уровня на основе текущего SmartScore студента.

---

## 💡 Особенности структуры данных

1. **Уровни вопросов (level 1-5)**: Вопросы одного навыка имеют разную сложность. Система автоматически подбирает вопросы на основе прогресса студента.

2. **Гибкая структура ответов**: 
   - `data` содержит метаданные (варианты ответов для MCQ, min/max для NUMERIC)
   - `correct_answer` содержит правильный ответ в структурированном формате

3. **Иерархия**: Предмет → Класс → Навык → Вопрос

4. **Теги и фильтрация**: Навыки имеют теги для удобной категоризации и поиска.

5. **Публикация**: Навыки могут быть опубликованы или скрыты (`is_published`).

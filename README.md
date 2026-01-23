# Math Edu Frontend

Frontend приложение для образовательной платформы Math Edu, построенное на Vue 3 + Vite + TypeScript.

## Технологический стек

- **Vue 3** с Composition API
- **TypeScript** для типобезопасности
- **Vite** для сборки и разработки
- **Pinia** для управления состоянием
- **Vue Router** для роутинга
- **Axios** для HTTP запросов
- **Tailwind CSS** для стилизации
- **Vitest** для тестирования
- **Chart.js** для графиков (опционально)

## Требования

- Node.js ^20.19.0 или >=22.12.0
- npm или yarn
- Backend API должен быть доступен на `http://localhost:8000` (или настроен через `VITE_API_URL`)

## Установка

```bash
# Установка зависимостей
npm install

# Запуск dev-сервера
npm run dev

# Сборка для production
npm run build

# Запуск тестов
npm test

# Проверка типов
npm run type-check

# Линтинг
npm run lint
```

## Конфигурация

Создайте файл `.env` в корне проекта (опционально):

```env
VITE_API_URL=http://localhost:8000
```

Если переменная не указана, используется значение по умолчанию: `http://localhost:8000`

## Структура проекта

```
src/
├── api/              # API клиенты (auth, catalog, practice, analytics)
│   ├── client.ts     # Axios инстанс с interceptors
│   ├── auth.ts
│   ├── catalog.ts
│   ├── practice.ts
│   └── analytics.ts
├── components/       # Vue компоненты
│   ├── layout/       # Layout компоненты (Header, Footer)
│   └── ui/           # UI компоненты (Button, Card, Toast)
├── composables/      # Vue composables (useToast)
├── pages/            # Страницы приложения
│   ├── auth/         # Auth страницы (Login, Register)
│   ├── Home.vue
│   ├── ClassView.vue
│   ├── SkillView.vue
│   ├── PracticeSession.vue
│   ├── PracticeResults.vue
│   ├── Analytics.vue
│   └── Profile.vue
├── router/           # Vue Router конфигурация
│   └── index.ts
├── stores/           # Pinia stores
│   ├── auth.ts
│   ├── catalog.ts
│   ├── practice.ts
│   └── analytics.ts
├── types/            # TypeScript типы
│   └── api.ts
├── test/             # Тесты
│   └── setup.ts
├── style.css         # Глобальные стили (Tailwind)
├── App.vue
└── main.ts
```

## Роутинг

- `/` - Домашняя страница (список классов)
- `/class/:gradeId` - Страница класса (список навыков)
- `/skill/:skillId` - Страница навыка (старт практики)
- `/practice/:sessionId` - Интерфейс активной сессии практики
- `/practice/:sessionId/results` - Результаты сессии
- `/analytics` - Личная аналитика студента
- `/auth/login` - Вход
- `/auth/register` - Регистрация
- `/profile` - Профиль пользователя

Все роуты, кроме `/auth/*`, требуют аутентификации.

## API Endpoints

Приложение использует следующие эндпоинты из OpenAPI спецификации (`http://localhost:8000/docs`):

### Auth
- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `POST /api/v1/auth/refresh` - Обновление токена
- `POST /api/v1/auth/logout` - Выход
- `GET /api/v1/users/me` - Получение текущего пользователя

### Catalog
- `GET /api/v1/subjects` - Список предметов
- `GET /api/v1/grades` - Список классов
- `GET /api/v1/skills` - Список навыков (с фильтрами по subject_slug, grade_number)
- `GET /api/v1/skills/{skill_id}` - Детали навыка
- `GET /api/v1/skills/{skill_id}/stats` - Статистика по навыку

### Practice
- `POST /api/v1/practice/sessions` - Создание сессии практики
- `GET /api/v1/practice/sessions/{session_id}` - Получение сессии
- `POST /api/v1/practice/sessions/{session_id}/next` - Следующий вопрос
- `POST /api/v1/practice/sessions/{session_id}/submit` - Отправка ответа (с Idempotency-Key)
- `POST /api/v1/practice/sessions/{session_id}/finish` - Завершение сессии

### Analytics
- `GET /api/v1/analytics/overview` - Общая аналитика
- `GET /api/v1/analytics/skills` - Статистика по навыкам

## Особенности реализации

### Аутентификация

- Access token хранится в памяти (Pinia store) и localStorage
- Refresh token сохраняется в localStorage (предполагается поддержка httpOnly cookies на бэкенде)
- Axios interceptor автоматически добавляет `Authorization: Bearer <token>` заголовок
- При 401 ошибке автоматически выполняется refresh token и повтор запроса
- При неудачном refresh выполняется редирект на `/auth/login`

### Idempotency

- Для операций создания/обновления (POST/PUT/PATCH) автоматически добавляется заголовок `Idempotency-Key: <UUID>`
- Для отправки ответов генерируется новый UUID на каждую попытку

### Rate Limiting

- Локальное ограничение: максимум 30 запросов в минуту для отправки ответов
- При превышении лимита показывается сообщение с временем ожидания
- 429 ответы обрабатываются с показом сообщения и Retry-After заголовка

### Кэширование

- Каталог (subjects, grades, skills) кэшируется в Pinia store и localStorage с TTL 5 минут
- Аналитика кэшируется аналогично
- При ошибках API используется кэш из localStorage как fallback

### Heartbeat

- Для активных сессий практики отправляется heartbeat каждые 30 секунд
- Учитывается порог неактивности (5 минут)
- Время активности обновляется при каждом действии пользователя

### Восстановление сессий

- Состояние сессии сохраняется в localStorage
- При восстановлении проверяется возраст сессии (максимум 24 часа)
- Автоматическое восстановление при перезагрузке страницы

## Тестирование

Минимальный набор тестов для ключевых компонентов:

```bash
# Запуск тестов
npm test

# Запуск тестов с coverage
npm test -- --coverage
```

## Известные несоответствия API

Если при использовании обнаруживаются несоответствия между фронтендом и бэкендом API:

1. Проверьте OpenAPI спецификацию на `http://localhost:8000/docs`
2. Сравните схемы ответов с типами в `src/types/api.ts`
3. При необходимости обновите типы и API клиенты

### Примеры возможных несоответствий:

- Формат ошибок может отличаться от ожидаемого (поле `detail` vs `message`)
- Некоторые опциональные поля могут быть обязательными или наоборот
- Номера страниц в пагинации могут начинаться с 0 или 1

## Разработка

### Добавление нового компонента

1. Создайте файл в `src/components/` или `src/components/ui/`
2. Используйте TypeScript и Composition API
3. Добавьте стили через Tailwind CSS классы
4. При необходимости добавьте тесты в `*.spec.ts`

### Добавление новой страницы

1. Создайте файл в `src/pages/`
2. Добавьте роут в `src/router/index.ts`
3. Если требуется аутентификация, установите `meta: { requiresAuth: true }`

### Добавление нового API endpoint

1. Добавьте метод в соответствующий файл в `src/api/`
2. Используйте типизированный `apiClient` из `src/api/client.ts`
3. Добавьте TypeScript типы в `src/types/api.ts` если необходимо

## Безопасность

- Refresh token НЕ должен храниться в localStorage в production (предпочтительно httpOnly cookie)
- Все пользовательские вводы должны валидироваться
- CSRF защита должна быть реализована на бэкенде
- Используйте HTTPS в production

## Лицензия

Private project.

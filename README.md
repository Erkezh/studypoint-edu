# 🎓 StudyPoint Edu (Math Edu Platform)

![Vue 3](https://img.shields.io/badge/Vue-3.5-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-6.0-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7+-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

> **StudyPoint Edu** — это современная полнофункциональная интерактивная образовательная платформа (аналог IXL) для изучения математики и других дисциплин. Платформа поддерживает адаптивные практические сессии с алгоритмом **SmartScore**, интерактивные HTML5/React плагины с детерминированной генерацией задач, разделение ролей (Студент, Учитель, Родитель, Администратор) и подробную аналитику.

---

## 📋 Оглавление

1. [Особенности платформы](#-особенности-платформы)
2. [Ролевая модель пользователей](#-ролевая-модель-пользователей)
3. [Архитектура и Технологический стек](#-архитектура-и-технологический-стек)
4. [Требования к окружению](#-требования-к-окружению)
5. [Быстрый запуск и Установка](#-быстрый-запуск-и-установка)
   - [Локальная разработка (Frontend + Backend)](#1-локальная-разработка)
   - [Запуск через Docker (Backend)](#2-запуск-backend-в-docker)
6. [Конфигурация (Переменные окружения)](#-конфигурация-переменные-окружения)
7. [Структура проекта](#-структура-проекта)
8. [Маршрутизация и Роуты](#-маршрутизация-и-роуты)
9. [API Эндпоинты](#-api-эндпоинты)
10. [Разработка интерактивных плагинов (IXL Contract)](#-разработка-интерактивных-плагинов-ixl-contract)
11. [Тестирование, Линтинг и Валидация](#-тестирование-линтинг-и-валидация)
12. [Деплой на сервер и CI/CD](#-деплой-на-сервер-и-cicd)
13. [Безопасность и Надежность](#-безопасность-и-надежность)
14. [Документация и Ресурсы](#-документация-и-ресурсы)

---

## ✨ Особенности платформы

- **Адаптивный алгоритм SmartScore (0 - 100):**
  - **Learning Zone (0–69):** Базовое освоение материала (+1..+2 балла за верный ответ).
  - **Refining Zone (70–89):** Закрепление навыков и усложненные задачи.
  - **Challenge Zone (90–100):** Задачи повышенной сложности для достижения полного мастерства (Mastery).
- **Интерактивный движок плагинов (HTML5 / React / Canvas):**
  - 100% детерминированный **Seed PRNG** generator — идентичные условия у ученика и преподавателя при одинаковом `seed`.
  - 5 динамических уровней сложности (`level=1..5`).
  - Пошаговые подробные решения и объяснения (`Түсіндірме`) на казахском языке.
- **Трекинг активности (Heartbeat & Anti-AFK):**
  - Автоматическая отправка пульса каждые 30 секунд для подсчета чистого времени практики без защиты от "накрутки".
- **Система викторин и тестов (Quizzes):**
  - Режим контрольных с ограничением по времени и мгновенной выгрузкой результатов.
- **Наглядная аналитика и графики:**
  - Данные по динамике SmartScore, точности ответов, освоенным навыкам и проблемным темам на базе Chart.js.
- **Геймификация и Сертификаты:**
  - Награды (Awards), бейджи, праздничные салюты (Confetti) при достижении 100 баллов и возможность генерации PDF-сертификатов.

---

## 👥 Ролевая модель пользователей

| Роль | Основной роут | Главные возможности |
| :--- | :--- | :--- |
| 🎓 **Студент (Student)** | `/my-ixl`, `/practice/:id` | Прохождение практики, зарабатывание SmartScore, викторины, просмотр личной аналитики и наград. |
| 👨‍🏫 **Учитель (Teacher)** | `/teacher` | Создание классов, назначение заданий с целевым SmartScore, таблица успеваемости (Score Grid), просмотр журналов. |
| 👨‍👩‍👧 **Родитель (Parent)** | `/parent` | Привязка аккаунтов детей, просмотр отчетов о динамике обучения и времени занятий. |
| 🛠️ **Администратор (Admin)** | `/admin/*` | Полный контроль предметов, тем, навыков, вопросов, загрузка и привязка плагинов, управление пользователями и подписками. |

---

## 🛠 Архитектура и Технологический стек

### Frontend
- **Фреймворк:** [Vue 3](https://vuejs.org/) (Composition API, `<script setup>`)
- **Сборщик:** [Vite 6](https://vitejs.dev/)
- **Язык:** [TypeScript 5.7](https://www.typescriptlang.org/)
- **Стейт-менеджер:** [Pinia 2.3](https://pinia.vuejs.org/)
- **Роутинг:** [Vue Router 4.5](https://router.vuejs.org/)
- **Стилизация:** [Tailwind CSS 4.0](https://tailwindcss.com/) + PostCSS
- **Графики и визуализация:** Chart.js 4.4, Vue-Chartjs, TresJS / Three.js (3D пресеты), Canvas-confetti
- **Тестирование:** Vitest + Testing Library Vue

### Backend
- **Язык & Фреймворк:** Python 3.11+, [FastAPI](https://fastapi.tiangolo.com/) (Pydantic v2)
- **База данных:** PostgreSQL 15+ (SQLAlchemy 2.0 Async + asyncpg)
- **Миграции:** Alembic
- **Кэширование & Сессии:** Redis (Idempotency Key, Rate Limiting, Heartbeat locks)
- **Аутентификация:** JWT Access/Refresh tokens + Argon2 password hashing
- **Тестирование:** Pytest

### DevOps & Инфраструктура
- **Контейнеризация:** Docker & Docker Compose
- **Веб-сервер / Reverse Proxy:** Nginx (поддержка vhost и gateway режимов)
- **CI/CD:** GitHub Actions (автоматический деплой при пуше в `main`)

---

## 💻 Требования к окружению

Для локального запуска и сборки проекта понадобятся:

- **Node.js:** `^20.19.0` или `>=22.12.0` *(обязательно для совместимости Vite/Vue 3)*
- **npm:** `>=10.0.0`
- **Python:** `>=3.11` *(для работы локального бэкенда)*
- **Docker & Docker Compose:** *(для запуска PostgreSQL и Redis)*

---

## 🚀 Быстрый запуск и Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/YourOrg/studypoint-edu.git
cd studypoint-edu
```

### 2. Запуск Backend (Docker + FastAPI)

1. Перейдите в директорию `backend`:
   ```bash
   cd backend
   ```
2. Создайте файл окружения из шаблона:
   ```bash
   cp .env.example .env
   ```
3. Запустите базы данных Postgres и Redis:
   ```bash
   docker compose up -d --build postgres redis
   ```
4. Синхронизируйте пароли базы данных и запустите API:
   ```bash
   ./scripts/sync_postgres_password.sh
   docker compose up -d --build api
   ```
5. Примените миграции и заполните базовые тестовые данные (Seed):
   ```bash
   docker compose run --rm api python -m alembic upgrade head
   docker compose run --rm api python -m app.db.seed
   ```
   > 📍 **Документация API (Swagger):** `http://localhost:8001/docs`  
   > 📍 **Health Check:** `http://localhost:8001/api/v1/health/ready`

### 3. Запуск Frontend (Vue 3 + Vite)

1. Вернитесь в корень проекта и установите зависимости:
   ```bash
   cd ..
   npm install
   ```
2. Запустите сервер разработки Vite:
   ```bash
   npm run dev
   ```
   > 🌐 Приложение откроется по адресу: **`http://localhost:5174`** (или `http://localhost:5173`)

3. Для проверки готовности production-сборки используйте:
   ```bash
   # Проверка типов + сборка
   npm run build

   # Запуск локального сервера превью с проксированием API
   npm run preview
   ```

---

## ⚙️ Конфигурация (Переменные окружения)

### Frontend (`.env` в корне проекта)

```env
# URL бэкенд API. Оставьте пустым в production для использования относительного прокси /api
VITE_API_URL=http://localhost:8001
```

### Backend (`backend/.env`)

```env
PROJECT_NAME="StudyPoint Edu API"
ENV=development
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key

# Берутся по умолчанию в Docker контейнерах:
POSTGRES_SERVER=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=math_edu
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
```

---

## 📁 Структура проекта

```
studypoint-edu/
├── backend/                  # FastAPI Бэкенд на Python
│   ├── alembic/              # Миграции структуры базы данных
│   ├── app/                  # Исходный код API
│   │   ├── api/v1/routes/    # Эндпоинты (auth, catalog, practice, teacher, admin, etc.)
│   │   ├── core/             # Конфигурация, безопасность, JWT
│   │   ├── db/               # Сессии SQLAlchemy и Seed скрипты
│   │   ├── models/           # Модели базы данных (ORM)
│   │   ├── schemas/          # Схемы валидации Pydantic v2
│   │   └── services/         # Бизнес-логика (SmartScore, Practice, Quiz, Reports)
│   ├── scripts/              # Вспомогательные скрипты администрирования
│   ├── Dockerfile            # Dockerfile бэкенда
│   └── docker-compose.yml    # Инфраструктура Postgres, Redis, API
├── deploy/                   # Конфигурации для серверов
│   └── nginx/                # vhost и gateway конфигурационные файлы Nginx
├── scripts/                  # Скрипты проверки плагинов и утилиты фронтенда
│   ├── check_plugin.py       # Валидатор соответствия плагинов контракту IXL
│   ├── serve-dist.mjs        # Node.js сервер превью с проксированием запросов
│   └── check-node-version.cjs# Скрипт валидации версии Node.js
├── src/                      # Vue 3 Фронтенд приложение
│   ├── api/                  # API-клиенты Axios (client.ts, auth, catalog, practice)
│   ├── components/           # Переиспользуемые UI компоненты и Layouts
│   │   ├── layout/           # Header, Footer, Sidebar, Navigation
│   │   └── ui/               # Button, Card, Toast, Modal, ScoreGrid, etc.
│   ├── composables/          # Vue Composables (useToast, usePractice, etc.)
│   ├── pages/                # Страницы Vue Router
│   │   ├── admin/            # Панель администратора (Topics, Skills, Questions, Plugins)
│   │   ├── auth/             # Вход (Login) и Регистрация (Register)
│   │   ├── parent/           # Кабинет родителя
│   │   ├── teacher/          # Кабинет учителя и управление классами
│   │   ├── Analytics.vue     # Страница личной аналитики
│   │   ├── ClassView.vue     # Просмотр класса и навыков
│   │   ├── Home.vue          # Главная страница
│   │   ├── PracticeSession.vue# Активный интерфейс решения задач
│   │   └── SkillView.vue     # Карточка навыка и старт практики
│   ├── router/               # Конфигурация роутинга и проверки прав (Navigation Guards)
│   ├── stores/               # Хранилище Pinia (auth, catalog, practice, analytics)
│   ├── types/                # TypeScript типы и интерфейсы API
│   ├── App.vue               # Главный компонент
│   └── main.ts               # Точка входа приложений
├── static/                   # Интерактивные HTML5/React плагины и ассеты
├── .github/workflows/        # GitHub Actions CI/CD пайплайны
├── CICD_SETUP.md             # Инструкция по настройке автоматического деплоя
├── PLUGIN_PROMPT_TEMPLATE.md# Строгий регламент и промт генерации плагинов
├── SERVER_DEPLOYMENT.md      # Подробный гайд по развертыванию на Ubuntu сервере
├── SITE_DOCUMENTATION.md     # Архитектурный обзор проекта
├── plugins.json              # Реестр интерактивных плагинов
├── questions.json            # База вопросов
├── package.json              # Скрипты и зависимости Node.js
├── vite.config.ts            # Конфигурация Vite
└── README.md                 # Документация проекта
```

---

## 🗺 Маршрутизация и Роуты

### Публичные страницы
- `/` — Главная страница платформы
- `/topics`, `/topics/:topicSlug` — Каталог учебных тем
- `/class/:gradeId` — Выбор класса и навыков
- `/pricing`, `/payment` — Тарифы и подписка
- `/auth/login`, `/auth/register` — Авторизация и регистрация

### Зона Студента (Требуется Auth)
- `/my-ixl` — Дашборд студента
- `/skill/:skillId` — Описание навыка
- `/practice/:sessionId` — Экран решения задач в реальном времени
- `/practice/:sessionId/results` — Итоги практической сессии
- `/my-ixl/quiz/:quizId` — Прохождение викторины
- `/analytics` — Личная статистика и аналитика
- `/profile` — Профиль пользователя

### Зона Учителя и Родителя
- `/teacher` — Дашборд преподавателя, управление классами и Score Grid
- `/parent` — Кабинет родителя и привязка детей

### Панель Администратора (`/admin`)
- `/admin/topics`, `/admin/skills`, `/admin/questions`, `/admin/plugins`, `/admin/users`, `/admin/subscriptions`

---

## 🔌 API Эндпоинты

Приложение взаимодействует с бэкендом через следующие ключевые эндпоинты (полный список доступен в Swagger по адресу `/docs`):

### Auth & User (`/api/v1/auth`, `/api/v1/users`)
- `POST /api/v1/auth/register` — Регистрация пользователя
- `POST /api/v1/auth/login` — Аутентификация и получение JWT
- `POST /api/v1/auth/refresh` — Обновление access-токена
- `GET /api/v1/users/me` — Получение профиля текущего пользователя

### Catalog (`/api/v1/catalog`)
- `GET /api/v1/subjects` — Список предметов
- `GET /api/v1/grades` — Список классов
- `GET /api/v1/skills` — Фильтрованный список навыков
- `GET /api/v1/skills/{skill_id}` — Карточка навыка и статистика

### Practice Engine (`/api/v1/practice`)
- `POST /api/v1/practice/sessions` — Старт сессии
- `GET /api/v1/practice/sessions/{id}` — Состояние сессии
- `POST /api/v1/practice/sessions/{id}/next` — Запрос следующего вопроса
- `POST /api/v1/practice/sessions/{id}/submit` — Отправка ответа (с `Idempotency-Key`)
- `POST /api/v1/practice/sessions/{id}/heartbeat` — Отправка сигнала активности
- `POST /api/v1/practice/sessions/{id}/finish` — Завершение практики

---

## 🧩 Разработка интерактивных плагинов (IXL Contract)

Интерактивные плагины в `static/` отображаются внутри `<iframe>` во время практики. Все плагины должны **строго соблюдать спецификацию**, описанную в [`PLUGIN_PROMPT_TEMPLATE.md`](file:///Users/erkenazzhanabay/Desktop/studypoint%20ixl/studypoint-edu/PLUGIN_PROMPT_TEMPLATE.md).

### Ключевые требования контракта:
1. **Детерминированный Seed PRNG:**
   Запрещено использовать `Math.random()`. Генерация задач обязана зависеть **только** от `createSeededRandom(seed)`, получаемого из URL (`?seed=12345`).
2. **5 уровней сложности:**
   Поддержка аргумента `?level=1..5`.
3. **Казахский язык и Пошаговое объяснение:**
   Все тексты интерфейса строго на казахском языке. При ответе плагин сам выводит вердикт и пошаговый разбор (`Түсіндірме`).
4. **PostMessage протокол:**
   - `STUDENT_ANSWER` — передача введённого значения родительскому окну при каждом изменении.
   - `exercise-result` — отправка итогового ответа (обязательно с полем `userAnswer`).
   - `HEIGHT_CHANGE` — динамическое изменение высоты iframe.
   - `SERVER_RESULT` — обработка ответа серверной проверки.

### Автоматическая проверка плагинов

Перед добавлением плагина запушьте скрипт валидации:

```bash
npm run check-plugin
# или напрямую: python3 scripts/check_plugin.py
```

---

## 🧪 Тестирование, Линтинг и Валидация

В проекте настроен комплекс проверок качества кода:

```bash
# Запуск модульных тестов Vitest
npm test

# Запуск тестов в UI-режиме
npm run test:ui

# Проверка типов TypeScript (vue-tsc)
npm run type-check

# Автоматический линтинг и исправление стилей (ESLint)
npm run lint

# Форматирование файлов через Prettier
npm run format

# Проверка корректности интерактивных плагинов
npm run check-plugin
```

---

## 🚀 Деплой на сервер и CI/CD

Подробные инструкции по деплою и настройке инфраструктуры вынесены в отдельные специализированные руководства:

- **Серверный деплой (Ubuntu, Docker, Nginx):** [`SERVER_DEPLOYMENT.md`](file:///Users/erkenazzhanabay/Desktop/studypoint%20ixl/studypoint-edu/SERVER_DEPLOYMENT.md)
- **Настройка CI/CD (GitHub Actions):** [`CICD_SETUP.md`](file:///Users/erkenazzhanabay/Desktop/studypoint%20ixl/studypoint-edu/CICD_SETUP.md)
- **Архитектура и База Данных:** [`SITE_DOCUMENTATION.md`](file:///Users/erkenazzhanabay/Desktop/studypoint%20ixl/studypoint-edu/SITE_DOCUMENTATION.md)

---

## 🔒 Безопасность и Надежность

- **Защита от повторных отправок (Idempotency):**
  Все `POST/PUT` запросы отправки ответов содержат уникальный `Idempotency-Key` (UUID v4) для предотвращения дублирования данных при нестабильном интернете.
- **Ограничение частоты запросов (Rate Limiting):**
  На уровне бэкенда и клиента действует лимит (до 30 отправок ответов в минуту) с обработкой статуса HTTP 429 (`Retry-After`).
- **Автоматический Refresh токенов:**
  При истечении срока действия Access Token через Axios interceptors происходит прозрачный запрос нового токена без разрыва рабочей сессии пользователя.

---

## 📄 Лицензия

Private repository. Все права защищены © **StudyPoint Edu**.

# StudyPoint Edu - Site Documentation

## 1. Overview and Architecture
**StudyPoint Edu** is a comprehensive, production-ready educational platform inspired by IXL. It offers skills-based practice, progress tracking, and analytics for multiple user roles (Admin, Teacher, Student, and Parent).

### Tech Stack
- **Frontend**: Vue.js 3, Vite, Pinia (State Management), Vue Router, Tailwind CSS for modern styling, Chart.js for analytics.
- **Backend**: Python 3.11+ with FastAPI, Pydantic v2.
- **Database**: PostgreSQL (with SQLAlchemy 2.0 async and asyncpg) and Alembic for migrations.
- **Caching & Sessions**: Redis.
- **Auth**: JWT-based access and refresh tokens, Argon2 password hashing.

---

## 2. Main User Roles
The platform separates functionalities by four primary roles:

1. **Admin (`/admin/*`)**
   - Has full control over the platform's content and users.
   - Manages Topics, Skills, Questions, Plugins, and Users.
   - Oversees Grades, Subscriptions, and Analytics.
   
2. **Teacher (`/teacher`)**
   - Can view the Teacher Dashboard, assign tasks, track student scores via Score Grids.
   - Manage classrooms, view student logs, generate reports on assignments and classroom performance.

3. **Student (Default / Auth Zone)**
   - Takes practice sessions (`/practice/:sessionId`).
   - Earns a "SmartScore", going through Learning (0-69), Refining (70-89), and Challenge (90-100) zones.
   - Views their IXL-like dashboard (`/my-ixl`).
   - Takes Quizzes (`/my-ixl/quiz/:quizId`).

4. **Parent (`/parent`)**
   - Connects to student accounts to track their progress, view reports, and analyze scores over time.

---

## 3. Frontend Pages and Views
The frontend routing (`src/router`) exposes a robust application separated into specific views.

### Public Pages
- `Home` (`/`) - Landing page and entry point.
- `Topics` (`/topics`), `TopicDetail` (`/topics/:topicSlug`) - Browsing available curriculum themes and topics (available freely).
- `Class` (`/class/:gradeId`) - View topics by grade level.
- `Pricing` (`/pricing`), `Payment` (`/payment`) - Public-facing subscription and purchasing pages.
- `Auth` (`/auth/login`, `/auth/register`) - User authentication forms.

### Practice and Learning (Core Engine)
- `Practice Session` (`/practice/:sessionId`) & `Results` (`/practice/:sessionId/results`)
  - A highly interactive UI for students solving questions in real-time.
  - Heartbeat checks (`/practice/sessions/{id}/heartbeat`) track exact active time preventing AFK (Away From Keyboard) stat padding.
- `Skills` (`/skill/:skillId`)

### Analytics & Reporting
- `AnalyticsView` (`/analytics`) - Comprehensive data visualization leveraging Vue-Chartjs. Displays questions logs and progress tracking.

### Admin Dashboard (`/admin`)
Modularized by distinct tasks:
- `AdminGrades`, `AdminTopics`, `AdminSkills`, `AdminQuestions`, `AdminPlugins`, `AdminSubscriptions`, `AdminUsers`.

---

## 4. Backend Logic & Functionality
The FastAPI backend (`backend/app/api/v1/routes`) powers the frontend via strict RESTful APIs.

1. **Auth & Me (`auth.py`, `me.py`)** - Registration, JWT exchanges, profile updates.
2. **Catalog & Classrooms (`catalog.py`, `classrooms.py`)** - Data models mapping students into classes, assigning them specific syllabuses.
3. **Practice Engine (`practice.py`)** - Complex logic evaluating answers, updating the SmartScore based on correct (+1..+2) and incorrect (-3..-8) weights, detecting the "Mastery" streak.
4. **Quiz Engine (`quiz.py`, `student_quiz.py`)** - Custom quiz formulation and checking, allowing timed and specific assessments outside of standard practice.
5. **Teacher Utils (`teacher.py`, `assignments.py`)** - Creating assignments with a `target_smartscore` and automatically calculating if a student meets criteria via the score-grid.
6. **Reports & Awards (`reports.py`, `awards.py`)** - PDF generation endpoint for Practice Sessions, Assignments, and Certificates to reward students for leveling up.

---

## 5. Design Philosophy
- **Responsive & Modern UI**: With TailwindCSS built-in natively, the application focuses on clean, card-based interfaces.
- **Gamification**: The "SmartScore" integration, Challenge zones, and Awards system are designed deliberately to engage students heavily.
- **Robustness**: Redis handles idempotent protections preventing double-submissions, and async features keep the backend extremely responsive.

To run the full stack, you simultaneously run the dev Vite server (`npm run dev`) and Uvicorn FastAPI (`make run`) with background Redis and Postgres docker containers.

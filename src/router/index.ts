import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useGameSettingsStore } from '@/stores/gameSettings'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/pages/Home.vue'),
    meta: { requiresAuth: false }, // Главная страница доступна без авторизации
  },
  {
    path: '/class/:gradeId',
    name: 'class',
    component: () => import('@/pages/ClassView.vue'),
    meta: { requiresAuth: false }, // Просмотр тем доступен без авторизации
    props: true,
  },
  {
    path: '/topics',
    name: 'topics',
    component: () => import('@/pages/TopicsView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/topics/:topicSlug',
    name: 'topic-detail',
    component: () => import('@/pages/TopicDetailView.vue'),
    meta: { requiresAuth: false },
    props: true,
  },
  {
    path: '/skill/:skillId',
    name: 'skill',
    component: () => import('@/pages/SkillView.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/practice/:sessionId',
    name: 'practice',
    component: () => import('@/pages/PracticeSession.vue'),
    meta: { requiresAuth: false }, // Практика доступна без авторизации (пробные вопросы)
    props: true,
  },
  {
    path: '/practice/:sessionId/results',
    name: 'practice-results',
    component: () => import('@/pages/PracticeResults.vue'),
    meta: { requiresAuth: false }, // Результаты доступны без авторизации
    props: true,
  },
  {
    path: '/analytics',
    name: 'analytics',
    component: () => import('@/pages/AnalyticsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/auth/login',
    name: 'login',
    component: () => import('@/pages/auth/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/auth/register',
    name: 'register',
    component: () => import('@/pages/auth/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/pricing',
    name: 'pricing',
    component: () => import('@/pages/Pricing.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/payment',
    name: 'payment',
    component: () => import('@/pages/Payment.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/welcome',
    name: 'welcome',
    component: () => import('@/pages/Welcome.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/pages/Profile.vue'),
    meta: { requiresAuth: true, requiresGame: true },
  },
  {
    path: '/game/select',
    name: 'game-select',
    component: () => import('@/pages/GameSelect.vue'),
    meta: { requiresAuth: true, requiresRole: 'STUDENT' },
  },
  {
    path: '/teacher',
    name: 'teacher-dashboard',
    component: () => import('@/pages/TeacherDashboard.vue'),
    meta: { requiresAuth: true, requiresRole: 'TEACHER' },
  },
  {
    path: '/teacher/quizzes/create',
    name: 'teacher-quiz-create',
    component: () => import('@/pages/teacher/QuizCreateView.vue'),
    meta: { requiresAuth: true, requiresRole: 'TEACHER' },
  },
  {
    path: '/teacher/quizzes/edit/:quizId',
    name: 'teacher-quiz-edit',
    component: () => import('@/pages/teacher/QuizCreateView.vue'),
    meta: { requiresAuth: true, requiresRole: 'TEACHER' },
    props: true,
  },
  {
    path: '/parent',
    name: 'parent-dashboard',
    component: () => import('@/pages/ParentDashboard.vue'),
    meta: { requiresAuth: true, requiresRole: 'PARENT' },
  },
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: () => import('@/pages/AdminDashboard.vue'),
    meta: { requiresAuth: true, requiresRole: 'ADMIN' },
  },
  {
    path: '/admin/skills',
    name: 'admin-skills',
    component: () => import('@/pages/AdminSkills.vue'),
    meta: { requiresAuth: true, requiresRole: 'ADMIN' },
  },
  {
    path: '/admin/plugins',
    name: 'admin-plugins',
    component: () => import('@/pages/AdminPlugins.vue'),
    meta: { requiresAuth: true, requiresRole: 'ADMIN' },
  },
  {
    path: '/admin/questions',
    name: 'admin-questions',
    component: () => import('@/pages/AdminQuestions.vue'),
    meta: { requiresAuth: true, requiresRole: 'ADMIN' },
  },
  {
    path: '/admin/users',
    name: 'admin-users',
    component: () => import('@/pages/AdminUsers.vue'),
    meta: { requiresAuth: true, requiresRole: 'ADMIN' },
  },
  {
    path: '/admin/questions/list',
    name: 'admin-questions-list',
    component: () => import('@/pages/AdminQuestionsList.vue'),
    meta: { requiresAuth: true, requiresRole: 'ADMIN' },
  },
  {
    path: '/admin/subscriptions',
    name: 'admin-subscriptions',
    component: () => import('@/pages/AdminSubscriptions.vue'),
    meta: { requiresAuth: true, requiresRole: 'ADMIN' },
  },
  {
    path: '/admin/topics',
    name: 'admin-topics',
    component: () => import('@/pages/AdminTopics.vue'),
    meta: { requiresAuth: true, requiresRole: 'ADMIN' },
  },
  {
    path: '/admin/topics/:topicId',
    name: 'admin-topic-detail',
    component: () => import('@/pages/AdminTopicDetail.vue'),
    meta: { requiresAuth: true, requiresRole: 'ADMIN' },
    props: true,
  },
  {
    path: '/admin/grades',
    name: 'admin-grades',
    component: () => import('@/pages/AdminGrades.vue'),
    meta: { requiresAuth: true, requiresRole: 'ADMIN' },
  },
  {
    path: '/my-cabinet',
    name: 'my-cabinet',
    component: () => import('@/pages/MyIxlView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/my-cabinet/quiz/:quizId',
    name: 'student-quiz',
    component: () => import('@/pages/StudentQuizView.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/garage',
    name: 'garage',
    component: () => import('@/pages/GarageView.vue'),
    meta: { requiresAuth: true, requiresRole: 'STUDENT', requiresGame: true, gameType: 'car' },
  },
  {
    path: '/game-shop',
    name: 'game-shop',
    component: () => import('@/pages/GameShop.vue'),
    meta: { requiresAuth: true, requiresRole: 'STUDENT', requiresGame: true },
  },
  {
    path: '/character-customization',
    name: 'avatar-demo',
    alias: '/avatar-demo',
    component: () => import('@/views/AvatarDemo.vue'),
    meta: { requiresAuth: true, requiresRole: 'STUDENT', requiresGame: true, gameType: 'character' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/pages/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Навигационный guard для защиты роутов
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const gameSettings = useGameSettingsStore()

  // Ждем завершения инициализации (бесшумного обновления токена через cookie)
  await authStore.init()

  // Если роут требует аутентификацию
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // Если пользователь не авторизован, редирект на логин
      next({ name: 'login', query: { redirect: to.fullPath } })
    } else {
      // Проверяем, есть ли данные пользователя
      if (!authStore.user) {
        try {
          await authStore.fetchUser()
        } catch {
          // Если не удалось получить пользователя, редирект на логин
          next({ name: 'login', query: { redirect: to.fullPath } })
          return
        }
      }

      // Проверяем роль, если требуется
      if (to.meta.requiresRole && authStore.user?.role !== to.meta.requiresRole) {
        next({ name: 'home' }) // Редирект на главную, если нет прав
        return
      }

      if (authStore.user?.role === 'STUDENT') {
        try {
          await gameSettings.fetchGameSettings()
        } catch {
          next({ name: 'home' })
          return
        }

        const isGameTrial = to.query.trial === '1' && (to.name === 'garage' || to.name === 'avatar-demo')

        if (to.meta.requiresGame && !gameSettings.hasSelectedGame && !isGameTrial) {
          next({ name: 'game-select', query: { redirect: to.fullPath } })
          return
        }
        if (to.meta.gameType && gameSettings.activeGame !== to.meta.gameType && !isGameTrial) {
          next(gameSettings.isCarGame ? { name: 'garage' } : { name: 'avatar-demo' })
          return
        }
      }

      next()
    }
  } else if (to.name === 'home' && authStore.isAuthenticated && authStore.user?.role === 'TEACHER') {
    // Teachers see their dashboard as their home/cabinet page
    next({ name: 'teacher-dashboard' })
  } else {
    // Если роут не требует аутентификации (например, login/register)
    // и пользователь уже авторизован, редирект на главную
    if (to.name === 'login' || to.name === 'register') {
      if (authStore.isAuthenticated) {
        next({ name: 'home' })
      } else {
        next()
      }
    } else {
      next()
    }
  }
})

export default router

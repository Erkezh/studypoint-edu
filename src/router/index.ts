import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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
    component: () => import('@/pages/Analytics.vue'),
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
    path: '/profile',
    name: 'profile',
    component: () => import('@/pages/Profile.vue'),
    meta: { requiresAuth: true },
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
    path: '/admin/questions/list',
    name: 'admin-questions-list',
    component: () => import('@/pages/AdminQuestionsList.vue'),
    meta: { requiresAuth: true, requiresRole: 'ADMIN' },
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
        } catch (error) {
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

      next()
    }
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

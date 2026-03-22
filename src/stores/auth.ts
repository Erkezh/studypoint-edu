import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { UserMeResponse, AuthLoginRequest, AuthRegisterRequest } from '@/types/api'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const user = ref<UserMeResponse | null>(null)
  const loading = ref(false)
  const initialized = ref(false)

  // isAuthenticated проверяет только наличие токена, так как user может загружаться асинхронно
  const isAuthenticated = computed(() => !!accessToken.value)
  const isStudent = computed(() => user.value?.role === 'STUDENT')
  const isTeacher = computed(() => user.value?.role === 'TEACHER' || user.value?.role === 'ADMIN')

  const clearStoredAuth = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  const syncAuthBridge = () => {
    ;(window as any).__authStore = {
      accessToken: computed(() => accessToken.value),
      refreshToken: computed(() => refreshToken.value),
      getAccessToken: () => accessToken.value,
      getRefreshToken: () => refreshToken.value,
      setAccessToken: (token: string) => {
        accessToken.value = token
        localStorage.setItem('access_token', token)
      },
      setRefreshToken: (token: string) => {
        refreshToken.value = token
        localStorage.setItem('refresh_token', token)
      },
      logout: () => {
        accessToken.value = null
        refreshToken.value = null
        user.value = null
        clearStoredAuth()
      },
    }
  }

  // Инициализация store из localStorage
  const init = () => {
    if (initialized.value) {
      syncAuthBridge()
      return
    }

    const storedToken = localStorage.getItem('access_token')
    const storedRefresh = localStorage.getItem('refresh_token')
    const storedUser = localStorage.getItem('user')

    if (storedToken) {
      accessToken.value = storedToken
    }
    if (storedRefresh) {
      refreshToken.value = storedRefresh
    }
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (e) {
        console.error('Failed to parse stored user', e)
      }
    }

    initialized.value = true
    syncAuthBridge()
  }

  const login = async (credentials: AuthLoginRequest) => {
    loading.value = true
    try {
      const response = await authApi.login(credentials)
      if (response.data) {
        accessToken.value = response.data.access_token
        refreshToken.value = response.data.refresh_token
        user.value = response.data.user

        localStorage.setItem('access_token', response.data.access_token)
        localStorage.setItem('refresh_token', response.data.refresh_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        syncAuthBridge()

        const { useTrialQuestions } = await import('@/composables/useTrialQuestions')
        const trialQuestions = useTrialQuestions()
        if (response.data.user?.subscription?.is_active) {
          trialQuestions.resetTrialQuestions()
        }

        return response.data
      }

      throw new Error('Invalid response from server')
    } catch (error: any) {
      console.error('Login error:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const register = async (data: AuthRegisterRequest) => {
    loading.value = true
    try {
      const response = await authApi.register(data)
      if (response.data) {
        accessToken.value = response.data.access_token
        refreshToken.value = response.data.refresh_token
        user.value = response.data.user

        localStorage.setItem('access_token', response.data.access_token)
        localStorage.setItem('refresh_token', response.data.refresh_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        syncAuthBridge()

        return response.data
      }

      throw new Error('Invalid response from server')
    } catch (error: any) {
      console.error('Register error:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchUser = async () => {
    if (!accessToken.value) return

    try {
      const response = await authApi.getMe()
      if (response.data) {
        user.value = response.data
        localStorage.setItem('user', JSON.stringify(response.data))
      }
    } catch (error) {
      console.error('Failed to fetch user:', error)
      accessToken.value = null
      refreshToken.value = null
      user.value = null
      clearStoredAuth()
      syncAuthBridge()
    }
  }

  const logout = async () => {
    loading.value = true
    try {
      if (refreshToken.value) {
        await authApi.logout({ refresh_token: refreshToken.value })
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      accessToken.value = null
      refreshToken.value = null
      user.value = null
      clearStoredAuth()
      syncAuthBridge()

      loading.value = false
      const { default: router } = await import('@/router')
      router.push({ name: 'home' })
    }
  }

  const setAccessToken = (token: string) => {
    accessToken.value = token
    localStorage.setItem('access_token', token)
    syncAuthBridge()
  }

  const setRefreshToken = (token: string) => {
    refreshToken.value = token
    localStorage.setItem('refresh_token', token)
    syncAuthBridge()
  }

  return {
    accessToken,
    refreshToken,
    user,
    loading,
    isAuthenticated,
    isStudent,
    isTeacher,
    init,
    login,
    register,
    logout,
    fetchUser,
    setAccessToken,
    setRefreshToken,
  }
})

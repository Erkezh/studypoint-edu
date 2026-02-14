import axios, { type AxiosInstance, AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { v4 as uuidv4 } from 'uuid'
import type { ApiResponse } from '@/types/api'
import { API_BASE_URL } from '@/config/api'

// Генерация UUID для idempotency
let idempotencyKey: string | null = null

// Проверка доступности сервера при инициализации
if (typeof window !== 'undefined') {
  console.log('API Client initialized:', {
    baseURL: `${API_BASE_URL}/api/v1`,
    origin: window.location.origin,
    apiUrl: API_BASE_URL,
    env: import.meta.env.MODE,
  })
  
  // Опциональная проверка доступности сервера (можно отключить)
  if (import.meta.env.DEV) {
    fetch(`${API_BASE_URL}/api/v1/grades`)
      .then(() => console.log('✓ API server is reachable'))
      .catch((err) => console.warn('⚠ API server check failed:', err.message))
  }
}

// Создание Axios инстанса
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  // withCredentials только для запросов с авторизацией (устанавливается динамически)
  timeout: 30000, // 30 секунд таймаут
})

// Interceptor для добавления access token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Получаем токен из localStorage напрямую
    // authStore может быть не инициализирован на момент запроса
    const token = localStorage.getItem('access_token')
    
    // НЕ используем withCredentials, так как бэкенд возвращает Access-Control-Allow-Origin: *
    // с Access-Control-Allow-Credentials: true, что недопустимо в браузере
    // Токен отправляется через заголовок Authorization, а не через cookies
    config.withCredentials = false
    
    // Добавляем токен только если он есть
    // Для пробных вопросов можно создавать сессию без токена (если бэкенд поддерживает)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    if (import.meta.env.DEV) {
      console.log('Request config:', {
        url: config.url,
        method: config.method,
        withCredentials: config.withCredentials,
        hasToken: !!token,
      })
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Добавляем Idempotency-Key для операций, требующих идемпотентности
    const idempotentMethods = ['POST', 'PUT', 'PATCH']
    if (idempotentMethods.includes(config.method?.toUpperCase() || '')) {
      // Генерируем новый ключ для каждой попытки
      if (!idempotencyKey || config.url?.includes('/submit') || config.url?.includes('/attempts')) {
        idempotencyKey = uuidv4()
      }
      config.headers['Idempotency-Key'] = idempotencyKey
    }

    // Логируем только важные запросы для отладки (можно отключить в production)
    if (import.meta.env.DEV) {
      const fullUrl = `${config.baseURL}${config.url}`
      console.log('API Request:', {
        method: config.method?.toUpperCase(),
        url: config.url,
        fullUrl: fullUrl,
        data: config.data,
        params: config.params,
        headers: {
          Authorization: config.headers.Authorization ? 'Bearer ***' : undefined,
          'Idempotency-Key': config.headers['Idempotency-Key'],
          'Content-Type': config.headers['Content-Type'],
        },
        origin: window.location.origin,
      })
    }

    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Interceptor для обработки ответов и refresh token
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: any) => void
  reject: (reason?: any) => void
}> = []

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Обработка 401 - токен истёк
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Получаем refresh token из localStorage
      const refreshToken = localStorage.getItem('refresh_token')

      // Если нет refresh token, просто возвращаем ошибку без попытки refresh
      // Пользователь может продолжать использовать пробные вопросы без авторизации
      if (!refreshToken) {
        // Для пробных вопросов не требуется авторизация, просто возвращаем ошибку
        // Но устанавливаем понятное сообщение
        const errorData = error.response?.data
        let message = 'Бұл әрекетті орындау үшін авторизация қажет. Жүйеге кіріңіз.'
        if (errorData?.detail) {
          if (typeof errorData.detail === 'string') {
            message = errorData.detail
          } else if (errorData.detail.message) {
            message = errorData.detail.message
          } else if (errorData.detail.error?.message) {
            message = errorData.detail.error.message
          }
        }
        
        // Если это админский endpoint, предлагаем перелогиниться
        if (originalRequest.url?.includes('/admin/')) {
          message = 'Админ панеліне кіру үшін қайта кіріңіз. Токен мерзімі аяқталған.'
        } else if (errorData?.message) {
          message = errorData.message
        } else if (errorData?.error?.message) {
          message = errorData.error.message
        }
        error.message = message
        return Promise.reject(error)
      }

      if (isRefreshing) {
        // Если уже идёт refresh, добавляем запрос в очередь
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`
            }
            return apiClient(originalRequest)
          })
          .catch((err) => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {

        // Пробуем обновить токен
        const response = await axios.post<ApiResponse>(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          { refresh_token: refreshToken }
        )

        const newAccessToken = response.data?.data?.access_token

        if (newAccessToken) {
          localStorage.setItem('access_token', newAccessToken)
          const authStore = (window as any).__authStore
          if (authStore) {
            authStore.setAccessToken(newAccessToken)
          }
        }

        // Обновляем заголовок и повторяем запрос
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        }

        processQueue(null, newAccessToken)
        return apiClient(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError as Error, null)
        // Если refresh не удался - очищаем токены, но НЕ редиректим на логин
        // Пользователь может продолжать использовать пробные вопросы
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        const authStore = (window as any).__authStore
        if (authStore) {
          authStore.logout()
        }
        // Устанавливаем понятное сообщение об ошибке
        const refreshErrorData = (refreshError as any).response?.data
        let message = 'Сессия мерзімі өтті. Жүйеге қайта кіріңіз.'
        if (refreshErrorData?.detail) {
          if (typeof refreshErrorData.detail === 'string') {
            message = refreshErrorData.detail
          } else if (refreshErrorData.detail.message) {
            message = refreshErrorData.detail.message
          } else if (refreshErrorData.detail.error?.message) {
            message = refreshErrorData.detail.error.message
          }
        } else if (refreshErrorData?.message) {
          message = refreshErrorData.message
        } else if (refreshErrorData?.error?.message) {
          message = refreshErrorData.error.message
        }
        
        // Если это админский endpoint, предлагаем перелогиниться
        if (originalRequest.url?.includes('/admin/')) {
          message = 'Админ панеліне кіру үшін қайта кіріңіз. Токен мерзімі аяқталған.'
          // Редиректим на логин для админских endpoints
          const router = (await import('@/router')).default
          router.push({ 
            name: 'login', 
            query: { 
              redirect: router.currentRoute.value.fullPath,
              reason: 'token_expired'
            } 
          })
        }
        ;(refreshError as any).message = message
        // НЕ редиректим на логин - пользователь может продолжать без авторизации
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // Обработка 401 - если не обработано выше (например, после неудачного refresh)
    if (error.response?.status === 401) {
      const errorData = error.response.data
      let message = 'Бұл әрекетті орындау үшін авторизация қажет.'
      if (errorData?.detail) {
        if (typeof errorData.detail === 'string') {
          message = errorData.detail
        } else if (errorData.detail.message) {
          message = errorData.detail.message
        }
      } else if (errorData?.message) {
        message = errorData.message
      } else if (errorData?.error?.message) {
        message = errorData.error.message
      }
      error.message = message
    }

    // Обработка 400 - Bad Request (показываем детали ошибки)
    if (error.response?.status === 400) {
      const errorData = error.response.data
      console.error('API 400 Error:', {
        url: originalRequest.url,
        method: originalRequest.method,
        data: originalRequest.data,
        response: errorData,
      })
      
      // Извлекаем сообщение об ошибке
      let message = 'Bad Request'
      if (errorData?.detail) {
        if (Array.isArray(errorData.detail)) {
          message = errorData.detail.map((e: any) => e.msg || e.message).join(', ')
        } else if (typeof errorData.detail === 'string') {
          message = errorData.detail
        } else if (errorData.detail.message) {
          message = errorData.detail.message
        }
      } else if (errorData?.message) {
        message = errorData.message
      } else if (errorData?.error?.message) {
        message = errorData.error.message
      }
      
      error.message = message
    }

    // Обработка 402 - Payment Required
    if (error.response?.status === 402) {
      const errorData = error.response.data
      const message = errorData?.detail || errorData?.message || 'Практиканы жалғастыру үшін жазылым қажет. Профильде жазылымды рәсімдеңіз.'
      error.message = message
    }

    // Обработка 403 - Forbidden
    if (error.response?.status === 403) {
      const errorData = error.response.data
      const message = errorData?.detail || errorData?.message || 'Қол жеткізу тыйым салынған. Сізде бұл әрекетті орындау құқығы жоқ.'
      error.message = message
    }

    // Обработка 404 - Not Found
    if (error.response?.status === 404) {
      const errorData = error.response.data
      const message = errorData?.detail || errorData?.message || 'Ресурс табылмады.'
      error.message = message
    }

    // Обработка 409 - Conflict
    if (error.response?.status === 409) {
      const errorData = error.response.data
      const message = errorData?.detail || errorData?.message || 'Қайшылық: операция орындалуы мүмкін емес. Сессия бұрын аяқталған немесе өзгертілген болуы мүмкін.'
      error.message = message
    }

    // Обработка 422 - Unprocessable Entity (Validation Error)
    if (error.response?.status === 422) {
      const errorData = error.response.data
      let message = 'Деректерді валидациялау қатесі'
      if (errorData?.detail) {
        if (Array.isArray(errorData.detail)) {
          message = errorData.detail.map((e: any) => e.msg || e.message).join(', ')
        } else if (typeof errorData.detail === 'string') {
          message = errorData.detail
        } else if (errorData.detail.message) {
          message = errorData.detail.message
        }
      } else if (errorData?.message) {
        message = errorData.message
      }
      error.message = message
    }

    // Обработка 429 - rate limit
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after']
      const message = retryAfter
        ? `Сұраулар лимиті асып кетті. ${retryAfter} секундтан кейін қайталап көріңіз.`
        : 'Сұраулар лимиті асып кетті. Күте тұрыңыз.'
      error.message = message
    }

    // Обработка 500+ - Server Error
    if (error.response?.status && error.response.status >= 500) {
      const errorData = error.response.data
      const message = errorData?.detail || errorData?.message || 'Сервер қатесі. Кейінірек қайталап көріңіз.'
      error.message = message
    }

    // Обработка сетевых ошибок (нет ответа от сервера)
    if (!error.response) {
      const fullUrl = `${originalRequest.baseURL}${originalRequest.url}`
      console.error('Network Error Details:', {
        message: error.message,
        code: error.code,
        url: fullUrl,
        method: originalRequest.method,
        baseURL: originalRequest.baseURL,
        timeout: originalRequest.timeout,
        hasAuth: !!originalRequest.headers?.Authorization,
        requestConfig: {
          data: originalRequest.data,
          params: originalRequest.params,
        },
      })
      
      // Улучшаем сообщение об ошибке с более конкретной информацией
      if (error.code === 'ECONNABORTED') {
        error.message = `Күту уақыты асып кетті (${originalRequest.timeout}мс). Сервер ${fullUrl} мекенжайына жауап бермейді`
      } else if (error.code === 'ERR_NETWORK' || error.message === 'Network Error' || error.message?.includes('Network Error')) {
        // Проверяем, может быть это CORS проблема
        const isCorsIssue = error.message.includes('CORS') || error.code === 'ERR_CORS'
        if (isCorsIssue) {
          error.message = `CORS қатесі. Сервер ${window.location.origin} мекенжайынан сұрауларды рұқсат ететініне көз жеткізіңіз`
        } else {
          // Более информативное сообщение
          const method = originalRequest.method?.toUpperCase() || 'GET'
          error.message = `Ошибка сети при запросе ${method} ${fullUrl}. Проверьте, что сервер запущен на ${API_BASE_URL} и доступен.`
        }
      }
    }

    return Promise.reject(error)
  }
)

// Rate limiting: локальный счётчик для ограничения частоты отправки ответов
let attemptQueue: Array<() => Promise<any>> = []
let isProcessingAttempts = false
const MAX_ATTEMPTS_PER_MINUTE = 30
const attemptTimestamps: number[] = []

export const rateLimitedAttempt = async <T>(
  requestFn: () => Promise<T>,
  onRateLimit?: (retryAfter: number) => void
): Promise<T> => {
  const now = Date.now()
  const oneMinuteAgo = now - 60000

  // Очищаем старые записи
  while (attemptTimestamps.length > 0 && attemptTimestamps[0]! < oneMinuteAgo) {
    attemptTimestamps.shift()
  }

  if (attemptTimestamps.length >= MAX_ATTEMPTS_PER_MINUTE && attemptTimestamps.length > 0) {
    const oldestTimestamp = attemptTimestamps[0]
    if (oldestTimestamp !== undefined) {
      const retryAfter = Math.ceil((oldestTimestamp + 60000 - now) / 1000)
      if (onRateLimit) {
        onRateLimit(retryAfter)
      }
      throw new Error(`Rate limit exceeded. Try again in ${retryAfter} seconds.`)
    }
  }

  attemptTimestamps.push(now)
  return requestFn()
}

export default apiClient

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { practiceApi } from '@/api/practice'
import type {
  PracticeSessionResponse,
  PracticeSubmitRequest,
  PracticeSubmitResponse,
  QuestionPublic,
} from '@/types/api'
import router from '@/router'
import { useTrialQuestions } from '@/composables/useTrialQuestions'
import { useAuthStore } from '@/stores/auth'

const HEARTBEAT_INTERVAL = 30000 // 30 секунд
const INACTIVITY_THRESHOLD = 300000 // 5 минут

export const usePracticeStore = defineStore('practice', () => {
  const currentSession = ref<PracticeSessionResponse | null>(null)
  const currentQuestion = ref<QuestionPublic | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const heartbeatTimer = ref<number | null>(null)
  const lastActivity = ref<number>(Date.now())
  const rateLimitMessage = ref<string | null>(null)

  const smartscore = computed(() => currentSession.value?.smartscore || 0)
  const zone = computed(() => {
    const score = smartscore.value
    if (score < 60) return 'LEARNING'
    if (score < 80) return 'REFINING'
    return 'CHALLENGE'
  })
  const questionsAnswered = computed(() => currentSession.value?.questions_answered || 0)
  const correctCount = computed(() => currentSession.value?.correct_count || 0)
  const wrongCount = computed(() => currentSession.value?.wrong_count || 0)
  const timeElapsed = computed(() => currentSession.value?.time_elapsed_sec || 0)

  // Создание или восстановление сессии
  const createSession = async (skillId: number) => {
    loading.value = true
    error.value = null
    
    // НЕ проверяем пробные вопросы перед созданием сессии
    // Позволяем создать сессию без авторизации, проверка будет после каждого ответа
    // Если пробные вопросы исчерпаны, модальное окно покажется после ответа
    const authStore = useAuthStore()
    
    console.log('PracticeStore.createSession: isAuthenticated:', authStore.isAuthenticated)
    console.log('PracticeStore.createSession: user role:', authStore.user?.role)
    
    try {
      // Убеждаемся, что skillId - число
      const numericSkillId = typeof skillId === 'string' ? parseInt(skillId, 10) : skillId
      if (isNaN(numericSkillId)) {
        throw new Error('Invalid skill ID')
      }

      const response = await practiceApi.createSession({ skill_id: numericSkillId })
      if (response.data) {
        currentSession.value = response.data
        currentQuestion.value = response.data.current_question || null
        
        // Восстанавливаем из localStorage если есть сохранённая сессия
        const savedSessionId = localStorage.getItem(`session_${numericSkillId}`)
        if (savedSessionId && savedSessionId === response.data.id) {
          // Сессия восстановлена
        } else {
          localStorage.setItem(`session_${numericSkillId}`, response.data.id)
        }

        // Запускаем heartbeat
        startHeartbeat(response.data.id)

        // Сохраняем состояние в localStorage для восстановления
        saveSessionState()

        return response.data
      }
      throw new Error('Failed to create session')
    } catch (err: any) {
      console.error('PracticeStore: Failed to create session:', err)
      console.error('PracticeStore: Error response:', err.response?.data)
      console.error('PracticeStore: Error status:', err.response?.status)
      console.error('PracticeStore: isAuthenticated:', authStore.isAuthenticated)
      console.error('PracticeStore: user role:', authStore.user?.role)
      
      // Инициализируем trialQuestions для проверки
      const trialQuestions = useTrialQuestions()
      
      // Если ошибка 401 (Unauthorized)
      if (err.response?.status === 401) {
        // Если пользователь авторизован, но получил 401, это проблема с токеном
        if (authStore.isAuthenticated) {
          error.value = 'Авторизация қатесі. Токендің жарамды екенін тексеріңіз.'
          throw err
        }
        // Если пользователь не авторизован, но API требует авторизацию
        // Это означает, что бэкенд не поддерживает создание сессии без авторизации
        // Показываем сообщение, что требуется авторизация
        error.value = 'Сессияны құру үшін авторизация қажет. Жүйеге кіріңіз.'
        throw err
      }
      
      // Если ошибка 402 (Payment Required), обрабатываем отдельно
      if (err.response?.status === 402) {
        // Для авторизованных пользователей ошибка 402 не должна блокировать
        if (authStore.isAuthenticated) {
          error.value = 'Қол жеткізу қатесі. Қайталап көріңіз.'
          throw err
        }
        // Если пользователь не авторизован и пробные вопросы исчерпаны
        if (trialQuestions.isTrialQuestionsExhausted.value) {
          error.value = 'Сіз бүгін барлық сынақ сұрақтарды пайдаландыңыз. Шексіз қол жеткізу үшін жүйеге кіріңіз.'
          throw err
        } else {
          error.value = 'Практиканы жалғастыру үшін жазылым қажет. Профильде жазылымды рәсімдеңіз.'
        }
      } else {
        const errorMsg = err.response?.data?.detail 
          ? (Array.isArray(err.response.data.detail) 
            ? err.response.data.detail.map((e: any) => e.msg).join(', ')
            : err.response.data.detail)
          : err.message || 'Failed to create session'
        error.value = errorMsg
      }
      console.error('Failed to create session:', err.response?.data || err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Получение сессии
  const getSession = async (sessionId: string) => {
    loading.value = true
    error.value = null
    try {
      const response = await practiceApi.getSession(sessionId)
      if (response.data) {
        currentSession.value = response.data
        currentQuestion.value = response.data.current_question || null
        saveSessionState()
        startHeartbeat(sessionId)
        return response.data
      }
      throw new Error('Session not found')
    } catch (err: any) {
      const status = err.response?.status
      if (status === 404) {
        error.value = 'Сессия табылмады немесе аяқталған. Жаңа практиканы бастаңыз.'
        try {
          const raw = localStorage.getItem('practice_session_state')
          if (raw) {
            const state = JSON.parse(raw)
            if (state?.sessionId === sessionId) localStorage.removeItem('practice_session_state')
          }
        } catch (_) { /* ignore */ }
      } else {
        error.value = err.response?.data?.error?.message || err.message || 'Сессияны жүктеу мүмкін болмады.'
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  // Получение следующего вопроса
  const getNextQuestion = async (sessionId: string) => {
    if (!currentSession.value) return null

    try {
      const response = await practiceApi.getNextQuestion(sessionId)
      if (response.data) {
        currentQuestion.value = response.data.question || null
        if (currentSession.value) {
          currentSession.value.current_question = currentQuestion.value
        }
        saveSessionState()
        return currentQuestion.value
      }
      return null
    } catch (err: any) {
      error.value = err.message || 'Failed to get next question'
      throw err
    }
  }

  // Отправка ответа
  const submitAnswer = async (
    sessionId: string,
    data: PracticeSubmitRequest
  ): Promise<PracticeSubmitResponse | null> => {
    if (!currentSession.value) return null

    updateActivity()
    loading.value = true
    error.value = null
    rateLimitMessage.value = null

    try {
      console.log('PracticeStore: Submitting answer', {
        sessionId,
        data,
        submitted_answer_type: typeof data.submitted_answer,
      })

      const response = await practiceApi.submitAnswer(
        sessionId,
        data,
        (retryAfter) => {
          rateLimitMessage.value = `Жіберу лимиті асып кетті. ${retryAfter} секундтан кейін қайталап көріңіз.`
        }
      )

      if (response.data) {
        // Проверяем пробные вопросы и увеличиваем счетчик только для неавторизованных пользователей
        const authStore = useAuthStore()
        const trialQuestions = useTrialQuestions()
        
        // Увеличиваем счетчик пробных вопросов только для неавторизованных пользователей
        // Для всех авторизованных пользователей ограничения не применяются
        if (!authStore.isAuthenticated) {
          // Увеличиваем счетчик пробных вопросов
          const newCount = trialQuestions.incrementTrialQuestions()
          console.log('Trial questions count:', newCount)
          
          // Если пробные вопросы исчерпаны, отмечаем это
          if (newCount >= trialQuestions.TRIAL_QUESTIONS_LIMIT) {
            console.log('Trial questions exhausted')
          }
        }

        currentSession.value = response.data.session
        currentQuestion.value = response.data.next_question || null

        if (response.data.finished) {
          // Сессия завершена
          stopHeartbeat()
          await finishSession(sessionId)
          router.push({
            name: 'practice-results',
            params: { sessionId },
          })
        }

        saveSessionState()
        return response.data
      }
      throw new Error('Failed to submit answer')
    } catch (err: any) {
      // Обработка ошибки 402 (Payment Required)
      if (err.response?.status === 402) {
        const authStore = useAuthStore()
        const trialQuestions = useTrialQuestions()
        
        console.error('PracticeStore: 402 Payment Required error:', {
          isAuthenticated: authStore.isAuthenticated,
          userRole: authStore.user?.role,
          errorData: err.response?.data,
        })
        
        // Для авторизованных пользователей ошибка 402 не должна возникать
        // Если она возникла, это проблема с бэкендом или подпиской
        if (authStore.isAuthenticated) {
          // Пробуем повторить запрос или показываем более информативное сообщение
          const errorDetail = err.response?.data?.detail || err.response?.data?.message || 'Қол жеткізу құқығы жеткіліксіз'
          error.value = `Қол жеткізу қатесі: ${errorDetail}. Профильде жазылымды тексеріңіз немесе қайталап көріңіз.`
          console.error('PracticeStore: 402 error for authenticated user - this should not happen')
          throw err // Пробрасываем ошибку дальше, чтобы компонент мог её обработать
        }
        
        // Если пользователь не авторизован и пробные вопросы исчерпаны
        if (trialQuestions.isTrialQuestionsExhausted.value) {
          error.value = 'Сіз бүгін барлық сынақ сұрақтарды пайдаландыңыз. Шексіз қол жеткізу үшін жүйеге кіріңіз.'
          router.push({ 
            name: 'login', 
            query: { 
              redirect: router.currentRoute.value.fullPath,
              requireSubscription: 'true'
            } 
          })
        } else {
          error.value = 'Практиканы жалғастыру үшін жазылым қажет. Профильде жазылымды рәсімдеңіз.'
        }
      } else {
        const errorMsg = err.response?.data?.detail
          ? (Array.isArray(err.response.data.detail)
            ? err.response.data.detail.map((e: any) => e.msg).join(', ')
            : err.response.data.detail)
          : err.message || 'Failed to submit answer'
        
        error.value = errorMsg
      }
      
      console.error('PracticeStore: Submit answer error', {
        error: err.response?.data || err,
        requestData: data,
      })
      
      if (err.message?.includes('Rate limit')) {
        rateLimitMessage.value = err.message
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  // Завершение сессии
  const finishSession = async (sessionId: string) => {
    if (!currentSession.value) return

    try {
      await practiceApi.finishSession(sessionId)
      stopHeartbeat()

      // Очищаем сохранённое состояние
      if (currentSession.value.skill_id) {
        localStorage.removeItem(`session_${currentSession.value.skill_id}`)
      }
      localStorage.removeItem('practice_session_state')
    } catch (err: any) {
      // Если ошибка 409 (Conflict) - сессия уже завершена, это нормально
      if (err.response?.status === 409) {
        console.log('Session already finished (409), cleaning up...')
        // Продолжаем очистку, так как сессия уже завершена
      } else {
        console.error('Failed to finish session:', err)
        error.value = err.message || 'Failed to finish session'
      }
    } finally {
      resetSession()
    }
  }

  // Heartbeat для обновления времени активности
  const startHeartbeat = (sessionId: string) => {
    if (heartbeatTimer.value) {
      clearInterval(heartbeatTimer.value)
    }

    heartbeatTimer.value = window.setInterval(() => {
      if (!currentSession.value) return

      const now = Date.now()
      const inactiveTime = now - lastActivity.value

      // Если неактивность превышает порог, не отправляем heartbeat
      if (inactiveTime > INACTIVITY_THRESHOLD) {
        return
      }

      // Heartbeat можно отправить через обновление сессии
      // Или через специальный endpoint, если он есть в API
      updateActivity()
    }, HEARTBEAT_INTERVAL)
  }

  const stopHeartbeat = () => {
    if (heartbeatTimer.value) {
      clearInterval(heartbeatTimer.value)
      heartbeatTimer.value = null
    }
  }

  const updateActivity = () => {
    lastActivity.value = Date.now()
  }

  // Сохранение состояния сессии в localStorage
  const saveSessionState = () => {
    if (!currentSession.value) return

    try {
      const state = {
        sessionId: currentSession.value.id,
        skillId: currentSession.value.skill_id,
        lastActivity: lastActivity.value,
        timestamp: Date.now(),
      }
      localStorage.setItem('practice_session_state', JSON.stringify(state))
    } catch (err) {
      console.error('Failed to save session state:', err)
    }
  }

  // Восстановление состояния сессии из localStorage
  const restoreSessionState = async () => {
    try {
      const saved = localStorage.getItem('practice_session_state')
      if (!saved) return null

      const state = JSON.parse(saved)
      const age = Date.now() - state.timestamp

      // Восстанавливаем только если прошло менее 24 часов
      if (age < 24 * 60 * 60 * 1000) {
        return await getSession(state.sessionId)
      } else {
        localStorage.removeItem('practice_session_state')
        return null
      }
    } catch (err) {
      console.error('Failed to restore session state:', err)
      return null
    }
  }

  const resetSession = () => {
    stopHeartbeat()
    currentSession.value = null
    currentQuestion.value = null
    error.value = null
    rateLimitMessage.value = null
    lastActivity.value = Date.now()
    localStorage.removeItem('practice_session_state')
  }

  return {
    currentSession,
    currentQuestion,
    loading,
    error,
    rateLimitMessage,
    smartscore,
    zone,
    questionsAnswered,
    correctCount,
    wrongCount,
    timeElapsed,
    createSession,
    getSession,
    getNextQuestion,
    submitAnswer,
    finishSession,
    restoreSessionState,
    resetSession,
    updateActivity,
  }
})

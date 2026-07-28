import { ref, computed } from 'vue'

const TRIAL_QUESTIONS_LIMIT = 10
const TRIAL_QUESTIONS_KEY = 'trial_questions_count'
const TRIAL_QUESTIONS_START_TIME_KEY = 'trial_questions_start_time'
const TWENTY_FOUR_HOURS_MS = 24 * 60 * 60 * 1000

/**
 * Composable для управления пробными вопросами
 * Неавторизованный пользователь может ответить максимум на 10 вопросов в сумме.
 * По истечении 24 часов с момента первого вопроса лимит сбрасывается.
 */
export function useTrialQuestions() {
  // Проверяем 24-часовой интервал и сбрасываем счетчик, если прошло >= 24 часов
  const checkAndResetIfNeeded = (): void => {
    if (typeof window === 'undefined') return

    const startTimeStr = localStorage.getItem(TRIAL_QUESTIONS_START_TIME_KEY)
    if (startTimeStr) {
      const startTime = parseInt(startTimeStr, 10)
      const now = Date.now()

      if (isNaN(startTime) || now - startTime >= TWENTY_FOUR_HOURS_MS) {
        localStorage.setItem(TRIAL_QUESTIONS_KEY, '0')
        localStorage.removeItem(TRIAL_QUESTIONS_START_TIME_KEY)
      }
    }
  }

  // Получаем количество использованных пробных вопросов
  const getTrialQuestionsCount = (): number => {
    checkAndResetIfNeeded()
    const count = localStorage.getItem(TRIAL_QUESTIONS_KEY)
    return count ? parseInt(count, 10) : 0
  }

  // Увеличиваем счетчик пробных вопросов
  const incrementTrialQuestions = (): number => {
    checkAndResetIfNeeded()

    // Устанавливаем время первого пробного вопроса
    if (!localStorage.getItem(TRIAL_QUESTIONS_START_TIME_KEY)) {
      localStorage.setItem(TRIAL_QUESTIONS_START_TIME_KEY, Date.now().toString())
    }

    const current = getTrialQuestionsCount()
    const newCount = current + 1
    localStorage.setItem(TRIAL_QUESTIONS_KEY, newCount.toString())
    return newCount
  }

  // Сбрасываем счетчик (например, при авторизации)
  const resetTrialQuestions = () => {
    if (typeof window === 'undefined') return
    localStorage.removeItem(TRIAL_QUESTIONS_KEY)
    localStorage.removeItem(TRIAL_QUESTIONS_START_TIME_KEY)
  }

  // Расчет оставшегося времени до сброса (24 часа)
  const getTimeUntilReset = (): { hours: number; minutes: number; seconds: number; formatted: string } | null => {
    checkAndResetIfNeeded()
    const startTimeStr = localStorage.getItem(TRIAL_QUESTIONS_START_TIME_KEY)
    if (!startTimeStr) return null

    const startTime = parseInt(startTimeStr, 10)
    if (isNaN(startTime)) return null

    const now = Date.now()
    const elapsed = now - startTime
    const remainingMs = Math.max(0, TWENTY_FOUR_HOURS_MS - elapsed)

    if (remainingMs <= 0) return null

    const totalSeconds = Math.floor(remainingMs / 1000)
    const hours = Math.floor(totalSeconds / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    const seconds = totalSeconds % 60

    let formatted = ''
    if (hours > 0) {
      formatted = `${hours} сағат ${minutes} минут`
    } else if (minutes > 0) {
      formatted = `${minutes} минут`
    } else {
      formatted = `${seconds} секунд`
    }

    return { hours, minutes, seconds, formatted }
  }

  // Проверяем, можно ли использовать пробные вопросы
  const canUseTrialQuestions = computed(() => {
    return getTrialQuestionsCount() < TRIAL_QUESTIONS_LIMIT
  })

  // Получаем оставшееся количество пробных вопросов
  const remainingTrialQuestions = computed(() => {
    const used = getTrialQuestionsCount()
    return Math.max(0, TRIAL_QUESTIONS_LIMIT - used)
  })

  // Проверяем, использованы ли все пробные вопросы
  const isTrialQuestionsExhausted = computed(() => {
    return getTrialQuestionsCount() >= TRIAL_QUESTIONS_LIMIT
  })

  return {
    getTrialQuestionsCount,
    incrementTrialQuestions,
    resetTrialQuestions,
    getTimeUntilReset,
    canUseTrialQuestions,
    remainingTrialQuestions,
    isTrialQuestionsExhausted,
    TRIAL_QUESTIONS_LIMIT,
  }
}

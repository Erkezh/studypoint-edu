import { ref, computed } from 'vue'

const TRIAL_QUESTIONS_LIMIT = 10
const TRIAL_QUESTIONS_KEY = 'trial_questions_count'
const TRIAL_QUESTIONS_START_TIME_KEY = 'trial_questions_start_time'
const TWENTY_FOUR_HOURS_MS = 24 * 60 * 60 * 1000

// Глобальный реактивный счётчик — один на всё приложение
const _count = ref(0)
const _initialized = ref(false)

function _syncFromStorage(): void {
  if (typeof window === 'undefined') return

  // Проверяем 24-часовой интервал
  const startTimeStr = localStorage.getItem(TRIAL_QUESTIONS_START_TIME_KEY)
  if (startTimeStr) {
    const startTime = parseInt(startTimeStr, 10)
    if (isNaN(startTime) || Date.now() - startTime >= TWENTY_FOUR_HOURS_MS) {
      localStorage.setItem(TRIAL_QUESTIONS_KEY, '0')
      localStorage.removeItem(TRIAL_QUESTIONS_START_TIME_KEY)
    }
  }

  const raw = localStorage.getItem(TRIAL_QUESTIONS_KEY)
  _count.value = raw ? parseInt(raw, 10) : 0
}

/**
 * Composable для управления пробными вопросами.
 * Неавторизованный пользователь может ответить максимум на 10 вопросов в сумме.
 * По истечении 24 часов с момента первого вопроса лимит сбрасывается.
 *
 * Счётчик хранится в глобальном реактивном ref, синхронизированном с localStorage,
 * поэтому computed-свойства корректно обновляются при переходах между скиллами.
 */
export function useTrialQuestions() {
  // Инициализируем при первом вызове
  if (!_initialized.value) {
    _syncFromStorage()
    _initialized.value = true
  }

  const getTrialQuestionsCount = (): number => {
    _syncFromStorage()
    return _count.value
  }

  const incrementTrialQuestions = (): number => {
    _syncFromStorage()

    if (!localStorage.getItem(TRIAL_QUESTIONS_START_TIME_KEY)) {
      localStorage.setItem(TRIAL_QUESTIONS_START_TIME_KEY, Date.now().toString())
    }

    const newCount = _count.value + 1
    localStorage.setItem(TRIAL_QUESTIONS_KEY, newCount.toString())
    _count.value = newCount
    return newCount
  }

  const resetTrialQuestions = () => {
    if (typeof window === 'undefined') return
    localStorage.removeItem(TRIAL_QUESTIONS_KEY)
    localStorage.removeItem(TRIAL_QUESTIONS_START_TIME_KEY)
    _count.value = 0
  }

  const getTimeUntilReset = (): { hours: number; minutes: number; seconds: number; formatted: string } | null => {
    _syncFromStorage()
    const startTimeStr = localStorage.getItem(TRIAL_QUESTIONS_START_TIME_KEY)
    if (!startTimeStr) return null

    const startTime = parseInt(startTimeStr, 10)
    if (isNaN(startTime)) return null

    const remainingMs = Math.max(0, TWENTY_FOUR_HOURS_MS - (Date.now() - startTime))
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

  // Реактивные computed — зависят от _count.value (реактивный ref)
  const canUseTrialQuestions = computed(() => _count.value < TRIAL_QUESTIONS_LIMIT)
  const remainingTrialQuestions = computed(() => Math.max(0, TRIAL_QUESTIONS_LIMIT - _count.value))
  const isTrialQuestionsExhausted = computed(() => _count.value >= TRIAL_QUESTIONS_LIMIT)

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

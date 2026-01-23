import { ref, computed } from 'vue'

const TRIAL_QUESTIONS_LIMIT = 10
const TRIAL_QUESTIONS_KEY = 'trial_questions_count'
const TRIAL_QUESTIONS_DATE_KEY = 'trial_questions_date'

/**
 * Composable для управления пробными вопросами
 * Пользователь может ответить на 10 вопросов без подписки каждый день
 */
export function useTrialQuestions() {
  // Получаем текущую дату в формате YYYY-MM-DD
  const getTodayDate = (): string => {
    const today = new Date()
    return today.toISOString().split('T')[0] // YYYY-MM-DD
  }

  // Проверяем и сбрасываем счетчик, если дата изменилась
  const checkAndResetIfNeeded = (): void => {
    const savedDate = localStorage.getItem(TRIAL_QUESTIONS_DATE_KEY)
    const today = getTodayDate()
    
    // Если дата не сохранена или отличается от сегодняшней, сбрасываем счетчик
    if (!savedDate || savedDate !== today) {
      localStorage.setItem(TRIAL_QUESTIONS_KEY, '0')
      localStorage.setItem(TRIAL_QUESTIONS_DATE_KEY, today)
    }
  }

  // Получаем количество использованных пробных вопросов
  const getTrialQuestionsCount = (): number => {
    // Проверяем и сбрасываем, если нужно
    checkAndResetIfNeeded()
    
    const count = localStorage.getItem(TRIAL_QUESTIONS_KEY)
    return count ? parseInt(count, 10) : 0
  }

  // Увеличиваем счетчик пробных вопросов
  const incrementTrialQuestions = (): number => {
    // Проверяем и сбрасываем, если нужно
    checkAndResetIfNeeded()
    
    const current = getTrialQuestionsCount()
    const newCount = current + 1
    localStorage.setItem(TRIAL_QUESTIONS_KEY, newCount.toString())
    localStorage.setItem(TRIAL_QUESTIONS_DATE_KEY, getTodayDate())
    return newCount
  }

  // Сбрасываем счетчик (при входе с подпиской)
  const resetTrialQuestions = () => {
    localStorage.removeItem(TRIAL_QUESTIONS_KEY)
    localStorage.removeItem(TRIAL_QUESTIONS_DATE_KEY)
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
    canUseTrialQuestions,
    remainingTrialQuestions,
    isTrialQuestionsExhausted,
    TRIAL_QUESTIONS_LIMIT,
  }
}

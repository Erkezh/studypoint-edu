<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8">
      <div v-if="practiceStore.loading && !practiceStore.currentSession" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600">Сессия жүктелуде...</p>
      </div>

      <div v-else-if="practiceStore.error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        <p>{{ practiceStore.error }}</p>
        <Button @click="router.push({ name: 'home' })" class="mt-4" variant="primary">
          Басты бетке
        </Button>
      </div>

      <div v-else-if="practiceStore.currentSession && (currentQuestion || showingResult)">
        <!-- Информация о предыдущем прохождении теста -->
        <div v-if="previousBestScore !== null && previousBestScore > 0" class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-blue-700">
                <strong>Сіз бұл тестті бұрын өткенсіз.</strong> <span v-if="authStore.isAuthenticated">Сіздің ең жақсы нәтижеңіз: <strong class="text-blue-800">{{ previousBestScore }}</strong> SmartScore</span>
              </p>
            </div>
          </div>
        </div>

        <!-- Предупреждение о необходимости подписки (если пробные вопросы исчерпаны и пользователь не авторизован) -->
        <div v-if="shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value" class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-yellow-700">
                <strong>Сынақ кезеңі аяқталды.</strong> Практиканы жалғастыру үшін аккаунтқа кіріп, жазылымды рәсімдеңіз.
              </p>
            </div>
          </div>
        </div>

        <!-- Прогресс сессии -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6" :class="{ 'opacity-50': shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value }">
          <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
            <div>
              <div v-if="authStore.isAuthenticated" class="flex items-center gap-3">
                <h2 class="text-xl font-semibold">SmartScore: {{ practiceStore.smartscore }}</h2>
                <span v-if="previousBestScore !== null && previousBestScore > 0" class="text-sm text-gray-600">
                  (Ең жақсы: {{ previousBestScore }})
                </span>
              </div>
              <span
                :class="[
                  'px-3 py-1 rounded-full text-sm font-medium',
                  {
                    'bg-yellow-100 text-yellow-800': practiceStore.zone === 'LEARNING',
                    'bg-blue-100 text-blue-800': practiceStore.zone === 'REFINING',
                    'bg-purple-100 text-purple-800': practiceStore.zone === 'CHALLENGE',
                  },
                ]"
              >
                {{ getZoneText(practiceStore.zone) }}
              </span>
            </div>
            <div class="flex gap-4 text-sm">
              <div>
                <span class="text-gray-500">Уақыт:</span>
                <span class="ml-2 font-medium text-blue-600 font-mono">{{ formatTime(currentTime) }}</span>
              </div>
              <div>
                <span class="text-gray-500">Дұрыс:</span>
                <span class="ml-2 font-medium text-green-600">{{ practiceStore.correctCount }}</span>
              </div>
              <div>
                <span class="text-gray-500">Қате:</span>
                <span class="ml-2 font-medium text-red-600">{{ practiceStore.wrongCount }}</span>
              </div>
              <div>
                <span class="text-gray-500">Сұрақтар:</span>
                <span class="ml-2 font-medium">{{ practiceStore.questionsAnswered }}</span>
              </div>
            </div>
          </div>

          <div v-if="practiceStore.rateLimitMessage" class="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
            {{ practiceStore.rateLimitMessage }}
          </div>
          <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {{ error }}
          </div>
        </div>

        <!-- Результат ответа (показывается вместо вопроса после отправки) -->
        <div v-if="showingResult && lastResult" class="bg-white rounded-lg shadow-md p-6 mb-6">
          <div
            :class="[
              'rounded-lg p-6 mb-6',
              lastResult.is_correct
                ? 'bg-green-100 border border-green-300 text-green-800'
                : 'bg-red-100 border border-red-300 text-red-800',
            ]"
          >
            <p class="font-semibold text-lg mb-4">
              {{ lastResult.is_correct ? '✓ Дұрыс!' : '✗ Қате' }}
            </p>

            <!-- Показываем ответ пользователя и правильный ответ при неправильном ответе -->
            <div v-if="!lastResult.is_correct" class="space-y-3 mt-4">
              <div>
                <p class="font-medium mb-1">Сіздің жауабыңыз:</p>
                <p
                  class="text-sm bg-white px-3 py-2 rounded border border-red-400"
                  v-html="formatUserAnswer(userAnswer, lastQuestion)"
                ></p>
              </div>
              <div>
                <p class="font-medium mb-1">Дұрыс жауап:</p>
                <p
                  class="text-sm bg-white px-3 py-2 rounded border border-green-400"
                  v-html="formatCorrectAnswer(lastQuestion, lastResult)"
                ></p>
              </div>
            </div>

            <p v-if="lastResult.explanation" class="text-sm mt-4 italic">{{ lastResult.explanation }}</p>
          </div>

          <!-- Кнопки: Келесі (при !finished), К результатам (при finished). Без авто-перехода. -->
          <div class="flex gap-4 justify-center mt-4">
            <Button
              v-if="!lastResult.finished"
              @click="loadNextQuestion"
              :disabled="loadingNext"
              :loading="loadingNext"
              class="px-8"
            >
              Келесі
            </Button>
            <Button
              v-if="lastResult.finished"
              @click="goToResults"
              :disabled="loadingNext"
              class="px-8"
            >
              Нәтижелерге өту
            </Button>
            <Button
              v-if="!lastResult.finished"
              @click="finishSession"
              variant="outline"
              :disabled="loadingNext"
            >
              Сессияны аяқтау
            </Button>
          </div>
        </div>

        <!-- Вопрос (скрывается после отправки ответа) -->
        <div v-else-if="currentQuestion && !showingResult" class="bg-white rounded-lg shadow-md p-6 mb-6 relative" :class="{ 'opacity-75': shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value }">
          <!-- Overlay для блокировки взаимодействия, если пробные вопросы исчерпаны и пользователь не авторизован -->
          <div v-if="shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value" class="absolute inset-0 bg-white bg-opacity-60 z-10 flex items-center justify-center rounded-lg">
            <div class="text-center p-4 bg-white bg-opacity-90 rounded-lg border-2 border-yellow-300">
              <p class="text-lg font-semibold text-gray-700 mb-2">Жазылым қажет</p>
              <p class="text-sm text-gray-600">Жалғастыру үшін аккаунтқа кіріңіз</p>
            </div>
          </div>

          <div class="mb-4">
            <span class="text-sm text-gray-500">Деңгей:</span>
            <span class="ml-2 font-medium">{{ currentQuestion.level }}</span>
          </div>

          <div class="mb-6">
            <p
              class="text-lg font-medium mb-4"
              v-html="containsFraction(currentQuestion.prompt) ? formatFraction(currentQuestion.prompt) : currentQuestion.prompt"
            ></p>

            <!-- MCQ (Multiple Choice Question) -->
            <div v-if="currentQuestion.type === 'MCQ'" class="space-y-2">
              <div v-if="!currentQuestion.data?.choices && !currentQuestion.data?.options" class="text-red-500 text-sm mb-2">
                ⚠ Жауап нұсқалары жүктелмеді. Сұрақ деректерін тексеріңіз.
              </div>
              <div v-else class="text-sm text-gray-500 mb-2">
                Нұсқалар: {{ (currentQuestion.data?.choices || currentQuestion.data?.options || []).length }}
              </div>
              <button
                v-for="(option, index) in (currentQuestion.data?.choices || currentQuestion.data?.options || [])"
                :key="index"
                @click="submitMCQAnswer(option, index)"
                :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
                class="w-full text-left p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-html="formatMCQOption(option)"></span>
              </button>
              <div v-if="(currentQuestion.data?.choices || currentQuestion.data?.options || []).length === 0" class="text-gray-500 text-sm">
                Қолжетімді жауап нұсқалары жоқ
              </div>
            </div>

            <!-- NUMERIC -->
            <div v-else-if="currentQuestion.type === 'NUMERIC'" class="space-y-4">
              <input
                v-model.number="numericAnswer"
                type="number"
                step="any"
                placeholder="Санды енгізіңіз"
                class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                @keyup.enter="submitAnswer(numericAnswer)"
                :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
              />
              <Button
                @click="submitAnswer(numericAnswer)"
                :disabled="submitting || numericAnswer === null || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
                :loading="submitting"
              >
                Жіберу
              </Button>
            </div>

            <!-- TEXT -->
            <div v-else-if="currentQuestion.type === 'TEXT'" class="space-y-4">
              <input
                v-model="textAnswer"
                type="text"
                placeholder="Жауапты енгізіңіз"
                class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                @keyup.enter="submitAnswer(textAnswer)"
                :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
              />
              <Button
                @click="submitAnswer(textAnswer)"
                :disabled="submitting || !textAnswer || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
                :loading="submitting"
              >
                Жіберу
              </Button>
            </div>

            <!-- INTERACTIVE (интерактивные задания с кодом) -->
            <div v-else-if="currentQuestion.type === 'INTERACTIVE'" class="space-y-4">
              <InteractiveQuestion
                v-if="currentQuestion.data?.component_code"
                :component-code="currentQuestion.data.component_code"
                :question-data="currentQuestion.data"
                :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
                @answer="handleInteractiveAnswer"
              />
              <div v-else class="text-red-500 text-sm">
                ⚠ Интерактивное задание не загружено. Код компонента отсутствует.
              </div>
            </div>

            <!-- PLUGIN (iframe плагина из /static/plugins, embed — только задание; проверка через кнопку теста) -->
            <div v-else-if="currentQuestion.type === 'PLUGIN'" class="space-y-4">
              <iframe
                v-if="pluginIframeSrc"
                ref="pluginIframeRef"
                :src="pluginIframeSrc"
                :style="{ width: '100%', height: `${pluginEmbedHeight}px`, border: '1px solid #e5e7eb', borderRadius: '8px' }"
                sandbox="allow-scripts allow-same-origin"
                scrolling="yes"
                class="rounded-lg"
              />
              <div v-else class="text-red-500 text-sm">
                ⚠ Плагин не загружен. Отсутствуют plugin_id, plugin_version или entry.
              </div>
              <Button
                v-if="pluginIframeSrc"
                @click="requestPluginAnswer"
                :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
                :loading="submitting"
              >
                Жіберу
              </Button>
            </div>

            <!-- MULTI_SELECT или неизвестный тип -->
            <div v-else class="space-y-4">
              <p class="text-sm text-gray-500 mb-2">
                Сұрақ түрі: {{ currentQuestion.type || 'Белгісіз' }}
              </p>
              <!-- По умолчанию показываем текстовое поле -->
              <input
                v-model="textAnswer"
                type="text"
                placeholder="Жауапты енгізіңіз"
                class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                @keyup.enter="submitAnswer(textAnswer)"
                :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
              />
              <Button
                @click="submitAnswer(textAnswer)"
                :disabled="submitting || !textAnswer || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
                :loading="submitting"
              >
                Жіберу
              </Button>
            </div>
          </div>

              <div class="flex gap-4">
                <Button
                  @click="finishSession"
                  variant="outline"
                  :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
                >
                  Сессияны аяқтау
                </Button>
              </div>
        </div>
      </div>

      <div v-else class="text-center py-12 text-gray-600">
        <p>Сессия не найдена или завершена</p>
        <Button @click="router.push({ name: 'home' })" class="mt-4">Басты бетке</Button>
      </div>
    </main>
    <Footer />

    <!-- Модальное окно о завершении пробного периода -->
    <Modal
      :is-open="showTrialEndedModal"
      title="Сынақ кезеңі аяқталды"
      :show-close="false"
      @close="showTrialEndedModal = false"
    >
      <template #content>
        <p class="text-gray-700 mb-4">
          Сіз бүгін барлық {{ TRIAL_QUESTIONS_LIMIT }} тегін сұрақтарды пайдаландыңыз.
        </p>
        <p class="text-gray-700 mb-4">
          Практиканы жалғастыру және шексіз сұрақтарға қол жеткізу үшін аккаунтқа кіріңіз.
        </p>
      </template>
      <template #actions>
        <Button @click="goToLogin" variant="primary">
          Аккаунтқа кіру
        </Button>
        <Button @click="goToHome" variant="outline">
          Басты бетке
        </Button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePracticeStore } from '@/stores/practice'
import { useAuthStore } from '@/stores/auth'
import { useTrialQuestions } from '@/composables/useTrialQuestions'
import { useCatalogStore } from '@/stores/catalog'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import Modal from '@/components/ui/Modal.vue'
import InteractiveQuestion from '@/components/practice/InteractiveQuestion.vue'
import type { PracticeSubmitResponse, QuestionPublic } from '@/types/api'

interface Props {
  sessionId: string
}

const props = defineProps<Props>()
const router = useRouter()
const route = useRoute()
const practiceStore = usePracticeStore()
const authStore = useAuthStore()

// Инициализируем trialQuestions сразу, чтобы он был доступен везде
const trialQuestions = useTrialQuestions()
const catalogStore = useCatalogStore()

// Статистика навыка для отображения предыдущего результата
const previousBestScore = ref<number | null>(null)

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const currentQuestion = computed(() => practiceStore.currentQuestion)

const pluginIframeSrc = computed(() => {
  const q = currentQuestion.value
  if (!q || q.type !== 'PLUGIN' || !q.data) return ''
  const id = q.data.plugin_id
  const ver = q.data.plugin_version
  const entry = q.data.entry
  if (!id || !ver || !entry) return ''
  return `${API_BASE_URL}/static/plugins/${id}/${ver}/${entry}?embed=1`
})

const pluginEmbedHeight = computed(() => {
  const q = currentQuestion.value
  if (!q?.data?.height) return 250
  // Используем высоту из manifest или минимум 200, максимум 400
  return Math.min(400, Math.max(200, Number(q.data.height) || 250))
})

const submitting = ref(false)
const numericAnswer = ref<number | null>(null)
const textAnswer = ref('')
const lastResult = ref<PracticeSubmitResponse | null>(null)
const pluginIframeRef = ref<HTMLIFrameElement | null>(null)
const questionStartTime = ref(Date.now())
const showingResult = ref(false) // Показывать ли результат вместо вопроса
const userAnswer = ref<any>(null) // Сохраненный ответ пользователя
const lastQuestion = ref<QuestionPublic | null>(null) // Последний вопрос для отображения правильного ответа
const loadingNext = ref(false) // Загрузка следующего вопроса
const currentTime = ref(0) // Текущее время сессии в секундах
let timeInterval: number | null = null // Интервал для обновления времени
const error = ref<string | null>(null) // Ошибка для отображения

// Для всех авторизованных пользователей ограничения не применяются
const hasActiveSubscription = computed(() => {
  // Все авторизованные пользователи имеют доступ без ограничений
  return authStore.isAuthenticated
})
const isAuthenticated = computed(() => authStore.isAuthenticated)
// Для авторизованных пользователей пробные вопросы не применяются
const shouldCheckTrialQuestions = computed(() => !isAuthenticated.value)
const remainingTrialQuestions = computed(() => trialQuestions.remainingTrialQuestions.value)
const TRIAL_QUESTIONS_LIMIT = trialQuestions.TRIAL_QUESTIONS_LIMIT

// Модальное окно для завершения пробного периода
const showTrialEndedModal = ref(false)

const goToLogin = () => {
  showTrialEndedModal.value = false
  router.push({
    name: 'login',
    query: {
      redirect: router.currentRoute.value.fullPath,
      requireSubscription: 'true'
    }
  })
}

const goToHome = () => {
  showTrialEndedModal.value = false
  router.push({ name: 'home' })
}

const getZoneText = (zone: string) => {
  const zones: Record<string, string> = {
    LEARNING: 'Оқу',
    REFINING: 'Жетілдіру',
    CHALLENGE: 'Сынақ',
  }
  return zones[zone] || zone
}

// Форматирование времени в формат MM:SS или HH:MM:SS
const formatTime = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// Запуск таймера
const startTimer = () => {
  // Останавливаем предыдущий таймер, если он есть
  stopTimer()

  // Инициализируем время из store или начинаем с 0
  const initialTime = practiceStore.timeElapsed || 0
  currentTime.value = initialTime

  // Обновляем время каждую секунду
  timeInterval = setInterval(() => {
    currentTime.value++
  }, 1000) as unknown as number
}

// Остановка таймера
const stopTimer = () => {
  if (timeInterval !== null) {
    clearInterval(timeInterval)
    timeInterval = null
  }
}

// Функция для форматирования дробей в красивом виде
const formatFraction = (text: string): string => {
  // Паттерн для дробей вида "a/b", "a/b/c" (смешанные дроби), "a/b + c/d" и т.д.
  // Заменяем простые дроби вида "число/число" на HTML с вертикальной чертой
  return text.replace(
    /(\d+)\/(\d+)/g,
    '<span class="inline-flex flex-col items-center mx-0.5"><span class="border-b border-current pb-0.5">$1</span><span>$2</span></span>'
  )
}

// Функция для проверки, содержит ли текст дробь
const containsFraction = (text: string): boolean => {
  return /\d+\/\d+/.test(text)
}

// Форматирование варианта MCQ для отображения
const formatMCQOption = (option: any): string => {
  let result: string
  if (typeof option === 'string') {
    result = option
  } else if (typeof option === 'object' && option !== null) {
    result = option.label || option.text || option.value || String(option)
  } else {
    result = String(option)
  }

  // Если содержит дробь, форматируем её
  if (containsFraction(result)) {
    return formatFraction(result)
  }
  return result
}

// Форматирование ответа пользователя для отображения
const formatUserAnswer = (answer: any, question: QuestionPublic | null): string => {
  if (!question || answer === null || answer === undefined) return String(answer || '')

  let result: string
  if (question.type === 'MCQ') {
    result = formatMCQOption(answer)
  } else if (question.type === 'NUMERIC') {
    result = String(answer)
  } else if ((question.type === 'PLUGIN' || question.type === 'INTERACTIVE') && typeof answer === 'object' && answer !== null) {
    result = (answer as any).question || JSON.stringify(answer)
  } else {
    result = String(answer)
  }

  // Если содержит дробь, форматируем её
  if (containsFraction(result)) {
    return formatFraction(result)
  }
  return result
}

// Извлечение правильного ответа из explanation
const extractAnswerFromExplanation = (explanation: string | null | undefined): string | null => {
  if (!explanation) return null

  // Пытаемся найти ответ в формате "= 104" или "=104" в конце строки
  const equalsMatch = explanation.match(/=\s*(\d+(?:\.\d+)?)\s*$/i)
  if (equalsMatch) {
    return equalsMatch[1]
  }

  // Пытаемся найти число после знака равенства в любом месте
  const equalsAnywhere = explanation.match(/=\s*(\d+(?:\.\d+)?)/i)
  if (equalsAnywhere) {
    return equalsAnywhere[1]
  }

  // Пытаемся найти последнее число в строке (может быть ответом)
  const numbers = explanation.match(/\d+(?:\.\d+)?/g)
  if (numbers && numbers.length > 0) {
    // Берем последнее число как потенциальный ответ
    return numbers[numbers.length - 1]
  }

  return null
}

// Форматирование правильного ответа для отображения
const formatCorrectAnswer = (question: QuestionPublic | null, result: PracticeSubmitResponse | null): string => {
  // Логируем только в режиме разработки
  if (import.meta.env.DEV && !result?.is_correct) {
    console.log('Formatting correct answer:', {
      question,
      result,
      resultKeys: result ? Object.keys(result) : [],
      explanation: result?.explanation,
    })
  }

  // Сначала проверяем результат ответа (может содержать правильный ответ)
  if (result) {
    const resultAny = result as any
    // Логируем только в режиме разработки и только если ответ неправильный
    if (import.meta.env.DEV && !result.is_correct) {
      console.log('Checking result fields:', {
        correct_answer: resultAny.correct_answer,
        expected_answer: resultAny.expected_answer,
        answer: resultAny.answer,
        explanation: resultAny.explanation,
        allKeys: Object.keys(resultAny),
      })
    }

    // Проверяем явные поля
    if (resultAny.correct_answer !== undefined && resultAny.correct_answer !== null) {
      const answer = String(resultAny.correct_answer)
      if (containsFraction(answer)) {
        return formatFraction(answer)
      }
      return answer
    }
    if (resultAny.expected_answer !== undefined && resultAny.expected_answer !== null) {
      const answer = String(resultAny.expected_answer)
      if (containsFraction(answer)) {
        return formatFraction(answer)
      }
      return answer
    }
    if (resultAny.answer !== undefined && resultAny.answer !== null) {
      const answer = String(resultAny.answer)
      if (containsFraction(answer)) {
        return formatFraction(answer)
      }
      return answer
    }

    // Пытаемся извлечь из explanation
    if (result.explanation) {
      const extracted = extractAnswerFromExplanation(result.explanation)
      if (extracted) {
        // Логируем только в режиме разработки
        if (import.meta.env.DEV) {
          console.log('Extracted answer from explanation:', extracted)
        }
        if (containsFraction(extracted)) {
          return formatFraction(extracted)
        }
        return extracted
      }
    }
  }

  if (!question) {
    // Если есть explanation в результате, пытаемся извлечь оттуда
    if (result?.explanation) {
      const extracted = extractAnswerFromExplanation(result.explanation)
      if (extracted) {
        return extracted
      }
    }
    return 'Правильный ответ не указан'
  }

  // Логируем только в режиме разработки
  if (import.meta.env.DEV && !result?.is_correct) {
    console.log('Checking question data:', {
      type: question.type,
      data: question.data,
      dataKeys: question.data ? Object.keys(question.data) : [],
    })
  }

  // Пытаемся получить правильный ответ из данных вопроса
  if (question.data?.correct_answer !== undefined && question.data.correct_answer !== null) {
    return String(question.data.correct_answer)
  }

  // Для MCQ пытаемся найти правильный вариант
  if (question.type === 'MCQ') {
    const choices = question.data?.choices || question.data?.options || []
    console.log('MCQ question - looking for correct answer:', {
      choices,
      choicesLength: choices.length,
      correctIndex: question.data?.correct_index,
      answer: question.data?.answer,
      correctAnswer: question.data?.correct_answer
    })

    // Сначала проверяем correct_answer
    if (question.data?.correct_answer !== undefined && question.data.correct_answer !== null) {
      const correct = question.data.correct_answer
      // Если это индекс, получаем вариант по индексу
      if (typeof correct === 'number' && choices[correct] !== undefined) {
        const option = choices[correct]
        return typeof option === 'object' ? (option.label || option.text || option.value || String(option)) : String(option)
      }
      // Если это значение, возвращаем его
      const answerStr = String(correct)
      if (containsFraction(answerStr)) {
        return formatFraction(answerStr)
      }
      return answerStr
    }

    // Проверяем correct_index
    const correctIndex = question.data?.correct_index
    if (correctIndex !== undefined && choices[correctIndex] !== undefined) {
      const correct = choices[correctIndex]
      const answerStr = typeof correct === 'object' ? (correct.label || correct.text || correct.value || String(correct)) : String(correct)
      if (containsFraction(answerStr)) {
        return formatFraction(answerStr)
      }
      return answerStr
    }

    // Если есть answer в data
    if (question.data?.answer !== undefined && question.data.answer !== null) {
      const answer = question.data.answer
      // Если это индекс, получаем вариант по индексу
      if (typeof answer === 'number' && choices[answer] !== undefined) {
        const option = choices[answer]
        const answerStr = typeof option === 'object' ? (option.label || option.text || option.value || String(option)) : String(option)
        if (containsFraction(answerStr)) {
          return formatFraction(answerStr)
        }
        return answerStr
      }
      const answerStr = String(answer)
      if (containsFraction(answerStr)) {
        return formatFraction(answerStr)
      }
      return answerStr
    }

    // Пытаемся извлечь из explanation, если это MCQ
    if (result?.explanation) {
      const extracted = extractAnswerFromExplanation(result.explanation)
      if (extracted) {
        // Проверяем, соответствует ли извлеченный ответ одному из вариантов
        const matchingChoice = choices.find((c: any) => {
          const choiceStr = typeof c === 'object' ? (c.label || c.text || c.value || String(c)) : String(c)
          return choiceStr === extracted || String(c) === extracted
        })
        if (matchingChoice) {
          const answerStr = typeof matchingChoice === 'object' ? (matchingChoice.label || matchingChoice.text || matchingChoice.value || String(matchingChoice)) : String(matchingChoice)
          if (containsFraction(answerStr)) {
            return formatFraction(answerStr)
          }
          return answerStr
        }
        // Если не нашли совпадение, возвращаем извлеченное значение
        if (containsFraction(extracted)) {
          return formatFraction(extracted)
        }
        return extracted
      }
    }
  }

  // Для NUMERIC и TEXT
  if (question.data?.answer !== undefined && question.data.answer !== null) {
    const answer = String(question.data.answer)
    // Если содержит дробь, форматируем её
    if (containsFraction(answer)) {
      return formatFraction(answer)
    }
    return answer
  }

  // Если ничего не найдено, пытаемся вычислить правильный ответ из вопроса
  // Для вопроса "What is the last digit of 41?" правильный ответ - 1
  if (question.prompt) {
    const prompt = question.prompt.toLowerCase()
    if (prompt.includes('last digit')) {
      const match = question.prompt.match(/\d+/)
      if (match) {
        const number = parseInt(match[0])
        const lastDigit = number % 10
        // Логируем только в режиме разработки
        if (import.meta.env.DEV) {
          console.log('Computed last digit:', { number, lastDigit })
        }
        return String(lastDigit)
      }
    }
  }

  // Последняя попытка - извлечь из explanation
  if (result?.explanation) {
    const extracted = extractAnswerFromExplanation(result.explanation)
    if (extracted) {
      // Если содержит дробь, форматируем её
      if (containsFraction(extracted)) {
        return formatFraction(extracted)
      }
      return extracted
    }
  }

  return 'Правильный ответ не указан'
}

// Обработка ответа для MCQ вопросов
const submitMCQAnswer = async (option: any, index: number) => {
  if (!currentQuestion.value || !practiceStore.currentSession || submitting.value || showingResult.value) return

  const choices = currentQuestion.value.data?.choices || currentQuestion.value.data?.options || []

  // Для MCQ важно отправить правильное значение
  // Правильный ответ может быть:
  // 1. ID варианта (например, "A", "B", "C") - если варианты имеют поле "id"
  // 2. Само значение варианта (например, "5", "56") - если варианты простые значения
  // 3. Индекс варианта (например, "0", "1", "2") - если правильный ответ хранится как индекс

  let choiceValue: string
  const exactChoice = choices[index]

  if (exactChoice !== undefined) {
    // Если вариант - объект с полем "id", используем ID (например, "A", "B", "C")
    if (typeof exactChoice === 'object' && exactChoice !== null && exactChoice.id !== undefined) {
      choiceValue = String(exactChoice.id).trim()
    }
    // Если вариант - объект без "id", используем value, label, text или choice
    else if (typeof exactChoice === 'object' && exactChoice !== null) {
      const extracted = exactChoice.value !== undefined ? String(exactChoice.value) :
                        (exactChoice.label || exactChoice.text || exactChoice.choice || String(exactChoice))
      choiceValue = typeof extracted === 'string' ? extracted.trim() : String(extracted)
    }
    // Если вариант - строка или число, используем его значение
    else if (typeof exactChoice === 'string') {
      choiceValue = exactChoice.trim()
    } else if (typeof exactChoice === 'number') {
      choiceValue = String(exactChoice)
    } else {
      choiceValue = String(exactChoice)
    }
  } else {
    // Fallback: используем переданный option
    if (typeof option === 'string') {
      choiceValue = option.trim()
    } else if (typeof option === 'number') {
      choiceValue = String(option)
    } else if (typeof option === 'object' && option !== null) {
      // Если option - объект с "id", используем ID
      if (option.id !== undefined) {
        choiceValue = String(option.id).trim()
      } else {
        const extracted = option.value !== undefined ? String(option.value) :
                          (option.label || option.text || option.choice || String(option))
        choiceValue = typeof extracted === 'string' ? extracted.trim() : String(extracted)
      }
    } else {
      choiceValue = String(option || index)
    }
  }

  // Логируем только в режиме разработки
  if (import.meta.env.DEV) {
    console.log('MCQ choice prepared:', {
      original: option,
      formatted: choiceValue,
      index: index,
      exactChoice: exactChoice,
      allChoices: choices.map((c: any, i: number) => ({
        index: i,
        value: c,
        type: typeof c,
        id: typeof c === 'object' ? c.id : undefined,
        asString: typeof c === 'string' ? c.trim() : (typeof c === 'number' ? String(c) : String(c))
      }))
    })
  }

  // Сохраняем для отображения - сохраняем оригинальный вариант для правильного отображения
  userAnswer.value = typeof option === 'object' ? (option.label || option.text || option.value || String(option)) : option
  lastQuestion.value = { ...currentQuestion.value }

  // Вызываем submitAnswer с уже подготовленной строкой
  await submitAnswer(choiceValue, 'MCQ')
}

// Обработчик ответа для интерактивных заданий
const handleInteractiveAnswer = async (answer: any) => {
  await submitAnswer(answer, 'INTERACTIVE')
}

const submitAnswer = async (answer: any, questionType?: string) => {
  if (!currentQuestion.value || !practiceStore.currentSession || submitting.value || showingResult.value) return

  submitting.value = true

  // Обновление сессии перед отправкой теперь происходит ниже, после создания requestData
  // Это позволяет избежать дублирования и правильно обновить questionId

  // Сохраняем ответ пользователя и текущий вопрос (если еще не сохранено)
  if (userAnswer.value === null) {
    userAnswer.value = answer
    lastQuestion.value = { ...currentQuestion.value }
  }

  // Определяем тип вопроса
  const qType = questionType || currentQuestion.value.type

  // Проверяем, что у нас есть актуальный вопрос
  if (!currentQuestion.value || !currentQuestion.value.id) {
    error.value = 'Вопрос не найден. Обновите страницу.'
    submitting.value = false
    return
  }

  // Объявляем переменные для использования в catch блоке
  let requestData: any = null
  let submittedAnswer: Record<string, any> | null = null

  try {
    const timeSpent = Math.max(0, Math.min(3600, Math.floor((Date.now() - questionStartTime.value) / 1000)))

    // Формируем submitted_answer - API ожидает объект Record<string, any>
    // Для MCQ API ожидает { choice: "..." } - ОБЯЗАТЕЛЬНО строка
    submittedAnswer = {} as Record<string, any>

    if (qType === 'MCQ') {
      // Для MCQ API ожидает поле "choice" со СТРОКОЙ
      // Важно: строка должна точно соответствовать одному из вариантов в choices
      const choices = currentQuestion.value.data?.choices || currentQuestion.value.data?.options || []
      let choiceStr: string

      if (typeof answer === 'string') {
        choiceStr = answer.trim()
      } else if (typeof answer === 'number') {
        // Если число, преобразуем в строку
        choiceStr = String(answer)
      } else {
        choiceStr = String(answer).trim()
      }

      // Проверяем, что choiceStr не пустой
      if (!choiceStr || choiceStr === '') {
        throw new Error('Не выбран вариант ответа')
      }

      // Проверяем, что выбранный вариант существует в списке choices
      // Важно: сравниваем точно, учитывая тип исходного варианта
      const choiceExists = choices.some((c: any) => {
        // Если вариант - число, сравниваем как число и как строка
        if (typeof c === 'number') {
          return String(c) === choiceStr || c === Number(choiceStr)
        }
        // Если вариант - строка, сравниваем как строки (с учетом trim)
        if (typeof c === 'string') {
          return c.trim() === choiceStr || c === choiceStr
        }
        // Если вариант - объект, извлекаем значение и сравниваем
        if (typeof c === 'object' && c !== null) {
          const cValue = c.value !== undefined ? String(c.value) : (c.label || c.text || String(c))
          return String(cValue).trim() === choiceStr || String(c) === choiceStr
        }
        // Для других типов - простое сравнение строк
        return String(c) === choiceStr
      })

      if (!choiceExists && choices.length > 0) {
        console.warn('Selected choice does not match any option:', {
          selected: choiceStr,
          choices: choices,
          choiceTypes: choices.map((c: any) => typeof c),
          allChoicesAsStrings: choices.map((c: any) => {
            if (typeof c === 'string') return c.trim()
            if (typeof c === 'number') return String(c)
            if (typeof c === 'object') return String(c.value || c.label || c.text || c)
            return String(c)
          })
        })
      }

      submittedAnswer = { choice: choiceStr }

      // Логируем только важную информацию (можно отключить в production)
      if (import.meta.env.DEV) {
        console.log('MCQ answer formatted for API:', {
          original: answer,
          formatted: choiceStr,
          type: typeof choiceStr,
          questionChoices: choices,
          choiceExists: choiceExists,
          submittedAnswer: submittedAnswer,
          questionId: currentQuestion.value.id,
          questionPrompt: currentQuestion.value.prompt,
        })
      }
    } else if (qType === 'NUMERIC') {
      // Для NUMERIC - число в поле "value"
      const numValue = typeof answer === 'number' ? answer : parseFloat(String(answer))
      if (isNaN(numValue)) {
        throw new Error('Некорректное числовое значение')
      }
      submittedAnswer = { value: numValue }
    } else if (qType === 'INTERACTIVE' || qType === 'PLUGIN') {
      // INTERACTIVE / PLUGIN — ответ объектом (например userAnswer от плагина)
      if (typeof answer === 'object' && answer !== null) {
        submittedAnswer = answer
      } else {
        submittedAnswer = { answer: String(answer) }
      }
    } else {
      // Для TEXT и других типов - строка в поле "answer"
      submittedAnswer = { answer: String(answer) }
    }

    // Убеждаемся, что объект не пустой
    if (Object.keys(submittedAnswer).length === 0) {
      submittedAnswer = { answer: String(answer) }
    }

    // Для генераторов используем оригинальный ID из data._generator_id
    // Для обычных вопросов используем числовой ID
    // ВАЖНО: Используем актуальный questionId из currentQuestion.value,
    // который уже должен быть синхронизирован с сервером
    let questionId: string | number

    // Проверяем, есть ли _generator_id (для генераторов)
    const generatorId = currentQuestion.value.data?._generator_id
    if (generatorId) {
      // Для генераторов используем оригинальный строковый ID
      // Бэкенд сравнивает current_q_id (строка) с str(req.question_id)
      // ВАЖНО: _generator_id должен точно совпадать с current_question_id в state сессии
      questionId = String(generatorId)

      if (import.meta.env.DEV) {
        console.log('Using generator question ID:', {
          generatorId,
          questionId,
          questionIdType: typeof questionId,
          currentQuestionData: currentQuestion.value.data,
        })
      }
    } else {
      // Для обычных вопросов (включая PLUGIN) используем числовой ID
      // ВАЖНО: Для PLUGIN вопросов question_id должен совпадать с last_question_id в сессии
      // Используем ID из currentQuestion, который должен быть синхронизирован с сервером
      const qId = currentQuestion.value.id
      questionId = typeof qId === 'number' ? qId : Number(qId)

      // Проверяем, что ID валидный
      if (isNaN(questionId as number)) {
        error.value = 'Неверный ID вопроса. Обновите страницу.'
        submitting.value = false
        return
      }

      // Для PLUGIN вопросов проверяем, что question_id совпадает с last_question_id в сессии
      // Если не совпадает, это может привести к 409 ошибке
      if (currentQuestion.value.type === 'PLUGIN' && practiceStore.currentSession?.last_question_id) {
        const sessionLastQId = typeof practiceStore.currentSession.last_question_id === 'number'
          ? practiceStore.currentSession.last_question_id
          : Number(practiceStore.currentSession.last_question_id)

        if (!isNaN(sessionLastQId) && sessionLastQId !== questionId) {
          console.warn('PLUGIN question ID mismatch:', {
            currentQuestionId: questionId,
            sessionLastQuestionId: sessionLastQId,
            currentQuestion: currentQuestion.value,
          })
          // Используем last_question_id из сессии, чтобы избежать 409
          questionId = sessionLastQId
          console.log('Using session last_question_id instead:', questionId)
        }
      }

      if (import.meta.env.DEV) {
        console.log('Using regular question ID:', {
          qId,
          questionId,
          questionIdType: typeof questionId,
          sessionLastQuestionId: practiceStore.currentSession?.last_question_id,
          questionType: currentQuestion.value?.type,
        })
      }
    }

    // Для PLUGIN вопросов (не генераторов) нужно убедиться, что question_id совпадает с last_question_id
    // в сессии. Если они не совпадают, это может привести к 409 ошибке.
    // Для генераторов используем _generator_id, который должен совпадать с current_question_id в state.

    requestData = {
      question_id: questionId,
      submitted_answer: submittedAnswer,
      time_spent_sec: timeSpent,
    }

    // Логируем для диагностики
    if (import.meta.env.DEV) {
      console.log('Preparing to submit:', {
        questionId,
        questionIdType: typeof questionId,
        currentQuestionId: currentQuestion.value?.id,
        currentQuestionType: currentQuestion.value?.type,
        isGenerator: !!currentQuestion.value?.data?._generator_id,
        sessionLastQuestionId: practiceStore.currentSession?.last_question_id,
      })
    }

    // Логируем для диагностики (всегда в DEV режиме)
    if (import.meta.env.DEV) {
      console.log('=== SUBMIT ANSWER DEBUG ===')
      console.log('Question ID details:', {
        questionId,
        questionIdType: typeof questionId,
        questionIdAsString: String(questionId),
        questionIdTrimmed: String(questionId).trim(),
        currentQuestionId: currentQuestion.value?.id,
        currentQuestionGeneratorId: currentQuestion.value?.data?._generator_id,
        currentQuestionGeneratorIdType: typeof currentQuestion.value?.data?._generator_id,
        currentQuestionGeneratorIdString: String(currentQuestion.value?.data?._generator_id || ''),
        sessionId: practiceStore.currentSession?.id,
        isGenerator: !!currentQuestion.value?.data?._generator_id,
        currentQuestionData: currentQuestion.value?.data,
      })
      console.log('Request data:', {
        ...requestData,
        question_id_type: typeof requestData.question_id,
        question_id_string: String(requestData.question_id),
      })
      console.log('=== END DEBUG ===')
    }

    const response = await practiceStore.submitAnswer(practiceStore.currentSession.id, requestData)

    if (response) {
      // Логируем только если ответ неправильный или в режиме разработки
      if (import.meta.env.DEV && !response.is_correct) {
        console.warn('Incorrect answer received:', {
          is_correct: response.is_correct,
          submittedAnswer: submittedAnswer,
          userAnswer: userAnswer.value,
          questionChoices: currentQuestion.value.data?.choices || currentQuestion.value.data?.options,
          explanation: response.explanation
        })
      }

      // Детальная диагностика для MCQ (всегда в режиме разработки)
      if (qType === 'MCQ' && import.meta.env.DEV) {
        const choices = currentQuestion.value.data?.choices || currentQuestion.value.data?.options || []
        console.log('MCQ DIAGNOSTICS:', {
          submittedChoice: submittedAnswer.choice,
          submittedChoiceType: typeof submittedAnswer.choice,
          submittedChoiceValue: String(submittedAnswer.choice),
          allChoices: choices,
          choicesTypes: choices.map((c: any) => typeof c),
          choicesAsStrings: choices.map((c: any) => {
            if (typeof c === 'string') return c.trim()
            if (typeof c === 'number') return String(c)
            if (typeof c === 'object') return String(c.value || c.label || c.text || c)
            return String(c)
          }),
          questionData: currentQuestion.value.data,
          correctAnswer: currentQuestion.value.data?.correct_answer,
          correctIndex: currentQuestion.value.data?.correct_index,
          answer: currentQuestion.value.data?.answer,
          isCorrect: response.is_correct,
          explanation: response.explanation,
          questionId: currentQuestion.value.id
        })
      }

      lastResult.value = response
      showingResult.value = true // Показываем результат вместо вопроса

      // Логируем для диагностики
      if (import.meta.env.DEV) {
        console.log('Answer submitted successfully:', {
          is_correct: response.is_correct,
          finished: response.finished,
          smartscore: response.session?.current_smartscore || response.session?.smartscore,
          questions_answered: response.session?.questions_answered,
          explanation: response.explanation,
        })
      }

      // Плагин (PLUGIN): отправляем SERVER_RESULT в iframe
      if (qType === 'PLUGIN' && pluginIframeRef.value?.contentWindow) {
        try {
          pluginIframeRef.value.contentWindow.postMessage(
            {
              type: 'SERVER_RESULT',
              correct: response.is_correct,
              score: response.is_correct ? 1 : 0,
              explanation: response.explanation || '',
            },
            '*'
          )
        } catch (e) {
          console.warn('PracticeSession: postMessage SERVER_RESULT to plugin failed', e)
        }
      }

      // Синхронизируем время с сервером
      if (response.session?.time_elapsed_sec !== undefined) {
        currentTime.value = response.session.time_elapsed_sec
      }

      // SmartScore 100: завершаем сессию, показываем результат и кнопку «Нәтижелерге өту» (без авто-редиректа)
      const currentSmartScore = response.session?.current_smartscore || response.session?.smartscore || 0

      // Логируем для диагностики
      if (import.meta.env.DEV) {
        console.log('Checking SmartScore completion:', {
          currentSmartScore,
          finished: response.finished,
          is_correct: response.is_correct,
          questions_answered: response.session?.questions_answered,
        })
      }

      if (currentSmartScore >= 100 && !response.finished) {
        console.log('SmartScore reached 100, finishing session...')
        try {
          await practiceStore.finishSession(practiceStore.currentSession!.id)
        } catch (err) {
          console.error('Failed to finish session:', err)
        }
        stopTimer()
        lastResult.value = { ...response, finished: true }
        return
      }

      // Проверяем пробные вопросы после каждого ответа
      // Счетчик уже увеличен в practiceStore.submitAnswer для неавторизованных пользователей
      // Проверяем сразу после получения ответа, чтобы показать модальное окно, если лимит достигнут
      if (shouldCheckTrialQuestions.value) {
        // Проверяем текущее количество использованных вопросов
        const currentCount = trialQuestions.getTrialQuestionsCount()
        console.log('PracticeSession: Trial questions count after answer:', currentCount)

        // Если пробные вопросы исчерпаны, показываем модальное окно сразу
        if (trialQuestions.isTrialQuestionsExhausted.value || currentCount >= trialQuestions.TRIAL_QUESTIONS_LIMIT) {
          console.log('PracticeSession: Trial questions exhausted after answer, showing modal')
          showTrialEndedModal.value = true
          // Не загружаем следующий вопрос, если пробные вопросы исчерпаны
          return
        }
      }

      // Сессия завершена: останавливаем таймер, без авто-редиректа (кнопка «Нәтижелерге өту»)
      if (response.finished) {
        stopTimer()
        if (shouldCheckTrialQuestions.value && trialQuestions.isTrialQuestionsExhausted.value) {
          showTrialEndedModal.value = true
        }
      }
      // Правильный/неправильный — переход только по кнопке «Келесі», без авто-перехода
    }
  } catch (err: any) {
    console.error('PracticeSession: Failed to submit answer:', err)
    console.error('PracticeSession: Error details:', {
      status: err.response?.status,
      data: err.response?.data,
      message: err.message,
      isAuthenticated: authStore.isAuthenticated,
      userRole: authStore.user?.role,
      storeError: practiceStore.error,
    })

    // Используем сообщение об ошибке из store, если оно есть
    if (practiceStore.error) {
      error.value = practiceStore.error
    } else {
      // Обрабатываем ошибки напрямую
      const status = err.response?.status
      const errorData = err.response?.data

      if (status === 409) {
        // Конфликт - сессия уже завершена, вопрос изменен или уже отвечен
        console.log('Session conflict detected (409), refreshing session...', {
          errorMessage: errorData?.error?.message || errorData?.message,
          submittedQuestionId: requestData?.question_id,
        })

        try {
          // Обновляем состояние сессии
          if (practiceStore.currentSession?.id) {
            await practiceStore.getSession(practiceStore.currentSession.id)

            // Если сессия завершена, переходим на результаты
            if (practiceStore.currentSession?.finished_at) {
              console.log('Session is finished, redirecting to results')
              stopTimer()
              router.push({
                name: 'practice-results',
                params: { sessionId: practiceStore.currentSession.id }
              })
              return
            }

            // Проверяем, изменился ли текущий вопрос
            const currentQId = practiceStore.currentQuestion?.data?._generator_id
              || practiceStore.currentQuestion?.id
            const submittedQId = requestData?.question_id

            console.log('Question comparison after refresh:', {
              currentQId,
              submittedQId,
              currentQIdType: typeof currentQId,
              submittedQIdType: typeof submittedQId,
              match: String(currentQId) === String(submittedQId),
            })

            // Если вопрос изменился, значит он уже был отвечен или сессия продвинулась
            // Просто загружаем актуальный вопрос (не пытаемся повторно отправить)
            if (currentQId && submittedQId && String(currentQId) !== String(submittedQId)) {
              console.log('Question changed after refresh, loading new question instead of retrying')
              // Вопрос уже был отвечен или изменился - просто обновляем UI
              // Не показываем ошибку, просто продолжаем с новым вопросом
              submitting.value = false
              showingResult.value = false
              userAnswer.value = null
              return
            }

            // Если вопрос тот же, но все равно 409 - возможно, он уже был отвечен
            // Или сессия в неконсистентном состоянии
            // Пытаемся повторить отправку только если вопрос совпадает
            if (requestData && practiceStore.currentQuestion) {
              console.log('Retrying submit after session refresh...')

              // Для PLUGIN вопросов (не генераторов) используем last_question_id из сессии
              // чтобы избежать 409 ошибки
              let updatedQuestionId: string | number

              if (practiceStore.currentQuestion.data?._generator_id) {
                // Для генераторов используем _generator_id
                updatedQuestionId = String(practiceStore.currentQuestion.data._generator_id)
              } else if (practiceStore.currentQuestion.type === 'PLUGIN' && practiceStore.currentSession?.last_question_id) {
                // Для PLUGIN вопросов используем last_question_id из сессии
                const sessionLastQId = typeof practiceStore.currentSession.last_question_id === 'number'
                  ? practiceStore.currentSession.last_question_id
                  : Number(practiceStore.currentSession.last_question_id)

                if (!isNaN(sessionLastQId)) {
                  updatedQuestionId = sessionLastQId
                  console.log('Using session last_question_id for PLUGIN question:', updatedQuestionId)
                } else {
                  updatedQuestionId = typeof practiceStore.currentQuestion.id === 'number'
                    ? practiceStore.currentQuestion.id
                    : Number(practiceStore.currentQuestion.id)
                }
              } else {
                // Для обычных вопросов используем ID из currentQuestion
                updatedQuestionId = typeof practiceStore.currentQuestion.id === 'number'
                  ? practiceStore.currentQuestion.id
                  : Number(practiceStore.currentQuestion.id)
              }

              if (isNaN(updatedQuestionId as number) && !practiceStore.currentQuestion.data?._generator_id) {
                console.error('Invalid question ID after refresh')
                error.value = 'Сессия уақытша қате көрсетті. Бетті жаңартып, қайталап көріңіз.'
                submitting.value = false
                return
              }

              // Обновляем requestData с актуальным question_id
              const updatedRequestData = {
                ...requestData,
                question_id: updatedQuestionId
              }

              console.log('Retrying with updated question_id:', {
                updatedQuestionId,
                updatedQuestionIdType: typeof updatedQuestionId,
                originalQuestionId: requestData.question_id,
                sessionLastQuestionId: practiceStore.currentSession?.last_question_id,
              })

              try {
                // Повторяем отправку с обновленными данными (только один раз)
                const retryResponse = await practiceStore.submitAnswer(
                  practiceStore.currentSession.id,
                  updatedRequestData
                )

                if (retryResponse) {
                  // Успешно отправили после обновления
                  lastResult.value = retryResponse
                  showingResult.value = true
                  userAnswer.value = answer

                  // Безопасно копируем currentQuestion (может быть null)
                  if (practiceStore.currentQuestion) {
                    lastQuestion.value = { ...practiceStore.currentQuestion }
                  }

                  // Продолжаем обычную обработку ответа
                  if (retryResponse.session?.time_elapsed_sec !== undefined) {
                    currentTime.value = retryResponse.session.time_elapsed_sec
                  }

                  // Обрабатываем результат как обычно
                  if (retryResponse.finished) {
                    stopTimer()
                  }

                  submitting.value = false
                  return // Выходим из обработки ошибки
                }
              } catch (retryErr: any) {
                console.warn('Retry after 409 also failed:', retryErr)
                // Если повторная попытка тоже не удалась, не показываем ошибку
                // Просто обновляем UI и продолжаем с текущим вопросом
                submitting.value = false
                showingResult.value = false
                userAnswer.value = null
                // Не устанавливаем error.value, чтобы не пугать пользователя
                // Сессия уже обновлена, пользователь может продолжить
              }
            } else {
              // Вопрос не совпадает или отсутствует - просто обновляем UI
              console.log('Question mismatch or missing, updating UI without retry')
              submitting.value = false
              showingResult.value = false
              userAnswer.value = null
            }
          }
        } catch (refreshErr) {
          console.error('Failed to refresh session after 409:', refreshErr)
          const errorDetail = errorData?.error?.message || errorData?.message || 'Сессия бұрын аяқталған немесе өзгертілген болуы мүмкін'

          // Если сессия точно завершена, перенаправляем
          if (practiceStore.currentSession?.finished_at) {
            stopTimer()
            setTimeout(() => {
              if (practiceStore.currentSession?.id) {
                router.push({ name: 'practice-results', params: { sessionId: practiceStore.currentSession.id } })
              } else {
                router.push({ name: 'home' })
              }
            }, 2000)
          } else {
            // Если сессия не завершена, просто обновляем UI
            submitting.value = false
            showingResult.value = false
            userAnswer.value = null
            // Не показываем ошибку, чтобы не пугать пользователя
          }
        }
      } else if (status === 402) {
        // Ошибка 402 - Payment Required
        if (authStore.isAuthenticated) {
          const errorDetail = errorData?.detail || errorData?.message || 'Қол жеткізу құқығы жеткіліксіз'
          error.value = `Қол жеткізу қатесі: ${errorDetail}. Профильде жазылымды тексеріңіз немесе қайталап көріңіз.`
        } else if (shouldCheckTrialQuestions.value && trialQuestions.isTrialQuestionsExhausted.value) {
          showTrialEndedModal.value = true
          return // Не показываем ошибку, показываем модальное окно
        } else {
          error.value = 'Практиканы жалғастыру үшін жазылым қажет. Профильде жазылымды рәсімдеңіз.'
        }
      } else if (status === 401) {
        // Ошибка 401 - не авторизован
        if (shouldCheckTrialQuestions.value && trialQuestions.isTrialQuestionsExhausted.value) {
          showTrialEndedModal.value = true
          return // Не показываем ошибку, показываем модальное окно
        }
        error.value = 'Авторизация қажет. Жүйеге кіріңіз.'
      } else if (!err.response) {
        // Сетевые ошибки
        if (err.code === 'ECONNABORTED') {
          error.value = 'Күту уақыты асып кетті. Сервер жауап бермейді. Қайталап көріңіз.'
        } else {
          error.value = err.message || 'Желі қатесі. Интернет қосылымын және сервердің қолжетімділігін тексеріңіз.'
        }
      } else {
        // Другие ошибки
        const errorDetail = errorData?.detail || errorData?.message || err.message
        error.value = typeof errorDetail === 'string' ? errorDetail : 'Жауапты жіберу мүмкін болмады. Қайталап көріңіз.'
      }
    }

    // Обработка завершения сессии при ошибке 409
    if (err.response?.status === 409 && practiceStore.currentSession) {
      setTimeout(() => {
        router.push({
          name: 'practice-results',
          params: { sessionId: practiceStore.currentSession!.id },
        })
      }, 1000)
    }
  } finally {
    submitting.value = false
  }
}

// Загрузка следующего вопроса после нажатия "Далее"
const loadNextQuestion = async () => {
  if (!practiceStore.currentSession || loadingNext.value) return

  // Проверяем пробные вопросы перед загрузкой следующего вопроса
  if (shouldCheckTrialQuestions.value && trialQuestions.isTrialQuestionsExhausted.value) {
    console.log('PracticeSession: Trial questions exhausted, showing modal before loading next question')
    showTrialEndedModal.value = true
    return
  }

  loadingNext.value = true

  try {
    // Сохраняем информацию о следующем вопросе перед сбросом
    const hasNextQuestion = lastResult.value?.next_question !== null && lastResult.value?.next_question !== undefined

    // Сбрасываем состояние результата
    showingResult.value = false
    const savedResult = lastResult.value
    lastResult.value = null
    userAnswer.value = null
    lastQuestion.value = null
    error.value = null

    // Сбрасываем форму
    numericAnswer.value = null
    textAnswer.value = ''

    // Если есть следующий вопрос в ответе, он уже загружен в store через submitAnswer
    // Просто проверяем, что вопрос доступен
    if (hasNextQuestion && practiceStore.currentQuestion) {
      questionStartTime.value = Date.now()
    } else {
      // Загружаем следующий вопрос, если его нет
      await practiceStore.getNextQuestion(practiceStore.currentSession.id)
      questionStartTime.value = Date.now()
    }
  } catch (err: any) {
    console.error('Failed to load next question:', err)
    // В случае ошибки показываем результат снова
    showingResult.value = true
  } finally {
    loadingNext.value = false
  }
}

const finishSession = async () => {
  if (!practiceStore.currentSession) return
  try {
    await practiceStore.finishSession(practiceStore.currentSession.id)
    goToResults()
  } catch (err: any) {
    console.error('Failed to finish session:', err)
  }
}

const goToResults = () => {
  stopTimer()
  if (practiceStore.currentSession?.id) {
    router.push({
      name: 'practice-results',
      params: { sessionId: practiceStore.currentSession.id },
    })
  }
}

const requestPluginAnswer = () => {
  if (!pluginIframeRef.value?.contentWindow || !currentQuestion.value || currentQuestion.value.type !== 'PLUGIN') return
  if (submitting.value || showingResult.value) return
  error.value = null
  try {
    pluginIframeRef.value.contentWindow.postMessage({ type: 'REQUEST_ANSWER' }, '*')
  } catch (e) {
    console.warn('PracticeSession: postMessage REQUEST_ANSWER failed', e)
  }
}

// Флаг для предотвращения двойной отправки от плагина
const pluginSubmitInProgress = ref(false)

const pluginMessageHandler = (event: MessageEvent) => {
  try {
    const d = typeof event.data === 'string' ? JSON.parse(event.data) : event.data
    if (!d || !d.type) return
    const q = currentQuestion.value
    if (!q || q.type !== 'PLUGIN') return

    if (d.type === 'ANSWER_NOT_READY') {
      error.value = d.message || 'Тапсырманы толтырыңыз'
      return
    }
    if (d.type !== 'SUBMIT') return
    if (submitting.value || showingResult.value || pluginSubmitInProgress.value) return
    const userAnswer = d.userAnswer
    if (!userAnswer) return
    error.value = null
    pluginSubmitInProgress.value = true
    submitAnswer(userAnswer, 'PLUGIN').finally(() => {
      pluginSubmitInProgress.value = false
    })
  } catch {
    // ignore
  }
}

onMounted(async () => {
  window.addEventListener('message', pluginMessageHandler)
  try {
    const session = await practiceStore.getSession(props.sessionId)
    console.log('Session loaded:', session)
    console.log('Current question:', session?.current_question)
    console.log('Session smartscore:', session?.current_smartscore || session?.smartscore)
    console.log('Session time:', session?.time_elapsed_sec)
    console.log('Session questions answered:', session?.questions_answered)

    // Загружаем статистику навыка для отображения предыдущего результата
    if (session?.skill_id) {
      try {
        const skillStats = await catalogStore.getSkillStats(session.skill_id)
        if (skillStats && skillStats.best_smartscore) {
          previousBestScore.value = skillStats.best_smartscore
          console.log('Previous best score for skill:', skillStats.best_smartscore)
        }
      } catch (err) {
        console.warn('Failed to load skill stats:', err)
      }
    }

    // Восстанавливаем время сессии
    if (session?.time_elapsed_sec !== undefined) {
      currentTime.value = session.time_elapsed_sec
    }

    if (session && !session.current_question) {
      // Если нет текущего вопроса, запрашиваем следующий
      const nextQuestion = await practiceStore.getNextQuestion(props.sessionId)
      console.log('Next question received:', nextQuestion)
    }

    // Логируем текущий вопрос для отладки
    if (practiceStore.currentQuestion) {
      console.log('Current question in store:', {
        id: practiceStore.currentQuestion.id,
        type: practiceStore.currentQuestion.type,
        prompt: practiceStore.currentQuestion.prompt,
        data: practiceStore.currentQuestion.data,
      })
    }

    questionStartTime.value = Date.now()

    // Запускаем таймер
    startTimer()
  } catch (err: any) {
    console.error('Failed to load session:', err)
  }
})

onUnmounted(() => {
  window.removeEventListener('message', pluginMessageHandler)
  stopTimer()
})
</script>

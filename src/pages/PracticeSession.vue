<template>
  <div class="min-h-screen bg-gradient-to-b from-cyan-50 to-cyan-100">
    <Header />

    <!-- Breadcrumb -->
    <div class="bg-gray-100 border-b border-gray-200 py-2 px-4">
      <div class="container mx-auto">
        <nav class="flex items-center text-sm text-gray-600">
          <router-link to="/" class="hover:text-green-600">Басты бет</router-link>
          <span class="mx-2">›</span>
          <span v-if="skillInfo" class="text-gray-800">{{ skillInfo.gradeNumber }} сынып</span>
          <span class="mx-2">›</span>
          <span v-if="skillInfo" class="font-medium text-gray-900">{{ skillInfo.code }} {{ skillInfo.title }}</span>
        </nav>
      </div>
    </div>

    <main class="container mx-auto px-4 py-6">
      <!-- Loading -->
      <div v-if="practiceStore.loading && !practiceStore.currentSession" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
        <p class="mt-4 text-gray-600">Сессия жүктелуде...</p>
      </div>

      <!-- Error -->
      <div v-else-if="practiceStore.error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        <p>{{ practiceStore.error }}</p>
        <Button @click="router.push({ name: 'home' })" class="mt-4" variant="primary">
          Басты бетке
        </Button>
      </div>

      <!-- Main content -->
      <div v-else-if="practiceStore.currentSession && (currentQuestion || showingResult)">

        <!-- Trial warning -->
        <div v-if="shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value"
          class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
          <div class="flex items-center">
            <div class="shrink-0">
              <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-yellow-700">
                <strong>Сынақ кезеңі аяқталды.</strong> Практиканы жалғастыру үшін аккаунтқа кіріп, жазылымды
                рәсімдеңіз.
              </p>
            </div>
          </div>
        </div>

        <!-- Two-column layout -->
        <div class="flex flex-col lg:flex-row gap-6">

          <!-- Main question area -->
          <div class="flex-1 lg:w-3/4">
            <!-- Question card -->
            <div class="bg-white rounded-xl shadow-lg p-8 mb-6 relative"
              :class="{ 'opacity-75': shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value }">

              <!-- Overlay for trial exhausted -->
              <div v-if="shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value"
                class="absolute inset-0 bg-white bg-opacity-60 z-10 flex items-center justify-center rounded-xl">
                <div class="text-center p-4 bg-white bg-opacity-90 rounded-lg border-2 border-yellow-300">
                  <p class="text-lg font-semibold text-gray-700 mb-2">Жазылым қажет</p>
                  <p class="text-sm text-gray-600">Жалғастыру үшін аккаунтқа кіріңіз</p>
                </div>
              </div>

              <!-- Question display - always visible when there's a question -->
              <div v-if="currentQuestion">
                <!-- Question prompt (hide for plugins) -->
                <p v-if="currentQuestion.type !== 'PLUGIN'" class="text-xl text-gray-800 mb-8 leading-relaxed"
                  v-html="containsFraction(currentQuestion.prompt) ? formatFraction(currentQuestion.prompt) : currentQuestion.prompt">
                </p>

                <!-- MCQ -->
                <div v-if="currentQuestion.type === 'MCQ'" class="space-y-3">
                  <button
                    v-for="(option, index) in (currentQuestion.data?.choices || currentQuestion.data?.options || [])"
                    :key="index" @click="submitMCQAnswer(option, Number(index))"
                    :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
                    class="w-full text-left p-4 border-2 border-gray-200 rounded-xl hover:border-green-400 hover:bg-green-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                    <span v-html="formatMCQOption(option)"></span>
                  </button>
                </div>

                <!-- NUMERIC -->
                <div v-else-if="currentQuestion.type === 'NUMERIC'" class="space-y-4">
                  <div class="flex items-center gap-3">
                    <input v-model.number="numericAnswer" type="number" step="any" placeholder="Жауап"
                      class="w-40 p-3 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:outline-none text-lg"
                      @keyup.enter="submitAnswer(numericAnswer)"
                      :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)" />
                    <span v-if="currentQuestion.data?.unit" class="text-gray-600 text-lg">{{ currentQuestion.data.unit
                      }}</span>
                  </div>
                  <button @click="submitAnswer(numericAnswer)"
                    :disabled="submitting || numericAnswer === null || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
                    class="px-8 py-3 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                    {{ submitting ? 'Жіберілуде...' : 'Жіберу' }}
                  </button>
                </div>

                <!-- TEXT -->
                <div v-else-if="currentQuestion.type === 'TEXT'" class="space-y-4">
                  <input v-model="textAnswer" type="text" placeholder="Жауапты енгізіңіз"
                    class="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:outline-none text-lg"
                    @keyup.enter="submitAnswer(textAnswer)"
                    :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)" />
                  <button @click="submitAnswer(textAnswer)"
                    :disabled="submitting || !textAnswer || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
                    class="px-8 py-3 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                    {{ submitting ? 'Жіберілуде...' : 'Жіберу' }}
                  </button>
                </div>

                <!-- INTERACTIVE -->
                <div v-else-if="currentQuestion.type === 'INTERACTIVE'" class="space-y-4">
                  <InteractiveQuestion v-if="currentQuestion.data?.component_code"
                    :component-code="currentQuestion.data.component_code" :question-data="currentQuestion.data"
                    :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
                    @answer="handleInteractiveAnswer" />
                  <div v-else class="text-red-500 text-sm">
                    ⚠ Интерактивное задание не загружено.
                  </div>
                </div>

                <!-- PLUGIN -->
                <div v-else-if="currentQuestion.type === 'PLUGIN'" class="space-y-4">
                  <iframe v-if="isTsxPlugin && pluginIframeSrcdoc" ref="pluginIframeRef" :srcdoc="pluginIframeSrcdoc"
                    :style="{ width: '100%', height: `${pluginEmbedHeight}px`, border: 'none', borderRadius: '12px' }"
                    sandbox="allow-scripts allow-same-origin" class="rounded-xl" />
                  <iframe v-else-if="!isTsxPlugin && pluginIframeSrc" ref="pluginIframeRef" :src="pluginIframeSrc"
                    :style="{ width: '100%', height: `${pluginEmbedHeight}px`, border: 'none', borderRadius: '12px' }"
                    sandbox="allow-scripts allow-same-origin" class="rounded-xl" />
                  <div v-else class="text-red-500 text-sm">
                    ⚠ Плагин не загружен.
                  </div>
                  <button v-if="!isTsxPlugin && pluginIframeSrc" @click="requestPluginAnswer"
                    :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
                    class="px-8 py-3 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                    {{ submitting ? 'Жіберілуде...' : 'Жіберу' }}
                  </button>
                </div>

                <!-- Unknown type -->
                <div v-else class="space-y-4">
                  <input v-model="textAnswer" type="text" placeholder="Жауапты енгізіңіз"
                    class="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:outline-none"
                    @keyup.enter="submitAnswer(textAnswer)"
                    :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)" />
                  <button @click="submitAnswer(textAnswer)"
                    :disabled="submitting || !textAnswer || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
                    class="px-8 py-3 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                    {{ submitting ? 'Жіберілуде...' : 'Жіберу' }}
                  </button>
                </div>

                <!-- Finish button at bottom -->
                <div class="flex justify-end mt-8 pt-4 border-t border-gray-100">
                  <button @click="finishSession"
                    :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
                    class="text-gray-500 hover:text-gray-700 text-sm flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Сессияны аяқтау
                  </button>
                </div>
              </div>

              <!-- Result display - shows below question/iframe -->
              <div v-if="showingResult && lastResult" class="mt-6">
                <div :class="[
                  'rounded-xl p-6',
                  lastResult.is_correct
                    ? 'bg-green-50 border-2 border-green-300 text-green-800'
                    : 'bg-red-50 border-2 border-red-300 text-red-800',
                ]">
                  <p class="font-bold text-xl mb-4">
                    {{ lastResult.is_correct ? '✓ Дұрыс!' : '✗ Қате' }}
                  </p>

                  <!-- Answer comparison for wrong answer -->
                  <div v-if="!lastResult.is_correct" class="space-y-4 mt-4">
                    <template v-if="lastAnswerData && !lastQuestionData">
                      <div class="bg-green-50 border border-green-200 rounded-xl p-4">
                        <p class="font-semibold text-green-700 mb-3">✓ Дұрыс жауап:</p>
                        <p v-if="lastAnswerData.correctDisplay?.note" class="text-sm text-gray-600 mb-3 italic">
                          {{ lastAnswerData.correctDisplay.note }}
                        </p>
                        <AnswerVisualizer :data="{ type: lastAnswerData.type, ...lastAnswerData.correctDisplay }"
                          variant="correct" class="mb-3" />
                        <p class="text-green-700 font-medium">
                          {{ lastAnswerData.correctDisplay?.text || formatCorrectAnswer(lastQuestion, lastResult) }}
                        </p>
                      </div>

                      <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
                        <p class="font-semibold text-gray-700 mb-3">👤 Сіздің жауабыңыз:</p>
                        <AnswerVisualizer :data="{ type: lastAnswerData.type, ...lastAnswerData.userDisplay }"
                          variant="user" class="mb-3" />
                        <p class="text-gray-700 font-medium">
                          {{ lastAnswerData.userDisplay?.text || formatUserAnswer(userAnswer, lastQuestion) }}
                        </p>
                      </div>
                    </template>

                    <template v-else>
                      <div>
                        <p class="font-medium mb-1">Сіздің жауабыңыз:</p>
                        <p class="text-sm bg-white px-3 py-2 rounded border border-red-400"
                          v-html="formatUserAnswer(userAnswer, lastQuestion)"></p>
                      </div>
                      <div>
                        <p class="font-medium mb-1">Дұрыс жауап:</p>
                        <p class="text-sm bg-white px-3 py-2 rounded border border-green-400"
                          v-html="formatCorrectAnswer(lastQuestion, lastResult)"></p>
                      </div>
                    </template>
                  </div>

                  <p v-if="lastResult.explanation" class="text-sm mt-4 italic">{{ lastResult.explanation }}</p>
                </div>

                <!-- Action buttons -->
                <div class="flex gap-4 justify-center mt-6">
                  <Button v-if="!lastResult.finished" @click="loadNextQuestion" :disabled="loadingNext"
                    :loading="loadingNext"
                    class="px-8 py-3 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-lg">
                    Келесі
                  </Button>
                  <Button v-if="lastResult.finished" @click="goToResults" :disabled="loadingNext"
                    class="px-8 py-3 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-lg">
                    Нәтижелерге өту
                  </Button>
                  <Button v-if="!lastResult.finished" @click="finishSession" variant="outline" :disabled="loadingNext"
                    class="px-6 py-3">
                    Сессияны аяқтау
                  </Button>
                </div>
              </div>

            </div>
          </div>

          <!-- Right sidebar - Statistics -->
          <div class="lg:w-64 space-y-4">
            <!-- Questions answered -->
            <div class="rounded-xl overflow-hidden shadow-lg">
              <div class="bg-orange-500 text-white text-center py-2 px-4">
                <span class="text-sm font-medium">Жауап берілді</span>
              </div>
              <div class="bg-white text-center py-6">
                <span class="text-4xl font-bold text-gray-800">{{ practiceStore.questionsAnswered }}</span>
              </div>
            </div>

            <!-- Time elapsed -->
            <div class="rounded-xl overflow-hidden shadow-lg">
              <div class="bg-blue-500 text-white text-center py-2 px-4">
                <span class="text-sm font-medium">Уақыт</span>
              </div>
              <div class="bg-white text-center py-4">
                <div class="flex justify-center gap-1 text-gray-800">
                  <div class="text-center">
                    <div class="text-2xl font-bold font-mono">{{ formatTimeHours(currentTime) }}</div>
                    <div class="text-xs text-gray-500">САҒ</div>
                  </div>
                  <span class="text-2xl font-bold">:</span>
                  <div class="text-center">
                    <div class="text-2xl font-bold font-mono">{{ formatTimeMinutes(currentTime) }}</div>
                    <div class="text-xs text-gray-500">МИН</div>
                  </div>
                  <span class="text-2xl font-bold">:</span>
                  <div class="text-center">
                    <div class="text-2xl font-bold font-mono">{{ formatTimeSeconds(currentTime) }}</div>
                    <div class="text-xs text-gray-500">СЕК</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- SmartScore -->
            <div class="relative group" v-if="authStore.isAuthenticated">
              <!-- Tooltip - positioned above the container -->
              <div
                class="absolute bottom-full left-0 right-0 mb-2 w-72 p-3 bg-gray-800 text-white text-xs rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none"
                style="z-index: 9999;">
                <p class="mb-2"><strong>SmartScore</strong> — бұл пайызға негізделген баға емес, шеберлікке қарай
                  прогресті
                  динамикалық түрде өлшейді.</p>
                <p>Ол сіздің деңгейіңізді қиындау сұрақтарға жауап бергенде қадағалайды. Тамаша нәтижеге (90) жету үшін
                  сұрақтарға
                  дұрыс жауап беріңіз, ал шеберлікке (100) жету үшін Сынақ аймағын жеңіп шығыңыз!</p>
              </div>

              <div class="rounded-xl shadow-lg">
                <div
                  class="bg-green-500 text-white text-center py-2 px-4 flex items-center justify-center gap-2 rounded-t-xl">
                  <span class="text-sm font-medium">SmartScore</span>
                  <span class="text-xs bg-white/20 px-2 py-0.5 rounded">100-ден</span>
                  <svg class="w-4 h-4 cursor-help" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z"
                      clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="bg-white text-center py-6 rounded-b-xl">
                  <span class="text-5xl font-bold text-gray-800">{{ practiceStore.smartscore }}</span>
                </div>
              </div>
            </div>

            <!-- Correct/Wrong stats -->
            <div class="bg-white rounded-xl p-4 shadow-lg">
              <div class="flex justify-between items-center">
                <div class="text-center flex-1">
                  <div class="text-2xl font-bold text-green-600">{{ practiceStore.correctCount }}</div>
                  <div class="text-xs text-gray-500">Дұрыс</div>
                </div>
                <div class="w-px h-10 bg-gray-200"></div>
                <div class="text-center flex-1">
                  <div class="text-2xl font-bold text-red-500">{{ practiceStore.wrongCount }}</div>
                  <div class="text-xs text-gray-500">Қате</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No session found -->
      <div v-else class="text-center py-12 text-gray-600">
        <p>Сессия табылмады немесе аяқталды</p>
        <Button @click="router.push({ name: 'home' })" class="mt-4">Басты бетке</Button>
      </div>
    </main>

    <Footer />

    <!-- Trial ended modal -->
    <Modal :is-open="showTrialEndedModal" title="Сынақ кезеңі аяқталды" :show-close="false"
      @close="showTrialEndedModal = false">
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
/* eslint-disable @typescript-eslint/no-explicit-any */
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { usePracticeStore } from '@/stores/practice'
import { useAuthStore } from '@/stores/auth'
import { useTrialQuestions } from '@/composables/useTrialQuestions'
import { useCatalogStore } from '@/stores/catalog'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import Modal from '@/components/ui/Modal.vue'
import InteractiveQuestion from '@/components/practice/InteractiveQuestion.vue'
import AnswerVisualizer from '@/components/analytics/AnswerVisualizer.vue'
import type { PracticeSubmitResponse, QuestionPublic } from '@/types/api'
import { createTsxIframeHtml } from '@/utils/tsxTransformer'

interface Props {
  sessionId: string
}

const props = defineProps<Props>()
const router = useRouter()
const practiceStore = usePracticeStore()
const authStore = useAuthStore()

// Инициализируем trialQuestions сразу, чтобы он был доступен везде
const trialQuestions = useTrialQuestions()
const catalogStore = useCatalogStore()

// Статистика навыка для отображения предыдущего результата
const previousBestScore = ref<number | null>(null)

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Режим разработки - временно закомментировано
// const isDev = computed(() => import.meta.env.DEV)

const currentQuestion = computed(() => practiceStore.currentQuestion)

// Определяем, является ли плагин TSX файлом из miniapp-v2
const isTsxPlugin = computed(() => {
  const q = currentQuestion.value
  if (!q || q.type !== 'PLUGIN' || !q.data) return false

  // Проверяем наличие tsx_file или miniapp_file в данных вопроса
  if (q.data.tsx_file || q.data.miniapp_file) return true

  // Проверяем entry с расширением .tsx
  if (q.data.entry && q.data.entry.endsWith('.tsx')) return true

  // Проверяем по plugin_id - если содержит "kazakh-rectangle" или другие известные TSX плагины
  const pluginId = q.data.plugin_id || q.prompt || ''
  const knownTsxPlugins = ['kazakh-rectangle-area', 'kazakh-rectangle-area-app', 'fraction-comparison', 'fraction_comparison']
  if (knownTsxPlugins.some(name => pluginId.includes(name))) {
    return true
  }

  return false
})

// URL или путь к TSX файлу
const tsxFilePath = computed(() => {
  const q = currentQuestion.value
  if (!q || q.type !== 'PLUGIN' || !q.data) return null

  // Приоритет: tsx_file > miniapp_file > entry (если заканчивается на .tsx) > определение по plugin_id
  if (q.data.tsx_file) return q.data.tsx_file
  if (q.data.miniapp_file) return q.data.miniapp_file
  if (q.data.entry && q.data.entry.endsWith('.tsx')) {
    // Если entry - это путь к TSX файлу в miniapp-v2
    const fileName = q.data.entry.includes('/') ? q.data.entry.split('/').pop() : q.data.entry
    return `/miniapp-v2/exercieses/${fileName}`
  }

  // Определяем по plugin_id или prompt
  const pluginId = q.data.plugin_id || q.prompt || ''

  // Маппинг известных плагинов на файлы
  const pluginFileMap: Record<string, string> = {
    'kazakh-rectangle-area-app': 'kazakh_rectangle_area_app.tsx',
    'kazakh-rectangle-area-app-1': 'kazakh_rectangle_area_app.tsx',
    'kazakh-rectangle-area': 'kazakh_rectangle_area_app.tsx',
    'fraction-comparison': 'fraction_comparison_app.tsx',
    'fractioncomparisonapp': 'fraction_comparison_app.tsx',
  }

  // Ищем совпадение в plugin_id или prompt
  for (const [key, fileName] of Object.entries(pluginFileMap)) {
    if (pluginId.includes(key) || pluginId.toLowerCase().includes(key.toLowerCase())) {
      return `/miniapp-v2/exercieses/${fileName}`
    }
  }

  return null
})

// Содержимое iframe для TSX файлов (srcdoc)
const pluginIframeSrcdoc = ref<string>('')

// URL для обычных плагинов (src)
const pluginIframeSrc = computed(() => {
  const q = currentQuestion.value
  if (!q || q.type !== 'PLUGIN' || !q.data) return ''

  // Если это TSX файл, используем srcdoc вместо src
  if (isTsxPlugin.value) return ''

  const id = q.data.plugin_id
  const ver = q.data.plugin_version
  const entry = q.data.entry
  if (!id || !ver || !entry) return ''
  return `${API_BASE_URL}/static/plugins/${id}/${ver}/${entry}?embed=1`
})

// Загрузка TSX файла и создание iframe содержимого
const loadTsxPlugin = async () => {
  const filePath = tsxFilePath.value
  if (!filePath) {
    pluginIframeSrcdoc.value = ''
    return
  }

  try {
    // Пытаемся загрузить файл
    let tsxCode: string

    // Если путь начинается с /, это абсолютный путь от корня сайта
    if (filePath.startsWith('/')) {
      const response = await fetch(filePath)
      if (!response.ok) {
        throw new Error(`Failed to load TSX file (${response.status}): ${response.statusText}`)
      }
      tsxCode = await response.text()
    } else if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
      // Полный URL
      const response = await fetch(filePath)
      if (!response.ok) {
        throw new Error(`Failed to load TSX file (${response.status}): ${response.statusText}`)
      }
      tsxCode = await response.text()
    } else {
      // Относительный путь - пробуем от корня проекта
      const response = await fetch(`/${filePath}`)
      if (!response.ok) {
        throw new Error(`Failed to load TSX file (${response.status}): ${response.statusText}`)
      }
      tsxCode = await response.text()
    }

    // Трансформируем и создаем HTML для iframe
    pluginIframeSrcdoc.value = createTsxIframeHtml(tsxCode)
  } catch (err: Error | unknown) {
    console.error('Failed to load TSX plugin:', err)
    const errorMessage = err instanceof Error ? err.message : 'Unknown error'
    pluginIframeSrcdoc.value = `<html><body><p style="color:red;padding:20px">Ошибка загрузки упражнения: ${errorMessage}</p></body></html>`
  }
}

// Динамическая высота iframe от плагина
const dynamicPluginHeight = ref<number | null>(null)

// Отслеживаем изменения вопроса и загружаем TSX при необходимости
watch([currentQuestion, isTsxPlugin], async () => {
  // Сбрасываем динамическую высоту при смене вопроса
  dynamicPluginHeight.value = null

  if (isTsxPlugin.value && currentQuestion.value) {
    await loadTsxPlugin()
  } else {
    pluginIframeSrcdoc.value = ''
  }
}, { immediate: true })

const pluginEmbedHeight = computed(() => {
  // Если плагин сообщил свою высоту через postMessage, используем её
  if (dynamicPluginHeight.value && dynamicPluginHeight.value > 0) {
    return dynamicPluginHeight.value + 50 // +50 для padding
  }

  const q = currentQuestion.value
  // Дефолтная высота 900px, достаточная для большинства плагинов
  if (!q?.data?.height) return 900
  // Используем высоту из manifest или минимум 800, максимум 1400
  return Math.min(1400, Math.max(800, Number(q.data.height) || 900))
})

const submitting = ref(false)
const numericAnswer = ref<number | null>(null)
const textAnswer = ref('')
const lastResult = ref<PracticeSubmitResponse | null>(null)
const pluginIframeRef = ref<HTMLIFrameElement | null>(null)
const questionStartTime = ref(Date.now())
const showingResult = ref(false) // Показывать ли результат вместо вопроса
const userAnswer = ref<unknown>(null) // Сохраненный ответ пользователя
const lastQuestion = ref<QuestionPublic | null>(null) // Последний вопрос для отображения правильного ответа
const lastQuestionData = ref<any>(null) // Визуальные данные ВОПРОСА (числовая прямая, дробь и т.д.)
const lastAnswerData = ref<any>(null) // Визуальные данные ОТВЕТОВ (сетки, drag-drop и т.д.)
const lastSubmittedQuestionId = ref<string | number | null>(null)
const lastSubmittedAt = ref<number>(0)
const loadingNext = ref(false) // Загрузка следующего вопроса
const currentTime = ref(0) // Текущее время сессии в секундах
let timeInterval: number | null = null // Интервал для обновления времени
const error = ref<string | null>(null) // Ошибка для отображения

// Для всех авторизованных пользователей ограничения не применяются
// hasActiveSubscription используется для будущего функционала подписок
const _hasActiveSubscription = computed(() => authStore.isAuthenticated)
void _hasActiveSubscription.value // suppress unused warning

const isAuthenticated = computed(() => authStore.isAuthenticated)
// Для авторизованных пользователей пробные вопросы не применяются
const shouldCheckTrialQuestions = computed(() => !isAuthenticated.value)
const _remainingTrialQuestions = computed(() => trialQuestions.remainingTrialQuestions.value)
void _remainingTrialQuestions.value // suppress unused warning
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

// getZoneText - для будущего функционала зон
const _getZoneText = (zone: string) => {
  const zones: Record<string, string> = {
    LEARNING: 'Оқу',
    REFINING: 'Жетілдіру',
    CHALLENGE: 'Сынақ',
  }
  return zones[zone] || zone
}
void _getZoneText // suppress unused warning

// Форматирование времени в формат MM:SS или HH:MM:SS - для будущего использования
const _formatTime = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}
void _formatTime // suppress unused warning

// Форматирование компонентов времени для IXL-стиля отображения
const formatTimeHours = (seconds: number): string => {
  return Math.floor(seconds / 3600).toString().padStart(2, '0')
}

const formatTimeMinutes = (seconds: number): string => {
  return Math.floor((seconds % 3600) / 60).toString().padStart(2, '0')
}

const formatTimeSeconds = (seconds: number): string => {
  return (seconds % 60).toString().padStart(2, '0')
}

// Информация о навыке для хлебных крошек
const skillInfo = computed(() => {
  const session = practiceStore.currentSession
  if (!session) return null

  // Получаем информацию о навыке из store или данных сессии
  const skillId = session.skill_id
  const skill = catalogStore.skillDetails.get(skillId)

  if (skill) {
    return {
      gradeNumber: skill.grade_id || 6,
      code: skill.code || 'A.1',
      title: skill.title
    }
  }

  // Fallback: используем данные из сессии
  return {
    gradeNumber: (session as any).grade_number || 6,
    code: (session as any).skill_code || 'A.1',
    title: (session as any).skill_title || 'Тапсырма'
  }
})

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
    const answerAny = answer as any
    result = answerAny.userAnswer ?? answerAny.user_answer ?? answerAny.answer ?? answerAny.question ?? JSON.stringify(answer)
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
    return equalsMatch[1] ?? null
  }

  // Пытаемся найти число после знака равенства в любом месте
  const equalsAnywhere = explanation.match(/=\s*(\d+(?:\.\d+)?)/i)
  if (equalsAnywhere) {
    return equalsAnywhere[1] ?? null
  }

  // Пытаемся найти последнее число в строке (может быть ответом)
  const numbers = explanation.match(/\d+(?:\.\d+)?/g)
  if (numbers && numbers.length > 0) {
    // Берем последнее число как потенциальный ответ
    return numbers[numbers.length - 1] ?? null
  }

  return null
}

// Форматирование правильного ответа для отображения
const formatCorrectAnswer = (question: QuestionPublic | null, result: PracticeSubmitResponse | null): string => {

  // ДЛЯ ПЛАГИНОВ: сначала берем правильный ответ от плагина (приоритет!)
  const userAnswerAny = userAnswer.value as any
  if (
    userAnswerAny &&
    (question?.type === 'PLUGIN' || question?.type === 'INTERACTIVE')
  ) {
    const pluginCorrect =
      userAnswerAny.correctAnswer ??
      userAnswerAny.correct_answer ??
      userAnswerAny.expectedAnswer ??
      userAnswerAny.expected_answer
    if (pluginCorrect !== undefined && pluginCorrect !== null) {
      const answer = String(pluginCorrect)
      if (containsFraction(answer)) {
        return formatFraction(answer)
      }
      return answer
    }
  }

  // Проверяем результат ответа от сервера
  if (result) {
    const resultAny = result as any

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

    // Пытаемся извлечь из explanation (только если не плагин)
    if (result.explanation && question?.type !== 'PLUGIN' && question?.type !== 'INTERACTIVE') {
      const extracted = extractAnswerFromExplanation(result.explanation)
      if (extracted) {
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


  // Пытаемся получить правильный ответ из данных вопроса
  if (question.data?.correct_answer !== undefined && question.data.correct_answer !== null) {
    return String(question.data.correct_answer)
  }

  // Для MCQ пытаемся найти правильный вариант
  if (question.type === 'MCQ') {
    const choices = question.data?.choices || question.data?.options || []

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

  const now = Date.now()
  const currentQuestionId = currentQuestion.value.data?._generator_id ?? currentQuestion.value.id
  if (
    lastSubmittedQuestionId.value !== null &&
    currentQuestionId !== null &&
    String(lastSubmittedQuestionId.value) === String(currentQuestionId) &&
    now - lastSubmittedAt.value < 2000
  ) {
    return
  }

  submitting.value = true

  // Обновление сессии перед отправкой теперь происходит ниже, после создания requestData
  // Это позволяет избежать дублирования и правильно обновить questionId

  // Сохраняем ответ пользователя и текущий вопрос (если еще не сохранено)
  if (userAnswer.value === null) {
    userAnswer.value = answer
    lastQuestion.value = { ...currentQuestion.value }
    // Сохраняем данные для визуализации от плагина
    if (answer && typeof answer === 'object') {
      // questionData - визуал ВОПРОСА (числовая прямая, дробная полоска и т.д.)
      lastQuestionData.value = answer.questionData ?? null
      // answerData - визуал ОТВЕТОВ (сетки, drag-drop и т.д.)
      lastAnswerData.value = answer.answerData ?? null
    } else {
      lastQuestionData.value = null
      lastAnswerData.value = null
    }
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
      // Проверка выполняется, но результат не используется, т.к. мы продолжаем в любом случае
      choices.some((c: any) => {
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

      // Если выбор не найден, продолжаем - возможно это новый вариант

      submittedAnswer = { choice: choiceStr }

      // Логируем только важную информацию (можно отключить в production)
      if (import.meta.env.DEV) {
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
    if (!submittedAnswer || Object.keys(submittedAnswer).length === 0) {
      submittedAnswer = { answer: String(answer) }
    }

    // Определяем questionId: для генераторов используем _generator_id, для остальных - id
    let questionId: string | number
    const generatorId = currentQuestion.value.data?._generator_id
    if (generatorId) {
      questionId = String(generatorId)
    } else {
      const qId = currentQuestion.value.id
      questionId = typeof qId === 'number' ? qId : Number(qId)
      if (isNaN(questionId as number)) {
        error.value = 'Неверный ID вопроса. Обновите страницу.'
        submitting.value = false
        return
      }
    }

    requestData = {
      question_id: questionId,
      submitted_answer: submittedAnswer,
      time_spent_sec: timeSpent,
    }

    const response = await practiceStore.submitAnswer(practiceStore.currentSession.id, requestData)

    if (response) {
      lastSubmittedQuestionId.value = questionId
      lastSubmittedAt.value = Date.now()
      // Сохраняем результат и показываем его
      lastResult.value = response
      showingResult.value = true
      if (currentQuestion.value) {
        lastQuestion.value = { ...currentQuestion.value }
      }
      userAnswer.value = answer

      // Отправляем результат в iframe для PLUGIN
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

      // SmartScore 100: завершаем сессию
      const sessionAny = response.session as any
      const currentSmartScore = sessionAny?.current_smartscore || sessionAny?.smartscore || 0
      if (currentSmartScore >= 100 && !response.finished) {
        try {
          await practiceStore.finishSession(practiceStore.currentSession!.id)
        } catch (err) {
          console.error('Failed to finish session:', err)
        }
        stopTimer()
        lastResult.value = { ...response, finished: true }
        return
      }

      // Проверяем пробные вопросы
      if (shouldCheckTrialQuestions.value && trialQuestions.isTrialQuestionsExhausted.value) {
        showTrialEndedModal.value = true
        return
      }

      // Сессия завершена
      if (response.finished) {
        stopTimer()
        if (shouldCheckTrialQuestions.value && trialQuestions.isTrialQuestionsExhausted.value) {
          showTrialEndedModal.value = true
        }
      }
    }
  } catch (err: any) {
    const status = err.response?.status

    // 409 CONFLICT: сессия завершена - перенаправляем на результаты
    if (status === 409 && practiceStore.currentSession) {
      try {
        const refreshed = await practiceStore.getSession(practiceStore.currentSession.id)
        if (refreshed?.current_question) {
          showingResult.value = false
          lastResult.value = null
          userAnswer.value = null
          lastQuestion.value = null
          lastQuestionData.value = null
          lastAnswerData.value = null
          questionStartTime.value = Date.now()
          submitting.value = false
          return
        }
      } catch {
        // fallback to results below
      }
      stopTimer()
      router.push({
        name: 'practice-results',
        params: { sessionId: practiceStore.currentSession.id },
      })
      return
    }

    // Показываем ошибку из store или общую ошибку
    error.value = practiceStore.error || err.response?.data?.message || err.message || 'Жауапты жіберу мүмкін болмады.'
  } finally {
    submitting.value = false
  }
}

// Загрузка следующего вопроса после нажатия "Далее"
const loadNextQuestion = async () => {
  if (!practiceStore.currentSession || loadingNext.value) return

  if (shouldCheckTrialQuestions.value && trialQuestions.isTrialQuestionsExhausted.value) {
    showTrialEndedModal.value = true
    return
  }

  loadingNext.value = true

  try {
    // Сбрасываем состояние результата
    showingResult.value = false
    lastResult.value = null
    userAnswer.value = null
    lastQuestion.value = null
    lastQuestionData.value = null
    lastAnswerData.value = null
    error.value = null
    numericAnswer.value = null
    textAnswer.value = ''

    // Загружаем следующий вопрос
    // lastResult.value уже null, поэтому всегда загружаем следующий вопрос
    if (!practiceStore.currentQuestion) {
      await practiceStore.getNextQuestion(practiceStore.currentSession.id)
    }
    questionStartTime.value = Date.now()
  } catch (err: any) {
    const status = err.response?.status

    showingResult.value = true

    if (status === 409 && practiceStore.currentSession) {
      stopTimer()
      router.push({
        name: 'practice-results',
        params: { sessionId: practiceStore.currentSession.id }
      })
      return
    }

    error.value = err.response?.data?.message || err.message || 'Келесі сұрақты жүктеу мүмкін болмады.'
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

// Упрощенный обработчик сообщений как в miniapp-v2
const pluginMessageHandler = (event: MessageEvent) => {
  try {
    const d = typeof event.data === 'string' ? JSON.parse(event.data) : event.data
    if (!d) return

    // Обработка сообщений о высоте контента от плагина
    if (d.type === 'resize' || d.type === 'RESIZE' || d.type === 'content-height') {
      const height = d.height ?? d.contentHeight ?? d.scrollHeight
      if (typeof height === 'number' && height > 0) {
        dynamicPluginHeight.value = Math.max(height, 400) // Минимум 400px
      }
      return
    }

    if (d.type !== 'exercise-result') return

    const q = currentQuestion.value
    if (!q || q.type !== 'PLUGIN') return

    // Если плагин уже определил корректность, передаем это в backend
    const isCorrect = d.isCorrect ?? d.correct ?? d.is_correct
    const userAnswer = d.userAnswer ?? d.user_answer ?? d.studentAnswer ?? d.answer ?? d.value
    const correctAnswer = d.correctAnswer ?? d.correct_answer ?? d.expectedAnswer ?? d.expected_answer
    // Извлекаем текст вопроса от плагина (разные плагины могут использовать разные поля)
    const question = d.question ?? d.prompt ?? d.equation ?? d.problem ?? d.questionText ?? null
    // Данные для визуализации ВОПРОСА (если вопрос содержит картинку/график)
    const questionData = d.questionData ?? null
    // Данные для визуализации ОТВЕТОВ (если ответ визуальный - сетка, drag-drop и т.д.)
    const answerData = d.answerData ?? null

    error.value = null

    if (isCorrect !== undefined || correctAnswer !== undefined) {
      submitAnswer(
        {
          isCorrect,
          userAnswer,
          correctAnswer,
          question, // Сохраняем текст вопроса от плагина
          questionData, // Визуальные данные ВОПРОСА (для аналитики)
          answerData, // Визуальные данные ОТВЕТОВ
        },
        'PLUGIN'
      )
      return
    }

    if (userAnswer === null || userAnswer === undefined) return

    // Фолбэк: отправляем только ответ
    submitAnswer({ userAnswer, question, questionData, answerData }, 'PLUGIN')
  } catch (err) {
    console.error('Plugin message handler error:', err)
  }
}

onMounted(async () => {
  window.addEventListener('message', pluginMessageHandler)
  try {
    const session = await practiceStore.getSession(props.sessionId)

    // Загружаем статистику навыка для отображения предыдущего результата
    if (session?.skill_id) {
      try {
        const skillStats = await catalogStore.getSkillStats(session.skill_id)
        if (skillStats && skillStats.best_smartscore) {
          previousBestScore.value = skillStats.best_smartscore
        }
      } catch {
        // Игнорируем ошибку загрузки статистики
      }
    }

    // Восстанавливаем время сессии
    if (session?.time_elapsed_sec !== undefined) {
      currentTime.value = session.time_elapsed_sec
    }

    if (session && !session.current_question) {
      await practiceStore.getNextQuestion(props.sessionId)
    }

    questionStartTime.value = Date.now()
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

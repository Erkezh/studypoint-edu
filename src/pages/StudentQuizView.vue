<template>
  <div class="min-h-screen bg-gradient-to-b from-cyan-50 to-cyan-100 flex flex-col">
    <Header />

    <!-- Breadcrumb -->
    <div class="bg-gray-100 border-b border-gray-200 py-2 px-4 shrink-0 overflow-x-auto whitespace-nowrap scrollbar-hide">
      <div class="container mx-auto">
        <nav class="flex items-center text-xs sm:text-sm text-gray-600">
          <router-link to="/my-cabinet" class="hover:text-green-600 shrink-0">{{ isChildWithParent ? 'Менің кабинетім' : 'Менің IXL' }}</router-link>
          <span class="mx-2 text-gray-400 shrink-0">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </span>
          <span class="font-medium text-gray-900 truncate">{{ currentQuiz?.name || 'Викторина' }}</span>
        </nav>
      </div>
    </div>

    <main class="container mx-auto px-4 py-4 sm:py-6 flex-1 flex flex-col">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
        <p class="mt-4 text-gray-600">Викторина жүктелуде...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 p-6 rounded-xl text-center max-w-2xl mx-auto mt-8">
        <p class="text-lg font-medium">{{ error }}</p>
        <button @click="$router.push('/my-cabinet')" class="mt-4 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
          Артқа қайту
        </button>
      </div>

      <!-- Main content active state -->
      <div v-else-if="currentQuiz && !isFinished" class="flex flex-col lg:flex-row gap-6 w-full max-w-6xl mx-auto flex-1">
        
        <!-- Mobile stats bar -->
        <div class="mb-4 flex overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm lg:hidden shrink-0">
          <div class="border-r border-gray-200 flex-1 px-4 py-2 text-center">
            <div class="text-[11px] font-medium text-gray-500 uppercase">Жауап берілді</div>
            <div class="mt-1 text-xl font-bold text-orange-500">{{ currentIndex }}</div>
          </div>
          <div class="flex-1 px-4 py-2 text-center">
            <div class="text-[11px] font-medium text-gray-500 uppercase">Уақыт</div>
            <div class="mt-1 text-base font-bold font-mono text-blue-500">{{ formatTimeCompact(currentTime) }}</div>
          </div>
        </div>

        <!-- Left Column: Question Area -->
        <div class="flex-1 lg:w-3/4 flex flex-col">
          <div class="bg-white rounded-xl shadow-lg p-5 sm:p-8 relative flex-1 flex flex-col">
            
            <div v-if="currentQuestion" class="flex-1 flex flex-col justify-center">
              <!-- Question prompt (hidden for plugins since iframe shows it) -->
              <p v-if="!isCurrentQuestionPlugin" class="text-lg sm:text-2xl text-gray-800 mb-8 sm:mb-10 leading-relaxed font-medium"
                v-html="formatPrompt(currentQuestion.question?.prompt || '')">
              </p>

              <div class="w-full max-w-2xl">
                <!-- MCQ -->
                <div v-if="currentQuestion.question?.type === 'MCQ'" class="space-y-4">
                  <button
                    v-for="(option, index) in getOptions(currentQuestion.question?.data)"
                    :key="index"
                    @click="submitAnswer(option)"
                    class="w-full text-left p-4 sm:p-5 border-2 border-gray-200 rounded-xl hover:border-green-400 hover:bg-green-50 focus:border-green-500 focus:bg-green-50 transition-all text-base sm:text-lg"
                  >
                    <span v-html="formatPrompt(typeof option === 'object' && option !== null ? ((option as Record<string, unknown>).label || (option as Record<string, unknown>).text || (option as Record<string, unknown>).value || String(option)) as string : String(option))"></span>
                  </button>
                </div>

                <!-- NUMERIC -->
                <div v-else-if="currentQuestion.question?.type === 'NUMERIC'" class="space-y-6">
                  <div class="flex items-center gap-3">
                    <input v-model="textAnswer" type="number" step="any" placeholder="Жауап"
                      class="w-48 sm:w-64 p-4 border-2 border-gray-300 rounded-xl focus:border-green-500 focus:outline-none text-lg sm:text-xl"
                      @keyup.enter="submitAnswer(textAnswer)" />
                    <span v-if="currentQuestion.question?.data?.unit" class="text-gray-600 text-lg">{{ currentQuestion.question.data.unit }}</span>
                  </div>
                  <button @click="submitAnswer(textAnswer)"
                    :disabled="!textAnswer"
                    class="px-8 sm:px-12 py-3 sm:py-4 bg-green-500 hover:bg-green-600 text-white font-bold text-lg rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md hover:shadow-lg">
                    Жіберу
                  </button>
                </div>

                <!-- TEXT -->
                <div v-else-if="currentQuestion.question?.type === 'TEXT'" class="space-y-6">
                  <input v-model="textAnswer" type="text" placeholder="Жауапты енгізіңіз"
                    class="w-full p-4 border-2 border-gray-300 rounded-xl focus:border-green-500 focus:outline-none text-lg sm:text-xl"
                    @keyup.enter="submitAnswer(textAnswer)" />
                  <button @click="submitAnswer(textAnswer)"
                    :disabled="!textAnswer"
                    class="px-8 sm:px-12 py-3 sm:py-4 bg-green-500 hover:bg-green-600 text-white font-bold text-lg rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md hover:shadow-lg">
                    Жіберу
                  </button>
                </div>

                <!-- PLUGIN / INTERACTIVE -->
                <div v-else-if="isCurrentQuestionPlugin" class="space-y-4">
                  <iframe
                    v-if="pluginIframeSrc"
                    ref="pluginIframeRef"
                    :src="pluginIframeSrc"
                    :style="{ width: '100%', height: pluginHeight + 'px', border: 'none', borderRadius: '12px' }"
                    sandbox="allow-scripts allow-same-origin"
                    scrolling="no"
                    class="rounded-xl"
                  ></iframe>
                  <div v-else class="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-yellow-700 text-sm">
                    Плагин жүктелуде...
                  </div>
                </div>

                <!-- Other types (fallback) -->
                <div v-else class="space-y-6">
                  <p class="text-red-500 font-medium mb-4 flex items-center gap-2">
                     Бұл сұрақ түрі интерфейсте толық қолдау таппаған. Жауабыңызды төменге енгізіңіз.
                  </p>
                  <input v-model="textAnswer" type="text" placeholder="Мәтіндік жауап енгізіңіз"
                    class="w-full p-4 border-2 border-gray-300 rounded-xl focus:border-green-500 focus:outline-none text-lg sm:text-xl"
                    @keyup.enter="submitAnswer(textAnswer)" />
                  <button @click="submitAnswer(textAnswer)"
                    :disabled="!textAnswer"
                    class="px-8 sm:px-12 py-3 sm:py-4 bg-green-500 hover:bg-green-600 text-white font-bold text-lg rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md hover:shadow-lg">
                    Жіберу
                  </button>
                </div>
              </div>
            </div>

            <div v-else class="text-center py-12">
              <p>Сұрақ қолжетімсіз.</p>
            </div>
            
            <div class="mt-12 pt-6 border-t border-gray-100 flex justify-between items-center text-sm text-gray-500">
              <span>Сұрақ: {{ currentIndex + 1 }} / {{ sortedQuestions.length }}</span>
              <button @click="$router.push('/my-cabinet')" class="hover:text-gray-800 transition-colors">Алдын ала шығу</button>
            </div>
          </div>
        </div>

        <!-- Right Column: Stats (Desktop) -->
        <div class="hidden lg:flex lg:w-64 flex-col space-y-5">
          <!-- Жауап берілді -->
          <div class="rounded-xl overflow-hidden shadow-md">
            <div class="bg-orange-500 text-white text-center py-2 px-4 uppercase tracking-wider text-xs font-semibold">
              Жауап берілді
            </div>
            <div class="bg-white text-center py-8">
              <span class="text-5xl font-bold text-gray-800">{{ currentIndex }}</span>
            </div>
          </div>

          <!-- Уақыт -->
          <div class="rounded-xl overflow-hidden shadow-md">
            <div class="bg-blue-500 text-white text-center py-2 px-4 uppercase tracking-wider text-xs font-semibold">
              Уақыт
            </div>
            <div class="bg-white text-center py-6">
              <div class="flex justify-center gap-1 text-gray-800">
                <div class="text-center">
                  <div class="text-3xl font-bold font-mono">{{ formatTimeHours(currentTime) }}</div>
                  <div class="text-[10px] text-gray-400 font-bold uppercase mt-1">Сағ</div>
                </div>
                <span class="text-3xl font-bold text-gray-300 -mt-1">:</span>
                <div class="text-center">
                  <div class="text-3xl font-bold font-mono">{{ formatTimeMinutes(currentTime) }}</div>
                  <div class="text-[10px] text-gray-400 font-bold uppercase mt-1">Мин</div>
                </div>
                <span class="text-3xl font-bold text-gray-300 -mt-1">:</span>
                <div class="text-center">
                  <div class="text-3xl font-bold font-mono">{{ formatTimeSeconds(currentTime) }}</div>
                  <div class="text-[10px] text-gray-400 font-bold uppercase mt-1">Сек</div>
                </div>
              </div>
            </div>
          </div>

          <!-- SmartScore -->
          <div class="rounded-xl overflow-hidden shadow-md">
             <div class="bg-green-500 text-white text-center py-2 px-4 uppercase tracking-wider text-xs font-semibold">
              SmartScore
            </div>
            <div class="bg-white text-center py-8">
              <span class="text-5xl font-bold font-mono" :class="{'text-green-600': currentSmartScore > 0, 'text-gray-400': currentSmartScore === 0}">{{ currentSmartScore }}</span>
            </div>
          </div>
        </div>

      </div>

      <!-- Finished state -->
      <div v-else-if="isFinished" class="flex-1 flex flex-col items-center justify-center">
        <div class="bg-white p-8 sm:p-12 rounded-2xl shadow-xl text-center max-w-2xl w-full border border-gray-100 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-full h-3 bg-green-500"></div>
          
          <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg class="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          
          <h2 class="text-3xl font-bold text-gray-800 mb-4">Керемет жұмыс!</h2>
          <p class="text-gray-600 mb-8 text-lg">Сіз барлық сұрақтарды аяқтадыңыз.</p>
          
          <div class="grid grid-cols-2 gap-4 max-w-sm mx-auto mb-8">
             <div class="bg-gray-50 border border-gray-200 p-4 rounded-xl">
               <div class="text-sm text-gray-500 uppercase font-semibold mb-1">Сұрақтар</div>
               <div class="text-2xl font-bold text-gray-800">{{ sortedQuestions.length }}</div>
             </div>
             <div class="bg-gray-50 border border-gray-200 p-4 rounded-xl">
               <div class="text-sm text-gray-500 uppercase font-semibold mb-1">Уақыт</div>
               <div class="text-2xl font-bold text-gray-800 font-mono">{{ formatTimeCompact(currentTime) }}</div>
             </div>
          </div>

          <button @click="$router.push('/my-cabinet')" 
            class="px-8 py-3 bg-green-500 text-white rounded-xl font-bold text-lg hover:bg-green-600 transition-colors w-full sm:w-auto">
            Жалғастыру
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Header from '@/components/layout/Header.vue'
import { quizApi, type QuizResponse } from '@/api/quiz'

const authStore = useAuthStore()
const isChildWithParent = computed(() => authStore.user?.role === 'STUDENT' && !!(authStore.user as Record<string, unknown>)?.parent_id)

const props = defineProps<{
  quizId: string
}>()

// UI State
const loading = ref(true)
const error = ref<string | null>(null)
const currentQuiz = ref<QuizResponse | null>(null)

// Quiz State
const currentIndex = ref(0)
const isFinished = ref(false)
const textAnswer = ref('')

// Timer
const currentTime = ref(0)
let timeInterval: number | null = null

// Plugin state
const pluginIframeRef = ref<HTMLIFrameElement | null>(null)
const pluginIframeSrc = ref('')
const pluginHeight = ref(500)

const sortedQuestions = computed(() => {
  if (!currentQuiz.value?.questions) return []
  return [...currentQuiz.value.questions].sort((a, b) => a.position - b.position)
})

const currentQuestion = computed(() => {
  if (!sortedQuestions.value.length || currentIndex.value >= sortedQuestions.value.length) return null
  return sortedQuestions.value[currentIndex.value]
})

// Plugin detection helpers
const isQuestionPlugin = (q: Record<string, unknown> | null | undefined): boolean => {
  if (!q) return false
  const type = q.type as string | undefined
  return type === 'PLUGIN' || type === 'INTERACTIVE'
}

const getRegularPluginSrc = (q: Record<string, unknown> | null | undefined): string => {
  if (!q || !q.data) return ''
  const data = q.data as Record<string, unknown>
  const id = data.plugin_id as string | undefined
  const ver = data.plugin_version as string | undefined
  const entry = data.entry as string | undefined
  if (!id || !ver || !entry) return ''
  return `/static/modules/${id}/${ver}/${entry}?embed=1`
}

const isCurrentQuestionPlugin = computed(() => {
  if (!currentQuestion.value) return false
  return isQuestionPlugin(currentQuestion.value.question as Record<string, unknown> | undefined)
})

// Load plugin iframe when question changes
const loadCurrentPlugin = async () => {
  pluginIframeSrc.value = ''
  pluginHeight.value = 500
  if (!currentQuestion.value?.question) return
  const q = currentQuestion.value.question as Record<string, unknown>
  if (!isQuestionPlugin(q)) return

  pluginIframeSrc.value = getRegularPluginSrc(q)
}

// Listen for exercise-result messages from plugin iframes
const handlePluginMessage = (event: MessageEvent) => {
  try {
    const d = event.data
    if (!d || typeof d !== 'object') return

    // Handle iframe resize
    if (d.type === 'resize' || d.type === 'content-height') {
      const height = d.height ?? d.contentHeight ?? d.scrollHeight
      if (typeof height === 'number' && height > 0) {
        pluginHeight.value = Math.max(height, 400)
      }
      return
    }

    if (d.type !== 'exercise-result') return
    if (!isCurrentQuestionPlugin.value) return

    // The plugin submitted its result — move to the next question
    submitAnswer(d.userAnswer ?? d.studentAnswer ?? d.answer ?? 'plugin-answer')
  } catch (err) {
    console.error('Plugin message error:', err)
  }
}

// Watch question changes to reload plugin
watch(currentIndex, () => {
  if (isCurrentQuestionPlugin.value) {
    loadCurrentPlugin()
  }
})

const currentSmartScore = computed(() => {
  if (!sortedQuestions.value.length) return 0
  return Math.round((currentIndex.value / sortedQuestions.value.length) * 100)
})

const formatPrompt = (text: string): string => {
  if (!text) return ''
  return text.replace(
    /(\d+)\/(\d+)/g,
    '<span class="inline-flex flex-col items-center mx-0.5 align-middle"><span class="border-b-2 border-current pb-0.5 px-0.5 leading-none">$1</span><span class="pt-0.5 px-0.5 leading-none">$2</span></span>'
  )
}

const getOptions = (data: unknown) => {
  if (!data) return []
  const d = data as Record<string, unknown>
  return d.choices || d.options || []
}

const submitAnswer = (answer: string) => { // eslint-disable-line @typescript-eslint/no-unused-vars
  // Clear input
  textAnswer.value = ''

  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' })

  // Since there is no backend API to validate or score, we immediately proceed.
  if (currentIndex.value < sortedQuestions.value.length - 1) {
    currentIndex.value++
  } else {
    // Record completion in local storage
    currentIndex.value++ // bump to max
    isFinished.value = true
    stopTimer()
    
    try {
      localStorage.setItem(`quiz_result_${props.quizId}`, JSON.stringify({
        completedAt: new Date().toISOString(),
        score: 100
      }))
    } catch { }
  }
}

// Timer Functions
const startTimer = () => {
  stopTimer()
  timeInterval = setInterval(() => {
    currentTime.value++
  }, 1000) as unknown as number
}

const stopTimer = () => {
  if (timeInterval !== null) {
    clearInterval(timeInterval)
    timeInterval = null
  }
}

const formatTimeHours = (s: number) => Math.floor(s / 3600).toString().padStart(2, '0')
const formatTimeMinutes = (s: number) => Math.floor((s % 3600) / 60).toString().padStart(2, '0')
const formatTimeSeconds = (s: number) => (s % 60).toString().padStart(2, '0')
const formatTimeCompact = (s: number) => {
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60).toString().padStart(2, '0')
  const sec = (s % 60).toString().padStart(2, '0')
  return h > 0 ? `${h}:${m}:${sec}` : `${m}:${sec}`
}

const fetchQuiz = async () => {
  loading.value = true
  error.value = null
  
  try {
    const listResp = await quizApi.listStudentAssignedQuizzes()
    const quizzes = listResp.data.data || []
    
    const foundQuiz = quizzes.find(q => q.id === props.quizId)
    if (foundQuiz) {
      currentQuiz.value = foundQuiz
      
      const resultStr = localStorage.getItem(`quiz_result_${props.quizId}`)
      if (resultStr) {
        isFinished.value = true
        currentIndex.value = foundQuiz.questions.length
      } else {
        startTimer()
        // Load plugin iframe if the first question is a plugin
        await loadCurrentPlugin()
      }
    } else {
      error.value = 'Викторина табылмады немесе қолжетімсіз.'
    }
  } catch (err) {
    console.error('Quiz Error:', err)
    error.value = 'Викторинаны жүктеу кезінде қателік орын алды.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchQuiz()
  window.addEventListener('message', handlePluginMessage)
})

onUnmounted(() => {
  stopTimer()
  window.removeEventListener('message', handlePluginMessage)
})
</script>

<style scoped>
/* Focus & hover improvements */
button {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.scrollbar-hide::-webkit-scrollbar {
    display: none;
}
.scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
}
</style>

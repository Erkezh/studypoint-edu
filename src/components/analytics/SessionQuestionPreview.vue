<template>
  <div class="session-question-preview">
    <!-- Header: Prompt -->
    <div class="mb-4">
      <div v-if="!isPlugin" class="text-lg text-gray-800 mb-4 leading-relaxed font-medium"
        v-html="formatContent(question.prompt)">
      </div>
    </div>

    <!-- Question Content -->
    <div class="mb-6">
      <!-- MCQ -->
      <div v-if="isMCQ" class="space-y-2">
        <div
          v-for="(option, index) in (question.data?.choices || question.data?.options || [])"
          :key="index"
          class="p-3 border rounded-lg transition-colors flex items-center justify-between"
          :class="getMCQClass(option, index)"
        >
          <span v-html="formatMCQOption(option)"></span>
        </div>
      </div>

      <!-- NUMERIC -->
      <div v-else-if="isNumeric" class="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div class="flex items-center gap-3">
          <span v-if="question.data?.unit" class="text-gray-600">{{ question.data.unit }}</span>
        </div>
      </div>

      <!-- TEXT -->
      <div v-else-if="isText" class="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <!-- Text question preview only -->
      </div>

      <!-- PLUGIN / INTERACTIVE -->
      <div v-if="isPlugin" class="space-y-4">
        <!-- Iframe container -->
        <div class="relative w-full overflow-hidden rounded-xl border border-gray-200 bg-white min-h-[200px]">
             <!-- Loading Overlay -->
             <div v-if="iframeLoading" class="absolute inset-0 flex items-center justify-center bg-white/95 z-10 min-h-[200px]">
                <div class="text-center">
                  <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-100 border-t-cyan-500 mb-2"></div>
                  <p class="text-sm font-semibold text-gray-500">Жүктелуде...</p>
                </div>
              </div>

              <iframe
                v-if="pluginIframeSrc"
                ref="iframeRef"
                :src="pluginIframeSrc"
                class="w-full border-0 select-none"
                :style="{ height: `${iframeHeight}px`, overflow: 'hidden', pointerEvents: 'none' }"
                sandbox="allow-scripts"
                scrolling="no"
                @load="onIframeLoad"
              ></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'

const props = defineProps<{
  question: {
    prompt: string
    type: string
    data: {
      choices?: unknown[]
      options?: unknown[]
      unit?: string
      entry?: string
      plugin_id?: string
      [key: string]: unknown
    } | null
    userAnswer: unknown
    isCorrect: boolean
    correctAnswer: unknown
    seed?: number | string | null
  }
}>()

const qType = computed(() => String(props.question.type || '').toUpperCase())
const isPlugin = computed(() => qType.value === 'PLUGIN' || qType.value === 'INTERACTIVE')
const isMCQ = computed(() => qType.value === 'MCQ')
const isNumeric = computed(() => qType.value === 'NUMERIC')
const isText = computed(() => qType.value === 'TEXT')

const iframeRef = ref<HTMLIFrameElement | null>(null)
const pluginIframeSrc = ref('')
const iframeLoading = ref(true)

const getDefaultHeight = () => {
  const data = props.question.data
  if (data && typeof data.height === 'number') {
    return Math.min(1400, Math.max(450, data.height))
  }
  if (data && typeof data.height === 'string') {
    const val = parseInt(data.height, 10)
    if (!isNaN(val)) return Math.min(1400, Math.max(450, val))
  }
  return 650
}

const iframeHeight = ref(getDefaultHeight())

const setIframeHeight = (height: unknown) => {
  if (height === null || height === undefined) return
  let parsedHeight = 0
  if (typeof height === 'number') {
    parsedHeight = height
  } else if (typeof height === 'string') {
    parsedHeight = parseFloat(height)
  }
  if (isNaN(parsedHeight) || parsedHeight <= 0) return
  iframeHeight.value = Math.max(450, Math.min(Math.ceil(parsedHeight) + 32, 3000))
}

const measureIframeContent = () => {
  // Staggered measurements to handle dynamic rendering / load latency
  const timeouts = [100, 300, 800, 1500]
  timeouts.forEach(delay => {
    window.setTimeout(() => {
      try {
        const doc = iframeRef.value?.contentDocument
        if (!doc) return
        const body = doc.body
        const html = doc.documentElement
        setIframeHeight(Math.max(
          body?.scrollHeight || 0,
          body?.offsetHeight || 0,
          html?.scrollHeight || 0,
          html?.offsetHeight || 0,
        ))
      } catch {
        // Cross-origin or sandbox restrictions
      }
    }, delay)
  })
}

// Helpers for formatted display
const formatContent = (text: string) => {
  return text.replace(
    /(\d+)\/(\d+)/g,
    '<span class="inline-flex flex-col items-center mx-0.5 align-middle"><span class="border-b border-gray-600 pb-0.5 leading-none text-sm">$1</span><span class="leading-none text-sm">$2</span></span>'
  )
}

const formatMCQOption = (option: unknown) => {
  if (typeof option === 'object' && option !== null) {
    const optObj = option as Record<string, unknown>
    return optObj.label || optObj.value || ''
  }
  return formatContent(String(option))
}

const isSelected = (option: unknown, index: number | string) => {
  const optObj = typeof option === 'object' && option !== null ? (option as Record<string, unknown>) : null
  const val = optObj ? optObj.value : option
  return props.question.userAnswer === index || props.question.userAnswer == val
}

const getMCQClass = (option: unknown, index: number | string) => {
  if (isSelected(option, index)) {
    return 'bg-blue-50 border-blue-300'
  }
  return 'bg-white border-gray-200 opacity-60' // Dim non-selected options
}

// Plugin Logic (simplified from PracticeSession)
const loadPlugin = async () => {
  pluginIframeSrc.value = ''
  iframeLoading.value = true
  iframeHeight.value = getDefaultHeight()

  if (!isPlugin.value) return

  const qData = props.question.data
  if (!qData) return

  // Ordinary plugin (HTML/JS)
  const id = qData.plugin_id as string | undefined
  const ver = qData.plugin_version as string | undefined
  const entry = qData.entry as string | undefined
  if (!id || !ver || !entry) return

  const hasUserAnswer = props.question.userAnswer !== null && props.question.userAnswer !== undefined

  if (!hasUserAnswer) {
    // Question-only preview: load in quiz+frozen mode to just show the question
    const params = new URLSearchParams({
      embed: '1',
      mode: 'quiz',
      frozen: '1',
      questionData: qData ? JSON.stringify(qData) : '',
      seed: props.question.seed ? String(props.question.seed) : ''
    })
    pluginIframeSrc.value = `/static/modules/${id}/${ver}/${entry}?${params.toString()}`
    return
  }

  // Review mode: show student answer + correct answer
  const rawUserAns = normalizePayload(props.question.userAnswer) as Record<string, unknown> | null
  
  const isWrapper = rawUserAns && typeof rawUserAns === 'object' && !Array.isArray(rawUserAns) && (
    'studentAnswer' in rawUserAns ||
    'student_answer' in rawUserAns ||
    'userAnswer' in rawUserAns ||
    'user_answer' in rawUserAns ||
    'correctAnswer' in rawUserAns ||
    'correct_answer' in rawUserAns ||
    'expectedAnswer' in rawUserAns ||
    'expected_answer' in rawUserAns ||
    'answerData' in rawUserAns ||
    'questionData' in rawUserAns
  )

  const questionData = isWrapper ? (rawUserAns.questionData || rawUserAns.visualData) : props.question.data
  const answerData = isWrapper ? rawUserAns.answerData : null

  const reviewData = {
    mode: 'review',
    studentAnswer: isWrapper
      ? (rawUserAns.studentAnswer ?? rawUserAns.student_answer ?? rawUserAns.userAnswer ?? rawUserAns.user_answer ?? rawUserAns.answer ?? rawUserAns.value)
      : props.question.userAnswer,
    correctAnswer: isWrapper
      ? (rawUserAns.correctAnswer ?? rawUserAns.correct_answer ?? rawUserAns.expectedAnswer ?? rawUserAns.expected_answer ?? props.question.correctAnswer)
      : props.question.correctAnswer,
    isCorrect: props.question.isCorrect,
    questionData,
    answerData
  }

  const params = new URLSearchParams({
    embed: '1',
    mode: 'review',
    frozen: '1',
    studentAnswer: typeof reviewData.studentAnswer === 'object' ? JSON.stringify(reviewData.studentAnswer) : String(reviewData.studentAnswer || ''),
    correctAnswer: typeof reviewData.correctAnswer === 'object' ? JSON.stringify(reviewData.correctAnswer) : String(reviewData.correctAnswer || ''),
    isCorrect: String(reviewData.isCorrect || false),
    questionData: questionData ? JSON.stringify(questionData) : '',
    answerData: answerData ? JSON.stringify(answerData) : '',
    seed: props.question.seed ? String(props.question.seed) : ''
  })
  pluginIframeSrc.value = `/static/modules/${id}/${ver}/${entry}?${params.toString()}`
}

const normalizePayload = (payload: unknown): unknown => {
  if (typeof payload !== 'string') return payload
  const trimmed = payload.trim()
  if (!trimmed.startsWith('{') && !trimmed.startsWith('[')) return payload
  try {
    return JSON.parse(trimmed)
  } catch {
    return payload
  }
}

const handleIframeMessage = (event: MessageEvent) => {
  if (!iframeRef.value?.contentWindow || event.source !== iframeRef.value.contentWindow) return
  const data = typeof event.data === 'string' ? normalizePayload(event.data) : event.data
  if (!data || typeof data !== 'object') return

  const payload = data as Record<string, unknown>
  if (payload.type === 'resize' || payload.type === 'RESIZE' || payload.type === 'content-height') {
    setIframeHeight(payload.height ?? payload.contentHeight ?? payload.scrollHeight)
  }
}

const onIframeLoad = () => {
    iframeLoading.value = false
    measureIframeContent()
    // Optional: Send message to iframe as a fallback mechanism
    try {
      iframeRef.value?.contentWindow?.postMessage({
        type: 'SERVER_RESULT',
        correct: props.question.isCorrect,
        score: props.question.isCorrect ? 1 : 0,
        studentAnswer: props.question.userAnswer,
        correctAnswer: props.question.correctAnswer,
        isCorrect: props.question.isCorrect,
        mode: 'review'
      }, '*')
      iframeRef.value?.contentWindow?.postMessage({
        type: 'SHOW_ANSWER',
        value: true
      }, '*')
      measureIframeContent()
    } catch (err) {
      console.warn('Failed postMessage to iframe in review mode:', err)
    }
}

onMounted(() => {
  window.addEventListener('message', handleIframeMessage)
  loadPlugin()
})

onUnmounted(() => {
  window.removeEventListener('message', handleIframeMessage)
})

watch(() => props.question, () => {
  loadPlugin()
}, { deep: true })
</script>

<style scoped>
iframe {
  overflow: hidden;
  scrollbar-width: none;
}
iframe::-webkit-scrollbar {
  display: none;
}
</style>

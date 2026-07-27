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
        <div class="relative w-full rounded-xl border border-gray-200 bg-white min-h-[300px]">
             <!-- Loading Overlay -->
             <div v-if="iframeLoading" class="absolute inset-0 flex items-center justify-center bg-white/95 z-10 min-h-[300px]">
                <div class="text-center">
                  <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-100 border-t-cyan-500 mb-2"></div>
                  <p class="text-sm font-semibold text-gray-500">Жүктелуде...</p>
                </div>
              </div>

              <iframe
                v-if="pluginIframeSrc"
                ref="iframeRef"
                :src="pluginIframeSrc"
                class="w-full border-0 select-none rounded-xl"
                :style="{ height: `${iframeHeight}px`, pointerEvents: 'none' }"
                sandbox="allow-scripts"
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
    level?: number | string | null
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
  let baseHeight = 750
  if (data && typeof data.height === 'number') {
    baseHeight = data.height
  } else if (data && typeof data.height === 'string') {
    const val = parseInt(data.height, 10)
    if (!isNaN(val)) baseHeight = val
  }
  const hasUserAns = props.question.userAnswer !== null && props.question.userAnswer !== undefined
  if (hasUserAns) {
    baseHeight = Math.max(baseHeight, 850)
  }
  return Math.min(1800, Math.max(550, baseHeight))
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
  iframeHeight.value = Math.max(650, Math.min(Math.ceil(parsedHeight) + 100, 3000))
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

// Helpers to safely extract student answer and correct answer from wrapper or direct value
const extractAns = (raw: Record<string, unknown> | null, fallback: unknown) => {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return fallback
  const val = raw.studentAnswer ?? raw.student_answer ?? raw.userAnswer ?? raw.user_answer ?? raw.answer ?? raw.value ?? raw.choice ?? raw.text
  if (val !== undefined && val !== null) return val
  return fallback
}

const extractCorrectAns = (raw: Record<string, unknown> | null, fallback: unknown) => {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return fallback
  const val = raw.correctAnswer ?? raw.correct_answer ?? raw.expectedAnswer ?? raw.expected_answer
  if (val !== undefined && val !== null) return val
  return fallback
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
  const level = props.question.level ?? (qData?.level as string | number | undefined) ?? 1

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
    'questionData' in rawUserAns ||
    'visualData' in rawUserAns
  )

  const extractedQData = isWrapper ? (rawUserAns.questionData || rawUserAns.visualData) : null
  const mergedQData = extractedQData && typeof extractedQData === 'object'
    ? { ...(qData || {}), ...(extractedQData as Record<string, unknown>) }
    : (qData || {})

  const getSeed = (): string => {
    if (props.question.seed !== null && props.question.seed !== undefined && props.question.seed !== '') {
      return String(props.question.seed)
    }
    if (mergedQData && mergedQData.seed !== null && mergedQData.seed !== undefined && mergedQData.seed !== '') {
      return String(mergedQData.seed)
    }
    if (rawUserAns && typeof rawUserAns === 'object' && rawUserAns.seed !== null && rawUserAns.seed !== undefined && rawUserAns.seed !== '') {
      return String(rawUserAns.seed)
    }
    // Fallback deterministic seed from prompt string or qData to guarantee matching seed between question and answer previews
    const str = props.question.prompt || (qData ? JSON.stringify(qData) : '') || 'default-seed'
    let hash = 0
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i)
      hash |= 0
    }
    return String(Math.abs(hash) || 12345)
  }

  const effectiveSeed = getSeed()

  if (!hasUserAnswer) {
    // Question-only preview: load in quiz+frozen mode to just show the question
    const params = new URLSearchParams({
      embed: '1',
      mode: 'quiz',
      frozen: '1',
      questionData: mergedQData ? JSON.stringify(mergedQData) : '',
      seed: effectiveSeed,
      level: String(level)
    })
    pluginIframeSrc.value = `/static/modules/${id}/${ver}/${entry}?${params.toString()}`
    return
  }

  // Review mode: show student answer + correct answer
  const answerData = isWrapper ? rawUserAns.answerData : null
  const extractedStudentAns = isWrapper ? extractAns(rawUserAns, props.question.userAnswer) : props.question.userAnswer
  const extractedCorrectAns = isWrapper ? extractCorrectAns(rawUserAns, props.question.correctAnswer) : props.question.correctAnswer

  const reviewData = {
    mode: 'review',
    studentAnswer: extractedStudentAns,
    correctAnswer: extractedCorrectAns,
    isCorrect: props.question.isCorrect,
    questionData: mergedQData,
    answerData
  }

  const params = new URLSearchParams({
    embed: '1',
    mode: 'review',
    frozen: '1',
    studentAnswer: typeof reviewData.studentAnswer === 'object' ? JSON.stringify(reviewData.studentAnswer) : String(reviewData.studentAnswer ?? ''),
    userAnswer: typeof reviewData.studentAnswer === 'object' ? JSON.stringify(reviewData.studentAnswer) : String(reviewData.studentAnswer ?? ''),
    correctAnswer: typeof reviewData.correctAnswer === 'object' ? JSON.stringify(reviewData.correctAnswer) : String(reviewData.correctAnswer ?? ''),
    isCorrect: String(reviewData.isCorrect || false),
    questionData: mergedQData ? JSON.stringify(mergedQData) : '',
    answerData: answerData ? JSON.stringify(answerData) : '',
    seed: effectiveSeed,
    level: String(level)
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
    try {
      const rawUserAns = normalizePayload(props.question.userAnswer) as Record<string, unknown> | null
      const studentAns = extractAns(rawUserAns, props.question.userAnswer)
      const correctAns = extractCorrectAns(rawUserAns, props.question.correctAnswer)

      iframeRef.value?.contentWindow?.postMessage({
        type: 'SERVER_RESULT',
        correct: props.question.isCorrect,
        score: props.question.isCorrect ? 1 : 0,
        studentAnswer: studentAns,
        userAnswer: studentAns,
        correctAnswer: correctAns,
        isCorrect: props.question.isCorrect,
        mode: 'review'
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

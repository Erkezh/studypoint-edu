<template>
  <div class="session-question-preview">
    <!-- Header: Prompt -->
    <div class="mb-4">
      <div v-if="question.type !== 'PLUGIN'" class="text-lg text-gray-800 mb-4 leading-relaxed font-medium"
        v-html="formatContent(question.prompt)">
      </div>
    </div>

    <!-- Question Content -->
    <div class="mb-6">
      <!-- MCQ -->
      <div v-if="question.type === 'MCQ'" class="space-y-2">
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
      <div v-else-if="question.type === 'NUMERIC'" class="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div class="flex items-center gap-3">
          <span v-if="question.data?.unit" class="text-gray-600">{{ question.data.unit }}</span>
        </div>
      </div>

      <!-- TEXT -->
      <div v-else-if="question.type === 'TEXT'" class="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <!-- Text question preview only -->
      </div>

      <!-- PLUGIN / INTERACTIVE -->
      <div v-if="question.type === 'PLUGIN' || question.type === 'INTERACTIVE'" class="space-y-4">
        <!-- Iframe container -->
        <div class="relative w-full overflow-hidden rounded-xl border border-gray-200 bg-white">
             <iframe
                v-if="pluginIframeSrc"
                ref="iframeRef"
                :src="pluginIframeSrc"
                class="w-full border-0"
                :style="{ height: `${iframeHeight}px`, overflow: 'hidden' }"
                sandbox="allow-scripts allow-same-origin"
                scrolling="no"
                @load="onIframeLoad"
              ></iframe>
               <div v-else class="flex items-center justify-center h-64 bg-gray-50 text-gray-500">
                <div class="text-center">
                  <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-400 mb-2"></div>
                  <p class="text-sm">Жүктелуде...</p>
                </div>
              </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'

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
  }
}>()

const iframeRef = ref<HTMLIFrameElement | null>(null)
const pluginIframeSrc = ref('')
const iframeHeight = ref(420)

const setIframeHeight = (height: unknown) => {
  if (typeof height !== 'number' || !Number.isFinite(height) || height <= 0) return
  iframeHeight.value = Math.max(420, Math.min(Math.ceil(height) + 24, 3000))
}

const measureIframeContent = () => {
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
      // Cross-origin or sandbox restrictions: rely on postMessage resize events.
    }
  }, 100)
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
  iframeHeight.value = 420

  if (props.question.type !== 'PLUGIN' && props.question.type !== 'INTERACTIVE') return

  const qData = props.question.data
  if (!qData) return

  // Common review data structure injected into plugins
  const rawUserAns = normalizePayload(props.question.userAnswer) as Record<string, unknown> | null
  const questionData = (rawUserAns && typeof rawUserAns === 'object') ? rawUserAns.questionData : null
  const answerData = (rawUserAns && typeof rawUserAns === 'object') ? rawUserAns.answerData : null

  const reviewData = {
    mode: 'review',
    studentAnswer: (rawUserAns && typeof rawUserAns === 'object')
      ? (rawUserAns.studentAnswer ?? rawUserAns.student_answer ?? rawUserAns.userAnswer ?? rawUserAns.user_answer ?? rawUserAns.answer ?? rawUserAns.value)
      : props.question.userAnswer,
    correctAnswer: (rawUserAns && typeof rawUserAns === 'object')
      ? (rawUserAns.correctAnswer ?? rawUserAns.correct_answer ?? rawUserAns.expectedAnswer ?? rawUserAns.expected_answer ?? props.question.correctAnswer)
      : props.question.correctAnswer,
    isCorrect: props.question.isCorrect,
    questionData,
    answerData
  }

  // Ordinary plugin (HTML/JS)
  const id = qData.plugin_id as string | undefined
  const ver = qData.plugin_version as string | undefined
  const entry = qData.entry as string | undefined
  if (id && ver && entry) {
    const params = new URLSearchParams({
      embed: '1',
      mode: 'review',
      studentAnswer: typeof reviewData.studentAnswer === 'object' ? JSON.stringify(reviewData.studentAnswer) : String(reviewData.studentAnswer || ''),
      correctAnswer: typeof reviewData.correctAnswer === 'object' ? JSON.stringify(reviewData.correctAnswer) : String(reviewData.correctAnswer || ''),
      isCorrect: String(reviewData.isCorrect || false),
      questionData: questionData ? JSON.stringify(questionData) : '',
      answerData: answerData ? JSON.stringify(answerData) : ''
    })
    pluginIframeSrc.value = `/static/modules/${id}/${ver}/${entry}?${params.toString()}`
  }
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
/* Add any specific styles here */
</style>

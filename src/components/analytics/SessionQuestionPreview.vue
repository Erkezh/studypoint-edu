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
      <div v-else-if="question.type === 'PLUGIN' || question.type === 'INTERACTIVE'" class="space-y-4">
        <!-- Iframe container -->
        <div class="relative w-full overflow-hidden rounded-xl border border-gray-200 bg-white">
             <iframe
                v-if="pluginIframeSrcdoc"
                ref="iframeRef"
                :srcdoc="pluginIframeSrcdoc"
                class="w-full border-0"
                :style="{ height: '400px' }"
                sandbox="allow-scripts allow-same-origin"
                @load="onIframeLoad"
              ></iframe>
             <iframe
                v-else-if="pluginIframeSrc"
                ref="iframeRef"
                :src="pluginIframeSrc"
                class="w-full border-0"
                :style="{ height: '400px' }"
                sandbox="allow-scripts allow-same-origin"
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
import { ref, onMounted, watch } from 'vue'
import { createTsxIframeHtml } from '@/utils/tsxTransformer'

const props = defineProps<{
  question: {
    prompt: string
    type: string
    data: {
      choices?: unknown[]
      options?: unknown[]
      unit?: string
      tsx_file?: string
      miniapp_file?: string
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
const pluginIframeSrcdoc = ref('')
const pluginIframeSrc = ref('')

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
  pluginIframeSrcdoc.value = ''
  pluginIframeSrc.value = ''

  if (props.question.type !== 'PLUGIN' && props.question.type !== 'INTERACTIVE') return

  const qData = props.question.data
  if (!qData) return

  // Determine if it is a TSX plugin
  let isTsx = false
  let tsxPath = ''

  if (qData.tsx_file) {
    tsxPath = qData.tsx_file as string
    isTsx = true
  } else if (qData.miniapp_file) {
    tsxPath = qData.miniapp_file as string
    isTsx = true
  } else if (qData.entry && String(qData.entry).endsWith('.tsx')) {
     const fileName = String(qData.entry).split('/').pop()
     tsxPath = `/miniapp-v2/exercieses/${fileName}`
     isTsx = true
  } else {
     const pluginId = (qData.plugin_id || props.question.prompt || '') as string
     if (pluginId.includes('kazakh-rectangle')) {
       tsxPath = '/miniapp-v2/exercieses/kazakh_rectangle_area_app.tsx'
       isTsx = true
     } else if (pluginId.includes('fraction')) {
       tsxPath = '/miniapp-v2/exercieses/fraction_comparison_app.tsx'
       isTsx = true
     }
  }

  // Common review data structure injected into plugins
  const rawUserAns = props.question.userAnswer as Record<string, any> | null
  const questionData = (rawUserAns && typeof rawUserAns === 'object') ? rawUserAns.questionData : null
  const answerData = (rawUserAns && typeof rawUserAns === 'object') ? rawUserAns.answerData : null

  const reviewData = {
    mode: 'review',
    studentAnswer: (rawUserAns && typeof rawUserAns === 'object') ? (rawUserAns.studentAnswer ?? rawUserAns.userAnswer) : props.question.userAnswer,
    correctAnswer: (rawUserAns && typeof rawUserAns === 'object') ? rawUserAns.correctAnswer : props.question.correctAnswer,
    isCorrect: props.question.isCorrect,
    questionData,
    answerData
  }

  if (isTsx && tsxPath) {
    try {
      const response = await fetch(tsxPath.startsWith('/') ? tsxPath : `/${tsxPath}`)
      if (!response.ok) throw new Error('Failed to load plugin code')
      const code = await response.text()
      pluginIframeSrcdoc.value = createTsxIframeHtml(code, reviewData)
    } catch (e) {
      console.error('Preview load error:', e)
      pluginIframeSrcdoc.value = '<body>Error loading preview</body>'
    }
  } else {
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
}

const onIframeLoad = () => {
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
    } catch (err) {
      console.warn('Failed postMessage to iframe in review mode:', err)
    }
}

onMounted(() => {
  loadPlugin()
})

watch(() => props.question, () => {
  loadPlugin()
}, { deep: true })

</script>

<style scoped>
/* Add any specific styles here */
</style>

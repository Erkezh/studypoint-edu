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
import { ref, computed, onMounted, watch } from 'vue'
import { createTsxIframeHtml } from '@/utils/tsxTransformer'
// We might need to import API_BASE_URL if we support non-tsx plugins later,
// but for now let's focus on TSX as they seem to be the primary target for "interactive"
// import { API_BASE_URL } from '@/config/api'

const props = defineProps<{
  question: {
    prompt: string
    type: string
    data: any
    userAnswer: any
    isCorrect: boolean
    correctAnswer: any
  }
}>()

const iframeRef = ref<HTMLIFrameElement | null>(null)
const pluginIframeSrcdoc = ref('')

// Helpers for formatted display
const formatContent = (text: string) => {
  return text.replace(
    /(\d+)\/(\d+)/g,
    '<span class="inline-flex flex-col items-center mx-0.5 align-middle"><span class="border-b border-gray-600 pb-0.5 leading-none text-sm">$1</span><span class="leading-none text-sm">$2</span></span>'
  )
}

const formatMCQOption = (option: any) => {
  if (typeof option === 'object') return option.label || option.value
  return formatContent(String(option))
}

const isSelected = (option: any, index: number) => {
  // Simple comparison, might need refinement based on exact data structure
  const val = typeof option === 'object' ? option.value : option
  // Check against userAnswer index or value
  return props.question.userAnswer === index || props.question.userAnswer == val
}

const getMCQClass = (option: any, index: number) => {
  if (isSelected(option, index)) {
    return 'bg-blue-50 border-blue-300'
  }
  return 'bg-white border-gray-200 opacity-60' // Dim non-selected options
}

const formatUserAnswer = (answer: any) => {
  if (typeof answer === 'object' && answer !== null) {
    return JSON.stringify(answer)
  }
  return String(answer)
}

// Plugin Logic (simplified from PracticeSession)
const loadPlugin = async () => {
  if (props.question.type !== 'PLUGIN') return

  const qData = props.question.data
  // Determine TSX path
  let tsxPath = ''

  if (qData.tsx_file) tsxPath = qData.tsx_file
  else if (qData.miniapp_file) tsxPath = qData.miniapp_file
  else if (qData.entry && qData.entry.endsWith('.tsx')) {
     const fileName = qData.entry.split('/').pop()
     tsxPath = `/miniapp-v2/exercieses/${fileName}`
  }
  // Try to guess from ID if path missing (fallback)
   else {
      const pluginId = qData.plugin_id || props.question.prompt || ''
      if (pluginId.includes('kazakh-rectangle')) tsxPath = '/miniapp-v2/exercieses/kazakh_rectangle_area_app.tsx'
      else if (pluginId.includes('fraction')) tsxPath = '/miniapp-v2/exercieses/fraction_comparison_app.tsx'
  }

  if (!tsxPath) return

  try {
    const response = await fetch(tsxPath)
    if (!response.ok) throw new Error('Failed to load plugin code')
    const code = await response.text()
    pluginIframeSrcdoc.value = createTsxIframeHtml(code)
  } catch (e) {
    console.error('Preview load error:', e)
    pluginIframeSrcdoc.value = '<body>Error loading preview</body>'
  }
}

const onIframeLoad = () => {
    // Optional: Send message to iframe to set "read-only" state if plugin supports it
    // iframeRef.value?.contentWindow?.postMessage({ type: 'set-read-only', value: true }, '*')
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

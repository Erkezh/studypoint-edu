<template>
  <div class="interactive-question">
    <!-- Используем iframe для безопасного выполнения React кода -->
    <iframe
      v-if="iframeSrcdoc"
      ref="questionFrame"
      :srcdoc="iframeSrcdoc"
      class="w-full border-0 min-h-[600px] rounded-lg"
      sandbox="allow-scripts allow-same-origin allow-forms"
      @load="onIframeLoad"
    ></iframe>
    <div v-else class="text-center py-8 text-gray-500">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      <p class="mt-4">Интерактивное задание загружается...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { createTsxIframeHtml } from '@/utils/tsxTransformer'

interface Props {
  componentCode: string
  questionData?: Record<string, any>
  disabled?: boolean
}

interface Emits {
  (e: 'answer', answer: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const questionFrame = ref<HTMLIFrameElement | null>(null)
const iframeSrcdoc = ref<string>('')

// Создаем HTML страницу с React компонентом используя утилиту трансформации
const createIframeContent = () => {
  // createTsxIframeHtml принимает только tsxCode, трансформирует его и создает полный HTML
  return createTsxIframeHtml(props.componentCode)
}

// Слушаем сообщения от iframe
const handleMessage = (event: MessageEvent) => {
  // Поддерживаем оба формата: старый (interactive-question-answer) и новый (exercise-result)
  if (event.data?.type === 'interactive-question-answer') {
    emit('answer', event.data.answer)
  } else if (event.data?.type === 'exercise-result') {
    // Формат из miniapp-v2: { type: 'exercise-result', studentAnswer, correctAnswer, isCorrect }
    // Если есть isCorrect/correctAnswer, передаем объект целиком для backend
    const isCorrect = event.data?.isCorrect ?? event.data?.correct ?? event.data?.is_correct
    const correctAnswer = event.data?.correctAnswer ?? event.data?.correct_answer
    if (isCorrect !== undefined || correctAnswer !== undefined) {
      emit('answer', {
        isCorrect,
        userAnswer: event.data?.userAnswer ?? event.data?.studentAnswer ?? event.data?.answer,
        correctAnswer,
      })
    } else {
      emit('answer', event.data.studentAnswer || event.data)
    }
  }
}

const onIframeLoad = () => {
  // После загрузки iframe можно выполнить дополнительные действия
  if (questionFrame.value?.contentWindow) {
    // Можно установить связь с iframe
  }
}

onMounted(() => {
  iframeSrcdoc.value = createIframeContent()
  window.addEventListener('message', handleMessage)
})

watch(() => props.componentCode, () => {
  iframeSrcdoc.value = createIframeContent()
})

onUnmounted(() => {
  window.removeEventListener('message', handleMessage)
})
</script>

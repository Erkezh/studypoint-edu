<template>
  <Transition
    enter-active-class="transition ease-out duration-300"
    enter-from-class="opacity-0 transform translate-y-2"
    enter-to-class="opacity-100 transform translate-y-0"
    leave-active-class="transition ease-in duration-200"
    leave-from-class="opacity-100 transform translate-y-0"
    leave-to-class="opacity-0 transform translate-y-2"
  >
    <div
      v-if="visible"
      :class="[
        'fixed bottom-4 right-4 p-4 rounded-lg shadow-lg max-w-md z-50',
        {
          'bg-green-100 text-green-800 border border-green-300': type === 'success',
          'bg-red-100 text-red-800 border border-red-300': type === 'error',
          'bg-yellow-100 text-yellow-800 border border-yellow-300': type === 'warning',
          'bg-blue-100 text-blue-800 border border-blue-300': type === 'info',
        },
      ]"
    >
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <p class="font-medium">{{ title }}</p>
          <p v-if="message" class="mt-1 text-sm">{{ message }}</p>
        </div>
        <button
          @click="close"
          class="ml-4 text-gray-500 hover:text-gray-700"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

interface Props {
  visible: boolean
  type?: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'info',
  duration: 5000,
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  close: []
}>()

const visible = ref(props.visible)

watch(
  () => props.visible,
  (newVal) => {
    visible.value = newVal
  }
)

let timeoutId: number | null = null

onMounted(() => {
  if (props.duration > 0) {
    timeoutId = window.setTimeout(() => {
      close()
    }, props.duration)
  }
})

const close = () => {
  visible.value = false
  emit('update:visible', false)
  emit('close')
  if (timeoutId) {
    clearTimeout(timeoutId)
    timeoutId = null
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="fixed inset-0 z-40 flex items-center justify-center p-4 transition-all" :class="backdropClass" @click.self="showClose && close()">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6 relative z-50" :class="customClass">
          <div class="flex justify-between items-start mb-4">
            <h3 class="text-xl font-semibold">{{ title }}</h3>
            <button
              v-if="showClose"
              @click="close"
              class="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-gray-100"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="mb-6">
            <p v-if="message" class="text-gray-700">{{ message }}</p>
            <slot name="content"></slot>
          </div>
          
          <div class="flex gap-3 justify-end">
            <slot name="actions">
              <Button v-if="showClose" @click="close" variant="outline">Закрыть</Button>
            </slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { onBeforeUnmount, watch } from 'vue'
import Button from './Button.vue'

interface Props {
  isOpen: boolean
  title?: string
  message?: string
  showClose?: boolean
  customClass?: string
  backdropClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  message: '',
  showClose: true,
  customClass: '',
  backdropClass: 'bg-black/20 backdrop-blur-[2px]'
})

const emit = defineEmits<{
  close: []
}>()

const close = () => {
  emit('close')
}

let removeKeydownListener: (() => void) | null = null

const cleanupKeydownListener = () => {
  if (removeKeydownListener) {
    removeKeydownListener()
    removeKeydownListener = null
  }
}

// Закрытие по Escape
watch(() => props.isOpen, (isOpen) => {
  cleanupKeydownListener()

  if (isOpen) {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && props.showClose) {
        close()
      }
    }
    document.addEventListener('keydown', handleEscape)
    removeKeydownListener = () => {
      document.removeEventListener('keydown', handleEscape)
    }
  }
})

onBeforeUnmount(() => {
  cleanupKeydownListener()
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .bg-white,
.modal-leave-active .bg-white {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from .bg-white,
.modal-leave-to .bg-white {
  transform: scale(0.9);
  opacity: 0;
}
</style>

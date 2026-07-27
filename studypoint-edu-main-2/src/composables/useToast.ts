import { ref } from 'vue'

export interface ToastMessage {
  id: number
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
}

const toasts = ref<ToastMessage[]>([])
let nextId = 0

export const useToast = () => {
  const show = (
    type: ToastMessage['type'],
    title: string,
    message?: string,
    duration = 5000
  ) => {
    const id = nextId++
    toasts.value.push({ id, type, title, message, duration })

    if (duration > 0) {
      setTimeout(() => {
        remove(id)
      }, duration)
    }

    return id
  }

  const remove = (id: number) => {
    const index = toasts.value.findIndex((t) => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  const success = (title: string, message?: string, duration?: number) => {
    return show('success', title, message, duration)
  }

  const error = (title: string, message?: string, duration?: number) => {
    return show('error', title, message, duration)
  }

  const warning = (title: string, message?: string, duration?: number) => {
    return show('warning', title, message, duration)
  }

  const info = (title: string, message?: string, duration?: number) => {
    return show('info', title, message, duration)
  }

  return {
    toasts,
    show,
    remove,
    success,
    error,
    warning,
    info,
  }
}

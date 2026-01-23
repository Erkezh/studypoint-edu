<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8 max-w-6xl">
      <div class="mb-6">
        <h1 class="text-3xl font-bold mb-2">Плагины для интерактивных заданий</h1>
        <p class="text-gray-600">Загружайте ZIP-архивы с плагинами для создания интерактивных заданий</p>
      </div>

      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {{ error }}
      </div>

      <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
        {{ successMessage }}
      </div>

      <!-- Загрузка плагина -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Загрузить новый плагин</h2>
        
        <div class="mb-4 p-4 bg-blue-50 border border-blue-200 rounded">
          <p class="text-sm text-blue-800 mb-2"><strong>Требования к плагину:</strong></p>
          <ul class="text-sm text-blue-700 list-disc list-inside space-y-1">
            <li>ZIP архив с файлами плагина</li>
            <li>В корне архива должен быть <code class="bg-blue-100 px-1 rounded">manifest.json</code></li>
            <li>Entry файл (обычно <code class="bg-blue-100 px-1 rounded">index.html</code>) должен существовать</li>
            <li>Максимальный размер: 10MB</li>
          </ul>
        </div>

        <form @submit.prevent="handleUpload" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              ZIP файл плагина
            </label>
            <input
              ref="fileInput"
              type="file"
              accept=".zip"
              @change="handleFileSelect"
              class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
            />
            <p v-if="selectedFile" class="text-sm text-gray-600 mt-2">
              Выбран файл: {{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
            </p>
          </div>

          <div class="flex gap-4">
            <Button type="submit" variant="primary" :loading="uploading">
              Загрузить плагин
            </Button>
            <Button type="button" variant="outline" @click="resetUpload">
              Очистить
            </Button>
          </div>
        </form>
      </div>

      <!-- Список плагинов -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold mb-4">Загруженные плагины</h2>
        
        <div v-if="loading" class="text-center py-8">
          <p class="text-gray-500">Загрузка...</p>
        </div>

        <div v-else-if="plugins.length === 0" class="text-center py-8">
          <p class="text-gray-500">Плагины не загружены</p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="plugin in plugins"
            :key="plugin.id"
            class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-800">{{ plugin.name }}</h3>
                <div class="mt-2 space-y-1 text-sm text-gray-600">
                  <p><strong>ID:</strong> {{ plugin.plugin_id }}</p>
                  <p><strong>Версия:</strong> {{ plugin.version }}</p>
                  <p><strong>Entry:</strong> {{ plugin.entry }}</p>
                  <p><strong>API Version:</strong> {{ plugin.api_version }}</p>
                  <p><strong>Высота:</strong> {{ plugin.height }}px</p>
                  <p><strong>Статус:</strong> 
                    <span :class="plugin.is_published ? 'text-green-600' : 'text-gray-500'">
                      {{ plugin.is_published ? 'Опубликован' : 'Не опубликован' }}
                    </span>
                  </p>
                  <p><strong>Загружен:</strong> {{ formatDate(plugin.created_at) }}</p>
                </div>
              </div>
              
              <div class="flex flex-col gap-2 ml-4">
                <Button
                  v-if="!plugin.is_published"
                  variant="primary"
                  size="sm"
                  @click="publishPlugin(plugin.id, true)"
                  :loading="publishing === plugin.id"
                >
                  Опубликовать
                </Button>
                <Button
                  v-else
                  variant="outline"
                  size="sm"
                  @click="publishPlugin(plugin.id, false)"
                  :loading="publishing === plugin.id"
                >
                  Скрыть
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  @click="previewPlugin(plugin)"
                >
                  Preview
                </Button>
                <Button
                  v-if="!plugin.is_published"
                  variant="danger"
                  size="sm"
                  @click="deletePlugin(plugin.id)"
                  :loading="deleting === plugin.id"
                >
                  Удалить
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Preview Modal -->
      <div
        v-if="previewPluginData"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="closePreview"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
          <div class="p-4 border-b flex items-center justify-between">
            <h3 class="text-lg font-semibold">Preview: {{ previewPluginData.name }}</h3>
            <button
              @click="closePreview"
              class="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>
          
          <div class="flex-1 overflow-auto p-4">
            <!-- Лог postMessage событий -->
            <div class="mb-4 p-3 bg-gray-50 rounded border">
              <h4 class="font-semibold mb-2">PostMessage Events:</h4>
              <div class="space-y-1 max-h-32 overflow-y-auto">
                <div
                  v-for="(event, idx) in messageLog"
                  :key="idx"
                  class="text-xs font-mono p-2 bg-white rounded border"
                >
                  <span class="font-semibold">{{ event.type }}:</span>
                  <pre class="mt-1 text-xs">{{ JSON.stringify(event.data, null, 2) }}</pre>
                </div>
                <div v-if="messageLog.length === 0" class="text-gray-500 text-sm">
                  Нет событий
                </div>
              </div>
            </div>

            <!-- Iframe с плагином -->
            <iframe
              :src="pluginUrl"
              :style="{ width: '100%', height: `${previewPluginData.height}px`, border: '1px solid #e5e7eb' }"
              sandbox="allow-scripts allow-same-origin"
              class="rounded"
              @load="handleIframeLoad"
            ></iframe>
          </div>
        </div>
      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { adminApi } from '@/api/admin'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'

const router = useRouter()

const authStore = useAuthStore()
const loading = ref(false)
const uploading = ref(false)
const publishing = ref<string | null>(null)
const deleting = ref<string | null>(null)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const plugins = ref<Array<Record<string, any>>>([])
const previewPluginData = ref<Record<string, any> | null>(null)
const messageLog = ref<Array<{ type: string; data: any }>>([])
const messageHandler = ref<((event: MessageEvent) => void) | null>(null)

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString('ru-RU')
}

const handleUpload = async () => {
  if (!selectedFile.value) {
    error.value = 'Выберите файл для загрузки'
    return
  }

  uploading.value = true
  error.value = null
  successMessage.value = null

  try {
    const response = await adminApi.uploadPlugin(selectedFile.value)
    successMessage.value = `Плагин "${response.data.name}" успешно загружен!`
    resetUpload()
    await loadPlugins()
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err: any) {
    console.error('Upload error:', err)
    const errorDetail = err.response?.data?.error || err.response?.data
    let errorMsg = err.message
    
    if (errorDetail) {
      if (typeof errorDetail === 'string') {
        errorMsg = errorDetail
      } else if (errorDetail.message) {
        errorMsg = errorDetail.message
      } else if (errorDetail.code === 'plugin_exists') {
        errorMsg = `Плагин уже существует. Если он не опубликован, он будет заменен. Если опубликован - сначала скройте его.`
      }
    }
    
    // Обработка 409 Conflict
    if (err.response?.status === 409) {
      errorMsg = errorDetail?.message || 'Плагин с таким ID и версией уже существует. Если он опубликован, сначала скройте его.'
    }
    
    error.value = errorMsg || 'Ошибка при загрузке плагина'
  } finally {
    uploading.value = false
  }
}

const resetUpload = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const loadPlugins = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await adminApi.listPlugins()
    plugins.value = response.data || []
  } catch (err: any) {
    console.error('Load plugins error:', err)
    
    // Обработка ошибок авторизации
    if (err.response?.status === 401) {
      const errorDetail = err.response.data?.error || err.response.data?.detail
      if (errorDetail?.message) {
        error.value = `Ошибка авторизации: ${errorDetail.message}. Пожалуйста, войдите снова.`
      } else {
        error.value = 'Ошибка авторизации. Токен истек или недействителен. Пожалуйста, войдите снова.'
      }
      
      // Предлагаем перелогиниться
      setTimeout(() => {
        if (confirm('Токен истек. Перейти на страницу входа?')) {
          router.push({ name: 'login', query: { redirect: '/admin/plugins' } })
        }
      }, 2000)
    } else if (err.response?.status === 403) {
      error.value = 'У вас нет прав для доступа к этой странице. Требуется роль ADMIN.'
    } else {
      const errorMsg = err.response?.data?.message || err.response?.data?.error?.message || err.message
      error.value = errorMsg || 'Ошибка при загрузке списка плагинов'
    }
  } finally {
    loading.value = false
  }
}

const publishPlugin = async (pluginId: string, isPublished: boolean) => {
  publishing.value = pluginId
  error.value = null

  try {
    await adminApi.publishPlugin(pluginId, isPublished)
    successMessage.value = `Плагин ${isPublished ? 'опубликован' : 'скрыт'}`
    await loadPlugins()
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  } catch (err: any) {
    console.error('Publish error:', err)
    const errorMsg = err.response?.data?.message || err.response?.data?.error?.message || err.message
    error.value = errorMsg || 'Ошибка при изменении статуса плагина'
  } finally {
    publishing.value = null
  }
}

const deletePlugin = async (pluginId: string) => {
  if (!confirm('Вы уверены, что хотите удалить этот плагин? Это действие нельзя отменить.')) {
    return
  }

  deleting.value = pluginId
  error.value = null

  try {
    await adminApi.deletePlugin(pluginId)
    successMessage.value = 'Плагин успешно удален'
    await loadPlugins()
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  } catch (err: any) {
    console.error('Delete error:', err)
    const errorMsg = err.response?.data?.message || err.response?.data?.error?.message || err.message
    error.value = errorMsg || 'Ошибка при удалении плагина'
  } finally {
    deleting.value = null
  }
}

const pluginUrl = ref('')

const previewPlugin = (plugin: Record<string, any>) => {
  previewPluginData.value = plugin
  messageLog.value = []
  
  // Формируем URL для iframe
  // Путь: /static/plugins/{plugin_id}/{version}/{entry}
  pluginUrl.value = `${API_BASE_URL}/static/plugins/${plugin.plugin_id}/${plugin.version}/${plugin.entry}`
  
  // Настраиваем обработчик postMessage
  setupMessageHandler()
}

const setupMessageHandler = () => {
  // Удаляем предыдущий обработчик, если есть
  if (messageHandler.value) {
    window.removeEventListener('message', messageHandler.value)
  }
  
  messageHandler.value = (event: MessageEvent) => {
    // Проверяем origin для безопасности (в продакшене нужно строже)
    // if (event.origin !== window.location.origin) return
    
    try {
      const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data
      
      if (data.type) {
        messageLog.value.push({
          type: data.type,
          data: data,
        })
        
        // Обрабатываем SUBMIT - отправляем на сервер
        if (data.type === 'SUBMIT') {
          handlePluginSubmit(data)
        }
        
        // Обрабатываем INIT - отправляем подтверждение
        if (data.type === 'INIT') {
          sendMessageToPlugin({
            type: 'INIT',
            status: 'ready',
          })
        }
      }
    } catch (e) {
      console.error('Error parsing message:', e)
    }
  }
  
  window.addEventListener('message', messageHandler.value)
}

const handlePluginSubmit = async (data: any) => {
  try {
    // Отправляем на сервер для проверки
    const response = await fetch(`${API_BASE_URL}/api/v1/plugins/evaluate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        plugin_id: previewPluginData.value?.plugin_id,
        task_id: data.taskId || 'preview',
        userAnswer: data.userAnswer,
      }),
    })
    
    const result = await response.json()
    
    // Отправляем результат обратно в плагин
    sendMessageToPlugin({
      type: 'SERVER_RESULT',
      correct: result.data?.correct || false,
      score: result.data?.score || 0,
      explanation: result.data?.explanation || '',
    })
  } catch (err) {
    console.error('Evaluate error:', err)
    sendMessageToPlugin({
      type: 'SERVER_RESULT',
      correct: false,
      score: 0,
      explanation: 'Ошибка при проверке ответа',
    })
  }
}

const sendMessageToPlugin = (data: any) => {
  // Находим iframe и отправляем сообщение
  const iframe = document.querySelector('iframe')
  if (iframe && iframe.contentWindow) {
    iframe.contentWindow.postMessage(data, '*') // В продакшене указать конкретный origin
  }
}

const handleIframeLoad = () => {
  // Отправляем INIT сообщение в плагин
  sendMessageToPlugin({
    type: 'INIT',
    status: 'ready',
  })
}

const closePreview = () => {
  if (messageHandler.value) {
    window.removeEventListener('message', messageHandler.value)
    messageHandler.value = null
  }
  previewPluginData.value = null
  messageLog.value = []
}

onMounted(async () => {
  // Проверяем авторизацию
  if (!authStore.isAuthenticated) {
    error.value = 'Необходима авторизация. Перенаправление на страницу входа...'
    setTimeout(() => {
      router.push({ name: 'login', query: { redirect: '/admin/plugins' } })
    }, 2000)
    return
  }
  
  // Проверяем роль
  if (authStore.user?.role !== 'ADMIN') {
    error.value = 'Только администраторы могут управлять плагинами'
    return
  }
  
  // Загружаем плагины
  await loadPlugins()
})

onUnmounted(() => {
  if (messageHandler.value) {
    window.removeEventListener('message', messageHandler.value)
  }
})
</script>

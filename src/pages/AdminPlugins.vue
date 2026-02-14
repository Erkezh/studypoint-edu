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

      <!-- Загрузка TSX плагина -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Загрузить тест из TSX файла</h2>

        <div class="mb-4 p-4 bg-purple-50 border border-purple-200 rounded">
          <p class="text-sm text-purple-800 mb-2"><strong>Как это работает:</strong></p>
          <ul class="text-sm text-purple-700 list-disc list-inside space-y-1">
            <li>Загрузите TSX/JSX файл с React компонентом (как в примере <code class="bg-purple-100 px-1 rounded">fraction_comparison_app.tsx</code>)</li>
            <li>Система автоматически преобразует TSX в HTML плагин</li>
            <li>Плагин будет создан и опционально добавлен в тест для выбранного класса</li>
            <li>Максимальный размер: 1MB</li>
          </ul>
        </div>

        <form @submit.prevent="handleTsxUpload" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              TSX/JSX файл
            </label>
            <input
              ref="tsxFileInput"
              type="file"
              accept=".tsx,.ts,.jsx,.js"
              @change="handleTsxFileSelect"
              class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:outline-none"
            />
            <p v-if="selectedTsxFile" class="text-sm text-gray-600 mt-2">
              Выбран файл: {{ selectedTsxFile.name }} ({{ formatFileSize(selectedTsxFile.size) }})
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Название плагина (опционально)
            </label>
            <input
              v-model="tsxPluginName"
              type="text"
              placeholder="Автоматически из имени файла"
              class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:outline-none"
            />
          </div>

          <div class="flex gap-4">
            <Button type="submit" variant="primary" :loading="uploadingTsx">
              Загрузить TSX и создать плагин
            </Button>
            <Button type="button" variant="outline" @click="resetTsxUpload">
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
                <div class="flex items-center gap-3">
                  <h3 class="text-lg font-semibold text-gray-800">{{ plugin.name }}</h3>
                  <span class="px-2 py-0.5 bg-blue-100 text-blue-700 text-sm font-medium rounded-full">
                    v{{ plugin.version }}
                  </span>
                </div>
                <div class="mt-2 space-y-1 text-sm text-gray-600">
                  <p><strong>ID:</strong> {{ plugin.plugin_id }}</p>
                  <p><strong>Entry:</strong> {{ plugin.entry }}</p>
                  <p><strong>API Version:</strong> {{ plugin.api_version }}</p>
                  <p><strong>Высота:</strong> {{ plugin.height }}px</p>
                  <p><strong>Статус:</strong>
                    <span :class="plugin.is_published ? 'text-green-600' : 'text-gray-500'">
                      {{ plugin.is_published ? 'Опубликован' : 'Не опубликован' }}
                    </span>
                  </p>
                  <p><strong>Создан:</strong> {{ formatDate(plugin.created_at) }}</p>
                  <p v-if="plugin.updated_at && plugin.updated_at !== plugin.created_at">
                    <strong>Обновлён:</strong>
                    <span class="text-yellow-600 font-medium">{{ formatDate(plugin.updated_at) }}</span>
                  </p>
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
                  v-if="plugin.is_published"
                  variant="primary"
                  size="sm"
                  @click="openAddToTest(plugin)"
                  :loading="addingToTest === plugin.id"
                >
                  Добавить в тест
                </Button>
                <!-- Кнопка обновления плагина -->
                <label class="cursor-pointer">
                  <input
                    type="file"
                    accept=".tsx,.ts,.jsx,.js"
                    class="hidden"
                    @change="(e) => handleUpdatePlugin(plugin.id, e)"
                    :disabled="updating === plugin.id"
                  />
                  <span
                    :class="[
                      'inline-flex items-center justify-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                      updating === plugin.id
                        ? 'bg-gray-200 text-gray-500 cursor-wait'
                        : 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border border-yellow-300'
                    ]"
                  >
                    {{ updating === plugin.id ? 'Обновление...' : 'Обновить' }}
                  </span>
                </label>
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
            <!-- Кнопка «Проверить» для embed-режима -->
            <div class="mb-4 flex gap-2 items-center">
              <Button
                variant="primary"
                size="sm"
                @click="requestPluginAnswer"
              >
                Проверить
              </Button>
              <span class="text-sm text-gray-500">Плагин в тестовом режиме — только задание.</span>
            </div>
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

      <!-- Модальное окно «Добавить в тест» -->
      <div
        v-if="addToTestPlugin"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="addToTestPlugin = null"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-semibold mb-4">Добавить плагин «{{ addToTestPlugin.name }}» в тест</h3>
          <p class="text-sm text-gray-600 mb-4">
            Плагин станет отдельным навыком. Выберите класс и тему — навык появится в практике.
          </p>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Класс (сынып)</label>
              <select
                v-model="addToTestGradeId"
                class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option :value="null">— Выберите класс —</option>
                <option v-for="g in grades" :key="g.id" :value="g.id">{{ g.title }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Тема (тақырып) — необязательно</label>
              <select
                v-model="addToTestTopicId"
                class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option :value="null">— Без темы —</option>
                <option v-for="t in topics" :key="t.id" :value="t.id">{{ t.icon ? t.icon + ' ' : '' }}{{ t.title }}</option>
              </select>
            </div>
          </div>
          <div class="flex gap-2 mt-6">
            <Button variant="primary" :loading="addingToTest !== null" :disabled="!addToTestGradeId" @click="submitAddToTest">
              Добавить в тест
            </Button>
            <Button variant="outline" @click="addToTestPlugin = null">Отмена</Button>
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
import { catalogApi } from '@/api/catalog'
import { API_BASE_URL } from '@/config/api'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import type { AxiosError } from 'axios'

interface Plugin {
  id: string
  plugin_id: string
  version: string
  name: string
  entry: string
  api_version: string
  height: number
  is_published: boolean
  created_at: string
  updated_at?: string
}

interface PluginUploadResponse {
  name: string
  added_to_test?: {
    already_exists: boolean
    skill_title: string
  }
}

interface PluginMessage {
  type: string
  taskId?: string
  userAnswer?: unknown
  [key: string]: unknown
}

interface ErrorDetail {
  msg?: string
  message?: string
  code?: string
  details?: unknown
}

interface ApiErrorResponse {
  error?: {
    code?: string
    message?: string
    details?: unknown
  } | string
  detail?: string | ErrorDetail[] | { message?: string }
  message?: string
}

interface Grade {
  id: number
  number: number
  title: string
}

interface PluginSubmitData {
  taskId?: string
  userAnswer?: unknown
  [key: string]: unknown
}

interface PluginResponse {
  data?: {
    correct?: boolean
    score?: number
    explanation?: string
  }
}

const router = useRouter()

const authStore = useAuthStore()
const loading = ref(false)
const publishing = ref<string | null>(null)
const deleting = ref<string | null>(null)
const updating = ref<string | null>(null)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const selectedTsxFile = ref<File | null>(null)
const tsxFileInput = ref<HTMLInputElement | null>(null)
const tsxPluginName = ref<string>('')
const uploadingTsx = ref(false)
const plugins = ref<Plugin[]>([])
const previewPluginData = ref<Plugin | null>(null)
const messageLog = ref<Array<{ type: string; data: PluginMessage }>>([])
const messageHandler = ref<((event: MessageEvent) => void) | null>(null)
const addToTestPlugin = ref<Plugin | null>(null)
const addToTestGradeId = ref<number | null>(null)
const addToTestTopicId = ref<number | null>(null)
const grades = ref<Array<{ id: number; number: number; title: string }>>([])
const topics = ref<Array<{ id: number; title: string; icon: string | null }>>([])
const addingToTest = ref<string | null>(null)

const handleTsxFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file instanceof File) {
    selectedTsxFile.value = file
    // Автоматически заполняем название плагина из имени файла
    if (!tsxPluginName.value && file.name) {
      const fileName = file.name.replace(/\.(tsx|ts)$/, '')
      tsxPluginName.value = fileName.replace(/[^a-zA-Z0-9\s-]/g, '').replace(/\s+/g, '-').toLowerCase()
    }
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

const handleTsxUpload = async () => {
  if (!selectedTsxFile.value) {
    error.value = 'Выберите TSX файл для загрузки'
    return
  }

  uploadingTsx.value = true
  error.value = null
  successMessage.value = null

  try {
    const response = await adminApi.uploadTsxPlugin(
      selectedTsxFile.value,
      tsxPluginName.value || undefined
    )

    const responseData = (response.data ?? null) as PluginUploadResponse | null
    let message =
      responseData?.name !== undefined
        ? `Плагин "${responseData.name}" успешно создан из TSX файла!`
        : 'Плагин успешно создан из TSX файла!'

    if (responseData?.added_to_test) {
      if (responseData.added_to_test.already_exists) {
        message += ` Плагин уже был добавлен в тест как навык «${responseData.added_to_test.skill_title}».`
      } else {
        message += ` Плагин добавлен в тест как навык «${responseData.added_to_test.skill_title}».`
      }
    }

    successMessage.value = message
    resetTsxUpload()
    await loadPlugins()
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err: unknown) {
    const axiosError = err as AxiosError<ApiErrorResponse>
    console.error('TSX Upload error:', axiosError)
    console.error('TSX Upload error response:', axiosError.response?.data)
    console.error('TSX Upload error status:', axiosError.response?.status)

    const errorData = axiosError.response?.data

    let errorMsg = 'Ошибка при загрузке TSX файла'

    // Обработка сетевых ошибок
    if (!axiosError.response) {
      errorMsg = 'Не удалось подключиться к серверу. Проверьте, что backend запущен.'
    }
    // Обработка ошибок от сервера
    else if (errorData?.error) {
      if (typeof errorData.error === 'object' && errorData.error?.message) {
        errorMsg = errorData.error.message
      } else if (typeof errorData.error === 'object' && errorData.error?.code) {
        const codeMessages: Record<string, string> = {
          invalid_file: 'Некорректный файл. Файл должен быть .tsx, .jsx, .ts или .js',
          invalid_tsx: 'Некорректный TSX код. Проверьте синтаксис React компонента.',
          file_read_error: 'Ошибка при чтении файла. Убедитесь, что файл не поврежден.',
          file_encoding_error: 'Ошибка декодирования файла. Убедитесь, что файл в кодировке UTF-8.',
          empty_file: 'Файл пустой или не содержит TSX код.',
          tsx_transform_error: 'Ошибка при преобразовании TSX в HTML.',
        }
        const code = errorData.error.code
        errorMsg = (code && codeMessages[code]) || code || errorMsg
        if (errorData.error.details) {
          errorMsg += ` (${JSON.stringify(errorData.error.details)})`
        }
      }
    } else if (errorData?.detail) {
      if (typeof errorData.detail === 'string') {
        errorMsg = errorData.detail
      } else if (Array.isArray(errorData.detail)) {
        errorMsg = errorData.detail.map((e: ErrorDetail) => e.msg || e.message).join(', ')
      } else if (typeof errorData.detail === 'object' && 'message' in errorData.detail) {
        errorMsg = (errorData.detail as { message?: string }).message || errorMsg
      }
    } else if (axiosError.message) {
      errorMsg = axiosError.message
    }

    error.value = errorMsg
  } finally {
    uploadingTsx.value = false
  }
}

const resetTsxUpload = () => {
  selectedTsxFile.value = null
  tsxPluginName.value = ''
  if (tsxFileInput.value) {
    tsxFileInput.value.value = ''
  }
  error.value = null
  successMessage.value = null
}

const loadPlugins = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await adminApi.listPlugins()
    plugins.value = (response.data || []) as Plugin[]
  } catch (err: unknown) {
    const axiosError = err as AxiosError<ApiErrorResponse>
    console.error('Load plugins error:', axiosError)

    // Обработка ошибок авторизации
    if (axiosError.response?.status === 401) {
      const errorDetail = axiosError.response.data?.error || axiosError.response.data?.detail
      if (errorDetail && typeof errorDetail === 'object' && 'message' in errorDetail) {
        error.value = `Ошибка авторизации: ${(errorDetail as { message?: string }).message}. Пожалуйста, войдите снова.`
      } else {
        error.value = 'Ошибка авторизации. Токен истек или недействителен. Пожалуйста, войдите снова.'
      }

      setTimeout(() => {
        if (confirm('Токен истек. Перейти на страницу входа?')) {
          router.push({ name: 'login', query: { redirect: '/admin/plugins' } })
        }
      }, 2000)
    } else if (axiosError.response?.status === 403) {
      error.value = 'У вас нет прав для доступа к этой странице. Требуется роль ADMIN.'
    } else {
      const errorMsg =
        axiosError.response?.data?.message ||
        (typeof axiosError.response?.data?.error === 'object' &&
          (axiosError.response?.data?.error as { message?: string }).message) ||
        (typeof axiosError.response?.data?.error === 'string'
          ? axiosError.response?.data?.error
          : undefined) ||
        axiosError.message
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
  } catch (err) {
    console.error('Publish error:', err)
    const axiosError = err as AxiosError<ApiErrorResponse>
    const errorMsg = axiosError.response?.data?.message ||
      (typeof axiosError.response?.data?.error === 'object' && axiosError.response?.data?.error?.message) ||
      (typeof axiosError.response?.data?.error === 'string' ? axiosError.response?.data?.error : undefined) ||
      axiosError.message
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
  } catch (err: unknown) {
    const axiosError = err as AxiosError<ApiErrorResponse>
    console.error('Delete error:', axiosError)
    const errorMsg =
      axiosError.response?.data?.message ||
      (typeof axiosError.response?.data?.error === 'object' &&
        (axiosError.response?.data?.error as { message?: string }).message) ||
      (typeof axiosError.response?.data?.error === 'string'
        ? axiosError.response?.data?.error
        : undefined) ||
      axiosError.message
    error.value = errorMsg || 'Ошибка при удалении плагина'
  } finally {
    deleting.value = null
  }
}

const handleUpdatePlugin = async (pluginId: string, event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  updating.value = pluginId
  error.value = null

  try {
    const response = await adminApi.updateTsxPlugin(pluginId, file)
    const data = response.data?.data as { old_version?: string; version?: string } | undefined
    if (data?.old_version && data?.version) {
      successMessage.value = `Плагин обновлён! Версия: ${data.old_version} → ${data.version}`
    } else {
      successMessage.value = 'Плагин успешно обновлен!'
    }
    await loadPlugins()
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err: unknown) {
    const axiosError = err as AxiosError<ApiErrorResponse>
    console.error('Update plugin error:', axiosError)
    const errorMsg =
      axiosError.response?.data?.message ||
      (typeof axiosError.response?.data?.error === 'object' &&
        (axiosError.response?.data?.error as { message?: string }).message) ||
      (typeof axiosError.response?.data?.error === 'string'
        ? axiosError.response?.data?.error
        : undefined) ||
      axiosError.message
    error.value = errorMsg || 'Ошибка при обновлении плагина'
  } finally {
    updating.value = null
    // Очищаем input, чтобы можно было выбрать тот же файл снова
    target.value = ''
  }
}

const pluginUrl = ref('')

const previewPlugin = (plugin: Plugin) => {
  previewPluginData.value = plugin
  messageLog.value = []
  error.value = null

  // Формируем URL для iframe (embed=1 — только задание, без кнопок)
  // Путь: /static/plugins/{plugin_id}/{version}/{entry}
  const base = `${API_BASE_URL}/static/plugins/${plugin.plugin_id}/${plugin.version}/${plugin.entry}`
  pluginUrl.value = base.includes('?') ? `${base}&embed=1` : `${base}?embed=1`

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
      const data = (typeof event.data === 'string' ? JSON.parse(event.data) : event.data) as PluginMessage

      if (data.type) {
        messageLog.value.push({
          type: data.type,
          data,
        })

        if (data.type === 'SUBMIT') {
          handlePluginSubmit(data)
        }

        if (data.type === 'INIT') {
          sendMessageToPlugin({
            type: 'INIT',
            status: 'ready',
          })
        }
        if (data.type === 'ANSWER_NOT_READY') {
          error.value = 'Заполните оба поля (перетащите числа в ячейки)'
          setTimeout(() => {
            error.value = null
          }, 3000)
        }
      }
    } catch (e: unknown) {
      console.error('Error parsing message:', e)
    }
  }

  window.addEventListener('message', messageHandler.value)
}

const handlePluginSubmit = async (data: PluginSubmitData) => {
  try {
    // Отправляем на сервер для проверки
    const response = await fetch(`${API_BASE_URL}/api/v1/admin/plugins/evaluate`, {
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

    const result = (await response.json()) as PluginResponse

    sendMessageToPlugin({
      type: 'SERVER_RESULT',
      correct: result.data?.correct || false,
      score: result.data?.score || 0,
      explanation: result.data?.explanation || '',
    })
  } catch (err: unknown) {
    console.error('Evaluate error:', err)
    sendMessageToPlugin({
      type: 'SERVER_RESULT',
      correct: false,
      score: 0,
      explanation: 'Ошибка при проверке ответа',
    })
  }
}

const sendMessageToPlugin = (data: PluginMessage) => {
  const iframe = document.querySelector('iframe')
  if (iframe && iframe.contentWindow) {
    iframe.contentWindow.postMessage(data, '*')
  }
}

const requestPluginAnswer = () => {
  if (!previewPluginData.value) return
  sendMessageToPlugin({ type: 'REQUEST_ANSWER' })
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

const loadGrades = async () => {
  try {
    const res = await catalogApi.getGrades()
    grades.value = (res.data || []).map((g: Grade) => ({
      id: g.id,
      number: g.number,
      title: g.title,
    }))
  } catch (e) {
    console.error('Load grades error:', e)
  }
}

const loadTopics = async () => {
  try {
    const res = await catalogApi.getTopics()
    topics.value = (res.data || []).map((t: { id: number; title: string; icon?: string | null }) => ({
      id: t.id,
      title: t.title,
      icon: t.icon ?? null,
    }))
  } catch (e) {
    console.error('Load topics error:', e)
  }
}

const openAddToTest = (plugin: Plugin) => {
  addToTestPlugin.value = plugin
  addToTestGradeId.value = null
  addToTestTopicId.value = null
}

const submitAddToTest = async () => {
  if (!addToTestPlugin.value || !addToTestGradeId.value) return
  addingToTest.value = addToTestPlugin.value.id
  error.value = null
  try {
    const res = await adminApi.addPluginToTest({
      grade_id: addToTestGradeId.value,
      topic_id: addToTestTopicId.value,
      plugin_id: addToTestPlugin.value.plugin_id,
      plugin_version: addToTestPlugin.value.version,
    })
    const title = res.data?.skill_title ?? addToTestPlugin.value.name
    if (res.data?.already_exists) {
      successMessage.value =
        res.data?.message ||
        `Плагин «${addToTestPlugin.value.name}» уже добавлен в тест как навык «${title}».`
    } else {
      successMessage.value = `Плагин «${addToTestPlugin.value.name}» добавлен в тест как навык «${title}».`
    }
    addToTestPlugin.value = null
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err: unknown) {
    const axiosError = err as AxiosError<ApiErrorResponse>
    console.error('Add plugin to test error:', axiosError)
    if (axiosError.response?.status === 409) {
      const detail = axiosError.response?.data?.error || axiosError.response?.data
      const message =
        (typeof detail === 'string'
          ? detail
          : detail && typeof detail === 'object' && 'message' in detail
          ? (detail as { message?: string }).message
          : undefined) ||
        'Плагин уже добавлен в тест или возник конфликт при создании навыка'
      error.value = message
    } else {
      const detail = axiosError.response?.data?.error || axiosError.response?.data
      error.value =
        (typeof detail === 'string'
          ? detail
          : detail && typeof detail === 'object' && 'message' in detail
          ? (detail as { message?: string }).message
          : undefined) ||
        axiosError.message ||
        'Ошибка при добавлении плагина в тест'
    }
  } finally {
    addingToTest.value = null
  }
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
  await loadGrades()
  await loadTopics()
})

onUnmounted(() => {
  if (messageHandler.value) {
    window.removeEventListener('message', messageHandler.value)
  }
})
</script>

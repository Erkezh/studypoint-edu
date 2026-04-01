<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8 max-w-5xl">
      <div class="mb-6">
        <h1 class="text-3xl font-bold mb-2">Тест жүктеу</h1>
        <p class="text-gray-600">TSX файлдан тест жүктеп, сыныпқа, тақырыпқа және ішкі тақырыпқа тіркеңіз. Жүктелген тесттерді <router-link :to="{ name: 'admin-skills' }" class="text-blue-600 underline hover:text-blue-800">Тесттер</router-link> бетінде басқара аласыз.</p>
      </div>

      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{{ error }}</div>
      <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">{{ successMessage }}</div>

      <!-- Upload Form -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
          TSX файлдан тест жүктеу
        </h2>

        <div class="mb-4 p-3 bg-purple-50 border border-purple-200 rounded text-sm text-purple-700">
          <p>TSX/JSX файлды жүктеңіз → атауын, сыныпты, тақырыпты және ішкі тақырыпты таңдаңыз → «Жүктеу» басыңыз. Тест автоматты түрде жарияланады.</p>
        </div>

        <form @submit.prevent="handleTsxUpload" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">TSX/JSX файл *</label>
            <input ref="tsxFileInput" type="file" accept=".tsx,.ts,.jsx,.js" @change="handleTsxFileSelect"
              class="w-full p-2.5 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:outline-none" />
            <p v-if="selectedTsxFile" class="text-sm text-gray-600 mt-1">{{ selectedTsxFile.name }} ({{ formatFileSize(selectedTsxFile.size) }})</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Атауы *</label>
              <input v-model="tsxPluginName" type="text" placeholder="Бөлшектерді салыстыру"
                class="w-full p-2.5 border border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Сынып *</label>
              <select v-model="uploadGradeId" class="w-full p-2.5 border border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none bg-white">
                <option :value="null">— Сыныпты таңдаңыз —</option>
                <option v-for="g in grades" :key="g.id" :value="g.id">{{ g.title }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Тақырып</label>
              <select v-model="uploadThemeId" class="w-full p-2.5 border border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none bg-white" @change="uploadSubthemeId = null">
                <option :value="null">— Тақырыпты таңдаңыз —</option>
                <option v-for="t in themes" :key="t.id" :value="t.id">{{ t.icon ? t.icon + ' ' : '' }}{{ t.title }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Ішкі тақырып</label>
              <select v-model="uploadSubthemeId" :disabled="!uploadThemeId"
                class="w-full p-2.5 border border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none bg-white disabled:bg-gray-100">
                <option :value="null">— Ішкі тақырыпты таңдаңыз —</option>
                <option v-for="s in uploadSubthemes" :key="s.id" :value="s.id">{{ s.title }}</option>
              </select>
            </div>
          </div>

          <div class="flex gap-3">
            <Button type="submit" variant="primary" :loading="uploadingTsx" :disabled="!selectedTsxFile || !tsxPluginName || !uploadGradeId">
              Жүктеу және жариялау
            </Button>
            <Button type="button" variant="outline" @click="resetTsxUpload">Тазалау</Button>
          </div>
        </form>
      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { adminApi } from '@/api/admin'
import { catalogApi } from '@/api/catalog'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import type { AxiosError } from 'axios'

interface PluginUploadResponse { name: string; added_to_test?: { already_exists: boolean; skill_title: string } }
interface ApiErrorResponse { error?: { code?: string; message?: string } | string; detail?: string; message?: string }
interface Grade { id: number; number: number; title: string }
interface TopicItem { id: number; title: string; icon: string | null; parent_id: number | null }
interface Plugin { id: string; plugin_id: string; version: string; name: string; is_published: boolean }

const router = useRouter()
const authStore = useAuthStore()
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const selectedTsxFile = ref<File | null>(null)
const tsxFileInput = ref<HTMLInputElement | null>(null)
const tsxPluginName = ref('')
const uploadingTsx = ref(false)
const uploadGradeId = ref<number | null>(null)
const uploadThemeId = ref<number | null>(null)
const uploadSubthemeId = ref<number | null>(null)
const grades = ref<Grade[]>([])
const allTopics = ref<TopicItem[]>([])

const themes = computed(() => allTopics.value.filter(t => !t.parent_id))
const uploadSubthemes = computed(() =>
  uploadThemeId.value ? allTopics.value.filter(t => t.parent_id === uploadThemeId.value) : []
)

const handleTsxFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file instanceof File) {
    selectedTsxFile.value = file
    if (!tsxPluginName.value && file.name) {
      const fileName = file.name.replace(/\.(tsx|ts|jsx|js)$/, '')
      tsxPluginName.value = fileName.replace(/[_-]/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
    }
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const handleTsxUpload = async () => {
  if (!selectedTsxFile.value || !tsxPluginName.value || !uploadGradeId.value) {
    error.value = 'Файл, атауы және сынып міндетті!'
    return
  }
  uploadingTsx.value = true
  error.value = null
  successMessage.value = null

  try {
    const response = await adminApi.uploadTsxPlugin(selectedTsxFile.value, tsxPluginName.value || undefined)
    const responseData = (response.data ?? null) as PluginUploadResponse | null
    const pluginName = responseData?.name || tsxPluginName.value

    // Load plugins to find the new one, auto-publish & add to test
    const pluginsResp = await adminApi.listPlugins()
    const plugins = (pluginsResp.data || []) as unknown as Plugin[]
    const newPlugin = plugins.find(p => p.name === pluginName)
    if (newPlugin) {
      if (!newPlugin.is_published) await adminApi.publishPlugin(newPlugin.id, true)
      const topicId = uploadSubthemeId.value || uploadThemeId.value
      try {
        await adminApi.addPluginToTest({
          grade_id: uploadGradeId.value!,
          topic_id: topicId,
          plugin_id: newPlugin.plugin_id,
          plugin_version: newPlugin.version,
        })
      } catch (e) { console.warn('Auto add-to-test failed:', e) }
    }

    successMessage.value = `Тест «${pluginName}» сәтті жүктелді және жарияланды!`
    resetTsxUpload()
    setTimeout(() => { successMessage.value = null }, 5000)
  } catch (err: unknown) {
    const axiosError = err as AxiosError<ApiErrorResponse>
    const errorData = axiosError.response?.data
    let errorMsg = 'TSX файлды жүктеу қатесі'
    if (!axiosError.response) errorMsg = 'Серверге қосылу мүмкін болмады.'
    else if (errorData?.error && typeof errorData.error === 'object' && errorData.error?.message) errorMsg = errorData.error.message
    else if (typeof errorData?.detail === 'string') errorMsg = errorData.detail
    error.value = errorMsg
  } finally {
    uploadingTsx.value = false
  }
}

const resetTsxUpload = () => {
  selectedTsxFile.value = null
  tsxPluginName.value = ''
  uploadGradeId.value = null
  uploadThemeId.value = null
  uploadSubthemeId.value = null
  if (tsxFileInput.value) tsxFileInput.value.value = ''
}

onMounted(async () => {
  if (!authStore.isAuthenticated || authStore.user?.role !== 'ADMIN') {
    router.push({ name: 'login', query: { redirect: '/admin/plugins' } })
    return
  }
  try {
    const [gradesResp, topicsResp] = await Promise.all([catalogApi.getGrades(), catalogApi.getTopics()])
    grades.value = (gradesResp.data || []).map((g: Grade) => ({ id: g.id, number: g.number, title: g.title }))
    allTopics.value = (topicsResp.data || []).map((t: TopicItem) => ({ id: t.id, title: t.title, icon: t.icon ?? null, parent_id: t.parent_id ?? null }))
  } catch (e) { console.error('Load error:', e) }
})
</script>

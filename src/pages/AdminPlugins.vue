<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8 max-w-5xl">
      <div class="mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-3xl font-bold mb-2 text-gray-900">Тест жүктеу</h1>
          <p class="text-gray-600">TSX файлдан тест жүктеп, сыныпқа, тақырыпқа және ішкі тақырыпқа тіркеңіз. Жүктелген тесттерді <router-link :to="{ name: 'admin-skills' }" class="text-blue-600 underline hover:text-blue-800">Тесттер</router-link> бетінде басқара аласыз.</p>
        </div>
        <button
          type="button"
          @click="copyPluginPromptTemplate"
          class="px-4 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-bold rounded-xl shadow-md hover:shadow-lg transition-all flex items-center gap-2 text-sm cursor-pointer shrink-0"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
          <span>{{ pluginPromptTemplateCopied ? 'Промт көшірілді! ✓' : '📋 Плагин промтын көшіру' }}</span>
        </button>
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
            <label class="block text-sm font-medium text-gray-700 mb-1">TSX/JSX/HTML файл *</label>
            <input ref="tsxFileInput" type="file" accept=".html,.htm,.tsx,.ts,.jsx,.js" @change="handleTsxFileSelect"
              class="w-full p-2.5 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:outline-none" />
            <p v-if="selectedTsxFile" class="text-sm text-gray-600 mt-1">{{ selectedTsxFile.name }} ({{ formatFileSize(selectedTsxFile.size) }})</p>

            <!-- AUTOMATIC PLUGIN AUDIT RESULT CARD -->
            <div v-if="fileCheckResult" class="mt-4 p-4 rounded-xl border transition-all" :class="fileCheckResult.isValid && fileCheckResult.warnings.length === 0 ? 'bg-emerald-50 border-emerald-300 text-emerald-900' : 'bg-amber-50 border-amber-300 text-slate-900'">
              <div class="flex flex-wrap items-center justify-between gap-2 font-bold text-sm mb-2">
                <div class="flex items-center gap-2">
                  <span v-if="fileCheckResult.isValid && fileCheckResult.warnings.length === 0" class="text-emerald-600 text-lg">✅</span>
                  <span v-else-if="fileCheckResult.issues.length > 0" class="text-rose-600 text-lg">🔴</span>
                  <span v-else class="text-amber-600 text-lg">⚠️</span>

                  <span v-if="fileCheckResult.isValid && fileCheckResult.warnings.length === 0" class="text-emerald-900 font-bold">
                    Плагин регламентке (PLUGIN_PROMPT_TEMPLATE.md) толық сәйкес келеді!
                  </span>
                  <span v-else-if="fileCheckResult.issues.length > 0" class="text-rose-900 font-extrabold">
                    Плагинде қателер табылды! (Учитель мен оқушыда әртүрлі сұрақ шығуы мүмкін)
                  </span>
                  <span v-else class="text-amber-900 font-bold">
                    Плагинде ескертулер бар
                  </span>
                </div>

                <!-- Copy AI Prompt Button -->
                <button 
                  v-if="fileCheckResult.aiPrompt" 
                  type="button" 
                  @click="copyAiPrompt(fileCheckResult.aiPrompt)" 
                  class="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
                  {{ promptCopied ? 'Промт көшірілді! ✓' : 'ИИ промтын көшіру (AI Fix Prompt)' }}
                </button>
              </div>

              <!-- Passed checks -->
              <div v-if="fileCheckResult.passed.length > 0" class="text-xs space-y-1 mb-2">
                <div v-for="(p, idx) in fileCheckResult.passed" :key="idx" class="flex items-center gap-1.5 text-emerald-700 font-medium">
                  <span class="font-bold">✓</span> {{ p }}
                </div>
              </div>

              <!-- Critical Issues -->
              <div v-if="fileCheckResult.issues.length > 0" class="mt-2 space-y-2 border-t border-rose-200/80 pt-2">
                <div v-for="issue in fileCheckResult.issues" :key="issue.code" class="p-3 bg-rose-100/90 border border-rose-300 rounded-lg text-xs text-rose-950 space-y-1">
                  <div class="font-bold flex items-center gap-1.5 text-rose-900 text-xs">
                    <span>❌</span> <span>[{{ issue.code }}] {{ issue.title }}</span>
                  </div>
                  <div class="text-rose-800 leading-relaxed">{{ issue.description }}</div>
                </div>
              </div>

              <!-- Warnings -->
              <div v-if="fileCheckResult.warnings.length > 0" class="mt-2 space-y-2 border-t border-amber-200/80 pt-2">
                <div v-for="warn in fileCheckResult.warnings" :key="warn.code" class="p-3 bg-amber-100/90 border border-amber-300 rounded-lg text-xs text-amber-950 space-y-1">
                  <div class="font-bold flex items-center gap-1.5 text-amber-900 text-xs">
                    <span>⚠️</span> <span>[{{ warn.code }}] {{ warn.title }}</span>
                  </div>
                  <div class="text-amber-800 leading-relaxed">{{ warn.description }}</div>
                </div>
              </div>
            </div>
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
import { validatePluginCode, type PluginCheckResult } from '@/utils/pluginValidator'
import { PLUGIN_PROMPT_TEMPLATE } from '@/data/pluginPromptTemplate'
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
const fileCheckResult = ref<PluginCheckResult | null>(null)
const promptCopied = ref(false)
const pluginPromptTemplateCopied = ref(false)

const copyPluginPromptTemplate = async () => {
  try {
    await navigator.clipboard.writeText(PLUGIN_PROMPT_TEMPLATE)
    pluginPromptTemplateCopied.value = true
    setTimeout(() => {
      pluginPromptTemplateCopied.value = false
    }, 3000)
  } catch (err) {
    console.error('Failed to copy plugin prompt:', err)
  }
}

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
      const fileName = file.name.replace(/\.(tsx|ts|jsx|js|html|htm)$/, '')
      tsxPluginName.value = fileName.replace(/[_-]/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
    }

    // Read file and validate automatically
    const reader = new FileReader()
    reader.onload = (e) => {
      const text = (e.target?.result as string) || ''
      fileCheckResult.value = validatePluginCode(text)
    }
    reader.readAsText(file)
  } else {
    fileCheckResult.value = null
  }
}

const copyAiPrompt = async (promptText: string) => {
  if (!promptText) return
  try {
    await navigator.clipboard.writeText(promptText)
    promptCopied.value = true
    setTimeout(() => { promptCopied.value = false }, 3000)
  } catch (err) {
    console.error('Failed to copy to clipboard:', err)
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
  fileCheckResult.value = null
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

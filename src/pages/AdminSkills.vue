<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8 max-w-6xl">
      <div class="mb-6">
        <h1 class="text-3xl font-bold mb-2">Тесттер</h1>
        <p class="text-gray-600">
          Барлық тесттерді басқару: атауын, сыныпты, тақырыпты өзгерту, алдын ала қарау, жою.
          Жаңа тест жүктеу үшін
          <router-link :to="{ name: 'admin-plugins' }" class="text-blue-600 underline hover:text-blue-800">Плагиндер</router-link>
          бетіне өтіңіз.
        </p>
      </div>

      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{{ error }}</div>
      <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">{{ successMessage }}</div>

      <!-- Filters -->
      <div class="bg-white rounded-xl shadow-sm p-4 mb-6 border border-gray-100 flex flex-col md:flex-row gap-4 items-stretch md:items-center">
        <div class="relative flex-1">
          <svg class="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
          <input v-model="searchQuery" type="text" placeholder="Тест атауы немесе код бойынша іздеу..."
            class="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500 focus:outline-none transition-all" />
        </div>
        <div class="flex flex-wrap gap-2">
          <select v-model="filterGradeId" class="flex-1 min-w-[120px] p-2 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500 focus:outline-none text-sm">
            <option :value="null">Барлық сыныптар</option>
            <option v-for="g in grades" :key="g.id" :value="g.id">{{ g.title }}</option>
          </select>
          <select v-model="filterTopicId" class="flex-1 min-w-[120px] p-2 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500 focus:outline-none text-sm">
            <option :value="null">Барлық тақырыптар</option>
            <option v-for="t in themes" :key="t.id" :value="t.id">{{ t.icon ? t.icon + ' ' : '' }}{{ t.title }}</option>
          </select>
        </div>
        <span class="text-sm text-gray-500 text-center md:text-left">{{ filteredSkills.length }} тест</span>
      </div>

      <!-- Skills List -->
      <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <div v-if="loadingSkills" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p class="text-gray-500 mt-2">Жүктелуде...</p>
        </div>

        <div v-else-if="filteredSkills.length === 0" class="text-center py-12 text-gray-500">
          Тесттер табылмады
        </div>

        <div v-else>
          <div
            v-for="skill in filteredSkills"
            :key="skill.id"
            @click="openSkillModal(skill)"
            class="flex items-center justify-between px-4 py-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors group last:border-b-0"
          >
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <!-- Icon -->
              <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                :class="skill.code.startsWith('PLG') ? 'bg-purple-100 text-purple-600' : 'bg-blue-100 text-blue-600'">
                <svg v-if="skill.code.startsWith('PLG')" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              </div>
              <!-- Info -->
              <div class="min-w-0 flex-1">
                <h3 class="text-sm font-semibold text-gray-800 truncate">{{ skill.title }}</h3>
                <p class="text-xs text-gray-500">
                  {{ getGradeName(skill.grade_id) }}
                  <span v-if="skill.topic_title"> · {{ skill.topic_title }}</span>
                  <span class="text-gray-400 ml-1">· {{ skill.code }}</span>
                </p>
              </div>
            </div>
            <!-- Arrow -->
            <svg class="w-4 h-4 text-gray-300 group-hover:text-gray-500 shrink-0 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </div>
        </div>
      </div>
    </main>
    <Footer />

    <!-- Edit Skill Modal (from EditSkillModal component) -->
    <EditSkillModal
      :isVisible="!!skillToEdit"
      :skill="skillToEdit"
      @close="skillToEdit = null"
      @save="handleEditSave"
    />

    <!-- Expanded Skill Detail Modal -->
    <div
      v-if="selectedSkill"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="selectedSkill = null"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-lg w-full p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-800">{{ selectedSkill.title }}</h3>
          <button @click="selectedSkill = null" class="text-gray-400 hover:text-gray-700 text-2xl leading-none">&times;</button>
        </div>

        <div class="space-y-3 mb-6">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-0.5">Код</label>
              <p class="text-sm font-mono text-gray-800 bg-gray-50 p-2 rounded">{{ selectedSkill.code }}</p>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-0.5">ID</label>
              <p class="text-sm font-mono text-gray-800 bg-gray-50 p-2 rounded">{{ selectedSkill.id }}</p>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-0.5">Сынып</label>
              <p class="text-sm text-gray-800">{{ getGradeName(selectedSkill.grade_id) }}</p>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-0.5">Тақырып</label>
              <p class="text-sm text-gray-800">{{ selectedSkill.topic_title || '—' }}</p>
            </div>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-0.5">Қиындық</label>
            <p class="text-sm text-gray-800">{{ selectedSkill.difficulty }}</p>
          </div>
          <div v-if="selectedSkill.tags && selectedSkill.tags.length > 0">
            <label class="block text-xs font-medium text-gray-500 mb-0.5">Тегтер</label>
            <div class="flex gap-1 flex-wrap">
              <span v-for="tag in selectedSkill.tags" :key="tag"
                class="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">{{ tag }}</span>
            </div>
          </div>

          <!-- Plugin preview for plugin-based skills -->
          <div v-if="selectedSkill.code.startsWith('PLG')" class="border-t pt-3 mt-3">
            <label class="block text-xs font-medium text-gray-500 mb-2">Плагин алдын ала қарау</label>
            <div v-if="!showingPreview">
              <Button variant="outline" size="sm" @click="loadPluginPreview(selectedSkill)">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                Алдын ала қарау
              </Button>
            </div>
            <div v-else>
              <iframe
                :src="previewUrl"
                style="width: 100%; height: 450px; border: 1px solid #e5e7eb;"
                sandbox="allow-scripts"
                class="rounded"
              ></iframe>
            </div>
          </div>
        </div>

        <div class="flex gap-2 border-t pt-4">
          <Button variant="primary" @click="editFromModal(selectedSkill)">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
            Өзгерту
          </Button>
          <Button variant="danger" @click="confirmDelete(selectedSkill)" :loading="deletingSkillId === selectedSkill.id">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
            Жою
          </Button>
          <Button variant="outline" @click="selectedSkill = null" class="ml-auto">Жабу</Button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <Modal :isOpen="!!skillToDelete" @close="skillToDelete = null" title="Тестті жою" :showClose="true">
      <template #content>
        <p class="text-gray-700 mb-4">
          Сіз шынымен "<strong>{{ skillToDelete?.title }}</strong>" тестін жойғыңыз келе ме?
        </p>
        <p class="text-sm text-red-600 flex items-center gap-2">
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
          Бұл әрекетті қайтару мүмкін емес!
        </p>
      </template>
      <template #actions>
        <Button v-if="skillToDelete" @click="handleDelete" variant="primary" :loading="deletingSkillId === skillToDelete.id" class="bg-red-600 hover:bg-red-700">
          Иә, жою
        </Button>
        <Button @click="skillToDelete = null" variant="outline">Болдырмау</Button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCatalogStore } from '@/stores/catalog'
import { adminApi, type SkillListItem } from '@/api/admin'
import { useRouter } from 'vue-router'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import Modal from '@/components/ui/Modal.vue'
import EditSkillModal from '@/components/catalog/EditSkillModal.vue'

const authStore = useAuthStore()
const catalogStore = useCatalogStore()
const router = useRouter()

const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const loadingSkills = ref(false)
const skillsList = ref<SkillListItem[]>([])
const skillToDelete = ref<SkillListItem | null>(null)
const deletingSkillId = ref<number | null>(null)
const skillToEdit = ref<SkillListItem | null>(null)
const selectedSkill = ref<SkillListItem | null>(null)

// Filters
const searchQuery = ref('')
const filterGradeId = ref<number | null>(null)
const filterTopicId = ref<number | null>(null)

// Plugin preview
const showingPreview = ref(false)
const previewUrl = ref('')

const grades = computed(() => catalogStore.grades)
const themes = computed(() => catalogStore.topics.filter(t => !t.parent_id))

const filteredSkills = computed(() => {
  let result = skillsList.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(s => s.title.toLowerCase().includes(q) || s.code.toLowerCase().includes(q))
  }
  if (filterGradeId.value) {
    result = result.filter(s => s.grade_id === filterGradeId.value)
  }
  if (filterTopicId.value) {
    // Include subthemes of the selected theme
    const subthemeIds = catalogStore.topics
      .filter(t => t.parent_id === filterTopicId.value)
      .map(t => t.id)
    const allIds = [filterTopicId.value, ...subthemeIds]
    result = result.filter(s => s.topic_id && allIds.includes(s.topic_id))
  }
  return result
})

const getGradeName = (gradeId: number): string => {
  const grade = grades.value.find(g => g.id === gradeId)
  return grade ? grade.title : `ID: ${gradeId}`
}

const openSkillModal = (skill: SkillListItem) => {
  selectedSkill.value = skill
  showingPreview.value = false
  previewUrl.value = ''
}

const editFromModal = (skill: SkillListItem) => {
  selectedSkill.value = null
  skillToEdit.value = skill
}

const loadPluginPreview = async (skill: SkillListItem) => {
  // The plugin code starts with PLG, the plugin_id is stored in tags or we can derive from skill
  // Try to find plugin by listing plugins
  try {
    const resp = await adminApi.listPlugins()
    const plugins = resp.data || []
    // Match by skill title or code
    const pluginName = skill.title
    const plugin = plugins.find((p: Record<string, unknown>) => p.name === pluginName) || plugins.find((p: Record<string, unknown>) => typeof skill.code === 'string' && skill.code.includes(p.plugin_id as string))
    if (plugin) {
      const base = `/static/modules/${plugin.plugin_id}/${plugin.version}/${plugin.entry}`
      previewUrl.value = base.includes('?') ? `${base}&embed=1` : `${base}?embed=1`
      showingPreview.value = true
    } else {
      error.value = 'Плагин табылмады'
      setTimeout(() => { error.value = null }, 3000)
    }
  } catch (e) {
    console.error('Failed to load plugin for preview:', e)
    error.value = 'Плагинді жүктеу қатесі'
  }
}

const handleEditSave = async () => {
  await loadSkills()
  successMessage.value = 'Тест сәтті өзгертілді!'
  setTimeout(() => { successMessage.value = null }, 3000)
}

const confirmDelete = (skill: SkillListItem) => {
  selectedSkill.value = null
  skillToDelete.value = skill
}

const handleDelete = async () => {
  if (!skillToDelete.value) return
  deletingSkillId.value = skillToDelete.value.id
  try {
    await adminApi.deleteSkill(skillToDelete.value.id)
    successMessage.value = `«${skillToDelete.value.title}» сәтті жойылды!`
    skillToDelete.value = null
    await loadSkills()
    setTimeout(() => { successMessage.value = null }, 3000)
  } catch (err: unknown) {
    const e = err as { response?: { data?: { error?: { message?: string } } } }
    error.value = e.response?.data?.error?.message || 'Жою қатесі'
    skillToDelete.value = null
  } finally {
    deletingSkillId.value = null
  }
}

const loadSkills = async () => {
  loadingSkills.value = true
  try {
    const response = await adminApi.listSkills(1, 200)
    if (response.data) skillsList.value = response.data
  } catch (err: unknown) {
    const e = err as { response?: { status?: number } }
    if (e.response?.status === 401) {
      router.push({ name: 'login' })
    } else {
      error.value = 'Тесттерді жүктеу қатесі'
    }
  } finally {
    loadingSkills.value = false
  }
}

onMounted(async () => {
  if (!authStore.isAuthenticated || authStore.user?.role !== 'ADMIN') {
    router.push({ name: 'login', query: { redirect: '/admin/skills' } })
    return
  }
  await Promise.all([
    catalogStore.getGrades(),
    catalogStore.getTopics(),
    loadSkills()
  ])
})
</script>

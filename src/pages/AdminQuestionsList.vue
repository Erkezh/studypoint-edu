<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8 max-w-7xl">
      <div class="mb-6">
        <h1 class="text-3xl font-bold mb-2">Сұрақтарды басқару</h1>
        <p class="text-gray-600">Барлық тесттер мен сұрақтарды көру, өңдеу және жою</p>
      </div>

      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{{ error }}</div>
      <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">{{ successMessage }}</div>

      <!-- Tabs -->
      <div class="flex gap-1 mb-6 bg-white rounded-lg shadow-sm p-1 border border-gray-200 w-fit">
        <button @click="activeTab = 'skills'"
          :class="['px-4 py-2 rounded-md text-sm font-medium transition-colors', activeTab === 'skills' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100']">
          Тесттер ({{ skillsList.length }})
        </button>
        <button @click="activeTab = 'questions'"
          :class="['px-4 py-2 rounded-md text-sm font-medium transition-colors', activeTab === 'questions' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100']">
          Сұрақтар ({{ totalQuestions }})
        </button>
      </div>

      <!-- ==================== SKILLS TAB ==================== -->
      <div v-if="activeTab === 'skills'">
        <!-- Filters -->
        <div class="bg-white rounded-lg shadow-sm p-4 mb-4 flex flex-wrap gap-4 items-center">
          <div class="flex-1 min-w-[200px]">
            <input v-model="skillSearch" type="text" placeholder="Тест атауы бойынша іздеу..."
              class="w-full p-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none text-sm" />
          </div>
          <select v-model="skillFilterGradeId" class="p-2 border border-gray-300 rounded-lg text-sm bg-white">
            <option :value="null">Барлық сыныптар</option>
            <option v-for="g in grades" :key="g.id" :value="g.id">{{ g.title }}</option>
          </select>
          <select v-model="skillFilterTopicId" class="p-2 border border-gray-300 rounded-lg text-sm bg-white">
            <option :value="null">Барлық тақырыптар</option>
            <option v-for="t in themes" :key="t.id" :value="t.id">{{ t.icon ? t.icon + ' ' : '' }}{{ t.title }}</option>
          </select>
        </div>

        <!-- Skills List -->
        <div class="bg-white rounded-lg shadow-md overflow-hidden">
          <div v-if="loadingSkills" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
          <div v-else-if="filteredSkills.length === 0" class="text-center py-12 text-gray-500">Тесттер табылмады</div>
          <div v-else>
            <div v-for="skill in filteredSkills" :key="skill.id"
              @click="navigateToSkill(skill.id)"
              class="flex items-center justify-between px-4 py-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors group last:border-b-0">
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                  :class="skill.code.startsWith('PLG') ? 'bg-purple-100 text-purple-600' : 'bg-blue-100 text-blue-600'">
                  <svg v-if="skill.code.startsWith('PLG')" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                </div>
                <div class="min-w-0 flex-1">
                  <h3 class="text-sm font-semibold text-gray-800 truncate">{{ skill.title }}</h3>
                  <p class="text-xs text-gray-500">
                    {{ getGradeName(skill.grade_id) }}
                    <span v-if="skill.topic_title"> · {{ skill.topic_title }}</span>
                    <span class="text-gray-400 ml-1">· {{ skill.code }}</span>
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-1 ml-2 shrink-0">
                <!-- Edit button (hover) -->
                <button @click.stop="editFromModal(skill)"
                  class="text-gray-300 hover:text-blue-600 p-1.5 rounded hover:bg-blue-50 opacity-0 group-hover:opacity-100 transition-opacity" title="Өзгерту">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                </button>
                <!-- Delete button (hover) -->
                <button @click.stop="confirmDeleteSkill(skill)"
                  class="text-gray-300 hover:text-red-600 p-1.5 rounded hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-opacity" title="Жою">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
                <!-- Arrow -->
                <svg class="w-4 h-4 text-gray-300 group-hover:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ==================== QUESTIONS TAB ==================== -->
      <div v-if="activeTab === 'questions'">
        <!-- Filters -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Навык атауы бойынша іздеу</label>
              <input v-model="filters.search" type="text"
                class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                placeholder="Навық атауын жазыңыз..." @keyup.enter="loadQuestions" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Навық ID</label>
              <input v-model.number="filters.skill_id" type="number"
                class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                placeholder="ID нөмірі" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Сұрыптау</label>
              <select v-model="filters.sort_order" @change="loadQuestions"
                class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none">
                <option value="desc">Жаңалары алдымен</option>
                <option value="asc">Ескілері алдымен</option>
              </select>
            </div>
            <div class="flex items-end gap-2">
              <Button @click="loadQuestions" variant="primary" :loading="loadingQ">Іздеу</Button>
              <Button @click="resetFilters" variant="outline">Тазалау</Button>
            </div>
          </div>
        </div>

        <!-- Questions List -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-semibold">Сұрақтар тізімі</h2>
            <span class="text-sm text-gray-600">Барлығы: {{ totalQuestions }}</span>
          </div>

          <div v-if="loadingQ" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
          <div v-else-if="questionsList.length === 0" class="text-center py-8 text-gray-500">Сұрақтар табылмады</div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Навық</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Тип</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Сұрақ</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Деңгей</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Күні</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Әрекеттер</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="question in questionsList" :key="question.id">
                  <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-900">{{ question.id }}</td>
                  <td class="px-4 py-4 text-sm text-gray-500 max-w-xs">
                    <div class="truncate"><span class="text-gray-400 text-xs">#{{ question.skill_id }}</span> {{ question.skill_title || '' }}</div>
                  </td>
                  <td class="px-4 py-4 whitespace-nowrap text-sm">
                    <span class="px-2 py-1 text-xs font-medium rounded-full"
                      :class="{
                        'bg-blue-100 text-blue-800': question.type === 'MCQ',
                        'bg-green-100 text-green-800': question.type === 'NUMERIC',
                        'bg-purple-100 text-purple-800': question.type === 'TEXT',
                        'bg-yellow-100 text-yellow-800': question.type === 'MULTI_SELECT',
                        'bg-red-100 text-red-800': question.type === 'INTERACTIVE',
                        'bg-indigo-100 text-indigo-800': question.type === 'PLUGIN',
                      }">{{ question.type }}</span>
                  </td>
                  <td class="px-4 py-4 text-sm text-gray-900 max-w-xs"><div class="truncate">{{ question.prompt || '(Сұрақ жоқ)' }}</div></td>
                  <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">{{ question.level }}</td>
                  <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-400">{{ formatDate(question.created_at) }}</td>
                  <td class="px-4 py-4 whitespace-nowrap text-right">
                    <Button @click="confirmDeleteQ(question)" variant="outline" :loading="deletingQId === question.id"
                      class="text-red-600 hover:text-red-800 hover:bg-red-50 text-xs">Жою</Button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div v-if="totalQuestions > pageSize" class="mt-6 flex items-center justify-between">
            <div class="text-sm text-gray-600">Бет {{ currentPage }} / {{ totalPages }}</div>
            <div class="flex gap-2">
              <Button @click="currentPage = Math.max(1, currentPage - 1); loadQuestions()" variant="outline" :disabled="currentPage === 1">← Алдыңғы</Button>
              <Button @click="currentPage = Math.min(totalPages, currentPage + 1); loadQuestions()" variant="outline" :disabled="currentPage === totalPages">Келесі →</Button>
            </div>
          </div>
        </div>
      </div>
    </main>
    <Footer />


    <!-- Edit Skill Modal -->
    <EditSkillModal :isVisible="!!skillToEdit" :skill="skillToEdit" @close="skillToEdit = null" @save="handleEditSave" />

    <!-- Delete Skill Confirmation -->
    <Modal :isOpen="!!skillToDelete" @close="skillToDelete = null" title="Тестті жою" :showClose="true">
      <template #content>
        <p class="text-gray-700 mb-4">«<strong>{{ skillToDelete?.title }}</strong>» тестін жойғыңыз келе ме?</p>
        <p class="text-sm text-red-600">Бұл әрекетті қайтару мүмкін емес!</p>
      </template>
      <template #actions>
        <Button v-if="skillToDelete" @click="handleDeleteSkill" variant="primary" :loading="deletingSkillId === skillToDelete.id" class="bg-red-600 hover:bg-red-700">Иә, жою</Button>
        <Button @click="skillToDelete = null" variant="outline">Болдырмау</Button>
      </template>
    </Modal>

    <!-- Delete Question Confirmation -->
    <Modal :isOpen="!!questionToDelete" @close="questionToDelete = null" title="Сұрақты жою" :showClose="true">
      <template #content>
        <p class="text-gray-700 mb-4">Бұл сұрақты жойғыңыз келе ме?</p>
        <div v-if="questionToDelete" class="bg-gray-50 p-3 rounded mb-3 text-sm">
          <p><strong>ID:</strong> {{ questionToDelete.id }}</p>
          <p><strong>Тип:</strong> {{ questionToDelete.type }}</p>
          <p class="truncate"><strong>Сұрақ:</strong> {{ questionToDelete.prompt || '(Сұрақ жоқ)' }}</p>
        </div>
        <p class="text-sm text-red-600">Бұл әрекетті қайтару мүмкін емес!</p>
      </template>
      <template #actions>
        <Button v-if="questionToDelete" @click="handleDeleteQ" variant="primary" :loading="deletingQId === questionToDelete.id" class="bg-red-600 hover:bg-red-700">Иә, жою</Button>
        <Button @click="questionToDelete = null" variant="outline">Болдырмау</Button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCatalogStore } from '@/stores/catalog'
import { adminApi, type QuestionListItem } from '@/api/admin'
import { catalogApi } from '@/api/catalog'
import { useRouter } from 'vue-router'
import { usePracticeStore } from '@/stores/practice'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import Modal from '@/components/ui/Modal.vue'
import EditSkillModal from '@/components/catalog/EditSkillModal.vue'
import type { SkillListItem } from '@/types/api'

const authStore = useAuthStore()
const catalogStore = useCatalogStore()
const practiceStore = usePracticeStore()
const router = useRouter()

const activeTab = ref<'skills' | 'questions'>('skills')
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

// ==================== SKILLS ====================
const loadingSkills = ref(false)
const skillsList = ref<SkillListItem[]>([])
const skillToEdit = ref<SkillListItem | null>(null)
const skillToDelete = ref<SkillListItem | null>(null)
const deletingSkillId = ref<number | null>(null)
const skillSearch = ref('')
const skillFilterGradeId = ref<number | null>(null)
const skillFilterTopicId = ref<number | null>(null)

const grades = computed(() => catalogStore.grades)
const themes = computed(() => catalogStore.topics.filter(t => !t.parent_id))

const filteredSkills = computed(() => {
  let result = skillsList.value
  if (skillSearch.value) {
    const q = skillSearch.value.toLowerCase()
    result = result.filter(s => s.title.toLowerCase().includes(q) || s.code.toLowerCase().includes(q))
  }
  if (skillFilterGradeId.value) {
    result = result.filter(s => s.grade_id === skillFilterGradeId.value)
  }
  if (skillFilterTopicId.value) {
    const subIds = catalogStore.topics.filter(t => t.parent_id === skillFilterTopicId.value).map(t => t.id)
    const allIds = [skillFilterTopicId.value, ...subIds]
    result = result.filter(s => s.topic_id && allIds.includes(s.topic_id))
  }
  return result
})

const getGradeName = (gradeId: number): string => {
  const g = grades.value.find(g => g.id === gradeId)
  return g ? g.title : `ID: ${gradeId}`
}

const loadSkills = async () => {
  loadingSkills.value = true
  try {
    // Use catalog API (public) to list all skills
    const response = await catalogApi.getSkills({ page_size: 500 })
    if (response.data) skillsList.value = response.data as SkillListItem[]
  } catch (err: unknown) {
    console.error('Failed to load skills:', err)
    error.value = 'Тесттерді жүктеу қатесі'
  } finally {
    loadingSkills.value = false
  }
}

const navigateToSkill = async (skillId: number) => {
  try {
    const session = await practiceStore.createSession(skillId)
    if (session?.id) {
      router.push({ name: 'practice', params: { sessionId: session.id } })
    } else {
      error.value = 'Сессияны құру мүмкін болмады'
    }
  } catch (err) {
    console.error('Failed to create session:', err)
    error.value = 'Тестті ашу қатесі'
  }
}

const editFromModal = (skill: SkillListItem) => {
  skillToEdit.value = skill
}

const handleEditSave = async () => {
  await loadSkills()
  successMessage.value = 'Тест сәтті өзгертілді!'
  setTimeout(() => { successMessage.value = null }, 3000)
}

const confirmDeleteSkill = (skill: SkillListItem) => {
  skillToDelete.value = skill
}

const handleDeleteSkill = async () => {
  if (!skillToDelete.value) return
  deletingSkillId.value = skillToDelete.value.id
  try {
    await adminApi.deleteSkill(skillToDelete.value.id)
    successMessage.value = `«${skillToDelete.value.title}» сәтті жойылды!`
    skillToDelete.value = null
    await loadSkills()
    setTimeout(() => { successMessage.value = null }, 3000)
  } catch (err: unknown) {
    const errorResponse = err as { response?: { data?: { error?: { message?: string } } } }
    error.value = errorResponse.response?.data?.error?.message || 'Жою қатесі'
    skillToDelete.value = null
  } finally {
    deletingSkillId.value = null
  }
}

// ==================== QUESTIONS ====================
const loadingQ = ref(false)
const questionsList = ref<QuestionListItem[]>([])
const totalQuestions = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)
const questionToDelete = ref<QuestionListItem | null>(null)
const deletingQId = ref<number | null>(null)
const filters = ref({ skill_id: undefined as number | undefined, search: '', sort_order: 'desc' as 'asc' | 'desc' })

const totalPages = computed(() => Math.ceil(totalQuestions.value / pageSize.value))

const formatDate = (dateStr: string | null | undefined): string => {
  if (!dateStr) return '-'
  try { return new Date(dateStr).toLocaleDateString('kk-KZ', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) }
  catch { return '-' }
}

const loadQuestions = async () => {
  loadingQ.value = true
  error.value = null
  try {
    const params: Record<string, string | number> = { page: currentPage.value, page_size: pageSize.value, sort_order: filters.value.sort_order }
    if (filters.value.skill_id) params.skill_id = filters.value.skill_id
    if (filters.value.search?.trim()) params.search = filters.value.search.trim()
    const response = await adminApi.listQuestions(params)
    if (response.data) {
      questionsList.value = response.data
      totalQuestions.value = (response.meta && 'total' in response.meta) ? response.meta.total as number : response.data.length
    }
  } catch (err: unknown) {
    const apiError = err as { response?: { status?: number, data?: { error?: { message?: string } } } }
    if (apiError.response?.status === 401) { router.push({ name: 'login' }) }
    else { error.value = apiError.response?.data?.error?.message || 'Сұрақтарды жүктеу қатесі' }
  } finally { loadingQ.value = false }
}

const resetFilters = () => {
  filters.value = { skill_id: undefined, search: '', sort_order: 'desc' }
  currentPage.value = 1
  loadQuestions()
}

const confirmDeleteQ = (q: QuestionListItem) => { questionToDelete.value = q }

const handleDeleteQ = async () => {
  if (!questionToDelete.value) return
  deletingQId.value = questionToDelete.value.id
  try {
    await adminApi.deleteQuestion(questionToDelete.value.id)
    successMessage.value = `Сұрақ ID ${questionToDelete.value.id} сәтті жойылды!`
    questionToDelete.value = null
    await loadQuestions()
    setTimeout(() => { successMessage.value = null }, 5000)
  } catch (err: unknown) {
    const apiError = err as { response?: { data?: { error?: { message?: string } } } }
    error.value = apiError.response?.data?.error?.message || 'Сұрақты жою қатесі'
    questionToDelete.value = null
  } finally { deletingQId.value = null }
}

// ==================== INIT ====================
onMounted(async () => {
  if (!authStore.isAuthenticated || authStore.user?.role !== 'ADMIN') {
    router.push({ name: 'home' })
    return
  }
  await Promise.all([
    catalogStore.getGrades(),
    catalogStore.getTopics(),
    loadSkills(),
    loadQuestions()
  ])
})
</script>

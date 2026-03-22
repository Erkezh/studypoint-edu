<template>
  <div class="analytics-page">
    <Header />

    <!-- IXL-style Header with Tabs -->
    <div class="analytics-header">
      <nav class="analytics-tabs">
        <div v-for="tab in tabs" :key="tab.id" class="tab-item-group"
             @mouseenter="hoverTab = tab.id" @mouseleave="hoverTab = null">
          <button @click="tab.dropdown ? (activeTab = tab.dropdown[0].id) : (activeTab = tab.id)"
            :class="['tab-item', { active: activeTab === tab.id || (tab.dropdown && tab.dropdown.some(d => d.id === activeTab)) }]">
            <span class="tab-icon">
              <svg v-if="tab.id === 'summary' && !isTeacher" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
              <svg v-else-if="tab.id === 'students_dropdown' && isTeacher" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
              <svg v-else-if="tab.id === 'usage'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <svg v-else-if="tab.id === 'trouble'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
              <svg v-else-if="tab.id === 'scores'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" /></svg>
              <svg v-else-if="tab.id === 'questions'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
              <svg v-else-if="tab.id === 'progress'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            </span>
            {{ tab.label }}
            <svg v-if="tab.dropdown" class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </button>
          
          <div v-if="tab.dropdown && hoverTab === tab.id" class="tab-dropdown">
            <button v-for="sub in tab.dropdown" :key="sub.id" 
              @click.stop="activeTab = sub.id; hoverTab = null"
              :class="['dropdown-item', { active: activeTab === sub.id }]">
              {{ sub.label }}
            </button>
          </div>
        </div>
      </nav>
    </div>

    <div v-if="activeTab !== 'scores'" class="filters-bar">
      <!-- Teacher: Student Picker -->
      <!-- Teacher: Student Picker moved to content -->
      <div class="filter-group grade-range-filter">
        <label @click="toggleGradeDropdown" class="filter-label clickable">
          СЫНЫП ДЕҢГЕЙІ: {{ gradeRangeLabel }}
          <svg class="dropdown-arrow w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
        </label>
        <div v-if="showGradeDropdown" class="grade-dropdown-popup">
          <p class="dropdown-title">Осы сыныптардағы дағдыларды көрсету:</p>
          <div class="grade-range-selectors">
            <select v-model="gradeFrom" class="filter-select small">
              <option :value="-1">Pre-K</option>
              <option :value="0">0</option>
              <option v-for="n in 12" :key="n" :value="n">{{ n }}</option>
            </select>
            <span class="range-separator">-</span>
            <select v-model="gradeTo" class="filter-select small">
              <option :value="-1">Pre-K</option>
              <option :value="0">0</option>
              <option v-for="n in 12" :key="n" :value="n">{{ n }}</option>
            </select>
          </div>
          <button @click="applyGradeFilter" class="apply-btn">Дайын</button>
        </div>
      </div>
      <div class="filter-group date-range-filter">
        <label @click="toggleDateDropdown" class="filter-label clickable">
          УАҚЫТ АРАЛЫҒЫ: {{ dateRangeLabel }}
          <svg class="dropdown-arrow w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
        </label>
        <div v-if="showDateDropdown" class="date-dropdown-popup">
          <button
            v-for="option in dateOptions"
            :key="option.id"
            @click="selectDateRange(option.id)"
            :class="['date-option', { active: selectedDateOption === option.id }]"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
    </div>



    <main class="analytics-content">
      <!-- Loading State -->
      <div v-if="analyticsStore.loading" class="loading-state">
        <div class="spinner"></div>
        <p>Жүктелуде...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="analyticsStore.error" class="error-state">
        <p class="error-title">Талдауды жүктеу қатесі:</p>
        <p>{{ analyticsStore.error }}</p>
      </div>

      <!-- Teacher Needs Selection State -->
      <div v-else-if="isTeacher && !selectedStudentId && activeTab !== 'students_quickview'" class="empty-state teacher-select-prompt">
        <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
        <h3 class="text-xl font-medium text-gray-700 mb-2">Оқушыны таңдаңыз</h3>
        
        <div class="student-carousel-container mt-6">
          <button @click="prevStudent" class="carousel-arrow" :disabled="teacherStudents.length === 0">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
          </button>
          <div class="carousel-select-wrapper">
            <span class="carousel-label">ОҚУШЫ:</span>
            <select v-model="selectedStudentId" @change="onStudentChange" class="carousel-select">
              <option value="" disabled>Оқушыны таңдаңыз...</option>
              <option v-for="s in teacherStudents" :key="s.id" :value="s.id">{{ s.full_name }}</option>
            </select>
          </div>
          <button @click="nextStudent" class="carousel-arrow" :disabled="teacherStudents.length === 0">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </button>
        </div>
      </div>

      <div v-else>
        <!-- Teacher Student Carousel for active views (Usage, Summary) - HIDDEN on Quickview -->
        <div v-if="isTeacher && selectedStudentId && activeTab !== 'students_quickview'" class="student-carousel-container active-view-carousel">
          <button @click="prevStudent" class="carousel-arrow">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
          </button>
          <div class="carousel-select-wrapper">
            <span class="carousel-label">ОҚУШЫ:</span>
            <select v-model="selectedStudentId" @change="onStudentChange" class="carousel-select">
              <option v-for="s in teacherStudents" :key="s.id" :value="s.id">{{ s.full_name }}</option>
            </select>
          </div>
          <button @click="nextStudent" class="carousel-arrow">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </button>
        </div>
        <div v-if="activeTab === 'students_quickview'" class="quickview-container">
          <div class="quickview-header">
            <h2 class="quickview-title">ОҚУШЫЛАРДЫҢ ҚЫСҚАША КӨРІНІСІ
              <button class="print-btn" title="Print">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" /></svg>
              </button>
            </h2>
            <div class="quickview-student-select">
              <select :value="''" @change="onQuickviewStudentChange($event)" class="quickview-select">
                <option value="" disabled>Белгілі бір оқушыны іздеп жүрсіз бе?</option>
                <option v-for="s in teacherStudents" :key="s.id" :value="s.id">{{ s.full_name }}</option>
              </select>
            </div>
          </div>
          
          <div class="mt-8">
            <UsageTab 
              :grade-from="gradeFrom" 
              :grade-to="gradeTo" 
              :date-range="dateRange" 
              :period="selectedDateOption" 
            />
          </div>
        </div>

        <SummaryTab v-else-if="activeTab === 'summary'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :date-range="dateRange" :skill-names="skillNames" />

        <UsageTab v-else-if="activeTab === 'usage'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :date-range="dateRange" :period="selectedDateOption" />

        <TroubleTab v-else-if="activeTab === 'trouble'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :date-range="dateRange" />

        <ScoresTab v-else-if="activeTab === 'scores'" />

        <QuestionsTab v-else-if="activeTab === 'questions'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :date-range="dateRange" />

        <ProgressTab v-else-if="activeTab === 'progress'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :skill-names="skillNames" :date-range="dateRange" />
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref, watch } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { useAuthStore } from '@/stores/auth'
import { useTeacherStore } from '@/stores/teacher'
import { storeToRefs } from 'pinia'
import { teacherApi } from '@/api/teacher'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import SummaryTab from '@/components/analytics/SummaryTab.vue'
import UsageTab from '@/components/analytics/UsageTab.vue'
import ScoresTab from '@/components/analytics/ScoresTab.vue'
import TroubleTab from '@/components/analytics/TroubleTab.vue'
import QuestionsTab from '@/components/analytics/QuestionsTab.vue'
import ProgressTab from '@/components/analytics/ProgressTab.vue'

const analyticsStore = useAnalyticsStore()
const authStore = useAuthStore()
const teacherStore = useTeacherStore()
const { students: teacherStudents } = storeToRefs(teacherStore)

const isTeacher = computed(() => authStore.isTeacher)

/* === Local Storage Persistence === */
const SAVED_STATE_KEY = 'analytics_view_state'
const loadState = () => {
  try {
    const saved = localStorage.getItem(SAVED_STATE_KEY)
    return saved ? JSON.parse(saved) : {}
  } catch {
    return {}
  }
}
const initialState = loadState()

// Teacher student selection — only restore from localStorage if user is a teacher
const selectedStudentId = ref(initialState.selectedStudentId || '')
const studentAnalyticsLoading = ref(false)
const hoverTab = ref<string | null>(null)

// Carousel Logic
const prevStudent = () => {
  if (teacherStudents.value.length === 0) return
  const currentIndex = teacherStudents.value.findIndex((s: { id: string }) => s.id === selectedStudentId.value)
  if (currentIndex <= 0) {
    // Wrap to end or stay at 0
    selectedStudentId.value = teacherStudents.value[teacherStudents.value.length - 1].id
  } else {
    selectedStudentId.value = teacherStudents.value[currentIndex - 1].id
  }
  onStudentChange()
}

const nextStudent = () => {
  if (teacherStudents.value.length === 0) return
  const currentIndex = teacherStudents.value.findIndex((s: { id: string }) => s.id === selectedStudentId.value)
  if (currentIndex === -1 || currentIndex === teacherStudents.value.length - 1) {
    // Wrap to start
    selectedStudentId.value = teacherStudents.value[0].id
  } else {
    selectedStudentId.value = teacherStudents.value[currentIndex + 1].id
  }
  onStudentChange()
}

const tabsThatNeedQuestionData = new Set(['usage', 'trouble', 'questions', 'progress', 'students_quickview'])
const ownQuestionsLoaded = ref(false)

const shouldLoadQuestionData = () => {
  return tabsThatNeedQuestionData.has(activeTab.value) || selectedDateOption.value !== 'all'
}

// Load own analytics (for any user)
const loadOwnAnalytics = async (includeQuestions = shouldLoadQuestionData()) => {
  analyticsStore.loading = true
  try {
    const requests: Promise<unknown>[] = [
      analyticsStore.getOverview(true),
      analyticsStore.getSkills(true),
    ]

    if (includeQuestions) {
      requests.push(analyticsStore.getAllQuestions(true))
    } else {
      analyticsStore.allQuestions = []
    }

    await Promise.all(requests)
    ownQuestionsLoaded.value = includeQuestions
  } finally {
    analyticsStore.loading = false
  }
}

// Load teacher aggregate analytics
const loadTeacherQuickviewAnalytics = async () => {
  analyticsStore.loading = true
  studentAnalyticsLoading.value = true
  try {
    const resp = await teacherApi.getTeacherQuickviewAnalytics()
    const data = resp.data.data as { overview: Record<string, unknown>; skills: Array<Record<string, unknown>>; all_questions: Array<Record<string, unknown>> }
    analyticsStore.overview = data.overview as typeof analyticsStore.overview
    analyticsStore.skills = (data.skills || []) as typeof analyticsStore.skills
    analyticsStore.allQuestions = (data.all_questions || []) as typeof analyticsStore.allQuestions
    analyticsStore.error = null
  } catch (err: unknown) {
    const e = err as { response?: { data?: { message?: string } } }
    analyticsStore.error = e.response?.data?.message || 'Оқушылардың жалпы аналитикасын жүктеу мүмкін болмады'
  } finally {
    analyticsStore.loading = false
    studentAnalyticsLoading.value = false
  }
}

const onStudentChange = async () => {
  if (!selectedStudentId.value || !isTeacher.value) {
    selectedStudentId.value = ''
    if (isTeacher.value && activeTab.value === 'students_quickview') {
      await loadTeacherQuickviewAnalytics()
    } else {
      await loadOwnAnalytics()
    }
    return
  }

  // Teacher selected a specific student
  studentAnalyticsLoading.value = true
  analyticsStore.loading = true
  try {
    const includeQuestions = shouldLoadQuestionData()
    const resp = await teacherApi.getStudentAnalytics(selectedStudentId.value, includeQuestions)
    const data = resp.data.data as { overview: Record<string, unknown>; skills: Array<Record<string, unknown>>; all_questions: Array<Record<string, unknown>> }
    // Inject student data into the shared store so all tabs use it
    analyticsStore.overview = data.overview as typeof analyticsStore.overview
    analyticsStore.skills = (data.skills || []) as typeof analyticsStore.skills
    analyticsStore.allQuestions = (includeQuestions ? (data.all_questions || []) : []) as typeof analyticsStore.allQuestions
    analyticsStore.error = null
  } catch (err: unknown) {
    const e = err as { response?: { data?: { message?: string } } }
    analyticsStore.error = e.response?.data?.message || 'Оқушы аналитикасын жүктеу мүмкін болмады'
  } finally {
    analyticsStore.loading = false
    studentAnalyticsLoading.value = false
  }
}

const onQuickviewStudentChange = async (event: Event) => {
  const target = event.target as HTMLSelectElement
  if (target.value) {
    selectedStudentId.value = target.value
    activeTab.value = 'usage'
    await onStudentChange()
  }
}

interface TabItem {
  id: string
  label: string
  dropdown?: { id: string; label: string }[]
}

// Tab configuration
const tabs = computed<TabItem[]>(() => {
  if (isTeacher.value) {
    return [
      {
        id: 'students_dropdown',
        label: 'Оқушылар',
        dropdown: [
          { id: 'students_quickview', label: 'Оқушылардың қысқаша көрінісі' },
          { id: 'usage', label: 'Оқушының қолдануы' },
          { id: 'summary', label: 'Оқушының қорытындысы' },
        ]
      },
      { id: 'trouble', label: 'Қиындықтар' },
      { id: 'scores', label: 'Ұпайлар' },
      { id: 'questions', label: 'Сұрақтар' },
      { id: 'progress', label: 'Прогресс' },
    ]
  }
  return [
    { id: 'summary', label: 'Қорытынды' },
    { id: 'usage', label: 'Қолдану' },
    { id: 'trouble', label: 'Қиындықтар' },
    { id: 'scores', label: 'Ұпайлар' },
    { id: 'questions', label: 'Сұрақтар' },
    { id: 'progress', label: 'Прогресс' },
  ]
})

// Initialize active tab based on role and stored state
const defaultTeacherTab = 'students_quickview'
const activeTab = ref<string>(initialState.activeTab || (isTeacher.value ? defaultTeacherTab : 'summary'))
const gradeFrom = ref<number>(initialState.gradeFrom !== undefined ? initialState.gradeFrom : -1)
const gradeTo = ref<number>(initialState.gradeTo !== undefined ? initialState.gradeTo : 12)
const showGradeDropdown = ref<boolean>(false)
const skillNames = computed(() => {
  return new Map(
    analyticsStore.skills.map(skill => [
      Number(skill.skill_id),
      (skill as Record<string, unknown>).skill_name as string || `Дағды ${skill.skill_id}`,
    ])
  )
})

// Grade range label for display
const gradeRangeLabel = computed(() => {
  const formatGrade = (g: number) => g === -1 ? 'Pre-K' : g
  if (gradeFrom.value === -1 && gradeTo.value === 12) {
    return 'Барлық сыныптар'
  }
  if (gradeFrom.value === gradeTo.value) {
    return `${formatGrade(gradeFrom.value)} сынып`
  }
  return `${formatGrade(gradeFrom.value)} - ${formatGrade(gradeTo.value)} сынып`
})

const toggleGradeDropdown = () => {
  showGradeDropdown.value = !showGradeDropdown.value
}

const applyGradeFilter = () => {
  if (gradeFrom.value > gradeTo.value) {
    const temp = gradeFrom.value
    gradeFrom.value = gradeTo.value
    gradeTo.value = temp
  }
  showGradeDropdown.value = false
}

// Date Range Logic
const dateRangeLabel = ref<string>('Барлық уақыт')
const showDateDropdown = ref<boolean>(false)
const selectedDateOption = ref<string>(initialState.selectedDateOption || 'all')

const dateRange = ref<{ start: Date | null; end: Date | null }>({
  start: null,
  end: null
})

const dateOptions = [
  { id: 'today', label: 'Бүгін' },
  { id: 'yesterday', label: 'Кеше' },
  { id: 'week', label: 'Осы апта' },
  { id: 'last7', label: 'Соңғы 7 күн' },
  { id: 'month', label: 'Осы ай' },
  { id: 'last30', label: 'Соңғы 30 күн' },
  { id: 'year', label: 'Осы жыл' },
  { id: 'all', label: 'Барлық уақыт' },
]

const toggleDateDropdown = () => {
  showDateDropdown.value = !showDateDropdown.value
}

const selectDateRange = (optionId: string) => {
  selectedDateOption.value = optionId
  const option = dateOptions.find(o => o.id === optionId)
  dateRangeLabel.value = option ? option.label : 'Теңшелетін'
  showDateDropdown.value = false

  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())

  switch (optionId) {
    case 'today':
      dateRange.value = { start: today, end: new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59) }
      break
    case 'yesterday':
      const yesterday = new Date(today)
      yesterday.setDate(yesterday.getDate() - 1)
      const yesterdayEnd = new Date(yesterday)
      yesterdayEnd.setHours(23, 59, 59)
      dateRange.value = { start: yesterday, end: yesterdayEnd }
      break
    case 'week':
      // This week (starting Monday)
      const day = today.getDay() || 7 // 1 (Mon) to 7 (Sun)
      const monday = new Date(today)
      monday.setHours(0, 0, 0, 0)
      monday.setDate(monday.getDate() - day + 1)
      dateRange.value = { start: monday, end: new Date() }
      break
    case 'last7':
      const last7 = new Date(today)
      last7.setDate(last7.getDate() - 6)
      dateRange.value = { start: last7, end: new Date() }
      break
    case 'month':
      const firstDayMonth = new Date(today.getFullYear(), today.getMonth(), 1)
      dateRange.value = { start: firstDayMonth, end: new Date() }
      break
    case 'last30':
      const last30 = new Date(today)
      last30.setDate(last30.getDate() - 29)
      dateRange.value = { start: last30, end: new Date() }
      break
    case 'year':
      const firstDayYear = new Date(today.getFullYear(), 0, 1)
      dateRange.value = { start: firstDayYear, end: new Date() }
      break
    case 'all':
    default:
      dateRange.value = { start: null, end: null }
      break
  }
}

// Watch state changes and save to local storage
watch(
  [activeTab, gradeFrom, gradeTo, selectedDateOption, selectedStudentId],
  () => {
    localStorage.setItem(SAVED_STATE_KEY, JSON.stringify({
      activeTab: activeTab.value,
      gradeFrom: gradeFrom.value,
      gradeTo: gradeTo.value,
      selectedDateOption: selectedDateOption.value,
      selectedStudentId: selectedStudentId.value
    }))
  },
  { deep: true }
)

// Automatically load quickview data when returning to the quickview tab
watch(activeTab, async (newVal) => {
  if (isTeacher.value && newVal === 'students_quickview') {
    selectedStudentId.value = ''
    await loadTeacherQuickviewAnalytics()
    return
  }

  if (isTeacher.value && selectedStudentId.value && shouldLoadQuestionData() && analyticsStore.allQuestions.length === 0) {
    await onStudentChange()
    return
  }

  if (!isTeacher.value && shouldLoadQuestionData() && !ownQuestionsLoaded.value) {
    analyticsStore.loading = true
    try {
      await analyticsStore.getAllQuestions(true)
      ownQuestionsLoaded.value = true
    } finally {
      analyticsStore.loading = false
    }
  }
})

watch(selectedDateOption, async () => {
  if (isTeacher.value && selectedStudentId.value && shouldLoadQuestionData() && analyticsStore.allQuestions.length === 0) {
    await onStudentChange()
    return
  }

  if (!isTeacher.value && shouldLoadQuestionData() && !ownQuestionsLoaded.value) {
    analyticsStore.loading = true
    try {
      await analyticsStore.getAllQuestions(true)
      ownQuestionsLoaded.value = true
    } finally {
      analyticsStore.loading = false
    }
  }
})

onMounted(async () => {
  // Initialize date range from saved state
  selectDateRange(selectedDateOption.value)

  // If teacher, load student list for the picker
  if (isTeacher.value && teacherStudents.value.length === 0) {
    await teacherStore.fetchStudents()
  }
  
  try {
    if (isTeacher.value && selectedStudentId.value && activeTab.value !== 'students_quickview') {
      // Teacher has a student selected and specific tab — load that student's data
      await onStudentChange()
    } else if (isTeacher.value && activeTab.value === 'students_quickview') {
      // Teacher is on quickview page - load aggregate data
      await loadTeacherQuickviewAnalytics()
    } else {
      // Student or teacher with no selection — load own data
      await loadOwnAnalytics()
    }
  } catch (err) {
    console.error('Failed to load analytics:', err)
  }
})
</script>

<style scoped>
.analytics-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* Header & Tabs */
.analytics-header {
  background: linear-gradient(135deg, #00BCD4 0%, #00ACC1 100%);
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.analytics-tabs {
  display: flex;
  gap: 0;
  max-width: 1200px;
  margin: 0 auto;
  overflow: visible;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 24px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  border-bottom: 3px solid transparent;
}

.tab-item:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.tab-item.active {
  color: white;
  background: rgba(255, 255, 255, 0.15);
  border-bottom-color: white;
}

.tab-icon {
  font-size: 16px;
}

/* Student Options Carousel */
.student-carousel-container {
  display: flex;
  align-items: center;
  gap: 16px;
  max-width: fit-content;
}

.student-carousel-container.mt-6 {
  margin-top: 24px;
  justify-content: center;
  margin-left: auto;
  margin-right: auto;
}

.active-view-carousel {
  margin-bottom: 24px;
}

.carousel-arrow {
  background: transparent;
  border: none;
  color: #00BCD4;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.carousel-arrow:hover:not(:disabled) {
  background-color: #e0f7fa;
}

.carousel-arrow:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.carousel-select-wrapper {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 16px;
  gap: 8px;
}

.carousel-label {
  font-size: 12px;
  font-weight: 700;
  color: #888;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.carousel-select {
  border: none;
  background: transparent;
  font-size: 16px;
  color: #555;
  font-weight: 500;
  cursor: pointer;
  outline: none;
  min-width: 250px;
  appearance: none;
  padding-right: 24px;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%22%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23999%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.4-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right center;
  background-size: 12px auto;
}

.carousel-select:hover {
  text-decoration: underline;
}

/* Quickview Styles */
.quickview-container {
  padding: 24px 0;
}

.quickview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.quickview-title {
  font-size: 28px;
  font-weight: 300;
  color: #555;
  display: flex;
  align-items: center;
  gap: 12px;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.quickview-student-select {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 4px;
  gap: 12px;
}

.quickview-select-label {
  font-size: 14px;
  color: #888;
  font-style: italic;
}

.quickview-select {
  border: none;
  background: transparent;
  font-size: 14px;
  color: #333;
  font-weight: 500;
  cursor: pointer;
  outline: none;
  min-width: 200px;
  appearance: none;
  padding-right: 24px;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%22%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23999%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.4-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right center;
  background-size: 12px auto;
}

/* Filters */
.filters-bar {
  display: flex;
  gap: 24px;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  max-width: 1200px;
  margin: 0 auto;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
}

.filter-select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  background: white;
  cursor: pointer;
}

.filter-select.small {
  padding: 8px 16px;
  min-width: 70px;
}

/* Grade Range Filter */
.grade-range-filter {
  position: relative;
}

.filter-label.clickable {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  color: #00ACC1;
  font-weight: 600;
}

.filter-label.clickable:hover {
  background: #f5f5f5;
}

.dropdown-arrow {
  font-size: 10px;
  color: #666;
}

.grade-dropdown-popup {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 16px;
  z-index: 100;
  min-width: 240px;
  margin-top: 4px;
}

.dropdown-title {
  font-size: 13px;
  color: #666;
  margin: 0 0 12px 0;
}

.grade-range-selectors {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.range-separator {
  font-size: 16px;
  color: #666;
}

.apply-btn {
  display: block;
  width: 100%;
  padding: 8px 16px;
  background: transparent;
  color: #00ACC1;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
}

.apply-btn:hover {
  color: #00838F;
}

/* Content */
.analytics-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* Loading & Error */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e0e0e0;
  border-top-color: #00BCD4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-state {
  background: #ffebee;
  border: 1px solid #f44336;
  border-radius: 8px;
  padding: 20px;
  color: #c62828;
}

.error-title {
  font-weight: 600;
  margin-bottom: 8px;
}

/* Date Range Filter */
.date-range-filter {
  position: relative;
}

.date-dropdown-popup {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 8px 0;
  z-index: 100;
  min-width: 200px;
  margin-top: 4px;
}

.date-option {
  display: block;
  width: 100%;
  text-align: left;
  padding: 10px 16px;
  background: transparent;
  border: none;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: background-color 0.1s;
}

.date-option:hover {
  background-color: #f5f5f5;
}

.date-option.active {
  color: #00ACC1;
  background-color: #e0f7fa;
  font-weight: 500;
}

.date-option.custom {
  border-top: 1px solid #eee;
  margin-top: 4px;
  padding-top: 12px;
}

/* Dropdown Menu */
.tab-item-group {
  position: relative;
  display: flex;
}

.tab-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  min-width: 240px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  border-radius: 0 0 8px 8px;
  overflow: hidden;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  border: 1px solid #eee;
  border-top: none;
}

.dropdown-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 14px 20px;
  border: none;
  background: white;
  color: #555;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.dropdown-item:hover {
  background: #f8f9fa;
  color: #333;
}

.dropdown-item.active {
  background: #e0f7fa;
  color: #00838F;
  border-left: 3px solid #00ACC1;
  padding-left: 17px;
}

/* Responsive */
@media (max-width: 768px) {
  .filters-bar {
    flex-direction: column;
    gap: 12px;
  }

  .date-dropdown-popup {
    right: auto;
    left: 0;
  }
}

/* ===== PRINT STYLES ===== */
@media print {
  /* Hide navigation, filters and footer */
  :deep(header),
  :deep(nav),
  :deep(footer),
  .analytics-header,
  .filters-bar,
  .tab-icon {
    display: none !important;
  }

  /* Reset page background */
  .analytics-page {
    background: white !important;
    min-height: unset;
  }

  /* Full-width content, no padding trimming */
  .analytics-content {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  /* Notebook-style: clean white, no shadows, pages break nicely */
  * {
    box-shadow: none !important;
    text-shadow: none !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  /* Page setup */
  @page {
    size: A4 portrait;
    margin: 15mm 15mm 15mm 15mm;
  }

  /* Avoid breaking inside cards/sections */
  section,
  .card,
  table,
  tr {
    page-break-inside: avoid;
  }
}
</style>

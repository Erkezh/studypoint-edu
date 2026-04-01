<template>
  <div class="teacher-dashboard">
    <Header />

    <!-- Sub-navigation tabs -->
    <div class="tabs-bar">
      <div class="tabs-inner">
        <div 
          v-for="tab in tabs" 
          :key="tab.key" 
          class="tab-item-group"
          @mouseenter="hoverTab = tab.key" 
          @mouseleave="hoverTab = null"
        >
          <button
            @click="tab.dropdown ? (activeTab = tab.dropdown[0].key) : (activeTab = tab.key)"
            class="tab-btn"
            :class="{ active: activeTab === tab.key || (tab.dropdown && tab.dropdown.some(d => d.key === activeTab)) }"
          >
            <component :is="tab.icon" class="tab-icon" />
            {{ tab.label }}
            <svg v-if="tab.dropdown" class="w-4 h-4 ml-1 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </button>

          <div v-if="tab.dropdown && hoverTab === tab.key" class="tab-dropdown">
            <button v-for="sub in tab.dropdown" :key="sub.key"
              @click.stop="activeTab = sub.key; hoverTab = null"
              :class="['dropdown-item', { active: activeTab === sub.key }]">
              {{ sub.label }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <main class="main-content">

      <!-- ===================== ВЗГЛЯНУТЬ ===================== -->
      <template v-if="activeTab === 'glance'">

        <!-- Loading -->
        <div v-if="loadingData" class="loading-state">
          <div class="spinner"></div>
          <p>Жүктелуде...</p>
        </div>

        <template v-else>
          <!-- Welcome -->
          <div class="welcome-row">
            <h1 class="welcome-title">
              Қош келдіңіз, {{ teacherName }}!
            </h1>
            <div class="student-selector">
              <select v-model="selectedStudentId" class="student-select">
                <option value="all">Барлық оқушылар</option>
                <option v-for="s in studentsBreakdown" :key="s.student_id" :value="s.student_id">
                  {{ s.full_name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Big blue stats strip -->
          <div class="blue-strip">
            <div class="blue-strip-inner">
              <span class="blue-strip-label">ОСЫ ЖЫЛЫ БІЗ</span>
              <span class="digit-row">
                <span
                  v-for="(d, i) in questionsDigits"
                  :key="i"
                  class="digit-box"
                >{{ d }}</span>
              </span>
              <span class="blue-strip-label">СҰРАҚҚА ЖАУАП БЕРДІК!</span>
            </div>
          </div>

          <!-- Two-column cards -->
          <div class="dashboard-cards">
            <!-- Skill progress -->
            <div class="card">
              <h2 class="card-title">Дағды прогресі</h2>
              <div class="mountain-area">
                <!-- Mountain SVG -->
                <svg viewBox="0 0 320 200" class="mountain-svg" preserveAspectRatio="xMidYMax meet">
                  <!-- Sky -->
                  <rect x="0" y="0" width="320" height="200" fill="#e8f4f8" rx="0"/>
                  <!-- Clouds -->
                  <ellipse cx="50" cy="40" rx="25" ry="10" fill="white" opacity="0.7"/>
                  <ellipse cx="70" cy="35" rx="20" ry="8" fill="white" opacity="0.6"/>
                  <ellipse cx="260" cy="30" rx="18" ry="7" fill="white" opacity="0.5"/>
                  <ellipse cx="280" cy="35" rx="22" ry="9" fill="white" opacity="0.6"/>
                  <!-- Back mountain -->
                  <polygon points="180,200 230,100 290,200" fill="#b8d4e3"/>
                  <polygon points="200,200 260,80 320,200" fill="#a3c4d6"/>
                  <!-- Main green mountain -->
                  <polygon points="40,200 160,55 280,200" fill="#8ec63f"/>
                  <!-- Mountain shading -->
                  <polygon points="160,55 220,140 280,200 160,200" fill="#7bb336" opacity="0.6"/>
                  <!-- Snow cap -->
                  <polygon points="160,55 145,85 155,80 165,90 180,82" fill="white"/>
                  <!-- Trees -->
                  <polygon points="80,200 95,165 110,200" fill="#5a9a20" opacity="0.7"/>
                  <polygon points="110,200 130,155 150,200" fill="#6aab28" opacity="0.6"/>
                  <polygon points="190,200 205,160 220,200" fill="#5a9a20" opacity="0.7"/>
                  <polygon points="220,200 240,170 260,200" fill="#6aab28" opacity="0.5"/>
                  <!-- Ground -->
                  <rect x="0" y="195" width="320" height="5" fill="#c5e1a5"/>
                </svg>

                <!-- Stats overlaid on left side -->
                <div class="mountain-stats">
                  <div class="stat-row stat-mastered">
                    <span class="stat-number">{{ currentMastered }}</span>
                    <span class="stat-line"></span>
                    <span class="stat-label">МЕҢГЕРІЛГЕН</span>
                  </div>
                  <div class="stat-row stat-proficient">
                    <span class="stat-number">{{ currentProficient }}</span>
                    <span class="stat-line"></span>
                    <span class="stat-label">ЖЕТІК</span>
                  </div>
                  <div class="stat-row stat-practiced">
                    <span class="stat-number">{{ currentSkillsPracticed }}</span>
                    <span class="stat-line"></span>
                    <span class="stat-label">ЖАТТЫҒЫЛҒАН</span>
                  </div>
                </div>
              </div>
              <div class="card-footer">
                <a href="#" class="card-footer-link">
                  🎯 Осы аптада {{ currentSkillsPracticedThisWeek }} дағды жаттықтырылды ›
                </a>
              </div>
            </div>

            <!-- Time spent -->
            <div class="card">
              <h2 class="card-title">Жұмсалған уақыт</h2>
              <div class="donut-area">
                <div class="donut-wrapper">
                  <svg viewBox="0 0 120 120" class="donut-svg">
                    <circle cx="60" cy="60" r="48" fill="none" stroke="#e8f0f4" stroke-width="14"/>
                    <circle
                      v-if="currentTotalTime > 0"
                      cx="60" cy="60" r="48"
                      fill="none"
                      stroke="#00bcd4"
                      stroke-width="14"
                      :stroke-dasharray="`${(currentTotalTime / Math.max(currentTotalTime, 1)) * 301.6} 301.6`"
                      stroke-linecap="round"
                      class="donut-arc"
                    />
                  </svg>
                  <div class="donut-center">
                    <span class="donut-value">{{ currentTimeFormatted }}</span>
                    <span class="donut-sub">ОСЫ ЖЫЛ</span>
                  </div>
                </div>
                <div class="donut-legend">
                  <div class="legend-item">
                    <span class="legend-dot" style="background: #0097a7;"></span>
                    МЕКТЕП
                  </div>
                  <div class="legend-item">
                    <span class="legend-dot" style="background: #4dd0e1;"></span>
                    ҮЙ
                  </div>
                </div>
              </div>
              <div class="card-footer">
                <a href="#" class="card-footer-link">
                  ⚡ Қазір StudyPoint-та {{ students.length }} оқушы ›
                </a>
              </div>
            </div>
          </div>

          <!-- Achievement summary footer -->
          <div class="achievement-footer">
            <a href="#" class="achievement-link">
              🏆 Жетістіктер қорытындысы ›
            </a>
          </div>

          <!-- Achievement summary footer -->
          <div class="achievement-footer">
            <a href="#" class="achievement-link">
              🏆 Жетістіктер қорытындысы ›
            </a>
          </div>
        </template>
      </template>

      <!-- ===================== ROSTER (ОҚУШЫЛАР ТІЗІМІ) ===================== -->
      <template v-if="activeTab === 'roster'">
        <div class="tools-section">
          <div class="tools-header">
            <div>
              <h1 class="tools-title">Оқушылар тізімі</h1>
              <p class="tools-subtitle">Барлық оқушылардың логині мен құпиясөзі осында</p>
            </div>
            <button @click="showAddModal = true" class="add-btn">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
              Оқушы қосу
            </button>
          </div>

          <div class="table-card">
            <div v-if="loadingStudents" class="table-loading">
              <div class="spinner"></div>
            </div>
            <div v-else-if="studentsError" class="table-error">{{ studentsError }}</div>
            <div v-else-if="students.length === 0" class="table-empty">
              <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              <p class="font-medium text-gray-500">Оқушылар жоқ</p>
              <p class="text-sm text-gray-400 mt-1">«Оқушы қосу» түймесін басыңыз</p>
            </div>
            <div v-else class="overflow-x-auto">
              <table class="roster-table">
                <thead>
                  <tr>
                    <th class="w-10">#</th>
                    <th>Аты-жөні</th>
                    <th>Сыныбы</th>
                    <th>Логин</th>
                    <th>Құпиясөз</th>
                    <th class="w-36">Әрекет</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(student, index) in students" :key="student.id">
                    <td class="text-gray-400">{{ index + 1 }}</td>
                    <td class="font-medium text-gray-900">{{ student.full_name }}</td>
                    <td class="text-gray-500">{{ student.grade_level ? `${student.grade_level} сынып` : '—' }}</td>
                    <td>
                      <span @click="copyToClipboard(student.username, student.id + '_u')" class="copy-badge copy-badge-blue" :title="'Көшіру'">
                        {{ student.username }}
                        <span v-if="copiedId === student.id + '_u'" class="copy-toast">Көшірілді ✓</span>
                      </span>
                    </td>
                    <td>
                      <span v-if="student.password && student.password !== '—'" @click="copyToClipboard(student.password!, student.id + '_p')" class="copy-badge copy-badge-green" :title="'Көшіру'">
                        {{ student.password }}
                        <span v-if="copiedId === student.id + '_p'" class="copy-toast">Көшірілді ✓</span>
                      </span>
                      <span v-else class="text-xs text-gray-400 italic">Тек жасағанда көрінеді</span>
                    </td>
                    <td>
                      <div class="action-btns">
                        <button @click="resetPassword(student)" :disabled="resettingId === student.id" class="action-link action-link-blue">
                          {{ resettingId === student.id ? 'Жасалуда...' : 'Жаңа пароль' }}
                        </button>
                        <button @click="confirmDelete(student)" :disabled="deletingId === student.id" class="action-link action-link-red">
                          {{ deletingId === student.id ? '...' : 'Өшіру' }}
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div class="table-foot">Барлығы {{ students.length }} оқушы</div>
            </div>
          </div>
          <div v-if="resetError" class="error-msg">{{ resetError }}</div>
        </div>
      </template>

      <!-- ===================== Құралдар ===================== -->
      <template v-if="activeTab === 'tools'">
        <div class="empty-tab">
          <div class="empty-icon">⚙️</div>
          <h2>Құралдар</h2>
          <p>Бұл бөлім әзірше бос. Жуық арада жаңа мүмкіндіктер қосылады.</p>
        </div>
      </template>

      <!-- ===================== КВИЗЫ ===================== -->
      <template v-if="activeTab === 'quizzes'">
        <div class="empty-tab">
          <div class="empty-icon">📝</div>
          <h2>Квизы</h2>
          <p>Квизы мен тесттер жуық арада қосылады</p>
        </div>
      </template>

    </main>
    <Footer />

    <!-- Add Student Modal -->
    <Modal :is-open="showAddModal" title="Жаңа оқушы қосу" :show-close="true" @close="showAddModal = false">
      <template #content>
        <form @submit.prevent="submitAddStudent" class="space-y-4">
          <div v-if="createError" class="text-sm text-red-600 bg-red-50 p-2 rounded">{{ createError }}</div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Аты</label>
            <input v-model="form.firstName" type="text" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm border px-3 py-2">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Тегі</label>
            <input v-model="form.lastName" type="text" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm border px-3 py-2">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Сыныбы</label>
            <select v-model="form.gradeId" required class="mt-1 block bg-white w-full rounded-md border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm border px-3 py-2">
              <option value="" disabled>Таңдаңыз</option>
              <option v-for="grade in grades" :key="grade.number" :value="grade.number">{{ grade.title || `${grade.number} сынып` }}</option>
            </select>
          </div>
        </form>
      </template>
      <template #actions>
        <button @click="submitAddStudent" :disabled="creating" class="add-btn">
          <svg v-if="creating" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
          Қосу
        </button>
        <button @click="showAddModal = false" :disabled="creating" class="cancel-btn">Болдырмау</button>
      </template>
    </Modal>

    <!-- Success Modal -->
    <Modal :is-open="showSuccessModal" title="Оқушы сәтті құрылды!" :show-close="false">
      <template #content>
        <div class="space-y-3">
          <p class="text-sm text-gray-600">Бұл мәліметтерді оқушыға беріңіз.</p>
          <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 font-mono text-sm space-y-2">
            <div class="flex justify-between"><span class="text-gray-500">Аты-жөні:</span><span class="font-bold text-gray-900">{{ createdStudentData?.full_name }}</span></div>
            <div class="flex justify-between border-t border-gray-200 pt-2"><span class="text-gray-500">Логин:</span><span class="font-bold text-cyan-600 select-all">{{ createdStudentData?.username }}</span></div>
            <div class="flex justify-between border-t border-gray-200 pt-2"><span class="text-gray-500">Құпиясөз:</span><span class="font-bold text-green-600 select-all">{{ createdStudentData?.password }}</span></div>
          </div>
        </div>
      </template>
      <template #actions>
        <button @click="closeSuccessModal" class="add-btn">Жабып, жалғастыру</button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { h } from 'vue'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Modal from '@/components/ui/Modal.vue'
import { useTeacherStore } from '@/stores/teacher'
import { teacherApi } from '@/api/teacher'
import type { StudentInfo } from '@/api/teacher'
import { useCatalogStore } from '@/stores/catalog'
import { useAuthStore } from '@/stores/auth'

defineOptions({ name: 'TeacherDashboard' })

// Icon components (inline SVGs as render functions)
const EyeIcon = { render: () => h('svg', { class: 'tab-icon', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z' }),
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z' }),
])}
const BoltIcon = { render: () => h('svg', { class: 'tab-icon', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M13 10V3L4 14h7v7l9-11h-7z' }),
])}
const QuizIcon = { render: () => h('svg', { class: 'tab-icon', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' }),
])}

const tabs = ref([
  { 
    key: 'glance_group', 
    label: 'Қысқаша шолу', 
    icon: EyeIcon,
    dropdown: [
      { key: 'glance', label: 'Жалпы көрініс' },
      { key: 'roster', label: 'Оқушылар тізімі' }
    ]
  },
  { key: 'tools', label: 'Құралдар', icon: BoltIcon },
  { key: 'quizzes', label: 'Квиздер', icon: QuizIcon },
])

const activeTab = ref('glance')
const hoverTab = ref<string | null>(null)

const teacherStore = useTeacherStore()
const catalogStore = useCatalogStore()
const authStore = useAuthStore()

const { students, loading: loadingStudents, error: studentsError } = storeToRefs(teacherStore)
const { grades } = storeToRefs(catalogStore)

// Dashboard analytics data
const loadingData = ref(true)
const selectedStudentId = ref('all')

interface StudentBreakdown {
  student_id: string
  full_name: string
  total_questions: number
  total_time_sec: number
  mastered_count: number
  proficient_count: number
  skills: Array<Record<string, unknown>>
}

const overviewData = ref<{
  total_time_sec: number
  skills_practiced: number
  avg_accuracy_percent: number
  total_questions_answered: number
}>({ total_time_sec: 0, skills_practiced: 0, avg_accuracy_percent: 0, total_questions_answered: 0 })

const studentsBreakdown = ref<StudentBreakdown[]>([])

const teacherName = computed(() => {
  return authStore.user?.full_name || 'Мұғалім'
})

// Selected student or "all" computed data
const currentTotalQuestions = computed(() => {
  if (selectedStudentId.value === 'all') return overviewData.value.total_questions_answered
  const s = studentsBreakdown.value.find(x => x.student_id === selectedStudentId.value)
  return s?.total_questions || 0
})

const questionsDigits = computed(() => {
  const n = currentTotalQuestions.value
  if (n === 0) return ['0']
  return n.toString().split('')
})

const currentTotalTime = computed(() => {
  if (selectedStudentId.value === 'all') return overviewData.value.total_time_sec
  const s = studentsBreakdown.value.find(x => x.student_id === selectedStudentId.value)
  return s?.total_time_sec || 0
})

const currentTimeFormatted = computed(() => {
  const sec = currentTotalTime.value
  if (sec < 60) return `${sec} сек`
  const min = Math.round(sec / 60)
  if (min < 60) return `${min} мин`
  const hrs = Math.floor(min / 60)
  const remMin = min % 60
  return `${hrs} сағ ${remMin} мин`
})

const currentSkillsPracticed = computed(() => {
  if (selectedStudentId.value === 'all') return overviewData.value.skills_practiced
  const s = studentsBreakdown.value.find(x => x.student_id === selectedStudentId.value)
  return s?.skills?.length || 0
})

const currentMastered = computed(() => {
  if (selectedStudentId.value === 'all') {
    return studentsBreakdown.value.reduce((sum, s) => sum + (s.mastered_count || 0), 0)
  }
  const s = studentsBreakdown.value.find(x => x.student_id === selectedStudentId.value)
  return s?.mastered_count || 0
})

const currentProficient = computed(() => {
  if (selectedStudentId.value === 'all') {
    return studentsBreakdown.value.reduce((sum, s) => sum + (s.proficient_count || 0), 0)
  }
  const s = studentsBreakdown.value.find(x => x.student_id === selectedStudentId.value)
  return s?.proficient_count || 0
})

const currentSkillsPracticedThisWeek = ref(0) // We don't track weekly yet

// Roster functionality
const showAddModal = ref(false)
const showSuccessModal = ref(false)
const creating = ref(false)
const createError = ref('')
const resettingId = ref<string | null>(null)
const resetError = ref('')
const deletingId = ref<string | null>(null)
const copiedId = ref<string | null>(null)

const copyToClipboard = (text: string, id: string) => {
  navigator.clipboard.writeText(text).then(() => {
    copiedId.value = id
    setTimeout(() => { if (copiedId.value === id) copiedId.value = null }, 1500)
  })
}

const form = ref({ firstName: '', lastName: '', gradeId: '' as string | number })
const createdStudentData = ref<{ full_name: string; username: string; password: string } | null>(null)

onMounted(async () => {
  // Load analytics data
  loadingData.value = true
  try {
    const [quickviewResp] = await Promise.all([
      teacherApi.getTeacherQuickviewAnalytics(false),
      teacherStore.fetchStudents(),
      grades.value.length === 0 ? catalogStore.getGrades() : Promise.resolve(),
    ])
    const qd = quickviewResp.data?.data as Record<string, unknown> | undefined
    if (qd) {
      const ov = qd.overview as Record<string, unknown> | undefined
      if (ov) {
        overviewData.value = {
          total_time_sec: (ov.total_time_sec as number) || 0,
          skills_practiced: (ov.skills_practiced as number) || 0,
          avg_accuracy_percent: (ov.avg_accuracy_percent as number) || 0,
          total_questions_answered: (ov.total_questions_answered as number) || 0,
        }
      }
      if (Array.isArray(qd.students_breakdown)) {
        studentsBreakdown.value = qd.students_breakdown as StudentBreakdown[]
      }
    }
  } catch (err) {
    console.error('Failed to load teacher dashboard data:', err)
  } finally {
    loadingData.value = false
  }
})

const submitAddStudent = async () => {
  if (!form.value.firstName || !form.value.lastName || form.value.gradeId === '') {
    createError.value = 'Барлық өрістерді толтырыңыз.'
    return
  }
  createError.value = ''
  creating.value = true
  try {
    const res = await teacherStore.createStudent({ first_name: form.value.firstName, last_name: form.value.lastName, grade_id: Number(form.value.gradeId) })
    createdStudentData.value = res
    showAddModal.value = false
    showSuccessModal.value = true
    form.value = { firstName: '', lastName: '', gradeId: '' }
  } catch (err: unknown) {
    const error = err as { response?: { data?: { message?: string } }; message?: string }
    createError.value = error.response?.data?.message || error.message || 'Қате шықты'
  } finally {
    creating.value = false
  }
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
  createdStudentData.value = null
  teacherStore.fetchStudents()
}

const resetPassword = async (student: StudentInfo) => {
  resettingId.value = student.id
  resetError.value = ''
  try {
    const resp = await teacherApi.resetStudentPassword(student.id)
    const newPass = resp.data.data.password
    const found = students.value.find(s => s.id === student.id)
    if (found) (found as StudentInfo & { password?: string }).password = newPass
  } catch (err: unknown) {
    const e = err as { response?: { data?: { message?: string } }; message?: string }
    resetError.value = e.response?.data?.message || e.message || 'Қате шықты'
  } finally {
    resettingId.value = null
  }
}

const confirmDelete = async (student: StudentInfo) => {
  if (!window.confirm(`"${student.full_name}" оқушысын өшіруді растайсыз ба?`)) return
  deletingId.value = student.id
  resetError.value = ''
  try {
    await teacherApi.deleteStudent(student.id)
    teacherStore.students = students.value.filter(s => s.id !== student.id)
  } catch (err: unknown) {
    const e = err as { response?: { data?: { message?: string } }; message?: string }
    resetError.value = e.response?.data?.message || e.message || 'Жою кезінде қате шықты'
  } finally {
    deletingId.value = null
  }
}
</script>

<style scoped>
/* ============ BASE ============ */
.teacher-dashboard {
  min-height: 100vh;
  background: #e8f4f8;
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
}

/* ============ TABS BAR ============ */
.tabs-bar {
  background: linear-gradient(135deg, #00BCD4 0%, #00ACC1 100%);
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  width: 100%;
}
.tabs-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 0;
  padding: 0;
  overflow: visible;
}
.tab-item-group {
  position: relative;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 24px;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  height: 100%;
}
.tab-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}
.tab-btn.active {
  color: white;
  background: rgba(255, 255, 255, 0.15);
  border-bottom-color: white;
  font-weight: 600;
}
.tab-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.tab-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  min-width: 220px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  border-radius: 0 0 8px 8px;
  z-index: 50;
  overflow: hidden;
  padding: 8px 0;
}

.dropdown-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 12px 24px;
  border: none;
  background: white;
  color: #4a5568;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background-color: #f7fafc;
  color: #00BCD4;
}

.dropdown-item.active {
  background-color: #e6fffa;
  color: #00BCD4;
  font-weight: 600;
  border-left: 3px solid #00BCD4;
  padding-left: 21px; 
}

/* ============ MAIN ============ */
.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 16px;
}

/* ============ WELCOME ============ */
.welcome-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.welcome-title {
  font-size: 30px;
  font-weight: 300;
  color: #3f454a;
  line-height: 1.2;
}
.student-selector {
  position: relative;
}
.student-select {
  appearance: none;
  background: #e8edef;
  border: none;
  border-radius: 20px;
  padding: 6px 32px 6px 16px;
  font-size: 14px;
  font-weight: 500;
  color: #3f454a;
  cursor: pointer;
  outline: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236b7c85' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3e%3cpath d='M6 9l6 6 6-6'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  transition: background-color 0.2s;
}
.student-select:hover {
  background-color: #dce3e7;
}

/* ============ INFO BANNER ============ */
.info-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(90deg, #eef9fb 0%, #f0faf4 100%);
  border: 1px solid #d2eef3;
  border-radius: 12px;
  padding: 14px 20px;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
}
.info-banner-icon {
  font-size: 28px;
  flex-shrink: 0;
}
.info-banner p {
  font-size: 14px;
  color: #3f454a;
  margin: 0;
  flex: 1;
}
.info-link {
  color: #00838f;
  font-weight: 600;
  text-decoration: none;
}
.info-link:hover {
  text-decoration: underline;
}
.info-banner-star {
  font-size: 32px;
  flex-shrink: 0;
  opacity: 0.7;
}

/* ============ BLUE STRIP ============ */
.blue-strip {
  background: linear-gradient(135deg, #00acc1 0%, #00838f 100%);
  border-radius: 14px 14px 0 0;
  padding: 28px 20px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 131, 143, 0.3);
}
.blue-strip-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}
.blue-strip-label {
  color: rgba(255,255,255,0.95);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
}
.digit-row {
  display: flex;
  gap: 4px;
}
.digit-box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 52px;
  background: rgba(255,255,255,0.18);
  border: 2px solid rgba(255,255,255,0.35);
  border-radius: 8px;
  color: white;
  font-size: 32px;
  font-weight: 800;
  text-shadow: 0 2px 4px rgba(0,0,0,0.15);
}

/* ============ DASHBOARD CARDS ============ */
.dashboard-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: white;
  border-radius: 0 0 14px 14px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  overflow: hidden;
  border: 1px solid #e0e8ec;
  border-top: none;
}
@media (max-width: 768px) {
  .dashboard-cards { grid-template-columns: 1fr; }
}
.card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 24px 0;
}
.card:first-child {
  border-right: 1px solid #e8eff2;
}
@media (max-width: 768px) {
  .card:first-child {
    border-right: none;
    border-bottom: 1px solid #e8eff2;
  }
}
.card-title {
  font-size: 20px;
  font-weight: 400;
  color: #5a6a72;
  margin-bottom: 24px;
  text-align: center;
}

/* Mountain area */
.mountain-area {
  width: 100%;
  position: relative;
  margin-bottom: 12px;
}
.mountain-svg {
  width: 100%;
  height: auto;
  border-radius: 8px;
}
.mountain-stats {
  position: absolute;
  left: 10px;
  top: 15%;
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.stat-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.stat-number {
  font-size: 28px;
  font-weight: 800;
  color: #3f454a;
  min-width: 28px;
  text-align: right;
  text-shadow: 0 1px 2px rgba(255,255,255,0.8);
}
.stat-line {
  width: 32px;
  height: 2px;
  background: #8aa0ab;
}
.stat-label {
  font-size: 9px;
  font-weight: 700;
  color: #6b7c85;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

/* Donut area */
.donut-area {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  margin-bottom: 12px;
  width: 100%;
  min-height: 180px;
}
.donut-wrapper {
  position: relative;
  width: 160px;
  height: 160px;
}
.donut-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}
.donut-arc {
  transition: stroke-dasharray 1s ease-out;
}
.donut-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.donut-value {
  font-size: 28px;
  font-weight: 300;
  color: #3f454a;
}
.donut-sub {
  font-size: 10px;
  font-weight: 600;
  color: #8aa0ab;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-top: 2px;
}
.donut-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #6b7c85;
  letter-spacing: 1px;
  text-transform: uppercase;
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Card footers */
.card-footer {
  width: 100%;
  border-top: 1px solid #e8eff2;
  padding: 14px 0;
  text-align: center;
  margin-top: auto;
}
.card-footer-link {
  color: #00838f;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}
.card-footer-link:hover {
  text-decoration: underline;
  color: #006064;
}

/* Achievement footer */
.achievement-footer {
  background: #f0f8fa;
  border: 1px solid #d2eef3;
  border-top: none;
  border-radius: 0 0 14px 14px;
  padding: 14px;
  text-align: center;
}
.achievement-link {
  color: #00838f;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
}
.achievement-link:hover {
  text-decoration: underline;
}

/* ============ LOADING ============ */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #6b7c85;
}
.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e0e8ec;
  border-top-color: #00acc1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 12px;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ============ TOOLS TAB ============ */
.tools-section {
  animation: fadeIn 0.3s ease;
}
.tools-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.tools-title {
  font-size: 24px;
  font-weight: 600;
  color: #3f454a;
}
.tools-subtitle {
  font-size: 13px;
  color: #8aa0ab;
  margin-top: 2px;
}
.add-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #00acc1;
  color: white;
  font-size: 14px;
  font-weight: 600;
  padding: 8px 18px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}
.add-btn:hover {
  background: #00838f;
}
.cancel-btn {
  display: inline-flex;
  align-items: center;
  background: #e8edef;
  color: #3f454a;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 18px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  margin-left: 8px;
  transition: background 0.2s;
}
.cancel-btn:hover {
  background: #dce3e7;
}

/* Table */
.table-card {
  background: white;
  border: 1px solid #e0e8ec;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.table-loading {
  display: flex;
  justify-content: center;
  padding: 48px;
}
.table-error {
  padding: 24px;
  color: #c62828;
  background: #fbe9e7;
}
.table-empty {
  padding: 64px 24px;
  text-align: center;
}
.roster-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.roster-table thead tr {
  background: #00acc1;
  color: white;
}
.roster-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 13px;
}
.roster-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f4f5;
}
.roster-table tbody tr:hover {
  background: #f0f8fa;
}
.table-foot {
  padding: 10px 16px;
  font-size: 12px;
  color: #8aa0ab;
  background: #f8fafb;
  border-top: 1px solid #e8eff2;
}
.copy-badge {
  font-family: 'SF Mono', 'Menlo', monospace;
  font-size: 13px;
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
  position: relative;
  transition: background 0.2s;
  user-select: all;
}
.copy-badge-blue {
  color: #00838f;
  background: #e0f7fa;
}
.copy-badge-blue:hover { background: #b2ebf2; }
.copy-badge-green {
  color: #2e7d32;
  background: #e8f5e9;
}
.copy-badge-green:hover { background: #c8e6c9; }
.copy-toast {
  position: absolute;
  top: -28px;
  left: 50%;
  transform: translateX(-50%);
  background: #37474f;
  color: white;
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 4px;
  white-space: nowrap;
  z-index: 10;
  pointer-events: none;
}
.action-btns {
  display: flex;
  align-items: center;
  gap: 12px;
}
.action-link {
  font-size: 12px;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
  padding: 0;
}
.action-link:disabled { opacity: 0.5; }
.action-link-blue {
  color: #00838f;
}
.action-link-blue:hover { color: #006064; text-decoration: underline; }
.action-link-red {
  color: #c62828;
}
.action-link-red:hover { color: #b71c1c; text-decoration: underline; }
.error-msg {
  margin-top: 12px;
  font-size: 13px;
  color: #c62828;
  background: #fbe9e7;
  border: 1px solid #ffcdd2;
  border-radius: 8px;
  padding: 8px 16px;
}

/* ============ EMPTY TAB ============ */
.empty-tab {
  background: white;
  border: 1px solid #e0e8ec;
  border-radius: 14px;
  padding: 80px 24px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  animation: fadeIn 0.3s ease;
}
.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
.empty-tab h2 {
  font-size: 22px;
  font-weight: 400;
  color: #5a6a72;
  margin-bottom: 8px;
}
.empty-tab p {
  font-size: 14px;
  color: #8aa0ab;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

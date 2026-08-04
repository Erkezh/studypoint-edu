<template>
  <div class="ixl-skills-practiced">
    <!-- Header -->
    <div class="sp-header flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-6 border-b border-gray-200">
      <div class="header-left flex items-center">
        <h1 class="header-title text-xl sm:text-2xl font-semibold uppercase text-gray-700 m-0 mr-4">ОРЫНДАЛҒАН ДАҒДЫЛАР</h1>
        <button class="icon-btn text-gray-400 hover:text-gray-600 p-1" @click="printReport" title="Басып шығару">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" /></svg>
        </button>
        <button class="icon-btn text-gray-400 hover:text-gray-600 p-1 ml-1" title="Анықтама">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </button>
      </div>
      <div class="header-right w-full sm:w-auto">
        <div class="search-box flex items-center border border-gray-300 rounded bg-white px-3 py-1.5 w-full sm:w-64">
          <input type="text" placeholder="Дағды бойынша іздеу..." v-model="searchQuery" class="border-none outline-none w-full text-sm text-gray-600" />
          <span class="search-arrow text-gray-300 ml-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </span>
        </div>
      </div>
    </div>

    <!-- Practice Overview Cards -->
    <div class="sp-overview-panel bg-white border border-gray-200 p-5 sm:p-6 text-center mt-6 shadow-sm">
      <h2 class="overview-title text-base sm:text-xl font-medium text-gray-600 mb-6">Тәжірибе шолуы - {{ dateLabel || 'Барлық уақыт' }}</h2>
      <div class="overview-cards flex flex-col sm:flex-row justify-center items-center gap-5 sm:gap-10">
        <div class="o-card flex flex-col items-center w-full sm:w-56">
          <div class="o-value text-teal-400 text-3xl sm:text-4xl font-medium flex items-center justify-center leading-none mb-2">
            <svg class="w-8 h-8 sm:w-10 sm:h-10 mr-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
            {{ totalStudentsPracticed }}
          </div>
          <div class="o-label text-[10px] sm:text-xs font-semibold tracking-wider text-gray-400 uppercase">ТӘЖІРИБЕ ЖАСАҒАН ОҚУШЫЛАР</div>
        </div>
        <div class="hidden sm:block o-divider w-px h-16 bg-gray-200"></div>
        <div class="o-card flex flex-col items-center w-full sm:w-56">
          <div class="o-value text-indigo-400 text-3xl sm:text-4xl font-medium flex items-center justify-center leading-none mb-2">
            <svg class="w-8 h-8 sm:w-10 sm:h-10 mr-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" /></svg>
            {{ totalSkillsPracticed }}
          </div>
          <div class="o-label text-[10px] sm:text-xs font-semibold tracking-wider text-gray-400 uppercase">ОРЫНДАЛҒАН ДАҒДЫЛАР</div>
        </div>
        <div class="hidden sm:block o-divider w-px h-16 bg-gray-200"></div>
        <div class="o-card flex flex-col items-center w-full sm:w-56 cursor-pointer hover:bg-gray-100 rounded-lg p-2 transition-colors" @click="emit('navigate', 'trouble_class')">
          <div class="o-value text-red-500 text-3xl sm:text-4xl font-medium flex items-center justify-center leading-none mb-2">
            <svg class="w-8 h-8 sm:w-10 sm:h-10 mr-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
            {{ totalTroubleSpots }}
          </div>
          <div class="o-label text-[10px] sm:text-xs font-semibold tracking-wider text-gray-400 uppercase">ҚИЫНДЫҚТАР</div>
        </div>
      </div>
    </div>

    <!-- Skills Table -->
    <div class="sp-table-container mt-12">
      <!-- Table Header -->
      <div class="sp-table-header sp-table-grid bg-[#00AEEF] text-white px-4 sm:px-5 py-3 text-[11px] sm:text-sm font-bold items-center">
        <div class="th-skill flex items-center">
          ДАҒДЫ
        </div>
        <div class="th-progress flex items-center">
          ДАҒДЫЛАР ПРОГРЕСІ
          <span class="info-circle hidden sm:inline-flex justify-center items-center w-3.5 h-3.5 rounded-full border border-white text-[9px] font-bold ml-1.5 cursor-help" @mouseenter="showInfoTooltip = true" @mouseleave="showInfoTooltip = false">i</span>
          <div v-if="showInfoTooltip" class="info-tooltip absolute bottom-full left-0 bg-white border border-gray-200 p-2 sm:p-4 rounded shadow-lg z-10 mb-2 text-xs font-normal text-gray-700 leading-relaxed">
            <div class="tt-item text-green-500">Меңгерілген</div>
            <div class="tt-item text-cyan-500">Білікті</div>
            <div class="tt-item text-blue-500">Жаттығуда</div>
            <div class="tt-item text-orange-400">Тәжірибе жоқ</div>
          </div>
        </div>
        <div class="th-trouble text-left">ҚИЫНДЫҚТАР</div>
        <div aria-hidden="true"></div>
      </div>

      <!-- Table Body -->
      <div class="sp-table-body">
        <div v-if="analyzedSkills.length === 0" class="p-8 text-center text-gray-500">
          Орындалған дағдылар жоқ.
        </div>

        <div v-for="skill in analyzedSkills" :key="skill.skillId" class="sp-row">
          <!-- Main row (always visible) -->
          <div class="sp-row-main sp-table-grid px-4 sm:px-5 py-3 items-center cursor-pointer hover:bg-white transition-colors" @click="toggleRow(skill.skillId)">
            <div class="td-skill flex min-w-0 items-baseline gap-x-2">
              <span class="sk-grade text-gray-500 text-xs sm:text-sm whitespace-nowrap">{{ skill.gradeLabel }}</span>
              <span class="sk-name min-w-0 truncate text-[#1685c5] text-xs sm:text-sm font-semibold">{{ skill.skillName }}</span>
              <span class="sk-code shrink-0 text-gray-300 text-xs uppercase tracking-tight">{{ skill.skillCode }}</span>
            </div>
            <div class="td-progress relative pr-2 sm:pr-0">
              <div class="progress-segmented-bar w-full h-1.5 sm:h-2 flex gap-0.5 rounded-full overflow-hidden bg-gray-100">
                <div class="bg-green-500 h-full" :style="{ width: getPercentage(skill.mastered.length) + '%' }" v-if="skill.mastered.length"></div>
                <div class="bg-cyan-500 h-full" :style="{ width: getPercentage(skill.proficient.length) + '%' }" v-if="skill.proficient.length"></div>
                <div class="bg-blue-500 h-full" :style="{ width: getPercentage(skill.practicing.length) + '%' }" v-if="skill.practicing.length"></div>
                <div class="bg-gray-200 h-full" :style="{ width: getPercentage(skill.noPractice.length) + '%' }" v-if="skill.noPractice.length"></div>
              </div>
            </div>
            <div class="td-trouble text-red-500 flex items-center gap-2 text-xs font-medium whitespace-nowrap">
              <svg v-if="skill.hasTroubleSpot" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
              <span v-if="skill.hasTroubleSpot">{{ skill.troubleStudentsCount }} оқушыға көмек керек</span>
            </div>
            <div class="td-arrow flex justify-end">
              <svg class="w-5 h-5 text-gray-300 transform transition-transform" :class="{'rotate-180': isRowExpanded(skill.skillId)}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
            </div>
          </div>

          <!-- Expanded section -->
          <div class="sp-row-expanded" v-if="isRowExpanded(skill.skillId)">
            <div class="exp-cols grid grid-cols-4 gap-4 px-6 py-4">
              <!-- Mastered -->
              <div class="exp-col">
                <h4 class="col-title text-green-500">МЕҢГЕРІЛГЕН: {{ skill.mastered.length }} оқушы</h4>
                <div class="col-students border-l-2 border-green-200 pl-4 mt-3 space-y-2">
                  <div v-for="st in skill.mastered" :key="st.id" class="st-item">
                    <a href="#" @click.prevent="goToQuestions(st.id)" class="hover:text-teal-600 hover:underline">{{ st.name }}</a> ({{ st.score }})
                  </div>
                </div>
              </div>
              <!-- Proficient -->
              <div class="exp-col">
                <h4 class="col-title text-cyan-500">БІЛІКТІ: {{ skill.proficient.length }} оқушы</h4>
                <div class="col-students border-l-2 border-cyan-200 pl-4 mt-3 space-y-2">
                  <div v-for="st in skill.proficient" :key="st.id" class="st-item">
                    <a href="#" @click.prevent="goToQuestions(st.id)" class="hover:text-cyan-600 hover:underline">{{ st.name }}</a> ({{ st.score }})
                  </div>
                </div>
              </div>
              <!-- Practicing -->
              <div class="exp-col">
                <h4 class="col-title text-blue-500">ЖАТТЫҒУДА: {{ skill.practicing.length }} оқушы</h4>
                <div class="col-students border-l-2 border-blue-200 pl-4 mt-3 space-y-2">
                  <div v-for="st in [...skill.practicing].sort((a,b) => b.score - a.score)" :key="st.id" class="st-item">
                    <span class="text-xs text-blue-400 font-bold block mb-0.5 mt-2 first:mt-0" v-if="st.score < 50">1-ДЕҢГЕЙ</span>
                    <span class="text-xs text-blue-500 font-bold block mb-0.5 mt-2 first:mt-0" v-else>2-ДЕҢГЕЙ</span>
                    <a href="#" @click.prevent="goToQuestions(st.id)" class="hover:text-blue-600 hover:underline">{{ st.name }}</a> ({{ st.score }})
                  </div>
                </div>
              </div>
              <!-- No Practice -->
              <div class="exp-col">
                <h4 class="col-title text-orange-400">ТӘЖІРИБЕ ЖОҚ: {{ skill.noPractice.length }} оқушы</h4>
                <div class="col-students border-l-2 border-orange-200 pl-4 mt-3 space-y-2">
                  <div v-for="st in skill.noPractice" :key="st.id" class="st-item text-gray-600">
                    <a href="#" @click.prevent="goToQuestions(st.id)" class="hover:text-gray-800 hover:underline">{{ st.name }}</a>
                  </div>
                </div>
              </div>
            </div>

            <div class="exp-footer px-6 pb-6 text-center">
              <a href="#" @click.prevent="goToAnalysis(skill.skillId)" class="text-blue-500 hover:text-blue-700 font-medium text-sm">
                Толығырақ ақпарат алу үшін "Дағдылар талдауына" өтіңіз &gt;
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface StudentAnalyticsData {
  student_id: string
  full_name: string
  skills?: {
    skill_id: number
    skill_name?: string
    skill_code?: string
    grade_label?: string
    grade_number?: number
    best_smartscore?: number
    last_smartscore?: number
    total_questions?: number
    last_practiced_at?: string | null
    missed_questions?: number
  }[]
}

interface Props {
  gradeFrom?: number
  gradeTo?: number
  dateRange?: { start: Date | null; end: Date | null }
  dateLabel?: string
  allStudentsData?: StudentAnalyticsData[]
}
const props = withDefaults(defineProps<Props>(), {
  allStudentsData: () => [],
})

const emit = defineEmits<{
  (e: 'navigate', route: string, context?: Record<string, unknown>): void
}>()

const searchQuery = ref('')
const showInfoTooltip = ref(false)
const expandedRows = ref<Record<string, boolean>>({})

// Extract the total count of students passed in
const totalStudents = computed(() => {
  return props.allStudentsData?.length || 1
})

const getPercentage = (count: number) => {
  if (totalStudents.value === 0) return 0
  return (count / totalStudents.value) * 100
}

const toggleRow = (skillId: string | number) => {
  expandedRows.value[skillId] = !isRowExpanded(skillId)
}

const isRowExpanded = (skillId: string | number) => expandedRows.value[skillId] === true

const printReport = () => window.print()

const goToAnalysis = (skillId: string | number) => {
  // Pass control back to parent to switch active tab to "skill_analysis" and focus on this skillId if possible.
  emit('navigate', 'skill_analysis', { skillId })
}

const goToQuestions = (studentId: string) => {
  emit('navigate', 'questions', { studentId })
}

interface StudentGroup {
  id: string
  name: string
  score: number
}

interface SkillData {
  skillId: string
  skillName: string
  skillCode: string
  gradeLabel: string
  mastered: StudentGroup[]
  proficient: StudentGroup[]
  practicing: StudentGroup[]
  noPractice: StudentGroup[]
  hasTroubleSpot: boolean
  troubleStudentsCount: number
}

// Compute the categorized skills based on student data
const analyzedSkills = computed<SkillData[]>(() => {
  if (!props.allStudentsData || props.allStudentsData.length === 0) return []

  const skillMap = new Map<number, SkillData>()

  // Pass 1: find all unique skills any student practiced in this dataset
  for (const st of props.allStudentsData) {
    if (!st.skills) continue
    for (const sk of st.skills) {
      if (!skillMap.has(sk.skill_id)) {
        skillMap.set(sk.skill_id, {
          skillId: sk.skill_id.toString(),
          skillName: sk.skill_name || 'Дағды',
          skillCode: sk.skill_code || '',
          gradeLabel: sk.grade_label || `${sk.grade_number} сынып`,
          mastered: [],
          proficient: [],
          practicing: [],
          noPractice: [],
          hasTroubleSpot: false,
          troubleStudentsCount: 0,
        })
      }
    }
  }

  // Pass 2: map every student into one of the 4 buckets per skill
  for (const skill of skillMap.values()) {
    const troubleStudentIds = new Set<string>()
    for (const st of props.allStudentsData) {
      const studentSkill = st.skills?.find((s) => s.skill_id.toString() === skill.skillId)
      const score = studentSkill ? Math.max(Number(studentSkill.best_smartscore || 0), Number(studentSkill.last_smartscore || 0)) : 0
      const groupData = { id: st.student_id, name: st.full_name, score }

      // AnalyticsView has already restricted this list to the selected period.
      const practicedInWindow = Boolean(studentSkill && Number(studentSkill.total_questions || 0) > 0)

      if (!studentSkill || !practicedInWindow) {
        skill.noPractice.push(groupData)
      } else if (groupData.score >= 90) {
        skill.mastered.push(groupData)
      } else if (groupData.score >= 80) {
        skill.proficient.push(groupData)
      } else {
        skill.practicing.push(groupData)
      }

      if (practicedInWindow && Number(studentSkill?.missed_questions || 0) > 0) {
        troubleStudentIds.add(st.student_id)
      }
    }
    skill.troubleStudentsCount = troubleStudentIds.size
    skill.hasTroubleSpot = skill.troubleStudentsCount > 0
  }

  // Remove skills where nobody actually practiced (all students in "No Practice")
  const result = Array.from(skillMap.values()).filter(s =>
    s.mastered.length > 0 || s.proficient.length > 0 || s.practicing.length > 0
  )
  
  // Basic search filter
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    return result.filter(s => 
      s.skillName.toLowerCase().includes(q) || 
      s.skillCode.toLowerCase().includes(q) ||
      s.gradeLabel.toLowerCase().includes(q)
    )
  }

  // Sort by most practiced
  return result.sort((a, b) => {
    const aPracticed = a.mastered.length + a.proficient.length + a.practicing.length
    const bPracticed = b.mastered.length + b.proficient.length + b.practicing.length
    return bPracticed - aPracticed
  })
})

const totalStudentsPracticed = computed(() => {
  if (!props.allStudentsData) return 0
  return props.allStudentsData.filter(st => {
    if (!st.skills || st.skills.length === 0) return false
    return st.skills.some(sk => Number(sk.total_questions || 0) > 0)
  }).length
})

const totalSkillsPracticed = computed(() => {
  return analyzedSkills.value.length
})

const totalTroubleSpots = computed(() => {
  return analyzedSkills.value.filter(s => s.hasTroubleSpot).length
})

</script>

<style scoped>
.ixl-skills-practiced {
  font-family: 'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  color: #333;
}

.header-title {
  font-size: clamp(1.35rem, 2.5vw, 1.75rem) !important;
  font-weight: 600 !important;
  letter-spacing: 0 !important;
}

.sp-overview-panel {
  min-height: 180px;
}

.overview-cards {
  max-width: 940px;
  margin: 0 auto;
}

.sp-table-container {
  margin-top: 26px !important;
  border: 1px solid #e7edf0;
  overflow-x: auto;
  overflow-y: hidden;
}

.sp-table-grid {
  display: grid;
  grid-template-columns: minmax(260px, 1.45fr) minmax(180px, .85fr) minmax(180px, .65fr) 36px;
  min-width: 700px;
}

.sp-row-main {
  min-height: 56px;
  border-bottom: 1px solid #edf1f2;
}

.sp-row:nth-child(odd) .sp-row-main {
  background: #fff;
}

.sp-row:nth-child(even) .sp-row-main {
  background: #f4fbfc;
}

.sp-row:hover .sp-row-main {
  background: #eef9fc;
}

.sp-row-expanded {
  border-bottom: 1px solid #edf1f2;
  background: white;
  min-width: 700px;
}

.exp-cols {
  display: grid;
  grid-template-columns: repeat(4, minmax(155px, 1fr));
  gap: 0 !important;
}

.exp-col {
  min-width: 0;
  padding: 0 16px;
}

.exp-col + .exp-col {
  border-left: 1px solid #e6e9ea;
}

.col-title {
  font-size: 13px;
  font-weight: 700;
}

.st-item {
  color: #62676b;
  font-size: 13px;
}

.exp-footer {
  padding-top: 14px;
}

@media (max-width: 640px) {
  .sp-overview-panel {
    min-height: auto;
  }

  .exp-cols {
    grid-template-columns: repeat(4, minmax(155px, 1fr)) !important;
    min-width: 700px;
  }

  .exp-col {
    padding: 0 20px;
  }

  .exp-col + .exp-col {
    border-top: 0;
    border-left: 1px solid #e6e9ea;
  }
}

/* Custom Scrollbar Hide */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.sk-name {
  line-height: 1.3;
}

.th-progress {
  justify-self: stretch;
  padding-left: 6px;
}

.td-progress {
  padding-right: 20px;
}

.progress-segmented-bar {
  height: 11px !important;
  background: #e7e9ea !important;
}

.td-arrow svg {
  width: 16px;
  height: 16px;
}

@media (min-width: 641px) {
  .sp-table-header {
    min-height: 66px;
  }
}

@media (max-width: 640px) {
  .td-progress {
    padding-right: 14px;
  }

  .progress-segmented-bar {
    height: 9px !important;
  }
}

.progress-segmented-bar div:first-child {
  border-top-left-radius: 9999px;
  border-bottom-left-radius: 9999px;
}
.progress-segmented-bar div:last-child {
  border-top-right-radius: 9999px;
  border-bottom-right-radius: 9999px;
}
</style>

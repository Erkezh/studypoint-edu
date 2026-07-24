<template>
  <div class="ixl-skills-practiced">
    <!-- Header -->
    <div class="sp-header flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-6 border-b border-gray-200">
      <div class="header-left flex items-center">
        <h1 class="header-title text-xl sm:text-2xl font-light uppercase tracking-wider text-gray-700 m-0 mr-4">ОРЫНДАЛҒАН ДАҒДЫЛАР</h1>
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
    <div class="sp-overview-panel bg-gray-50 p-6 sm:p-8 text-center mt-6 rounded-lg shadow-inner">
      <h2 class="overview-title text-lg sm:text-2xl font-light text-gray-600 mb-8">Тәжірибе шолуы - {{ dateLabel || 'Барлық уақыт' }}</h2>
      <div class="overview-cards flex flex-col sm:flex-row justify-center items-center gap-6 sm:gap-12">
        <div class="o-card flex flex-col items-center w-full sm:w-56">
          <div class="o-value text-teal-400 text-4xl sm:text-5xl font-light flex items-center justify-center leading-none mb-2">
            <svg class="w-8 h-8 sm:w-10 sm:h-10 mr-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
            {{ totalStudentsPracticed }}
          </div>
          <div class="o-label text-[10px] sm:text-xs font-semibold tracking-wider text-gray-400 uppercase">ТӘЖІРИБЕ ЖАСАҒАН ОҚУШЫЛАР</div>
        </div>
        <div class="hidden sm:block o-divider w-px h-16 bg-gray-200"></div>
        <div class="o-card flex flex-col items-center w-full sm:w-56">
          <div class="o-value text-indigo-400 text-4xl sm:text-5xl font-light flex items-center justify-center leading-none mb-2">
            <svg class="w-8 h-8 sm:w-10 sm:h-10 mr-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" /></svg>
            {{ totalSkillsPracticed }}
          </div>
          <div class="o-label text-[10px] sm:text-xs font-semibold tracking-wider text-gray-400 uppercase">ОРЫНДАЛҒАН ДАҒДЫЛАР</div>
        </div>
        <div class="hidden sm:block o-divider w-px h-16 bg-gray-200"></div>
        <div class="o-card flex flex-col items-center w-full sm:w-56 cursor-pointer hover:bg-gray-100 rounded-lg p-2 transition-colors" @click="emit('navigate', 'trouble_class')">
          <div class="o-value text-red-500 text-4xl sm:text-5xl font-light flex items-center justify-center leading-none mb-2">
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
      <div class="sp-table-header bg-[#00AEEF] text-white grid grid-cols-[1fr,80px,40px] sm:grid-cols-[2fr,1fr,150px,40px] px-4 py-3 text-[10px] sm:text-[11px] font-bold tracking-wider items-center">
        <div class="th-skill flex items-center">
          ДАҒДЫ
          <label class="toggle-switch ml-4 scale-75 sm:scale-100 origin-left">
            <input type="checkbox" v-model="showSuggested" />
            <span class="slider"></span>
          </label>
          <span class="hidden sm:inline text-xs ml-2 font-normal">Ұсынылатын дағдылар</span>
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
        <div class="th-trouble text-center hidden sm:block">ҚИЫНДЫҚТАР</div>
        <div class="th-spacer sm:hidden"></div>
      </div>

      <!-- Table Body -->
      <div class="sp-table-body">
        <div v-if="analyzedSkills.length === 0" class="p-8 text-center text-gray-500">
          Орындалған дағдылар жоқ.
        </div>

        <div v-for="skill in analyzedSkills" :key="skill.skillId" class="sp-row">
          <!-- Main row (always visible) -->
          <div class="sp-row-main grid grid-cols-[1fr,80px,40px] sm:grid-cols-[2fr,1fr,150px,40px] px-4 py-4 items-center cursor-pointer hover:bg-gray-50 transition-colors" @click="toggleRow(skill.skillId)">
            <div class="td-skill flex flex-wrap gap-x-2 gap-y-0.5 items-baseline">
              <span class="sk-grade text-gray-500 text-xs sm:text-sm whitespace-nowrap">{{ skill.gradeLabel }}</span>
              <span class="sk-name text-[#00838F] text-sm font-semibold">{{ skill.skillName }}</span>
              <span class="sk-code text-gray-300 text-[10px] sm:text-xs uppercase tracking-tight">{{ skill.skillCode }}</span>
            </div>
            <div class="td-progress relative pr-2 sm:pr-0">
              <div class="progress-segmented-bar w-full h-1.5 sm:h-2 flex gap-0.5 rounded-full overflow-hidden bg-gray-100">
                <div class="bg-green-500 h-full" :style="{ width: getPercentage(skill.mastered.length) + '%' }" v-if="skill.mastered.length"></div>
                <div class="bg-cyan-500 h-full" :style="{ width: getPercentage(skill.proficient.length) + '%' }" v-if="skill.proficient.length"></div>
                <div class="bg-blue-500 h-full" :style="{ width: getPercentage(skill.practicing.length) + '%' }" v-if="skill.practicing.length"></div>
                <div class="bg-gray-200 h-full" :style="{ width: getPercentage(skill.noPractice.length) + '%' }" v-if="skill.noPractice.length"></div>
              </div>
            </div>
            <div class="td-trouble text-red-500 flex justify-center items-center hidden sm:flex">
              <svg v-if="skill.hasTroubleSpot" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
            </div>
            <div class="td-arrow flex justify-end">
              <svg class="w-5 h-5 text-gray-300 transform transition-transform" :class="{'rotate-180': expandedRows[skill.skillId]}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
            </div>
          </div>

          <!-- Expanded section -->
          <div class="sp-row-expanded" v-if="expandedRows[skill.skillId]">
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
const showSuggested = ref(false)
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
  expandedRows.value[skillId] = !expandedRows.value[skillId]
}

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
          hasTroubleSpot: false
        })
      }
    }
  }

  // Pass 2: map every student into one of the 4 buckets per skill
  for (const skill of skillMap.values()) {
    let troubleInThisSkill = false
    for (const st of props.allStudentsData) {
      const studentSkill = st.skills?.find((s) => s.skill_id.toString() === skill.skillId)
      const score = studentSkill ? Math.max(Number(studentSkill.best_smartscore || 0), Number(studentSkill.last_smartscore || 0)) : 0
      const groupData = { id: st.student_id, name: st.full_name, score }

      let practicedInWindow = false
      if (studentSkill && studentSkill.last_practiced_at) {
        if (!props.dateRange?.start) {
          practicedInWindow = true
        } else {
          const lastPracticed = new Date(studentSkill.last_practiced_at)
          if (lastPracticed >= props.dateRange.start) {
            practicedInWindow = true
          }
        }
      } else if (studentSkill && !props.dateRange?.start) {
        // If there's no last_practiced_at but they have a score
        practicedInWindow = true
      }

      if (!studentSkill || groupData.score === 0 || !practicedInWindow) {
        skill.noPractice.push(groupData)
      } else if (groupData.score >= 100) {
        skill.mastered.push(groupData)
      } else if (groupData.score >= 80) {
        skill.proficient.push(groupData)
      } else {
        skill.practicing.push(groupData)
        // IXL: trouble spot = student missed 3+ questions and SmartScore < 80
        if ((studentSkill.total_questions || 0) >= 3 && groupData.score < 80) {
          troubleInThisSkill = true
        }
      }
    }
    skill.hasTroubleSpot = troubleInThisSkill
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
    if (!props.dateRange?.start) return true
    return st.skills.some(sk => sk.last_practiced_at && new Date(sk.last_practiced_at) >= props.dateRange!.start!)
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

/* Custom Scrollbar Hide */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Standard Switch styling if Tailwind not enabled for form elements */
.slider {
  border-radius: 34px;
}
.slider:before {
  content: "";
  height: 14px;
  width: 14px;
  left: 2px;
  bottom: 2px;
  background-color: #00AEEF;
  transition: .4s;
  border-radius: 50%;
  position: absolute;
}
input:checked + .slider { background-color: #2196F3; }
input:checked + .slider:before {
  background-color: white;
  transform: translateX(14px);
}

.sk-name {
  line-height: 1.3;
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

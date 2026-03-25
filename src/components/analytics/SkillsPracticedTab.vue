<template>
  <div class="ixl-skills-practiced">
    <!-- Header -->
    <div class="sp-header">
      <div class="header-left">
        <h1 class="header-title">ОРЫНДАЛҒАН ДАҒДЫЛАР</h1>
        <button class="icon-btn" @click="printReport" title="Басып шығару">
          <svg class="w-6 h-6 shrink-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" /></svg>
        </button>
        <button class="icon-btn" title="Анықтама">
          <svg class="w-6 h-6 shrink-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </button>
      </div>
      <div class="header-right">
        <div class="search-box">
          <input type="text" placeholder="Дағды бойынша іздеу..." v-model="searchQuery" />
          <span class="search-arrow">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </span>
        </div>
      </div>
    </div>

    <!-- Practice Overview Cards -->
    <div class="sp-overview-panel">
      <h2 class="overview-title">Тәжірибе шолуы - {{ dateLabel || 'Барлық уақыт' }}</h2>
      <div class="overview-cards">
        <div class="o-card">
          <div class="o-value text-teal">
            <svg class="w-10 h-10 mr-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
            {{ totalStudentsPracticed }}
          </div>
          <div class="o-label">ТӘЖІРИБЕ ЖАСАҒАН ОҚУШЫЛАР</div>
        </div>
        <div class="o-divider"></div>
        <div class="o-card">
          <div class="o-value text-indigo">
            <svg class="w-10 h-10 mr-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" /></svg>
            {{ totalSkillsPracticed }}
          </div>
          <div class="o-label">ОРЫНДАЛҒАН ДАҒДЫЛАР</div>
        </div>
        <div class="o-divider"></div>
        <div class="o-card cursor-pointer hover:bg-gray-100 rounded p-2 transition-colors" @click="emit('navigate', 'trouble_class')">
          <div class="o-value text-trouble">
            <svg class="w-10 h-10 mr-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
            {{ totalTroubleSpots }}
          </div>
          <div class="o-label">ҚИЫНДЫҚТАР</div>
        </div>
      </div>
    </div>

    <!-- Skills Table -->
    <div class="sp-table-container mt-12">
      <!-- Table Header -->
      <div class="sp-table-header">
        <div class="th-skill">
          ДАҒДЫ
          <label class="toggle-switch ml-4">
            <input type="checkbox" v-model="showSuggested" />
            <span class="slider"></span>
          </label>
          <span class="text-xs ml-2 font-normal">Ұсынылатын дағдылар</span>
        </div>
        <div class="th-progress relative">
          ДАҒДЫЛАР ПРОГРЕСІ
          <span class="info-circle" @mouseenter="showInfoTooltip = true" @mouseleave="showInfoTooltip = false">i</span>
          <div v-if="showInfoTooltip" class="info-tooltip">
            <div class="tt-item text-green-500">Mastered</div>
            <div class="tt-item text-cyan-500">Proficient</div>
            <div class="tt-item text-blue-500">Practicing</div>
            <div class="tt-item text-orange-400">No practice</div>
          </div>
        </div>
        <div class="th-trouble">ҚИЫНДЫҚТАР</div>
      </div>

      <!-- Table Body -->
      <div class="sp-table-body">
        <div v-if="analyzedSkills.length === 0" class="p-8 text-center text-gray-500">
          Орындалған дағдылар жоқ.
        </div>

        <div v-for="skill in analyzedSkills" :key="skill.skillId" class="sp-row">
          <!-- Main row (always visible) -->
          <div class="sp-row-main" @click="toggleRow(skill.skillId)">
            <div class="td-skill">
              <span class="sk-grade">{{ skill.gradeLabel }}</span>
              <span class="sk-name">{{ skill.skillName }}</span>
              <span class="sk-code">{{ skill.skillCode }}</span>
            </div>
            <div class="td-progress relative">
              <div class="progress-segmented-bar w-full h-2 flex gap-1 rounded overflow-hidden">
                <div class="bg-green-500 h-full" :style="{ width: getPercentage(skill.mastered.length) + '%' }" v-if="skill.mastered.length"></div>
                <div class="bg-cyan-500 h-full" :style="{ width: getPercentage(skill.proficient.length) + '%' }" v-if="skill.proficient.length"></div>
                <div class="bg-blue-500 h-full" :style="{ width: getPercentage(skill.practicing.length) + '%' }" v-if="skill.practicing.length"></div>
                <div class="bg-gray-200 h-full" :style="{ width: getPercentage(skill.noPractice.length) + '%' }" v-if="skill.noPractice.length"></div>
              </div>
            </div>
            <div class="td-trouble text-red-500 flex justify-center items-center">
              <svg v-if="skill.hasTroubleSpot" class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
            </div>
            <div class="td-arrow">
              <svg class="w-5 h-5 text-gray-400 transform transition-transform" :class="{'rotate-180': expandedRows[skill.skillId]}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
            </div>
          </div>

          <!-- Expanded section -->
          <div class="sp-row-expanded" v-if="expandedRows[skill.skillId]">
            <div class="exp-cols grid grid-cols-4 gap-4 px-6 py-4">
              <!-- Mastered -->
              <div class="exp-col">
                <h4 class="col-title text-green-500">MASTERED: {{ skill.mastered.length }} student{{ skill.mastered.length !== 1 ? 's' : '' }}</h4>
                <div class="col-students border-l-2 border-green-200 pl-4 mt-3 space-y-2">
                  <div v-for="st in skill.mastered" :key="st.id" class="st-item">
                    <a href="#" @click.prevent="goToQuestions(st.id)" class="hover:text-teal-600 hover:underline">{{ st.name }}</a> ({{ st.score }})
                  </div>
                </div>
              </div>
              <!-- Proficient -->
              <div class="exp-col">
                <h4 class="col-title text-cyan-500">PROFICIENT: {{ skill.proficient.length }} student{{ skill.proficient.length !== 1 ? 's' : '' }}</h4>
                <div class="col-students border-l-2 border-cyan-200 pl-4 mt-3 space-y-2">
                  <div v-for="st in skill.proficient" :key="st.id" class="st-item">
                    <a href="#" @click.prevent="goToQuestions(st.id)" class="hover:text-cyan-600 hover:underline">{{ st.name }}</a> ({{ st.score }})
                  </div>
                </div>
              </div>
              <!-- Practicing -->
              <div class="exp-col">
                <h4 class="col-title text-blue-500">PRACTICING: {{ skill.practicing.length }} student{{ skill.practicing.length !== 1 ? 's' : '' }}</h4>
                <div class="col-students border-l-2 border-blue-200 pl-4 mt-3 space-y-2">
                  <div v-for="st in [...skill.practicing].sort((a,b) => b.score - a.score)" :key="st.id" class="st-item">
                    <span class="text-xs text-blue-400 font-bold block mb-0.5 mt-2 first:mt-0" v-if="st.score < 50">LEVEL 1</span>
                    <span class="text-xs text-blue-500 font-bold block mb-0.5 mt-2 first:mt-0" v-else>LEVEL 2</span>
                    <a href="#" @click.prevent="goToQuestions(st.id)" class="hover:text-blue-600 hover:underline">{{ st.name }}</a> ({{ st.score }})
                  </div>
                </div>
              </div>
              <!-- No Practice -->
              <div class="exp-col">
                <h4 class="col-title text-orange-400">NO PRACTICE: {{ skill.noPractice.length }} student{{ skill.noPractice.length !== 1 ? 's' : '' }}</h4>
                <div class="col-students border-l-2 border-orange-200 pl-4 mt-3 space-y-2">
                  <div v-for="st in skill.noPractice" :key="st.id" class="st-item text-gray-600">
                    <a href="#" @click.prevent="goToQuestions(st.id)" class="hover:text-gray-800 hover:underline">{{ st.name }}</a>
                  </div>
                </div>
              </div>
            </div>

            <div class="exp-footer px-6 pb-6 text-center">
              <a href="#" @click.prevent="goToAnalysis(skill.skillId)" class="text-blue-500 hover:text-blue-700 font-medium text-sm">
                See Skill Analysis for detailed class performance including recent questions &gt;
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
      const groupData = { id: st.student_id, name: st.full_name, score: studentSkill?.best_smartscore || 0 }

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

/* Header */
.sp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 24px;
  border-bottom: 1px solid #eaeaea;
}
.header-left {
  display: flex;
  align-items: center;
}
.header-title {
  font-size: 28px;
  font-weight: 300;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #444;
  margin: 0;
  margin-right: 16px;
}
.icon-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #aaa;
  padding: 4px;
}
.icon-btn:hover { color: #555; }
.shrink-icon { width: 22px; height: 22px; }

.header-right {
  position: relative;
}
.search-box {
  display: flex;
  align-items: center;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #fff;
  padding: 6px 12px;
  width: 260px;
}
.search-box input {
  border: none;
  outline: none;
  width: 100%;
  font-size: 14px;
  color: #555;
}
.search-arrow {
  color: #ccc;
  margin-left: 8px;
}

/* Overview Panel */
.sp-overview-panel {
  background: #FAFAFA;
  padding: 32px;
  text-align: center;
  margin-top: 24px;
  border-radius: 8px;
  box-shadow: inset 0 0 10px rgba(0,0,0,0.02);
}
.overview-title {
  font-size: 24px;
  font-weight: 300;
  color: #666;
  margin: 0 0 32px 0;
}
.overview-cards {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 48px;
}
.o-divider {
  width: 1px;
  height: 80px;
  background: #eee;
}
.o-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 220px;
}
.o-value {
  font-size: 56px;
  font-weight: 300;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  margin-bottom: 8px;
}
.text-teal { color: #00BFA5; }
.text-indigo { color: #7986CB; }
.text-trouble { color: #E53935; } /* Red for trouble */
.o-label {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: #888;
}

/* Skills Table */
.sp-table-container {
  border: 1px solid #E0E0E0;
  border-radius: 4px;
  overflow: hidden;
}
.sp-table-header {
  background-color: #00AEEF; /* IXL blue */
  color: white;
  display: grid;
  grid-template-columns: 2fr 1fr 150px 40px;
  padding: 12px 16px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  align-items: center;
}
.th-skill { display: flex; align-items: center; }
.th-progress { display: flex; align-items: center; }
.th-trouble { text-align: center; }

/* Switch matching screenshot */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 32px;
  height: 18px;
}
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: #fff;
  transition: .4s;
  border-radius: 34px;
}
.slider:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 2px;
  bottom: 2px;
  background-color: #00AEEF;
  transition: .4s;
  border-radius: 50%;
}
input:checked + .slider { background-color: #2196F3; }
input:checked + .slider:before {
  background-color: white;
  transform: translateX(14px);
}

.info-circle {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  width: 14px; height: 14px;
  border-radius: 50%;
  border: 1px solid white;
  font-size: 10px;
  font-weight: bold;
  margin-left: 6px;
  cursor: default;
}
.info-tooltip {
  position: absolute;
  bottom: 100%; left: 0;
  background: white;
  border: 1px solid #ccc;
  padding: 8px 16px;
  border-radius: 4px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  z-index: 10;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: normal;
  line-height: 1.8;
}

/* Rows */
.sp-table-body {
  background: white;
}
.sp-row {
  border-bottom: 1px solid #eee;
}
.sp-row:last-child {
  border-bottom: none;
}
.sp-row-main {
  display: grid;
  grid-template-columns: 2fr 1fr 150px 40px;
  padding: 16px;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s;
}
.sp-row-main:hover {
  background-color: #F9F9F9;
}
.td-skill {
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.sk-grade {
  color: #555;
  font-size: 14px;
}
.sk-name {
  color: #00838F; /* Deep teal link color */
  font-size: 14px;
  font-weight: 600;
}
.sk-code {
  color: #AAA;
  font-size: 12px;
  text-transform: uppercase;
}
.td-arrow {
  display: flex;
  justify-content: flex-end;
}

/* Expanded section */
.sp-row-expanded {
  background-color: #FFF;
  border-top: 1px solid #F5F5F5;
}
.col-title {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}
.st-item {
  font-size: 13px;
  color: #444;
  line-height: 1.4;
}
</style>

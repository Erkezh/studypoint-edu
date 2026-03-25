<template>
  <div class="ixl-skill-analysis">
    <!-- Header -->
    <div class="sa-header">
      <h1 class="sa-title">ДАҒДЫЛАРДЫҢ ТАЛДАУЫ</h1>
      <button class="icon-btn" @click="printReport" title="Басып шығару">
        <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5"><path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z" /></svg>
      </button>
    </div>

    <!-- Skill Selector -->
    <div class="sa-skill-selector">
      <label class="selector-label">ДАҒДЫ:</label>
      <select v-model="selectedSkillId" class="selector-dropdown">
        <option value="" disabled>Дағдыны таңдаңыз...</option>
        <option v-for="sk in availableSkills" :key="sk.skillId" :value="sk.skillId">
          {{ sk.gradeLabel }} ({{ sk.skillCode }}) {{ sk.skillName }}
        </option>
      </select>
    </div>

    <!-- No Skill Selected -->
    <div v-if="!selectedSkillId" class="empty-state">
      <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" /></svg>
      <p>Жоғарыдан дағдыны таңдаңыз</p>
    </div>

    <!-- Skill Overview -->
    <div v-else class="sa-content">
      <div class="overview-panel">
        <h2 class="overview-heading">Дағды шолуы - {{ dateLabel || 'Барлық уақыт' }}</h2>
        <div class="overview-grid">
          <!-- Donut Chart: CLASS STATUS -->
          <div class="overview-card donut-card">
            <h3 class="card-label">СЫНЫП КҮЙІ</h3>
            <div class="donut-row">
              <div class="donut-container">
                <svg viewBox="0 0 36 36" class="donut-svg">
                  <!-- Background circle -->
                  <circle cx="18" cy="18" r="15.9155" fill="none" stroke="#e0e0e0" stroke-width="3" />
                  <!-- No Practice (orange) -->
                  <circle cx="18" cy="18" r="15.9155" fill="none"
                    stroke="#ffa726" stroke-width="3"
                    :stroke-dasharray="`${noPracticePercent} ${100 - noPracticePercent}`"
                    :stroke-dashoffset="25" />
                  <!-- Practicing (blue) -->
                  <circle cx="18" cy="18" r="15.9155" fill="none"
                    stroke="#42a5f5" stroke-width="3"
                    :stroke-dasharray="`${practicingPercent} ${100 - practicingPercent}`"
                    :stroke-dashoffset="25 - noPracticePercent" />
                  <!-- Mastered (green) -->
                  <circle cx="18" cy="18" r="15.9155" fill="none"
                    stroke="#66bb6a" stroke-width="3"
                    :stroke-dasharray="`${masteredPercent} ${100 - masteredPercent}`"
                    :stroke-dashoffset="25 - noPracticePercent - practicingPercent" />
                </svg>
              </div>
              <div class="donut-legend">
                <div class="legend-item"><span class="legend-dot bg-green"></span>{{ masteredPercent }}% Mastered</div>
                <div class="legend-item"><span class="legend-dot bg-blue"></span>{{ practicingPercent }}% Practicing</div>
                <div class="legend-item"><span class="legend-dot bg-orange"></span>{{ noPracticePercent }}% No practice</div>
              </div>
            </div>
          </div>

          <!-- Questions Answered -->
          <div class="overview-card stat-card">
            <h3 class="card-label">ЖАУАП БЕРІЛГЕН СҰРАҚТАР</h3>
            <div class="stat-value-col">
              <svg class="stat-icon text-green-500" viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" /></svg>
              <span class="stat-number text-green-500">{{ selectedSkillStats.totalQuestions }}</span>
            </div>
          </div>

          <!-- Time Spent -->
          <div class="overview-card stat-card">
            <h3 class="card-label">ЖҰМСАЛҒАН УАҚЫТ</h3>
            <div class="stat-value-col">
              <svg class="stat-icon text-cyan-500" viewBox="0 0 24 24" fill="currentColor"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z" /></svg>
              <span class="stat-number text-cyan-500">{{ selectedSkillStats.timeSpent }}</span>
            </div>
          </div>

          <!-- Students Who Practiced -->
          <div class="overview-card stat-card">
            <h3 class="card-label">ТӘЖІРИБЕ ЖАСАҒАН ОҚУШЫЛАР</h3>
            <div class="stat-value-col">
              <svg class="stat-icon text-orange-500" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
              <span class="stat-number text-orange-500">{{ selectedSkillStats.studentsPracticed }}</span>
            </div>
            <p class="stat-note">{{ dateLabel || 'Барлық уақыт' }} ішіндегі тәжірибе</p>
          </div>
        </div>
      </div>

      <!-- Class Breakdown -->
      <div class="breakdown-panel">
        <h2 class="breakdown-heading">Сынып бөлінісі</h2>

        <!-- MASTERED -->
        <div class="breakdown-section">
          <div class="section-header bg-mastered">
            <span class="section-icon">🏆</span>
            <span class="section-title">MASTERED</span>
            <span class="section-count">
              <svg class="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
              {{ masteredStudents.length }}
            </span>
          </div>
          <div class="section-body">
            <div v-if="masteredStudents.length === 0" class="section-empty">
              Әзірге бірде-бір оқушы бұл дағдыны меңгерген жоқ. Оларды тәжірибе жасауға ынталандырыңыз!
            </div>
            <div v-else class="student-list">
              <div v-for="st in masteredStudents" :key="st.id" class="student-row">
                <a href="#" @click.prevent="goToQuestions(st.id)" class="student-name-link">{{ st.name }}</a>
                <span class="student-score score-mastered">{{ st.score }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- PRACTICING -->
        <div class="breakdown-section">
          <div class="section-header bg-practicing">
            <span class="section-icon">📘</span>
            <span class="section-title">PRACTICING</span>
            <span class="section-count">
              <svg class="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
              {{ practicingStudents.length }}
            </span>
          </div>
          <div class="section-body">
            <div v-if="practicingStudents.length === 0" class="section-empty">
              Осы дағды бойынша тәжірибе жасап жатқан оқушылар жоқ.
            </div>
            <div v-else class="student-list">
              <div v-for="st in practicingStudents" :key="st.id" class="student-row">
                <a href="#" @click.prevent="goToQuestions(st.id)" class="student-name-link">{{ st.name }}</a>
                <div class="student-score-bar">
                  <div class="score-bar-bg">
                    <div class="score-bar-fill" :style="{ width: st.score + '%' }"></div>
                  </div>
                  <span class="student-score score-practicing">{{ st.score }}</span>
                  <span v-if="st.isTroubleSpot" class="trouble-icon" title="Қиындық">⚠️</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- NO PRACTICE -->
        <div class="breakdown-section">
          <div class="section-header bg-nopractice">
            <span class="section-icon">⏸️</span>
            <span class="section-title">NO PRACTICE</span>
            <span class="section-count">
              <svg class="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
              {{ noPracticeStudents.length }}
            </span>
          </div>
          <div class="section-body">
            <div v-if="noPracticeStudents.length === 0" class="section-empty">
              Барлық оқушылар бұл дағды бойынша тәжірибе жасаған!
            </div>
            <div v-else class="student-list">
              <div v-for="st in noPracticeStudents" :key="st.id" class="student-row">
                <a href="#" @click.prevent="goToQuestions(st.id)" class="student-name-link text-gray-500">{{ st.name }}</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

interface SkillInfo {
  skill_id: number
  skill_name?: string
  skill_code?: string
  grade_label?: string
  grade_number?: number
  best_smartscore?: number
  total_questions?: number
  total_time_seconds?: number
  last_practiced_at?: string | null
}

interface StudentAnalyticsData {
  student_id: string
  full_name: string
  skills?: SkillInfo[]
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

const selectedSkillId = ref('')

// Build unique skills list from all students
interface AvailableSkill {
  skillId: string
  skillName: string
  skillCode: string
  gradeLabel: string
}

const availableSkills = computed<AvailableSkill[]>(() => {
  const map = new Map<string, AvailableSkill>()
  for (const st of props.allStudentsData) {
    if (!st.skills) continue
    for (const sk of st.skills) {
      const id = sk.skill_id.toString()
      if (!map.has(id)) {
        map.set(id, {
          skillId: id,
          skillName: sk.skill_name || 'Дағды',
          skillCode: sk.skill_code || '',
          gradeLabel: sk.grade_label || `${sk.grade_number} сынып`,
        })
      }
    }
  }
  return Array.from(map.values())
})

// Auto-select first skill when list is ready
watch(availableSkills, (skills) => {
  if (skills.length > 0 && !selectedSkillId.value) {
    selectedSkillId.value = skills[0].skillId
  }
}, { immediate: true })

// Per-student data for the selected skill
interface StudentSkillEntry {
  id: string
  name: string
  score: number
  totalQuestions: number
  totalTime: number
  isTroubleSpot: boolean
  practicedInWindow: boolean
}

const studentEntries = computed<StudentSkillEntry[]>(() => {
  if (!selectedSkillId.value) return []
  return props.allStudentsData.map(st => {
    const sk = st.skills?.find(s => s.skill_id.toString() === selectedSkillId.value)
    let practicedInWindow = false
    if (sk && sk.last_practiced_at) {
      if (!props.dateRange?.start) {
        practicedInWindow = true
      } else {
        practicedInWindow = new Date(sk.last_practiced_at) >= props.dateRange.start
      }
    } else if (sk && !props.dateRange?.start) {
      practicedInWindow = true
    }

    const score = (sk?.best_smartscore || 0)
    return {
      id: st.student_id,
      name: st.full_name,
      score: practicedInWindow ? score : 0,
      totalQuestions: practicedInWindow ? (sk?.total_questions || 0) : 0,
      totalTime: practicedInWindow ? (sk?.total_time_seconds || 0) : 0,
      isTroubleSpot: practicedInWindow && (sk?.total_questions || 0) >= 3 && score < 80,
      practicedInWindow,
    }
  })
})

const masteredStudents = computed(() =>
  studentEntries.value.filter(s => s.practicedInWindow && s.score >= 100).sort((a, b) => b.score - a.score)
)
const practicingStudents = computed(() =>
  studentEntries.value.filter(s => s.practicedInWindow && s.score > 0 && s.score < 100).sort((a, b) => b.score - a.score)
)
const noPracticeStudents = computed(() =>
  studentEntries.value.filter(s => !s.practicedInWindow || s.score === 0).sort((a, b) => a.name.localeCompare(b.name))
)

const totalStudents = computed(() => studentEntries.value.length || 1)
const masteredPercent = computed(() => Math.round((masteredStudents.value.length / totalStudents.value) * 100))
const practicingPercent = computed(() => Math.round((practicingStudents.value.length / totalStudents.value) * 100))
const noPracticePercent = computed(() => 100 - masteredPercent.value - practicingPercent.value)

const selectedSkillStats = computed(() => {
  const practiced = studentEntries.value.filter(s => s.practicedInWindow && s.score > 0)
  const totalQ = studentEntries.value.reduce((sum, s) => sum + s.totalQuestions, 0)
  const totalSec = studentEntries.value.reduce((sum, s) => sum + s.totalTime, 0)
  const mins = Math.floor(totalSec / 60)
  let timeStr = '<1 мин'
  if (mins >= 60) {
    const hrs = Math.floor(mins / 60)
    const rem = mins % 60
    timeStr = rem > 0 ? `${hrs} сағ ${rem} мин` : `${hrs} сағ`
  } else if (mins >= 1) {
    timeStr = `${mins} мин`
  }
  return {
    totalQuestions: totalQ,
    timeSpent: timeStr,
    studentsPracticed: practiced.length,
  }
})

const printReport = () => window.print()
const goToQuestions = (studentId: string) => {
  emit('navigate', 'questions', { studentId })
}
</script>

<style scoped>
.ixl-skill-analysis {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
  font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Header */
.sa-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.sa-title {
  font-size: 26px;
  font-weight: 300;
  color: #333;
  letter-spacing: 0.5px;
}
.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #aaa;
  padding: 6px;
  border-radius: 4px;
  transition: color 0.2s;
}
.icon-btn:hover { color: #333; }
.icon-btn svg { width: 20px; height: 20px; }

/* Skill Selector */
.sa-skill-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;
  background: white;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
}
.selector-label {
  font-size: 12px;
  font-weight: 700;
  color: #666;
  letter-spacing: 0.5px;
  white-space: nowrap;
}
.selector-dropdown {
  flex: 1;
  border: none;
  font-size: 14px;
  color: #333;
  background: transparent;
  outline: none;
  cursor: pointer;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #888;
  font-size: 16px;
}

/* Overview Panel */
.overview-panel {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 28px;
  margin-bottom: 28px;
}
.overview-heading {
  font-size: 22px;
  font-weight: 300;
  color: #333;
  margin-bottom: 24px;
}
.overview-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr 1fr;
  gap: 0;
}
.overview-card {
  padding: 16px 20px;
  border-left: 1px solid #eee;
}
.overview-card:first-child { border-left: none; }
.donut-card { padding: 16px 24px; }
.card-label {
  font-size: 11px;
  font-weight: 700;
  color: #888;
  letter-spacing: 0.5px;
  margin-bottom: 16px;
}

/* Donut */
.donut-row {
  display: flex;
  align-items: center;
  gap: 20px;
}
.donut-container { width: 110px; height: 110px; flex-shrink: 0; }
.donut-svg { transform: rotate(-90deg); }
.donut-legend { font-size: 14px; line-height: 2; }
.legend-item { display: flex; align-items: center; gap: 8px; }
.legend-dot {
  width: 12px; height: 12px;
  border-radius: 2px;
  display: inline-block;
  flex-shrink: 0;
}
.bg-green { background: #66bb6a; }
.bg-blue { background: #42a5f5; }
.bg-orange { background: #ffa726; }

/* Stat Cards */
.stat-card { text-align: center; }
.stat-value-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.stat-icon { width: 32px; height: 32px; }
.stat-number { font-size: 32px; font-weight: 700; }
.stat-note { font-size: 11px; color: #999; margin-top: 8px; font-style: italic; }
.text-green-500 { color: #66bb6a; }
.text-cyan-500 { color: #00bcd4; }
.text-orange-500 { color: #ff9800; }

/* Class Breakdown */
.breakdown-panel {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}
.breakdown-heading {
  font-size: 22px;
  font-weight: 300;
  color: #333;
  padding: 24px 28px 16px;
}
.breakdown-section { border-top: 1px solid #eee; }
.section-header {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  color: white;
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.5px;
}
.bg-mastered { background: linear-gradient(135deg, #66bb6a, #43a047); }
.bg-practicing { background: linear-gradient(135deg, #42a5f5, #1e88e5); }
.bg-nopractice { background: linear-gradient(135deg, #ffa726, #fb8c00); }
.section-icon { font-size: 18px; margin-right: 10px; }
.section-title { flex: 1; }
.section-count {
  display: flex;
  align-items: center;
  font-size: 14px;
}
.section-body { padding: 12px 20px; }
.section-empty {
  color: #888;
  font-size: 14px;
  font-style: italic;
  padding: 12px 0;
}

/* Student List */
.student-list { }
.student-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 4px;
  border-bottom: 1px solid #f5f5f5;
}
.student-row:last-child { border-bottom: none; }
.student-name-link {
  color: #333;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.15s;
}
.student-name-link:hover { color: #00bcd4; text-decoration: underline; }
.student-score {
  font-weight: 700;
  font-size: 14px;
  min-width: 30px;
  text-align: right;
}
.score-mastered { color: #43a047; }
.score-practicing { color: #1e88e5; }
.student-score-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}
.score-bar-bg {
  width: 120px;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}
.score-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #42a5f5, #1e88e5);
  border-radius: 4px;
  transition: width 0.3s ease;
}
.trouble-icon { font-size: 14px; }
.w-4 { width: 16px; }
.h-4 { height: 16px; }
.w-5 { width: 20px; }
.h-5 { height: 20px; }
.w-16 { width: 64px; }
.h-16 { height: 64px; }
.mx-auto { margin-left: auto; margin-right: auto; }
.mb-4 { margin-bottom: 16px; }
.text-gray-300 { color: #d1d5db; }
.text-gray-500 { color: #9ca3af; }
.inline { display: inline; }
.mr-1 { margin-right: 4px; }
</style>

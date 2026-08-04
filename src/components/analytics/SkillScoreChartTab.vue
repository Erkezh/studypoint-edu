<template>
  <div class="skill-score-chart">
    <!-- Header -->
    <div class="ssc-header">
      <h1 class="ssc-title">ДАҒДЫ ҰПАЙЛАРЫНЫҢ КЕСТЕСІ</h1>
      <button class="icon-btn" @click="printReport" title="Басып шығару">
        <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5"><path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z" /></svg>
      </button>
    </div>

    <!-- Skill Selector -->
    <div class="ssc-skill-selector">
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
      <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" /></svg>
      <p>Жоғарыдан дағдыны таңдаңыз</p>
    </div>

    <!-- Content -->
    <div v-else class="ssc-content">
      <!-- Performance Overview Panel -->
      <div class="performance-panel">
        <h2 class="panel-heading">Дағдылар бойынша шолу - {{ dateLabel || 'Барлық уақыт' }}</h2>

        <div class="chart-area">
          <!-- Donut Chart -->
          <div class="donut-wrapper">
            <svg viewBox="0 0 200 200" class="donut-chart">
              <!-- Background circle -->
              <circle cx="100" cy="100" r="80" fill="none" stroke="#e8e8e8" stroke-width="32"/>
              <!-- No Practice (gray) -->
              <circle cx="100" cy="100" r="80" fill="none"
                stroke="#d0d0d0" stroke-width="32"
                :stroke-dasharray="circumference"
                :stroke-dashoffset="0"
                transform="rotate(-90 100 100)" />
              <!-- Practiced (blue) -->
              <circle cx="100" cy="100" r="80" fill="none"
                stroke="#29b6f6" stroke-width="32"
                :stroke-dasharray="`${practicedArc} ${circumference - practicedArc}`"
                :stroke-dashoffset="0"
                transform="rotate(-90 100 100)" />
              <!-- Proficiency (teal/green) -->
              <circle cx="100" cy="100" r="80" fill="none"
                stroke="#4dd0e1" stroke-width="32"
                :stroke-dasharray="`${proficiencyArc} ${circumference - proficiencyArc}`"
                :stroke-dashoffset="0"
                transform="rotate(-90 100 100)" />
              <!-- Mastery (green) -->
              <circle cx="100" cy="100" r="80" fill="none"
                stroke="#9ccc65" stroke-width="32"
                :stroke-dasharray="`${masteryArc} ${circumference - masteryArc}`"
                :stroke-dashoffset="0"
                transform="rotate(-90 100 100)" />
              <!-- Center white circle -->
              <circle cx="100" cy="100" r="64" fill="white" />
            </svg>
            <!-- Center Text -->
            <div class="donut-center-text">
              <span class="progress-label">Прогресс:</span>
              <span class="progress-value">{{ progressPercent }}%</span>
            </div>
          </div>

          <!-- Legend -->
          <div class="chart-legend">
            <div class="legend-row">
              <span class="legend-color mastery"></span>
              <span class="legend-percent">{{ masteryPercent }}%</span>
              <span class="legend-text">Меңгеру</span>
            </div>
            <div class="legend-row">
              <span class="legend-color proficiency"></span>
              <span class="legend-percent">{{ proficiencyPercent }}%</span>
              <span class="legend-text">Біліктілік</span>
            </div>
            <div class="legend-row">
              <span class="legend-color practiced"></span>
              <span class="legend-percent">{{ practicedPercent }}%</span>
              <span class="legend-text">Жаттыққан</span>
            </div>
            <div class="legend-row">
              <span class="legend-color no-practice"></span>
              <span class="legend-percent">{{ noPracticePercent }}%</span>
              <span class="legend-text">Тәжірибе жоқ</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Scores Table -->
      <div class="scores-panel">
        <h2 class="panel-heading">Ұпайлар</h2>
        <p class="panel-sub">Бұл оқу жылындағы ағымдағы ұпайлар немесе бұрынғы меңгерулер.</p>
        <table class="scores-table">
          <thead>
            <tr>
              <th class="th-name">АТЫ-ЖӨНІ</th>
              <th class="th-score">SMARTSCORE</th>
              <th class="th-questions">ЖАУАП БЕРІЛГЕН СҰРАҚТАР</th>
              <th class="th-time">ЖҰМСАЛҒАН УАҚЫТ</th>
              <th class="th-last">СОҢҒЫ ТӘЖІРИБЕ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="st in sortedStudents" :key="st.id" class="score-tr">
              <td class="td-name">{{ st.name }}</td>
              <td class="td-score-val">
                <span v-if="st.practicedInWindow" class="score-num" :style="{ color: getScoreColor(st.score) }">{{ st.score }}</span>
                <span v-else class="score-dash"></span>
              </td>
              <td class="td-questions">
                <span v-if="st.practicedInWindow && st.totalQuestions > 0">{{ st.totalQuestions }}</span>
              </td>
              <td class="td-time">
                <span v-if="st.practicedInWindow && st.totalTime > 0">{{ formatTime(st.totalTime) }}</span>
              </td>
              <td class="td-last">
                <span v-if="st.practicedInWindow && st.lastPracticed">{{ formatDateLabel(st.lastPracticed) }}</span>
              </td>
            </tr>
          </tbody>
        </table>
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
  last_smartscore?: number
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

const selectedSkillId = ref('')

// Build unique skills list
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

// Auto-select first skill
watch(availableSkills, (skills) => {
  if (skills.length > 0 && !selectedSkillId.value) {
    selectedSkillId.value = skills[0].skillId
  }
}, { immediate: true })

// Per-student entries for selected skill
interface StudentEntry {
  id: string
  name: string
  score: number
  totalQuestions: number
  totalTime: number
  lastPracticed: string | null
  practicedInWindow: boolean
}

const studentEntries = computed<StudentEntry[]>(() => {
  if (!selectedSkillId.value) return []
  return props.allStudentsData.map(st => {
    const sk = st.skills?.find(s => s.skill_id.toString() === selectedSkillId.value)
    // The parent has already applied the selected date range to this skill list.
    // A non-zero question count therefore means the student practiced this skill.
    const practicedInWindow = Boolean(sk && Number(sk.total_questions || 0) > 0)
    const score = Math.max(Number(sk?.best_smartscore || 0), Number(sk?.last_smartscore || 0))
    return {
      id: st.student_id,
      name: st.full_name,
      score: practicedInWindow ? score : 0,
      totalQuestions: practicedInWindow ? (sk?.total_questions || 0) : 0,
      totalTime: practicedInWindow ? (sk?.total_time_seconds || 0) : 0,
      lastPracticed: practicedInWindow ? (sk?.last_practiced_at || null) : null,
      practicedInWindow,
    }
  })
})

const sortedStudents = computed(() =>
  [...studentEntries.value].sort((a, b) => b.score - a.score || a.name.localeCompare(b.name))
)

// Counts
const totalStudents = computed(() => studentEntries.value.length || 1)
const masteryCount = computed(() => studentEntries.value.filter(s => s.practicedInWindow && s.score >= 100).length)
const proficiencyCount = computed(() => studentEntries.value.filter(s => s.practicedInWindow && s.score >= 80 && s.score < 100).length)
const practicedCount = computed(() => studentEntries.value.filter(s => s.practicedInWindow && s.score < 80).length)

const masteryPercent = computed(() => Math.round((masteryCount.value / totalStudents.value) * 100))
const proficiencyPercent = computed(() => Math.round((proficiencyCount.value / totalStudents.value) * 100))
const practicedPercent = computed(() => Math.round((practicedCount.value / totalStudents.value) * 100))
const noPracticePercent = computed(() => 100 - masteryPercent.value - proficiencyPercent.value - practicedPercent.value)
const progressPercent = computed(() => masteryPercent.value + proficiencyPercent.value + practicedPercent.value)

// Donut arcs
const circumference = 2 * Math.PI * 80 // ≈ 502.65
const masteryArc = computed(() => (masteryPercent.value / 100) * circumference)
const proficiencyArc = computed(() => ((masteryPercent.value + proficiencyPercent.value) / 100) * circumference)
const practicedArc = computed(() => ((masteryPercent.value + proficiencyPercent.value + practicedPercent.value) / 100) * circumference)

const getScoreColor = (score: number) => {
  if (score >= 100) return '#7cb342' // Greenish
  if (score >= 80) return '#7cb342'
  if (score > 0) return '#7cb342' // Keeping it green as per IXL scores list usually
  return '#666'
}

const formatTime = (totalSec: number) => {
  const mins = Math.floor(totalSec / 60)
  if (mins < 1) return '<1 мин'
  return `${mins} мин`
}

const formatDateLabel = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 3600 * 24))

  if (diffDays === 0) return 'Бүгін'
  if (diffDays === 1) return 'Кеше'

  const months = ['Қаңтар', 'Ақпан', 'Наурыз', 'Сәуір', 'Мамыр', 'Маусым', 'Шілде', 'Тамыз', 'Қыркүйек', 'Қазан', 'Қараша', 'Желтоқсан']
  return `${date.getDate()} ${months[date.getMonth()]}`
}

const printReport = () => window.print()
</script>

<style scoped>
.skill-score-chart {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
  font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Header */
.ssc-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.ssc-title {
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
.ssc-skill-selector {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 12px 16px;
  gap: 10px;
  margin-bottom: 24px;
  max-width: 500px;
}
.selector-label {
  font-size: 12px;
  font-weight: 700;
  color: #666;
  letter-spacing: 0.5px;
  white-space: nowrap;
}
.selector-dropdown {
  border: none;
  font-size: 14px;
  color: #333;
  background: transparent;
  outline: none;
  cursor: pointer;
  flex: 1;
  min-width: 200px;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px;
  color: #aaa;
}
.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  color: #ddd;
}

/* Performance Panel */
.performance-panel {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}
.panel-heading {
  font-size: 18px;
  font-weight: 400;
  color: #444;
  margin-bottom: 24px;
}
.panel-sub {
  font-size: 13px;
  color: #888;
  margin-bottom: 16px;
}

/* Chart Area */
.chart-area {
  display: flex;
  align-items: center;
  gap: 48px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Donut */
.donut-wrapper {
  position: relative;
  width: 220px;
  height: 220px;
}
.donut-chart {
  width: 100%;
  height: 100%;
}
.donut-center-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}
.progress-label {
  display: block;
  font-size: 12px;
  color: #999;
  margin-bottom: 2px;
}
.progress-value {
  display: block;
  font-size: 28px;
  font-weight: 300;
  color: #333;
}

/* Legend */
.chart-legend {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.legend-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  flex-shrink: 0;
}
.legend-color.mastery { background: #9ccc65; }
.legend-color.proficiency { background: #4dd0e1; }
.legend-color.practiced { background: #29b6f6; }
.legend-color.no-practice { background: #d0d0d0; }
.legend-percent {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  min-width: 40px;
}
.legend-text {
  font-size: 14px;
  color: #666;
}

/* Scores Panel */
.scores-panel {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 24px;
}
.scores-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}
.scores-table th {
  text-align: left;
  font-size: 11px;
  font-weight: 700;
  color: #777;
  padding: 12px;
  background: #eef6f8;
  border: 1px solid #ddd;
}
.th-score, .th-questions, .th-time, .th-last {
  text-align: center;
}
.score-tr {
  border-bottom: 1px solid #f0f0f0;
}
.score-tr:hover {
  background: #f5fbfc;
}
.td-name {
  padding: 12px;
  font-size: 13px;
  color: #666;
  border: 1px solid #eee;
}
.td-score-val, .td-questions, .td-time, .td-last {
  padding: 12px;
  text-align: center;
  border: 1px solid #eee;
  font-size: 13px;
  color: #666;
}
.score-num {
  font-weight: 700;
  font-size: 16px;
}
.score-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  color: white;
}
.badge-mastery { background: #9ccc65; }
.badge-proficiency { background: #4dd0e1; }
.badge-practiced { background: #29b6f6; }
.score-dash {
  color: #ccc;
  font-size: 16px;
}
.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}
.status-mastery { background: #e8f5e9; color: #558b2f; }
.status-proficiency { background: #e0f7fa; color: #00695c; }
.status-practiced { background: #e3f2fd; color: #1565c0; }
.status-none { background: #f5f5f5; color: #999; }

.w-5 { width: 20px; }
.h-5 { height: 20px; }
</style>

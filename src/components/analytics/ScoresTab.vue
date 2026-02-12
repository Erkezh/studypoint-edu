<template>
  <div>
    <!-- Date filter -->
    <div class="scores-date-filter">
      <label class="scores-filter-label">УАҚЫТ АРАЛЫҒЫ:</label>
      <select v-model="scoreDateRange" class="scores-filter-select">
        <option value="all">Барлық уақыт</option>
        <option value="week">Осы апта</option>
        <option value="month">Осы ай</option>
      </select>
    </div>

    <div class="scores-main-card">
      <div class="scores-card-header">
        <h1 class="scores-card-title">ҰПАЙЛАР КЕСТЕСІ</h1>
        <button class="print-btn" @click="printReport">
          <svg class="print-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z" />
          </svg>
        </button>
      </div>

      <!-- Grade Picker Dropdown -->
      <div class="scores-grade-picker">
        <div class="scores-grade-dropdown" @click="showScoreGradeDropdown = !showScoreGradeDropdown">
          <span class="scores-grade-label">СЫНЫП:</span>
          <span class="scores-grade-value">{{ scoreGrade === -1 ? 'Pre-K' : scoreGrade }}</span>
          <span class="scores-grade-caret">▼</span>
        </div>
        <div v-if="showScoreGradeDropdown" class="scores-grade-options">
          <div
            v-for="g in gradeOptions"
            :key="g.value"
            class="scores-grade-option"
            :class="{ active: scoreGrade === g.value }"
            @click="scoreGrade = g.value; showScoreGradeDropdown = false"
          >
            <span class="scores-grade-check">{{ scoreGrade === g.value ? '✓' : '' }}</span>
            <span>{{ g.label }}</span>
          </div>
        </div>
      </div>

      <!-- Performance Overview -->
      <div class="scores-overview-card">
        <h2 class="scores-overview-title">
          {{ userName }} нәтижелері — {{ scoreDateRange === 'all' ? 'Барлық уақыт' : scoreDateRange === 'week' ? 'Осы апта' : 'Осы ай' }}
        </h2>
        <div class="chart-section">
          <div class="donut-chart">
            <svg viewBox="0 0 100 100" class="chart-svg">
              <circle cx="50" cy="50" r="40" fill="transparent" stroke="#e0e0e0" stroke-width="12" />
              <circle v-for="(segment, index) in scoreChartSegments" :key="index" cx="50" cy="50" r="40"
                fill="transparent" :stroke="segment.color" stroke-width="12" :stroke-dasharray="segment.dashArray"
                :stroke-dashoffset="segment.offset" transform="rotate(-90 50 50)" />
            </svg>
            <div class="chart-center">
              <span class="chart-label-small">Прогресс:</span>
              <span class="chart-value">{{ scoreBreakdown.progressPercent }}%</span>
            </div>
          </div>
          <div class="chart-legend">
            <div class="legend-item">
              <span class="legend-dot" style="background-color: #8BC34A"></span>
              <span class="legend-percent">{{ scoreBreakdown.masteryPercent }}%</span>
              <span class="legend-label">Меңгерілген (Mastery)</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background-color: #4CAF50"></span>
              <span class="legend-percent">{{ scoreBreakdown.proficiencyPercent }}%</span>
              <span class="legend-label">Шеберлік (Proficiency)</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background-color: #2196F3"></span>
              <span class="legend-percent">{{ scoreBreakdown.practicedPercent }}%</span>
              <span class="legend-label">Жаттығылған (Practiced)</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background-color: #e0e0e0"></span>
              <span class="legend-percent">{{ scoreBreakdown.noPracticePercent }}%</span>
              <span class="legend-label">Жаттығылмаған</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Scores Table: ALL skills grouped by topic -->
    <div class="skills-table-section">
      <h3 class="section-subtitle">Ұпайлар</h3>
      <p class="scores-viewing-hint">{{ scoreGrade >= 0 ? scoreGrade + ' сынып' : 'Pre-K' }} бойынша дағдылар</p>
      <div v-if="allGradeSkills.length === 0" class="empty-state">
        <p>Бұл сыныпта дағдылар табылмады</p>
      </div>
      <table v-else class="scores-table">
        <thead>
          <tr>
            <th class="skill-col">ДАҒДЫ</th>
            <th class="score-col">SMARTSCORE</th>
            <th class="num-col">СҰРАҚТАР</th>
            <th class="num-col">УАҚЫТ</th>
            <th class="date-col">СОҢҒЫ ПРАКТИКА</th>
          </tr>
        </thead>
        <tbody v-for="group in allSkillsGroupedByTopic" :key="group.topicTitle">
          <tr class="topic-header-row">
            <td colspan="5" class="topic-header-cell">
              <span class="topic-header-icon">▼</span>
              {{ group.topicTitle }}
            </td>
          </tr>
          <tr v-for="skill in group.skills" :key="skill.id" :class="{ 'skill-row-practiced': skill.hasPractice }">
            <td class="skill-col">
              <span class="skill-name-text">{{ skill.title }}</span>
            </td>
            <td class="score-col">
              <template v-if="skill.hasPractice">
                <div class="score-bar-container">
                  <div class="score-bar-track">
                    <div class="score-bar-fill" :style="{ width: skill.best_smartscore + '%', backgroundColor: getScoreColor(skill.best_smartscore) }"></div>
                  </div>
                  <span class="score-value" :style="{ color: getScoreColor(skill.best_smartscore) }">{{ skill.best_smartscore }}</span>
                </div>
              </template>
            </td>
            <td class="num-col">{{ skill.hasPractice ? skill.total_questions : '' }}</td>
            <td class="num-col">{{ skill.hasPractice ? formatTimeShort(skill.total_time_seconds) : '' }}</td>
            <td class="date-col">{{ skill.hasPractice ? formatLastPracticed(skill.last_practiced_at) : '' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { useAuthStore } from '@/stores/auth'
import { catalogApi } from '@/api/catalog'
import type { SkillListItem } from '@/types/api'

const analyticsStore = useAnalyticsStore()
const authStore = useAuthStore()

const userName = computed(() => authStore.user?.full_name || 'Сіздің')

const scoreGrade = ref<number>(authStore.user?.profile?.grade_level ?? 6)
const scoreDateRange = ref<string>('all')
const showScoreGradeDropdown = ref(false)

const gradeOptions = [
  { value: -1, label: 'Pre-K' },
  { value: 0, label: '0' },
  { value: 1, label: '1' },
  { value: 2, label: '2' },
  { value: 3, label: '3' },
  { value: 4, label: '4' },
  { value: 5, label: '5' },
  { value: 6, label: '6' },
  { value: 7, label: '7' },
  { value: 8, label: '8' },
  { value: 9, label: '9' },
  { value: 10, label: '10' },
  { value: 11, label: '11' },
  { value: 12, label: '12' },
]

// Close dropdown when clicking outside
const handleClickOutside = (e: MouseEvent) => {
  const picker = document.querySelector('.scores-grade-picker')
  if (picker && !picker.contains(e.target as Node)) {
    showScoreGradeDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  loadGradeSkills()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// All catalog skills for the selected grade
const allGradeSkills = ref<SkillListItem[]>([])

const loadGradeSkills = async () => {
  try {
    const response = await catalogApi.getSkills({ grade_number: scoreGrade.value, page_size: 500 })
    if (response.data) {
      allGradeSkills.value = response.data
    }
  } catch (err) {
    console.error('Failed to load grade skills:', err)
  }
}

watch(scoreGrade, () => {
  loadGradeSkills()
})

const printReport = () => {
  window.print()
}

// Skills filtered by grade (only practiced)
const scoreGradeFilteredSkills = computed(() => {
  return analyticsStore.skills.filter(skill => {
    if ((skill.total_questions || 0) === 0) return false
    const gradeNumber = (skill as Record<string, unknown>).grade_number as number | undefined
    if (gradeNumber !== undefined) {
      return gradeNumber === scoreGrade.value
    }
    return true
  })
})

// Practiced skill lookup map
const practicedSkillMap = computed(() => {
  const map = new Map<number, Record<string, unknown>>()
  for (const skill of scoreGradeFilteredSkills.value) {
    map.set(skill.skill_id, skill as Record<string, unknown>)
  }
  return map
})

// All skills grouped by topic, merged with analytics progress
const allSkillsGroupedByTopic = computed(() => {
  const groups = new Map<string, { topicTitle: string; skills: Array<{
    id: number
    title: string
    hasPractice: boolean
    best_smartscore: number
    total_questions: number
    total_time_seconds: number
    last_practiced_at: string
  }> }>()

  for (const skill of allGradeSkills.value) {
    const topicTitle = skill.topic_title || 'Тақырыпсыз'
    if (!groups.has(topicTitle)) {
      groups.set(topicTitle, { topicTitle, skills: [] })
    }
    const practiced = practicedSkillMap.value.get(skill.id)
    groups.get(topicTitle)!.skills.push({
      id: skill.id,
      title: skill.title,
      hasPractice: !!practiced,
      best_smartscore: practiced ? ((practiced.best_smartscore as number) || 0) : 0,
      total_questions: practiced ? ((practiced.total_questions as number) || 0) : 0,
      total_time_seconds: practiced ? ((practiced.total_time_seconds as number) || 0) : 0,
      last_practiced_at: practiced ? ((practiced.last_practiced_at as string) || (practiced.last_practiced as string) || '') : '',
    })
  }

  return Array.from(groups.values())
})

const scoreBreakdown = computed(() => {
  let totalSkills = allGradeSkills.value.length

  if (totalSkills === 0) {
    const skillsByGrade = analyticsStore.overview?.total_skills_by_grade
    if (skillsByGrade) {
      totalSkills = skillsByGrade[String(scoreGrade.value)] || 0
    }
  }

  totalSkills = Math.max(totalSkills, 1)

  const practiced = scoreGradeFilteredSkills.value
  let mastery = 0
  let proficiency = 0
  let practicedOnly = 0

  for (const skill of practiced) {
    const score = skill.best_smartscore || 0
    if (score >= 100) mastery++
    else if (score >= 80) proficiency++
    else if (score >= 1) practicedOnly++
  }

  const noPractice = Math.max(0, totalSkills - mastery - proficiency - practicedOnly)
  const progressPercent = Math.round(((mastery + proficiency) / totalSkills) * 100)

  return {
    masteryPercent: Math.round((mastery / totalSkills) * 100),
    proficiencyPercent: Math.round((proficiency / totalSkills) * 100),
    practicedPercent: Math.round((practicedOnly / totalSkills) * 100),
    noPracticePercent: Math.round((noPractice / totalSkills) * 100),
    mastery,
    proficiency,
    practicedOnly,
    noPractice,
    progressPercent,
  }
})

const scoreChartSegments = computed(() => {
  const data = scoreBreakdown.value
  const total = data.mastery + data.proficiency + data.practicedOnly + data.noPractice || 1
  const circumference = 2 * Math.PI * 40
  let offset = 0

  const colors = [
    { count: data.mastery, color: '#8BC34A' },
    { count: data.proficiency, color: '#4CAF50' },
    { count: data.practicedOnly, color: '#2196F3' },
  ]

  return colors.filter(c => c.count > 0).map(c => {
    const segmentSize = (c.count / total) * circumference
    const segment = {
      color: c.color,
      dashArray: `${segmentSize} ${circumference - segmentSize}`,
      offset: -offset,
    }
    offset += segmentSize
    return segment
  })
})

const getScoreColor = (score: number): string => {
  if (score >= 100) return '#8BC34A'
  if (score >= 80) return '#4CAF50'
  if (score >= 50) return '#FF9800'
  return '#F44336'
}

const formatTimeShort = (seconds: number): string => {
  if (!seconds || seconds === 0) return '<1 мин'
  const mins = Math.floor(seconds / 60)
  if (mins < 1) return '<1 мин'
  if (mins >= 60) {
    const hrs = Math.floor(mins / 60)
    const remainMins = mins % 60
    return remainMins > 0 ? `${hrs} сағ ${remainMins} мин` : `${hrs} сағ`
  }
  return `${mins} мин`
}

const formatLastPracticed = (dateString: string): string => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  const now = new Date()
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Бүгін'
  if (diffDays === 1) return 'Кеше'
  if (diffDays < 7) return `${diffDays} күн бұрын`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} апта бұрын`
  return date.toLocaleDateString('kk-KZ', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.scores-date-filter {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  padding: 12px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.scores-filter-label {
  font-size: 12px;
  font-weight: 700;
  color: #666;
  letter-spacing: 0.5px;
}

.scores-filter-select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  background: white;
  cursor: pointer;
}

.scores-main-card {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  margin-bottom: 24px;
}

.scores-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.scores-card-title {
  font-size: 28px;
  font-weight: 300;
  color: #333;
  letter-spacing: 1px;
}

.print-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  color: #999;
  transition: color 0.2s;
}

.print-btn:hover {
  color: #333;
}

.print-icon {
  width: 20px;
  height: 20px;
}

.scores-grade-picker {
  position: relative;
  margin-bottom: 24px;
  width: fit-content;
}

.scores-grade-dropdown {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  background: #f9f9f9;
  border: 1px solid #ccc;
  border-radius: 6px;
  cursor: pointer;
  user-select: none;
  transition: border-color 0.15s;
}

.scores-grade-dropdown:hover {
  border-color: #999;
}

.scores-grade-label {
  font-size: 13px;
  font-weight: 700;
  color: #555;
  letter-spacing: 0.5px;
}

.scores-grade-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  min-width: 30px;
}

.scores-grade-caret {
  font-size: 10px;
  color: #888;
  margin-left: 4px;
}

.scores-grade-options {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 100;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  min-width: 160px;
  max-height: 320px;
  overflow-y: auto;
  margin-top: 4px;
}

.scores-grade-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  cursor: pointer;
  font-size: 15px;
  color: #333;
  transition: background 0.1s;
}

.scores-grade-option:hover {
  background: #f0f0f0;
}

.scores-grade-option.active {
  color: #4CAF50;
  font-weight: 600;
}

.scores-grade-check {
  width: 16px;
  font-size: 14px;
  color: #4CAF50;
  font-weight: 700;
}

.scores-overview-card {
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 10px;
  padding: 28px;
}

.scores-overview-title {
  font-size: 20px;
  font-weight: 400;
  color: #333;
  margin-bottom: 24px;
  text-align: center;
}

.chart-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 48px;
  padding: 24px 0;
}

.donut-chart {
  width: 200px;
  height: 200px;
  position: relative;
}

.chart-svg {
  width: 100%;
  height: 100%;
}

.chart-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.chart-label-small {
  font-size: 12px;
  color: #999;
  display: block;
}

.chart-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
}

.chart-legend {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
}

.legend-dot {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 3px;
  margin-right: 8px;
  vertical-align: middle;
  flex-shrink: 0;
}

.legend-percent {
  font-size: 18px;
  font-weight: 700;
  color: #333;
  margin-right: 8px;
  min-width: 40px;
}

.legend-label {
  font-size: 14px;
  color: #666;
}

.scores-viewing-hint {
  font-size: 14px;
  color: #888;
  font-style: italic;
  margin-bottom: 16px;
}

.section-subtitle {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.skills-table-section {
  background: white;
  border-radius: 12px;
  padding: 28px;
  margin-top: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.scores-table {
  width: 100%;
  border-collapse: collapse;
}

.scores-table thead tr {
  background: linear-gradient(135deg, #4CAF50, #43A047);
  color: white;
}

.scores-table th {
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-align: left;
  white-space: nowrap;
}

.scores-table td {
  padding: 14px 16px;
  font-size: 14px;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
}

.scores-table tbody tr:hover {
  background: #f8fffe;
}

.topic-header-row {
  background: linear-gradient(135deg, #0bb5c4, #19a5b4) !important;
}

.topic-header-row:hover {
  background: linear-gradient(135deg, #0bb5c4, #19a5b4) !important;
}

.topic-header-cell {
  color: white !important;
  font-weight: 700 !important;
  font-size: 13px !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 10px 16px !important;
  border: none !important;
}

.topic-header-icon {
  margin-right: 8px;
  font-size: 10px;
}

.skill-row-practiced {
  background: #fafffe;
}

.scores-table .skill-col {
  min-width: 200px;
}

.scores-table .score-col {
  min-width: 180px;
}

.scores-table .num-col {
  text-align: center;
  min-width: 80px;
}

.scores-table .date-col {
  text-align: right;
  min-width: 120px;
  color: #888;
}

.score-bar-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-bar-track {
  flex: 1;
  height: 10px;
  background: #e8e8e8;
  border-radius: 5px;
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.4s ease;
}

.score-value {
  font-size: 16px;
  font-weight: 700;
  min-width: 28px;
  text-align: right;
}

.skill-name-text {
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 48px;
  color: #888;
}

@media (max-width: 768px) {
  .chart-section {
    flex-direction: column;
  }

  .scores-table .skill-col {
    min-width: 140px;
  }

  .scores-table .score-col {
    min-width: 120px;
  }
}
</style>

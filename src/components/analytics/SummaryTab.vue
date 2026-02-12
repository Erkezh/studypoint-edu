<template>
  <div>
    <div class="summary-header">
      <h1 class="summary-title">ҚОРЫТЫНДЫ ЕСЕП</h1>
      <button class="print-btn" @click="printReport">
        <svg class="print-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z" />
        </svg>
      </button>
    </div>

    <!-- Accomplishments Card -->
    <div class="accomplishments-card">
      <h2 class="card-title">Сіздің StudyPoint жетістіктеріңіз</h2>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-icon answered">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" />
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-label">ЖАУАП БЕРІЛДІ</span>
            <span class="stat-value">{{ filteredTotalQuestions }}</span>
            <span class="stat-sublabel">СҰРАҚТАР</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon spent">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z" />
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-label">ЖҰМСАЛҒАН</span>
            <span class="stat-value">{{ formatTimeMinutes(filteredTotalTime) }}</span>
            <span class="stat-sublabel">ОҚУ УАҚЫТЫ</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon progress">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-label">ПРОГРЕСС ЖАСАЛДЫ</span>
            <span class="stat-value">{{ skillsWithProgress.length }}</span>
            <span class="stat-sublabel">ДАҒДЫЛАР</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Skills by Topic Chart -->
    <div class="skills-practiced-card">
      <h3 class="section-title">МЕҢГЕРІЛГЕН МАТЕМАТИКА ДАҒДЫЛАРЫ</h3>
      <div class="chart-section">
        <div class="donut-chart">
          <svg viewBox="0 0 100 100" class="chart-svg">
            <circle v-if="skillsByTopic.length === 0" cx="50" cy="50" r="40"
              fill="transparent" stroke="#e0e0e0" stroke-width="12" />
            <circle v-for="(segment, index) in topicChartSegments" :key="index" cx="50" cy="50" r="40"
              fill="transparent" :stroke="segment.color" stroke-width="12" :stroke-dasharray="segment.dashArray"
              :stroke-dashoffset="segment.offset" transform="rotate(-90 50 50)" />
          </svg>
          <div class="chart-center">
            <span class="chart-value">{{ skillsWithProgress.length }}</span>
            <span class="chart-label">дағды</span>
          </div>
        </div>
        <div class="chart-legend">
          <div v-for="(topic, index) in skillsByTopic" :key="topic.name" class="legend-item">
            <span class="legend-dot" :style="{ backgroundColor: chartColors[index % chartColors.length] }"></span>
            <span class="legend-label">{{ topic.name }}</span>
          </div>
          <div v-if="skillsByTopic.length === 0" class="legend-item">
            <span class="legend-label text-gray">Әлі дағдылар жоқ</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Skills Table -->
    <div class="skills-table-section">
      <h3 class="section-subtitle">Сіз мына дағдыларды меңгердіңіз:</h3>
      <div v-if="completedTopics.length === 0" class="empty-state">
        <p>Әлі өткен дағдылар жоқ. Практиканы бастаңыз!</p>
      </div>
      <table v-else class="skills-table">
        <thead>
          <tr>
            <th @click="sortBy('skill')">
              Дағды
              <span class="sort-icon inline-block ml-1">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" /></svg>
              </span>
            </th>
            <th @click="sortBy('lastPracticed')">
              Соңғы жаттығу
              <span class="sort-icon inline-block ml-1">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" /></svg>
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="skill in sortedSkills" :key="skill.skill_id">
            <td>
              <router-link :to="`/skill/${skill.skill_id}`" class="skill-link">
                {{ skill.name }}
              </router-link>
            </td>
            <td class="date-cell">{{ formatLastPracticed(skill.last_practiced) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'

const props = defineProps<{
  gradeFrom: number
  gradeTo: number
  skillNames: Map<number, string>
}>()

const analyticsStore = useAnalyticsStore()

const chartColors = ['#00BCD4', '#FF9800', '#4CAF50', '#9C27B0', '#F44336', '#2196F3']
const sortField = ref<string>('lastPracticed')
const sortDirection = ref<'asc' | 'desc'>('desc')

const printReport = () => {
  window.print()
}

const formatTimeMinutes = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
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

// Filtered totals based on grade range
const filteredTotalQuestions = computed(() => {
  return analyticsStore.skills.reduce((sum, skill) => {
    const gradeNumber = (skill as Record<string, unknown>).grade_number as number | undefined
    if (gradeNumber !== undefined) {
      if (gradeNumber >= props.gradeFrom && gradeNumber <= props.gradeTo) {
        return sum + (skill.total_questions || 0)
      }
      return sum
    }
    return sum + (skill.total_questions || 0)
  }, 0)
})

const filteredTotalTime = computed(() => {
  return analyticsStore.skills.reduce((sum, skill) => {
    const gradeNumber = (skill as Record<string, unknown>).grade_number as number | undefined
    const totalTime = (skill as Record<string, unknown>).total_time_seconds as number | undefined
    if (gradeNumber !== undefined) {
      if (gradeNumber >= props.gradeFrom && gradeNumber <= props.gradeTo) {
        return sum + (totalTime || 0)
      }
      return sum
    }
    return sum + (totalTime || 0)
  }, 0)
})

// Skills with progress, filtered by grade range
const skillsWithProgress = computed(() => {
  return analyticsStore.skills.filter(skill => {
    if ((skill.total_questions || 0) === 0) return false
    const gradeNumber = (skill as Record<string, unknown>).grade_number as number | undefined
    if (gradeNumber !== undefined) {
      return gradeNumber >= props.gradeFrom && gradeNumber <= props.gradeTo
    }
    return true
  })
})

// Completed topics (SmartScore = 100)
const completedTopics = computed(() => {
  return analyticsStore.skills
    .filter(skill => {
      if ((skill.best_smartscore || 0) < 100) return false
      const gradeNumber = (skill as Record<string, unknown>).grade_number as number | undefined
      if (gradeNumber !== undefined) {
        return gradeNumber >= props.gradeFrom && gradeNumber <= props.gradeTo
      }
      return true
    })
    .map(skill => {
      const apiName = (skill as Record<string, unknown>).skill_name as string | undefined
      return {
        skill_id: skill.skill_id,
        name: apiName || props.skillNames.get(skill.skill_id) || `Дағды ${skill.skill_id}`,
        best_smartscore: skill.best_smartscore || 0,
        total_questions: skill.total_questions || 0,
        accuracy_percent: skill.accuracy_percent || 0,
        last_practiced: skill.last_practiced_at || '',
      }
    })
})

// Skills grouped by topic
const skillsByTopic = computed(() => {
  const topicMap = new Map<string, { name: string; count: number }>()

  for (const skill of skillsWithProgress.value) {
    const rec = skill as Record<string, unknown>
    const topicTitle = (rec.topic_title as string) || 'Басқа'

    if (topicMap.has(topicTitle)) {
      topicMap.get(topicTitle)!.count++
    } else {
      topicMap.set(topicTitle, { name: topicTitle, count: 1 })
    }
  }

  return Array.from(topicMap.values()).sort((a, b) => b.count - a.count)
})

// Donut chart segments
const topicChartSegments = computed(() => {
  const total = skillsWithProgress.value.length || 1
  const circumference = 2 * Math.PI * 40
  let offset = 0

  return skillsByTopic.value.map((topic, index) => {
    const segmentSize = (topic.count / total) * circumference
    const segment = {
      color: chartColors[index % chartColors.length],
      dashArray: `${segmentSize} ${circumference - segmentSize}`,
      offset: -offset,
    }
    offset += segmentSize
    return segment
  })
})

// Sorted skills table
const sortedSkills = computed(() => {
  const skills = [...completedTopics.value]
  return skills.sort((a, b) => {
    if (sortField.value === 'lastPracticed') {
      const dateA = new Date(a.last_practiced || 0).getTime()
      const dateB = new Date(b.last_practiced || 0).getTime()
      return sortDirection.value === 'asc' ? dateA - dateB : dateB - dateA
    }
    return 0
  })
})

const sortBy = (field: string) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'desc'
  }
}
</script>

<style scoped>
.summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.summary-title {
  font-size: 28px;
  font-weight: 300;
  color: #333;
  letter-spacing: 1px;
}

.print-btn {
  padding: 8px;
  background: transparent;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}

.print-btn:hover {
  background: #f5f5f5;
  color: #333;
}

.print-icon {
  width: 20px;
  height: 20px;
}

.accomplishments-card {
  background: white;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.card-title {
  font-size: 22px;
  font-weight: 400;
  color: #333;
  margin-bottom: 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 40px;
}

.stat-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 24px;
  height: 24px;
}

.stat-icon.answered {
  background: #e8f5e9;
  color: #4CAF50;
}

.stat-icon.spent {
  background: #e3f2fd;
  color: #2196F3;
}

.stat-icon.progress {
  background: #fff3e0;
  color: #FF9800;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 12px;
  font-weight: 600;
  color: #888;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 36px;
  font-weight: 300;
  color: #333;
  line-height: 1.2;
}

.stat-sublabel {
  font-size: 12px;
  font-weight: 600;
  color: #888;
  letter-spacing: 0.5px;
}

.skills-practiced-card {
  background: white;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  letter-spacing: 1px;
  margin-bottom: 24px;
  text-align: center;
}

.chart-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 48px;
  flex-wrap: wrap;
}

.donut-chart {
  position: relative;
  width: 160px;
  height: 160px;
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

.chart-value {
  display: block;
  font-size: 32px;
  font-weight: 300;
  color: #333;
}

.chart-label {
  display: block;
  font-size: 14px;
  color: #888;
}

.chart-legend {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-label {
  font-size: 14px;
  color: #333;
}

.text-gray {
  color: #999;
}

.skills-table-section {
  background: white;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.section-subtitle {
  font-size: 18px;
  font-weight: 400;
  color: #333;
  margin-bottom: 20px;
}

.skills-table {
  width: 100%;
  border-collapse: collapse;
}

.skills-table thead {
  background: linear-gradient(135deg, #00BCD4 0%, #00ACC1 100%);
}

.skills-table th {
  padding: 14px 16px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  user-select: none;
}

.skills-table th:hover {
  background: rgba(255, 255, 255, 0.1);
}

.sort-icon {
  margin-left: 4px;
  opacity: 0.7;
}

.skills-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #eee;
  font-size: 14px;
  color: #333;
}

.skill-link {
  color: #00BCD4;
  text-decoration: none;
  transition: color 0.2s;
}

.skill-link:hover {
  color: #0097A7;
  text-decoration: underline;
}

.date-cell {
  color: #888;
}

.empty-state {
  text-align: center;
  padding: 48px 20px;
  color: #888;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .chart-section {
    flex-direction: column;
  }
}
</style>

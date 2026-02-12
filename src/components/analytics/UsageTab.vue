<template>
  <div>
    <div class="summary-header">
      <h1 class="summary-title">ҚОЛДАНУ МӘЛІМЕТТЕРІ</h1>
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
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" /></svg>
          </div>
          <div class="stat-info">
            <span class="stat-label">ЖАУАП БЕРІЛДІ</span>
            <span class="stat-value">{{ filteredTotalQuestions }}</span>
            <span class="stat-sublabel">СҰРАҚТАР</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon time">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z" /></svg>
          </div>
          <div class="stat-info">
            <span class="stat-label">ЖҰМСАЛҒАН</span>
            <span class="stat-value">{{ formatTimeMinutes(filteredTotalTime) }}</span>
            <span class="stat-sublabel">ОҚУ УАҚЫТЫ</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon skills">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" /></svg>
          </div>
          <div class="stat-info">
            <span class="stat-label">ПРОГРЕСС ЖАСАЛДЫ</span>
            <span class="stat-value">{{ skillsWithProgress.length }}</span>
            <span class="stat-sublabel">ДАҒДЫЛАР</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="usage-charts-row">
      <!-- Practice by Category -->
      <div class="usage-chart-card">
        <h3 class="section-title">КАТЕГОРИЯ БОЙЫНША ПРАКТИКА</h3>
        <div class="chart-section">
          <div class="donut-chart">
            <svg viewBox="0 0 100 100" class="chart-svg">
              <circle v-if="practiceByCategory.length === 0" cx="50" cy="50" r="40"
                fill="transparent" stroke="#e0e0e0" stroke-width="12" />
              <circle v-for="(segment, index) in categoryChartSegments" :key="index" cx="50" cy="50" r="40"
                fill="transparent" :stroke="segment.color" stroke-width="12" :stroke-dasharray="segment.dashArray"
                :stroke-dashoffset="segment.offset" transform="rotate(-90 50 50)" />
            </svg>
          </div>
          <div class="chart-legend">
            <div v-for="(cat, index) in practiceByCategory" :key="cat.name" class="legend-item">
              <span class="legend-badge" :style="{ backgroundColor: chartColors[index % chartColors.length] }">{{ cat.percent }}%</span>
              <span class="legend-label">{{ cat.name }}</span>
            </div>
            <div v-if="practiceByCategory.length === 0" class="legend-item">
              <span class="legend-label text-gray">Әлі деректер жоқ</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Practice by Day -->
      <div class="usage-chart-card">
        <h3 class="section-title">КҮНДЕР БОЙЫНША ПРАКТИКА</h3>
        <div class="day-chart-container" v-if="practiceByDay.length > 0">
          <div class="day-chart">
            <div class="day-chart-y-label">Жауап берілген сұрақтар</div>
            <div class="day-chart-y-axis">
              <span v-for="tick in dayChartYTicks" :key="tick">{{ tick }}</span>
            </div>
            <div class="day-chart-body">
              <div class="day-chart-grid">
                <div v-for="tick in dayChartYTicks" :key="'grid-' + tick" class="grid-line"></div>
              </div>
              <div class="day-chart-bars">
                <div v-for="day in practiceByDay" :key="day.date" class="day-bar-col">
                  <div class="day-bar-wrapper">
                    <div class="day-bar"
                      :style="{ height: day.heightPercent + '%' }"
                      :title="day.count + ' сұрақ'">
                      <span v-if="day.count > 0" class="day-bar-value">{{ day.count }}</span>
                    </div>
                  </div>
                  <span class="day-bar-label">{{ day.label }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>Әлі деректер жоқ</p>
        </div>
      </div>
    </div>

    <!-- Sessions and Skills -->
    <div class="sessions-section" v-if="sessionsByDate.length > 0">
      <h2 class="sessions-title">Сессиялар мен дағдылар</h2>
      <div class="sessions-list">
        <div v-for="session in sessionsByDate" :key="session.dateKey" class="session-item">
          <div class="session-header" @click="toggleSession(session.dateKey)"
            :class="{ 'session-expanded': expandedSessions.has(session.dateKey) }">
            <div class="session-date">{{ session.label }}</div>
            <div class="session-meta">
              <span>{{ session.skillsPracticed }} {{ session.skillsPracticed === 1 ? 'дағды' : 'дағды' }}: {{ session.totalQuestions }} сұрақ</span>
              <span class="session-toggle">{{ expandedSessions.has(session.dateKey) ? '−' : '+' }}</span>
            </div>
          </div>
          <div v-if="expandedSessions.has(session.dateKey)" class="session-details">
            <div v-for="skill in session.skills" :key="skill.skillId" class="session-skill">
              <div class="session-skill-header">
                <span class="session-skill-name">{{ skill.skillName }}</span>
              </div>
              <div class="session-skill-stats">
                <div class="session-stat">
                  <span class="session-stat-label">Уақыт: </span>
                  <span class="session-stat-value">{{ formatTimeShort(skill.totalTime) }}</span>
                </div>
                <div class="session-stat">
                  <span class="session-stat-label">Жауаптар: </span>
                  <span class="session-stat-value">{{ skill.totalQuestions }}</span>
                </div>
                <div class="session-stat">
                  <span class="session-stat-label">Қате: </span>
                  <span class="session-stat-value">{{ skill.missedQuestions }}</span>
                </div>
                <div class="session-stat">
                  <span class="session-stat-label">SmartScore: </span>
                  <span class="session-stat-value">{{ skill.scoreBefore }} → {{ skill.scoreAfter }}</span>
                </div>
              </div>
              <!-- Questions Log Preview -->
              <div class="session-questions-preview" v-if="skill.questions.length > 0">
                <div class="preview-title">СҰРАҚТАР ЖУРНАЛЫ</div>
                <div class="preview-questions">
                  <div v-for="(q, qi) in skill.questions" :key="qi" class="preview-question">
                    <div class="preview-question-row">
                      <span :class="['preview-dot', q.isCorrect ? 'dot-correct' : 'dot-incorrect']"></span>
                      <span class="preview-prompt">{{ q.prompt || 'Сұрақ' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'

const props = defineProps<{
  gradeFrom: number
  gradeTo: number
}>()

const analyticsStore = useAnalyticsStore()
const expandedSessions = ref<Set<string>>(new Set())

const chartColors = ['#00BCD4', '#FF9800', '#4CAF50', '#9C27B0', '#F44336', '#2196F3']

const printReport = () => {
  window.print()
}

const formatTimeMinutes = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  return `${mins} мин`
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
  return `${mins} мін`
}

const formatGradeLabel = (grade: number | undefined): string => {
  if (grade === undefined || grade === null) return ''
  if (grade === -1) return 'Pre-K'
  if (grade === 0) return 'Мектепалды'
  return `${grade} сынып`
}

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

// Practice by Category
const practiceByCategory = computed(() => {
  const topicMap = new Map<string, number>()
  let totalQuestions = 0

  for (const skill of skillsWithProgress.value) {
    const rec = skill as Record<string, unknown>
    const topicTitle = (rec.topic_title as string) || 'Басқа'
    const gradeNumber = rec.grade_number as number | undefined
    const gradeLabel = formatGradeLabel(gradeNumber)
    const categoryName = gradeLabel ? `${topicTitle} (${gradeLabel})` : topicTitle
    const questions = (rec.total_questions as number) || 0
    topicMap.set(categoryName, (topicMap.get(categoryName) || 0) + questions)
    totalQuestions += questions
  }

  const items = Array.from(topicMap.entries())
    .map(([name, count]) => ({
      name,
      count,
      percent: totalQuestions > 0 ? Math.round((count / totalQuestions) * 100) : 0,
    }))
    .sort((a, b) => b.count - a.count)

  if (items.length > 5) {
    const main = items.slice(0, 5)
    const other = items.slice(5)
    const otherCount = other.reduce((s, i) => s + i.count, 0)
    const otherPercent = totalQuestions > 0 ? Math.round((otherCount / totalQuestions) * 100) : 0
    main.push({ name: 'Басқа', count: otherCount, percent: otherPercent })
    return main
  }

  return items
})

const categoryChartSegments = computed(() => {
  const total = practiceByCategory.value.reduce((s, c) => s + c.count, 0) || 1
  const circumference = 2 * Math.PI * 40
  let offset = 0

  return practiceByCategory.value.map((cat, index) => {
    const segmentSize = (cat.count / total) * circumference
    const segment = {
      color: chartColors[index % chartColors.length],
      dashArray: `${segmentSize} ${circumference - segmentSize}`,
      offset: -offset,
    }
    offset += segmentSize
    return segment
  })
})

// Practice by Day
const practiceByDay = computed(() => {
  const questions = analyticsStore.allQuestions
  if (!questions || questions.length === 0) return []

  const dayMap = new Map<string, number>()

  for (const q of questions) {
    if (!q.answered_at) continue
    const date = new Date(q.answered_at)
    const key = date.toISOString().slice(0, 10)
    dayMap.set(key, (dayMap.get(key) || 0) + 1)
  }

  const days: { date: string; count: number; label: string; heightPercent: number }[] = []
  const now = new Date()
  for (let i = 13; i >= 0; i--) {
    const d = new Date(now)
    d.setDate(d.getDate() - i)
    const key = d.toISOString().slice(0, 10)
    days.push({
      date: key,
      count: dayMap.get(key) || 0,
      label: i === 0 ? 'Бүгін' : d.toLocaleDateString('kk-KZ', { month: 'short', day: 'numeric' }),
      heightPercent: 0,
    })
  }

  const maxCount = Math.max(...days.map(d => d.count), 1)
  for (const day of days) {
    day.heightPercent = Math.round((day.count / maxCount) * 100)
  }

  return days
})

const dayChartYTicks = computed(() => {
  const maxCount = Math.max(...practiceByDay.value.map(d => d.count), 1)
  const step = Math.max(1, Math.ceil(maxCount / 4))
  const ticks: number[] = []
  for (let i = Math.ceil(maxCount / step) * step; i >= 0; i -= step) {
    ticks.push(i)
  }
  return ticks
})

// Sessions and Skills
const sessionsByDate = computed(() => {
  const questions = analyticsStore.allQuestions || []
  if (questions.length === 0) return []

  const skillNameMap = new Map<number, string>()
  for (const s of analyticsStore.skills) {
    const rec = s as Record<string, unknown>
    skillNameMap.set(rec.skill_id as number, (rec.skill_name as string) || 'Белгісіз')
  }

  const dateMap = new Map<string, Array<Record<string, unknown>>>()
  for (const q of questions) {
    const rec = q as Record<string, unknown>
    const answeredAt = rec.answered_at as string
    if (!answeredAt) continue
    const dateKey = answeredAt.slice(0, 10)
    if (!dateMap.has(dateKey)) dateMap.set(dateKey, [])
    dateMap.get(dateKey)!.push(rec)
  }

  const sortedDates = Array.from(dateMap.keys()).sort((a, b) => b.localeCompare(a))

  return sortedDates.map(dateKey => {
    const dayQuestions = dateMap.get(dateKey)!
    const totalQuestions = dayQuestions.length

    const skillMap = new Map<number, Array<Record<string, unknown>>>()
    for (const q of dayQuestions) {
      const skillId = q.skill_id as number
      if (!skillMap.has(skillId)) skillMap.set(skillId, [])
      skillMap.get(skillId)!.push(q)
    }

    const skills = Array.from(skillMap.entries()).map(([skillId, qs]) => {
      const totalQ = qs.length
      const correctQ = qs.filter(q => q.is_correct).length
      const missedQ = totalQ - correctQ
      const totalTime = qs.reduce((s, q) => s + ((q.time_spent_seconds as number) || 0), 0)

      const scores = qs.filter(q => q.smartscore_before !== null && q.smartscore_after !== null)
      let scoreBefore = 0
      let scoreAfter = 0
      if (scores.length > 0) {
        scoreBefore = Math.min(...scores.map(q => (q.smartscore_before as number) || 0))
        scoreAfter = Math.max(...scores.map(q => (q.smartscore_after as number) || 0))
      }

      return {
        skillId,
        skillName: skillNameMap.get(skillId) || 'Белгісіз',
        totalQuestions: totalQ,
        correctQuestions: correctQ,
        missedQuestions: missedQ,
        totalTime,
        scoreBefore,
        scoreAfter,
        questions: qs.map(q => ({
          prompt: (q.question_prompt as string) || '',
          isCorrect: q.is_correct as boolean,
          userAnswer: q.user_answer,
          correctAnswer: q.correct_answer as string,
        })),
      }
    })

    const skillsPracticed = skills.length
    const d = new Date(dateKey + 'T00:00:00')
    const dayNames = ['ЖЕКСЕНБІ', 'ДҮЙСЕНБІ', 'СЕЙСЕНБІ', 'СӘРСЕНБІ', 'БЕЙСЕНБІ', 'ЖҰМА', 'СЕНБІ']
    const monthNames = ['ҚАҢТАР', 'АҚПАН', 'НАУРЫЗ', 'СӘУІР', 'МАМЫР', 'МАУСЫМ', 'ШІЛДЕ', 'ТАМЫЗ', 'ҚЫРКҮЙЕК', 'ҚАЗАН', 'ҚАРАША', 'ЖЕЛТОҚСАН']
    const label = `${dayNames[d.getDay()]}, ${d.getDate()} ${monthNames[d.getMonth()]}`

    return {
      dateKey,
      label,
      totalQuestions,
      skillsPracticed,
      skills,
    }
  })
})

const toggleSession = (dateKey: string) => {
  if (expandedSessions.value.has(dateKey)) {
    expandedSessions.value.delete(dateKey)
  } else {
    expandedSessions.value.add(dateKey)
  }
}
</script>

<style scoped>
.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.summary-title {
  font-size: 28px;
  font-weight: 400;
  color: #333;
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

.accomplishments-card {
  background: white;
  border-radius: 12px;
  padding: 32px;
  margin-top: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.card-title {
  font-size: 20px;
  font-weight: 300;
  color: #555;
  margin-bottom: 28px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
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
  background: #e3f2fd;
  color: #1976d2;
}

.stat-icon.time {
  background: #fff3e0;
  color: #f57c00;
}

.stat-icon.skills {
  background: #e8f5e9;
  color: #388e3c;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 11px;
  font-weight: 700;
  color: #888;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  line-height: 1.2;
}

.stat-sublabel {
  font-size: 12px;
  color: #888;
}

.usage-charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 24px;
}

.usage-chart-card {
  background: white;
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.section-title {
  font-size: 14px;
  font-weight: 700;
  color: #555;
  letter-spacing: 0.05em;
  margin-bottom: 20px;
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

.chart-legend {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
}

.legend-badge {
  display: inline-block;
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  min-width: 36px;
  text-align: center;
  margin-right: 8px;
}

.legend-label {
  font-size: 14px;
  color: #666;
}

.text-gray {
  color: #999;
}

/* Day Chart */
.day-chart-container {
  padding: 0;
}

.day-chart {
  display: flex;
  gap: 0;
  height: 280px;
  position: relative;
}

.day-chart-y-label {
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  font-size: 11px;
  font-weight: 600;
  color: #888;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-right: 8px;
  white-space: nowrap;
}

.day-chart-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  padding-bottom: 40px;
  min-width: 32px;
  font-size: 12px;
  color: #999;
  padding-right: 6px;
}

.day-chart-body {
  flex: 1;
  position: relative;
  display: flex;
  flex-direction: column;
  padding-bottom: 40px;
}

.day-chart-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  pointer-events: none;
  z-index: 0;
}

.grid-line {
  width: 100%;
  height: 1px;
  background: #e8e8e8;
}

.day-chart-bars {
  display: flex;
  flex: 1;
  gap: 3px;
  align-items: flex-end;
  position: relative;
  z-index: 1;
}

.day-bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  position: relative;
}

.day-bar-wrapper {
  flex: 1;
  display: flex;
  align-items: flex-end;
  width: 100%;
  justify-content: center;
}

.day-bar {
  width: 75%;
  max-width: 28px;
  background: linear-gradient(180deg, #FFD54F 0%, #FFC107 50%, #FFA000 100%);
  border-radius: 2px 2px 0 0;
  min-height: 0;
  position: relative;
  transition: height 0.4s ease;
  box-shadow: 0 -1px 3px rgba(255, 193, 7, 0.3);
}

.day-bar:hover {
  background: linear-gradient(180deg, #FFE082 0%, #FFD54F 50%, #FFB300 100%);
  box-shadow: 0 -2px 6px rgba(255, 193, 7, 0.5);
}

.day-bar-value {
  position: absolute;
  top: -18px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  font-weight: 700;
  color: #333;
  white-space: nowrap;
}

.day-bar-label {
  font-size: 9px;
  color: #888;
  margin-top: 4px;
  white-space: nowrap;
  transform: rotate(-50deg);
  transform-origin: top center;
  width: 55px;
  text-align: right;
  position: absolute;
  bottom: -36px;
}

/* Sessions & Skills */
.sessions-section {
  margin-top: 32px;
}

.sessions-title {
  font-size: 20px;
  font-weight: 400;
  color: #555;
  margin-bottom: 16px;
}

.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.session-item {
  overflow: hidden;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  background: #9e9e9e;
  color: white;
  cursor: pointer;
  transition: background 0.2s ease;
  border-radius: 4px;
}

.session-header:hover {
  background: #888;
}

.session-header.session-expanded {
  background: #7CB342;
  border-radius: 4px 4px 0 0;
}

.session-date {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.03em;
}

.session-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
}

.session-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  font-size: 20px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.session-details {
  background: white;
  border: 1px solid #e0e0e0;
  border-top: none;
  border-radius: 0 0 4px 4px;
}

.session-skill {
  border-bottom: 1px solid #f0f0f0;
}

.session-skill:last-child {
  border-bottom: none;
}

.session-skill-header {
  padding: 12px 20px;
  background: #7CB342;
  color: white;
}

.session-skill-name {
  font-size: 14px;
  font-weight: 600;
}

.session-skill-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  padding: 14px 20px;
  gap: 8px;
  font-size: 13px;
  border-bottom: 1px solid #f0f0f0;
}

.session-stat-label {
  color: #888;
}

.session-stat-value {
  font-weight: 600;
  color: #333;
}

/* Questions Log Preview */
.session-questions-preview {
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
}

.preview-title {
  font-size: 11px;
  font-weight: 700;
  color: #999;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
}

.preview-questions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-question {
  padding: 8px 12px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
}

.preview-question-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.preview-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-correct {
  background: #4CAF50;
}

.dot-incorrect {
  background: #F44336;
}

.preview-prompt {
  font-size: 13px;
  color: #333;
  line-height: 1.4;
}

.empty-state {
  text-align: center;
  padding: 48px;
  color: #888;
}

@media (max-width: 768px) {
  .usage-charts-row {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .chart-section {
    flex-direction: column;
  }

  .day-chart {
    height: 200px;
  }
}
</style>

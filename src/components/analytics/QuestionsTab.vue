<template>
  <div class="questions-log">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">СҰРАҚТАР ЖУРНАЛЫ</h1>
      <button class="print-btn" @click="printReport">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z"/>
        </svg>
      </button>
    </div>

    <!-- Filters row: Grade → Skill -->
    <div class="filters-row">
      <div class="filter-box">
        <span class="filter-label">СЫНЫП:</span>
        <select v-model="selectedGrade" class="filter-select" @change="selectedSkillId = null">
          <option :value="null">Сыныпты таңдаңыз</option>
          <option v-for="g in availableGrades" :key="g.value" :value="g.value">{{ g.label }}</option>
        </select>
      </div>

      <div class="filter-box" v-if="selectedGrade !== null">
        <span class="filter-label">ДАҒДЫ:</span>
        <select v-model="selectedSkillId" class="filter-select">
          <option :value="null">Дағдыны таңдаңыз</option>
          <option v-for="s in skillsForGrade" :key="s.skillId" :value="s.skillId">{{ s.name }}</option>
        </select>
      </div>
    </div>

    <!-- Skill Summary Card -->
    <div class="summary-card">
      <div class="summary-header">
        <span>Дағды қорытындысы</span>
      </div>

      <div v-if="!selectedSkillId" class="summary-placeholder">
        Жоғарыдан дағдыны таңдаңыз.
      </div>

      <div v-else class="summary-body">
        <!-- Left stats -->
        <div class="summary-stats">
          <div class="stat-row">
            <svg viewBox="0 0 24 24" fill="none" stroke="#f5a623" stroke-width="2" width="20" height="20">
              <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/>
            </svg>
            <span class="stat-value smartscore-val">{{ selectedSkillSummary.currentSmartScore }}</span>
            <span class="stat-label">АҒЫМДАҒЫ СМАРТСКОР</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-row">
            <svg viewBox="0 0 24 24" fill="none" stroke="#e74c3c" stroke-width="2" width="20" height="20">
              <path d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/>
            </svg>
            <span class="stat-value">{{ selectedSkillSummary.questionsAnswered }}</span>
            <span class="stat-label">ЖАУАП БЕРІЛДІ</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-row">
            <svg viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2" width="20" height="20">
              <circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/>
            </svg>
            <span class="stat-value time-val">{{ selectedSkillSummary.timeLabel }}</span>
            <span class="stat-label">ЖҰМСАЛҒАН УАҚЫТ</span>
          </div>
        </div>

        <!-- SmartScore chart -->
        <div class="chart-container">
          <div style="position:relative;height:280px;width:100%">
            <Line v-if="chartData" :data="chartData" :options="chartOptions" />
            <div v-else class="chart-placeholder">Деректер жоқ</div>
          </div>
          <div class="chart-x-label">ЖАУАП БЕРІЛГЕН СҰРАҚТАР</div>
        </div>
      </div>
    </div>

    <!-- Questions answered section -->
    <div v-if="selectedSkillId && sessions.length > 0" class="sessions-section">
      <div class="sessions-header-bar">
        <span>Жауап берілген сұрақтар</span>
      </div>

      <div v-for="(session, si) in sessions" :key="session.dateKey" class="session-block">
        <!-- Session header -->
        <div class="session-header">
          <span class="session-label">
            СЕССИЯ {{ si + 1 }}: {{ session.label }}
          </span>
          <span class="session-score">
            SmartScore: {{ session.scoreStart }} → {{ session.scoreEnd }}
          </span>
          <button class="session-toggle-btn" @click="toggleSession(session.dateKey)">
            {{ collapsedSessions.has(session.dateKey) ? '+' : '−' }}
          </button>
        </div>

        <!-- Questions list -->
        <template v-if="!collapsedSessions.has(session.dateKey)">
          <div
            v-for="(q, qi) in session.questions"
            :key="qi"
            class="question-row"
            :class="q.isCorrect ? 'q-correct' : 'q-incorrect'"
          >
            <!-- Left border indicator -->
            <div class="q-indicator" :class="q.isCorrect ? 'ind-correct' : 'ind-incorrect'"></div>

            <div class="q-body">
              <!-- Number + icon -->
              <div class="q-meta">
                <span class="q-number">{{ q.index }} / {{ selectedSkillSummary.questionsAnswered }}</span>
                <span class="q-icon" :class="q.isCorrect ? 'icon-correct' : 'icon-incorrect'">
                  {{ q.isCorrect ? '✓' : '✗' }}
                </span>
              </div>

              <div class="q-content">
                <div class="q-section-label">Сұрақ</div>
                <div class="q-text">{{ q.prompt || '—' }}</div>

                <div class="q-answers">
                  <div class="q-answer-block">
                    <div class="q-section-label">Дұрыс жауап</div>
                    <div class="q-answer correct-ans">{{ formatAnswer(q.correctAnswer) }}</div>
                  </div>
                  <div class="q-answer-block">
                    <div class="q-section-label">Пайдаланушы жауабы</div>
                    <div class="q-answer user-ans" :class="q.isCorrect ? 'ans-correct' : 'ans-incorrect'">
                      {{ formatAnswer(q.userAnswer) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <div v-else-if="selectedSkillId && sessions.length === 0" class="empty-questions">
      Бұл дағды бойынша сұрақтар табылмады.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'vue-chartjs'
import { useAnalyticsStore } from '@/stores/analytics'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

const props = defineProps<{
  gradeFrom: number
  gradeTo: number
  dateRange: { start: Date | null; end: Date | null }
}>()

const analyticsStore = useAnalyticsStore()

const printReport = () => window.print()

// ─── Filters ───────────────────────────────────────────────────────────────
const selectedGrade = ref<number | null>(null)
const selectedSkillId = ref<number | null>(null)
const collapsedSessions = ref<Set<string>>(new Set())

const toggleSession = (key: string) => {
  if (collapsedSessions.value.has(key)) collapsedSessions.value.delete(key)
  else collapsedSessions.value.add(key)
}

// Grade label helper
const gradeLabel = (g: number) => {
  if (g === -1) return 'Мектепалды'
  if (g === 0) return 'Балабақша'
  return `${g} сынып`
}

// Unique grades from skills that have questions and pass date filter
const availableGrades = computed(() => {
  const gradeSet = new Set<number>()
  for (const skill of analyticsStore.skills) {
    const rec = skill as Record<string, unknown>
    if ((rec.total_questions as number || 0) === 0) continue
    const g = (rec.grade_number as number) ?? 0
    if (g < props.gradeFrom || g > props.gradeTo) continue
    gradeSet.add(g)
  }
  return Array.from(gradeSet).sort((a, b) => a - b).map(g => ({ value: g, label: gradeLabel(g) }))
})

// Skills for selected grade
const skillsForGrade = computed(() => {
  if (selectedGrade.value === null) return []
  return analyticsStore.skills
    .filter(s => {
      const rec = s as Record<string, unknown>
      return (rec.grade_number as number) === selectedGrade.value && (rec.total_questions as number || 0) > 0
    })
    .map(s => {
      const rec = s as Record<string, unknown>
      return {
        skillId: rec.skill_id as number,
        name: (rec.skill_name as string) || `Дағды ${rec.skill_id}`,
      }
    })
})

// ─── Filtered questions for selected skill ──────────────────────────────────
const isInDateRange = (ts: string | undefined) => {
  if (!props.dateRange.start || !ts) return true
  const d = new Date(ts)
  const end = props.dateRange.end || new Date()
  return d >= props.dateRange.start && d <= end
}

const skillQuestions = computed(() => {
  if (!selectedSkillId.value) return []
  return analyticsStore.allQuestions
    .filter(q => {
      const rec = q as Record<string, unknown>
      if ((rec.skill_id as number) !== selectedSkillId.value) return false
      const ts = (rec.answered_at || rec.created_at) as string
      return isInDateRange(ts)
    })
    .map(q => q as Record<string, unknown>)
    .sort((a, b) => {
      const ta = (a.answered_at || a.created_at) as string
      const tb = (b.answered_at || b.created_at) as string
      return new Date(ta).getTime() - new Date(tb).getTime()
    })
})

// ─── Skill summary stats ────────────────────────────────────────────────────
const selectedSkillSummary = computed(() => {
  const qs = skillQuestions.value
  if (!qs.length) return { currentSmartScore: 0, questionsAnswered: 0, timeLabel: '0 мин' }
  const last = qs[qs.length - 1]
  const currentSmartScore = (last.smartscore_after as number) ?? (last.smartscore_before as number) ?? 0
  const totalTime = qs.reduce((s, q) => s + ((q.time_spent_seconds as number) || 0), 0)
  const mins = Math.floor(totalTime / 60)
  const timeLabel = mins < 1 ? '<1 мин' : mins < 60 ? `${mins} мин` : `${Math.floor(mins/60)} сағ ${mins%60} мин`
  return { currentSmartScore: Math.round(currentSmartScore), questionsAnswered: qs.length, timeLabel }
})

// ─── Chart.js data (one dataset per session) ───────────────────────────────────
const sessionColors = [
  { border: '#5cb85c', bg: 'rgba(92,184,92,0.18)' },
  { border: '#27ae60', bg: 'rgba(39,174,96,0.22)' },
  { border: '#2ecc71', bg: 'rgba(46,204,113,0.15)' },
  { border: '#16a085', bg: 'rgba(22,160,133,0.18)' },
]

const chartData = computed(() => {
  const sess = sessions.value
  if (sess.length === 0) return null

  const totalQ = sess.reduce((s, se) => s + se.questionsCount, 0)
  // Labels: 0, 1, 2, ..., totalQ
  const labels = Array.from({ length: totalQ + 1 }, (_, i) => i)

  let offset = 0
  const datasets = sess.map((session, si) => {
    const color = sessionColors[si % sessionColors.length]
    const n = totalQ + 1
    const data: (number | null)[] = new Array(n).fill(null)

    // First point of this session: scoreStart at current offset
    data[offset] = session.scoreStart
    // Each question's score
    session.chartScores.forEach((score, i) => { data[offset + 1 + i] = score })

    offset += session.questionsCount

    return {
      label: `Сессия ${si + 1}`,
      data,
      borderColor: color.border,
      backgroundColor: color.bg,
      pointBackgroundColor: color.border,
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: 4,
      fill: 'origin' as const,
      tension: 0.2,
      spanGaps: false,
    }
  })

  return { labels, datasets }
})

const formatTimeShort = (seconds: number) => {
  if (!seconds || seconds < 60) return '<1 мин'
  const mins = Math.floor(seconds / 60)
  return mins < 60 ? `${mins} мин` : `${Math.floor(mins/60)} сағ ${mins%60} мин`
}

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 400 },
  plugins: {
    legend: {
      display: true,
      position: 'top' as const,
      labels: { usePointStyle: true, boxWidth: 8, font: { size: 12 }, color: '#555' },
    },
    tooltip: {
      callbacks: {
        title: (items: { datasetIndex: number; label: string }[]) => {
          const si = items[0]?.datasetIndex
          const sess = sessions.value[si]
          return sess ? `Сессия ${si + 1}: ${sess.label}` : `Сұрақ ${items[0]?.label}`
        },
        label: (item: { datasetIndex: number; raw: unknown }) => {
          const si = item.datasetIndex
          const sess = sessions.value[si]
          if (!sess) return `SmartScore: ${item.raw}`
          return [
            `⭐ SmartScore: ${sess.scoreStart} → ${sess.scoreEnd}`,
            `✍️ Сұрақтар: ${sess.questionsCount}`,
            `⏱ Уақыт: ${formatTimeShort(sess.totalTime)}`,
          ]
        },
      },
    },
  },
  scales: {
    x: {
      ticks: { color: '#aaa', font: { size: 11 } },
      grid: { display: false },
    },
    y: {
      min: 0,
      max: 100,
      title: { display: true, text: 'СМАРТСКОР', color: '#aaa', font: { size: 10, weight: 'bold' as const } },
      ticks: { stepSize: 20, color: '#aaa', font: { size: 11 } },
      grid: { color: '#e8e8e8' },
    },
  },
}))

// ─── Sessions grouping ───────────────────────────────────────────────────────
const sessions = computed(() => {
  const qs = skillQuestions.value
  if (qs.length === 0) return []

  const dateMap = new Map<string, Array<Record<string, unknown>>>()
  for (const q of qs) {
    const ts = (q.answered_at || q.created_at) as string
    const dateKey = ts ? ts.slice(0, 10) : 'unknown'
    if (!dateMap.has(dateKey)) dateMap.set(dateKey, [])
    dateMap.get(dateKey)!.push(q)
  }

  const dayNames = ['ЖЕКСЕНБІ', 'ДҮЙСЕНБІ', 'СЕЙСЕНБІ', 'СӘРСЕНБІ', 'БЕЙСЕНБІ', 'ЖҰМА', 'СЕНБІ']
  const monthNames = ['ҚАҢТАР','АҚПАН','НАУРЫЗ','СӘУІР','МАМЫР','МАУСЫМ','ШІЛДЕ','ТАМЫЗ','ҚЫРКҮЙЕК','ҚАЗАН','ҚАРАША','ЖЕЛТОҚСАН']

  let globalIndex = 0

  return Array.from(dateMap.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([dateKey, dayQs]) => {
      const d = new Date(dateKey + 'T00:00:00')
      const label = `${dayNames[d.getDay()]}, ${d.getDate()} ${monthNames[d.getMonth()]}`

      const chartScores = dayQs.map(q => Math.round((q.smartscore_after as number) ?? 0))
      const scoreStart = Math.round((dayQs[0].smartscore_before as number) ?? 0)
      const scoreEnd = chartScores[chartScores.length - 1] ?? 0
      const totalTime = dayQs.reduce((s, q) => s + ((q.time_spent_seconds as number) || 0), 0)
      const questionsCount = dayQs.length

      const questions = dayQs.map(q => {
        globalIndex++
        return {
          index: globalIndex,
          isCorrect: q.is_correct as boolean,
          prompt: (q.question_prompt as string) || '',
          correctAnswer: q.correct_answer,
          userAnswer: q.user_answer,
        }
      }).reverse() // Show newest first like IXL

      return { dateKey, label, scoreStart, scoreEnd, totalTime, questionsCount, chartScores, questions }
    })
})

// ─── Helpers ────────────────────────────────────────────────────────────────
const tryParseJson = (str: unknown): unknown => {
  if (typeof str !== 'string') return str
  const t = str.trim()
  if ((t.startsWith('{') && t.endsWith('}')) || (t.startsWith('[') && t.endsWith(']'))) {
    try { return JSON.parse(t) } catch { return str }
  }
  return str
}

const formatAnswer = (answer: unknown): string => {
  if (answer === null || answer === undefined) return '—'
  if (typeof answer === 'boolean') return answer ? 'Иә' : 'Жоқ'
  if (typeof answer === 'number') return String(answer)
  if (typeof answer === 'string') {
    const parsed = tryParseJson(answer)
    if (parsed !== answer && typeof parsed === 'object') return formatAnswer(parsed)
    return answer || '—'
  }
  if (typeof answer === 'object') {
    const obj = answer as Record<string, unknown>
    if (obj.userAnswer !== undefined) return String(obj.userAnswer)
    if (obj.value !== undefined) return String(obj.value)
    if (obj.text !== undefined) return String(obj.text)
    return JSON.stringify(answer)
  }
  return String(answer)
}
</script>

<style scoped>
.questions-log { font-family: inherit; }

/* Header */
.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.page-title { font-size: 28px; font-weight: 400; color: #333; }
.print-btn { background: none; border: none; cursor: pointer; color: #aaa; padding: 4px; }
.print-btn:hover { color: #555; }

/* Filters */
.filters-row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 20px; }
.filter-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 6px 12px;
}
.filter-label { font-size: 12px; font-weight: 700; color: #555; white-space: nowrap; }
.filter-select {
  border: none;
  outline: none;
  font-size: 13px;
  color: #333;
  background: transparent;
  min-width: 180px;
  cursor: pointer;
}

/* Summary card */
.summary-card {
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 24px;
}
.summary-header {
  background: #00b0e8;
  color: white;
  font-size: 16px;
  font-weight: 500;
  padding: 14px 20px;
}
.summary-placeholder {
  background: white;
  padding: 24px 20px;
  color: #777;
  font-style: italic;
  font-size: 14px;
}
.summary-body {
  display: flex;
  background: white;
}

/* Stats panel */
.summary-stats {
  width: 200px;
  flex-shrink: 0;
  border-right: 1px solid #eee;
  padding: 16px 0;
}
.stat-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 16px;
  gap: 4px;
}
.stat-value { font-size: 28px; font-weight: 600; color: #333; line-height: 1; }
.stat-value.smartscore-val { color: #f5a623; }
.stat-value.time-val { font-size: 22px; color: #3498db; }
.stat-label { font-size: 11px; font-weight: 700; color: #999; letter-spacing: 0.05em; text-align: center; }
.stat-divider { height: 1px; background: #eee; margin: 0 16px; }

/* Chart */
.chart-container {
  flex: 1;
  padding: 16px 20px 32px 16px;
  position: relative;
  min-width: 0;
  min-height: 340px;
}
.chart-placeholder { color: #ccc; font-size: 13px; padding: 40px; text-align: center; }
.chart-x-label {
  text-align: center;
  font-size: 11px;
  color: #aaa;
  font-weight: 700;
  letter-spacing: 0.05em;
  margin-top: 4px;
}

/* Sessions section */
.sessions-section { margin-top: 8px; }
.sessions-header-bar {
  background: #00b0e8;
  color: white;
  font-size: 16px;
  font-weight: 500;
  padding: 14px 20px;
  border-radius: 6px 6px 0 0;
}

.session-block { border: 1px solid #ddd; border-top: none; background: white; }
.session-block:last-child { border-radius: 0 0 6px 6px; }

.session-header {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #444;
  color: white;
  padding: 10px 20px;
  font-size: 13px;
}
.session-label { font-weight: 600; flex: 1; }
.session-score { font-size: 12px; opacity: 0.85; }
.session-toggle-btn {
  background: none;
  border: 1px solid rgba(255,255,255,0.4);
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Question row */
.question-row {
  display: flex;
  border-bottom: 1px solid #eee;
}
.question-row:last-child { border-bottom: none; }

.q-indicator { width: 6px; flex-shrink: 0; }
.ind-correct { background: #5cb85c; }
.ind-incorrect { background: #e74c3c; }

.q-body {
  flex: 1;
  display: flex;
  gap: 16px;
  padding: 16px 20px;
}

.q-meta {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  width: 56px;
}
.q-number { font-size: 11px; color: #999; text-align: center; }
.q-icon { font-size: 18px; font-weight: 700; }
.icon-correct { color: #5cb85c; }
.icon-incorrect { color: #e74c3c; }

.q-content { flex: 1; min-width: 0; }
.q-section-label { font-size: 11px; font-weight: 700; color: #888; margin-bottom: 4px; letter-spacing: 0.04em; }
.q-text { font-size: 15px; color: #333; margin-bottom: 16px; line-height: 1.5; }

.q-answers { display: flex; gap: 24px; flex-wrap: wrap; }
.q-answer-block { min-width: 120px; }
.q-answer {
  font-size: 14px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 3px;
  display: inline-block;
  margin-top: 2px;
  border: 1px solid #ddd;
  background: #f9f9f9;
  color: #333;
}
.ans-correct { border-color: #5cb85c; background: #f0fff0; color: #2e7d32; }
.ans-incorrect { border-color: #e74c3c; background: #fff5f5; color: #c62828; }

/* Empty / misc */
.empty-questions {
  text-align: center;
  padding: 40px;
  color: #aaa;
  font-size: 14px;
  background: white;
  border: 1px solid #eee;
  border-radius: 6px;
}
</style>

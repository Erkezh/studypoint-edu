<template>
  <div class="analytics-page">
    <Header />

    <!-- IXL-style Header with Tabs -->
    <div class="analytics-header">
      <nav class="analytics-tabs">
        <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
          :class="['tab-item', { active: activeTab === tab.id }]">
          <span class="tab-icon">{{ tab.icon }}</span>
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="filter-group grade-range-filter">
        <label @click="toggleGradeDropdown" class="filter-label clickable">
          СЫНЫП ДЕҢГЕЙІ: {{ gradeRangeLabel }}
          <span class="dropdown-arrow">▼</span>
        </label>
        <div v-if="showGradeDropdown" class="grade-dropdown-popup">
          <p class="dropdown-title">Осы сыныптардағы дағдыларды көрсету:</p>
          <div class="grade-range-selectors">
            <select v-model="gradeFrom" class="filter-select small">
              <option :value="-1">-1</option>
              <option :value="0">0</option>
              <option v-for="n in 12" :key="n" :value="n">{{ n }}</option>
            </select>
            <span class="range-separator">-</span>
            <select v-model="gradeTo" class="filter-select small">
              <option :value="-1">-1</option>
              <option :value="0">0</option>
              <option v-for="n in 12" :key="n" :value="n">{{ n }}</option>
            </select>
          </div>
          <button @click="applyGradeFilter" class="apply-btn">Дайын</button>
        </div>
      </div>
      <div class="filter-group">
        <label>УАҚЫТ АРАЛЫҒЫ:</label>
        <select v-model="selectedDateRange" class="filter-select">
          <option value="all">Барлық уақыт</option>
          <option value="week">Осы апта</option>
          <option value="month">Осы ай</option>
        </select>
      </div>
    </div>

    <main class="analytics-content">
      <!-- Loading State -->
      <div v-if="analyticsStore.loading" class="loading-state">
        <div class="spinner"></div>
        <p>Жүктелуде...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="analyticsStore.error" class="error-state">
        <p class="error-title">Талдауды жүктеу қатесі:</p>
        <p>{{ analyticsStore.error }}</p>
      </div>

      <div v-else>
        <!-- ========== SUMMARY TAB ========== -->
        <div v-if="activeTab === 'summary'">
          <div class="summary-header">
            <h1 class="summary-title">ҚОРЫТЫНДЫ ЕСЕП</h1>
            <button class="print-btn" @click="printReport">
              <svg class="print-icon" viewBox="0 0 24 24" fill="currentColor">
                <path
                  d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z" />
              </svg>
            </button>
          </div>

          <!-- Accomplishments Card -->
          <div class="accomplishments-card">
            <h2 class="card-title">Сіздің StudyPoint жетістіктеріңіз</h2>

            <div class="stats-grid">
              <!-- Answered -->
              <div class="stat-item">
                <div class="stat-icon answered">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path
                      d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" />
                  </svg>
                </div>
                <div class="stat-info">
                  <span class="stat-label">ЖАУАП БЕРІЛДІ</span>
                  <span class="stat-value">{{ filteredTotalQuestions }}</span>
                  <span class="stat-sublabel">СҰРАҚТАР</span>
                </div>
              </div>

              <!-- Spent Time -->
              <div class="stat-item">
                <div class="stat-icon spent">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path
                      d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z" />
                  </svg>
                </div>
                <div class="stat-info">
                  <span class="stat-label">ЖҰМСАЛҒАН</span>
                  <span class="stat-value">{{ formatTimeMinutes(filteredTotalTime) }}</span>
                  <span class="stat-sublabel">ОҚУ УАҚЫТЫ</span>
                </div>
              </div>

              <!-- Made Progress -->
              <div class="stat-item">
                <div class="stat-icon progress">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path
                      d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
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

          <!-- Math Skills Practiced -->
          <div class="skills-practiced-card">
            <h3 class="section-title">МЕҢГЕРІЛГЕН МАТЕМАТИКА ДАҒДЫЛАРЫ</h3>

            <div class="chart-section">
              <!-- Donut Chart -->
              <div class="donut-chart">
                <svg viewBox="0 0 100 100" class="chart-svg">
                  <circle v-for="(segment, index) in skillChartSegments" :key="index" cx="50" cy="50" r="40"
                    fill="transparent" :stroke="segment.color" stroke-width="12" :stroke-dasharray="segment.dashArray"
                    :stroke-dashoffset="segment.offset" transform="rotate(-90 50 50)" />
                </svg>
                <div class="chart-center">
                  <span class="chart-value">{{ skillsWithProgress.length }}</span>
                  <span class="chart-label">дағды</span>
                </div>
              </div>

              <!-- Legend with actual skill names -->
              <div class="chart-legend">
                <div v-for="(skill, index) in skillsForChart" :key="skill.skill_id" class="legend-item">
                  <span class="legend-dot" :style="{ backgroundColor: chartColors[index % chartColors.length] }"></span>
                  <span class="legend-label">{{ skill.name }}</span>
                </div>
                <div v-if="skillsWithProgress.length === 0" class="legend-item">
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
                    <span class="sort-icon">↕</span>
                  </th>
                  <th @click="sortBy('lastPracticed')">
                    Соңғы жаттығу
                    <span class="sort-icon">↕</span>
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

        <!-- ========== TROUBLE SPOTS TAB ========== -->
        <div v-if="activeTab === 'trouble'">
          <div class="trouble-section">
            <h2 class="section-header">
              <span class="icon-warning">⚠️</span>
              Қиындықтар — Қайталау керек тақырыптар
            </h2>
            <p class="section-desc">Бұл сұрақтарға қате жауап берілді. Оларды қайта қарап, түсініңіз.</p>

            <div v-if="incorrectQuestions.length === 0" class="empty-state success">
              <span class="success-icon">✓</span>
              <p class="success-text">Керемет! Қателер жоқ!</p>
              <p class="success-subtext">Барлық сұрақтарға дұрыс жауап бердіңіз.</p>
            </div>

            <div v-else class="problems-list">
              <div v-for="question in incorrectQuestions" :key="question.attempt_id" class="problem-card">
                <div class="problem-header">
                  <span class="problem-type">{{ getQuestionType(question) }}</span>
                  <span class="problem-date">{{ formatDate(question.answered_at) }}</span>
                </div>
                <p v-if="question.question_prompt" class="problem-text">{{ question.question_prompt }}</p>
                <div class="answer-comparison">
                  <div class="user-answer">
                    <span class="answer-label">❌ Сіздің жауабыңыз:</span>
                    <span class="answer-value">{{ formatAnswer(question.user_answer) }}</span>
                  </div>
                  <div class="correct-answer">
                    <span class="answer-label">✓ Дұрыс жауап:</span>
                    <span class="answer-value">{{ formatAnswer(question.correct_answer) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ========== QUESTIONS TAB ========== -->
        <div v-if="activeTab === 'questions'">
          <div class="questions-section">
            <h2 class="section-header">📝 Барлық сұрақтар</h2>

            <div v-if="analyticsStore.allQuestions.length === 0" class="empty-state">
              <p>Әзірге сұрақтар жоқ</p>
            </div>

            <div v-else class="questions-list">
              <div v-for="question in analyticsStore.allQuestions" :key="question.attempt_id"
                :class="['question-card', question.is_correct ? 'correct' : 'incorrect']">
                <div class="question-header">
                  <span :class="['status-badge', question.is_correct ? 'success' : 'error']">
                    {{ question.is_correct ? '✓ Дұрыс' : '✗ Қате' }}
                  </span>
                  <span class="question-date">{{ formatDate(question.answered_at) }}</span>
                </div>
                <p v-if="question.question_prompt" class="question-text">{{ question.question_prompt }}</p>
                <div class="answer-row">
                  <div class="answer-box">
                    <span class="answer-label">Сіздің жауабыңыз:</span>
                    <span class="answer-value">{{ formatAnswer(question.user_answer) }}</span>
                  </div>
                  <div class="answer-box correct">
                    <span class="answer-label">Дұрыс жауап:</span>
                    <span class="answer-value">{{ formatAnswer(question.correct_answer) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ========== PROGRESS TAB ========== -->
        <div v-if="activeTab === 'progress'">
          <div class="progress-section">
            <h2 class="section-header">📈 Прогресс</h2>

            <div class="progress-stats">
              <div class="progress-card">
                <span class="progress-value">{{ analyticsStore.accuracy }}%</span>
                <span class="progress-label">Дәлдік</span>
              </div>
              <div class="progress-card">
                <span class="progress-value">{{ completedTopics.length }}</span>
                <span class="progress-label">Меңгерілген дағдылар</span>
              </div>
              <div class="progress-card">
                <span class="progress-value">{{ analyticsStore.totalQuestions }}</span>
                <span class="progress-label">Жауап берілген сұрақтар</span>
              </div>
            </div>

            <div v-if="completedTopics.length > 0" class="mastered-skills">
              <h3>Меңгерілген дағдылар (SmartScore = 100)</h3>
              <div class="skills-grid">
                <div v-for="topic in completedTopics" :key="topic.skill_id" class="mastered-skill-card">
                  <span class="skill-name">{{ topic.name }}</span>
                  <span class="skill-score">{{ topic.best_smartscore }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { useCatalogStore } from '@/stores/catalog'
// Auth store is available if needed for future features
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'

const analyticsStore = useAnalyticsStore()
const catalogStore = useCatalogStore()
// const authStore = useAuthStore() // Available for future use

// Tab configuration
const tabs = [
  { id: 'summary', label: 'Қорытынды', icon: '📊' },
  { id: 'trouble', label: 'Қиындықтар', icon: '⚠️' },
  { id: 'questions', label: 'Сұрақтар', icon: '📝' },
  { id: 'progress', label: 'Прогресс', icon: '📈' },
]

const activeTab = ref<string>('summary')
const gradeFrom = ref<number>(-1)
const gradeTo = ref<number>(12)
const showGradeDropdown = ref<boolean>(false)
const selectedDateRange = ref<string>('all')
const sortField = ref<string>('lastPracticed')
const sortDirection = ref<'asc' | 'desc'>('desc')
const skillNames = ref<Map<number, string>>(new Map())

// Grade range label for display
const gradeRangeLabel = computed(() => {
  if (gradeFrom.value === -1 && gradeTo.value === 12) {
    return 'Барлық сыныптар'
  }
  if (gradeFrom.value === gradeTo.value) {
    return `${gradeFrom.value} сынып`
  }
  return `${gradeFrom.value} - ${gradeTo.value} сынып`
})

// Toggle grade dropdown visibility
const toggleGradeDropdown = () => {
  showGradeDropdown.value = !showGradeDropdown.value
}

// Apply grade filter and close dropdown
const applyGradeFilter = () => {
  // Ensure gradeFrom <= gradeTo
  if (gradeFrom.value > gradeTo.value) {
    const temp = gradeFrom.value
    gradeFrom.value = gradeTo.value
    gradeTo.value = temp
  }
  showGradeDropdown.value = false
}

// Filtered totals based on grade range
const filteredTotalQuestions = computed(() => {
  // Sum total_questions from filtered skills
  return analyticsStore.skills.reduce((sum, skill) => {
    const gradeNumber = (skill as Record<string, unknown>).grade_number as number | undefined
    if (gradeNumber !== undefined) {
      if (gradeNumber >= gradeFrom.value && gradeNumber <= gradeTo.value) {
        return sum + (skill.total_questions || 0)
      }
      return sum
    }
    return sum + (skill.total_questions || 0)
  }, 0)
})

const filteredTotalTime = computed(() => {
  // Sum total_time_seconds from filtered skills
  return analyticsStore.skills.reduce((sum, skill) => {
    const gradeNumber = (skill as Record<string, unknown>).grade_number as number | undefined
    const totalTime = (skill as Record<string, unknown>).total_time_seconds as number | undefined
    if (gradeNumber !== undefined) {
      if (gradeNumber >= gradeFrom.value && gradeNumber <= gradeTo.value) {
        return sum + (totalTime || 0)
      }
      return sum
    }
    return sum + (totalTime || 0)
  }, 0)
})

// Chart colors
const chartColors = ['#00BCD4', '#FF9800', '#4CAF50', '#9C27B0', '#F44336', '#2196F3']

// Format time to minutes
const formatTimeMinutes = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  return `${mins} мин`
}

// Format date
const formatDate = (dateString: string): string => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

// Format last practiced as relative time
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

// Parse JSON if string
const tryParseJson = (str: string): unknown => {
  if (!str || typeof str !== 'string') return str
  const trimmed = str.trim()
  if ((trimmed.startsWith('{') && trimmed.endsWith('}')) ||
    (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
    try {
      return JSON.parse(trimmed)
    } catch {
      return str
    }
  }
  return str
}

// Format answer
const formatAnswer = (answer: unknown): string => {
  if (answer === null || answer === undefined) return '-'
  if (typeof answer === 'string') {
    const parsed = tryParseJson(answer)
    if (parsed !== answer && typeof parsed === 'object') {
      return formatAnswer(parsed)
    }
    return answer || '-'
  }
  if (typeof answer === 'number') return String(answer)
  if (typeof answer === 'boolean') return answer ? 'Иә' : 'Жоқ'
  if (typeof answer === 'object' && answer !== null) {
    const obj = answer as Record<string, unknown>
    if (obj.userAnswer !== undefined) return String(obj.userAnswer)
    if (obj.correctAnswer !== undefined) return String(obj.correctAnswer)
    if (obj.value !== undefined) return String(obj.value)
    if (obj.text !== undefined) return String(obj.text)
    return JSON.stringify(answer)
  }
  return String(answer)
}

// Get question type
const getQuestionType = (question: Record<string, unknown>): string => {
  const type = question.question_type as string || ''
  if (type.includes('PLUGIN')) return '🎮 Интерактивті'
  if (type.includes('MCQ')) return '📝 Таңдау'
  if (type.includes('NUMERIC')) return '🔢 Сандық'
  return '📋 Сұрақ'
}

// Skills with progress (practiced at least once), filtered by grade range
const skillsWithProgress = computed(() => {
  return analyticsStore.skills.filter(skill => {
    if ((skill.total_questions || 0) === 0) return false
    // Filter by grade range if grade_number is available
    const gradeNumber = (skill as Record<string, unknown>).grade_number as number | undefined
    if (gradeNumber !== undefined) {
      return gradeNumber >= gradeFrom.value && gradeNumber <= gradeTo.value
    }
    return true // Show skills without grade info
  })
})

// Completed topics (SmartScore = 100), filtered by grade range
const completedTopics = computed(() => {
  return analyticsStore.skills
    .filter(skill => {
      if ((skill.best_smartscore || 0) < 100) return false
      // Filter by grade range
      const gradeNumber = (skill as Record<string, unknown>).grade_number as number | undefined
      if (gradeNumber !== undefined) {
        return gradeNumber >= gradeFrom.value && gradeNumber <= gradeTo.value
      }
      return true
    })
    .map(skill => {
      const apiName = (skill as Record<string, unknown>).skill_name as string | undefined
      return {
        skill_id: skill.skill_id,
        name: apiName || skillNames.value.get(skill.skill_id) || `Дағды ${skill.skill_id}`,
        best_smartscore: skill.best_smartscore || 0,
        total_questions: skill.total_questions || 0,
        accuracy_percent: skill.accuracy_percent || 0,
        last_practiced: skill.last_practiced_at || '',
      }
    })
})

// Skills for chart legend (with actual names)
const skillsForChart = computed(() => {
  return skillsWithProgress.value.map(skill => {
    // Priority: 1) skill_name from API, 2) skillNames map, 3) fallback placeholder
    const apiName = (skill as Record<string, unknown>).skill_name as string | undefined
    const cachedName = skillNames.value.get(skill.skill_id)
    const name = apiName || cachedName || `Дағды ${skill.skill_id}`

    return {
      skill_id: skill.skill_id,
      name,
      total_questions: skill.total_questions || 0,
    }
  })
})

// Chart segments for donut chart (one segment per skill)
const skillChartSegments = computed(() => {
  const total = skillsWithProgress.value.length || 1
  const circumference = 2 * Math.PI * 40 // r=40
  const segmentSize = circumference / total
  let offset = 0

  return skillsForChart.value.map((skill, index) => {
    const segment = {
      color: chartColors[index % chartColors.length],
      dashArray: `${segmentSize} ${circumference - segmentSize}`,
      offset: -offset,
    }
    offset += segmentSize
    return segment
  })
})


// Sorted skills for table
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

// Incorrect questions
const incorrectQuestions = computed(() => {
  return (analyticsStore.allQuestions || []).filter(q => !q.is_correct)
})

// Sort by column
const sortBy = (field: string) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'desc'
  }
}

// Print report
const printReport = () => {
  window.print()
}

// Load skill names
const loadSkillNames = async () => {
  const skillIds = analyticsStore.skills.map(s => s.skill_id)
  for (const skillId of skillIds) {
    try {
      const skill = await catalogStore.getSkill(skillId)
      if (skill) {
        skillNames.value.set(skillId, skill.title)
      }
    } catch (err) {
      console.warn(`Failed to load skill ${skillId}:`, err)
    }
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      analyticsStore.getOverview(true),
      analyticsStore.getSkills(true),
    ])

    if (analyticsStore.skills.length > 0) {
      await loadSkillNames()
    }

    try {
      await analyticsStore.getAllQuestions()
    } catch (err) {
      console.warn('Failed to load questions:', err)
    }
  } catch (err) {
    console.error('Failed to load analytics:', err)
  }
})
</script>

<style scoped>
.analytics-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* Header & Tabs */
.analytics-header {
  background: linear-gradient(135deg, #00BCD4 0%, #00ACC1 100%);
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.analytics-tabs {
  display: flex;
  gap: 0;
  max-width: 1200px;
  margin: 0 auto;
  overflow-x: auto;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 24px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  border-bottom: 3px solid transparent;
}

.tab-item:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.tab-item.active {
  color: white;
  background: rgba(255, 255, 255, 0.15);
  border-bottom-color: white;
}

.tab-icon {
  font-size: 16px;
}

/* Filters */
.filters-bar {
  display: flex;
  gap: 24px;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  max-width: 1200px;
  margin: 0 auto;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
}

.filter-select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  background: white;
  cursor: pointer;
}

.filter-select.small {
  padding: 8px 16px;
  min-width: 70px;
}

/* Grade Range Filter */
.grade-range-filter {
  position: relative;
}

.filter-label.clickable {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  color: #00ACC1;
  font-weight: 600;
}

.filter-label.clickable:hover {
  background: #f5f5f5;
}

.dropdown-arrow {
  font-size: 10px;
  color: #666;
}

.grade-dropdown-popup {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 16px;
  z-index: 100;
  min-width: 240px;
  margin-top: 4px;
}

.dropdown-title {
  font-size: 13px;
  color: #666;
  margin: 0 0 12px 0;
}

.grade-range-selectors {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.range-separator {
  font-size: 16px;
  color: #666;
}

.apply-btn {
  display: block;
  width: 100%;
  padding: 8px 16px;
  background: transparent;
  color: #00ACC1;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
}

.apply-btn:hover {
  color: #00838F;
}

/* Content */
.analytics-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* Loading & Error */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e0e0e0;
  border-top-color: #00BCD4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-state {
  background: #ffebee;
  border: 1px solid #f44336;
  border-radius: 8px;
  padding: 20px;
  color: #c62828;
}

.error-title {
  font-weight: 600;
  margin-bottom: 8px;
}

/* Summary Header */
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

/* Accomplishments Card */
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

/* Skills Practiced Card */
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

/* Skills Table */
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

/* Empty State */
.empty-state {
  text-align: center;
  padding: 48px 20px;
  color: #888;
}

.empty-state.success {
  color: #4CAF50;
}

.success-icon {
  display: inline-block;
  width: 64px;
  height: 64px;
  line-height: 64px;
  font-size: 32px;
  background: #e8f5e9;
  border-radius: 50%;
  margin-bottom: 16px;
}

.success-text {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 8px;
}

.success-subtext {
  font-size: 14px;
  color: #888;
}

/* Trouble Spots */
.trouble-section {
  background: white;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 22px;
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.section-desc {
  color: #666;
  margin-bottom: 24px;
}

.problems-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.problem-card {
  background: #fff5f5;
  border: 1px solid #ffcdd2;
  border-radius: 8px;
  padding: 20px;
}

.problem-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.problem-type {
  font-size: 12px;
  font-weight: 600;
  color: #9c27b0;
  background: #f3e5f5;
  padding: 4px 10px;
  border-radius: 12px;
}

.problem-date {
  font-size: 12px;
  color: #888;
}

.problem-text {
  font-size: 15px;
  color: #333;
  margin-bottom: 16px;
}

.answer-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.user-answer {
  background: #ffebee;
  padding: 12px;
  border-radius: 8px;
}

.correct-answer {
  background: #e8f5e9;
  padding: 12px;
  border-radius: 8px;
}

.answer-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 4px;
}

.user-answer .answer-label {
  color: #c62828;
}

.correct-answer .answer-label {
  color: #2e7d32;
}

.answer-value {
  font-size: 16px;
  font-weight: 500;
}

.user-answer .answer-value {
  color: #c62828;
}

.correct-answer .answer-value {
  color: #2e7d32;
}

/* Questions Tab */
.questions-section {
  background: white;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-card {
  border-radius: 8px;
  padding: 20px;
}

.question-card.correct {
  background: #e8f5e9;
  border: 1px solid #a5d6a7;
}

.question-card.incorrect {
  background: #ffebee;
  border: 1px solid #ef9a9a;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.status-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
}

.status-badge.success {
  background: #c8e6c9;
  color: #2e7d32;
}

.status-badge.error {
  background: #ffcdd2;
  color: #c62828;
}

.question-date {
  font-size: 12px;
  color: #888;
}

.question-text {
  font-size: 15px;
  color: #333;
  margin-bottom: 16px;
}

.answer-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.answer-box {
  background: rgba(255, 255, 255, 0.7);
  padding: 12px;
  border-radius: 8px;
}

.answer-box .answer-label {
  color: #666;
}

.answer-box .answer-value {
  color: #333;
}

.answer-box.correct .answer-label {
  color: #2e7d32;
}

.answer-box.correct .answer-value {
  color: #2e7d32;
}

/* Progress Tab */
.progress-section {
  background: white;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.progress-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.progress-card {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  padding: 24px;
  border-radius: 12px;
  text-align: center;
}

.progress-value {
  display: block;
  font-size: 36px;
  font-weight: 600;
  color: #1976d2;
}

.progress-label {
  display: block;
  font-size: 13px;
  color: #555;
  margin-top: 8px;
}

.mastered-skills h3 {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 16px;
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.mastered-skill-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #e8f5e9;
  padding: 12px 16px;
  border-radius: 8px;
}

.mastered-skill-card .skill-name {
  font-size: 14px;
  color: #333;
}

.mastered-skill-card .skill-score {
  font-size: 14px;
  font-weight: 600;
  color: #4CAF50;
}

/* Responsive */
@media (max-width: 768px) {
  .filters-bar {
    flex-direction: column;
    gap: 12px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .chart-section {
    flex-direction: column;
  }

  .answer-comparison,
  .answer-row {
    grid-template-columns: 1fr;
  }
}

/* Print Styles */
@media print {

  /* Hide header (global) */
  header,
  .header,
  nav,
  .nav,
  [class*="header"] {
    display: none !important;
  }

  /* Hide analytics page elements that shouldn't print */
  .analytics-tabs,
  .filters-bar,
  .print-btn,
  .grade-dropdown-popup {
    display: none !important;
  }

  /* Ensure content takes full width */
  .analytics-page {
    padding: 0 !important;
  }

  .analytics-content {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  /* Summary title starts at top */
  .summary-header {
    margin-top: 0 !important;
    padding-top: 0 !important;
  }

  /* Remove shadows and backgrounds for printing */
  .accomplishments-card,
  .skills-practiced-card,
  .skills-table-section {
    box-shadow: none !important;
    border: 1px solid #ddd !important;
  }

  /* Page breaks */
  .skills-practiced-card {
    page-break-before: auto;
  }

  .skills-table-section {
    page-break-before: auto;
    page-break-inside: avoid;
  }
}
</style>

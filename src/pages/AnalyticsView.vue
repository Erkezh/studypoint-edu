<template>
  <div class="analytics-page">
    <Header />

    <!-- IXL-style Header with Tabs -->
    <div class="analytics-header">
      <nav class="analytics-tabs">
        <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
          :class="['tab-item', { active: activeTab === tab.id }]">
          <span class="tab-icon">
            <svg v-if="tab.id === 'summary'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
            <svg v-else-if="tab.id === 'usage'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <svg v-else-if="tab.id === 'trouble'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
            <svg v-else-if="tab.id === 'scores'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" /></svg>
            <svg v-else-if="tab.id === 'questions'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
            <svg v-else-if="tab.id === 'progress'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
          </span>
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="filter-group grade-range-filter">
        <label @click="toggleGradeDropdown" class="filter-label clickable">
          СЫНЫП ДЕҢГЕЙІ: {{ gradeRangeLabel }}
          <svg class="dropdown-arrow w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
        </label>
        <div v-if="showGradeDropdown" class="grade-dropdown-popup">
          <p class="dropdown-title">Осы сыныптардағы дағдыларды көрсету:</p>
          <div class="grade-range-selectors">
            <select v-model="gradeFrom" class="filter-select small">
              <option :value="-1">Pre-K</option>
              <option :value="0">0</option>
              <option v-for="n in 12" :key="n" :value="n">{{ n }}</option>
            </select>
            <span class="range-separator">-</span>
            <select v-model="gradeTo" class="filter-select small">
              <option :value="-1">Pre-K</option>
              <option :value="0">0</option>
              <option v-for="n in 12" :key="n" :value="n">{{ n }}</option>
            </select>
          </div>
          <button @click="applyGradeFilter" class="apply-btn">Дайын</button>
        </div>
      </div>
      <div class="filter-group date-range-filter">
        <label @click="toggleDateDropdown" class="filter-label clickable">
          УАҚЫТ АРАЛЫҒЫ: {{ dateRangeLabel }}
          <svg class="dropdown-arrow w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
        </label>
        <div v-if="showDateDropdown" class="date-dropdown-popup">
          <button
            v-for="option in dateOptions"
            :key="option.id"
            @click="selectDateRange(option.id)"
            :class="['date-option', { active: selectedDateOption === option.id }]"
          >
            {{ option.label }}
          </button>
          <!-- Placeholder for custom date picker if needed later -->
          <!-- <button class="date-option custom">Custom...</button> -->
        </div>
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
        <SummaryTab v-if="activeTab === 'summary'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :date-range="dateRange" :skill-names="skillNames" />

        <UsageTab v-else-if="activeTab === 'usage'"
          :grade-from="gradeFrom" :grade-to="gradeTo" />

        <TroubleTab v-else-if="activeTab === 'trouble'" />

        <ScoresTab v-else-if="activeTab === 'scores'" />

        <QuestionsTab v-else-if="activeTab === 'questions'" />

        <ProgressTab v-else-if="activeTab === 'progress'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :skill-names="skillNames" />
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { useCatalogStore } from '@/stores/catalog'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import SummaryTab from '@/components/analytics/SummaryTab.vue'
import UsageTab from '@/components/analytics/UsageTab.vue'
import ScoresTab from '@/components/analytics/ScoresTab.vue'
import TroubleTab from '@/components/analytics/TroubleTab.vue'
import QuestionsTab from '@/components/analytics/QuestionsTab.vue'
import ProgressTab from '@/components/analytics/ProgressTab.vue'

const analyticsStore = useAnalyticsStore()
const catalogStore = useCatalogStore()

// Tab configuration
const tabs = [
  { id: 'summary', label: 'Қорытынды' },
  { id: 'usage', label: 'Қолдану' },
  { id: 'trouble', label: 'Қиындықтар' },
  { id: 'scores', label: 'Ұпайлар' },
  { id: 'questions', label: 'Сұрақтар' },
  { id: 'progress', label: 'Прогресс' },
]

const activeTab = ref<string>('summary')
const gradeFrom = ref<number>(-1)
const gradeTo = ref<number>(12)
const showGradeDropdown = ref<boolean>(false)
// const selectedDateRange = ref<string>('all') // Replaced by new logic
const skillNames = ref<Map<number, string>>(new Map())

// Grade range label for display
const gradeRangeLabel = computed(() => {
  const formatGrade = (g: number) => g === -1 ? 'Pre-K' : g
  if (gradeFrom.value === -1 && gradeTo.value === 12) {
    return 'Барлық сыныптар'
  }
  if (gradeFrom.value === gradeTo.value) {
    return `${formatGrade(gradeFrom.value)} сынып`
  }
  return `${formatGrade(gradeFrom.value)} - ${formatGrade(gradeTo.value)} сынып`
})

const toggleGradeDropdown = () => {
  showGradeDropdown.value = !showGradeDropdown.value
}

const applyGradeFilter = () => {
  if (gradeFrom.value > gradeTo.value) {
    const temp = gradeFrom.value
    gradeFrom.value = gradeTo.value
    gradeTo.value = temp
  }
  showGradeDropdown.value = false
}

// Date Range Logic
const dateRangeLabel = ref<string>('Барлық уақыт')
const showDateDropdown = ref<boolean>(false)
const selectedDateOption = ref<string>('all')

const dateRange = ref<{ start: Date | null; end: Date | null }>({
  start: null,
  end: null
})

const dateOptions = [
  { id: 'today', label: 'Бүгін' },
  { id: 'yesterday', label: 'Кеше' },
  { id: 'week', label: 'Осы апта' },
  { id: 'last7', label: 'Соңғы 7 күн' },
  { id: 'month', label: 'Осы ай' },
  { id: 'last30', label: 'Соңғы 30 күн' },
  { id: 'year', label: 'Осы жыл' },
  { id: 'all', label: 'Барлық уақыт' },
]

const toggleDateDropdown = () => {
  showDateDropdown.value = !showDateDropdown.value
}

const selectDateRange = (optionId: string) => {
  selectedDateOption.value = optionId
  const option = dateOptions.find(o => o.id === optionId)
  dateRangeLabel.value = option ? option.label : 'Теңшелетін'
  showDateDropdown.value = false

  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())

  switch (optionId) {
    case 'today':
      dateRange.value = { start: today, end: new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59) }
      break
    case 'yesterday':
      const yesterday = new Date(today)
      yesterday.setDate(yesterday.getDate() - 1)
      const yesterdayEnd = new Date(yesterday)
      yesterdayEnd.setHours(23, 59, 59)
      dateRange.value = { start: yesterday, end: yesterdayEnd }
      break
    case 'week':
      // This week (starting Monday)
      const day = today.getDay() || 7 // 1 (Mon) to 7 (Sun)
      const monday = new Date(today)
      monday.setHours(0, 0, 0, 0)
      monday.setDate(monday.getDate() - day + 1)
      dateRange.value = { start: monday, end: new Date() }
      break
    case 'last7':
      const last7 = new Date(today)
      last7.setDate(last7.getDate() - 6)
      dateRange.value = { start: last7, end: new Date() }
      break
    case 'month':
      const firstDayMonth = new Date(today.getFullYear(), today.getMonth(), 1)
      dateRange.value = { start: firstDayMonth, end: new Date() }
      break
    case 'last30':
      const last30 = new Date(today)
      last30.setDate(last30.getDate() - 29)
      dateRange.value = { start: last30, end: new Date() }
      break
    case 'year':
      const firstDayYear = new Date(today.getFullYear(), 0, 1)
      dateRange.value = { start: firstDayYear, end: new Date() }
      break
    case 'all':
    default:
      dateRange.value = { start: null, end: null }
      break
  }
}

// Load skill names from catalog
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

/* Date Range Filter */
.date-range-filter {
  position: relative;
}

.date-dropdown-popup {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 8px 0;
  z-index: 100;
  min-width: 200px;
  margin-top: 4px;
}

.date-option {
  display: block;
  width: 100%;
  text-align: left;
  padding: 10px 16px;
  background: transparent;
  border: none;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: background-color 0.1s;
}

.date-option:hover {
  background-color: #f5f5f5;
}

.date-option.active {
  color: #00ACC1;
  background-color: #e0f7fa;
  font-weight: 500;
}

.date-option.custom {
  border-top: 1px solid #eee;
  margin-top: 4px;
  padding-top: 12px;
}

/* Responsive */
@media (max-width: 768px) {
  .filters-bar {
    flex-direction: column;
    gap: 12px;
  }

  .date-dropdown-popup {
    right: auto;
    left: 0;
  }
}
</style>

<template>
  <div class="score-grid-tab">
    <!-- Header -->
    <div class="sg-header">
      <h1 class="sg-title">ҰПАЙ ТОРЫ</h1>
      <button class="icon-btn" @click="printReport" title="Басып шығару">
        <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5"><path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z" /></svg>
      </button>
    </div>

    <!-- Filters Row -->
    <div class="sg-filters">
      <div class="sg-filter-group">
        <label class="sg-filter-label">СЫНЫП:</label>
        <select v-model.number="selectedGrade" class="sg-filter-select">
          <option v-for="g in gradeOptions" :key="g.value" :value="g.value">{{ g.label }}</option>
        </select>
      </div>
      <div class="sg-filter-group">
        <label class="sg-filter-label">ОҚУШЫ:</label>
        <select v-model="selectedStudentFilter" @change="onStudentFilterChange" class="sg-filter-select wide">
          <option value="all">Барлық оқушылар</option>
          <option v-for="st in studentsList" :key="st.id" :value="st.id">{{ st.name }}</option>
        </select>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loadingSkills" class="sg-loading">
      <div class="spinner"></div>
      <p>Жүктелуде...</p>
    </div>

    <!-- Grid Table -->
    <div v-else-if="groupedSkills.length > 0" class="sg-table-wrapper">
      <table class="sg-table">
        <thead>
          <tr>
            <th class="th-skill" :style="{ minWidth: '280px' }"></th>
            <th class="th-code"></th>
            <th v-for="st in displayStudents" :key="st.id" class="th-student">
              <div class="student-header">{{ st.name }}</div>
            </th>
          </tr>
        </thead>
        <tbody v-for="group in groupedSkills" :key="group.topicTitle">
          <!-- Topic Header -->
          <tr class="topic-row" @click="toggleTopic(group.topicTitle)">
            <td :colspan="2 + displayStudents.length" class="topic-cell">
              <span class="topic-caret">{{ expandedTopics[group.topicTitle] === false ? '▶' : '▼' }}</span>
              {{ group.topicTitle }}
            </td>
          </tr>
          <!-- Skill Rows -->
          <template v-if="expandedTopics[group.topicTitle] !== false">
            <tr v-for="skill in group.skills" :key="skill.id" class="skill-row">
              <td class="td-skill">
                <span class="skill-order">{{ skill.order }}.</span>
                <span class="skill-title">{{ skill.title }}</span>
              </td>
              <td class="td-code">{{ skill.code }}</td>
              <td v-for="st in displayStudents" :key="st.id" class="td-score">
                <div v-if="getStudentScore(st.id, skill.id) !== null"
                  class="score-cell"
                  :class="getScoreClass(getStudentScore(st.id, skill.id)!)"
                >
                  {{ getStudentScore(st.id, skill.id) }}
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div v-else class="sg-empty">
      <p>Бұл сыныпта дағдылар табылмады</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { catalogApi } from '@/api/catalog'
import type { SkillListItem } from '@/types/api'

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

// Find the most common grade among students
const defaultGrade = computed(() => {
  const gradeCount = new Map<number, number>()
  for (const st of props.allStudentsData) {
    if (!st.skills) continue
    for (const sk of st.skills) {
      if (sk.grade_number !== undefined) {
        gradeCount.set(sk.grade_number, (gradeCount.get(sk.grade_number) || 0) + 1)
      }
    }
  }
  let maxCount = 0
  let maxGrade = 3
  for (const [grade, count] of gradeCount) {
    if (count > maxCount) {
      maxCount = count
      maxGrade = grade
    }
  }
  return maxGrade
})

const gradeOptions = [
  { value: -1, label: 'Pre-K' },
  { value: 0, label: '0' },
  ...Array.from({ length: 12 }, (_, i) => ({ value: i + 1, label: `${i + 1}` })),
]

const selectedGrade = ref(defaultGrade.value)
const selectedStudentFilter = ref('all')
const loadingSkills = ref(false)
const catalogSkills = ref<SkillListItem[]>([])
const expandedTopics = ref<Record<string, boolean>>({})

// Students list for dropdown
const studentsList = computed(() =>
  props.allStudentsData.map(st => ({ id: st.student_id, name: st.full_name }))
)

// When a specific student is selected, navigate to scores_student
const onStudentFilterChange = () => {
  if (selectedStudentFilter.value !== 'all') {
    emit('navigate', 'scores_student', { studentId: selectedStudentFilter.value })
    // Reset back to "all" since we navigated away
    selectedStudentFilter.value = 'all'
  }
}

// Students to show as columns
const displayStudents = computed(() => {
  return props.allStudentsData.map(st => ({ id: st.student_id, name: st.full_name }))
})

// Build a lookup: studentId -> skillId -> score
const scoreMap = computed(() => {
  const map = new Map<string, Map<number, number>>()
  for (const st of props.allStudentsData) {
    const skillMap = new Map<number, number>()
    if (st.skills) {
      for (const sk of st.skills) {
        if ((sk.best_smartscore || 0) > 0) {
          skillMap.set(sk.skill_id, sk.best_smartscore || 0)
        }
      }
    }
    map.set(st.student_id, skillMap)
  }
  return map
})

const getStudentScore = (studentId: string, skillId: number): number | null => {
  const studentScores = scoreMap.value.get(studentId)
  if (!studentScores) return null
  const score = studentScores.get(skillId)
  return score !== undefined ? score : null
}

const getScoreClass = (score: number): string => {
  if (score >= 100) return 'score-mastered'
  if (score >= 80) return 'score-proficient'
  if (score >= 50) return 'score-practicing'
  return 'score-low'
}

// Load catalog skills for the selected grade
const loadGradeSkills = async () => {
  loadingSkills.value = true
  try {
    const response = await catalogApi.getSkills({ grade_number: selectedGrade.value, page_size: 500 })
    if (response.data) {
      catalogSkills.value = response.data
    }
  } catch (err) {
    console.error('Failed to load grade skills:', err)
  } finally {
    loadingSkills.value = false
  }
}

watch(selectedGrade, () => {
  expandedTopics.value = {}
  loadGradeSkills()
}, { immediate: true })

// Update default grade when data arrives
watch(defaultGrade, (g) => {
  if (catalogSkills.value.length === 0) {
    selectedGrade.value = g
  }
}, { immediate: true })

const toggleTopic = (topic: string) => {
  expandedTopics.value[topic] = expandedTopics.value[topic] === false ? true : false
}

// Group skills by topic
interface GroupedSkill {
  topicTitle: string
  skills: { id: number; title: string; code: string; order: number }[]
}

const groupedSkills = computed<GroupedSkill[]>(() => {
  const groups = new Map<string, GroupedSkill>()
  let orderCounter = 1

  for (const skill of catalogSkills.value) {
    const topic = skill.topic_title || 'Тақырыпсыз'
    if (!groups.has(topic)) {
      groups.set(topic, { topicTitle: topic, skills: [] })
      orderCounter = 1
    }
    groups.get(topic)!.skills.push({
      id: skill.id,
      title: skill.title,
      code: skill.code,
      order: orderCounter++,
    })
  }
  return Array.from(groups.values())
})

const printReport = () => window.print()
</script>

<style scoped>
.score-grid-tab {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
  font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Header */
.sg-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.sg-title {
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

/* Filters */
.sg-filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.sg-filter-group {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 10px 16px;
  gap: 10px;
}
.sg-filter-label {
  font-size: 12px;
  font-weight: 700;
  color: #666;
  letter-spacing: 0.5px;
  white-space: nowrap;
}
.sg-filter-select {
  border: none;
  font-size: 14px;
  color: #333;
  background: transparent;
  outline: none;
  cursor: pointer;
  min-width: 80px;
}
.sg-filter-select.wide {
  min-width: 180px;
}

/* Loading */
.sg-loading {
  text-align: center;
  padding: 60px;
  color: #888;
}
.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e0e0e0;
  border-top-color: #00bcd4;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Table Wrapper */
.sg-table-wrapper {
  overflow-x: auto;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

/* Table */
.sg-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

/* Header */
.sg-table thead tr {
  background: #f0f7fa;
  border-bottom: 2px solid #e0e0e0;
}
.th-skill {
  min-width: 260px;
  padding: 8px 12px;
  text-align: left;
}
.th-code {
  min-width: 50px;
  padding: 8px 6px;
  text-align: center;
  color: #999;
}
.th-student {
  min-width: 40px;
  max-width: 50px;
  padding: 8px 4px;
  text-align: center;
  vertical-align: bottom;
}
.student-header {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  transform: rotate(180deg);
  font-size: 11px;
  font-weight: 600;
  color: #00838f;
  white-space: nowrap;
  max-height: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Topic Row */
.topic-row {
  cursor: pointer;
  user-select: none;
}
.topic-cell {
  background: linear-gradient(135deg, #0bb5c4, #19a5b4);
  color: white;
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 8px 12px;
  border: none;
}
.topic-caret {
  font-size: 10px;
  margin-right: 8px;
}

/* Skill Rows */
.skill-row {
  border-bottom: 1px solid #f0f0f0;
}
.skill-row:hover {
  background: #fafffe;
}
.td-skill {
  padding: 6px 12px;
  color: #333;
  font-size: 13px;
}
.skill-order {
  color: #999;
  margin-right: 6px;
  font-size: 12px;
}
.skill-title {
  color: #333;
}
.td-code {
  padding: 6px;
  text-align: center;
  color: #aaa;
  font-size: 11px;
  font-family: monospace;
}
.td-score {
  padding: 4px;
  text-align: center;
  min-width: 40px;
}

/* Score Cells */
.score-cell {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 24px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  color: white;
}
.score-mastered { background: #66bb6a; }
.score-proficient { background: #4caf50; }
.score-practicing { background: #42a5f5; }
.score-low { background: #ff9800; }

/* Empty */
.sg-empty {
  text-align: center;
  padding: 60px;
  color: #888;
  font-size: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.w-5 { width: 20px; }
.h-5 { height: 20px; }
</style>

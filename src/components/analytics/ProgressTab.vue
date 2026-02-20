<template>
  <div>
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">ПРОГРЕСС ЖӘНЕ ЖЕТІЛДІРУ</h1>
      <button class="print-btn" @click="printReport">
        <svg class="print-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z" />
        </svg>
      </button>
    </div>

    <!-- Table -->
    <div class="progress-table">
      <!-- Table Header -->
      <div class="table-header">
        <div class="col-skill">ДАҒДЫ</div>
        <div class="col-time">УАҚЫТ</div>
        <div class="col-questions">СҰРАҚТАР</div>
        <div class="col-score">ҰПАЙ ӨЗГЕРІСІ</div>
      </div>

      <!-- Empty State -->
      <div v-if="skillsByGrade.length === 0" class="empty-state">
        Әлі бірде-бір дағды жаттықтырылмаған.
      </div>

      <!-- Grade Groups -->
      <template v-for="gradeGroup in skillsByGrade" :key="gradeGroup.grade">
        <!-- Grade Row -->
        <div class="grade-row" @click="toggleGrade(gradeGroup.grade)">
          <div class="col-skill grade-label">
            <span class="expand-arrow" :class="{ expanded: !collapsedGrades.has(gradeGroup.grade) }">▶</span>
            {{ gradeGroup.label }}
          </div>
          <div class="col-time"></div>
          <div class="col-questions"></div>
          <div class="col-score"></div>
        </div>

        <!-- Topics within grade -->
        <template v-if="!collapsedGrades.has(gradeGroup.grade)">
          <template v-for="topicGroup in gradeGroup.topics" :key="topicGroup.topicKey">
            <!-- Topic Row -->
            <div class="topic-row" @click="toggleTopic(topicGroup.topicKey)">
              <div class="col-skill topic-label">
                <span class="expand-arrow" :class="{ expanded: !collapsedTopics.has(topicGroup.topicKey) }">▶</span>
                {{ topicGroup.title }}
              </div>
              <div class="col-time"></div>
              <div class="col-questions"></div>
              <div class="col-score"></div>
            </div>

            <!-- Skills within topic -->
            <template v-if="!collapsedTopics.has(topicGroup.topicKey)">
              <div
                v-for="skill in topicGroup.skills"
                :key="skill.skillId"
                class="skill-row"
              >
                <!-- Skill name -->
                <div class="col-skill skill-label">
                  <span class="skill-icon">⊙</span>
                  <span class="skill-name-text">{{ skill.name }}</span>
                  <span v-if="skill.code" class="skill-code">{{ skill.code }}</span>
                </div>

                <!-- Time spent -->
                <div class="col-time skill-time">{{ formatTime(skill.timeSpent) }}</div>

                <!-- Questions count -->
                <div class="col-questions skill-questions">{{ skill.questions }}</div>

                <!-- Score improvement bar with arrow -->
                <div class="col-score">
                  <div class="score-bar-wrapper">
                    <span class="score-from">{{ skill.scoreFrom }}</span>
                    <div class="score-bar-track">
                      <!-- filled region from scoreFrom to scoreAfter -->
                      <div
                        class="score-bar-fill"
                        :style="{
                          left: skill.scoreFrom + '%',
                          width: Math.max(skill.scoreAfter - skill.scoreFrom, 2) + '%'
                        }"
                      ></div>
                      <!-- Arrow head at scoreAfter position -->
                      <div
                        class="score-arrow-head"
                        :style="{ left: skill.scoreAfter + '%' }"
                      ></div>
                    </div>
                    <span class="score-value">{{ skill.scoreAfter }}</span>
                  </div>
                </div>
              </div>
            </template>
          </template>
        </template>
      </template>
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
  dateRange: { start: Date | null; end: Date | null }
}>()

const analyticsStore = useAnalyticsStore()

const printReport = () => window.print()

// Expand / collapse state  (empty = all open by default)
const collapsedGrades = ref<Set<number>>(new Set())
const collapsedTopics = ref<Set<string>>(new Set())

const toggleGrade = (grade: number) => {
  if (collapsedGrades.value.has(grade)) {
    collapsedGrades.value.delete(grade)
  } else {
    collapsedGrades.value.add(grade)
  }
}

const toggleTopic = (topicKey: string) => {
  if (collapsedTopics.value.has(topicKey)) {
    collapsedTopics.value.delete(topicKey)
  } else {
    collapsedTopics.value.add(topicKey)
  }
}

// Grade label in Kazakh
const formatGradeLabel = (grade: number): string => {
  if (grade === -1) return 'МЕКТЕПАЛДЫ (PRE-K)'
  if (grade === 0) return 'БАЛАБАҚША'
  return `${grade} СЫНЫП`
}

const formatTime = (seconds: number): string => {
  if (!seconds || seconds === 0) return '<1 мин'
  if (seconds < 60) return '<1 мин'
  const mins = Math.floor(seconds / 60)
  if (mins < 60) return `${mins} мин`
  const hrs = Math.floor(mins / 60)
  const remainMins = mins % 60
  return remainMins > 0 ? `${hrs} сағ ${remainMins} мин` : `${hrs} сағ`
}

// Skill IDs that had activity in the selected date range
const skillIdsInRange = computed(() => {
  if (!props.dateRange.start) return null
  const ids = new Set<number>()
  for (const q of analyticsStore.allQuestions) {
    const ts = (q.answered_at || q.created_at) as string
    if (!ts) continue
    const d = new Date(ts)
    const end = props.dateRange.end || new Date()
    if (d >= props.dateRange.start! && d <= end) {
      ids.add(q.skill_id as number)
    }
  }
  return ids
})

// Per-skill score before/after computed from allQuestions
// Returns Map<skillId, { scoreFrom: number, scoreAfter: number }>
const scoreMap = computed(() => {
  const map = new Map<number, { scoreFrom: number; scoreAfter: number }>()
  for (const q of analyticsStore.allQuestions) {
    const rec = q as Record<string, unknown>
    const skillId = rec.skill_id as number
    const before = (rec.smartscore_before as number) ?? null
    const after = (rec.smartscore_after as number) ?? null
    if (before === null && after === null) continue

    // Date range filter
    if (props.dateRange.start) {
      const ts = (rec.answered_at || rec.created_at) as string
      if (!ts) continue
      const d = new Date(ts)
      const end = props.dateRange.end || new Date()
      if (d < props.dateRange.start || d > end) continue
    }

    const existing = map.get(skillId)
    if (!existing) {
      map.set(skillId, {
        scoreFrom: before ?? 0,
        scoreAfter: after ?? 0,
      })
    } else {
      // Earliest before = lowest starting score
      if (before !== null) existing.scoreFrom = Math.min(existing.scoreFrom, before)
      // Latest after = highest ending score
      if (after !== null) existing.scoreAfter = Math.max(existing.scoreAfter, after)
    }
  }
  return map
})

// Group skills by grade → topic
const skillsByGrade = computed(() => {
  const skillType = {
    skillId: 0,
    name: '',
    code: '',
    timeSpent: 0,
    questions: 0,
    scoreFrom: 0,
    scoreAfter: 0,
  }
  const gradeMap = new Map<number, Map<string, Array<typeof skillType>>>()

  for (const skill of analyticsStore.skills) {
    const rec = skill as Record<string, unknown>
    if ((rec.total_questions as number || 0) === 0) continue

    const grade = (rec.grade_number as number) ?? 0
    if (grade < props.gradeFrom || grade > props.gradeTo) continue

    // Date range filter
    if (skillIdsInRange.value !== null && !skillIdsInRange.value.has(rec.skill_id as number)) continue

    const topicTitle = (rec.topic_title as string) || 'Жалпы'
    const topicKey = `${grade}::${topicTitle}`

    if (!gradeMap.has(grade)) gradeMap.set(grade, new Map())
    const topicMap = gradeMap.get(grade)!
    if (!topicMap.has(topicKey)) topicMap.set(topicKey, [])

    const skillName = (rec.skill_name as string)
      || props.skillNames.get(rec.skill_id as number)
      || `Дағды ${rec.skill_id}`

    const skillId = rec.skill_id as number
    const scoreData = scoreMap.value.get(skillId)
    const scoreFrom = scoreData ? Math.min(scoreData.scoreFrom, 100) : 0
    const scoreAfter = scoreData ? Math.min(scoreData.scoreAfter, 100) : Math.min((rec.best_smartscore as number) || 0, 100)

    topicMap.get(topicKey)!.push({
      skillId,
      name: skillName,
      code: (rec.skill_code as string) || '',
      timeSpent: (rec.total_time_seconds as number) || 0,
      questions: (rec.total_questions as number) || 0,
      scoreFrom,
      scoreAfter,
    })
  }

  return Array.from(gradeMap.entries())
    .sort(([a], [b]) => a - b)
    .map(([grade, topicMap]) => ({
      grade,
      label: formatGradeLabel(grade),
      topics: Array.from(topicMap.entries()).map(([topicKey, skills]) => ({
        topicKey,
        title: topicKey.split('::')[1] || 'Жалпы',
        skills,
      })),
    }))
})
</script>

<style scoped>
/* Page header */
.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 400;
  color: #333;
  letter-spacing: 0.01em;
}

.print-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  color: #999;
  transition: color 0.2s;
}
.print-btn:hover { color: #555; }
.print-icon { width: 20px; height: 20px; }

/* Table */
.progress-table {
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #d0eaf7;
}

/* Columns */
.col-skill     { flex: 1; min-width: 0; }
.col-time      { width: 100px; flex-shrink: 0; text-align: center; }
.col-questions { width: 100px; flex-shrink: 0; text-align: center; }
.col-score     { width: 260px; flex-shrink: 0; }

/* Header */
.table-header {
  display: flex;
  align-items: center;
  background: #00b0e8;
  color: white;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 10px 16px;
  gap: 16px;
}

/* Grade row */
.grade-row {
  display: flex;
  align-items: center;
  background: #cce9f6;
  padding: 9px 16px;
  gap: 16px;
  cursor: pointer;
  user-select: none;
  border-top: 1px solid #bdddf0;
  transition: background 0.15s;
}
.grade-row:hover { background: #b8dff0; }

.grade-label {
  font-size: 13px;
  font-weight: 700;
  color: #1a6a9a;
  letter-spacing: 0.04em;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Topic row */
.topic-row {
  display: flex;
  align-items: center;
  background: #dff1fa;
  padding: 8px 16px 8px 32px;
  gap: 16px;
  cursor: pointer;
  user-select: none;
  border-top: 1px solid #cce4f2;
  transition: background 0.15s;
}
.topic-row:hover { background: #cce9f6; }

.topic-label {
  font-size: 13px;
  font-weight: 600;
  color: #1a6a9a;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Skill row */
.skill-row {
  display: flex;
  align-items: center;
  background: white;
  padding: 8px 16px 8px 48px;
  gap: 16px;
  border-top: 1px solid #e8f5fc;
  transition: background 0.1s;
}
.skill-row:hover { background: #f7fcff; }

.skill-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #333;
  overflow: hidden;
}

.skill-icon { color: #aaa; font-size: 14px; flex-shrink: 0; }

.skill-name-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.skill-code {
  font-size: 11px;
  color: #999;
  font-weight: 600;
  flex-shrink: 0;
  background: #f0f0f0;
  border-radius: 3px;
  padding: 1px 4px;
}

.skill-time,
.skill-questions {
  font-size: 13px;
  color: #555;
  font-weight: 500;
}

/* Expand arrow */
.expand-arrow {
  display: inline-block;
  font-size: 10px;
  color: #1a6a9a;
  transition: transform 0.2s;
}
.expand-arrow.expanded { transform: rotate(90deg); }

/* Score bar with arrow */
.score-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.score-from {
  font-size: 12px;
  color: #888;
  flex-shrink: 0;
  width: 14px;
  text-align: right;
}

.score-bar-track {
  flex: 1;
  height: 8px;
  background: #ddd;
  border-radius: 4px;
  position: relative;
  overflow: visible;
}

/* Flat, solid green bar - no gradient */
.score-bar-fill {
  height: 100%;
  background: #5cb85c;
  border-radius: 4px 0 0 4px;
  position: absolute;
  top: 0;
  left: 0;
  min-width: 2px;
}

/* Arrow head at the end */
.score-arrow-head {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-left: 10px solid #5cb85c;
  z-index: 2;
}

/* Score value to the right of arrow */
.score-value {
  font-size: 12px;
  font-weight: 700;
  color: #333;
  flex-shrink: 0;
  width: 28px;
  text-align: left;
}

/* Empty state */
.empty-state {
  padding: 40px;
  text-align: center;
  color: #999;
  font-size: 14px;
  background: white;
}
</style>

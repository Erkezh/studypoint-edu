<template>
  <section class="skill-analysis">
    <header class="sa-page-header">
      <div class="sa-title-row">
        <h1>ДАҒДЫЛАРДЫ ТАЛДАУ</h1>
        <button class="sa-icon-button" type="button" title="Басып шығару" @click="printReport">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 8V3h10v5M6 17H4V9h16v8h-2M7 14h10v7H7z" /></svg>
        </button>
      </div>

      <label class="skill-picker">
        <span>ДАҒДЫ</span>
        <select v-model="selectedSkillId">
          <option value="" disabled>Дағдыны таңдаңыз</option>
          <option v-for="skill in availableSkills" :key="skill.skillId" :value="skill.skillId">
            {{ skill.gradeLabel }} ({{ skill.skillCode }}) {{ skill.skillName }}
          </option>
        </select>
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6" /></svg>
      </label>
    </header>

    <div v-if="!selectedSkill" class="sa-empty">Дағдыны таңдау үшін жоғарыдағы тізімді пайдаланыңыз.</div>

    <template v-else>
      <section class="overview-card">
        <div class="overview-heading">
          <h2>Дағды шолуы</h2>
          <span>{{ dateLabel || 'Барлық уақыт' }}</span>
        </div>

        <div class="overview-grid">
          <div class="status-summary">
            <span class="metric-label">СЫНЫП КҮЙІ</span>
            <div class="status-content">
              <div class="donut" :style="{ background: donutBackground }">
                <div class="donut-center">{{ selectedSkillStats.studentsPracticed }}/{{ studentEntries.length }}</div>
              </div>
              <div class="legend">
                <span><i class="legend-mastered"></i>{{ masteredPercent }}% меңгерді</span>
                <span><i class="legend-practicing"></i>{{ practicingPercent }}% жаттығуда</span>
                <span><i class="legend-no-practice"></i>{{ noPracticePercent }}% практика жоқ</span>
              </div>
            </div>
          </div>

          <div class="summary-metric metric-questions">
            <span class="metric-label">ЖАУАП БЕРІЛГЕН СҰРАҚТАР</span>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m4 16.5 9.9-9.9 3.5 3.5-9.9 9.9H4zM14.9 5.6l1.5-1.5a1.5 1.5 0 0 1 2.1 0l1.4 1.4a1.5 1.5 0 0 1 0 2.1l-1.5 1.5z" /></svg>
            <strong>{{ selectedSkillStats.totalQuestions }}</strong>
          </div>

          <div class="summary-metric metric-time">
            <span class="metric-label">ЖҰМСАЛҒАН УАҚЫТ</span>
            <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5" /><path d="M12 7v5l3.5 2" /></svg>
            <strong>{{ selectedSkillStats.timeSpent }}</strong>
          </div>

          <div class="summary-metric metric-students">
            <span class="metric-label">ТӘЖІРИБЕ ЖАСАҒАН ОҚУШЫЛАР</span>
            <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="3.5" /><path d="M5.5 20c.2-4 2.5-6 6.5-6s6.3 2 6.5 6" /></svg>
            <strong>{{ selectedSkillStats.studentsPracticed }}</strong>
          </div>
        </div>
      </section>

      <section class="breakdown-card">
        <div class="breakdown-heading">
          <div>
            <h2>Сынып бөлінісі</h2>
            <p>{{ selectedSkill.gradeLabel }} · {{ selectedSkill.skillName }}</p>
          </div>
          <span>{{ studentEntries.length }} оқушы</span>
        </div>

        <StudentStatusSection
          tone="mastered"
          title="МЕҢГЕРІЛГЕН"
          :students="masteredStudents"
          empty-message="Бұл дағдыны әлі ешкім меңгерген жоқ."
          @select="goToQuestions"
        />

        <StudentStatusSection
          v-for="level in practiceLevels"
          :key="level.key"
          tone="practicing"
          :title="level.title"
          :students="level.students"
          :show-score="true"
          :empty-message="''"
          @select="goToQuestions"
        >
          <template #after-header>
            <span class="level-hint">{{ level.description }}</span>
          </template>
        </StudentStatusSection>

        <section v-if="recentSkillQuestions.length > 0" class="recent-questions">
          <div class="recent-heading">
            <div>
              <span>ОСЫ ДАҒДЫ БОЙЫНША СОҢҒЫ СҰРАҚТАР</span>
              <small>{{ recentSkillQuestions.length }} әрекет</small>
            </div>
            <div v-if="recentSkillQuestions.length > 1" class="question-nav">
              <button type="button" :disabled="selectedQuestionIndex === 0" @click="selectedQuestionIndex -= 1">‹</button>
              <span>{{ selectedQuestionIndex + 1 }} / {{ recentSkillQuestions.length }}</span>
              <button type="button" :disabled="selectedQuestionIndex === recentSkillQuestions.length - 1" @click="selectedQuestionIndex += 1">›</button>
            </div>
          </div>

          <div v-if="selectedPreviewQuestion" class="question-preview-shell">
            <div class="question-result" :class="selectedPreviewQuestion.isCorrect ? 'is-correct' : 'is-incorrect'">
              {{ selectedPreviewQuestion.isCorrect ? 'Дұрыс жауап' : 'Қате жауап' }}
            </div>
            <SessionQuestionPreview :question="selectedPreviewQuestion" />
          </div>
        </section>

        <StudentStatusSection
          tone="no-practice"
          title="ТӘЖІРИБЕ ЖОҚ"
          :students="noPracticeStudents"
          empty-message="Барлық оқушы осы дағды бойынша тәжірибе жасаған."
          @select="goToQuestions"
        />
      </section>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, ref, watch, type PropType } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import SessionQuestionPreview from './SessionQuestionPreview.vue'

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
  missed_questions?: number
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

interface StudentEntry {
  id: string
  name: string
  score: number
  totalQuestions: number
  totalTime: number
  practiced: boolean
}

interface StatusStudent {
  id: string
  name: string
  score: number
}

const StudentStatusSection = defineComponent({
  name: 'StudentStatusSection',
  props: {
    title: { type: String, required: true },
    tone: { type: String as PropType<'mastered' | 'practicing' | 'no-practice'>, required: true },
    students: { type: Array as PropType<StatusStudent[]>, required: true },
    showScore: { type: Boolean, default: false },
    emptyMessage: { type: String, required: true },
  },
  emits: ['select'],
  setup(props, { emit, slots }) {
    return () => h('section', { class: ['status-section', `status-${props.tone}`] }, [
      h('div', { class: 'status-header' }, [
        h('div', { class: 'status-heading' }, [
          h('span', { class: 'status-symbol' }, props.tone === 'mastered' ? '★' : props.tone === 'no-practice' ? '○' : '●'),
          h('span', props.title),
          slots['after-header']?.(),
        ]),
        h('span', { class: 'status-count' }, `${props.students.length} оқушы`),
      ]),
      props.students.length
        ? h('div', { class: 'status-students' }, props.students.map(student => h('button', {
          key: student.id,
          class: 'student-chip',
          type: 'button',
          onClick: () => emit('select', student.id),
        }, [
          h('span', student.name),
          props.showScore ? h('b', String(student.score)) : null,
        ])))
        : props.emptyMessage ? h('p', { class: 'status-empty' }, props.emptyMessage) : null,
    ])
  },
})

const props = withDefaults(defineProps<Props>(), { allStudentsData: () => [] })
const emit = defineEmits<{ (e: 'navigate', route: string, context?: Record<string, unknown>): void }>()
const analyticsStore = useAnalyticsStore()
const selectedSkillId = ref('')
const selectedQuestionIndex = ref(0)

const availableSkills = computed(() => {
  const skills = new Map<string, { skillId: string; skillName: string; skillCode: string; gradeLabel: string }>()
  for (const student of props.allStudentsData) {
    for (const skill of student.skills || []) {
      const skillId = String(skill.skill_id)
      if (!skills.has(skillId)) {
        skills.set(skillId, {
          skillId,
          skillName: skill.skill_name || 'Дағды',
          skillCode: skill.skill_code || '',
          gradeLabel: skill.grade_label || `${skill.grade_number || ''} сынып`,
        })
      }
    }
  }
  return [...skills.values()].sort((a, b) => a.gradeLabel.localeCompare(b.gradeLabel) || a.skillName.localeCompare(b.skillName))
})

const selectedSkill = computed(() => availableSkills.value.find(skill => skill.skillId === selectedSkillId.value) || null)

watch(availableSkills, skills => {
  if (!skills.some(skill => skill.skillId === selectedSkillId.value)) {
    selectedSkillId.value = skills[0]?.skillId || ''
  }
}, { immediate: true })

const studentEntries = computed<StudentEntry[]>(() => props.allStudentsData.map(student => {
  const skill = student.skills?.find(item => String(item.skill_id) === selectedSkillId.value)
  const totalQuestions = Number(skill?.total_questions || 0)
  const practiced = Boolean(skill && totalQuestions > 0)
  return {
    id: student.student_id,
    name: student.full_name,
    score: practiced ? Math.max(Number(skill?.best_smartscore || 0), Number(skill?.last_smartscore || 0)) : 0,
    totalQuestions: practiced ? totalQuestions : 0,
    totalTime: practiced ? Number(skill?.total_time_seconds || 0) : 0,
    practiced,
  }
}))

const masteredStudents = computed<StatusStudent[]>(() => studentEntries.value
  .filter(student => student.practiced && student.score >= 90)
  .sort((a, b) => b.score - a.score))

const practicingStudents = computed(() => studentEntries.value
  .filter(student => student.practiced && student.score < 90)
  .sort((a, b) => b.score - a.score))

const noPracticeStudents = computed<StatusStudent[]>(() => studentEntries.value
  .filter(student => !student.practiced)
  .sort((a, b) => a.name.localeCompare(b.name)))

const practiceLevels = computed(() => [
  { key: 'level-3', title: '3-ДЕҢГЕЙ', description: '80–89 SmartScore', students: practicingStudents.value.filter(student => student.score >= 80) },
  { key: 'level-2', title: '2-ДЕҢГЕЙ', description: '50–79 SmartScore', students: practicingStudents.value.filter(student => student.score >= 50 && student.score < 80) },
  { key: 'level-1', title: '1-ДЕҢГЕЙ', description: '0–49 SmartScore', students: practicingStudents.value.filter(student => student.score < 50) },
].filter(level => level.students.length > 0))

const studentCount = computed(() => Math.max(studentEntries.value.length, 1))
const masteredPercent = computed(() => Math.round((masteredStudents.value.length / studentCount.value) * 100))
const practicingPercent = computed(() => Math.round((practicingStudents.value.length / studentCount.value) * 100))
const noPracticePercent = computed(() => Math.max(0, 100 - masteredPercent.value - practicingPercent.value))

const donutBackground = computed(() => {
  const masteredEnd = masteredPercent.value
  const practicingEnd = masteredEnd + practicingPercent.value
  return `conic-gradient(#86ce1c 0 ${masteredEnd}%, #18afe4 ${masteredEnd}% ${practicingEnd}%, #ff9e13 ${practicingEnd}% 100%)`
})

const selectedSkillStats = computed(() => {
  const practiced = studentEntries.value.filter(student => student.practiced)
  const totalSeconds = practiced.reduce((sum, student) => sum + student.totalTime, 0)
  return {
    totalQuestions: practiced.reduce((sum, student) => sum + student.totalQuestions, 0),
    studentsPracticed: practiced.length,
    timeSpent: formatDuration(totalSeconds),
  }
})

const recentSkillQuestions = computed(() => {
  const start = props.dateRange?.start
  const end = props.dateRange?.end
  return (analyticsStore.allQuestions || [])
    .filter(question => {
      if (String(question.skill_id || '') !== selectedSkillId.value) return false
      const timestamp = String(question.answered_at || question.created_at || '')
      if (!start || !timestamp) return true
      const date = new Date(timestamp)
      return date >= start && (!end || date <= end)
    })
    .sort((a, b) => new Date(String(b.answered_at || b.created_at || 0)).getTime() - new Date(String(a.answered_at || a.created_at || 0)).getTime())
    .slice(0, 10)
})

const selectedPreviewQuestion = computed(() => {
  const question = recentSkillQuestions.value[selectedQuestionIndex.value]
  if (!question) return null
  const rawAnswer = normalizeJson(question.user_answer)
  const questionData = asRecord(question.question_data)
  const submittedData = asRecord(rawAnswer)
  const submittedQuestionData = asRecord(submittedData?.questionData) || asRecord(submittedData?.visualData)
  const data = submittedQuestionData ? { ...questionData, ...submittedQuestionData } : questionData
  const type = String(question.question_type || question.type || '')
  return {
    prompt: String(question.question_prompt || question.prompt || data.prompt || ''),
    type,
    data,
    userAnswer: rawAnswer,
    isCorrect: Boolean(question.is_correct),
    correctAnswer: normalizeJson(question.correct_answer),
    seed: (question.seed ?? data.seed ?? submittedData?.seed ?? null) as string | number | null,
    level: (question.level ?? data.level ?? null) as string | number | null,
  }
})

watch([selectedSkillId, recentSkillQuestions], () => { selectedQuestionIndex.value = 0 })

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {}
}

function normalizeJson(value: unknown): unknown {
  if (typeof value !== 'string') return value
  try { return JSON.parse(value) } catch { return value }
}

function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  if (minutes < 1) return '<1 мин'
  if (minutes < 60) return `${minutes} мин`
  const hours = Math.floor(minutes / 60)
  const remaining = minutes % 60
  return remaining ? `${hours} сағ ${remaining} мин` : `${hours} сағ`
}

function printReport() { window.print() }
function goToQuestions(studentId: string) { emit('navigate', 'questions', { studentId }) }
</script>

<style scoped>
.skill-analysis {
  color: #4a4f54;
  font-family: 'Open Sans', 'Helvetica Neue', sans-serif;
}
.sa-page-header { border-bottom: 1px solid #e5e9eb; padding-bottom: 20px; }
.sa-title-row { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.sa-title-row h1 { margin: 0; color: #3d4246; font-size: 28px; font-weight: 500; letter-spacing: -.4px; }
.sa-icon-button { display: grid; width: 30px; height: 30px; place-items: center; border: 0; background: transparent; color: #a2aaad; cursor: pointer; }
.sa-icon-button:hover { color: #4e575c; }
.sa-icon-button svg { width: 20px; fill: none; stroke: currentColor; stroke-width: 1.6; stroke-linejoin: round; }
.skill-picker { position: relative; display: flex; align-items: center; width: min(100%, 520px); border: 1px solid #d7dcdf; border-radius: 5px; background: #fff; color: #626a6f; }
.skill-picker > span { padding-left: 14px; color: #939b9f; font-size: 12px; font-weight: 700; letter-spacing: .25px; }
.skill-picker select { width: 100%; appearance: none; border: 0; background: transparent; color: #545b5f; cursor: pointer; font: inherit; font-size: 14px; outline: 0; padding: 13px 38px 13px 7px; }
.skill-picker > svg { position: absolute; right: 12px; width: 18px; fill: none; stroke: #9ca5a9; stroke-width: 2; pointer-events: none; }
.sa-empty { margin-top: 28px; border: 1px dashed #d9dfe1; background: #fff; color: #879196; padding: 44px 20px; text-align: center; }
.overview-card, .breakdown-card { margin-top: 26px; border: 1px solid #e2e7e9; background: #fff; box-shadow: 0 1px 2px rgb(21 47 56 / 4%); }
.overview-heading, .breakdown-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding: 20px 24px 15px; }
.overview-heading h2, .breakdown-heading h2 { margin: 0; color: #53595d; font-size: 23px; font-weight: 400; letter-spacing: -.3px; }
.overview-heading span, .breakdown-heading > span { color: #929a9d; font-size: 12px; }
.overview-grid { display: grid; grid-template-columns: 1.6fr repeat(3, 1fr); border-top: 1px solid #edf0f1; }
.status-summary, .summary-metric { min-height: 166px; padding: 20px; }
.summary-metric { display: flex; flex-direction: column; align-items: center; border-left: 1px solid #edf0f1; text-align: center; }
.metric-label { color: #788187; font-size: 11px; font-weight: 700; letter-spacing: .2px; }
.status-content { display: flex; align-items: center; gap: 22px; margin-top: 14px; }
.donut { display: grid; width: 112px; height: 112px; flex: 0 0 112px; place-items: center; border-radius: 50%; }
.donut::after { width: 76px; height: 76px; border-radius: 50%; background: #fff; content: ''; grid-area: 1 / 1; }
.donut-center { z-index: 1; grid-area: 1 / 1; color: #5c6569; font-size: 14px; font-weight: 700; }
.legend { display: grid; gap: 10px; color: #596166; font-size: 13px; }
.legend span { display: flex; align-items: center; gap: 8px; white-space: nowrap; }
.legend i { width: 11px; height: 11px; border-radius: 2px; }
.legend-mastered { background: #86ce1c; }.legend-practicing { background: #18afe4; }.legend-no-practice { background: #ff9e13; }
.summary-metric svg { width: 35px; height: 35px; margin-top: 20px; fill: none; stroke-width: 1.7; }
.summary-metric strong { margin-top: 7px; font-size: 31px; line-height: 1; }
.metric-questions svg, .metric-questions strong { color: #80c519; fill: currentColor; stroke: currentColor; }.metric-time svg, .metric-time strong { color: #12aee4; }.metric-students svg, .metric-students strong { color: #fb9b15; }
.breakdown-heading { padding-bottom: 19px; }.breakdown-heading p { margin: 5px 0 0; color: #8a9498; font-size: 13px; }
.status-section { border-top: 1px solid #edf0f1; }.status-header { display: flex; align-items: center; justify-content: space-between; min-height: 43px; padding: 0 19px; color: #fff; font-size: 12px; font-weight: 700; }.status-heading { display: flex; align-items: center; gap: 9px; }.status-symbol { font-size: 17px; line-height: 1; }.status-count { opacity: .9; font-size: 12px; font-weight: 600; }.status-mastered .status-header { background: #85ca1d; }.status-practicing .status-header { background: #18afe4; }.status-no-practice .status-header { background: #ff9e13; }.level-hint { margin-left: 4px; color: rgb(255 255 255 / 80%); font-size: 11px; font-weight: 400; }
.status-empty { margin: 0; padding: 22px 20px; color: #7f898d; font-size: 13px; font-style: italic; }.status-students { display: flex; flex-wrap: wrap; gap: 10px; padding: 16px 20px; }.student-chip { display: inline-flex; align-items: center; gap: 11px; border: 1px solid #b7dc7f; border-radius: 3px; background: #fff; color: #6ea615; cursor: pointer; font: inherit; font-size: 13px; font-weight: 600; padding: 8px 11px; }.student-chip:hover { background: #f8fdf0; }.student-chip b { color: #4f5960; }.status-practicing .student-chip { border-color: #8ddcf6; color: #168bb8; }.status-no-practice .student-chip { border-color: #facb83; color: #a86a05; }
:deep(.status-header) { display: flex; align-items: center; justify-content: space-between; min-height: 43px; padding: 0 19px; color: #fff; font-size: 12px; font-weight: 700; }
:deep(.status-heading) { display: flex; align-items: center; gap: 9px; }
:deep(.status-symbol) { font-size: 17px; line-height: 1; }
:deep(.status-count) { opacity: .9; font-size: 12px; font-weight: 600; }
:deep(.status-mastered .status-header) { background: #85ca1d; }
:deep(.status-practicing .status-header) { background: #18afe4; }
:deep(.status-no-practice .status-header) { background: #ff9e13; }
:deep(.level-hint) { margin-left: 4px; color: rgb(255 255 255 / 80%); font-size: 11px; font-weight: 400; }
:deep(.status-empty) { margin: 0; padding: 22px 20px; color: #7f898d; font-size: 13px; font-style: italic; }
:deep(.status-students) { display: flex; flex-wrap: wrap; gap: 10px; padding: 16px 20px; }
:deep(.student-chip) { display: inline-flex; align-items: center; gap: 11px; border: 1px solid #b7dc7f; border-radius: 3px; background: #fff; color: #6ea615; cursor: pointer; font: inherit; font-size: 13px; font-weight: 600; padding: 8px 11px; }
:deep(.student-chip:hover) { background: #f8fdf0; }
:deep(.student-chip b) { color: #4f5960; }
:deep(.status-practicing .student-chip) { border-color: #8ddcf6; color: #168bb8; }
:deep(.status-no-practice .student-chip) { border-color: #facb83; color: #a86a05; }
.recent-questions { border-top: 1px solid #edf0f1; padding: 20px; }.recent-heading { display: flex; align-items: center; justify-content: space-between; gap: 14px; border-bottom: 1px solid #e8edef; padding-bottom: 12px; }.recent-heading > div:first-child { display: grid; gap: 3px; }.recent-heading span { color: #707a7f; font-size: 11px; font-weight: 700; }.recent-heading small { color: #a0a8ab; font-size: 12px; }.question-nav { display: flex; align-items: center; gap: 8px; }.question-nav button { width: 26px; height: 26px; border: 1px solid #dce3e5; border-radius: 3px; background: #fff; color: #5c686d; cursor: pointer; font-size: 21px; line-height: 1; }.question-nav button:disabled { color: #cbd2d5; cursor: default; }.question-nav span { color: #6a7479; font-size: 12px; font-weight: 600; }.question-preview-shell { position: relative; padding: 20px 4px 0; }.question-result { position: absolute; z-index: 1; top: 19px; right: 4px; border-radius: 999px; font-size: 11px; font-weight: 700; padding: 5px 9px; }.is-correct { background: #eff9dc; color: #679f14; }.is-incorrect { background: #fff1ef; color: #e05a50; }
@media (max-width: 850px) { .overview-grid { grid-template-columns: 1fr 1fr; }.status-summary { grid-column: span 2; }.summary-metric:nth-child(2) { border-left: 0; }.summary-metric { border-top: 1px solid #edf0f1; } }
@media (max-width: 560px) { .sa-title-row h1 { font-size: 23px; }.skill-picker { width: 100%; }.overview-heading, .breakdown-heading { align-items: flex-start; flex-direction: column; gap: 4px; }.overview-grid { grid-template-columns: 1fr; }.status-summary { grid-column: auto; }.summary-metric { min-height: 135px; border-left: 0; }.status-content { gap: 14px; }.donut { width: 92px; height: 92px; flex-basis: 92px; }.donut::after { width: 62px; height: 62px; }.legend { font-size: 12px; }.recent-questions { padding: 16px; }.question-result { position: static; display: inline-block; margin-bottom: 10px; } }
</style>

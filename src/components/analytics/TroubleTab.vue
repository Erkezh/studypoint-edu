<template>
  <div>
    <div class="summary-header">
      <h1 class="summary-title">{{ isClassWide ? 'ЖАЛПЫ ҚИЫНДЫҚТАР' : ('ҚИЫНДЫҚТАР: ' + userName) }}</h1>
      <button class="print-btn" @click="printReport">
        <svg class="print-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z" />
        </svg>
      </button>
    </div>

    <!-- Class-wide Student Selector Dropdown -->
    <div class="trouble-student-selector" v-if="isClassWide && allStudentsData && allStudentsData.length > 0">
      <div class="custom-select-wrapper">
        <label class="ixl-select-label">ОҚУШЫ:</label>
        <select class="ixl-select" @change="onStudentSelectChanged($event)">
          <option value="ALL">Барлық оқушылар</option>
          <option v-for="st in allStudentsData" :key="st.student_id" :value="st.student_id">
            {{ st.full_name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Subtitle mapping IXL's 'Ways to help individual students...' -->
    <p class="trouble-subtitle" v-if="troubleSpotSkills.length > 0">Оқушыларға көмектесу жолдары...</p>

    <!-- Empty State -->
    <div v-if="troubleSpotSkills.length === 0" class="empty-state success">
      <span class="success-icon flex items-center justify-center">
        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
      </span>
      <p class="success-text">Керемет! Қателер жоқ!</p>
      <p class="success-subtext">Барлық сұрақтарға дұрыс жауап берілді.</p>
    </div>

    <!-- Skills List -->
    <div v-else class="trouble-skills-list">
      <div v-for="skill in troubleSpotSkills" :key="skill.skillId" class="ixl-trouble-card">
        
        <!-- IXL Horizontal Blue Header -->
        <div class="ixl-card-header">
          <div class="ixl-header-left">
            <span class="ixl-grade-code">{{ skill.gradeLabel }} ({{ skill.skillCode }})</span>
            <span class="ixl-skill-title">{{ skill.skillName }}</span>
          </div>
          <div class="ixl-header-right">
            <span class="ixl-shortcut">
              <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
              Search shortcut: {{ skill.skillCode || 'N/A' }}
            </span>
            <div class="ixl-student-count-badge" v-if="isClassWide">
              <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
              <span>{{ skill.strugglingStudentsCount }}</span>
            </div>
          </div>
        </div>

        <!-- Content Body -->
        <div class="ixl-card-body">
          <div class="ixl-section-title">ОСЫ ТАПСЫРМА ТҮРІНДЕГІ ҚАТЕ ЖІБЕРІЛГЕН СҰРАҚТАР</div>
          
          <div class="ixl-question-carousel">
            <button class="ixl-arrow-btn" @click="navigateTroubleQuestion(skill.skillId, -1)" :disabled="(troubleQuestionIndex[skill.skillId] || 0) <= 0">
              <svg viewBox="0 0 24 24" fill="currentColor" width="36" height="48" preserveAspectRatio="none"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
            </button>
            
            <div class="ixl-question-box">
              <p class="ixl-question-text">
                {{ skill.questions[troubleQuestionIndex[skill.skillId] || 0]?.prompt || 'Сұрақ мәтіні жоқ' }}
              </p>
            </div>
            
            <button class="ixl-arrow-btn" @click="navigateTroubleQuestion(skill.skillId, 1)" :disabled="(troubleQuestionIndex[skill.skillId] || 0) >= skill.questions.length - 1">
              <svg viewBox="0 0 24 24" fill="currentColor" width="36" height="48" preserveAspectRatio="none"><path d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z"/></svg>
            </button>
          </div>

          <!-- Stuck Students List (Only for Class Wide) -->
          <div v-if="isClassWide && skill.stuckStudents.length > 0" class="ixl-stuck-section">
            <div class="ixl-stuck-header">
              <div class="ixl-stuck-title" @click="toggleStuck(skill.skillId)">
                ОСЫ ТАПСЫРМА ТҮРІНДЕ ҚИЫНАЛАТЫН ОҚУШЫЛАР
                <span class="ixl-toggle-box">{{ stuckExpanded[skill.skillId] !== false ? '-' : '+' }}</span>
              </div>
            </div>
            <div class="ixl-stuck-list" v-show="stuckExpanded[skill.skillId] !== false">
              <div v-for="st in skill.stuckStudents" :key="st.id" class="ixl-stuck-badge">
                {{ st.name }} - {{ st.smartscore }}
              </div>
            </div>
          </div>
          
          <!-- Individual view smartscore footer -->
          <div v-if="!isClassWide" class="trouble-skill-footer">
            <div class="trouble-footer-item">
              <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16" class="trouble-star"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
              <span>SmartScore: <strong>{{ skill.smartscore }}</strong></span>
            </div>
            <div class="trouble-footer-item trouble-footer-warning">
              <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>
              <span><strong>{{ skill.missedCount }}</strong> қате жіберілген сұрақ</span>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { useAuthStore } from '@/stores/auth'
import { useTeacherStore } from '@/stores/teacher'

const props = defineProps<{
  gradeFrom: number
  gradeTo: number
  dateRange: { start: Date | null; end: Date | null }
  isClassWide?: boolean
  allStudentsData?: Array<{
    student_id: string
    full_name: string
    skills: Array<{ skill_id: number; last_smartscore?: number; best_smartscore?: number }>
  }>
}>()

const analyticsStore = useAnalyticsStore()
const authStore = useAuthStore()
const teacherStore = useTeacherStore()

const emit = defineEmits<{
  (e: 'select-student', studentId: string): void
}>()

const onStudentSelectChanged = (event: Event) => {
  const target = event.target as HTMLSelectElement
  if (target.value !== 'ALL') {
    emit('select-student', target.value)
    // Reset back to ALL visually since we are redirecting away from this view
    target.value = 'ALL'
  }
}

const isTeacher = computed(() => authStore.isTeacher)

const getStudentName = () => {
  if (isTeacher.value) {
    try {
      const state = JSON.parse(localStorage.getItem('analytics_view_state') || '{}')
      if (state.selectedStudentId && teacherStore.students) {
        const student = teacherStore.students.find((s: Record<string, unknown>) => s.id === state.selectedStudentId)
        if (student) return student.full_name as string
      }
    } catch { }
  }
  return authStore.user?.full_name || 'Сіздің'
}

const userName = computed(() => getStudentName())

const printReport = () => {
  window.print()
}

const troubleQuestionIndex = ref<Record<number, number>>({})
const stuckExpanded = ref<Record<number, boolean>>({})

onMounted(() => {
  // Can be left empty or removed since template now defaults to !== false
})

const toggleStuck = (skillId: number) => {
  stuckExpanded.value[skillId] = stuckExpanded.value[skillId] === false ? true : false
}

const isPlugin = (q: Record<string, unknown>) =>
  (q.question_type as string) === 'PLUGIN' || (q.question_type as string) === 'INTERACTIVE'

const getPluginPrompt = (q: Record<string, unknown>): string => {
  const ua = q.user_answer as Record<string, unknown> | null
  if (!ua) return (q.question_prompt as string) || ''
  return (ua.question ?? ua.prompt ?? ua.equation ?? ua.problem ?? ua.questionText ?? q.question_prompt ?? '') as string
}

const troubleSpotSkills = computed(() => {
  const questions = analyticsStore.allQuestions || []
  if (questions.length === 0) return []

  const isInDateRange = (dateStr: string | undefined) => {
    if (!props.dateRange.start) return true
    if (!dateStr) return false
    const d = new Date(dateStr)
    const end = props.dateRange.end || new Date()
    return d >= props.dateRange.start && d <= end
  }

  const skillInfoMap = new Map<number, { name: string; grade: number; label: string; code: string; smartscore: number }>()
  for (const s of analyticsStore.skills) {
    const rec = s as Record<string, unknown>
    const grade = (rec.grade_number as number) ?? 0
    if (grade < props.gradeFrom || grade > props.gradeTo) continue
    skillInfoMap.set(rec.skill_id as number, {
      name: (rec.skill_name as string) || 'Белгісіз',
      grade,
      label: (rec.grade_label as string) || `${grade} сынып`,
      code: (rec.skill_code as string) || '',
      smartscore: (rec.best_smartscore as number) || 0,
    })
  }

  const skillMissed = new Map<number, Array<Record<string, unknown>>>()
  for (const q of questions) {
    const rec = q as Record<string, unknown>
    if (rec.is_correct) continue
    const skillId = rec.skill_id as number
    if (!skillInfoMap.has(skillId)) continue
    const ts = (rec.answered_at || rec.created_at) as string
    if (!isInDateRange(ts)) continue
    if (!skillMissed.has(skillId)) skillMissed.set(skillId, [])
    skillMissed.get(skillId)!.push(rec)
  }

  const result = Array.from(skillMissed.entries()).map(([skillId, qs]) => {
    const info = skillInfoMap.get(skillId) || { name: 'Белгісіз', grade: 0, label: '', code: '', smartscore: 0 }
    
    let strugglingStudentsCount = 0
    const stuckStudents = []

    if (props.isClassWide) {
      const studentIds = new Set(qs.map(q => q.user_id as string))
      strugglingStudentsCount = studentIds.size

      if (props.allStudentsData && Array.isArray(props.allStudentsData)) {
        for (const sid of studentIds) {
          const studentInfo = props.allStudentsData.find(s => s.student_id === sid)
          if (studentInfo) {
            const sk = (studentInfo.skills || []).find((s_skill: { skill_id: number; last_smartscore?: number; best_smartscore?: number }) => s_skill.skill_id === skillId)
            const sc = sk ? Math.max(Number(sk.best_smartscore || 0), Number(sk.last_smartscore || 0)) : 0
            stuckStudents.push({
              id: sid,
              name: studentInfo.full_name,
              smartscore: sc
            })
          } else {
            stuckStudents.push({
              id: sid,
              name: 'Оқушы',
              smartscore: 0
            })
          }
        }
      }
      stuckStudents.sort((a, b) => a.smartscore - b.smartscore)
    }

    return {
      skillId,
      skillName: info.name,
      grade: info.grade,
      gradeLabel: info.label,
      skillCode: info.code,
      smartscore: info.smartscore,
      missedCount: qs.length,
      strugglingStudentsCount,
      stuckStudents,
      questions: qs.map(q => ({
        questionType: (q.question_type as string) || '',
        prompt: isPlugin(q) ? getPluginPrompt(q) : ((q.question_prompt as string) || ''),
      })),
    }
  })

  result.sort((a, b) => {
    if (props.isClassWide) {
      if (b.strugglingStudentsCount !== a.strugglingStudentsCount) {
        return b.strugglingStudentsCount - a.strugglingStudentsCount
      }
    }
    return b.missedCount - a.missedCount
  })
  
  return result
})

const navigateTroubleQuestion = (skillId: number, direction: number) => {
  const skill = troubleSpotSkills.value.find(s => s.skillId === skillId)
  if (!skill) return
  const current = troubleQuestionIndex.value[skillId] || 0
  const next = current + direction
  if (next >= 0 && next < skill.questions.length) {
    troubleQuestionIndex.value[skillId] = next
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
.print-btn:hover { color: #333; }
.print-icon { width: 20px; height: 20px; }

/* Student Dropdown */
.trouble-student-selector {
  margin-top: 16px;
  margin-bottom: 24px;
}
.custom-select-wrapper {
  display: inline-flex;
  align-items: center;
  border: 1px solid #dcdcdc;
  border-radius: 4px;
  padding: 6px 12px;
  background-color: white;
}
.ixl-select-label {
  font-size: 11px;
  font-weight: 700;
  color: #999;
  letter-spacing: 0.05em;
  margin-right: 8px;
}
.ixl-select {
  border: none;
  outline: none;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  padding: 0 24px 0 0;
  cursor: pointer;
  background: transparent;
  appearance: none;
  background-image: url('data:image/svg+xml;charset=US-ASCII,<svg viewBox="0 0 24 24" fill="%23999" xmlns="http://www.w3.org/2000/svg"><path d="M7 10l5 5 5-5z"/></svg>');
  background-repeat: no-repeat;
  background-position: right center;
  background-size: 20px;
}

.trouble-subtitle {
  font-size: 22px;
  font-weight: 300;
  color: #555;
  margin: 16px 0 28px;
}

.empty-state {
  text-align: center;
  padding: 48px;
  color: #888;
}
.empty-state.success {
  background: #e8f5e9;
  border-radius: 12px;
  padding: 40px;
}
.success-icon { font-size: 48px; margin-bottom: 16px; }
.success-text { font-size: 18px; font-weight: 500; color: #2e7d32; }
.success-subtext { font-size: 14px; color: #666; margin-top: 8px; }

/* IXL Layout Card */
.trouble-skills-list {
  display: flex;
  flex-direction: column;
  gap: 32px;
}
.ixl-trouble-card {
  background: white;
  border-radius: 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
}
.ixl-card-header {
  background-color: #00BBD4;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
}
.ixl-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.ixl-grade-code {
  font-weight: 600;
  font-size: 15px;
}
.ixl-skill-title {
  font-size: 14px;
  font-weight: 400;
}
.ixl-header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.ixl-shortcut {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  opacity: 0.9;
}
.ixl-student-count-badge {
  display: flex;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 4px;
  gap: 8px;
  font-weight: bold;
}

.ixl-card-body {
  padding: 32px 48px;
}
.ixl-section-title {
  font-size: 11px;
  font-weight: 700;
  color: #999;
  letter-spacing: 0.05em;
  margin-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 8px;
}

.ixl-question-carousel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 32px 0 48px;
}
.ixl-arrow-btn {
  background: transparent;
  border: none;
  color: #eee;
  cursor: pointer;
  outline: none;
}
.ixl-arrow-btn:hover:not(:disabled) {
  color: #ccc;
}
.ixl-arrow-btn:disabled {
  opacity: 0.3;
  cursor: default;
}
.ixl-question-box {
  flex: 1;
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}
.ixl-question-text {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.ixl-stuck-section {
  margin-top: 24px;
}
.ixl-stuck-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 8px;
  margin-bottom: 16px;
}
.ixl-stuck-title {
  font-size: 11px;
  font-weight: 700;
  color: #999;
  letter-spacing: 0.05em;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}
.ixl-toggle-box {
  border: 1px solid #ccc;
  width: 14px;
  height: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  border-radius: 2px;
}
.ixl-stuck-actions {
  display: flex;
  gap: 12px;
  color: #00BBD4;
}
.ixl-icon-btn {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
}
.ixl-icon-btn:hover { opacity: 0.8; }
.ixl-stuck-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.ixl-stuck-badge {
  border: 1px solid #81C784;
  color: #4CAF50;
  padding: 6px 16px;
  border-radius: 4px;
  font-weight: 500;
  font-size: 14px;
  background-color: white;
}

/* For individual view footer */
.trouble-skill-footer {
  display: flex;
  align-items: center;
  gap: 32px;
  padding-top: 24px;
  border-top: 1px solid #eee;
  font-size: 13px;
  color: #666;
}
.trouble-footer-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.trouble-star { color: #FFB300; }
.trouble-footer-warning svg { color: #FF9800; }
</style>

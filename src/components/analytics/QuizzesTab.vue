<template>
  <div class="quizzes-report-container p-6 bg-[#f3f7fc] min-h-screen">
    <!-- Quiz Selector Dropdown at the top (in place of student dropdown) -->
    <div class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm mb-8 flex items-center gap-4">
      <span class="font-bold text-gray-700 text-sm">Select Quiz:</span>
      <select 
        v-model="selectedQuizId" 
        class="border border-gray-200 rounded-lg px-4 py-2 bg-gray-50 text-gray-700 font-medium focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500 text-sm min-w-[280px]"
      >
        <option value="">-- Select a Quiz to View Report --</option>
        <option v-for="quiz in allQuizzes" :key="quiz.id" :value="quiz.id">
          {{ quiz.name }} (Assigned: {{ quiz.assignments?.[0] ? formatDateShort(quiz.assignments[0].created_at) : 'Draft' }})
        </option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="report-loading flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#00acc1]"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="report-error bg-red-50 text-red-600 p-4 rounded-lg border border-red-100 mb-6">
      {{ error }}
    </div>

    <!-- No quiz selected -->
    <div v-else-if="!selectedQuiz" class="report-empty bg-white p-12 rounded-xl border border-gray-100 shadow-sm text-center">
      <div class="empty-icon text-4xl mb-4">📋</div>
      <h3 class="text-lg font-bold text-gray-800 mb-2">No Quiz Selected</h3>
      <p class="text-sm text-gray-500">Please select a quiz from the dropdown menu above to view its detailed analytics report.</p>
    </div>

    <!-- Quiz Report Detail View -->
    <div v-else class="quiz-report-view bg-white p-8 rounded-xl border border-gray-100 shadow-sm max-w-5xl mx-auto">
      <div class="flex justify-between items-center mb-6 border-b border-gray-100 pb-4">
        <div>
          <h2 class="text-2xl font-bold text-gray-900">{{ selectedQuiz.name }} — Quiz Report</h2>
          <p class="text-xs text-gray-500 mt-1">
            Period: {{ getPeriodDates(selectedQuiz) }} | Total {{ selectedQuiz.questions.length }} questions
          </p>
        </div>
        <div class="text-right">
          <div class="text-xs text-gray-400 font-bold uppercase">Class average</div>
          <div class="text-3xl font-extrabold text-green-600 mt-1">{{ getAverageScoreText(selectedQuiz) }}</div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
        <div class="bg-gray-50 border border-gray-100 p-4 rounded-xl text-center">
          <div class="text-xs text-gray-400 font-bold uppercase">Total students</div>
          <div class="text-2xl font-extrabold text-gray-800 mt-1">
            {{ getCompletionStats(selectedQuiz).total }}
          </div>
        </div>
        <div class="bg-gray-50 border border-gray-100 p-4 rounded-xl text-center">
          <div class="text-xs text-gray-400 font-bold uppercase">Completed</div>
          <div class="text-2xl font-extrabold text-blue-600 mt-1">
            {{ getCompletionStats(selectedQuiz).completed }}
          </div>
        </div>
        <div class="bg-gray-50 border border-gray-100 p-4 rounded-xl text-center">
          <div class="text-xs text-gray-400 font-bold uppercase">Completion rate</div>
          <div class="text-2xl font-extrabold text-orange-500 mt-1">
            {{ getCompletionPercent(selectedQuiz) }}%
          </div>
        </div>
      </div>

      <!-- Student Results Table -->
      <div class="results-section">
        <h3 class="text-lg font-bold text-gray-800 mb-4 border-b border-gray-100 pb-2">Student Results</h3>
        <div class="results-table-wrapper overflow-x-auto">
          <table class="results-table min-w-full divide-y divide-gray-100 text-left text-sm">
            <thead class="bg-gray-50 text-xs font-bold text-gray-500 G uppercase tracking-wider">
              <tr>
                <th class="px-6 py-4">Student Name</th>
                <th class="px-6 py-4">Status</th>
                <th class="px-6 py-4">Score</th>
                <th class="px-6 py-4">Time spent</th>
                <th v-for="(q, idx) in selectedQuiz.questions" :key="q.id" class="px-3 py-4 text-center">
                  Q{{ idx + 1 }}
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 bg-white">
              <tr v-for="student in reportStudents" :key="student.id" class="hover:bg-gray-50/50 transition">
                <td class="px-6 py-4 font-semibold text-gray-900">{{ student.full_name }}</td>
                <td class="px-6 py-4">
                  <span 
                    :class="student.completed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'"
                    class="px-2 py-0.5 rounded text-xs font-semibold whitespace-nowrap"
                  >
                    {{ student.completed ? 'Completed' : 'In progress' }}
                  </span>
                </td>
                <td class="px-6 py-4 font-bold" :class="student.completed ? 'text-gray-900' : 'text-gray-400'">
                  {{ student.score }}%
                  <span class="text-xs text-gray-400 font-normal">({{ student.correctAnswers }} / {{ selectedQuiz.questions.length }})</span>
                </td>
                <td class="px-6 py-4 text-gray-500">{{ student.timeSpent }}</td>
                <td v-for="(q, idx) in selectedQuiz.questions" :key="q.id" class="px-3 py-4 text-center">
                  <span v-if="!student.completed" class="text-gray-300">—</span>
                  <span v-else-if="student.questionResults[idx]" class="text-green-500 font-extrabold text-base" title="Correct">✓</span>
                  <span v-else class="text-red-500 font-extrabold text-base" title="Incorrect">✗</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useQuizStore } from '@/stores/quiz'
import { useTeacherStore } from '@/stores/teacher'
import { storeToRefs } from 'pinia'
import type { QuizResponse, QuizAssignmentResponse } from '@/api/quiz'

const quizStore = useQuizStore()
const teacherStore = useTeacherStore()
const { quizzes: allQuizzes, loading, error } = storeToRefs(quizStore)
const { students: teacherStudents } = storeToRefs(teacherStore)

const selectedQuizId = ref('')
const route = useRoute()

const selectedQuiz = computed<QuizResponse | null>(() => {
  if (!selectedQuizId.value) return null
  return allQuizzes.value.find(q => q.id === selectedQuizId.value) || null
})

onMounted(async () => {
  await Promise.all([
    quizStore.fetchQuizzes(),
    teacherStore.fetchStudents()
  ])
})

// Auto-select quiz from route query (?quizId=xxx)
watch(
  [() => route.query.quizId, allQuizzes],
  ([newQuizId, quizzes]) => {
    if (newQuizId && typeof newQuizId === 'string' && quizzes && quizzes.length > 0) {
      const found = quizzes.find(q => q.id === newQuizId)
      if (found) {
        selectedQuizId.value = found.id
      }
    }
  },
  { immediate: true }
)

const formatDateShort = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const getPeriodDates = (quiz: QuizResponse) => {
  const assignments = quiz.assignments || []
  if (!assignments.length) return 'Draft'
  const first = assignments[0]
  const start = formatDateShort(first.created_at)
  const end = first.end_at ? formatDateShort(first.end_at) : 'Present'
  return `${start} – ${end}, 2026`
}

const getCompletionStats = (quiz: QuizResponse) => {
  const assignments = quiz.assignments || []
  const total = assignments.length
  const completed = assignments.filter(a => a.completed_at !== null).length
  return { completed, total }
}

const getCompletionPercent = (quiz: QuizResponse) => {
  const { completed, total } = getCompletionStats(quiz)
  if (total === 0) return 0
  return Math.round((completed / total) * 100)
}

const getAverageScoreText = (quiz: QuizResponse) => {
  const assignments = quiz.assignments || []
  const completedAssignments = assignments.filter(a => a.completed_at !== null)
  if (completedAssignments.length === 0) return '0%'
  const totalScore = completedAssignments.reduce((acc, a) => acc + (a.score || 0), 0)
  const avg = Math.round(totalScore / completedAssignments.length)
  return `${avg}% (${completedAssignments.length}/${assignments.length})`
}

const reportStudents = computed(() => {
  if (!selectedQuiz.value) return []
  const quiz = selectedQuiz.value
  const assignments = quiz.assignments || []

  return assignments.map(assignment => {
    const student = teacherStudents.value.find(s => s.id === assignment.student_id)
    const fullName = student?.full_name || `Оқушы (${assignment.student_id?.slice(0, 8) || 'Белгісіз'})`

    const isCompleted = assignment.completed_at !== null
    const score = assignment.score || 0

    let timeSpent = '—'
    if (isCompleted && assignment.time_spent_seconds !== null && assignment.time_spent_seconds !== undefined) {
      const mins = Math.floor(assignment.time_spent_seconds / 60)
      const secs = assignment.time_spent_seconds % 60
      timeSpent = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
    }

    const totalQuestions = quiz.questions.length || 5
    let correctAnswers = 0
    let questionResults: boolean[] = []

    if (isCompleted) {
      const sortedQs = [...quiz.questions].sort((a, b) => a.position - b.position)
      const resultsMap = (assignment.question_results as Record<string, boolean>) || {}
      
      for (const q of sortedQs) {
        const qId = q.question?.id
        const correct = resultsMap[String(qId)] === true
        if (correct) correctAnswers++
        questionResults.push(correct)
      }
    } else {
      questionResults = Array(totalQuestions).fill(false)
    }

    return { 
      id: assignment.student_id || assignment.id, 
      full_name: fullName, 
      completed: isCompleted, 
      score, 
      correctAnswers, 
      timeSpent, 
      questionResults 
    }
  })
})
</script>

<style scoped>
.quizzes-report-container {
  font-family: 'Outfit', 'Inter', sans-serif;
}
</style>

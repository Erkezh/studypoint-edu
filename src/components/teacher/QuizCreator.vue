<template>
  <div class="quiz-creator">
    <div class="creator-header">
      <button @click="$emit('cancel')" class="back-link">
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
        Артқа
      </button>
      <div class="step-indicator">
        ҚАДАМ {{ currentStep }} / 2: {{ stepTitle }}
      </div>
    </div>

    <!-- STEP 1: ADD QUESTIONS -->
    <div v-if="currentStep === 1" class="step-container">
      <div class="quiz-controls-box">
        <input 
          v-model="quizName" 
          type="text" 
          placeholder="Квиз атауын енгізіңіз" 
          class="quiz-name-input"
        />
        <button 
          @click="nextStep" 
          :disabled="!quizName || selectedQuestions.length === 0" 
          class="next-btn"
        >
          Қарау және жариялау
        </button>
      </div>

      <div class="selection-layout">
        <div class="catalog-browser">
          <div class="browser-header">
            <div class="search-box">
              <svg class="w-4 h-4 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
              <input type="text" placeholder="Дағды аты немесе коды бойынша іздеу" />
            </div>
          </div>

          <div class="browser-content">
            <div class="grouping-selector">
              <div v-if="!selectedGrade" class="selector-menu">
                <p class="section-label">Санатты таңдаңыз</p>
                <div @click="openGrades" class="menu-item">
                  <span>Сыныптар</span>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                </div>
                <div class="menu-item disabled">Дағды жоспарлары (Жақында)</div>
                <div class="menu-item disabled">Ұсынылған дағдылар (Жақында)</div>
              </div>

              <!-- Grades List -->
              <div v-else-if="selectedGrade === -1" class="selector-menu">
                <div @click="selectedGrade = null" class="menu-item back">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
                  Сыныптар
                </div>
                <div v-for="grade in grades" :key="grade.number" @click="selectGrade(grade.number)" class="menu-item">
                  {{ grade.number }} сынып
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                </div>
              </div>

              <!-- Topics List -->
              <div v-else-if="selectedGrade !== null && selectedTopic === null" class="selector-menu">
                <div @click="selectedGrade = -1; topics = []" class="menu-item back">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
                  {{ selectedGrade }} сынып
                </div>
                <div v-if="loadingTopics" class="p-4 text-center text-gray-400">
                   Жүктелуде...
                </div>
                <div v-else-if="topics.length === 0" class="p-8 text-center text-gray-400">
                  Бұл сынып үшін тақырыптар табылмады
                </div>
                <div v-for="topic in topics" :key="topic.id" @click="selectTopic(topic)" class="menu-item">
                  {{ topic.title }}
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                </div>
              </div>

              <!-- Questions List -->
              <div v-else class="question-list">
                <div @click="selectedTopic = null" class="menu-item back">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
                  {{ selectedTopic.title }}
                </div>
                <div v-if="loadingQuestions" class="p-4 text-center">Жүктелуде...</div>
                <div v-for="q in questions" :key="q.id" class="question-item">
                  <label class="q-checkbox">
                    <input type="checkbox" :checked="isQuestionSelected(q.id)" @change="toggleQuestion(q)" />
                    <span class="checkmark"></span>
                  </label>
                  <div class="q-content">
                    <div class="q-meta">Сұрақ {{ q.id }} • Деңгей {{ q.level }}</div>
                    <div class="q-prompt" v-html="q.prompt"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="selected-panel">
          <h3>Таңдалған сұрақтар ({{ selectedQuestions.length }})</h3>
          <div v-if="selectedQuestions.length === 0" class="empty-selection">
            Ешқандай сұрақ таңдалмаған
          </div>
          <div v-else class="selected-list">
            <div v-for="(q, idx) in selectedQuestions" :key="q.id" class="selected-item">
              <span class="idx">{{ idx + 1 }}.</span>
              <span class="txt" v-html="q.prompt"></span>
              <button @click="removeQuestion(q.id)" class="remove-btn">&times;</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- STEP 2: SETTINGS & PUBLISH -->
    <div v-else class="step-container">
      <div class="settings-layout">
        <div class="settings-card">
          <div class="form-group">
            <label>Сұрақтар реті</label>
            <select v-model="settings.question_order">
              <option value="FIXED">Барлық оқушылар үшін бірдей</option>
              <option value="RANDOMIZED">Кездейсоқ</option>
            </select>
          </div>

          <div class="form-group">
            <label>Квизді аяқтау</label>
            <select v-model="settings.end_type">
              <option value="MANUAL">Қолмен</option>
              <option value="SCHEDULED">Белгіленген уақытта</option>
            </select>
            <div v-if="settings.end_type === 'SCHEDULED'" class="date-picker-row mt-2">
              <input type="date" v-model="settings.end_date" />
              <input type="time" v-model="settings.end_time" />
            </div>
          </div>

          <div class="form-group">
            <label>Нәтижелерді көрсету</label>
            <select v-model="settings.result_visibility">
              <option value="ALWAYS">Ұпайлар мен дұрыс жауаптарды көрсету</option>
              <option value="SCORE_ONLY">Тек ұпайларды көрсету</option>
              <option value="HIDDEN">Нәтижелерді көрсетпеу</option>
            </select>
          </div>

          <div class="form-group mt-8">
            <button @click="showStudentSelector = true" class="select-students-btn">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
              Оқушыларды таңдау...
            </button>
            <p class="mt-2 text-sm text-gray-500">
              {{ assignedStudentsLabel }}
            </p>
          </div>

          <div class="publish-row mt-8">
            <button @click="publishQuiz" :disabled="loading" class="publish-btn">
              {{ loading ? 'Жариялануда...' : 'Квизді жариялау' }}
            </button>
          </div>
        </div>

        <div class="preview-panel">
          <h3>Квизді алдын ала қарау</h3>
          <div class="preview-scroll">
            <div v-for="(q, idx) in selectedQuestions" :key="q.id" class="preview-q">
              <div class="preview-q-header">Сұрақ {{ idx + 1 }}</div>
              <div class="preview-q-body" v-html="q.prompt"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Student Selection Modal -->
    <div v-if="showStudentSelector" class="modal-overlay" @click.self="showStudentSelector = false">
      <div class="modal-content">
        <h3>Оқушыларды таңдау</h3>
        <div class="student-list-container">
          <label class="student-option">
            <input type="checkbox" v-model="selectAllStudents" />
            <span>Барлық оқушылар</span>
          </label>
          <div class="student-divider"></div>
          <label v-for="student in students" :key="student.id" class="student-option">
            <input type="checkbox" :value="student.id" v-model="assignedStudentIds" />
            <span>{{ student.full_name }}</span>
          </label>
        </div>
        <div class="modal-actions">
          <button @click="showStudentSelector = false" class="done-btn">Дайын</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useCatalogStore } from '@/stores/catalog'
import { useTeacherStore } from '@/stores/teacher'
import { useQuizStore } from '@/stores/quiz'
import { teacherApi } from '@/api/teacher'
import { QuizQuestionOrder, QuizResultVisibility, QuizEndType } from '@/api/quiz'

const emit = defineEmits(['cancel', 'created'])

const props = defineProps({
  initialQuiz: {
    type: Object as () => any | null,
    default: null
  }
})

const catalogStore = useCatalogStore()
const teacherStore = useTeacherStore()
const quizStore = useQuizStore()

const currentStep = ref(1)
const quizName = ref('')
const selectedGrade = ref<number | null>(null)
const selectedTopic = ref<any | null>(null)
const topics = ref<any[]>([])
const questions = ref<any[]>([])
const selectedQuestions = ref<any[]>([])

const loadingTopics = ref(false)
const loadingQuestions = ref(false)
const loading = ref(false)

const showStudentSelector = ref(false)
const assignedStudentIds = ref<string[]>([])
const selectAllStudents = ref(false)

const settings = ref({
  question_order: QuizQuestionOrder.FIXED,
  result_visibility: QuizResultVisibility.ALWAYS,
  end_type: QuizEndType.MANUAL,
  end_date: '',
  end_time: ''
})

const stepTitle = computed(() => {
  return currentStep.value === 1 ? 'Сұрақтарды қосу' : 'Оқушыларды таңдау және жариялау'
})

const grades = computed(() => catalogStore.grades)
const students = computed(() => teacherStore.students)

const assignedStudentsLabel = computed(() => {
  if (selectAllStudents.value) return 'Барлық оқушылар таңдалды'
  if (assignedStudentIds.value.length === 0) return 'Ешқандай оқушы таңдалмаған'
  return `${assignedStudentIds.value.length} оқушы таңдалды`
})

watch(selectAllStudents, (val) => {
  if (val) {
    assignedStudentIds.value = students.value.map(s => s.id)
  } else if (assignedStudentIds.value.length === students.value.length) {
    assignedStudentIds.value = []
  }
})

const openGrades = async () => {
  if (grades.value.length === 0) await catalogStore.getGrades()
  selectedGrade.value = null
  selectedGrade.value = -1 // trigger list
}

const selectGrade = async (gradeNum: number) => {
  selectedGrade.value = gradeNum
  loadingTopics.value = true
  try {
    const res = await teacherApi.getGradeTopics(gradeNum)
    topics.value = res.data.data
  } finally {
    loadingTopics.value = false
  }
}

const selectTopic = async (topic: any) => {
  selectedTopic.value = topic
  loadingQuestions.value = true
  try {
    const res = await teacherApi.getTopicQuestions(topic.id)
    questions.value = res.data.data
  } finally {
    loadingQuestions.value = false
  }
}

const isQuestionSelected = (id: number) => {
  return selectedQuestions.value.some(q => q.id === id)
}

const toggleQuestion = (q: any) => {
  const idx = selectedQuestions.value.findIndex(sq => sq.id === q.id)
  if (idx > -1) {
    selectedQuestions.value.splice(idx, 1)
  } else {
    selectedQuestions.value.push(q)
  }
}

const removeQuestion = (id: number) => {
  const idx = selectedQuestions.value.findIndex(sq => sq.id === id)
  if (idx > -1) selectedQuestions.value.splice(idx, 1)
}

const nextStep = () => {
  currentStep.value = 2
}

const isEditing = computed(() => !!props.initialQuiz)

const publishQuiz = async () => {
  if (selectedQuestions.value.length === 0) {
    alert('Кем дегенде 1 сұрақ таңдаңыз')
    return
  }
  if (!quizName.value.trim()) {
    alert('Квиз атауын енгізіңіз')
    return
  }

  loading.value = true
  try {
    const payload = {
      name: quizName.value,
      question_order: settings.value.question_order as any,
      result_visibility: settings.value.result_visibility as any,
      end_type: settings.value.end_type as any,
      questions: selectedQuestions.value.map((q, i) => ({
        question_id: q.id,
        position: i
      }))
    }

    let createdQuiz;
    if (isEditing.value) {
      createdQuiz = await quizStore.updateQuiz(props.initialQuiz.id, payload)
    } else {
      createdQuiz = await quizStore.createQuiz(payload)
    }

    // Assign to students
    if (selectAllStudents.value) {
        await quizStore.assignQuiz({
            quiz_id: createdQuiz.id,
        })
    } else {
        for (const studentId of assignedStudentIds.value) {
            await quizStore.assignQuiz({
                quiz_id: createdQuiz.id,
                student_id: studentId
            })
        }
    }

    emit('created')
  } catch (err: any) {
    alert(err.response?.data?.message || err.message || 'Error publishing quiz')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    catalogStore.getGrades(),
    teacherStore.fetchStudents()
  ])
  
  if (props.initialQuiz) {
    quizName.value = props.initialQuiz.name
    settings.value.question_order = props.initialQuiz.question_order
    settings.value.result_visibility = props.initialQuiz.result_visibility
    settings.value.end_type = props.initialQuiz.end_type
    
    // Map initial questions
    if (props.initialQuiz.questions) {
      selectedQuestions.value = props.initialQuiz.questions.map((q: any) => ({
        id: q.question_id,
        prompt: q.question ? q.question.prompt : 'Сұрақ мәтіні жүктелмеді'
      }))
    }
  }
})
</script>

<style scoped>
.quiz-creator {
  background: white;
  min-height: 500px;
  display: flex;
  flex-direction: column;
}

.creator-header {
  padding: 16px 24px;
  border-bottom: 1px solid #eef2f5;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.back-link {
  display: flex;
  align-items: center;
  color: #00bcd4;
  font-weight: 500;
  cursor: pointer;
  background: none;
  border: none;
}

.step-indicator {
  font-size: 14px;
  font-weight: 700;
  color: #72849a;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.step-container {
  flex: 1;
  padding: 24px;
  background: #f8fbff;
}

.quiz-controls-box {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.quiz-name-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #d1d8e0;
  border-radius: 8px;
  font-size: 18px;
  outline: none;
}

.quiz-name-input:focus {
  border-color: #00bcd4;
  box-shadow: 0 0 0 3px rgba(0, 188, 212, 0.1);
}

.next-btn {
  background: #00bcd4;
  color: white;
  padding: 0 24px;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

.next-btn:disabled {
  background: #e0e6ed;
  cursor: not-allowed;
}

.selection-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  height: 600px;
}

.catalog-browser {
  background: white;
  border-radius: 12px;
  border: 1px solid #eef2f5;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.browser-header {
  padding: 16px;
  border-bottom: 1px solid #eef2f5;
}

.search-box {
  display: flex;
  align-items: center;
  background: #f1f4f8;
  padding: 8px 12px;
  border-radius: 6px;
}

.search-box input {
  background: none;
  border: none;
  outline: none;
  flex: 1;
  font-size: 14px;
}

.browser-content {
  flex: 1;
  overflow-y: auto;
}

.selector-menu {
  display: flex;
  flex-direction: column;
}

.section-label {
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 700;
  color: #72849a;
  text-transform: uppercase;
}

.menu-item {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f8fbff;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.menu-item:hover {
  background: #e1f5fe;
}

.menu-item.back {
  background: #f1f8e9;
  color: #2e7d32;
  justify-content: flex-start;
}

.menu-item.disabled {
  color: #bdc3c7;
  cursor: not-allowed;
}

.question-list {
  display: flex;
  flex-direction: column;
}

.question-item {
  padding: 16px;
  display: flex;
  gap: 16px;
  border-bottom: 1px solid #f8fbff;
}

.q-checkbox {
  position: relative;
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.q-checkbox input {
  opacity: 0;
  position: absolute;
}

.checkmark {
  position: absolute;
  top: 0;
  left: 0;
  height: 20px;
  width: 20px;
  background-color: #eee;
  border-radius: 4px;
}

.q-checkbox:hover input ~ .checkmark {
  background-color: #ccc;
}

.q-checkbox input:checked ~ .checkmark {
  background-color: #00bcd4;
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
  left: 7px;
  top: 3px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.q-checkbox input:checked ~ .checkmark:after {
  display: block;
}

.q-content {
  flex: 1;
}

.q-meta {
  font-size: 11px;
  color: #7f8c8d;
  margin-bottom: 4px;
}

.q-prompt {
  font-size: 14px;
  color: #2c3e50;
}

.selected-panel {
  background: white;
  border-radius: 12px;
  border: 1px solid #eef2f5;
  padding: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.selected-panel h3 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 12px;
}

.empty-selection {
  color: #95a5a6;
  text-align: center;
  padding: 40px 0;
}

.selected-list {
  flex: 1;
  overflow-y: auto;
}

.selected-item {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: #f8fbff;
  border-radius: 6px;
  margin-bottom: 8px;
  font-size: 13px;
  align-items: flex-start;
}

.selected-item .idx {
  font-weight: 700;
  color: #00bcd4;
}

.selected-item .txt {
  flex: 1;
}

.remove-btn {
  background: none;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  font-size: 18px;
}

/* STEP 2 STYLES */
.settings-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.settings-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #eef2f5;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #34495e;
  margin-bottom: 8px;
}

.form-group select, .form-group input[type="text"], .form-group input[type="date"], .form-group input[type="time"] {
  width: 100%;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  outline: none;
}

.date-picker-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.select-students-btn {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid #00bcd4;
  background: white;
  color: #00bcd4;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.publish-btn {
  width: 100%;
  padding: 16px;
  background: #00bcd4;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

.preview-panel {
  background: #f1f4f8;
  border-radius: 12px;
  padding: 24px;
  height: 600px;
  display: flex;
  flex-direction: column;
}

.preview-scroll {
  flex: 1;
  overflow-y: auto;
}

.preview-q {
  background: white;
  border-radius: 8px;
  margin-bottom: 16px;
  padding: 16px;
}

.preview-q-header {
  font-size: 12px;
  color: #95a5a6;
  margin-bottom: 8px;
}

/* MODAL */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  padding: 24px;
}

.student-list-container {
  max-height: 400px;
  overflow-y: auto;
  margin-top: 16px;
}

.student-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  cursor: pointer;
}

.student-divider {
  height: 1px;
  background: #eee;
  margin: 4px 0;
}

.modal-actions {
  margin-top: 24px;
  text-align: right;
}

.done-btn {
  background: #00bcd4;
  color: white;
  padding: 8px 24px;
  border-radius: 6px;
  border: none;
  font-weight: 600;
  cursor: pointer;
}
</style>

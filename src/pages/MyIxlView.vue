<template>
  <div class="my-ixl-page" :class="{ 'quizzes-bg': activeMainTab === 'quizzes' }">
    <Header />

    <!-- Sub-tab navigation bar -->
    <div class="subtab-bar">
      <div class="subtab-container">
        <button
          class="subtab-btn"
          :class="{ active: activeMainTab === 'dashboard' }"
          @click="activeMainTab = 'dashboard'"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          Басқару тақтасы
        </button>
        <button
          class="subtab-btn"
          :class="{ active: activeMainTab === 'quizzes' }"
          @click="activeMainTab = 'quizzes'"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          Квиздер
        </button>
      </div>
    </div>

    <!-- ==================== DASHBOARD TAB ==================== -->
    <div v-if="activeMainTab === 'dashboard'" class="dashboard-content">
      <!-- Wave background -->
      <div class="wave-bg">
        <div class="wave-inner">
          <!-- Greeting -->
          <div class="greeting-section">
            <div class="avatar-circle">
              <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div class="greeting-text">
              Сәлем, <strong>{{ studentName }}</strong>! {{ greetingTime }}
            </div>
          </div>

          <!-- What to work on -->
          <div class="work-section">
            <div class="work-label">
              <div class="work-bar"></div>
              <span>Не істеу керек?</span>
            </div>

            <!-- Tabs -->
            <div class="work-tabs">
              <button
                class="work-tab"
                :class="{ active: activeWorkTab === 'teacher' }"
                @click="activeWorkTab = 'teacher'"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
                Мұғалімнен
              </button>
              <button
                class="work-tab"
                :class="{ active: activeWorkTab === 'recent' }"
                @click="activeWorkTab = 'recent'"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Соңғы дағдылар
              </button>
            </div>

            <!-- FROM YOUR TEACHER tab -->
            <div v-if="activeWorkTab === 'teacher'" class="tab-content">
              <div v-if="loadingAssigned" class="loading-state">
                <div class="spinner"></div>
                <span>Жүктелуде...</span>
              </div>

              <div v-else-if="assignedQuizzes.length === 0" class="empty-state">
                <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
                <p class="empty-title">Мұғалім тапсырма бермеген</p>
                <p class="empty-sub">Мұғаліміңіз тапсырма бергенде осында көрінеді</p>
              </div>

              <div v-else class="quiz-list">
                <div
                  v-for="quiz in assignedQuizzes"
                  :key="quiz.id"
                  class="quiz-card"
                >
                  <div class="quiz-card-left">
                    <svg class="star-icon" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                    </svg>
                    <div>
                      <div class="quiz-name">
                        Квиз: {{ quiz.name }}
                        <span v-if="isQuizCompleted(quiz.id)" class="quiz-status-badge completed">Аяқталды</span>
                        <span v-else class="quiz-status-badge not-started">Басталмаған</span>
                      </div>
                      <div class="quiz-meta">
                        Жасалды: {{ formatDate(quiz.created_at) }} ·
                        {{ quiz.questions.length }} сұрақ
                      </div>
                    </div>
                  </div>
                  <div class="quiz-card-right">
                    <button 
                      class="start-quiz-btn" 
                      :class="{'completed-btn': isQuizCompleted(quiz.id)}"
                      @click="startQuiz(quiz.id)"
                    >
                      {{ isQuizCompleted(quiz.id) ? 'Нәтижелерді көру' : 'Бастау' }} →
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- RECENT SKILLS tab -->
            <div v-if="activeWorkTab === 'recent'" class="tab-content">
              <div v-if="recentSessions.length === 0" class="empty-state">
                <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="empty-title">IXL-де жаттығуды бастауға дайынсыз ба?</p>
                <p class="empty-sub">Соңғы жаттығулар осында көрсетіледі</p>
                <router-link to="/" class="start-btn">Бастау →</router-link>
              </div>

              <div v-else class="recent-list">
                <div
                  v-for="session in recentSessions"
                  :key="session.id"
                  class="recent-card"
                >
                  <div class="recent-icon">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="w-5 h-5 text-teal-600">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2M9 12l2 2 4-4" />
                    </svg>
                  </div>
                  <div class="recent-info">
                    <div class="recent-name">{{ session.skillName }}</div>
                    <div class="recent-meta">
                      {{ session.correct }}/{{ session.total }} дұрыс ·
                      {{ formatDate(session.date) }}
                    </div>
                  </div>
                  <div class="recent-score" :class="getScoreClass(session.correct, session.total)">
                    {{ Math.round((session.correct / session.total) * 100) }}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== QUIZZES TAB ==================== -->
    <div v-if="activeMainTab === 'quizzes'" class="quizzes-content">
      <div class="quizzes-header">
        <h1 class="quizzes-title">Квиздер</h1>
        <p class="quizzes-desc">
          Мұғаліміңіз сізге арнайы берген квиздер. Осы бетте барлық белсенді квиздерді тапсыруға,
          өткен нәтижелерді көруге болады.
        </p>
      </div>

      <!-- Active Quizzes -->
      <div class="quizzes-section">
        <h2 class="section-title">Белсенді квиздер</h2>

        <div v-if="loadingAssigned" class="loading-state">
          <div class="spinner"></div>
          <span>Жүктелуде...</span>
        </div>

        <div v-else-if="activeQuizzes.length === 0" class="quizzes-empty">
          <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p>Белсенді квиз жоқ</p>
        </div>

        <div v-else class="active-quizzes-grid">
          <div
            v-for="quiz in activeQuizzes"
            :key="quiz.id"
            class="active-quiz-card"
          >
            <div class="aq-name">{{ quiz.name }}</div>
            <div class="aq-meta">
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Берілді: {{ formatDateFull(quiz.created_at) }}
            </div>
            <div class="aq-questions">
              {{ quiz.questions.length }} сұрақ
            </div>
            <button class="aq-start-btn" @click="startQuiz(quiz.id)">Бастау</button>
          </div>
        </div>
      </div>

      <!-- Past Quizzes -->
      <div class="quizzes-section">
        <h2 class="section-title">Өткен квиздер</h2>

        <div v-if="completedQuizzes.length === 0" class="quizzes-empty">
          <p>Аяқталған квиз жоқ</p>
        </div>

        <div v-else class="past-quizzes-table-wrapper">
          <table class="past-quizzes-table">
            <thead>
              <tr>
                <th>Атауы</th>
                <th>Күндері</th>
                <th>Нәтиже</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="quiz in completedQuizzes" :key="quiz.id">
                <td>{{ quiz.name }}</td>
                <td>{{ formatDateFull(getQuizCompletedDate(quiz.id) || quiz.created_at) }}</td>
                <td>100% (Аяқталған)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { quizApi, type QuizResponse } from '@/api/quiz'
import Header from '@/components/layout/Header.vue'

defineOptions({ name: 'MyIxlView' })

const authStore = useAuthStore()
const router = useRouter()

// Tabs
const activeMainTab = ref<'dashboard' | 'quizzes'>('dashboard')
const activeWorkTab = ref<'teacher' | 'recent'>('teacher')

// Data
const assignedQuizzes = ref<QuizResponse[]>([])
const loadingAssigned = ref(false)

// Student name
const studentName = computed(() => {
  const name = authStore.user?.full_name || 'Оқушы'
  return name.split(' ')[0]
})

// Greeting based on time
const greetingTime = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Қайырлы таң!'
  if (hour < 17) return 'Қайырлы күн!'
  return 'Қайырлы кеш!'
})

// Recent sessions from localStorage (practice sessions)
interface RecentSession {
  id: string
  skillName: string
  correct: number
  total: number
  date: string
}

const recentSessions = ref<RecentSession[]>([])

const isQuizCompleted = (quizId: string) => {
  try {
    return !!localStorage.getItem(`quiz_result_${quizId}`)
  } catch {
    return false
  }
}

const getQuizCompletedDate = (quizId: string) => {
  try {
    const data = localStorage.getItem(`quiz_result_${quizId}`)
    if (data) {
      const parsed = JSON.parse(data)
      return parsed.completedAt
    }
  } catch {}
  return null
}

const activeQuizzes = computed(() => {
  return assignedQuizzes.value.filter(q => !isQuizCompleted(q.id))
})

const completedQuizzes = computed(() => {
  return assignedQuizzes.value.filter(q => isQuizCompleted(q.id))
})

const loadRecentSessions = () => {
  try {
    const keys = Object.keys(localStorage).filter(k => k.startsWith('practice_result_'))
    const sessions: RecentSession[] = []
    for (const key of keys) {
      const raw = localStorage.getItem(key)
      if (!raw) continue
      try {
        const data = JSON.parse(raw)
        if (data && data.skillName && typeof data.correct === 'number') {
          sessions.push(data)
        }
      } catch {}
    }
    // Sort by date descending
    sessions.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    recentSessions.value = sessions.slice(0, 10)
  } catch {
    recentSessions.value = []
  }
}

const fetchAssignedQuizzes = async () => {
  loadingAssigned.value = true
  try {
    const resp = await quizApi.listStudentAssignedQuizzes()
    assignedQuizzes.value = resp.data.data || []
  } catch (err) {
    console.error('Failed to fetch quizzes:', err)
    assignedQuizzes.value = []
  } finally {
    loadingAssigned.value = false
  }
}

const goToQuizzes = () => {
  activeMainTab.value = 'quizzes'
}

const startQuiz = (quizId: string) => {
  router.push(`/my-ixl/quiz/${quizId}`)
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const months = ['қаң', 'ақп', 'нау', 'сәу', 'мам', 'мау', 'шіл', 'там', 'қыр', 'қаз', 'қар', 'жел']
  return `${d.getDate()} ${months[d.getMonth()]}`
}

const formatDateFull = (dateStr: string) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const months = ['қаңтар', 'ақпан', 'наурыз', 'сәуір', 'мамыр', 'маусым', 'шілде', 'тамыз', 'қыркүйек', 'қазан', 'қараша', 'желтоқсан']
  return `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`
}

const getScoreClass = (correct: number, total: number): string => {
  const pct = total > 0 ? (correct / total) * 100 : 0
  if (pct >= 80) return 'score-high'
  if (pct >= 50) return 'score-mid'
  return 'score-low'
}

onMounted(async () => {
  await fetchAssignedQuizzes()
  loadRecentSessions()
})
</script>

<style scoped>
/* ===== PAGE BASE ===== */
.my-ixl-page {
  min-height: 100vh;
  background: #f0f4f8;
  font-family: 'Inter', system-ui, sans-serif;
}

.quizzes-bg {
  background: #f0f4f8;
}

/* ===== SUB-TAB BAR ===== */
.subtab-bar {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 40;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.subtab-container {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  gap: 0;
}

.subtab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 28px;
  font-size: 15px;
  font-weight: 500;
  color: #6b7280;
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
}

.subtab-btn:hover {
  color: #374151;
  background: #f9fafb;
}

.subtab-btn.active {
  color: #0ea5e9;
  border-bottom-color: #0ea5e9;
}

/* ===== DASHBOARD CONTENT ===== */
.dashboard-content {
  min-height: calc(100vh - 120px);
}

.wave-bg {
  min-height: calc(100vh - 120px);
  position: relative;
  overflow: hidden;
}

.wave-inner {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px 60px;
}

/* ===== GREETING ===== */
.greeting-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.avatar-circle {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  flex-shrink: 0;
}

.greeting-text {
  font-size: 24px;
  font-weight: 500;
  color: #1f2937;
}

.greeting-text strong {
  font-weight: 700;
}

/* ===== WORK SECTION ===== */
.work-section {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
}

.work-label {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.work-bar {
  width: 4px;
  height: 24px;
  background: #38b000;
  border-radius: 4px;
}

/* ===== WORK TABS ===== */
.work-tabs {
  display: flex;
  gap: 0;
  padding: 12px 16px 0;
  border-bottom: 1px solid #f3f4f6;
  margin-top: 8px;
}

.work-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: 8px 8px 0 0;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
}

.work-tab.active {
  background: #38b000;
  color: white;
}

.work-tab:not(.active):hover {
  background: #f3f4f6;
  color: #374151;
}

/* ===== TAB CONTENT ===== */
.tab-content {
  padding: 20px;
  min-height: 160px;
}

/* ===== QUIZ LIST (dashboard) ===== */
.quiz-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quiz-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #fafafa;
  transition: box-shadow 0.15s;
}

.quiz-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  background: white;
}

.quiz-card-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.star-icon {
  width: 18px;
  height: 18px;
  color: #f59e0b;
  flex-shrink: 0;
  margin-top: 2px;
}

.quiz-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.quiz-meta {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}

.quiz-status-badge {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 999px;
}

.quiz-status-badge.not-started {
  background: #fef3c7;
  color: #92400e;
}

.quiz-status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.quiz-card-right {}

.start-quiz-btn {
  padding: 7px 16px;
  background: #38b000;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.start-quiz-btn:hover {
  background: #2d8a00;
  transform: translateY(-1px);
}

.start-quiz-btn.completed-btn {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.start-quiz-btn.completed-btn:hover {
  background: #e5e7eb;
}

/* ===== RECENT SKILLS ===== */
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recent-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: white;
  transition: box-shadow 0.15s;
}

.recent-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}

.recent-icon {
  width: 36px;
  height: 36px;
  background: #ecfdf5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.recent-info {
  flex: 1;
  min-width: 0;
}

.recent-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  truncate: 1;
}

.recent-meta {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}

.recent-score {
  font-size: 14px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 8px;
  flex-shrink: 0;
}

.score-high { background: #d1fae5; color: #065f46; }
.score-mid  { background: #fef3c7; color: #92400e; }
.score-low  { background: #fee2e2; color: #991b1b; }

/* ===== EMPTY STATE ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  text-align: center;
  gap: 6px;
}

.empty-icon {
  width: 48px;
  height: 48px;
  color: #d1d5db;
  margin-bottom: 8px;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.empty-sub {
  font-size: 13px;
  color: #9ca3af;
}

.start-btn {
  margin-top: 12px;
  padding: 10px 24px;
  background: #38b000;
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  display: inline-block;
  transition: background 0.15s, transform 0.1s;
}

.start-btn:hover {
  background: #2d8a00;
  transform: translateY(-1px);
}

/* ===== LOADING ===== */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: #6b7280;
  font-size: 14px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top-color: #38b000;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===== QUIZZES TAB ===== */
.quizzes-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px 60px;
}

.quizzes-header {
  margin-bottom: 32px;
}

.quizzes-title {
  font-size: 32px;
  font-weight: 700;
  color: #0ea5e9;
  margin-bottom: 8px;
}

.quizzes-desc {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
  max-width: 640px;
}

.quizzes-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.quizzes-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px;
  color: #9ca3af;
  font-size: 14px;
  text-align: center;
}

.active-quizzes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.active-quiz-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 16px;
  background: #fafafa;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.aq-name {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
}

.aq-meta, .aq-due {
  font-size: 13px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 4px;
}

.aq-questions {
  font-size: 12px;
  color: #9ca3af;
}

.aq-start-btn {
  margin-top: 8px;
  padding: 10px;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
}

.aq-start-btn:hover {
  background: #0284c7;
  transform: translateY(-1px);
}

/* ===== PAST QUIZZES TABLE ===== */
.past-quizzes-table-wrapper {
  overflow-x: auto;
}

.past-quizzes-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.past-quizzes-table th {
  text-align: left;
  padding: 10px 16px;
  color: #0ea5e9;
  font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
}

.past-quizzes-table td {
  padding: 12px 16px;
  color: #374151;
  border-bottom: 1px solid #f3f4f6;
}

.past-quizzes-table tr:last-child td {
  border-bottom: none;
}

.past-quizzes-table tr:hover td {
  background: #f9fafb;
}

@media (max-width: 640px) {
  .greeting-text { font-size: 18px; }
  .avatar-circle { width: 48px; height: 48px; }
  .work-tab { padding: 8px 12px; font-size: 13px; }
  .subtab-btn { padding: 12px 16px; font-size: 13px; }
}
</style>

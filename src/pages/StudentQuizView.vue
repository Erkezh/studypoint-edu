<template>
  <div class="min-h-screen bg-gradient-to-b from-cyan-50 to-cyan-100 flex flex-col">
    <Header />

    <!-- Breadcrumb -->
    <div class="bg-gray-100 border-b border-gray-200 py-2 px-4 shrink-0 overflow-x-auto whitespace-nowrap scrollbar-hide">
      <div class="container mx-auto">
        <nav class="flex items-center text-xs sm:text-sm text-gray-600">
          <router-link to="/my-cabinet" class="hover:text-green-600 shrink-0">{{ isChildWithParent ? 'Менің кабинетім' : 'Менің IXL' }}</router-link>
          <span class="mx-2 text-gray-400 shrink-0">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </span>
          <span class="font-medium text-gray-900 truncate">{{ currentQuiz?.name || 'Викторина' }}</span>
        </nav>
      </div>
    </div>

    <main class="container mx-auto px-4 py-4 sm:py-6 flex-1 flex flex-col">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
        <p class="mt-4 text-gray-600">Викторина жүктелуде...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 p-6 rounded-xl text-center max-w-2xl mx-auto mt-8">
        <p class="text-lg font-medium">{{ error }}</p>
        <button @click="$router.push('/my-cabinet')" class="mt-4 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
          Артқа қайту
        </button>
      </div>

      <!-- Main content active state -->
      <div v-else-if="currentQuiz && !isFinished" class="flex flex-col w-full max-w-4xl mx-auto flex-1">
        
        <!-- Question Area -->
        <div class="w-full flex flex-col flex-1">
          <div class="bg-white rounded-xl shadow-lg p-5 sm:p-8 relative flex-1 flex flex-col">
            
            <!-- Question Navigation at the top -->
            <div v-if="sortedQuestions.length > 0" class="mb-8 border-b border-gray-100 pb-5">
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <span class="text-xs font-bold text-gray-400 uppercase tracking-wider">Сұрақтар</span>
                <span class="text-xs font-semibold text-gray-500">Жауап берілді: <span class="text-green-600 font-bold">{{ answeredCount }}</span> / {{ sortedQuestions.length }}</span>
              </div>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="(q, idx) in sortedQuestions"
                  :key="q.id"
                  @click="jumpToQuestion(idx)"
                  class="relative min-w-[40px] h-10 px-2 rounded-xl flex items-center justify-center font-bold text-sm transition-all border-2 duration-200 cursor-pointer"
                  :class="[
                    currentIndex === idx
                      ? 'bg-cyan-600 border-cyan-600 text-white shadow-md shadow-cyan-600/20'
                      : hasAnswered(q.id)
                        ? 'bg-emerald-50 border-emerald-500 text-emerald-700 hover:bg-emerald-100 hover:border-emerald-600'
                        : 'bg-white border-gray-200 text-gray-600 hover:border-cyan-500 hover:text-cyan-600 hover:bg-cyan-50/30'
                  ]"
                >
                  <span>{{ idx + 1 }}</span>
                  <!-- Small Checkmark or Dot for answered state when not active -->
                  <span
                    v-if="hasAnswered(q.id) && currentIndex !== idx"
                    class="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full border-2 border-white flex items-center justify-center"
                  >
                    <svg class="w-1.5 h-1.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                    </svg>
                  </span>
                </button>
              </div>
            </div>
            
            <div v-if="currentQuestion" class="flex-1 flex flex-col justify-center">
              <div>
                <!-- Question prompt (hidden for plugins since iframe shows it) -->
                <p v-if="!isCurrentQuestionPlugin" class="text-lg sm:text-2xl text-gray-800 mb-8 sm:mb-10 leading-relaxed font-medium"
                  v-html="formatPrompt(currentQuestion.question?.prompt || '')">
                </p>

                <div class="w-full max-w-2xl">
                  <!-- MCQ -->
                  <div v-if="currentQuestion.question?.type === 'MCQ'" class="space-y-4">
                    <button
                      v-for="(option, index) in getOptions(currentQuestion.question?.data)"
                      :key="index"
                      @click="submitAnswer(option)"
                      class="w-full text-left p-4 sm:p-5 border-2 rounded-xl text-base sm:text-lg transition-all"
                      :class="[
                        isOptionSelected(option)
                          ? 'border-cyan-500 bg-[#e3f2fd]/40 font-semibold text-cyan-700'
                          : 'border-gray-200 hover:border-green-400 hover:bg-green-50 focus:border-green-500 focus:bg-green-50 text-gray-700'
                      ]"
                    >
                      <span v-html="formatPrompt(typeof option === 'object' && option !== null ? ((option as Record<string, unknown>).label || (option as Record<string, unknown>).text || (option as Record<string, unknown>).value || String(option)) as string : String(option))"></span>
                    </button>
                  </div>

                  <!-- NUMERIC -->
                  <div v-else-if="currentQuestion.question?.type === 'NUMERIC'" class="space-y-6">
                    <div class="flex items-center gap-3">
                      <input v-model="textAnswer" type="number" step="any" placeholder="Жауап"
                        class="w-48 sm:w-64 p-4 border-2 border-gray-300 rounded-xl focus:border-green-500 focus:outline-none text-lg sm:text-xl"
                        @keyup.enter="submitAnswer(textAnswer)" />
                      <span v-if="currentQuestion.question?.data?.unit" class="text-gray-600 text-lg">{{ currentQuestion.question.data.unit }}</span>
                    </div>
                    <button @click="submitAnswer(textAnswer)"
                      :disabled="!textAnswer"
                      class="px-8 sm:px-12 py-3 sm:py-4 bg-green-500 hover:bg-green-600 text-white font-bold text-lg rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md hover:shadow-lg">
                      Жіберу
                    </button>
                  </div>

                  <!-- TEXT -->
                  <div v-else-if="currentQuestion.question?.type === 'TEXT'" class="space-y-6">
                    <input v-model="textAnswer" type="text" placeholder="Жауапты енгізіңіз"
                      class="w-full p-4 border-2 border-gray-300 rounded-xl focus:border-green-500 focus:outline-none text-lg sm:text-xl"
                      @keyup.enter="submitAnswer(textAnswer)" />
                    <button @click="submitAnswer(textAnswer)"
                      :disabled="!textAnswer"
                      class="px-8 sm:px-12 py-3 sm:py-4 bg-green-500 hover:bg-green-600 text-white font-bold text-lg rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md hover:shadow-lg">
                      Жіберу
                    </button>
                  </div>

                  <!-- PLUGIN / INTERACTIVE -->
                  <div v-else-if="isCurrentQuestionPlugin" class="space-y-4">
                    <iframe
                      v-if="pluginIframeSrc"
                      ref="pluginIframeRef"
                      :src="pluginIframeSrc"
                      :style="{ width: '100%', height: pluginHeight + 'px', border: 'none', borderRadius: '12px' }"
                      sandbox="allow-scripts"
                      scrolling="no"
                      class="rounded-xl"
                    ></iframe>
                    <div v-else class="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-yellow-700 text-sm">
                      Плагин жүктелуде...
                    </div>

                    <!-- If already answered during active quiz, show a button to change it -->
                    <button
                      v-if="isCurrentQuestionAnswered && !isFinished"
                      @click="clearCurrentAnswer"
                      class="mt-5 flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-200 text-gray-600 font-semibold rounded-xl hover:border-orange-400 hover:text-orange-600 hover:bg-orange-50 transition-all text-sm"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      Жауапты өзгерту
                    </button>
                  </div>

                  <!-- Other types (fallback) -->
                  <div v-else class="space-y-6">
                    <p class="text-red-500 font-medium mb-4 flex items-center gap-2">
                       Бұл сұрақ түрі интерфейсте толық қолдау таппаған. Жауабыңызды төменге енгізіңіз.
                    </p>
                    <input v-model="textAnswer" type="text" placeholder="Мәтіндік жауап енгізіңіз"
                      class="w-full p-4 border-2 border-gray-300 rounded-xl focus:border-green-500 focus:outline-none text-lg sm:text-xl"
                      @keyup.enter="submitAnswer(textAnswer)" />
                    <button @click="submitAnswer(textAnswer)"
                      :disabled="!textAnswer"
                      class="px-8 sm:px-12 py-3 sm:py-4 bg-green-500 hover:bg-green-600 text-white font-bold text-lg rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md hover:shadow-lg">
                      Жіберу
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="text-center py-12">
              <p>Сұрақ қолжетімсіз.</p>
            </div>
            
            <div class="mt-12 pt-6 border-t border-gray-100 flex justify-between items-center text-sm text-gray-500">
              <span>Сұрақ: {{ currentIndex + 1 }} / {{ sortedQuestions.length }}</span>
              <div class="flex items-center gap-3">
                <button @click="$router.push('/my-cabinet')" class="hover:text-gray-800 transition-colors">Алдын ала шығу</button>
                <button 
                  v-if="answeredCount > 0"
                  @click="showConfirmSubmitModal = true"
                  class="px-5 py-2 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-xl transition-colors text-sm shadow-sm"
                >
                  Жауаптарды жіберу
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Finished state -->
      <div v-else-if="isFinished" class="w-full max-w-7xl mx-auto px-4 py-8 space-y-8 flex-1">
        
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-gray-200 pb-4">
          <div class="flex items-center gap-3">
            <h1 class="text-3xl font-extrabold text-gray-700 tracking-tight uppercase">Квиз нәтижелері</h1>
          </div>
          <button @click="triggerPrint()" class="text-gray-400 hover:text-gray-600 transition p-2 rounded-lg hover:bg-gray-100 hidden sm:inline-flex items-center gap-2 font-semibold text-sm">
            🖨️ Басып шығару
          </button>
        </div>

        <!-- Stats Cards Grid -->
        <div 
          class="grid gap-6 mb-6"
          :class="{
            'grid-cols-1 md:grid-cols-3': activeVisibilitySetting !== 'HIDDEN',
            'grid-cols-1 max-w-md mx-auto': activeVisibilitySetting === 'HIDDEN'
          }"
        >
          <!-- Correct Answers -->
          <div v-if="activeVisibilitySetting !== 'HIDDEN'" class="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm flex items-center gap-5">
            <div class="w-14 h-14 bg-green-50 rounded-full flex items-center justify-center text-green-500 shrink-0 text-xl font-bold">
              ✓
            </div>
            <div>
              <div class="text-2xl font-black text-gray-800 font-mono">
                {{ sortedQuestions.filter(q => q.id && isQuestionCorrect(q.id)).length }} <span class="text-gray-400 font-normal text-sm">/ {{ sortedQuestions.length }}</span>
              </div>
              <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-1">Дұрыс жауаптар</div>
            </div>
          </div>

          <!-- Score -->
          <div v-if="activeVisibilitySetting !== 'HIDDEN'" class="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm flex items-center gap-5">
            <div class="w-14 h-14 bg-blue-50 rounded-full flex items-center justify-center text-blue-500 shrink-0 text-xl font-bold">
              %
            </div>
            <div>
              <div class="text-2xl font-black text-blue-600 font-mono">
                {{ currentAssignment?.score ?? 100 }}%
              </div>
              <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-1">Квиз ұпайы</div>
            </div>
          </div>

          <!-- Time Spent -->
          <div class="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm flex items-center gap-5">
            <div class="w-14 h-14 bg-cyan-50 rounded-full flex items-center justify-center text-cyan-500 shrink-0 text-xl font-bold">
              ⏱
            </div>
            <div>
              <div class="text-2xl font-black text-gray-800 font-mono">
                {{ formatTimeCompact(currentAssignment?.time_spent_seconds || currentTime) }}
              </div>
              <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-1">Жұмсалған уақыт</div>
            </div>
          </div>
        </div>

        <!-- Info boxes for restricted visibility -->
        <div v-if="activeVisibilitySetting === 'SCORE_ONLY'" class="bg-blue-50 border border-blue-100 rounded-2xl p-6 text-blue-700 text-center font-semibold text-sm shadow-sm flex flex-col items-center gap-2 mb-6">
          <span class="text-xl">ℹ️</span>
          <span>Жұмысыңыз сәтті қабылданды! Сұрақтар мен қателерді талдау квиз толық аяқталғаннан кейін қолжетімді болады.</span>
        </div>

        <div v-if="activeVisibilitySetting === 'HIDDEN'" class="bg-blue-50 border border-blue-100 rounded-2xl p-6 text-blue-700 text-center font-semibold text-sm shadow-sm flex flex-col items-center gap-2 mb-6">
          <span class="text-xl">ℹ️</span>
          <span>Жұмысыңыз сәтті қабылданды! Квиз нәтижелері мен дұрыс жауаптарын мұғалім кейінірек жариялайды.</span>
        </div>

        <!-- Question Review Container -->
        <div v-if="activeVisibilitySetting === 'ALWAYS' && currentAssignment?.question_results" class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div class="bg-cyan-600 px-6 py-4 flex items-center justify-between">
            <h3 class="text-lg font-bold text-white">Сұрақтарды талдау</h3>
          </div>

          <div class="divide-y divide-gray-150">
            <div 
              v-for="(q, idx) in sortedQuestions" 
              :key="q.id"
              class="flex border-b border-gray-100 last:border-b-0 bg-white"
            >
              <!-- Left border indicator -->
              <div 
                class="w-1.5 shrink-0" 
                :class="q.id && isQuestionCorrect(q.id) ? 'bg-green-500' : 'bg-red-500'"
              ></div>

              <div class="flex-1 flex gap-4 p-6 text-left">
                <!-- Number + icon -->
                <div class="flex flex-col items-center gap-1 shrink-0 w-14">
                  <span class="text-[11px] text-gray-400 text-center font-bold">
                    {{ idx + 1 }} / {{ sortedQuestions.length }}
                  </span>
                  <span 
                    class="text-lg font-black"
                    :class="q.id && isQuestionCorrect(q.id) ? 'text-green-600' : 'text-red-500'"
                  >
                    {{ q.id && isQuestionCorrect(q.id) ? '✓' : '✗' }}
                  </span>
                </div>

                <!-- Content -->
                <div class="flex-1 min-w-0 space-y-6">
                  <!-- Header info -->
                  <div class="flex items-center justify-between border-b border-gray-100 pb-2">
                    <div>
                      <h4 class="text-sm font-bold text-gray-800">Сұрақ {{ idx + 1 }}</h4>
                      <p class="text-[10px] text-gray-400 font-bold mt-0.5">
                        Деңгей {{ q?.question?.level || 2 }}
                      </p>
                    </div>
                  </div>

                  <!-- Question Iframe/Prompt Preview -->
                  <div class="bg-gray-50 border border-gray-100 rounded-xl p-5">
                    <div class="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-2">Сұрақ:</div>
                    <SessionQuestionPreview 
                      :question="buildQuestionReview(q)"
                    />
                  </div>

                  <!-- Student and Correct Answers -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Student's submitted answer -->
                    <div class="space-y-2">
                      <div class="text-[11px] font-bold text-gray-400 uppercase tracking-wider">Сіздің жауабыңыз:</div>
                      
                      <!-- Plugin visual answer -->
                      <div v-if="isQuestionPluginType(q) && buildStudentReviewPreview(q, isQuestionCorrect(q.id))" class="rounded-xl border p-2 overflow-hidden bg-white shadow-sm" :class="q.id && isQuestionCorrect(q.id) ? 'border-green-200' : 'border-red-200'">
                        <SessionQuestionPreview :question="buildStudentReviewPreview(q, isQuestionCorrect(q.id))!" />
                      </div>

                      <!-- Textual fallback -->
                      <div 
                        v-else
                        class="border rounded-xl bg-white px-5 py-4 font-semibold text-lg shadow-sm"
                        :class="q.id && isQuestionCorrect(q.id) ? 'border-green-200 text-green-700 bg-green-50/20' : 'border-red-200 text-red-700 bg-red-50/20'"
                      >
                        {{ getStudentSubmittedAnswerText(q.id) }}
                      </div>
                    </div>

                    <!-- Correct answer (only shown if student's answer was incorrect) -->
                    <div v-if="q.id && !isQuestionCorrect(q.id)" class="space-y-2">
                      <div class="text-[11px] font-bold text-gray-400 uppercase tracking-wider">Дұрыс жауап:</div>

                      <!-- Plugin visual correct answer -->
                      <div v-if="isQuestionPluginType(q) && buildCorrectReviewPreview(q)" class="rounded-xl border border-green-200 p-2 overflow-hidden bg-white bg-green-50/10 shadow-sm">
                        <SessionQuestionPreview :question="buildCorrectReviewPreview(q)!" />
                      </div>

                      <!-- Textual fallback -->
                      <div 
                        v-else
                        class="border border-green-200 rounded-xl bg-white px-5 py-4 font-semibold text-lg shadow-sm text-green-700 bg-green-50/20"
                      >
                        {{ getCorrectAnswerText(q) }}
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-center pt-4">
          <button @click="$router.push('/my-cabinet')" class="px-8 py-3.5 bg-cyan-600 hover:bg-cyan-700 text-white font-bold rounded-xl transition-all shadow-md shadow-cyan-600/20 text-md cursor-pointer">
            Кабинетке қайту
          </button>
        </div>

      </div>
    </main>

    <!-- Confirmation Modal -->
    <Modal :is-open="showConfirmSubmitModal" title="Жұмысты аяқтау" :show-close="true" @close="showConfirmSubmitModal = false">
      <template #content>
        <div class="p-6 text-center">
          <div class="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">Квизді аяқтауды растайсыз ба?</h3>
          <p class="text-gray-500 mb-4">Жауаптарыңыз тексеруге жіберіледі. Осыдан кейін жауаптарды өзгерту мүмкін болмайды.</p>

          <!-- Review and change answers list -->
          <div class="mb-6 text-left max-h-[240px] overflow-y-auto border border-gray-200 rounded-xl p-3 bg-gray-50/50 space-y-2">
            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Жауаптарды шолу:</h4>
            <div 
              v-for="(q, idx) in sortedQuestions" 
              :key="q.id" 
              class="p-3 rounded-lg border bg-white flex justify-between items-center transition hover:border-blue-300"
            >
              <div class="min-w-0 flex-1 pr-3">
                <p class="text-xs font-bold text-gray-500">Сұрақ {{ idx + 1 }}</p>
                <p class="text-sm text-gray-800 font-medium truncate" v-html="formatPrompt(getQuestionPrompt(q))"></p>
                <p class="text-xs mt-1">
                  <span v-if="hasAnswered(q.id)" class="text-green-600 font-semibold">
                    Жауап берілді: {{ getStudentSubmittedAnswerText(q.id) }}
                  </span>
                  <span v-else class="text-red-500 font-semibold">Жауап берілмеді</span>
                </p>
              </div>
              <button 
                @click="jumpToQuestion(idx)" 
                class="px-3 py-1 text-xs bg-blue-50 text-blue-600 font-semibold rounded-lg hover:bg-blue-100 transition whitespace-nowrap"
              >
                Өзгерту
              </button>
            </div>
          </div>

          <div class="flex gap-4 justify-center">
            <button @click="showConfirmSubmitModal = false" class="px-6 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl transition-all">
              Кейінге қалдыру
            </button>
            <button @click="confirmSubmitQuiz" class="px-6 py-2.5 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-xl transition-all shadow-md shadow-green-500/20">
              Жіберу
            </button>
          </div>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, isRef } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Header from '@/components/layout/Header.vue'
import Modal from '@/components/ui/Modal.vue'
import SessionQuestionPreview from '@/components/analytics/SessionQuestionPreview.vue'
import { quizApi, type QuizResponse } from '@/api/quiz'
import router from '@/router'

const authStore = useAuthStore()
const isChildWithParent = computed(() => authStore.user?.role === 'STUDENT' && !!(authStore.user as Record<string, unknown>)?.parent_id)

const props = defineProps<{
  quizId: string
}>()

// UI State
const loading = ref(true)
const error = ref<string | null>(null)
const currentQuiz = ref<QuizResponse | null>(null)

// Quiz State
const currentIndex = ref(0)
const isFinished = ref(false)
const textAnswer = ref('')

// Timer
const currentTime = ref(0)
const isComponentMounted = ref(false)

// Timer interval handle (local variable, matching PracticeSession.vue)
let timerInterval: ReturnType<typeof setInterval> | null = null
let savedTime = 0  // Ground-truth timer value, only updated when student answers a question

// Plugin state
const pluginIframeRef = ref<HTMLIFrameElement | null>(null)
const pluginIframeSrc = ref('')
const pluginHeight = ref(500)

import type { QuizAssignmentResponse } from '@/api/quiz'

const shuffledQuestions = ref<QuizResponse['questions']>([])
const questionAnswers = ref<{ question_id: string; submitted_answer: unknown }[]>([])
const currentAssignment = ref<QuizAssignmentResponse | null>(null)

const sortedQuestions = computed(() => {
  return shuffledQuestions.value
})

const answeredCount = computed(() => {
  return sortedQuestions.value.filter(q => hasAnswered(q.id)).length
})

import { getQuizEffectiveVisibility } from '@/utils/quizVisibility'

const activeVisibilitySetting = computed(() => {
  if (!currentQuiz.value) return 'HIDDEN'
  return getQuizEffectiveVisibility(currentQuiz.value, authStore.user?.id)
})

type QuizQuestion = QuizResponse['questions'][number]

const buildQuestionReview = (q: QuizQuestion) => {
  return {
    prompt: q.question?.prompt || '',
    type: q.question?.type || '',
    data: (q.question?.data as Record<string, unknown> | null) || null,
    userAnswer: null,
    isCorrect: false,
    correctAnswer: getCorrectAnswerText(q),
    seed: q.seed || null
  }
}

const isQuestionPluginType = (q: QuizQuestion): boolean => {
  const qType = String(q.question?.type || '').toUpperCase()
  return qType === 'PLUGIN' || qType === 'INTERACTIVE'
}

const getStudentRawSubmission = (qId: string | number | undefined) => {
  if (qId === undefined) return null
  if (currentAssignment.value?.question_results) {
    const res = currentAssignment.value.question_results[String(qId)]
    if (res && typeof res === 'object') {
      const resObj = res as Record<string, unknown>
      return resObj.submitted_answer || null
    }
  }
  return null
}

const getCorrectAnswerPayload = (qId: string | number | undefined) => {
  if (qId === undefined) return null
  if (currentAssignment.value?.question_results) {
    const res = currentAssignment.value.question_results[String(qId)]
    if (res && typeof res === 'object') {
      const resObj = res as Record<string, unknown>
      return resObj.correct_answer || null
    }
  }
  const q = sortedQuestions.value.find(x => String(x.id) === String(qId))
  return q?.question?.correct_answer || null
}

const buildStudentReviewPreview = (q: QuizQuestion, isCorrect: boolean) => {
  const rawAnswer = getStudentRawSubmission(q.id)
  return {
    prompt: q.question?.prompt || '',
    type: q.question?.type || '',
    data: (q.question?.data as Record<string, unknown> | null) || null,
    userAnswer: rawAnswer,
    isCorrect,
    correctAnswer: q.question?.correct_answer || null,
    seed: q.seed || null
  }
}

const buildCorrectReviewPreview = (q: QuizQuestion) => {
  const rawCorrectAnswer = getCorrectAnswerPayload(q.id)
  const rawSubmitted = getStudentRawSubmission(q.id) as Record<string, unknown> | null
  const studentQData = rawSubmitted ? (rawSubmitted.questionData || rawSubmitted.visualData) : null
  const studentAnsData = rawSubmitted ? rawSubmitted.answerData : null

  const mockCorrectPayload = {
    isCorrect: true,
    userAnswer: rawCorrectAnswer,
    studentAnswer: rawCorrectAnswer,
    correctAnswer: rawCorrectAnswer,
    questionData: studentQData || q.question?.data || null,
    answerData: studentAnsData
  }

  return {
    prompt: q.question?.prompt || '',
    type: q.question?.type || '',
    data: (q.question?.data as Record<string, unknown> | null) || null,
    userAnswer: mockCorrectPayload,
    isCorrect: true,
    correctAnswer: rawCorrectAnswer,
    seed: q.seed || null
  }
}

const triggerPrint = () => {
  window.print()
}

const currentQuestion = computed(() => {
  if (!sortedQuestions.value.length || currentIndex.value >= sortedQuestions.value.length) return null
  return sortedQuestions.value[currentIndex.value]
})

// Plugin detection helpers
const isQuestionPlugin = (q: Record<string, unknown> | null | undefined): boolean => {
  if (!q) return false
  const type = q.type as string | undefined
  return type === 'PLUGIN' || type === 'INTERACTIVE'
}

const getRegularPluginSrc = (q: Record<string, unknown> | null | undefined): string => {
  if (!q || !q.data) return ''
  const data = q.data as Record<string, unknown>
  const id = data.plugin_id as string | undefined
  const ver = data.plugin_version as string | undefined
  const entry = data.entry as string | undefined
  if (!id || !ver || !entry) return ''
  return `/static/modules/${id}/${ver}/${entry}`
}

const isCurrentQuestionPlugin = computed(() => {
  if (!currentQuestion.value) return false
  return isQuestionPlugin(currentQuestion.value.question as Record<string, unknown> | undefined)
})

const isCurrentQuestionAnswered = computed(() => {
  if (!currentQuestion.value) return false
  return hasAnswered(currentQuestion.value.id)
})

const clearCurrentAnswer = () => {
  if (!currentQuestion.value) return
  const qId = String(currentQuestion.value.id)
  const idx = questionAnswers.value.findIndex(a => a.question_id === qId)
  if (idx !== -1) {
    questionAnswers.value.splice(idx, 1)
  }
  textAnswer.value = ''
  // For plugin questions: reload the iframe to reset the plugin state
  if (isCurrentQuestionPlugin.value) {
    loadCurrentPlugin()
  }
}

// Load plugin iframe when question changes
const loadCurrentPlugin = async () => {
  pluginIframeSrc.value = ''
  pluginHeight.value = 500
  if (!currentQuestion.value?.question) return
  const q = currentQuestion.value.question as Record<string, unknown>
  if (!isQuestionPlugin(q)) return

  const base = getRegularPluginSrc(q)
  if (!base) return
  
  const seed = currentQuestion.value.seed
  const level = (currentQuestion.value as Record<string, unknown>).level || (q as Record<string, unknown>).level || 1
  
  // Check if this question is already answered in the active session
  const qId = String(currentQuestion.value.id)
  const ansObj = questionAnswers.value.find(a => String(a.question_id) === qId)
  
  if (ansObj && ansObj.submitted_answer) {
    const ans = ansObj.submitted_answer as Record<string, unknown>
    const studentAnswer = typeof ans.userAnswer === 'object' ? JSON.stringify(ans.userAnswer) : String(ans.userAnswer || '')
    const questionData = ans.questionData ? JSON.stringify(ans.questionData) : ''
    const answerData = ans.answerData ? JSON.stringify(ans.answerData) : ''

    if (isFinished.value) {
      // Already answered and quiz finished: load in review mode!
      const correctAnswer = typeof ans.correctAnswer === 'object' ? JSON.stringify(ans.correctAnswer) : String(ans.correctAnswer || '')
      const isCorrect = String(ans.isCorrect || false)

      const params = new URLSearchParams({
        embed: '1',
        mode: 'review',
        seed: String(seed || ''),
        level: String(level || 1),
        studentAnswer,
        correctAnswer,
        isCorrect,
        questionData,
        answerData
      })
      pluginIframeSrc.value = `${base}?${params.toString()}`
    } else {
      // Still taking the quiz: load in quiz mode with studentAnswer to display it frozen
      const params = new URLSearchParams({
        embed: '1',
        mode: 'quiz',
        seed: String(seed || ''),
        level: String(level || 1),
        studentAnswer,
        questionData,
        answerData
      })
      pluginIframeSrc.value = `${base}?${params.toString()}`
    }
  } else {
    // Unanswered: load in quiz mode with seed and level
    const params = new URLSearchParams({
      embed: '1',
      mode: 'quiz',
      level: String(level || 1)
    })
    if (seed !== null && seed !== undefined) {
      params.set('seed', String(seed))
    }
    pluginIframeSrc.value = `${base}?${params.toString()}`
  }
}

// Listen for exercise-result messages from plugin iframes
const handlePluginMessage = (event: MessageEvent) => {
  try {
    const d = event.data
    if (!d || typeof d !== 'object') return

    // Handle iframe resize
    if (d.type === 'resize' || d.type === 'content-height') {
      const height = d.height ?? d.contentHeight ?? d.scrollHeight
      if (typeof height === 'number' && height > 0) {
        pluginHeight.value = Math.max(height, 400)
      }
      return
    }

    if (d.type !== 'exercise-result') return
    if (!isCurrentQuestionPlugin.value) return

    // The plugin submitted its result — move to the next question
    const isCorrect = d.isCorrect ?? d.correct ?? d.is_correct
    const userAnswer = d.userAnswer ?? d.user_answer ?? d.studentAnswer ?? d.answer ?? d.value
    const correctAnswer = d.correctAnswer ?? d.correct_answer ?? d.expectedAnswer ?? d.expected_answer
    const question = d.question ?? d.prompt ?? d.equation ?? d.problem ?? d.questionText ?? null
    const questionData = d.questionData ?? null
    const answerData = d.answerData ?? null

    submitAnswer({
      isCorrect,
      userAnswer,
      correctAnswer,
      question,
      questionData,
      answerData,
    })
  } catch (err) {
    console.error('Plugin message error:', err)
  }
}

// Watch question changes to reload plugin and prefill answers if previously submitted
watch(currentIndex, () => {
  if (isCurrentQuestionPlugin.value) {
    loadCurrentPlugin()
  }

  // Pre-fill textAnswer with previously submitted answer if it exists
  if (currentQuestion.value) {
    const qId = String(currentQuestion.value.id)
    const prevAnswer = questionAnswers.value.find(a => a.question_id === qId)
    if (prevAnswer) {
      if (typeof prevAnswer.submitted_answer === 'object' && prevAnswer.submitted_answer !== null) {
        const obj = prevAnswer.submitted_answer as Record<string, unknown>
        textAnswer.value = String(obj.userAnswer ?? obj.user_answer ?? obj.value ?? obj.text ?? '')
      } else {
        textAnswer.value = String(prevAnswer.submitted_answer ?? '')
      }
    } else {
      textAnswer.value = ''
    }
  } else {
    textAnswer.value = ''
  }
})



const formatPrompt = (text: string): string => {
  if (!text) return ''
  return text.replace(
    /(\d+)\/(\d+)/g,
    '<span class="inline-flex flex-col items-center mx-0.5 align-middle"><span class="border-b-2 border-current pb-0.5 px-0.5 leading-none">$1</span><span class="pt-0.5 px-0.5 leading-none">$2</span></span>'
  )
}

const getOptions = (data: unknown) => {
  if (!data) return []
  const d = data as Record<string, unknown>
  return d.choices || d.options || []
}

const isOptionSelected = (option: unknown) => {
  if (!currentQuestion.value) return false
  const qId = String(currentQuestion.value.id)
  const prevAnswer = questionAnswers.value.find(a => String(a.question_id) === qId)
  if (!prevAnswer) return false

  const prevAnswerText = formatSubmittedAnswerText(prevAnswer.submitted_answer)
  const optionText = typeof option === 'object' && option !== null
    ? String((option as Record<string, unknown>).label || (option as Record<string, unknown>).text || (option as Record<string, unknown>).value || '')
    : String(option)

  return prevAnswerText === optionText
}

const showConfirmSubmitModal = ref(false)
const pendingFinalAnswer = ref<unknown>('')

const submitAnswer = (answer: unknown) => {
  let finalAnswer = answer
  if (isRef(answer)) {
    finalAnswer = answer.value
  }

  if (currentQuestion.value) {
    const qId = String(currentQuestion.value.id)
    const idx = questionAnswers.value.findIndex(a => a.question_id === qId)
    if (idx !== -1) {
      questionAnswers.value[idx].submitted_answer = finalAnswer
    } else {
      questionAnswers.value.push({
        question_id: qId,
        submitted_answer: finalAnswer
      })
    }
    savedTime = currentTime.value
    saveProgress()
  }

  // Clear input AFTER saving finalAnswer
  textAnswer.value = ''

  // Immediately transition to next question if not the last one
  if (currentIndex.value < sortedQuestions.value.length - 1) {
    currentIndex.value++
  } else {
    // If all questions are answered, show the submit modal.
    const allAnswered = sortedQuestions.value.every(q => hasAnswered(q.id))
    if (allAnswered) {
      pendingFinalAnswer.value = finalAnswer
      showConfirmSubmitModal.value = true
    }
  }
}

const confirmSubmitQuiz = async () => {
  showConfirmSubmitModal.value = false

  const userId = authStore.user?.id || ''
  // Clear progress storage since quiz is finished
  try {
    localStorage.removeItem(`quiz_progress_${userId}_${props.quizId}`)
  } catch {}

  // Submit to API
  if (currentAssignment.value) {
    try {
      const resp = await quizApi.submitQuizAssignment(currentAssignment.value.id, {
        score: 100, // calculated securely on server
        time_spent_seconds: currentTime.value,
        question_results: questionAnswers.value
      })
      if (resp?.data?.data) {
        currentAssignment.value = resp.data.data
      }
    } catch (err) {
      console.error('Failed to submit quiz assignment to server:', err)
    }
  }

  currentIndex.value++ // bump to max
  isFinished.value = true
  stopTimer()
  
  try {
    const finalScore = currentAssignment.value?.score ?? 100
    localStorage.setItem(`quiz_result_${userId}_${props.quizId}`, JSON.stringify({
      completedAt: new Date().toISOString(),
      score: finalScore,
      finalAnswer: pendingFinalAnswer.value
    }))
  } catch { }

  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const saveProgress = () => {
  if (currentQuiz.value && !isFinished.value) {
    try {
      const userId = authStore.user?.id || ''
      localStorage.setItem(`quiz_progress_${userId}_${props.quizId}`, JSON.stringify({
        currentTime: currentTime.value,
        answers: questionAnswers.value
      }))
    } catch (err) {
      console.warn('Failed to save quiz progress to localStorage:', err)
    }
  }
}

// Progress is saved explicitly in submitAnswer() only — no reactive watcher.
// This avoids Vue's async watch flush writing ticked-up currentTime to localStorage.

const formatSubmittedAnswerText = (answer: unknown): string => {
  if (!answer) return '—'
  if (typeof answer === 'object' && answer !== null) {
    const obj = answer as Record<string, unknown>
    if ('userAnswer' in obj) {
      return String(obj.userAnswer ?? '—')
    }
    if ('user_answer' in obj) {
      return String(obj.user_answer ?? '—')
    }
    if ('choice' in obj) {
      return String(obj.choice ?? '—')
    }
    if ('value' in obj) {
      return String(obj.value ?? '—')
    }
    if ('text' in obj) {
      return String(obj.text ?? '—')
    }
    if ('correctAnswer' in obj) {
      return String(obj.correctAnswer ?? '—')
    }
    if ('correct_answer' in obj) {
      return String(obj.correct_answer ?? '—')
    }
    return (obj.value || obj.label || obj.text || JSON.stringify(answer)) as string
  }
  return String(answer)
}

const getStudentSubmittedAnswerText = (qId: string | number | undefined) => {
  if (qId === undefined) return '—'
  const ansObj = questionAnswers.value.find(a => String(a.question_id) === String(qId))
  if (ansObj) {
    return formatSubmittedAnswerText(ansObj.submitted_answer)
  }
  if (currentAssignment.value?.question_results) {
    const res = currentAssignment.value.question_results[String(qId)]
    if (res && typeof res === 'object') {
      const resObj = res as Record<string, unknown>
      if ('submitted_answer' in resObj) {
        return formatSubmittedAnswerText(resObj.submitted_answer)
      }
    }
  }
  return '—'
}

const isQuestionCorrect = (qId: string | number | undefined): boolean => {
  if (!qId || !currentAssignment.value?.question_results) return false
  const res = currentAssignment.value.question_results[String(qId)]
  if (res === true) return true
  if (res && typeof res === 'object') {
    const resObj = res as Record<string, unknown>
    return resObj.correct === true
  }
  return false
}

const getQuestionPrompt = (
  q: { id?: string | number; question?: { prompt?: string } }
): string => {
  const qId = q.id
  if (!qId) return q.question?.prompt || ''
  
  // 1. Check current answers in memory first (if taking the quiz)
  const ansObj = questionAnswers.value.find(a => String(a.question_id) === String(qId))
  if (ansObj && ansObj.submitted_answer && typeof ansObj.submitted_answer === 'object') {
    const sAns = ansObj.submitted_answer as Record<string, unknown>
    if (sAns.question) {
      return String(sAns.question)
    }
  }

  // 2. Fallback to backend-saved assignment results (if finished)
  if (currentAssignment.value?.question_results) {
    const res = currentAssignment.value.question_results[String(qId)]
    if (res && typeof res === 'object') {
      const resObj = res as Record<string, unknown>
      if (resObj.question) {
        return String(resObj.question)
      }
    }
  }
  return q.question?.prompt || ''
}

const hasAnswered = (qId: string | number | undefined): boolean => {
  if (qId === undefined) return false
  const ansObj = questionAnswers.value.find(a => String(a.question_id) === String(qId))
  return !!ansObj && ansObj.submitted_answer !== null && ansObj.submitted_answer !== undefined && ansObj.submitted_answer !== ''
}

const jumpToQuestion = (idx: number) => {
  showConfirmSubmitModal.value = false
  if (idx >= 0 && idx < sortedQuestions.value.length) {
    currentIndex.value = idx
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const getCorrectAnswerText = (
  q: { id?: string | number; question?: { type?: string; correct_answer?: Record<string, unknown> | null; data?: { choices?: unknown[]; options?: unknown[] } } }
): string => {
  const qId = q.id
  if (qId && currentAssignment.value?.question_results) {
    const res = currentAssignment.value.question_results[String(qId)]
    if (res && typeof res === 'object') {
      const resObj = res as Record<string, unknown>
      if (resObj.correct_answer) {
        return formatSubmittedAnswerText(resObj.correct_answer)
      }
    }
  }
  const question = q.question
  if (!question) return '—'
  const correct = question.correct_answer
  if (!correct) return '—'
  if (question.type === 'MCQ') {
    const choices = (question.data?.choices || question.data?.options || []) as Array<Record<string, unknown> | string | number>
    const correctChoiceId = String(correct.choice ?? '')
    const found = choices.find((c) => {
      if (c && typeof c === 'object') {
        return String(c.id ?? '') === correctChoiceId
      }
      return String(c) === correctChoiceId
    })
    if (found) {
      return typeof found === 'object' ? String(found.label || found.text || found.value || '') : String(found)
    }
    return correctChoiceId || '—'
  }
  if (question.type === 'NUMERIC') {
    return String(correct.value ?? '—')
  }
  if (question.type === 'TEXT') {
    return String(correct.text ?? '—')
  }
  return formatSubmittedAnswerText(correct)
}

// Timer Functions (matching PracticeSession.vue architecture)
const stopTimer = () => {
  if (timerInterval !== null) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

const startTimer = () => {
  stopTimer()
  if (!isComponentMounted.value || isFinished.value || loading.value) {
    return
  }
  // Always reset from the confirmed savedTime — this prevents creep
  currentTime.value = savedTime
  timerInterval = setInterval(() => {
    currentTime.value++
  }, 1000) as unknown as ReturnType<typeof setInterval>
}

// Timer Functions
const formatTimeCompact = (s: number) => {
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60).toString().padStart(2, '0')
  const sec = (s % 60).toString().padStart(2, '0')
  return h > 0 ? `${h}:${m}:${sec}` : `${m}:${sec}`
}

const fetchQuiz = async () => {
  loading.value = true
  error.value = null
  
  try {
    const listResp = await quizApi.listStudentAssignedQuizzes()
    if (!isComponentMounted.value) return
    const quizzes = listResp.data.data || []
    
    const foundQuiz = quizzes.find(q => q.id === props.quizId)
    if (foundQuiz) {
      currentQuiz.value = foundQuiz
      
      const assignment = foundQuiz.assignments?.find(a => a.student_id === authStore.user?.id)
      currentAssignment.value = assignment || null

      if (assignment?.completed_at) {
        isFinished.value = true
        currentIndex.value = foundQuiz.questions.length
        const questionsList = [...foundQuiz.questions]
        questionsList.sort((a, b) => a.position - b.position)
        shuffledQuestions.value = questionsList
      } else {
        if (assignment && !assignment.completed_at) {
          // Mark as started in backend asynchronously
          quizApi.startQuizAssignment(assignment.id).catch(err => {
            console.warn('Failed to mark quiz as started:', err)
          })
        }

        const userId = authStore.user?.id || ''
        const resultStr = localStorage.getItem(`quiz_result_${userId}_${props.quizId}`)
        if (resultStr) {
          isFinished.value = true
          currentIndex.value = foundQuiz.questions.length
          const questionsList = [...foundQuiz.questions]
          questionsList.sort((a, b) => a.position - b.position)
          shuffledQuestions.value = questionsList
        } else {
          // Restore progress from localStorage if it exists
          const progressStr = localStorage.getItem(`quiz_progress_${userId}_${props.quizId}`)
          if (progressStr) {
            try {
              const progress = JSON.parse(progressStr)
              if (progress && typeof progress === 'object') {
                savedTime = Number(progress.currentTime || 0)
                currentTime.value = savedTime
                questionAnswers.value = Array.isArray(progress.answers) ? progress.answers : []
              }
            } catch (err) {
              console.warn('Failed to parse quiz progress:', err)
            }
          }

          // Prepare question ordering
          const questionsList = [...foundQuiz.questions]
          if (foundQuiz.question_order === 'RANDOMIZED') {
            for (let i = questionsList.length - 1; i > 0; i--) {
              const j = Math.floor(Math.random() * (i + 1));
              [questionsList[i], questionsList[j]] = [questionsList[j], questionsList[i]];
            }
          } else {
            questionsList.sort((a, b) => a.position - b.position)
          }
          shuffledQuestions.value = questionsList

          // Restore current index to first unanswered question
          if (questionAnswers.value.length > 0) {
            const firstUnansweredIndex = questionsList.findIndex(q => !hasAnswered(q.id))
            if (firstUnansweredIndex !== -1) {
              currentIndex.value = firstUnansweredIndex
            } else {
              currentIndex.value = Math.max(0, questionsList.length - 1)
            }
          }

          if (!isComponentMounted.value) return
          // Load plugin iframe if the current question is a plugin
          await loadCurrentPlugin()
        }
      }
    } else {
      error.value = 'Викторина табылмады немесе қолжетімсіз.'
    }
  } catch (err) {
    console.error('Quiz Error:', err)
    error.value = 'Викторинаны жүктеу кезінде қателік орын алды.'
  } finally {
    loading.value = false
    if (isComponentMounted.value && !isFinished.value && currentQuiz.value) {
      startTimer()
    }
  }
}

import { onBeforeRouteLeave } from 'vue-router'

const handleVisibilityChange = () => {
  if (!isComponentMounted.value) return
  if (document.hidden) {
    stopTimer()
  } else {
    if (currentQuiz.value && !isFinished.value && !loading.value) {
      startTimer()
    }
  }
}

onBeforeRouteLeave(() => {
  isComponentMounted.value = false
  stopTimer()
})

// Global safety net: kill quiz timer when navigating away from any quiz route
const unregisterGuard = router.beforeEach((to) => {
  if (to.name !== 'student-quiz') {
    stopTimer()
  }
})

onMounted(() => {
  stopTimer()
  isComponentMounted.value = true
  fetchQuiz()
  window.addEventListener('message', handlePluginMessage)
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onUnmounted(() => {
  isComponentMounted.value = false
  stopTimer()
  unregisterGuard()
  window.removeEventListener('message', handlePluginMessage)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<style scoped>
/* Focus & hover improvements */
button {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.scrollbar-hide::-webkit-scrollbar {
    display: none;
}
.scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
}
</style>

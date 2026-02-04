<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-6">Талдау</h1>

      <!-- Вкладки -->
      <div class="mb-6 border-b border-gray-200">
        <nav class="flex gap-4">
          <button
            @click="activeTab = 'overview'"
            :class="[
              'px-4 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'overview'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            📊 Жалпы статистика
          </button>
          <button
            @click="activeTab = 'problems'"
            :class="[
              'px-4 py-3 text-sm font-medium border-b-2 transition-colors relative',
              activeTab === 'problems'
                ? 'border-red-600 text-red-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            ⚠️ Қателер
            <span
              v-if="incorrectQuestions.length > 0"
              class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full"
              :class="activeTab === 'problems' ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'"
            >
              {{ incorrectQuestions.length }}
            </span>
          </button>
          <button
            @click="activeTab = 'history'"
            :class="[
              'px-4 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'history'
                ? 'border-green-600 text-green-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            📝 Барлық жауаптар
          </button>
        </nav>
      </div>

      <div v-if="analyticsStore.loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600">Жүктелуде...</p>
      </div>

      <div v-else-if="analyticsStore.error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        <p class="font-semibold">Талдауды жүктеу қатесі:</p>
        <p>{{ analyticsStore.error }}</p>
        <p class="text-sm mt-2">Жүйеге авторизацияланғаныңызға көз жеткізіңіз.</p>
        <p class="text-xs mt-2 text-gray-600">Бетті жаңартып немесе серверге қосылымды тексеріп көріңіз.</p>
      </div>

      <div v-else>
        <!-- ========== ВКЛАДКА: ОБЩАЯ СТАТИСТИКА ========== -->
        <div v-if="activeTab === 'overview'">
        <!-- Общая статистика -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <Card>
            <div>
              <span class="text-sm text-gray-500 block mb-1">Жалпы уақыт</span>
              <p class="text-2xl font-bold">{{ formatTime(analyticsStore.totalTime) }}</p>
            </div>
          </Card>

          <Card>
            <div>
              <span class="text-sm text-gray-500 block mb-1">Барлық сұрақтар</span>
              <p class="text-2xl font-bold">{{ analyticsStore.totalQuestions }}</p>
            </div>
          </Card>

          <Card>
            <div>
              <span class="text-sm text-gray-500 block mb-1">Дәлдік</span>
              <p class="text-2xl font-bold text-green-600">{{ analyticsStore.accuracy }}%</p>
            </div>
          </Card>

          <Card>
            <div>
              <span class="text-sm text-gray-500 block mb-1">Өткізілген тақырыптар</span>
              <p class="text-2xl font-bold text-blue-600">{{ completedTopics.length }}</p>
            </div>
          </Card>
        </div>

        <!-- Пройденные темы -->
        <div v-if="completedTopics.length > 0" class="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 class="text-2xl font-semibold mb-4 flex items-center gap-2">
            <svg class="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span v-if="authStore.isAuthenticated">Өткізілген тақырыптар (SmartScore = 100)</span>
            <span v-else>Өткізілген тақырыптар</span>
          </h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Тақырып
                  </th>
                  <th v-if="authStore.isAuthenticated" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    SmartScore
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Сұрақтар
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Уақыт
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Дәлдік
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="topic in completedTopics" :key="topic.skill_id">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 flex items-center gap-2">
                    <svg class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    {{ topic.name }}
                  </td>
                  <td v-if="authStore.isAuthenticated" class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-green-600">
                    {{ topic.best_smartscore }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ topic.total_questions }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatTime(topic.total_time_seconds || 0) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ topic.accuracy_percent }}%
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Сообщение, если нет данных на вкладке overview -->
        <div v-if="analyticsStore.skills.length === 0 && analyticsStore.totalQuestions === 0" class="bg-white rounded-lg shadow-md p-6 text-center text-gray-600">
          <p class="text-lg mb-2">Талдау деректері әлі жоқ</p>
          <p class="text-sm">Статистиканы көру үшін практиканы бастаңыз!</p>
        </div>
        </div>
        <!-- ========== КОНЕЦ ВКЛАДКИ: ОБЩАЯ СТАТИСТИКА ========== -->

        <!-- ========== ВКЛАДКА: ПРОБЛЕМЫ (ҚАТЕЛЕР) ========== -->
        <div v-if="activeTab === 'problems'">
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-semibold mb-4 flex items-center gap-2">
              <svg class="w-6 h-6 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
              Қате жауаптар — оларды қайталау керек
            </h2>
            <p class="text-gray-600 mb-6">Бұл сұрақтарға қате жауап берілді. Оларды қайта қарап, түсініңіз.</p>

            <div v-if="incorrectQuestions.length === 0" class="text-center py-12 text-gray-500">
              <svg class="w-16 h-16 mx-auto mb-4 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <p class="text-lg font-medium text-green-600">Керемет! Қателер жоқ!</p>
              <p class="text-sm mt-2">Барлық сұрақтарға дұрыс жауап бердіңіз.</p>
            </div>

            <div v-else class="space-y-4">
              <div
                v-for="question in incorrectQuestions"
                :key="question.attempt_id"
                class="border border-red-200 rounded-lg p-4 bg-red-50"
              >
                <!-- Для плагинов - специальное отображение -->
                <template v-if="isPluginQuestion(question)">
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex-1">
                      <div class="flex items-center gap-2 mb-2">
                        <span class="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded-full">
                          🎮 {{ getPluginData(question)?.pluginType }}
                        </span>
                      </div>
                      <!-- Если есть текст вопроса (не только тип) - показываем -->
                      <p
                        v-if="getPluginData(question)?.questionText !== getPluginData(question)?.pluginType"
                        class="font-medium text-gray-900 mb-1"
                      >
                        {{ getPluginData(question)?.questionText }}
                      </p>
                      <p class="text-xs text-gray-500">{{ formatDate(question.answered_at) }}</p>
                    </div>
                    <!-- Кнопка для повторения -->
                    <button
                      v-if="getPluginData(question)?.skillId"
                      @click="openSkillForPractice(getPluginData(question)?.skillId ?? null)"
                      class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white text-xs font-medium rounded-lg transition-colors flex items-center gap-1"
                    >
                      🔄 Қайталау
                    </button>
                  </div>

                  <!-- Визуализация вопроса (если есть questionData) -->
                  <div v-if="getPluginData(question)?.questionData" class="mt-3 mb-4">
                    <div class="bg-purple-50 border border-purple-200 rounded-xl p-4">
                      <div class="flex items-center gap-2 mb-3">
                        <span class="text-purple-600 font-semibold">📝 Тапсырма</span>
                      </div>
                      <AnswerVisualizer
                        :data="getPluginData(question)?.questionData"
                        variant="question"
                        class="mb-2"
                      />
                      <p v-if="getPluginData(question)?.questionData?.description" class="text-gray-700 mt-2">
                        {{ getPluginData(question)?.questionData?.description }}
                      </p>
                    </div>
                  </div>

                <!-- Визуализация в стиле IXL (если есть answerData) -->
                  <div v-if="getPluginData(question)?.answerData" class="mt-4 space-y-4">

                    <!-- Дұрыс жауап (Correct answer) -->
                    <div class="bg-green-50 border border-green-200 rounded-xl p-4">
                      <div class="flex items-center gap-2 mb-3">
                        <span class="text-green-600 font-semibold">✓ Дұрыс жауап</span>
                      </div>
                      <p v-if="getPluginData(question)?.answerData?.correctDisplay?.note" class="text-sm text-gray-600 mb-3 italic">
                        {{ getPluginData(question)?.answerData?.correctDisplay?.note }}
                      </p>
                      <!-- Универсальный визуализатор -->
                      <AnswerVisualizer
                        :data="{
                          type: getPluginData(question)?.answerData?.type,
                          ...getPluginData(question)?.answerData?.correctDisplay
                        }"
                        variant="correct"
                        class="mb-3"
                      />
                      <p class="text-green-700 font-semibold">{{ getPluginData(question)?.answerData?.correctDisplay?.text || getPluginData(question)?.correctAnswer }}</p>
                    </div>

                    <!-- Оқушының жауабы (Student answered) -->
                    <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
                      <div class="flex items-center gap-2 mb-3">
                        <span class="text-gray-700 font-semibold">👤 Сіздің жауабыңыз</span>
                      </div>
                      <!-- Универсальный визуализатор -->
                      <AnswerVisualizer
                        :data="{
                          type: getPluginData(question)?.answerData?.type,
                          ...getPluginData(question)?.answerData?.userDisplay
                        }"
                        variant="user"
                        class="mb-3"
                      />
                      <p class="text-gray-700 font-semibold">{{ getPluginData(question)?.answerData?.userDisplay?.text || getPluginData(question)?.userAnswer }}</p>
                    </div>

                  </div>

                  <!-- Простое отображение (если нет answerData) -->
                  <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                    <div class="bg-red-100 rounded-lg p-3">
                      <p class="text-xs text-red-600 font-medium mb-1">❌ Сіздің жауабыңыз:</p>
                      <p class="text-red-800 font-semibold text-lg">{{ getPluginData(question)?.userAnswer }}</p>
                    </div>
                    <div class="bg-green-100 rounded-lg p-3">
                      <p class="text-xs text-green-600 font-medium mb-1">✓ Дұрыс жауап:</p>
                      <p class="text-green-800 font-semibold text-lg">{{ getPluginData(question)?.correctAnswer }}</p>
                    </div>
                  </div>

                  <!-- Подсказка для визуальных заданий -->
                  <p class="text-xs text-gray-400 mt-3 italic">
                    💡 Толық тапсырманы көру үшін "Қайталау" батырмасын басыңыз
                  </p>
                </template>

                <!-- Для обычных вопросов -->
                <template v-else>
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex-1">
                      <p class="font-medium text-gray-900 mb-1">{{ question.question_prompt || 'Сұрақ' }}</p>
                      <p class="text-xs text-gray-500">{{ formatDate(question.answered_at) }}</p>
                    </div>
                  </div>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                    <div class="bg-red-100 rounded-lg p-3">
                      <p class="text-xs text-red-600 font-medium mb-1">❌ Сіздің жауабыңыз:</p>
                      <p class="text-red-800 font-semibold">{{ formatAnswer(question.user_answer) }}</p>
                    </div>
                    <div class="bg-green-100 rounded-lg p-3">
                      <p class="text-xs text-green-600 font-medium mb-1">✓ Дұрыс жауап:</p>
                      <p class="text-green-800 font-semibold">{{ formatAnswer(question.correct_answer) }}</p>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
        <!-- ========== КОНЕЦ ВКЛАДКИ: ПРОБЛЕМЫ ========== -->

        <!-- ========== ВКЛАДКА: ВСЕ ОТВЕТЫ (ИСТОРИЯ) ========== -->
        <div v-if="activeTab === 'history'">
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-semibold mb-4">Барлық сұрақтар</h2>

            <div v-if="analyticsStore.allQuestions && analyticsStore.allQuestions.length === 0" class="text-center py-12 text-gray-500">
              <p class="text-lg">Әзірге сұрақтар жоқ</p>
            </div>

            <div v-else class="space-y-4">
              <!-- Карточка для каждого вопроса -->
              <div
                v-for="question in analyticsStore.allQuestions"
                :key="question.attempt_id"
                :class="[
                  'border rounded-lg p-4',
                  question.is_correct ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                ]"
              >
                <!-- Для плагинов - специальное отображение -->
                <template v-if="isPluginQuestion(question)">
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex-1">
                      <div class="flex items-center gap-2 mb-2">
                        <span :class="[
                          'px-2 py-1 text-xs font-medium rounded-full',
                          question.is_correct ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                        ]">
                          {{ question.is_correct ? '✓ Дұрыс' : '✗ Қате' }}
                        </span>
                        <span class="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded-full">
                          🎮 {{ getPluginData(question)?.pluginType }}
                        </span>
                      </div>
                      <!-- Если есть текст вопроса (не только тип) - показываем -->
                      <p
                        v-if="getPluginData(question)?.questionText !== getPluginData(question)?.pluginType"
                        class="font-medium text-gray-900 mb-1"
                      >
                        {{ getPluginData(question)?.questionText }}
                      </p>
                      <p class="text-xs text-gray-500">{{ formatDate(question.answered_at) }}</p>
                    </div>
                  </div>

                  <!-- Визуализация в стиле IXL (если есть answerData) -->
                  <div v-if="getPluginData(question)?.answerData" class="mt-4 space-y-4">

                    <!-- Дұрыс жауап (Correct answer) -->
                    <div class="bg-green-50 border border-green-200 rounded-xl p-4">
                      <div class="flex items-center gap-2 mb-3">
                        <span class="text-green-600 font-semibold">✓ Дұрыс жауап</span>
                      </div>
                      <p v-if="getPluginData(question)?.answerData?.correctDisplay?.note" class="text-sm text-gray-600 mb-3 italic">
                        {{ getPluginData(question)?.answerData?.correctDisplay?.note }}
                      </p>
                      <!-- Универсальный визуализатор -->
                      <AnswerVisualizer
                        :data="{
                          type: getPluginData(question)?.answerData?.type,
                          ...getPluginData(question)?.answerData?.correctDisplay
                        }"
                        variant="correct"
                        class="mb-3"
                      />
                      <p class="text-green-700 font-semibold">{{ getPluginData(question)?.answerData?.correctDisplay?.text || getPluginData(question)?.correctAnswer }}</p>
                    </div>

                    <!-- Оқушының жауабы (Student answered) -->
                    <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
                      <div class="flex items-center gap-2 mb-3">
                        <span class="text-gray-700 font-semibold">👤 Сіздің жауабыңыз</span>
                      </div>
                      <!-- Универсальный визуализатор -->
                      <AnswerVisualizer
                        :data="{
                          type: getPluginData(question)?.answerData?.type,
                          ...getPluginData(question)?.answerData?.userDisplay
                        }"
                        variant="user"
                        class="mb-3"
                      />
                      <p class="text-gray-700 font-semibold">{{ getPluginData(question)?.answerData?.userDisplay?.text || getPluginData(question)?.userAnswer }}</p>
                    </div>

                  </div>

                  <!-- Простое отображение (если нет answerData) -->
                  <div v-else class="mt-3 grid grid-cols-2 gap-4">
                    <div :class="[
                      'rounded-lg p-3',
                      question.is_correct ? 'bg-green-100' : 'bg-gray-100'
                    ]">
                      <p class="text-xs text-gray-500 mb-1">Сіздің жауабыңыз:</p>
                      <p :class="[
                        'font-medium',
                        question.is_correct ? 'text-green-700' : 'text-gray-700'
                      ]">{{ getPluginData(question)?.userAnswer }}</p>
                    </div>
                    <div class="bg-green-100 rounded-lg p-3">
                      <p class="text-xs text-gray-500 mb-1">Дұрыс жауап:</p>
                      <p class="font-medium text-green-700">{{ getPluginData(question)?.correctAnswer }}</p>
                    </div>
                  </div>
                </template>

                <!-- Для обычных вопросов -->
                <template v-else>
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex-1">
                      <div class="flex items-center gap-2 mb-2">
                        <span :class="[
                          'px-2 py-1 text-xs font-medium rounded-full',
                          question.is_correct ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                        ]">
                          {{ question.is_correct ? '✓ Дұрыс' : '✗ Қате' }}
                        </span>
                      </div>
                      <p class="font-medium text-gray-900 mb-1">{{ question.question_prompt }}</p>
                      <p class="text-xs text-gray-500">{{ formatDate(question.answered_at) }}</p>
                    </div>
                  </div>
                  <div class="mt-3 grid grid-cols-2 gap-4">
                    <div :class="[
                      'rounded-lg p-3',
                      question.is_correct ? 'bg-green-100' : 'bg-gray-100'
                    ]">
                      <p class="text-xs text-gray-500 mb-1">Сіздің жауабыңыз:</p>
                      <p :class="[
                        'font-medium',
                        question.is_correct ? 'text-green-700' : 'text-gray-700'
                      ]">{{ formatAnswer(question.user_answer) }}</p>
                    </div>
                    <div class="bg-green-100 rounded-lg p-3">
                      <p class="text-xs text-gray-500 mb-1">Дұрыс жауап:</p>
                      <p class="font-medium text-green-700">{{ formatAnswer(question.correct_answer) }}</p>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
        <!-- ========== КОНЕЦ ВКЛАДКИ: ВСЕ ОТВЕТЫ ========== -->
      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { useCatalogStore } from '@/stores/catalog'
import { useAuthStore } from '@/stores/auth'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Card from '@/components/ui/Card.vue'
import AnswerVisualizer from '@/components/analytics/AnswerVisualizer.vue'

const analyticsStore = useAnalyticsStore()
const catalogStore = useCatalogStore()
const authStore = useAuthStore()

const activeTab = ref<'overview' | 'problems' | 'history'>('overview')
const skillNames = ref<Map<number, string>>(new Map())

// Убеждаемся, что skillNames всегда является Map
if (!skillNames.value) {
  skillNames.value = new Map()
}

const formatTime = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  if (hours > 0) {
    return `${hours}ч ${mins}м ${secs}с`
  }
  if (mins > 0) {
    return `${mins}м ${secs}с`
  }
  return `${secs}с`
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Парсит JSON строку если это JSON
const tryParseJson = (str: string): any => {
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

// Форматирует ответ для отображения
const formatAnswer = (answer: any): string => {
  if (answer === null || answer === undefined) return '-'

  // Если строка - попробуем распарсить как JSON
  if (typeof answer === 'string') {
    const parsed = tryParseJson(answer)
    if (parsed !== answer && typeof parsed === 'object') {
      return formatAnswer(parsed) // Рекурсивно форматируем распарсенный объект
    }
    return answer || '-'
  }

  if (typeof answer === 'number') return String(answer)
  if (typeof answer === 'boolean') return answer ? 'Иә' : 'Жоқ'

  if (typeof answer === 'object') {
    // Для плагинов - извлекаем userAnswer / correctAnswer
    if (answer.userAnswer !== undefined) return String(answer.userAnswer)
    if (answer.correctAnswer !== undefined) return String(answer.correctAnswer)
    if (answer.value !== undefined) return String(answer.value)
    if (answer.selected !== undefined) return String(answer.selected)
    if (answer.text !== undefined) return String(answer.text)
    if (answer.answer !== undefined) return String(answer.answer)
    if (answer.choice !== undefined) return String(answer.choice)

    // Если нет известных полей - показываем JSON красиво
    try {
      return JSON.stringify(answer)
    } catch {
      return String(answer)
    }
  }
  return String(answer)
}

// Тип плагина на человекочитаемом языке
const getPluginTypeName = (question: any): string => {
  const prompt = (question.question_prompt || '').toLowerCase()
  const type = (question.question_type || '').toLowerCase()

  // Определяем тип по названию
  if (prompt.includes('drag') || prompt.includes('drop') || type.includes('drag')) {
    return 'Сүйреп апару'
  }
  if (prompt.includes('graph') || prompt.includes('chart') || type.includes('graph')) {
    return 'График'
  }
  if (prompt.includes('draw') || prompt.includes('paint') || type.includes('draw')) {
    return 'Сурет салу'
  }
  if (prompt.includes('match') || type.includes('match')) {
    return 'Сәйкестендіру'
  }
  if (prompt.includes('sort') || prompt.includes('order') || type.includes('sort')) {
    return 'Реттеу'
  }
  if (prompt.includes('fraction') || type.includes('fraction')) {
    return 'Бөлшектер'
  }
  if (prompt.includes('equation') || type.includes('equation')) {
    return 'Теңдеу'
  }
  if (prompt.includes('addition') || prompt.includes('қосу')) {
    return 'Қосу'
  }
  if (prompt.includes('subtract') || prompt.includes('алу')) {
    return 'Азайту'
  }
  if (prompt.includes('multiply') || prompt.includes('көбейту')) {
    return 'Көбейту'
  }
  if (prompt.includes('divide') || prompt.includes('бөлу')) {
    return 'Бөлу'
  }

  return 'Интерактивті тапсырма'
}

// Тип данных для визуализации
interface AnswerData {
  type: 'grid' | 'graph' | 'dragdrop'
  gridSize?: number
  userSelection?: string[]
  correctSelection?: string[]
  targetArea?: number
  userPoints?: Array<{x: number, y: number}>
  correctPoints?: Array<{x: number, y: number}>
  equation?: string
  userOrder?: string[]
  correctOrder?: string[]
}

// Тип данных для визуализации вопроса
interface QuestionData {
  type: 'numberline' | 'grid' | 'fractionbar' | 'graph' | 'image'
  numberline?: {
    min: number
    max: number
    divisions: number
    markedPosition: number
    label?: string
  }
  grid?: {
    rows: number
    cols: number
    filled: string[]
    highlight?: string[]
  }
  fractionBar?: {
    total: number
    filled: number
    label?: string
  }
  description?: string
}

// Получить данные плагина из ответа
const getPluginData = (question: any): {
  userAnswer: string
  correctAnswer: string
  questionText: string
  pluginType: string
  pluginId: string | null
  skillId: number | null
  answerData: AnswerData | null
  questionData: QuestionData | null
} | null => {
  const userAnswerRaw = question.user_answer
  if (!userAnswerRaw) return null

  // Пробуем распарсить как JSON
  const parsed = typeof userAnswerRaw === 'string' ? tryParseJson(userAnswerRaw) : userAnswerRaw

  if (parsed && typeof parsed === 'object' && (parsed.userAnswer !== undefined || parsed.correctAnswer !== undefined)) {
    // Извлекаем текст вопроса из разных возможных полей
    const questionText = parsed.question
      ?? parsed.prompt
      ?? parsed.equation
      ?? parsed.problem
      ?? parsed.questionText
      ?? null

    const pluginType = getPluginTypeName(question)

    // Для визуальных заданий показываем тип вместо текста
    const displayQuestion = questionText || pluginType

    // Извлекаем данные для визуализации ответов
    const answerData: AnswerData | null = parsed.answerData || null

    // Извлекаем данные для визуализации вопроса
    const questionData: QuestionData | null = parsed.questionData || null

    return {
      userAnswer: String(parsed.userAnswer ?? parsed.studentAnswer ?? '-'),
      correctAnswer: String(parsed.correctAnswer ?? '-'),
      questionText: displayQuestion,
      pluginType: pluginType,
      pluginId: question.question_prompt || null,
      skillId: question.skill_id || null,
      answerData: answerData,
      questionData: questionData
    }
  }

  return null
}

// Проверяем, является ли вопрос плагином
const isPluginQuestion = (question: any): boolean => {
  return getPluginData(question) !== null
}

// Открыть навык для повторной практики
const openSkillForPractice = (skillId: number | null) => {
  if (skillId) {
    window.open(`/skill/${skillId}`, '_blank')
  }
}

// Пройденные темы (где best_smartscore = 100)
const completedTopics = computed(() => {
  console.log('Analytics: All skills:', analyticsStore.skills.map(s => ({ skill_id: s.skill_id, best_smartscore: s.best_smartscore, last_smartscore: s.last_smartscore })))
  const completed = analyticsStore.skills.filter(skill => (skill.best_smartscore || 0) >= 100)
  console.log('Analytics: Completed topics (best_smartscore >= 100):', completed.length)
  return completed
    .map(skill => {
      const skillId = skill.skill_id
      const skillName = (skillNames.value && skillNames.value.get(skillId)) || `Дағды ${skillId}`
        return {
          skill_id: skillId,
          name: skillName,
          best_smartscore: skill.best_smartscore || 0,
          total_questions: skill.total_questions || 0,
          total_time_seconds: skill.total_time_seconds || 0,
          accuracy_percent: skill.accuracy_percent || 0,
        }
    })
})

// Все вопросы, отсортированные по правильности (сначала правильные, потом неправильные)
const sortedQuestions = computed(() => {
  const questions = [...(analyticsStore.allQuestions || [])]
  // Сортируем: сначала правильные, потом неправильные
  return questions.sort((a, b) => {
    if (a.is_correct === b.is_correct) {
      // Если одинаковый статус, сортируем по дате (новые сначала)
      return new Date(b.answered_at).getTime() - new Date(a.answered_at).getTime()
    }
    // Правильные идут первыми
    return a.is_correct ? -1 : 1
  })
})

// Правильные вопросы
const correctQuestions = computed(() => {
  return sortedQuestions.value.filter(q => q.is_correct)
})

// Неправильные вопросы
const incorrectQuestions = computed(() => {
  return sortedQuestions.value.filter(q => !q.is_correct)
})

// Загрузка названий навыков
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
    console.log('Analytics: Loading overview, skills, and all questions...')

    // Загружаем основные данные (overview и skills) - принудительно обновляем для свежих данных
    await Promise.all([
      analyticsStore.getOverview(true),
      analyticsStore.getSkills(true),
    ])
    console.log('Analytics: Overview loaded:', analyticsStore.overview)
    console.log('Analytics: Skills loaded:', analyticsStore.skills.length)

    // Загружаем названия навыков для отображения
    if (analyticsStore.skills.length > 0) {
      await loadSkillNames()
    }

    // Загружаем все вопросы отдельно, чтобы ошибка не блокировала остальные данные
    try {
      await analyticsStore.getAllQuestions()
      console.log('Analytics: All questions loaded:', analyticsStore.allQuestions.length)
    } catch (questionsErr: any) {
      console.warn('Analytics: Failed to load all questions (non-critical):', questionsErr)
      // Не блокируем отображение остальных данных
    }
  } catch (err: any) {
    console.error('Analytics: Failed to load analytics:', err)
    console.error('Analytics: Error details:', {
      message: err.message,
      response: err.response?.data,
      status: err.response?.status,
    })
  }
})
</script>

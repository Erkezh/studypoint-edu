<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-6">Талдау</h1>

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

        <!-- Статистика по навыкам -->
        <div v-if="analyticsStore.skills && analyticsStore.skills.length > 0" class="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 class="text-2xl font-semibold mb-4">Барлық дағдылар бойынша статистика</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Дағды
                  </th>
                  <th v-if="authStore.isAuthenticated" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ең жақсы SmartScore
                  </th>
                  <th v-if="authStore.isAuthenticated" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Соңғы SmartScore
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Сұрақтар
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Дәлдік
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="skill in analyticsStore.skills" :key="skill.skill_id">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {{ (skillNames.value && skillNames.value.get(skill.skill_id)) || `Дағды ${skill.skill_id}` }}
                  </td>
                  <td v-if="authStore.isAuthenticated" class="px-6 py-4 whitespace-nowrap text-sm font-semibold" :class="{
                    'text-green-600': (skill.best_smartscore || 0) >= 90,
                    'text-blue-600': (skill.best_smartscore || 0) >= 70 && (skill.best_smartscore || 0) < 90,
                    'text-yellow-600': (skill.best_smartscore || 0) < 70
                  }">
                    {{ skill.best_smartscore || 0 }}
                  </td>
                  <td v-if="authStore.isAuthenticated" class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ skill.last_smartscore || 0 }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ skill.total_questions || 0 }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ skill.accuracy_percent || 0 }}%
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Все вопросы с ответами -->
        <div v-if="analyticsStore.allQuestions && analyticsStore.allQuestions.length > 0" class="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 class="text-2xl font-semibold mb-4">Барлық сұрақтар</h2>
          
          <!-- Правильные вопросы -->
          <div v-if="correctQuestions.length > 0" class="mb-6">
            <h3 class="text-lg font-semibold text-green-600 mb-3 flex items-center gap-2">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              Дұрыс жауаптар ({{ correctQuestions.length }})
            </h3>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Сұрақ</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Сіздің жауабыңыз</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дұрыс жауап</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Күні</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="question in correctQuestions" :key="question.attempt_id" class="bg-green-50">
                    <td class="px-4 py-3 text-sm text-gray-900">{{ question.question_prompt }}</td>
                    <td class="px-4 py-3 text-sm font-medium text-green-700">{{ question.user_answer || '-' }}</td>
                    <td class="px-4 py-3 text-sm text-gray-700">{{ question.correct_answer || '-' }}</td>
                    <td class="px-4 py-3 text-sm text-gray-500">{{ formatDate(question.answered_at) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Неправильные вопросы -->
          <div v-if="incorrectQuestions.length > 0">
            <h3 class="text-lg font-semibold text-red-600 mb-3 flex items-center gap-2">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
              Қате жауаптар ({{ incorrectQuestions.length }})
            </h3>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Сұрақ</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Сіздің жауабыңыз</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дұрыс жауап</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Күні</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="question in incorrectQuestions" :key="question.attempt_id" class="bg-red-50">
                    <td class="px-4 py-3 text-sm text-gray-900">{{ question.question_prompt }}</td>
                    <td class="px-4 py-3 text-sm font-medium text-red-700">{{ question.user_answer || '-' }}</td>
                    <td class="px-4 py-3 text-sm font-medium text-green-700">{{ question.correct_answer || '-' }}</td>
                    <td class="px-4 py-3 text-sm text-gray-500">{{ formatDate(question.answered_at) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Сообщение, если нет данных вообще -->
        <div v-if="!analyticsStore.loading && !analyticsStore.error && analyticsStore.skills.length === 0 && (!analyticsStore.overview || (analyticsStore.totalQuestions === 0 && analyticsStore.totalTime === 0)) && (!analyticsStore.allQuestions || analyticsStore.allQuestions.length === 0)" class="bg-white rounded-lg shadow-md p-6 text-center text-gray-600 mb-6">
          <p class="text-lg mb-2">Талдау деректері әлі жоқ</p>
          <p class="text-sm">Статистиканы көру үшін практиканы бастаңыз!</p>
        </div>
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

const analyticsStore = useAnalyticsStore()
const catalogStore = useCatalogStore()
const authStore = useAuthStore()

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

// Пройденные темы (где best_smartscore = 100)
const completedTopics = computed(() => {
  return analyticsStore.skills
    .filter(skill => (skill.best_smartscore || 0) >= 100)
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
    
    // Загружаем основные данные (overview и skills) - они критичны
    await Promise.all([
      analyticsStore.getOverview(),
      analyticsStore.getSkills(),
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

<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="flex">
      <!-- Боковая панель с классами (полукруги) -->
      <aside class="relative shrink-0">
        <nav class="flex flex-col pt-8">
          <div
            v-for="(grade, index) in grades"
            :key="grade.id"
            class="relative group"
            style="margin-bottom: 2px;"
          >
            <button
              @click="navigateToGrade(grade.number)"
              :class="[
                'relative w-12 h-16 flex items-center justify-center text-white font-bold text-xl transition-all shadow-lg z-10',
                currentGradeId === grade.number ? 'scale-110' : 'hover:scale-105',
              ]"
              :style="{
                backgroundColor: getGradeColor(index, currentGradeId === grade.number),
                borderRadius: '24px 0 0 24px',
              }"
            >
              {{ grade.number }}
            </button>

            <!-- Всплывающая подсказка с полным названием -->
            <div
              class="absolute left-full top-1/2 transform -translate-y-1/2 bg-gray-900 text-white px-3 py-2 rounded-lg text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 shadow-lg ml-1"
            >
              {{ grade.number }} {{ grade.title }}
              <div class="absolute right-full top-1/2 transform -translate-y-1/2 w-0 h-0 border-t-4 border-t-transparent border-r-4 border-r-gray-900 border-b-4 border-b-transparent"></div>
            </div>
          </div>
        </nav>
      </aside>

      <!-- Основной контент -->
      <div class="flex-1 px-8 py-8">
        <div class="mb-6">
          <h1 class="text-3xl font-bold text-orange-600 mb-2">
            {{ currentGradeTitle }}
          </h1>
          <p class="text-gray-600">
            Math Edu сотыңызға жүздеген математика дағдыларын ұсынады!
          </p>
        </div>

        <div v-if="catalogStore.loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p class="mt-4 text-gray-600">Жүктелуде...</p>
        </div>

        <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {{ error }}
        </div>

        <div v-else>
          <div v-if="!skills || skills.length === 0" class="text-center py-12 text-gray-600">
            <p>Дағдылар табылмады</p>
          </div>

          <!-- Список тем -->
          <div v-else-if="skills && skills.length > 0" class="space-y-1">
            <div
              v-for="skill in skills"
              :key="skill.id"
              @click.stop="navigateToSkill(skill.id)"
              :class="[
                'flex items-center justify-between p-4 bg-white rounded-lg border border-gray-200 hover:border-lime-400 hover:shadow-md transition-all',
                loadingSkillId === skill.id && 'opacity-75 cursor-wait'
              ]"
            >
              <div class="flex items-center gap-4 flex-1 cursor-pointer">
                <!-- Иконка статуса -->
                <div v-if="skillStats.has(skill.id) && skillStats.get(skill.id)!.best_smartscore >= 90" class="shrink-0">
                  <svg class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div v-else class="w-5 h-5 shrink-0"></div>

                <!-- Название темы -->
                <div class="flex-1">
                  <h3 class="text-base font-medium text-gray-900 hover:text-lime-600">
                    {{ skill.title }}
                  </h3>
                  <p v-if="skillStats.has(skill.id) && authStore.isAuthenticated" class="text-sm text-gray-500 mt-1">
                    SmartScore:
                    <span :class="{
                      'text-green-600 font-semibold': skillStats.get(skill.id)!.best_smartscore >= 90,
                      'text-blue-600': skillStats.get(skill.id)!.best_smartscore >= 70 && skillStats.get(skill.id)!.best_smartscore < 90,
                      'text-yellow-600': skillStats.get(skill.id)!.best_smartscore < 70
                    }">
                      {{ skillStats.get(skill.id)!.best_smartscore || skillStats.get(skill.id)!.last_smartscore || 0 }}
                    </span>
                  </p>
                </div>
              </div>

              <!-- Кнопка удаления для админа -->
              <div v-if="authStore.user?.role === 'ADMIN'" class="shrink-0 ml-4">
                <button
                  @click.stop="confirmDeleteSkill(skill.id, skill.title)"
                  :disabled="deletingSkillId === skill.id"
                  class="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Тестті жою"
                >
                  <svg v-if="deletingSkillId !== skill.id" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  <div v-else class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-red-600"></div>
                </button>
              </div>

              <!-- Индикатор загрузки -->
              <div v-if="loadingSkillId === skill.id && authStore.user?.role !== 'ADMIN'" class="shrink-0 ml-4">
                <div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    <Footer />

    <!-- Модальное окно о завершении пробного периода или необходимости авторизации -->
    <Modal
      :is-open="showTrialEndedModal"
      :title="trialQuestions.isTrialQuestionsExhausted.value ? 'Сынақ кезеңі аяқталды' : 'Авторизация қажет'"
      :show-close="true"
      @close="showTrialEndedModal = false"
    >
      <template #content>
        <div class="space-y-4">
          <p class="text-gray-700" v-if="trialQuestions.isTrialQuestionsExhausted.value">
            Сіз бүгін барлық {{ TRIAL_QUESTIONS_LIMIT }} тегін сұрақтарды пайдаландыңыз.
          </p>
          <p class="text-gray-700" v-else>
            Практиканы бастау үшін аккаунтқа кіру қажет.
          </p>
          <p class="text-gray-700" v-if="!trialQuestions.isTrialQuestionsExhausted.value">
            Кіргеннен кейін сіз күн сайын <strong>{{ TRIAL_QUESTIONS_LIMIT }} сұраққа тегін</strong> жауап бере аласыз.
          </p>
          <p class="text-gray-700" v-if="trialQuestions.isTrialQuestionsExhausted.value">
            Практиканы жалғастыру және шексіз сұрақтарға қол жеткізу үшін аккаунтқа кіріңіз.
          </p>
        </div>
      </template>
      <template #actions>
        <Button @click="goToLogin" variant="primary">
          Аккаунтқа кіру
        </Button>
        <Button @click="goToHome" variant="outline">
          Басты бетке
        </Button>
      </template>
    </Modal>

    <!-- Модальное окно подтверждения удаления теста -->
    <Modal
      :is-open="showDeleteModal"
      title="Тестті жою"
      :show-close="true"
      @close="showDeleteModal = false"
    >
      <template #content>
        <div class="space-y-4">
          <p class="text-gray-700">
            Сіз шынымен де <strong>"{{ skillToDelete?.title }}"</strong> тестін жойғыңыз келе ме?
          </p>
          <p class="text-sm text-red-600">
            ⚠ Бұл әрекетті к geri қайтару мүмкін емес. Тестпен байланысты барлық деректер жойылады.
          </p>
        </div>
      </template>
      <template #actions>
        <Button @click="deleteSkill" variant="primary" :disabled="deletingSkillId !== null" :loading="deletingSkillId !== null" class="bg-red-600 hover:bg-red-700">
          Жою
        </Button>
        <Button @click="showDeleteModal = false" variant="outline" :disabled="deletingSkillId !== null">
          Болдырмау
        </Button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onActivated, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'
import { usePracticeStore } from '@/stores/practice'
import { useAuthStore } from '@/stores/auth'
import { useTrialQuestions } from '@/composables/useTrialQuestions'
import { adminApi } from '@/api/admin'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import Modal from '@/components/ui/Modal.vue'

interface Props {
  gradeId: string
}

const props = defineProps<Props>()
const router = useRouter()
const catalogStore = useCatalogStore()
const practiceStore = usePracticeStore()
const authStore = useAuthStore()
const trialQuestions = useTrialQuestions()

const skills = computed(() => catalogStore.skills)
const grades = ref(catalogStore.grades)
const currentGradeId = ref<number>(parseInt(props.gradeId, 10))
const error = ref<string | null>(null)
const loadingSkillId = ref<number | null>(null)
const showTrialEndedModal = ref(false)
const skillStats = ref<Map<number, { best_smartscore: number; last_smartscore: number; is_completed: boolean }>>(new Map())
const loadingStats = ref(false)
const showDeleteModal = ref(false)
const skillToDelete = ref<{ id: number; title: string } | null>(null)
const deletingSkillId = ref<number | null>(null)

const TRIAL_QUESTIONS_LIMIT = trialQuestions.TRIAL_QUESTIONS_LIMIT

// Название текущего класса
const currentGradeTitle = computed(() => {
  const grade = grades.value.find(g => g.number === currentGradeId.value)
  return grade ? grade.title : `${currentGradeId.value} сынып`
})

// Переход к другому классу
const navigateToGrade = (gradeNumber: number) => {
  if (currentGradeId.value === gradeNumber) return
  currentGradeId.value = gradeNumber
  router.push({ name: 'class', params: { gradeId: gradeNumber } })
  loadSkillsForGrade(gradeNumber)
}

// Цвета для классов (чередуются)
const getGradeColor = (index: number, isActive: boolean): string => {
  const colors = [
    '#3B82F6', // синий
    '#F97316', // оранжевый
    '#10B981', // зеленый
    '#EF4444', // красный
    '#8B5CF6', // фиолетовый
    '#06B6D4', // голубой
    '#F59E0B', // желтый
    '#EC4899', // розовый
  ]
  const color = colors[index % colors.length] || '#3B82F6'
  if (isActive) {
    // Делаем активный цвет немного темнее
    return color
  }
  return color
}

const goToLogin = () => {
  showTrialEndedModal.value = false
  router.push({
    name: 'login',
    query: {
      redirect: router.currentRoute.value.fullPath,
      requireSubscription: 'true'
    }
  })
}

const goToHome = () => {
  showTrialEndedModal.value = false
  router.push({ name: 'home' })
}

const navigateToSkill = async (skillId: number) => {
  loadingSkillId.value = skillId
  error.value = null

  try {
    const numericSkillId = typeof skillId === 'string' ? parseInt(skillId, 10) : skillId
    if (isNaN(numericSkillId)) {
      throw new Error('Дағды ID-і дұрыс емес')
    }

    // НЕ проверяем пробные вопросы перед созданием сессии
    // Бэкенд теперь поддерживает создание сессии без авторизации (для пробных вопросов)
    // Проверка пробных вопросов будет происходить после каждого ответа

    const session = await practiceStore.createSession(numericSkillId)
    // Проверяем, что сессия создана успешно
    if (session && session.id) {
      // Если сессия была восстановлена (не новая), обновляем статистику
      if (session.questions_answered > 0) {
        await loadSkillStats(numericSkillId)
      }
      router.push({ name: 'practice', params: { sessionId: session.id } })
    } else {
      error.value = 'Сессияны құру мүмкін болмады. Қайталап көріңіз.'
    }
  } catch (err: unknown) {
    const apiError = err as { response?: { data?: { detail?: string | Array<{ loc?: string[]; msg?: string }>; message?: string }; status?: number }; message?: string }
    console.error('ClassView: Failed to create session:', err)
    console.error('ClassView: Error response:', apiError.response?.data)
    console.error('ClassView: Error status:', apiError.response?.status)
    console.error('ClassView: isAuthenticated:', authStore.isAuthenticated)
    console.error('ClassView: user role:', authStore.user?.role)

    // Обработка ошибки 401 (Unauthorized) - не должна происходить, так как бэкенд поддерживает неавторизованных пользователей
    // Но если произошла, обрабатываем как ошибку
    if (apiError.response?.status === 401) {
      console.log('ClassView: Handling 401 error (unexpected)')
      console.log('ClassView: isAuthenticated:', authStore.isAuthenticated)

      // Для авторизованных пользователей ошибка 401 не должна блокировать
      if (authStore.isAuthenticated) {
        // Если пользователь авторизован, но получил 401, это может быть проблема с токеном
        error.value = 'Авторизация қатесі. Шығып, қайта кіріңіз.'
        return
      }

      // Для неавторизованных пользователей 401 не должна происходить
      // Но если произошла, показываем общую ошибку
      error.value = 'Сессияны құру кезінде қате. Қайталап көріңіз.'
      return
    }

    // Обработка ошибки 402 (Payment Required)
    if (apiError.response?.status === 402) {
      // Для авторизованных пользователей ошибка 402 не должна блокировать
      if (authStore.isAuthenticated) {
        error.value = 'Қол жеткізу қатесі. Қайталап көріңіз.'
        return
      }
      // Если пользователь не авторизован и пробные вопросы исчерпаны, показываем модальное окно
      if (!authStore.isAuthenticated && trialQuestions.isTrialQuestionsExhausted.value) {
        showTrialEndedModal.value = true
        return
      }
      error.value = 'Практиканы жалғастыру үшін жазылым қажет. Профильде жазылымды рәсімдеңіз.'
      return
    }

    let errorMessage = 'Практиканы бастау мүмкін болмады'

    if (apiError.response?.data?.detail) {
      if (Array.isArray(apiError.response.data.detail)) {
        const validationErrors = apiError.response.data.detail
          .map((e: { loc?: string[]; msg?: string }) => `${e.loc?.join('.')}: ${e.msg}`)
          .join(', ')
        errorMessage = `Валидация қатесі: ${validationErrors}`
      } else if (typeof apiError.response.data.detail === 'string') {
        errorMessage = apiError.response.data.detail
      }
    } else if (apiError.response?.data?.message) {
      errorMessage = apiError.response.data.message
    } else if (apiError.message) {
      errorMessage = apiError.message
    }

    error.value = errorMessage
    console.error('Failed to start practice:', apiError.response?.data || err)
  } finally {
    loadingSkillId.value = null
  }
}

// Загрузка статистики для навыка
const loadSkillStats = async (skillId: number) => {
  try {
    const stats = await catalogStore.getSkillStats(skillId)
    skillStats.value.set(skillId, {
      best_smartscore: stats.best_smartscore || 0,
      last_smartscore: stats.last_smartscore || 0,
      is_completed: (stats.best_smartscore || 0) >= 90,
    })
  } catch (err) {
    // Игнорируем ошибки загрузки статистики (может быть неавторизованный пользователь)
    console.warn('Failed to load stats for skill', skillId, err)
  }
}

// Загрузка статистики для всех навыков
const loadAllSkillStats = async () => {
  loadingStats.value = true
  try {
    // Загружаем статистику параллельно для всех навыков
    const currentSkills = catalogStore.skills
    console.log('ClassView: Loading stats for skills:', currentSkills.length)
    const promises = currentSkills.map(skill => loadSkillStats(skill.id))
    await Promise.allSettled(promises)
  } finally {
    loadingStats.value = false
  }
}

// Загрузка навыков для класса
const loadSkillsForGrade = async (gradeNumber: number, force = false) => {
  try {
    error.value = null
    const fetchedSkills = await catalogStore.getSkills({
      grade_number: gradeNumber,
    }, force)

    // Загружаем статистику для всех навыков
    if (fetchedSkills && fetchedSkills.length > 0) {
      await loadAllSkillStats()
    }
  } catch (err: unknown) {
    const apiError = err as { response?: { data?: { detail?: string | Array<{ msg?: string }> }; status?: number }; message?: string; code?: string }
    const errorMsg = apiError.response?.data?.detail
      ? (Array.isArray(apiError.response.data.detail)
        ? apiError.response.data.detail.map((e: { msg?: string }) => e.msg).join(', ')
        : apiError.response.data.detail)
      : apiError.message || 'Дағдыларды жүктеу мүмкін болмады'

    error.value = errorMsg
    console.error('ClassView: Failed to load skills:', {
      error: err,
      response: apiError.response?.data,
      status: apiError.response?.status,
      code: apiError.code,
      message: apiError.message,
    })
  }
}

onMounted(async () => {
  try {
    const gradeNumber = parseInt(props.gradeId, 10)
    if (isNaN(gradeNumber)) {
      error.value = 'Сынып ID-і дұрыс емес'
      return
    }

    currentGradeId.value = gradeNumber

    // Загружаем классы для боковой панели
    if (grades.value.length === 0) {
      grades.value = await catalogStore.getGrades()
    }

    // Загружаем навыки для текущего класса
    await loadSkillsForGrade(gradeNumber)
  } catch (err: unknown) {
    const apiError = err as { response?: { data?: { detail?: string | Array<{ msg?: string }> }; status?: number }; message?: string; code?: string }
    error.value = apiError.message || 'Жүктеу қатесі'
    console.error('ClassView: Failed to initialize:', err)
  }
})

// Подтверждение удаления теста
const confirmDeleteSkill = (skillId: number, skillTitle: string) => {
  skillToDelete.value = { id: skillId, title: skillTitle }
  showDeleteModal.value = true
}

// Удаление теста
const deleteSkill = async () => {
  if (!skillToDelete.value) return

  deletingSkillId.value = skillToDelete.value.id
  error.value = null

  try {
    await adminApi.deleteSkill(skillToDelete.value.id)
    
    // Закрываем модальное окно
    showDeleteModal.value = false
    const deletedSkillId = skillToDelete.value.id
    skillToDelete.value = null

    // Удаляем из локального списка сразу (оптимистичное обновление)
    const index = skills.value.findIndex(s => s.id === deletedSkillId)
    if (index !== -1) {
      skills.value.splice(index, 1)
    }
    skillStats.value.delete(deletedSkillId)

    // Перезагружаем список навыков с сервера, чтобы убедиться, что удаление применилось
    // Используем force=true чтобы обойти кэш
    await catalogStore.getSkills({ grade_number: currentGradeId.value }, true)
    
    // Обновляем локальный computed
    // skills уже обновлен через catalogStore.skills
  } catch (err: any) {
    console.error('Failed to delete skill:', err)
    const status = err.response?.status
    const errorData = err.response?.data
    
    // Если навык уже удален (404), это не критическая ошибка
    if (status === 404) {
      // Удаляем из локального списка и перезагружаем
      const index = skills.value.findIndex(s => s.id === skillToDelete.value!.id)
      if (index !== -1) {
        skills.value.splice(index, 1)
      }
      skillStats.value.delete(skillToDelete.value.id)
      await catalogStore.getSkills({ grade_number: currentGradeId.value }, true)
      showDeleteModal.value = false
      skillToDelete.value = null
      return
    }
    
    const errorMsg = errorData?.detail || errorData?.message || err.message || 'Тестті жою мүмкін болмады'
    error.value = errorMsg
  } finally {
    deletingSkillId.value = null
  }
}

// Обновляем статистику при возврате на страницу
onActivated(async () => {
  if (catalogStore.skills.length > 0) {
    await loadAllSkillStats()
  }
  // Обновляем текущий класс из props, если изменился
  const gradeNumber = parseInt(props.gradeId, 10)
  if (!isNaN(gradeNumber) && currentGradeId.value !== gradeNumber) {
    currentGradeId.value = gradeNumber
    await loadSkillsForGrade(gradeNumber)
  }
})
</script>

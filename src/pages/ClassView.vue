<template>
  <div class="min-h-screen bg-gray-50 overflow-x-hidden">
    <Header />
    <div class="bg-white border-b border-gray-200">
      <ViewByToggle />
    </div>
    <main class="flex">
      <!-- Боковая панель с классами (IXL style - Popout Overlay) -->
      <aside class="relative shrink-0 w-12 z-30 pt-4 select-none">
        <!-- Sidebar Border Line -->
        <div class="absolute right-0 top-0 bottom-0 w-px bg-gray-200 z-10"></div>

        <nav class="flex flex-col gap-1 w-full relative z-20">
          <div v-for="(grade, index) in grades" :key="grade.number"
               class="relative h-14 w-full">

            <!-- Tab Button (Absolute positioned to grow right) -->
            <button @click="navigateToGrade(grade.number)"
              class="group absolute left-0 top-1 h-12 flex items-center transition-all duration-300 ease-out shadow-sm overflow-hidden border border-transparent"
              :class="[
                currentGradeId === grade.number
                  ? 'w-[49px] hover:w-56 md:hover:w-64 z-50 rounded-l-full rounded-r-none hover:rounded-r-full pr-0 shadow-none -mr-px border-gray-200 border-r-0 hover:border-r'
                  : 'w-12 hover:w-56 md:hover:w-64 z-30 rounded-l-full rounded-r-none hover:rounded-r-full hover:shadow-md hover:z-50',
              ]"
              :style="currentGradeId === grade.number
                ? { backgroundColor: '#f9fafb', color: getGradeColor(index), borderColor: '#e5e7eb' }
                : { backgroundColor: getGradeColor(index), color: 'white' }">

               <!-- Grade Title (Visible ONLY on Hover) -->
               <span class="absolute left-14 font-medium whitespace-nowrap opacity-0 transition-opacity duration-200 group-hover:opacity-100 delay-75 pointer-events-none">
                 {{ getKazakhGradeTitle(grade.number) }}
               </span>

               <!-- Grade Number (Always visible circle part) -->
               <span class="absolute left-0 w-12 h-12 flex items-center justify-center font-bold text-xl shrink-0 z-10">
                 {{ grade.number === -1 ? 'PK' : (grade.number === 0 ? 'K' : grade.number) }}
               </span>
            </button>
          </div>
        </nav>
      </aside>

      <!-- Основной контент -->
      <div class="flex-1 pl-6 pr-8 py-8">
        <div class="mb-8 flex items-end justify-between border-b pb-4">
          <div>
             <h1 class="text-3xl font-bold text-orange-600 mb-2">
              {{ currentGradeTitle }}
            </h1>
            <p class="text-gray-600 max-w-3xl">
              Math Edu offers hundreds of {{ currentGradeTitle.toLowerCase() }} skills to explore and learn! Not sure where to start?
            </p>
          </div>

          <!-- Mock Stats (IXL Style) -->
          <div class="hidden md:flex gap-4">
             <div class="flex flex-col items-center px-4 py-1 bg-orange-50 rounded-full border border-orange-200">
               <span class="text-lg font-bold text-orange-600">{{ skills.length }}</span>
               <span class="text-xs text-orange-800 uppercase font-semibold">skills</span>
             </div>
             <div class="flex flex-col items-center px-4 py-1 bg-orange-50 rounded-full border border-orange-200">
               <span class="text-lg font-bold text-orange-600">--</span>
               <span class="text-xs text-orange-800 uppercase font-semibold">lessons</span>
             </div>
          </div>
        </div>

        <div v-if="catalogStore.loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p class="mt-4 text-gray-600">Жүктелуде...</p>
        </div>

        <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {{ error }}
        </div>

          <!-- Grouped Skills List (Masonry Layout) -->
          <div v-else class="columns-1 md:columns-2 lg:columns-3 gap-8 space-y-8">
            <div v-for="group in groupedSkills" :key="group.id" class="break-inside-avoid mb-8">
              <!-- Topic Header -->
              <h3 class="text-lg font-bold mb-3 flex items-start gap-2 text-green-700 hover:text-green-800 cursor-pointer">
                 <span class="text-xl -mt-0.5">{{ group.letter }}.</span>
                 <span class="leading-tight">{{ group.title }}</span>
              </h3>

              <!-- Skills List -->
              <div class="space-y-1">
                <div v-for="(skill, index) in group.skills" :key="skill.id"
                  @click.stop="navigateToSkill(skill.id)"
                  class="group/skill flex items-start gap-2 py-0.5 px-2 -mx-2 rounded hover:bg-green-50 cursor-pointer transition-colors relative">

                  <!-- Skill Number -->
                  <span class="text-sm font-bold text-gray-500 w-5 text-right shrink-0 group-hover/skill:text-green-600">
                    {{ index + 1 }}
                  </span>

                  <!-- Skill Title -->
                  <span class="text-sm text-gray-700 group-hover/skill:text-green-700 group-hover/skill:underline decoration-green-700/50 underline-offset-2">
                    {{ skill.title }}
                  </span>

                  <!-- Status Icon (Medal/Ribbon) -->
                  <div v-if="skillStats.has(skill.id)" class="ml-auto shrink-0 pl-2">
                     <span v-if="(skillStats.get(skill.id)!.best_smartscore || 0) >= 90" title="Mastered" class="text-yellow-500">
                       🏅
                     </span>
                     <span v-else-if="(skillStats.get(skill.id)!.best_smartscore || 0) >= 70" title="Practiced" class="text-blue-500 text-xs font-bold">
                       {{ skillStats.get(skill.id)!.best_smartscore }}
                     </span>
                  </div>

                  <!-- Admin Delete Button -->
                  <button v-if="authStore.user?.role === 'ADMIN'"
                    @click.stop="confirmDeleteSkill(skill.id, skill.title)"
                    class="ml-2 text-gray-300 hover:text-red-500 opacity-0 group-hover/skill:opacity-100 transition-opacity"
                    title="Delete Skill">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  </button>

                  <!-- Hover Preview (Tooltip style could go here) -->
                </div>
              </div>
            </div>
          </div>
      </div>
    </main>
    <Footer />

    <!-- Модальное окно о завершении пробного периода или необходимости авторизации -->
    <Modal :is-open="showTrialEndedModal"
      :title="trialQuestions.isTrialQuestionsExhausted.value ? 'Сынақ кезеңі аяқталды' : 'Авторизация қажет'"
      :show-close="true" @close="showTrialEndedModal = false">
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
    <Modal :is-open="showDeleteModal" title="Тестті жою" :show-close="true" @close="showDeleteModal = false">
      <template #content>
        <div class="space-y-4">
          <p class="text-gray-700">
            Сіз шынымен де <strong>"{{ skillToDelete?.title }}"</strong> тестін жойғыңыз келе ме?
          </p>
          <p class="text-sm text-red-600 flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
            Бұл әрекетті қайтару мүмкін емес. Тестпен байланысты барлық деректер жойылады.
          </p>
        </div>
      </template>
      <template #actions>
        <Button @click="deleteSkill" variant="primary" :disabled="deletingSkillId !== null"
          :loading="deletingSkillId !== null" class="bg-red-600 hover:bg-red-700">
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
import ViewByToggle from '@/components/ui/ViewByToggle.vue'
import Button from '@/components/ui/Button.vue'
import Modal from '@/components/ui/Modal.vue'

interface Props {
  gradeId: string
}

interface Skill {
  id: number
  title: string
  code: string
  topic_id?: number | null
  topic_title?: string | null
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

const getKazakhGradeTitle = (gradeNumber: number) => {
  if (gradeNumber === -1) return 'Мектепалды даярлық'
  if (gradeNumber === 0) return 'Даярлық сынып'
  const mapping: Record<number, string> = {
    1: 'Бірінші',
    2: 'Екінші',
    3: 'Үшінші',
    4: 'Төртінші',
    5: 'Бесінші',
    6: 'Алтыншы',
    7: 'Жетінші',
    8: 'Сегізінші',
    9: 'Тоғызыншы',
    10: 'Оныншы',
    11: 'Он бірінші'
  }
  return `${mapping[gradeNumber] || gradeNumber} сынып`
}

const currentGradeTitle = computed(() => {
  return getKazakhGradeTitle(currentGradeId.value)
})
const showTrialEndedModal = ref(false)
const skillStats = ref<Map<number, { best_smartscore: number; last_smartscore: number; is_completed: boolean }>>(new Map())
const loadingStats = ref(false)
const showDeleteModal = ref(false)
const skillToDelete = ref<{ id: number; title: string } | null>(null)
const deletingSkillId = ref<number | null>(null)


const TRIAL_QUESTIONS_LIMIT = trialQuestions.TRIAL_QUESTIONS_LIMIT

// Grouped Skills for IXL Layout
const groupedSkills = computed(() => {
  const groups: Record<string, { id: number | string; title: string; skills: Skill[] }> = {}
  const otherSkills: Skill[] = []

  // 1. Group by Topic
  // 1. Group by Topic
  for (const skill of skills.value) {
    if (skill.topic_id && skill.topic_title) {
      if (!groups[skill.topic_id]) {
        groups[skill.topic_id] = {
          id: skill.topic_id,
          title: skill.topic_title,
          skills: []
        }
      }
      // Use non-null assertion or check existence (we just created it if missing)
      if (skill.topic_id != null && groups[skill.topic_id]) {
        groups[skill.topic_id]!.skills.push(skill)
      }
    } else {
      otherSkills.push(skill)
    }
  }

  // 2. Sort Topics (by ID or Title) and Assign Letters
  const sortedGroups = Object.values(groups).sort((a, b) => a.title.localeCompare(b.title))

  // Add "Other" group if needed
  if (otherSkills.length > 0) {
    sortedGroups.push({
      id: 'other',
      title: 'Common Skills',
      skills: otherSkills
    })
  }

  // 3. Map to Final Structure with Letters
  return sortedGroups.map((group, index) => {
    // Generate Letter: A, B, C... Z, AA, AB...
    const letter = index < 26
      ? String.fromCharCode(65 + index)
      : String.fromCharCode(65 + Math.floor(index / 26) - 1) + String.fromCharCode(65 + (index % 26))

    // Sort skills within group (by ID or difficulty code naturally)
    const sortedSkills = group.skills.sort((a, b) => {
        // Try to sort by code tail number if available e.g. A.1, A.2
        return a.code.localeCompare(b.code, undefined, { numeric: true })
    })

    return {
      ...group,
      letter,
      skills: sortedSkills
    }
  })
})

// Название текущего класса (удалено дублирование)

// Переход к другому классу
const navigateToGrade = (gradeNumber: number) => {
  if (currentGradeId.value === gradeNumber) return
  currentGradeId.value = gradeNumber
  router.push({ name: 'class', params: { gradeId: gradeNumber } })
  // Всегда загружаем с force=true при переключении класса, чтобы получить актуальные данные
  loadSkillsForGrade(gradeNumber, true)
}

// Цвета для классов (чередуются)
// Цвета для классов (IXL colors)
const getGradeColor = (index: number): string => {
  const colors = [
    '#00A7FA', // Kindergarten (Blue)
    '#70B62C', // 1st (Green)
    '#E05206', // 2nd (Orange)
    '#009DD9', // 3rd (Blue)
    '#913D88', // 4th (Purple)
    '#F59E0B', // 5th (Yellow)
    '#F26622', // 6th (Orange-Red)
    '#00B388', // 7th (Teal)
    '#D91E18', // 8th (Red)
  ]
  return colors[index % colors.length] || '#3B82F6'
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
      best_smartscore: Number(stats.best_smartscore || 0),
      last_smartscore: Number(stats.last_smartscore || 0),
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
  const deletedSkillId = skillToDelete.value.id

  try {
    await adminApi.deleteSkill(deletedSkillId)

    // Закрываем модальное окно
    showDeleteModal.value = false
    skillToDelete.value = null

    // Удаляем из store сразу (оптимистичное обновление)
    // Это обновление UI будет мгновенным
    catalogStore.removeSkillFromCache(deletedSkillId)
    skillStats.value.delete(deletedSkillId)

    // Принудительно очищаем кэш запросов, чтобы при следующем заходе данные обновились
    // Но НЕ вызываем перезагрузку прямо сейчас, чтобы избежать race condition (когда база еще не обновилась)
    // catalogStore.clearSkillsCache() НЕ вызываем, так как removeSkillFromCache уже чистит конкретные записи

  } catch (err: any) {
    console.error('Failed to delete skill:', err)
    const status = err.response?.status
    const errorData = err.response?.data

    // Если навык уже удален (404), это не критическая ошибка
    if (status === 404) {
      // Удаляем из store и закрываем модалку
      catalogStore.removeSkillFromCache(deletedSkillId)
      skillStats.value.delete(deletedSkillId)
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

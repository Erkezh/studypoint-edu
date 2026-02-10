<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8 max-w-5xl">
      <div class="mb-6">
        <h1 class="text-3xl font-bold mb-2">Навык қосу (Генератор)</h1>
        <p class="text-gray-600">
          Мұнда сіз код-генераторды кірістіре аласыз. Генератор динамикалық түрде тапсырмалар жасайды.
        </p>
      </div>

      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {{ error }}
      </div>

      <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
        {{ successMessage }}
      </div>

      <!-- Инструкция -->
      <div class="bg-blue-50 border-l-4 border-blue-400 p-6 mb-6 rounded">
        <h2 class="text-xl font-semibold text-blue-800 mb-3 flex items-center gap-2">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
          Нұсқаулық
        </h2>
        <div class="space-y-3 text-gray-700">
          <div class="bg-white p-4 rounded border border-blue-200">
            <p class="font-semibold text-blue-900 mb-2 flex items-center gap-2">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              Генератор қалай жұмыс істейді:
            </p>
            <ol class="list-decimal list-inside space-y-1 ml-2">
              <li>Сіз код-генераторды кірістіресіз</li>
              <li>Генератор әр сұрақ үшін жаңа тапсырмалар жасайды</li>
              <li>Тапсырмалар базада сақталмайды - олар динамикалық түрде жасалады</li>
              <li>Жауаптар генератор логикасы арқылы тексеріледі</li>
            </ol>
          </div>
          <div class="bg-green-50 p-3 rounded border border-green-200">
            <p class="text-sm text-green-800 flex items-center gap-1.5">
              <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <strong>Важно:</strong> Генератор должен быть написан на <strong>Python</strong>!
              Функция <code>generate(metadata)</code> должна возвращать словарь (dict) с полями:
              <code>prompt</code>, <code>type</code>, <code>data</code>, <code>correct_answer</code>,
              <code>explanation</code> (опционально).
            </p>
          </div>
        </div>
      </div>

      <!-- Форма создания навыка с генератором -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-semibold mb-6">Жаңа навык қосу</h2>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Название навыка -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Навык атауы <span class="text-red-500">*</span>
            </label>
            <input v-model="formData.title" type="text" required
              class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="Мысалы: Разрядтар" />
          </div>

          <!-- Предмет (только Математика) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Пән <span class="text-red-500">*</span>
            </label>
            <div class="w-full p-3 border-2 border-gray-200 rounded-lg bg-gray-50 text-gray-700">
              Математика
            </div>
            <input v-model.number="formData.subject_id" type="hidden" />
          </div>

          <!-- Класс -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Сынып <span class="text-red-500">*</span>
            </label>
            <select v-model.number="formData.grade_id" required
              class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none">
              <option value="">Сынып таңдаңыз</option>
              <option v-for="grade in grades" :key="grade.id" :value="grade.id">
                {{ grade.title }}
              </option>
            </select>
          </div>

          <!-- Тақырып (Topic) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Тақырып (категория)
            </label>
            <select v-model="formData.topic_id"
              class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none">
              <option :value="null">Тақырып таңдаңыз (міндетті емес)</option>
              <option v-for="topic in topicsList" :key="topic.id" :value="topic.id">
                {{ topic.icon }} {{ topic.title }}
              </option>
            </select>
            <p class="text-xs text-gray-500 mt-1">Навықты категорияға топтастыру үшін тақырып таңдаңыз</p>
          </div>

          <!-- Код генератора -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Код генератора <span class="text-red-500">*</span>
            </label>
            <div class="bg-green-50 border-2 border-green-300 rounded-lg p-4 mb-2">
              <p class="text-sm text-green-800 font-medium mb-2 flex items-center gap-2">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                Формат (Python код):
              </p>
              <pre class="text-xs text-green-700 bg-white p-2 rounded overflow-x-auto"><code>def generate(metadata):
    # Генерируем задачу
    import random

    # Пример: генерация простой задачи на сложение
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    answer = a + b

    return {
        "prompt": f"Сколько будет {a} + {b}?",
        "type": "MCQ",  # или "NUMERIC", "TEXT", "MULTI_SELECT"
        "data": {
            "choices": [
                {"id": "A", "text": str(answer)},
                {"id": "B", "text": str(answer + 1)},
                {"id": "C", "text": str(answer - 1)},
                {"id": "D", "text": str(answer + 2)}
            ]
        },
        "correct_answer": {"answer": "A"},
        "explanation": f"{a} + {b} = {answer}"
    }</code></pre>
            </div>
            <textarea v-model="formData.generator_code" required rows="20"
              class="w-full p-4 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none font-mono text-xs"
              placeholder="Мұнда генератор кодты кірістіріңіз..."></textarea>
            <p class="text-xs text-gray-500 mt-1 flex items-center gap-1.5">
              <svg class="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
              <strong>Важно:</strong> Генератор должен быть написан на <strong>Python</strong>, а не на JavaScript!
              Функция <code>generate(metadata)</code> должна возвращать словарь с полями:
              <code>prompt</code>, <code>type</code>, <code>data</code>, <code>correct_answer</code>,
              <code>explanation</code> (опционально).
            </p>
          </div>

          <!-- Метаданные генератора (опционально) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Метаданные генератора (JSON, опционально)
            </label>
            <textarea v-model="generatorMetadataJson" rows="4"
              class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none font-mono text-sm"
              placeholder='{"min": 1, "max": 100, ...}'></textarea>
            <p class="text-xs text-gray-500 mt-1">Параметры для генератора (если нужны)</p>
          </div>

          <!-- Описание -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Сипаттама
            </label>
            <textarea v-model="formData.description" rows="3"
              class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="Навык сипаттамасы"></textarea>
          </div>

          <!-- Кнопки -->
          <div class="flex gap-4 pt-4">
            <Button type="submit" variant="primary" :loading="submitting" class="px-8 flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
              Сақтау
            </Button>
            <Button type="button" variant="outline" @click="resetForm" class="flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
              Тазалау
            </Button>
          </div>
        </form>
      </div>

      <!-- Список навыков с возможностью удаления -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold">Барлық тақырыптар</h2>
          <Button @click="loadSkills" variant="outline" :loading="loadingSkills" class="flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
            Жаңарту
          </Button>
        </div>

        <div v-if="loadingSkills" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p class="mt-2 text-gray-600">Жүктелуде...</p>
        </div>

        <div v-else-if="skillsList.length === 0" class="text-center py-8 text-gray-500">
          Тақырыптар табылмады
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Атауы
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Код
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Сынып
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Қиындық
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Әрекеттер
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="skill in skillsList" :key="skill.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ skill.id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ skill.title }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ skill.code }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ getGradeName(skill.grade_id) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ skill.difficulty }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Button @click="confirmDelete(skill)" variant="outline"
                    class="text-red-600 hover:text-red-800 hover:bg-red-50 flex items-center gap-1" :loading="deletingSkillId === skill.id">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    Жою
                  </Button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
    <Footer />

    <!-- Модальное окно подтверждения удаления -->
    <Modal :isOpen="!!skillToDelete" @close="skillToDelete = null" title="Тақырыпты жою" :showClose="true">
      <template #content>
        <p class="text-gray-700 mb-4">
          Сіз шынымен "<strong>{{ skillToDelete?.title }}</strong>" тақырыбын жойғыңыз келе ме?
        </p>
        <p class="text-sm text-red-600 mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
          Бұл әрекетті қайтару мүмкін емес! Тақырыппен байланысты барлық деректер жойылады.
        </p>
      </template>
      <template #actions>
        <Button v-if="skillToDelete" @click="handleDelete" variant="primary"
          :loading="deletingSkillId === skillToDelete.id" class="bg-red-600 hover:bg-red-700">
          Иә, жою
        </Button>
        <Button @click="skillToDelete = null" variant="outline">
          Болдырмау
        </Button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCatalogStore } from '@/stores/catalog'
import { adminApi, type SkillListItem, type TopicListItem } from '@/api/admin'
import { useRouter } from 'vue-router'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import Modal from '@/components/ui/Modal.vue'

const authStore = useAuthStore()
const catalogStore = useCatalogStore()
const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const generatorMetadataJson = ref('{}')

const subjects = ref<any[]>([])
const grades = ref<any[]>([])
const mathSubjectId = ref<number>(0)

const skillsList = ref<SkillListItem[]>([])
const loadingSkills = ref(false)
const skillToDelete = ref<SkillListItem | null>(null)
const deletingSkillId = ref<number | null>(null)
const topicsList = ref<TopicListItem[]>([])

const formData = ref({
  title: '',
  subject_id: mathSubjectId.value, // Сохраняем выбранную математику
  grade_id: 0,
  topic_id: null as number | null,
  code: '',
  description: '',
  generator_code: '',
  generator_metadata: {},
  difficulty: 1,
  is_published: true,
})

const resetForm = () => {
  formData.value = {
    title: '',
    subject_id: mathSubjectId.value, // Сохраняем выбранную математику
    grade_id: 0,
    topic_id: null,
    code: '',
    description: '',
    generator_code: '',
    generator_metadata: {},
    difficulty: 1,
    is_published: true,
  }
  generatorMetadataJson.value = '{}'
  error.value = null
  successMessage.value = null
}

const handleSubmit = async () => {
  submitting.value = true
  error.value = null
  successMessage.value = null

  // Проверяем авторизацию
  if (!authStore.isAuthenticated || authStore.user?.role !== 'ADMIN') {
    error.value = 'Тек әкімшілер навык қоса алады!'
    submitting.value = false
    return
  }

  // Проверяем обязательные поля
  if (!formData.value.title || !formData.value.generator_code) {
    error.value = 'Навык атауы және код генератора міндетті!'
    submitting.value = false
    return
  }

  if (!formData.value.subject_id || !formData.value.grade_id) {
    error.value = 'Пән және сынып таңдау міндетті!'
    submitting.value = false
    return
  }

  try {
    // Парсим метаданные
    let metadata = {}
    if (generatorMetadataJson.value.trim() && generatorMetadataJson.value !== '{}') {
      try {
        metadata = JSON.parse(generatorMetadataJson.value)
      } catch (e) {
        error.value = 'Метаданные JSON форматында болуы керек'
        submitting.value = false
        return
      }
    }

    // Генерируем уникальный код навыка (максимум 16 символов)
    const timestamp = Date.now().toString().slice(-8) // Последние 8 цифр
    const skillCode = `GEN${timestamp}` // Максимум 11 символов

    console.log('Creating skill with data:', {
      subject_id: formData.value.subject_id,
      grade_id: formData.value.grade_id,
      code: skillCode,
      title: formData.value.title,
      description: formData.value.description || '',
      generator_code: formData.value.generator_code ? formData.value.generator_code.substring(0, 100) + '...' : '',
      generator_metadata: metadata,
      difficulty: formData.value.difficulty,
      is_published: formData.value.is_published,
    })

    await adminApi.createSkill({
      subject_id: formData.value.subject_id,
      grade_id: formData.value.grade_id,
      topic_id: formData.value.topic_id,
      code: skillCode,
      title: formData.value.title,
      description: formData.value.description || '',
      generator_code: formData.value.generator_code,
      generator_metadata: metadata,
      difficulty: formData.value.difficulty,
      is_published: formData.value.is_published,
    })

    successMessage.value = 'Навык с генератором успешно создан!'
    resetForm()
    // Обновляем список навыков
    await loadSkills()
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err: any) {
    console.error('Failed to create skill:', err)
    console.error('Error details:', {
      status: err.response?.status,
      statusText: err.response?.statusText,
      data: err.response?.data,
      message: err.message,
    })

    if (err.response?.status === 401) {
      error.value = 'Авторизация қатесі. Жүйеге қайта кіріңіз.'
      // Редирект на логин
      router.push({ name: 'login' })
    } else if (err.response?.status === 422) {
      const validationErrors = err.response?.data?.detail || err.response?.data?.error?.details
      if (Array.isArray(validationErrors)) {
        const errorMessages = validationErrors.map((e: any) =>
          `${e.loc?.join('.')}: ${e.msg}`
        ).join(', ')
        error.value = `Валидация қатесі: ${errorMessages}`
      } else {
        error.value = err.response?.data?.error?.message || err.response?.data?.message || 'Деректерді валидациялау қатесі'
      }
    } else {
      const errorMsg = err.response?.data?.error?.message || err.response?.data?.message || err.message
      error.value = errorMsg || 'Навык қосу кезінде қате пайда болды.'
    }
  } finally {
    submitting.value = false
  }
}

const loadSkills = async () => {
  loadingSkills.value = true
  try {
    const response = await adminApi.listSkills(1, 200)
    if (response.data) {
      skillsList.value = response.data
    }
  } catch (err: any) {
    console.error('Failed to load skills:', err)
    if (err.response?.status === 401) {
      router.push({ name: 'login' })
    } else {
      error.value = 'Тақырыптарды жүктеу кезінде қате пайда болды.'
    }
  } finally {
    loadingSkills.value = false
  }
}

const getGradeName = (gradeId: number): string => {
  const grade = grades.value.find(g => g.id === gradeId)
  return grade ? `${grade.number} ${grade.title}` : `ID: ${gradeId}`
}

const confirmDelete = (skill: SkillListItem) => {
  skillToDelete.value = skill
}

const handleDelete = async () => {
  if (!skillToDelete.value) return

  deletingSkillId.value = skillToDelete.value.id
  try {
    await adminApi.deleteSkill(skillToDelete.value.id)
    successMessage.value = `Тақырып "${skillToDelete.value.title}" сәтті жойылды!`
    skillToDelete.value = null
    await loadSkills()
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err: any) {
    console.error('Failed to delete skill:', err)
    if (err.response?.status === 401) {
      error.value = 'Авторизация қатесі. Жүйеге қайта кіріңіз.'
      router.push({ name: 'login' })
    } else if (err.response?.status === 404) {
      error.value = 'Тақырып табылмады.'
    } else {
      error.value = err.response?.data?.error?.message || err.message || 'Тақырыпты жою кезінде қате пайда болды.'
    }
    skillToDelete.value = null
  } finally {
    deletingSkillId.value = null
  }
}

onMounted(async () => {
  try {
    subjects.value = await catalogStore.getSubjects()
    grades.value = await catalogStore.getGrades()

    // Загружаем список тем
    try {
      const topicsResponse = await adminApi.listTopics()
      topicsList.value = topicsResponse.data || []
    } catch (e) {
      console.error('Failed to load topics:', e)
    }

    // Автоматически выбираем Математику (первый предмет или по названию)
    const mathSubject = subjects.value.find(s =>
      s.title?.toLowerCase().includes('math') ||
      s.title?.toLowerCase().includes('математика') ||
      s.slug?.toLowerCase().includes('math')
    ) || subjects.value[0]

    if (mathSubject) {
      mathSubjectId.value = mathSubject.id
      formData.value.subject_id = mathSubject.id
    }

    // Загружаем список навыков
    await loadSkills()
  } catch (err) {
    console.error('Failed to load subjects/grades:', err)
  }
})
</script>

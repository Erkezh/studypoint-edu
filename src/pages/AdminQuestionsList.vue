<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8 max-w-7xl">
      <div class="mb-6">
        <h1 class="text-3xl font-bold mb-2">Сұрақтарды басқару</h1>
        <p class="text-gray-600">Барлық сұрақтарды көру және жою</p>
      </div>

      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {{ error }}
      </div>

      <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
        {{ successMessage }}
      </div>

      <!-- Фильтры -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Навык ID (фильтр)
            </label>
            <input
              v-model.number="filters.skill_id"
              type="number"
              class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="Барлығы (бос қалдырыңыз)"
            />
          </div>
          <div class="flex items-end">
            <Button @click="loadQuestions" variant="primary" :loading="loading">
              🔍 Іздеу
            </Button>
            <Button @click="resetFilters" variant="outline" class="ml-2">
              🔄 Тазалау
            </Button>
          </div>
        </div>
      </div>

      <!-- Список вопросов -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold">Сұрақтар тізімі</h2>
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-600">
              Барлығы: {{ totalQuestions }}
            </span>
            <Button @click="loadQuestions" variant="outline" :loading="loading">
              🔄 Жаңарту
            </Button>
          </div>
        </div>

        <div v-if="loading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p class="mt-2 text-gray-600">Жүктелуде...</p>
        </div>

        <div v-else-if="questionsList.length === 0" class="text-center py-8 text-gray-500">
          Сұрақтар табылмады
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Навык ID
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Тип
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Сұрақ
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Деңгей
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Әрекеттер
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="question in questionsList" :key="question.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ question.id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ question.skill_id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span class="px-2 py-1 text-xs font-medium rounded-full"
                    :class="{
                      'bg-blue-100 text-blue-800': question.type === 'MCQ',
                      'bg-green-100 text-green-800': question.type === 'NUMERIC',
                      'bg-purple-100 text-purple-800': question.type === 'TEXT',
                      'bg-yellow-100 text-yellow-800': question.type === 'MULTI_SELECT',
                      'bg-red-100 text-red-800': question.type === 'INTERACTIVE',
                      'bg-indigo-100 text-indigo-800': question.type === 'PLUGIN',
                    }">
                    {{ question.type }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-900 max-w-md">
                  <div class="truncate" :title="question.prompt">
                    {{ question.prompt || '(Сұрақ жоқ)' }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ question.level }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Button
                    @click="confirmDelete(question)"
                    variant="outline"
                    class="text-red-600 hover:text-red-800 hover:bg-red-50"
                    :loading="deletingQuestionId === question.id"
                  >
                    🗑️ Жою
                  </Button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Пагинация -->
        <div v-if="totalQuestions > pageSize" class="mt-6 flex items-center justify-between">
          <div class="text-sm text-gray-600">
            Бет {{ currentPage }} / {{ totalPages }}
          </div>
          <div class="flex gap-2">
            <Button
              @click="currentPage = Math.max(1, currentPage - 1); loadQuestions()"
              variant="outline"
              :disabled="currentPage === 1"
            >
              ← Алдыңғы
            </Button>
            <Button
              @click="currentPage = Math.min(totalPages, currentPage + 1); loadQuestions()"
              variant="outline"
              :disabled="currentPage === totalPages"
            >
              Келесі →
            </Button>
          </div>
        </div>
      </div>
    </main>
    <Footer />

    <!-- Модальное окно подтверждения удаления -->
    <Modal
      :isOpen="!!questionToDelete"
      @close="questionToDelete = null"
      title="Сұрақты жою"
      :showClose="true"
    >
      <template #content>
        <p class="text-gray-700 mb-4">
          Сіз шынымен бұл сұрақты жойғыңыз келе ме?
        </p>
        <div v-if="questionToDelete" class="bg-gray-50 p-4 rounded mb-4">
          <p class="text-sm text-gray-600 mb-1"><strong>ID:</strong> {{ questionToDelete.id }}</p>
          <p class="text-sm text-gray-600 mb-1"><strong>Тип:</strong> {{ questionToDelete.type }}</p>
          <p class="text-sm text-gray-600"><strong>Сұрақ:</strong> {{ questionToDelete.prompt || '(Сұрақ жоқ)' }}</p>
        </div>
        <p class="text-sm text-red-600 mb-4">
          ⚠️ Бұл әрекетті қайтару мүмкін емес! Сұрақ толығымен жойылады.
        </p>
      </template>
      <template #actions>
        <Button
          v-if="questionToDelete"
          @click="handleDelete"
          variant="primary"
          :loading="deletingQuestionId === questionToDelete.id"
          class="bg-red-600 hover:bg-red-700"
        >
          Иә, жою
        </Button>
        <Button @click="questionToDelete = null" variant="outline">
          Болдырмау
        </Button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { adminApi, type QuestionListItem } from '@/api/admin'
import { useRouter } from 'vue-router'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import Modal from '@/components/ui/Modal.vue'

const authStore = useAuthStore()
const router = useRouter()

const loading = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

const questionsList = ref<QuestionListItem[]>([])
const totalQuestions = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)

const questionToDelete = ref<QuestionListItem | null>(null)
const deletingQuestionId = ref<number | null>(null)

const filters = ref({
  skill_id: undefined as number | undefined,
})

const totalPages = computed(() => {
  return Math.ceil(totalQuestions.value / pageSize.value)
})

const loadQuestions = async () => {
  loading.value = true
  error.value = null
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value,
    }

    if (filters.value.skill_id) {
      params.skill_id = filters.value.skill_id
    }

    const response = await adminApi.listQuestions(params)
    if (response.data) {
      questionsList.value = response.data
      // Получаем общее количество из meta, если доступно
      if (response.meta && 'total' in response.meta) {
        totalQuestions.value = response.meta.total as number
      } else {
        totalQuestions.value = response.data.length
      }
    }
  } catch (err: any) {
    console.error('Failed to load questions:', err)
    if (err.response?.status === 401) {
      error.value = 'Авторизация қатесі. Жүйеге қайта кіріңіз.'
      router.push({ name: 'login' })
    } else {
      error.value = err.response?.data?.error?.message || err.response?.data?.message || err.message || 'Сұрақтарды жүктеу кезінде қате пайда болды.'
    }
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    skill_id: undefined,
  }
  currentPage.value = 1
  loadQuestions()
}

const confirmDelete = (question: QuestionListItem) => {
  questionToDelete.value = question
}

const handleDelete = async () => {
  if (!questionToDelete.value) return

  deletingQuestionId.value = questionToDelete.value.id
  try {
    await adminApi.deleteQuestion(questionToDelete.value.id)
    successMessage.value = `Сұрақ ID ${questionToDelete.value.id} сәтті жойылды!`
    questionToDelete.value = null
    await loadQuestions()
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err: any) {
    console.error('Failed to delete question:', err)
    if (err.response?.status === 401) {
      error.value = 'Авторизация қатесі. Жүйеге қайта кіріңіз.'
      router.push({ name: 'login' })
    } else if (err.response?.status === 404) {
      error.value = 'Сұрақ табылмады.'
    } else {
      error.value = err.response?.data?.error?.message || err.response?.data?.message || err.message || 'Сұрақты жою кезінде қате пайда болды.'
    }
    questionToDelete.value = null
  } finally {
    deletingQuestionId.value = null
  }
}

onMounted(async () => {
  // Проверка прав доступа
  if (!authStore.isAuthenticated || authStore.user?.role !== 'ADMIN') {
    router.push({ name: 'home' })
    return
  }

  await loadQuestions()
})
</script>

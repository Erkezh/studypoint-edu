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
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Навык атауы бойынша іздеу
            </label>
            <input
              v-model="filters.search"
              type="text"
              class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="Навык атауын жазыңыз..."
              @keyup.enter="loadQuestions"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Навык ID
            </label>
            <input
              v-model.number="filters.skill_id"
              type="number"
              class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="ID нөмірі"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Сұрыптау
            </label>
            <select
              v-model="filters.sort_order"
              class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
              @change="loadQuestions"
            >
              <option value="desc">Жаңалары алдымен</option>
              <option value="asc">Ескілері алдымен</option>
            </select>
          </div>
          <div class="flex items-end gap-2">
            <Button @click="loadQuestions" variant="primary" :loading="loading" class="flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
              Іздеу
            </Button>
            <Button @click="resetFilters" variant="outline" class="flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
              Тазалау
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
            <Button @click="loadQuestions" variant="outline" :loading="loading" class="flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
              Жаңарту
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
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Навык
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Тип
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Сұрақ
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Деңгей
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Құрылған күні
                </th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Әрекеттер
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="question in questionsList" :key="question.id">
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ question.id }}
                </td>
                <td class="px-4 py-4 text-sm text-gray-500 max-w-xs">
                  <div class="truncate" :title="question.skill_title || `ID: ${question.skill_id}`">
                    <span class="text-gray-400 text-xs">#{{ question.skill_id }}</span>
                    {{ question.skill_title || '' }}
                  </div>
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
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
                <td class="px-4 py-4 text-sm text-gray-900 max-w-xs">
                  <div class="truncate" :title="question.prompt">
                    {{ question.prompt || '(Сұрақ жоқ)' }}
                  </div>
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ question.level }}
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-400">
                  {{ formatDate(question.created_at) }}
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Button
                    @click="confirmDelete(question)"
                    variant="outline"
                    :loading="deletingQuestionId === question.id"
                    class="text-red-600 hover:text-red-800 hover:bg-red-50 flex items-center gap-1"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    Жою
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
        <p class="text-sm text-red-600 mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
          Бұл әрекетті қайтару мүмкін емес! Сұрақ толығымен жойылады.
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
  search: '' as string,
  sort_order: 'desc' as 'asc' | 'desc',
})

const totalPages = computed(() => {
  return Math.ceil(totalQuestions.value / pageSize.value)
})

const formatDate = (dateStr: string | null | undefined): string => {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('kk-KZ', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return '-'
  }
}

const loadQuestions = async () => {
  loading.value = true
  error.value = null
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value,
      sort_order: filters.value.sort_order,
    }

    if (filters.value.skill_id) {
      params.skill_id = filters.value.skill_id
    }

    if (filters.value.search && filters.value.search.trim()) {
      params.search = filters.value.search.trim()
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
    search: '',
    sort_order: 'desc',
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

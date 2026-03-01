<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8 max-w-4xl">
      <!-- Заголовок -->
      <div class="mb-6 flex items-center gap-3">
        <router-link to="/admin" class="text-gray-400 hover:text-gray-600 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
        </router-link>
        <svg class="w-7 h-7 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-2 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Сыныптар</h1>
          <p class="text-sm text-gray-500">Сыныптарды қосу, өңдеу және жою</p>
        </div>
      </div>

      <!-- Уведомления -->
      <div v-if="error" class="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-lg mb-4 flex items-center gap-2">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        {{ error }}
      </div>
      <div v-if="successMessage" class="bg-green-100 border border-green-300 text-green-700 px-4 py-3 rounded-lg mb-4 flex items-center gap-2">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
        {{ successMessage }}
      </div>

      <!-- Форма добавления -->
      <section class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <svg class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
            Жаңа сынып қосу
          </h2>
          <button @click="showAddForm = !showAddForm" class="text-sm text-gray-500 hover:text-indigo-600 transition-colors font-medium">
            {{ showAddForm ? 'Жасыру' : 'Көрсету' }}
          </button>
        </div>
        <div v-if="showAddForm">
          <form @submit.prevent="handleCreate" class="flex flex-wrap gap-3 items-end">
            <div class="w-28">
              <label class="block text-xs font-medium text-gray-600 mb-1">Реті *</label>
              <input
                v-model.number="addForm.number"
                type="number"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 outline-none"
                placeholder="5"
              />
            </div>
            <div class="w-24">
              <label class="block text-xs font-medium text-gray-600 mb-1">Белгісі *</label>
              <input
                v-model="addForm.label"
                type="text"
                required
                maxlength="8"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 outline-none"
                placeholder="K"
              />
            </div>
            <div class="flex-1 min-w-[160px]">
              <label class="block text-xs font-medium text-gray-600 mb-1">Атауы *</label>
              <input
                v-model="addForm.title"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 outline-none"
                placeholder="5-сынып"
              />
            </div>
            <button
              type="submit"
              :disabled="creating"
              class="flex items-center gap-1.5 px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
              {{ creating ? '...' : 'Қосу' }}
            </button>
          </form>
          <p class="text-xs text-gray-400 mt-2">«Реті» — сұрыптау үшін сан. «Белгісі» — кружочкада көрінетін символ.</p>
        </div>
      </section>

      <!-- Список классов -->
      <section class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-lg font-semibold text-gray-800">Барлық сыныптар</h2>
          <span class="text-sm text-gray-400">{{ gradesList.length }} сынып</span>
        </div>

        <!-- Загрузка -->
        <div v-if="loading" class="flex justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>

        <!-- Пусто -->
        <div v-else-if="gradesList.length === 0" class="text-center py-12 text-gray-400">
          <svg class="w-12 h-12 mx-auto mb-3 text-gray-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-2 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
          <p>Сыныптар жоқ. Жаңа сынып қосыңыз!</p>
        </div>

        <!-- Список -->
        <div v-else class="space-y-2">
          <div
            v-for="grade in gradesList"
            :key="grade.id"
            class="rounded-lg border border-gray-100 hover:border-indigo-100 transition-colors"
          >
            <!-- Обычный вид -->
            <div v-if="editingId !== grade.id" class="flex items-center justify-between px-4 py-3">
              <div class="flex items-center gap-3">
                <span class="inline-flex items-center justify-center w-9 h-9 rounded-full bg-indigo-100 text-indigo-700 font-bold text-sm shrink-0">
                  {{ grade.label || grade.number }}
                </span>
                <div>
                  <span class="font-medium text-gray-900">{{ grade.title }}</span>
                  <span class="text-xs text-gray-400 ml-2">Реті: {{ grade.number }}</span>
                  <span class="text-xs text-indigo-500 ml-2">Белгісі: {{ grade.label }}</span>
                </div>
              </div>
              <div class="flex gap-2 shrink-0">
                <button
                  @click="startEdit(grade)"
                  class="flex items-center gap-1 text-xs px-3 py-1.5 rounded border border-gray-200 hover:bg-indigo-50 hover:border-indigo-300 transition-colors text-gray-600 hover:text-indigo-700"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                  Өңдеу
                </button>
                <button
                  @click="handleDelete(grade)"
                  :disabled="deletingId === grade.id"
                  class="flex items-center gap-1 text-xs px-3 py-1.5 rounded border border-red-200 hover:bg-red-50 transition-colors text-red-600 disabled:opacity-50"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  {{ deletingId === grade.id ? '...' : 'Жою' }}
                </button>
              </div>
            </div>

            <!-- Режим редактирования (inline) -->
            <div v-else class="px-4 py-3 bg-indigo-50 border-t border-indigo-100 rounded-lg">
              <form @submit.prevent="handleUpdate(grade.id)" class="flex flex-wrap gap-3 items-end">
                <div class="w-28">
                  <label class="block text-xs font-medium text-indigo-700 mb-1">Реті *</label>
                  <input
                    v-model.number="editForm.number"
                    type="number"
                    required
                    class="w-full px-3 py-2 border border-indigo-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-400 outline-none bg-white"
                  />
                </div>
                <div class="w-24">
                  <label class="block text-xs font-medium text-indigo-700 mb-1">Белгісі *</label>
                  <input
                    v-model="editForm.label"
                    type="text"
                    required
                    maxlength="8"
                    class="w-full px-3 py-2 border border-indigo-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-400 outline-none bg-white"
                    placeholder="K"
                  />
                </div>
                <div class="flex-1 min-w-[160px]">
                  <label class="block text-xs font-medium text-indigo-700 mb-1">Атауы *</label>
                  <input
                    v-model="editForm.title"
                    type="text"
                    required
                    class="w-full px-3 py-2 border border-indigo-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-400 outline-none bg-white"
                  />
                </div>
                <div class="flex gap-2">
                  <button
                    type="submit"
                    :disabled="saving"
                    class="flex items-center gap-1 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                    {{ saving ? '...' : 'Сақтау' }}
                  </button>
                  <button
                    type="button"
                    @click="cancelEdit"
                    class="flex items-center gap-1 px-4 py-2 border border-gray-300 text-gray-600 rounded-lg text-sm hover:bg-gray-50 transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                    Болдырмау
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Header from '@/components/layout/Header.vue'
import { adminApi, type GradeListItem } from '@/api/admin'

const authStore = useAuthStore()
const router = useRouter()

const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const loading = ref(false)
const creating = ref(false)
const saving = ref(false)
const deletingId = ref<number | null>(null)
const showAddForm = ref(true)

const editingId = ref<number | null>(null)
const gradesList = ref<GradeListItem[]>([])

const addForm = ref({ number: '' as number | '', label: '', title: '' })
const editForm = ref({ number: 0, label: '', title: '' })

// --- Helpers ---

const showSuccess = (msg: string) => {
  successMessage.value = msg
  setTimeout(() => { successMessage.value = null }, 3000)
}

const showError = (e: unknown, fallback: string) => {
  const err = e as { response?: { data?: { detail?: string } } }
  error.value = err.response?.data?.detail || fallback
}

// --- Load ---

const loadGrades = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await adminApi.listGrades()
    gradesList.value = ((res.data || []) as GradeListItem[]).sort((a, b) => a.number - b.number)
  } catch (e) {
    showError(e, 'Сыныптарды жүктеу қатесі')
  } finally {
    loading.value = false
  }
}

// --- Create ---

const handleCreate = async () => {
  if (addForm.value.number === '' || !addForm.value.title) return
  creating.value = true
  error.value = null
  try {
    await adminApi.createGrade({
      number: addForm.value.number as number,
      label: addForm.value.label,
      title: addForm.value.title,
      description: '',
    })
    addForm.value = { number: '', label: '', title: '' }
    showSuccess('Сынып сәтті қосылды!')
    await loadGrades()
  } catch (e) {
    showError(e, 'Сынып қосу қатесі')
  } finally {
    creating.value = false
  }
}

// --- Edit ---

const startEdit = (grade: GradeListItem) => {
  editingId.value = grade.id
  editForm.value = { number: grade.number, label: grade.label ?? '', title: grade.title }
}

const cancelEdit = () => {
  editingId.value = null
}

const handleUpdate = async (id: number) => {
  saving.value = true
  error.value = null
  try {
    await adminApi.updateGrade(id, {
      number: editForm.value.number,
      label: editForm.value.label,
      title: editForm.value.title,
    })
    editingId.value = null
    showSuccess('Сынып сәтті өзгертілді!')
    await loadGrades()
  } catch (e) {
    showError(e, 'Сынып өзгерту қатесі')
  } finally {
    saving.value = false
  }
}

// --- Delete ---

const handleDelete = async (grade: GradeListItem) => {
  if (!confirm(`"${grade.title}" сыныбын жойғыңыз келе ме?`)) return
  deletingId.value = grade.id
  error.value = null
  try {
    await adminApi.deleteGrade(grade.id)
    gradesList.value = gradesList.value.filter(g => g.id !== grade.id)
    showSuccess(`"${grade.title}" сыныбы жойылды`)
  } catch (e) {
    showError(e, 'Сынып жою қатесі')
  } finally {
    deletingId.value = null
  }
}

// --- Init ---

onMounted(async () => {
  if (!authStore.isAuthenticated || authStore.user?.role !== 'ADMIN') {
    router.push({ name: 'home' })
    return
  }
  await loadGrades()
})
</script>

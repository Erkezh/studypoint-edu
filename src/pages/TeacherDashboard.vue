<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <Header />
    <main class="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">

      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Roster</h1>
          <p class="text-sm text-gray-500 mt-1">Барлық оқушылардың логині мен құпиясөзі осында</p>
        </div>
        <button
          @click="showAddModal = true"
          class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Оқушы қосу
        </button>
      </div>

      <!-- Table Card -->
      <div class="bg-white rounded-xl shadow border border-gray-200 overflow-hidden">
        <!-- Loading -->
        <div v-if="loadingStudents" class="flex justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>

        <!-- Error -->
        <div v-else-if="studentsError" class="p-6 text-red-600 bg-red-50">{{ studentsError }}</div>

        <!-- Empty -->
        <div v-else-if="students.length === 0" class="p-12 text-center text-gray-400">
          <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          <p class="font-medium">Оқушылар жоқ</p>
          <p class="text-sm mt-1">«Оқушы қосу» түймесін басыңыз</p>
        </div>

        <!-- Roster Table -->
        <div v-else class="overflow-x-auto">
          <table class="min-w-full">
            <thead>
              <tr class="bg-blue-600 text-white text-sm">
                <th class="px-4 py-3 text-left font-semibold w-8">#</th>
                <th class="px-4 py-3 text-left font-semibold">Аты-жөні</th>
                <th class="px-4 py-3 text-left font-semibold">Сыныбы</th>
                <th class="px-4 py-3 text-left font-semibold">Логин (Username)</th>
                <th class="px-4 py-3 text-left font-semibold">Құпиясөз</th>
                <th class="px-4 py-3 text-left font-semibold w-36">Әрекет</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="(student, index) in students" :key="student.id" class="hover:bg-blue-50 transition-colors">
                <td class="px-4 py-3 text-sm text-gray-500">{{ index + 1 }}</td>
                <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ student.full_name }}</td>
                <td class="px-4 py-3 text-sm text-gray-600">{{ student.grade_level ? `${student.grade_level} сынып` : '—' }}</td>
                <td class="px-4 py-3">
                  <span
                    @click="copyToClipboard(student.username, student.id + '_u')"
                    class="font-mono text-sm text-blue-700 bg-blue-50 px-2 py-0.5 rounded cursor-pointer hover:bg-blue-100 select-all relative transition"
                    :title="'Кошіру үшін басыңыз'"
                  >
                    {{ student.username }}
                    <span v-if="copiedId === student.id + '_u'" class="absolute -top-7 left-1/2 -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-0.5 rounded whitespace-nowrap z-10">Көшірілді ✓</span>
                  </span>
                </td>
                <td class="px-4 py-3">
                  <span
                    v-if="student.password && student.password !== '—'"
                    @click="copyToClipboard(student.password!, student.id + '_p')"
                    class="font-mono text-sm text-green-700 bg-green-50 px-2 py-0.5 rounded cursor-pointer hover:bg-green-100 select-all relative transition"
                    :title="'Құпиясөзді кошіру'"
                  >
                    {{ student.password }}
                    <span v-if="copiedId === student.id + '_p'" class="absolute -top-7 left-1/2 -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-0.5 rounded whitespace-nowrap z-10">Көшірілді ✓</span>
                  </span>
                  <span v-else class="text-xs text-gray-400 italic">Тек жасағанда көрінеді</span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-3">
                    <button
                      @click="resetPassword(student)"
                      :disabled="resettingId === student.id"
                      class="text-xs text-blue-600 hover:text-blue-800 hover:underline disabled:opacity-50 transition"
                    >
                      {{ resettingId === student.id ? 'Жасалуда...' : 'Жаңа пароль' }}
                    </button>
                    <button
                      @click="confirmDelete(student)"
                      :disabled="deletingId === student.id"
                      class="text-xs text-red-500 hover:text-red-700 hover:underline disabled:opacity-50 transition"
                    >
                      {{ deletingId === student.id ? '...' : 'Өшіру' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <div class="px-4 py-3 text-xs text-gray-500 border-t border-gray-100 bg-gray-50">
            Барлығы {{ students.length }} оқушы
          </div>
        </div>
      </div>

      <!-- Reset error -->
      <div v-if="resetError" class="mt-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-2">{{ resetError }}</div>
    </main>
    <Footer />

    <!-- Add Student Modal -->
    <Modal :is-open="showAddModal" title="Жаңа оқушы қосу" :show-close="true" @close="showAddModal = false">
      <template #content>
        <form @submit.prevent="submitAddStudent" class="space-y-4">
          <div v-if="createError" class="text-sm text-red-600 bg-red-50 p-2 rounded">{{ createError }}</div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Аты (First Name)</label>
            <input v-model="form.firstName" type="text" required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border px-3 py-2">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Тегі (Last Name)</label>
            <input v-model="form.lastName" type="text" required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border px-3 py-2">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Сыныбы (Grade)</label>
            <select v-model="form.gradeId" required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border px-3 py-2">
              <option value="" disabled>Таңдаңыз</option>
              <option v-for="grade in grades" :key="grade.number" :value="grade.number">
                {{ grade.title || `${grade.number} сынып` }}
              </option>
            </select>
          </div>
        </form>
      </template>
      <template #actions>
        <Button @click="submitAddStudent" variant="primary" :disabled="creating" :loading="creating">Қосу</Button>
        <Button @click="showAddModal = false" variant="outline" :disabled="creating">Болдырмау</Button>
      </template>
    </Modal>

    <!-- Success Modal -->
    <Modal :is-open="showSuccessModal" title="Оқушы сәтті құрылды!" :show-close="false">
      <template #content>
        <div class="space-y-3">
          <p class="text-sm text-gray-600">Бұл мәліметтерді оқушыға беріңіз. Құпиясөзді тек осы жолы парақшада да көруге болады.</p>
          <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 font-mono text-sm space-y-2">
            <div class="flex justify-between">
              <span class="text-gray-500">Аты-жөні:</span>
              <span class="font-bold text-gray-900">{{ createdStudentData?.full_name }}</span>
            </div>
            <div class="flex justify-between border-t border-gray-200 pt-2">
              <span class="text-gray-500">Логин:</span>
              <span class="font-bold text-blue-600 select-all">{{ createdStudentData?.username }}</span>
            </div>
            <div class="flex justify-between border-t border-gray-200 pt-2">
              <span class="text-gray-500">Құпиясөз:</span>
              <span class="font-bold text-green-600 select-all">{{ createdStudentData?.password }}</span>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <Button @click="closeSuccessModal" variant="primary">Жабып, жалғастыру</Button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import Modal from '@/components/ui/Modal.vue'
import { useTeacherStore } from '@/stores/teacher'
import { teacherApi } from '@/api/teacher'
import type { StudentInfo } from '@/api/teacher'
import { useCatalogStore } from '@/stores/catalog'

const teacherStore = useTeacherStore()
const catalogStore = useCatalogStore()

const { students, loading: loadingStudents, error: studentsError } = storeToRefs(teacherStore)
const { grades } = storeToRefs(catalogStore)

const showAddModal = ref(false)
const showSuccessModal = ref(false)
const creating = ref(false)
const createError = ref('')
const resettingId = ref<string | null>(null)
const resetError = ref('')
const deletingId = ref<string | null>(null)
const copiedId = ref<string | null>(null)

const copyToClipboard = (text: string, id: string) => {
  navigator.clipboard.writeText(text).then(() => {
    copiedId.value = id
    setTimeout(() => { if (copiedId.value === id) copiedId.value = null }, 1500)
  })
}

const form = ref({ firstName: '', lastName: '', gradeId: '' as string | number })
const createdStudentData = ref<{ full_name: string, username: string, password: string } | null>(null)

onMounted(async () => {
  await teacherStore.fetchStudents()
  if (grades.value.length === 0) await catalogStore.getGrades()
})

const submitAddStudent = async () => {
  if (!form.value.firstName || !form.value.lastName || form.value.gradeId === '') {
    createError.value = 'Барлық өрістерді толтырыңыз.'
    return
  }
  createError.value = ''
  creating.value = true
  try {
    const res = await teacherStore.createStudent({
      first_name: form.value.firstName,
      last_name: form.value.lastName,
      grade_id: Number(form.value.gradeId)
    })
    createdStudentData.value = res
    showAddModal.value = false
    showSuccessModal.value = true
    form.value = { firstName: '', lastName: '', gradeId: '' }
  } catch (err: unknown) {
    const error = err as { response?: { data?: { message?: string } }, message?: string }
    createError.value = error.response?.data?.message || error.message || 'Қате шықты'
  } finally {
    creating.value = false
  }
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
  createdStudentData.value = null
  teacherStore.fetchStudents()
}

const resetPassword = async (student: StudentInfo) => {
  resettingId.value = student.id
  resetError.value = ''
  try {
    const resp = await teacherApi.resetStudentPassword(student.id)
    const newPass = resp.data.data.password
    const found = students.value.find(s => s.id === student.id)
    if (found) (found as StudentInfo & { password?: string }).password = newPass
  } catch (err: unknown) {
    const e = err as { response?: { data?: { message?: string } }, message?: string }
    resetError.value = e.response?.data?.message || e.message || 'Қате шықты'
  } finally {
    resettingId.value = null
  }
}

const confirmDelete = async (student: StudentInfo) => {
  if (!window.confirm(`"${student.full_name}" оқушысын өшіруді растайсыз ба?`)) return
  deletingId.value = student.id
  resetError.value = ''
  try {
    await teacherApi.deleteStudent(student.id)
    teacherStore.students = students.value.filter(s => s.id !== student.id)
  } catch (err: unknown) {
    const e = err as { response?: { data?: { message?: string } }, message?: string }
    resetError.value = e.response?.data?.message || e.message || 'Жою кезінде қате шықты'
  } finally {
    deletingId.value = null
  }
}
</script>

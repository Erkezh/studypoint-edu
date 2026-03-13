<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <Header />
    <main class="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex items-center justify-between mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Мұғалім кабинеті (Teacher Dashboard)</h1>
        <Button @click="showAddModal = true" variant="primary" class="flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          Оқушы қосу
        </Button>
      </div>

      <!-- Students List -->
      <div class="bg-white shadow rounded-lg overflow-hidden">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Менің оқушыларым</h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">Төменде сізге тіркелген оқушылар тізімі көрсетілген.</p>
        </div>
        
        <div v-if="loadingStudents" class="p-8 flex justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else-if="studentsError" class="p-4 text-red-600 bg-red-50">
          {{ studentsError }}
        </div>
        
        <div v-else-if="students.length === 0" class="p-8 text-center text-gray-500">
          Әзірге оқушылар жоқ. "Оқушы қосу" түймесін басып жаңа оқушыларды қосыңыз.
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Аты-жөні
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Логин
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Сыныбы
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="student in students" :key="student.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ student.full_name }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ student.username }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ student.grade_level ? `${student.grade_level} сынып` : 'Көрсетілмеген' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
    <Footer />

    <!-- Add Student Modal -->
    <Modal :is-open="showAddModal" title="Жаңа оқушы қосу" :show-close="true" @close="showAddModal = false">
      <template #content>
        <form @submit.prevent="submitAddStudent" class="space-y-4">
          <div v-if="createError" class="text-sm text-red-600 bg-red-50 p-2 rounded">
            {{ createError }}
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Аты (First Name)</label>
            <input v-model="form.firstName" type="text" required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm">
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Тегі (Last Name)</label>
            <input v-model="form.lastName" type="text" required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm">
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Сыныбы (Grade)</label>
            <select v-model="form.gradeId" required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm">
              <option value="" disabled>Таңдаңыз</option>
              <option v-for="grade in grades" :key="grade.number" :value="grade.number">
                {{ grade.title || `${grade.number} сынып` }}
              </option>
            </select>
          </div>
        </form>
      </template>
      <template #actions>
        <Button @click="submitAddStudent" variant="primary" :disabled="creating" :loading="creating">
          Қосу
        </Button>
        <Button @click="showAddModal = false" variant="outline" :disabled="creating">
          Болдырмау
        </Button>
      </template>
    </Modal>

    <!-- Success Modal showing Credentials -->
    <Modal :is-open="showSuccessModal" title="Оқушы сәтті құрылды!" :show-close="false">
      <template #content>
        <div class="space-y-4">
          <p class="text-gray-700">
            Оқушының аккаунты құрылды. <strong>Осы мәліметтерді міндетті түрде сақтап алыңыз немесе оқушыға беріңіз.</strong> Құпиясөз қайта көрсетілмейді!
          </p>
          <div class="bg-gray-100 p-4 rounded-md font-mono text-sm space-y-2">
            <div class="flex justify-between">
              <span class="text-gray-500">Аты-жөні:</span>
              <span class="font-bold text-gray-900">{{ createdStudentData?.full_name }}</span>
            </div>
            <div class="flex justify-between border-t border-gray-200 pt-2">
              <span class="text-gray-500">Логин (Username):</span>
              <span class="font-bold text-blue-600">{{ createdStudentData?.username }}</span>
            </div>
            <div class="flex justify-between border-t border-gray-200 pt-2">
              <span class="text-gray-500">Құпиясөз (Password):</span>
              <span class="font-bold text-green-600">{{ createdStudentData?.password }}</span>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <Button @click="closeSuccessModal" variant="primary">
          Жабып, жалғастыру
        </Button>
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
import { useCatalogStore } from '@/stores/catalog'

const teacherStore = useTeacherStore()
const catalogStore = useCatalogStore()

const { students, loading: loadingStudents, error: studentsError } = storeToRefs(teacherStore)
const { grades } = storeToRefs(catalogStore)

const showAddModal = ref(false)
const showSuccessModal = ref(false)
const creating = ref(false)
const createError = ref('')

const form = ref({
  firstName: '',
  lastName: '',
  gradeId: '' as string | number
})

const createdStudentData = ref<{ full_name: string, username: string, password: string } | null>(null)

onMounted(async () => {
  await teacherStore.fetchStudents()
  if (grades.value.length === 0) {
    await catalogStore.getGrades()
  }
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
    
    // Reset form
    form.value = {
      firstName: '',
      lastName: '',
      gradeId: ''
    }
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
}
</script>

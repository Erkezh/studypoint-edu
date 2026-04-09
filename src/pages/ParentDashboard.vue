<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <Header />
    <main class="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 leading-tight">Отбасы кабинеті</h1>
        <Button @click="showAddModal = true" variant="primary" class="w-full sm:w-auto flex items-center justify-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          Бала қосу
        </Button>
      </div>

      <!-- Children Analytics List -->
      <div class="bg-white shadow rounded-lg overflow-hidden">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Менің балаларымның үлгерімі</h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">Төменде балаларыңыздың білімгерлік статистикасы көрсетілген.</p>
        </div>
        
        <div v-if="loading" class="p-8 flex justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else-if="error" class="p-4 text-red-600 bg-red-50">
          {{ error }}
        </div>
        
        <div v-else-if="childrenAnalytics.length === 0" class="p-8 text-center text-gray-500">
          Әзірге балалар тіркелмеген. "Бала қосу" түймесін басып тіркеңіз.
        </div>
        
        <!-- Desktop Table -->
        <div v-else class="hidden sm:block overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Аты-жөні</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Сұрақтар саны</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дәлдік</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Уақыт (минут)</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="child in childrenAnalytics" :key="child.child_id">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ child.name }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ child.overview.total_questions_answered }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ child.overview.avg_accuracy_percent }}%
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ Math.round(child.overview.total_time_sec / 60) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Card List -->
        <div v-else class="block sm:hidden divide-y divide-gray-200">
          <div v-for="child in childrenAnalytics" :key="child.child_id" class="p-4 bg-white">
            <div class="flex justify-between items-start mb-3">
              <h4 class="text-base font-bold text-gray-900">{{ child.name }}</h4>
            </div>
            <div class="grid grid-cols-3 gap-2 text-center">
              <div class="bg-blue-50 p-2 rounded">
                <p class="text-[10px] text-blue-600 uppercase font-bold">Сұрақтар</p>
                <p class="text-sm font-bold text-blue-900">{{ child.overview.total_questions_answered }}</p>
              </div>
              <div class="bg-green-50 p-2 rounded">
                <p class="text-[10px] text-green-600 uppercase font-bold">Дәлдік</p>
                <p class="text-sm font-bold text-green-900">{{ child.overview.avg_accuracy_percent }}%</p>
              </div>
              <div class="bg-amber-50 p-2 rounded">
                <p class="text-[10px] text-amber-600 uppercase font-bold">Уақыт</p>
                <p class="text-sm font-bold text-amber-900">{{ Math.round(child.overview.total_time_sec / 60) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    <Footer />

    <!-- Add Child Modal -->
    <Modal :is-open="showAddModal" title="Жаңа бала профилін қосу" :show-close="true" @close="showAddModal = false">
      <template #content>
        <form @submit.prevent="submitAddChild" class="space-y-4">
          <div v-if="createError" class="text-sm text-red-600 bg-red-50 p-2 rounded">
            {{ createError }}
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Аты (Аты-жөні)</label>
            <input v-model="form.name" type="text" required minlength="2"
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
        <Button @click="submitAddChild" variant="primary" :disabled="creating" :loading="creating">
          Қосу
        </Button>
        <Button @click="showAddModal = false" variant="outline" :disabled="creating">
          Болдырмау
        </Button>
      </template>
    </Modal>

    <!-- Success Modal -->
    <Modal :is-open="showSuccessModal" title="Бала сәтті қосылды!" :show-close="false">
      <template #content>
        <p class="text-gray-700">
          Сіз жаңа бала профилін сәтті тіркедіңіз. Енді кіру кезінде бұл профиль таңдау үшін қолжетімді болады.
        </p>
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
import { familyApi } from '@/api/family'
import { useCatalogStore } from '@/stores/catalog'

const catalogStore = useCatalogStore()
const { grades } = storeToRefs(catalogStore)

interface ChildAnalytics {
  child_id: string;
  name: string;
  overview: {
    total_time_sec: number;
    avg_accuracy_percent: number;
    total_questions_answered: number;
  };
}
const childrenAnalytics = ref<ChildAnalytics[]>([])
const loading = ref(false)
const error = ref('')

const showAddModal = ref(false)
const showSuccessModal = ref(false)
const creating = ref(false)
const createError = ref('')

const form = ref({
  name: '',
  gradeId: '' as string | number
})

const fetchAnalytics = async () => {
  loading.value = true
  error.value = ''
  try {
    childrenAnalytics.value = await familyApi.getChildrenAnalytics()
  } catch (err: unknown) {
    const errorWithResp = err as { response?: { data?: { message?: string } } };
    error.value = errorWithResp.response?.data?.message || 'Деректерді жүктеу кезінде қателік орын алды'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (grades.value.length === 0) {
    await catalogStore.getGrades()
  }
  await fetchAnalytics()
})

const submitAddChild = async () => {
  if (!form.value.name || form.value.gradeId === '') {
    createError.value = 'Барлық өрістерді толтырыңыз.'
    return
  }
  
  createError.value = ''
  creating.value = true
  
  try {
    await familyApi.addChild({
      name: form.value.name,
      grade_level: Number(form.value.gradeId)
    })
    
    showAddModal.value = false
    showSuccessModal.value = true
    
    // Reset form
    form.value = { name: '', gradeId: '' }
    
    // Refresh analytics to show newly added child
    await fetchAnalytics()
  } catch (err: unknown) {
    const errObj = err as { response?: { data?: { message?: string } }, message?: string };
    createError.value = errObj.response?.data?.message || errObj.message || 'Бұл баланы қосу мүмкін болмады'
  } finally {
    creating.value = false
  }
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
}
</script>

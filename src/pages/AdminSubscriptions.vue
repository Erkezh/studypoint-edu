<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8 max-w-6xl">
      <!-- Back to Dashboard -->
      <router-link to="/admin" class="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors mb-6">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
        Админ панелі
      </router-link>

      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Жазылымдар</h1>
          <p class="text-gray-500 mt-1">Пайдаланушылардың жазылымдарын басқару</p>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center">
          <span class="text-2xl font-bold text-gray-900">{{ stats.total }}</span>
          <p class="text-xs text-gray-500 mt-1">Барлық жазылымдар</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center">
          <span class="text-2xl font-bold text-green-600">{{ stats.active }}</span>
          <p class="text-xs text-gray-500 mt-1">Белсенді</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center">
          <span class="text-2xl font-bold text-blue-600">{{ stats.family }}</span>
          <p class="text-xs text-gray-500 mt-1">Семейный</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center">
          <span class="text-2xl font-bold text-purple-600">{{ stats.classroom + stats.school }}</span>
          <p class="text-xs text-gray-500 mt-1">Класс / Мектеп</p>
        </div>
      </div>

      <!-- Error / Success -->
      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-4">{{ error }}</div>
      <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg mb-4">{{ successMessage }}</div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
        <p class="text-gray-500 mt-3 text-sm">Жүктелуде...</p>
      </div>

      <!-- Subscriptions Table -->
      <div v-else class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div v-if="subscriptions.length === 0" class="text-center py-12 text-gray-400">
          <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
          <p>Жазылымдар жоқ</p>
        </div>

        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Пайдаланушы</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Жоспар</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Мәртебе</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Мерзімі</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Әрекеттер</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="sub in subscriptions" :key="sub.user_id" class="hover:bg-gray-50 transition-colors">
              <td class="px-4 py-3">
                <div>
                  <p class="font-medium text-gray-900">{{ sub.user_name || '—' }}</p>
                  <p class="text-xs text-gray-400">{{ sub.user_email }}</p>
                </div>
              </td>
              <td class="px-4 py-3">
                <span class="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full"
                  :class="planBadgeClass(sub.plan)">
                  {{ planLabel(sub.plan) }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span class="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full"
                  :class="sub.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                  <span class="w-1.5 h-1.5 rounded-full" :class="sub.is_active ? 'bg-green-500' : 'bg-red-500'"></span>
                  {{ sub.is_active ? 'Белсенді' : 'Тоқтатылған' }}
                </span>
              </td>
              <td class="px-4 py-3 text-gray-600 text-xs">
                {{ sub.active_until ? formatDate(sub.active_until) : '—' }}
              </td>
              <td class="px-4 py-3 text-right">
                <button @click="openEditModal(sub)" class="text-xs px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-100 text-gray-600 transition-colors">
                  Өңдеу
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Add Subscription (for users without one) -->
      <div class="mt-6">
        <button @click="showAddForm = !showAddForm"
          class="inline-flex items-center gap-1.5 text-sm font-medium px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
          Жазылым қосу
        </button>

        <div v-if="showAddForm" class="mt-4 bg-white rounded-xl shadow-sm border border-gray-200 p-6 max-w-lg">
          <h3 class="font-semibold text-gray-900 mb-4">Жаңа жазылым қосу</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Пайдаланушы (User ID)</label>
              <select v-model="addForm.userId" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-400 outline-none">
                <option value="">Таңдаңыз...</option>
                <option v-for="u in usersWithoutSub" :key="u.id" :value="u.id">{{ u.full_name }} ({{ u.email }})</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Жоспар</label>
              <select v-model="addForm.plan" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-400 outline-none">
                <option value="FREE">Тегін</option>
                <option value="FAMILY">Семейный</option>
                <option value="CLASSROOM">Классный</option>
                <option value="SCHOOL">Мектеп</option>
              </select>
            </div>
            <button @click="handleAddSubscription" :disabled="!addForm.userId || addingSubscription"
              class="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors disabled:opacity-50">
              {{ addingSubscription ? 'Қосылуда...' : 'Қосу' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Edit Modal -->
      <div v-if="editModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="editModal = null">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Жазылымды өңдеу</h3>
          <p class="text-sm text-gray-600 mb-4">{{ editModal.user_name }} — {{ editModal.user_email }}</p>

          <div class="space-y-4">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Жоспар</label>
              <select v-model="editForm.plan" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-400 outline-none">
                <option value="FREE">Тегін</option>
                <option value="FAMILY">Семейный</option>
                <option value="CLASSROOM">Классный</option>
                <option value="SCHOOL">Мектеп</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Мәртебе</label>
              <select v-model="editForm.is_active" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-400 outline-none">
                <option :value="true">Белсенді</option>
                <option :value="false">Тоқтатылған</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Мерзімі</label>
              <input v-model="editForm.active_until" type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-400 outline-none" />
            </div>
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button @click="editModal = null" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors">
              Бас тарту
            </button>
            <button @click="handleUpdateSubscription" :disabled="updatingSubscription"
              class="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors disabled:opacity-50">
              {{ updatingSubscription ? 'Сақталуда...' : 'Сақтау' }}
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Header from '@/components/layout/Header.vue'
import { adminApi, type AdminSubscriptionItem } from '@/api/admin'
import type { AdminUser } from '@/types/api'

defineOptions({ name: 'AdminSubscriptions' })

const authStore = useAuthStore()
const router = useRouter()

const loading = ref(true)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const subscriptions = ref<AdminSubscriptionItem[]>([])
const allUsers = ref<AdminUser[]>([])
const showAddForm = ref(false)
const addingSubscription = ref(false)
const updatingSubscription = ref(false)

const editModal = ref<AdminSubscriptionItem | null>(null)
const editForm = ref({ plan: '', is_active: true, active_until: '' })
const addForm = ref({ userId: '', plan: 'FAMILY' })

const stats = computed(() => {
  const subs = subscriptions.value
  return {
    total: subs.length,
    active: subs.filter(s => s.is_active).length,
    family: subs.filter(s => s.plan === 'FAMILY').length,
    classroom: subs.filter(s => s.plan === 'CLASSROOM').length,
    school: subs.filter(s => s.plan === 'SCHOOL').length,
  }
})

const usersWithoutSub = computed(() => {
  const subUserIds = new Set(subscriptions.value.map(s => s.user_id))
  return allUsers.value.filter(u => !subUserIds.has(u.id))
})

const planLabel = (plan: string) => {
  const labels: Record<string, string> = {
    FREE: 'Тегін', PREMIUM: 'Premium', FAMILY: 'Семейный', CLASSROOM: 'Классный', SCHOOL: 'Мектеп'
  }
  return labels[plan] || plan
}

const planBadgeClass = (plan: string) => {
  const classes: Record<string, string> = {
    FREE: 'bg-gray-100 text-gray-600',
    FAMILY: 'bg-blue-100 text-blue-700',
    CLASSROOM: 'bg-green-100 text-green-700',
    SCHOOL: 'bg-purple-100 text-purple-700',
    PREMIUM: 'bg-yellow-100 text-yellow-700',
  }
  return classes[plan] || 'bg-gray-100 text-gray-600'
}

const formatDate = (iso: string) => {
  try {
    return new Date(iso).toLocaleDateString('kk-KZ', { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return iso
  }
}

const openEditModal = (sub: AdminSubscriptionItem) => {
  editModal.value = sub
  editForm.value = {
    plan: sub.plan,
    is_active: sub.is_active,
    active_until: sub.active_until ? sub.active_until.split('T')[0] : '',
  }
}

const loadData = async () => {
  loading.value = true
  error.value = null
  try {
    const [subsRes, usersRes] = await Promise.all([
      adminApi.listSubscriptions(),
      adminApi.getUsers(),
    ])
    subscriptions.value = (subsRes.data || []) as AdminSubscriptionItem[]
    allUsers.value = (usersRes.data || []) as AdminUser[]
  } catch (e: unknown) {
    console.error('Load subscriptions error:', e)
    error.value = 'Жазылымдарды жүктеу қатесі'
  } finally {
    loading.value = false
  }
}

const handleUpdateSubscription = async () => {
  if (!editModal.value) return
  updatingSubscription.value = true
  error.value = null
  try {
    const payload: Record<string, unknown> = { plan: editForm.value.plan, is_active: editForm.value.is_active }
    if (editForm.value.active_until) {
      payload.active_until = new Date(editForm.value.active_until).toISOString()
    }
    await adminApi.updateSubscription(editModal.value.user_id, payload as { plan?: string; is_active?: boolean; active_until?: string | null })
    editModal.value = null
    successMessage.value = 'Жазылым сәтті жаңартылды'
    setTimeout(() => { successMessage.value = null }, 3000)
    await loadData()
  } catch (e: unknown) {
    console.error('Update subscription error:', e)
    const err = e as { response?: { data?: { detail?: string } } }
    error.value = err.response?.data?.detail || 'Жазылымды жаңарту қатесі'
  } finally {
    updatingSubscription.value = false
  }
}

const handleAddSubscription = async () => {
  if (!addForm.value.userId) return
  addingSubscription.value = true
  error.value = null
  try {
    await adminApi.createSubscription(addForm.value.userId, { plan: addForm.value.plan, is_active: true })
    addForm.value = { userId: '', plan: 'FAMILY' }
    showAddForm.value = false
    successMessage.value = 'Жазылым сәтті қосылды'
    setTimeout(() => { successMessage.value = null }, 3000)
    await loadData()
  } catch (e: unknown) {
    console.error('Create subscription error:', e)
    const err = e as { response?: { data?: { detail?: string } } }
    error.value = err.response?.data?.detail || 'Жазылым қосу қатесі'
  } finally {
    addingSubscription.value = false
  }
}

onMounted(async () => {
  if (!authStore.isAuthenticated || authStore.user?.role !== 'ADMIN') {
    router.push({ name: 'home' })
    return
  }
  await loadData()
})
</script>

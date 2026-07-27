<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8 max-w-7xl">
    <!-- Header -->
    <div class="mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <router-link to="/admin" class="text-gray-400 hover:text-gray-600 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
        </router-link>
        <svg class="w-7 h-7 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
        <div>
          <h1 class="text-2xl font-bold text-gray-900 leading-tight">Пайдаланушылар</h1>
          <p class="text-sm text-gray-500">Платформаны пайдаланушыларды басқару</p>
        </div>
      </div>
      <div>
        <button
          @click="fetchUsers"
          class="flex items-center gap-2 bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 shadow-sm transition-all"
        >
          <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
          Жаңарту
        </button>
      </div>
    </div>

    <!-- Error/Success Messages -->
    <div v-if="error" class="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded shadow-sm">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        <p class="text-red-700">{{ error }}</p>
      </div>
    </div>
    <div v-if="successMsg" class="bg-green-50 border-l-4 border-green-500 p-4 mb-6 rounded shadow-sm">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
        <p class="text-green-700">{{ successMsg }}</p>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="p-5 border-b border-gray-100 flex flex-col sm:flex-row justify-between items-start sm:items-center bg-gray-50/50 gap-4">
        <div class="relative w-full sm:w-auto">
          <svg class="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Іздеу (аты немесе email)..."
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full sm:w-64 lg:w-80 transition-shadow"
          >
        </div>
        <span class="text-sm text-gray-500 font-medium shrink-0">Барлығы: {{ filteredUsers.length }}</span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200">
              <th class="py-4 px-6 text-xs font-semibold text-gray-500 uppercase tracking-wider">Пайдаланушы</th>
              <th class="py-4 px-6 text-xs font-semibold text-gray-500 uppercase tracking-wider">Email</th>
              <th class="py-4 px-6 text-xs font-semibold text-gray-500 uppercase tracking-wider text-center">Статус</th>
              <th class="py-4 px-6 text-xs font-semibold text-gray-500 uppercase tracking-wider">Рөл</th>
              <th class="py-4 px-6 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Әрекеттер</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="loading && users.length === 0">
              <td colspan="5" class="py-12 text-center text-gray-500">Жүктелуде...</td>
            </tr>
            <tr v-else-if="filteredUsers.length === 0">
              <td colspan="5" class="py-12 text-center text-gray-500 bg-gray-50/30">
                <svg class="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354l8 8-8 8-8-8 8-8z" /></svg>
                Пайдаланушылар табылмады.
              </td>
            </tr>
            <tr
              v-for="user in filteredUsers"
              :key="user.id"
              class="hover:bg-blue-50/30 transition-colors"
            >
              <td class="py-4 px-6">
                <div class="flex items-center">
                  <div class="h-9 w-9 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold mr-3 flex-shrink-0">
                    {{ user.full_name.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">{{ user.full_name }}</p>
                    <p class="text-xs text-gray-400 font-mono mt-0.5 truncate w-32" :title="user.id">{{ user.id.split('-')[0] }}...</p>
                  </div>
                </div>
              </td>
              <td class="py-4 px-6 text-sm text-gray-600">
                {{ user.email }}
              </td>
              <td class="py-4 px-6 text-center">
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                >
                  <span class="w-1.5 h-1.5 rounded-full mr-1.5" :class="user.is_active ? 'bg-green-500' : 'bg-red-500'"></span>
                  {{ user.is_active ? 'Белсенді' : 'Бұғатталған' }}
                </span>
              </td>
              <td class="py-4 px-6">
                <!-- Dropdown for role -->
                <select
                  v-model="user.role"
                  @change="updateUser(user, { role: user.role })"
                  class="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 py-1.5 pl-3 pr-8 shadow-sm bg-gray-50 hover:bg-white transition-colors"
                  :class="{
                    'text-purple-700 font-medium bg-purple-50 border-purple-200': user.role === UserRole.ADMIN,
                    'text-blue-700 font-medium bg-blue-50 border-blue-200': user.role === UserRole.TEACHER,
                    'text-gray-700': user.role === UserRole.STUDENT || user.role === UserRole.PARENT
                  }"
                  :disabled="updatingId === user.id"
                >
                  <option :value="UserRole.ADMIN">Admin</option>
                  <option :value="UserRole.TEACHER">Teacher</option>
                  <option :value="UserRole.STUDENT">Student</option>
                  <option :value="UserRole.PARENT">Parent</option>
                </select>
              </td>
              <td class="py-4 px-6 text-right">
                <button
                  @click="updateUser(user, { is_active: !user.is_active })"
                  class="inline-flex items-center p-2 rounded text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
                  :class="user.is_active
                    ? 'text-red-600 hover:bg-red-50 focus:ring-red-500'
                    : 'text-green-600 hover:bg-green-50 focus:ring-green-500'"
                  :disabled="updatingId === user.id"
                  :title="user.is_active ? 'Бұғаттау' : 'Құлпын ашу'"
                >
                  <svg v-if="updatingId === user.id" class="animate-spin w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                  <template v-else>
                    <svg v-if="user.is_active" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                    <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" /></svg>
                  </template>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
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
import { adminApi } from '@/api/admin'
import { UserRole } from '@/types/api'
import type { AdminUser, AdminUserUpdate } from '@/types/api'

const authStore = useAuthStore()
const router = useRouter()

const users = ref<AdminUser[]>([])
const loading = ref(false)
const error = ref('')
const successMsg = ref('')
const searchQuery = ref('')
const updatingId = ref<string | null>(null)

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value

  const query = searchQuery.value.toLowerCase()
  return users.value.filter(u =>
    u.full_name.toLowerCase().includes(query) ||
    u.email.toLowerCase().includes(query)
  )
})

const fetchUsers = async () => {
  loading.value = true
  error.value = ''
  successMsg.value = ''

  try {
    const response = await adminApi.getUsers()
    if (response.data) {
      users.value = response.data
    }
  } catch (e: unknown) {
    console.error('Failed to fetch users:', e)
    const err = e as { response?: { data?: { detail?: string } } }
    error.value = err.response?.data?.detail || 'Пайдаланушыларды жүктеу сәтсіз аяқталды'
  } finally {
    loading.value = false
  }
}

const updateUser = async (user: AdminUser, updates: AdminUserUpdate) => {
  updatingId.value = user.id
  error.value = ''
  successMsg.value = ''

  // Save original values in case of rollback
  const originalRole = user.role
  const originalStatus = user.is_active

  // Optimistic UI update for status toggle
  if (updates.is_active !== undefined) {
    user.is_active = updates.is_active
  }

  try {
    const response = await adminApi.updateUser(user.id, updates)
    if (response.data) {
      successMsg.value = `${user.full_name} деректері сәтті жаңартылды`
      // Update with server response
      Object.assign(user, response.data)

      // Clear success message after 3 seconds
      setTimeout(() => {
        successMsg.value = ''
      }, 3000)
    }
  } catch (e: unknown) { // Changed from 'e: any' to 'e: unknown'
    console.error(`Failed to update user ${user.id}:`, e)
    const err = e as { response?: { data?: { detail?: string } } } // Added type assertion for 'e'
    error.value = err.response?.data?.detail || 'Жаңарту сәтсіз аяқталды'

    // Rollback optimistic update
    if (updates.role !== undefined) user.role = originalRole
    if (updates.is_active !== undefined) user.is_active = originalStatus
  } finally {
    updatingId.value = null
  }
}

onMounted(() => {
  if (!authStore.isAuthenticated || authStore.user?.role !== 'ADMIN') {
    router.push({ name: 'home' })
    return
  }
  fetchUsers()
})
</script>

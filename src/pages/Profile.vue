<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-6">Профиль</h1>

      <div v-if="authStore.user" class="bg-white rounded-lg shadow-md p-6">
        <div class="mb-6">
          <h2 class="text-xl font-semibold mb-4">Жеке ақпарат</h2>
          <div class="space-y-3">
            <div>
              <span class="text-sm text-gray-500">Аты-жөні:</span>
              <p class="text-lg font-medium">{{ authStore.user.full_name }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Email:</span>
              <p class="text-lg font-medium">{{ authStore.user.email }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Рөл:</span>
              <p class="text-lg font-medium">{{ getRoleText(authStore.user.role) }}</p>
            </div>
            <div v-if="authStore.user.profile">
              <span class="text-sm text-gray-500">Сынып:</span>
              <p class="text-lg font-medium">{{ authStore.user.profile.grade_level }}</p>
            </div>
            <div v-if="authStore.user.subscription">
              <span class="text-sm text-gray-500">Жазылым:</span>
              <p class="text-lg font-medium">
                {{ authStore.user.subscription.plan === 'PREMIUM' ? 'Премиум' : 'Тегін' }}
                <span
                  :class="[
                    'ml-2 px-2 py-1 rounded text-xs',
                    authStore.user.subscription.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800',
                  ]"
                >
                  {{ authStore.user.subscription.is_active ? 'Белсенді' : 'Белсенді емес' }}
                </span>
              </p>
            </div>
          </div>
        </div>

        <div class="flex gap-4">
          <Button @click="handleLogout" variant="danger">Шығу</Button>
        </div>
      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import type { UserRole } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()

const getRoleText = (role: UserRole) => {
  const roles: Record<UserRole, string> = {
    ADMIN: 'Әкімші',
    TEACHER: 'Мұғалім',
    STUDENT: 'Оқушы',
    PARENT: 'Ата-ана',
  }
  return roles[role] || role
}

const handleLogout = async () => {
  await authStore.logout()
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Жүйеге кіру
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Немесе
          <router-link
            to="/auth/register"
            class="font-medium text-blue-600 hover:text-blue-500"
          >
            тіркеліңіз
          </router-link>
        </p>
        <div v-if="requireSubscription" class="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p class="text-sm text-yellow-800">
            <strong>Жазылым қажет:</strong> Сіз барлық сынақ сұрақтарды пайдаландыңыз. Практиканы жалғастыру үшін жүйеге кіріп, жазылымды рәсімдеңіз.
          </p>
        </div>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {{ error }}
        </div>

        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email" class="sr-only">Email</label>
            <input
              id="email"
              v-model="email"
              name="email"
              type="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="Email"
            />
          </div>
          <div>
            <label for="password" class="sr-only">Құпия сөз</label>
            <input
              id="password"
              v-model="password"
              name="password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="Құпия сөз"
            />
          </div>
        </div>

        <div>
          <Button
            type="submit"
            :loading="authStore.loading"
            :disabled="!email || !password"
            variant="primary"
            class="w-full"
          >
            Кіру
          </Button>
        </div>
      </form>

      <div class="mt-6 bg-gray-100 border border-gray-300 rounded-lg p-4">
        <p class="text-sm font-medium text-gray-700 mb-2">Тесттік аккаунттар (seed-тен):</p>
        <div class="text-xs text-gray-600 space-y-1">
          <p><strong>Admin:</strong> admin@example.com / Password123!</p>
          <p><strong>Teacher:</strong> teacher@example.com / Password123!</p>
          <p><strong>Student:</strong> student@example.com / Password123!</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Button from '@/components/ui/Button.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref<string | null>(null)
const requireSubscription = computed(() => route.query.requireSubscription === 'true')

const handleLogin = async () => {
  error.value = null

  try {
    await authStore.login({
      email: email.value,
      password: password.value,
    })

    // Редирект на страницу, с которой пришли, или на главную
    const redirect = route.query.redirect as string | undefined
    router.push(redirect || { name: 'home' })
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Кіру қатесі'
    console.error('Login error:', err)
  }
}

onMounted(() => {
  // Если уже авторизован, редирект на главную
  if (authStore.isAuthenticated) {
    router.push({ name: 'home' })
  }
})
</script>

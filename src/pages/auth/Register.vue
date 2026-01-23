<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Тіркелу
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Аккаунтыңыз бар ма?
          <router-link
            to="/auth/login"
            class="font-medium text-blue-600 hover:text-blue-500"
          >
            Кіріңіз
          </router-link>
        </p>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {{ error }}
        </div>

        <div class="space-y-4">
          <div>
            <label for="full_name" class="block text-sm font-medium text-gray-700">
              Толық аты-жөні
            </label>
            <input
              id="full_name"
              v-model="fullName"
              name="full_name"
              type="text"
              required
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Аты-жөні"
            />
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              id="email"
              v-model="email"
              name="email"
              type="email"
              required
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="user@example.com"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              Құпия сөз
            </label>
            <input
              id="password"
              v-model="password"
              name="password"
              type="password"
              required
              minlength="8"
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Кемінде 8 таңба"
            />
          </div>

          <div>
            <label for="grade_level" class="block text-sm font-medium text-gray-700">
              Сынып
            </label>
            <select
              id="grade_level"
              v-model.number="gradeLevel"
              name="grade_level"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="">Сыныпты таңдаңыз</option>
              <option v-for="grade in grades" :key="grade.id" :value="grade.number">
                {{ grade.title }}
              </option>
            </select>
          </div>

          <div>
            <label for="school" class="block text-sm font-medium text-gray-700">
              Мектеп (міндетті емес)
            </label>
            <input
              id="school"
              v-model="school"
              name="school"
              type="text"
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Мектеп атауы"
            />
          </div>
        </div>

        <div>
          <Button
            type="submit"
            :loading="authStore.loading"
            :disabled="!email || !password || !fullName || !gradeLevel"
            variant="primary"
            class="w-full"
          >
            Тіркелу
          </Button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCatalogStore } from '@/stores/catalog'
import Button from '@/components/ui/Button.vue'
import type { GradeResponse } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()
const catalogStore = useCatalogStore()

const fullName = ref('')
const email = ref('')
const password = ref('')
const gradeLevel = ref<number | null>(null)
const school = ref('')
const error = ref<string | null>(null)
const grades = ref<GradeResponse[]>([])

const handleRegister = async () => {
  if (!gradeLevel.value) return

  error.value = null

  try {
    await authStore.register({
      email: email.value,
      password: password.value,
      full_name: fullName.value,
      grade_level: gradeLevel.value,
      school: school.value || null,
    })

    // Редирект на главную после успешной регистрации
    router.push({ name: 'home' })
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Тіркелу қатесі'
    console.error('Register error:', err)
  }
}

onMounted(async () => {
  // Если уже авторизован, редирект на главную
  if (authStore.isAuthenticated) {
    router.push({ name: 'home' })
    return
  }

  // Загружаем классы для выбора
  try {
    grades.value = await catalogStore.getGrades()
  } catch (err) {
    console.error('Failed to load grades:', err)
  }
})
</script>

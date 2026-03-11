<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <Header />

    <main class="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-lg w-full">
        <!-- Card -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
          <!-- Card Header -->
          <div class="bg-gradient-to-br from-green-500 to-emerald-600 px-8 py-8 text-center">
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/20 backdrop-blur mb-4">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
            </div>
            <h1 class="text-2xl font-bold text-white">Тіркелу</h1>
            <p class="text-green-100 mt-1 text-sm">StudyPoint платформасына қош келдіңіз</p>
          </div>

          <!-- Progress Steps -->
          <div class="px-8 pt-6">
            <div class="flex items-center justify-center gap-2">
              <div class="flex items-center gap-2">
                <span
                  class="inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold transition-colors"
                  :class="step === 1 ? 'bg-green-500 text-white' : 'bg-green-100 text-green-700'"
                >1</span>
                <span class="text-xs font-medium" :class="step === 1 ? 'text-green-700' : 'text-gray-400'">Рөл</span>
              </div>
              <div class="w-8 h-0.5 bg-gray-200 rounded">
                <div class="h-full bg-green-500 rounded transition-all" :style="{ width: step >= 2 ? '100%' : '0%' }"></div>
              </div>
              <div class="flex items-center gap-2">
                <span
                  class="inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold transition-colors"
                  :class="step === 2 ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500'"
                >2</span>
                <span class="text-xs font-medium" :class="step === 2 ? 'text-green-700' : 'text-gray-400'">Деректер</span>
              </div>
            </div>
          </div>

          <div class="px-8 py-8">
            <!-- Error -->
            <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start gap-3">
              <svg class="w-5 h-5 text-red-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm text-red-700">{{ error }}</p>
            </div>

            <!-- Step 1: Role Selection -->
            <div v-if="step === 1">
              <p class="text-center text-sm text-gray-600 mb-6">Аккаунт түрін таңдаңыз</p>

              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <!-- Student -->
                <button
                  @click="selectRole('STUDENT')"
                  class="group relative flex flex-col items-center gap-3 p-5 rounded-xl border-2 transition-all hover:shadow-md"
                  :class="selectedRole === 'STUDENT'
                    ? 'border-green-500 bg-green-50 shadow-md'
                    : 'border-gray-200 hover:border-green-300'"
                >
                  <div class="w-14 h-14 rounded-full flex items-center justify-center transition-colors"
                    :class="selectedRole === 'STUDENT' ? 'bg-green-500' : 'bg-gray-100 group-hover:bg-green-100'">
                    <svg class="w-7 h-7" :class="selectedRole === 'STUDENT' ? 'text-white' : 'text-gray-500 group-hover:text-green-600'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                  <span class="text-sm font-semibold" :class="selectedRole === 'STUDENT' ? 'text-green-700' : 'text-gray-700'">Оқушы</span>
                </button>

                <!-- Parent -->
                <button
                  @click="selectRole('PARENT')"
                  class="group relative flex flex-col items-center gap-3 p-5 rounded-xl border-2 transition-all hover:shadow-md"
                  :class="selectedRole === 'PARENT'
                    ? 'border-green-500 bg-green-50 shadow-md'
                    : 'border-gray-200 hover:border-green-300'"
                >
                  <div class="w-14 h-14 rounded-full flex items-center justify-center transition-colors"
                    :class="selectedRole === 'PARENT' ? 'bg-green-500' : 'bg-gray-100 group-hover:bg-green-100'">
                    <svg class="w-7 h-7" :class="selectedRole === 'PARENT' ? 'text-white' : 'text-gray-500 group-hover:text-green-600'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                    </svg>
                  </div>
                  <span class="text-sm font-semibold" :class="selectedRole === 'PARENT' ? 'text-green-700' : 'text-gray-700'">Ата-ана</span>
                </button>

                <!-- Teacher -->
                <button
                  @click="selectRole('TEACHER')"
                  class="group relative flex flex-col items-center gap-3 p-5 rounded-xl border-2 transition-all hover:shadow-md"
                  :class="selectedRole === 'TEACHER'
                    ? 'border-green-500 bg-green-50 shadow-md'
                    : 'border-gray-200 hover:border-green-300'"
                >
                  <div class="w-14 h-14 rounded-full flex items-center justify-center transition-colors"
                    :class="selectedRole === 'TEACHER' ? 'bg-green-500' : 'bg-gray-100 group-hover:bg-green-100'">
                    <svg class="w-7 h-7" :class="selectedRole === 'TEACHER' ? 'text-white' : 'text-gray-500 group-hover:text-green-600'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                    </svg>
                  </div>
                  <span class="text-sm font-semibold" :class="selectedRole === 'TEACHER' ? 'text-green-700' : 'text-gray-700'">Мұғалім</span>
                </button>
              </div>

              <!-- Continue button -->
              <button
                @click="goToStep2"
                :disabled="!selectedRole"
                class="mt-6 w-full py-3 rounded-xl text-base font-semibold text-white transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                :class="selectedRole ? 'hover:opacity-90' : ''"
                style="background-color: #38B000;"
              >
                Жалғастыру
              </button>
            </div>

            <!-- Step 2: Credentials -->
            <div v-if="step === 2">
              <form @submit.prevent="handleRegister" class="space-y-4">
                <!-- Full Name -->
                <div>
                  <label for="reg-name" class="block text-sm font-medium text-gray-700 mb-1.5">Толық аты-жөні</label>
                  <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                      <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <input
                      id="reg-name"
                      v-model="fullName"
                      type="text"
                      required
                      placeholder="Аты-жөні"
                      class="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                    />
                  </div>
                </div>

                <!-- Email -->
                <div>
                  <label for="reg-email" class="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
                  <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                      <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <input
                      id="reg-email"
                      v-model="email"
                      type="email"
                      required
                      placeholder="user@example.com"
                      class="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                    />
                  </div>
                </div>

                <!-- Password -->
                <div>
                  <label for="reg-password" class="block text-sm font-medium text-gray-700 mb-1.5">Құпия сөз</label>
                  <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                      <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    </div>
                    <input
                      id="reg-password"
                      v-model="password"
                      type="password"
                      required
                      minlength="8"
                      placeholder="Кемінде 8 таңба"
                      class="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                    />
                  </div>
                </div>

                <!-- Grade (only for Student) -->
                <div v-if="selectedRole === 'STUDENT'">
                  <label for="reg-grade" class="block text-sm font-medium text-gray-700 mb-1.5">Сынып</label>
                  <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                      <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-2 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                    </div>
                    <select
                      id="reg-grade"
                      v-model.number="gradeLevel"
                      required
                      class="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all appearance-none"
                    >
                      <option value="">Сыныпты таңдаңыз</option>
                      <option v-for="grade in grades" :key="grade.id" :value="grade.number">
                        {{ grade.title }}
                      </option>
                    </select>
                  </div>
                </div>

                <!-- School (Optional) -->
                <div>
                  <label for="reg-school" class="block text-sm font-medium text-gray-700 mb-1.5">
                    Мектеп <span class="text-gray-400 font-normal">(міндетті емес)</span>
                  </label>
                  <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                      <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
                      </svg>
                    </div>
                    <input
                      id="reg-school"
                      v-model="school"
                      type="text"
                      placeholder="Мектеп атауы"
                      class="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                    />
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex gap-3 pt-2">
                  <button
                    type="button"
                    @click="step = 1"
                    class="px-5 py-3 rounded-xl text-sm font-medium text-gray-600 border border-gray-300 hover:bg-gray-50 transition-colors"
                  >
                    Артқа
                  </button>
                  <Button
                    type="submit"
                    :loading="authStore.loading"
                    :disabled="!canSubmit"
                    variant="primary"
                    class="flex-1 !py-3 !rounded-xl !text-base !font-semibold"
                    style="background-color: #38B000;"
                    onmouseover="this.style.backgroundColor='#2d8a00'"
                    onmouseout="this.style.backgroundColor='#38B000'"
                  >
                    Тіркелу
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <!-- Login link -->
        <p class="mt-6 text-center text-sm text-gray-600">
          Аккаунтыңыз бар ма?
          <router-link to="/auth/login" class="font-semibold text-green-600 hover:text-green-700 transition-colors">
            Кіру
          </router-link>
        </p>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCatalogStore } from '@/stores/catalog'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import type { GradeResponse } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()
const catalogStore = useCatalogStore()

const step = ref(1)
const selectedRole = ref<'STUDENT' | 'PARENT' | 'TEACHER' | null>(null)
const fullName = ref('')
const email = ref('')
const password = ref('')
const gradeLevel = ref<number | ''>('')
const school = ref('')
const error = ref<string | null>(null)
const grades = ref<GradeResponse[]>([])

const selectRole = (role: 'STUDENT' | 'PARENT' | 'TEACHER') => {
  selectedRole.value = role
}

const goToStep2 = () => {
  if (selectedRole.value) {
    step.value = 2
  }
}

const canSubmit = computed(() => {
  if (!fullName.value || !email.value || !password.value) return false
  if (selectedRole.value === 'STUDENT' && !gradeLevel.value) return false
  return true
})

const handleRegister = async () => {
  if (!canSubmit.value || !selectedRole.value) return

  error.value = null

  try {
    await authStore.register({
      email: email.value,
      password: password.value,
      full_name: fullName.value,
      role: selectedRole.value as any,
      grade_level: selectedRole.value === 'STUDENT' ? (gradeLevel.value as number) : 0,
      school: school.value || null,
    })

    // Redirect to pricing page after registration
    router.push({ name: 'pricing' })
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Тіркелу қатесі. Қайта көріңіз.'
    console.error('Register error:', err)
  }
}

onMounted(async () => {
  if (authStore.isAuthenticated) {
    router.push({ name: 'home' })
    return
  }

  try {
    grades.value = await catalogStore.getGrades()
  } catch (err) {
    console.error('Failed to load grades:', err)
  }
})
</script>

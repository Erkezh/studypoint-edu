<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <Header />

    <main class="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-md w-full">
        <!-- Card -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
          <!-- Card Header with gradient -->
          <div class="bg-gradient-to-br from-green-500 to-emerald-600 px-8 py-8 text-center">
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/20 backdrop-blur mb-4">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h1 class="text-2xl font-bold text-white">Жүйеге кіру</h1>
            <p class="text-green-100 mt-1 text-sm">StudyPoint аккаунтыңызға кіріңіз</p>
          </div>

          <!-- Subscription notice -->
          <div v-if="requireSubscription" class="mx-6 mt-6 bg-amber-50 border border-amber-200 rounded-xl p-4">
            <div class="flex items-start gap-3">
              <svg class="w-5 h-5 text-amber-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <p class="text-sm text-amber-800">
                <strong>Жазылым қажет:</strong> Сіз барлық сынақ сұрақтарды пайдаландыңыз. Практиканы жалғастыру үшін жүйеге кіріп, жазылымды рәсімдеңіз.
              </p>
            </div>
          </div>

          <!-- Form -->
          <div class="px-8 py-8">
            <!-- Error message -->
            <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start gap-3">
              <svg class="w-5 h-5 text-red-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm text-red-700">{{ error }}</p>
            </div>

            <form @submit.prevent="handleLogin" class="space-y-5">
              <div>
                <label for="login-email" class="block text-sm font-medium text-gray-700 mb-1.5">Email / Логин</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <input
                    id="login-email"
                    v-model="email"
                    type="text"
                    required
                    placeholder="user@example.com немесе user1234"
                    class="w-full pl-11 pr-4 py-3 border rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    :class="error ? 'border-red-300 bg-red-50/30' : 'border-gray-300'"
                  />
                </div>
              </div>

              <!-- Password -->
              <div>
                <div class="flex items-center justify-between mb-1.5">
                  <label for="login-password" class="block text-sm font-medium text-gray-700">Құпия сөз</label>
                  <button type="button" @click="handleForgotPassword" class="text-xs text-green-600 hover:text-green-700 font-medium transition-colors">
                    Ұмыттыңыз ба?
                  </button>
                </div>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <input
                    id="login-password"
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    placeholder="Құпия сөзді енгізіңіз"
                    class="w-full pl-11 pr-12 py-3 border rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    :class="error ? 'border-red-300 bg-red-50/30' : 'border-gray-300'"
                  />
                  <button type="button" @click="showPassword = !showPassword"
                    class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600 transition-colors">
                    <svg v-if="!showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Submit -->
              <Button
                type="submit"
                :loading="authStore.loading"
                :disabled="!email || !password"
                variant="primary"
                class="w-full !py-3 !rounded-xl !text-base !font-semibold"
                style="background-color: #38B000;"
                onmouseover="this.style.backgroundColor='#2d8a00'"
                onmouseout="this.style.backgroundColor='#38B000'"
              >
                Кіру
              </Button>
            </form>

            <!-- Test Accounts -->
            <div class="mt-6 bg-gray-50 border border-gray-200 rounded-xl p-4">
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Тест аккаунттары</p>
              <div class="space-y-2">
                <button type="button" @click="fillCredentials('admin@example.com', 'Password123!')"
                  class="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-white border border-transparent hover:border-gray-200 transition-all text-left">
                  <div>
                    <span class="text-xs font-medium text-gray-900">Админ</span>
                    <span class="text-xs text-gray-400 ml-2">admin@example.com</span>
                  </div>
                  <span class="text-xs px-2 py-0.5 bg-red-100 text-red-600 rounded-full font-medium">ADMIN</span>
                </button>
                <button type="button" @click="fillCredentials('teacher@example.com', 'Password123!')"
                  class="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-white border border-transparent hover:border-gray-200 transition-all text-left">
                  <div>
                    <span class="text-xs font-medium text-gray-900">Мұғалім</span>
                    <span class="text-xs text-gray-400 ml-2">teacher@example.com</span>
                  </div>
                  <span class="text-xs px-2 py-0.5 bg-blue-100 text-blue-600 rounded-full font-medium">TEACHER</span>
                </button>
                <button type="button" @click="fillCredentials('student@example.com', 'Password123!')"
                  class="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-white border border-transparent hover:border-gray-200 transition-all text-left">
                  <div>
                    <span class="text-xs font-medium text-gray-900">Оқушы</span>
                    <span class="text-xs text-gray-400 ml-2">student@example.com</span>
                  </div>
                  <span class="text-xs px-2 py-0.5 bg-green-100 text-green-600 rounded-full font-medium">STUDENT</span>
                </button>
              </div>
              <p class="text-xs text-gray-400 mt-2 text-center">Құпия сөз: <span class="font-mono">Password123!</span></p>
            </div>
          </div>
        </div>

        <!-- Register link -->
        <p class="mt-6 text-center text-sm text-gray-600">
          Аккаунтыңыз жоқ па?
          <router-link to="/auth/register" class="font-semibold text-green-600 hover:text-green-700 transition-colors">
            Тіркелу
          </router-link>
        </p>
      </div>
    </main>

    <Footer />

    <!-- "Who are you?" Profile Selection Modal -->
    <Teleport to="body">
      <div v-if="showProfileModal" class="fixed inset-0 z-[9999] flex items-center justify-center">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="cancelProfileSelection"></div>
        
        <!-- Modal -->
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden animate-modal-in">
          <!-- Close button -->
          <button @click="cancelProfileSelection" class="absolute top-4 right-4 w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500 hover:text-gray-700 transition-colors z-10">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>

          <!-- Header -->
          <div class="bg-gradient-to-br from-[#00a6c0] to-[#0089a0] px-8 py-6 text-center">
            <h2 class="text-2xl font-bold text-white">Қош келдіңіз!</h2>
            <p class="text-white/80 text-sm mt-1">Сіз кімсіз?</p>
          </div>

          <!-- Profiles -->
          <div class="px-8 py-6">
            <div v-if="loadingChildren" class="flex justify-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-4 border-gray-200 border-t-[#00a6c0]"></div>
            </div>
            <div v-else class="flex flex-wrap justify-center gap-6">
              <!-- Children -->
              <button 
                v-for="child in childrenList" :key="child.id"
                @click="selectChild(child.id)"
                class="flex flex-col items-center gap-2 p-4 rounded-xl hover:bg-[#e6f8fb] transition-colors group cursor-pointer min-w-[100px]"
              >
                <div class="w-16 h-16 rounded-full bg-[#e6f8fb] border-2 border-[#00a6c0] flex items-center justify-center group-hover:scale-110 transition-transform">
                  <svg class="w-8 h-8 text-[#00a6c0]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <span class="text-sm font-medium text-[#00a6c0]">{{ child.full_name }}</span>
                <span class="text-[10px] text-gray-400">{{ child.grade_level ? `${child.grade_level}-сынып` : 'Оқушы' }}</span>
              </button>

              <!-- Parent option -->
              <button 
                @click="selectParent()"
                class="flex flex-col items-center gap-2 p-4 rounded-xl hover:bg-orange-50 transition-colors group cursor-pointer min-w-[100px]"
              >
                <div class="w-16 h-16 rounded-full bg-orange-50 border-2 border-orange-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <svg class="w-8 h-8 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <span class="text-sm font-medium text-orange-500">Ата-ана</span>
                <span class="text-[10px] text-gray-400">Бақылау режимі</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import type { FamilyMemberResponse, UserMeResponse } from '@/types/api'

defineOptions({ name: 'LoginPage' })

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const error = ref<string | null>(null)
const requireSubscription = computed(() => route.query.requireSubscription === 'true')

// Profile selection modal state
const showProfileModal = ref(false)
const loadingChildren = ref(false)
const childrenList = ref<FamilyMemberResponse[]>([])
const switchingProfile = ref(false)

const handleLogin = async () => {
  error.value = null

  try {
    const result = await authStore.login({
      email: email.value,
      password: password.value,
    })

    // If user is a PARENT, show profile selection modal
    if (result?.user?.role === 'PARENT') {
      showProfileModal.value = true
      loadingChildren.value = true
      try {
        const childrenResp = await authApi.getFamilyMembers()
        childrenList.value = (childrenResp.data?.members || []).filter(m => m.role === 'STUDENT')
      } catch (err) {
        console.error('Failed to fetch children:', err)
        childrenList.value = []
      } finally {
        loadingChildren.value = false
      }
      return // Don't redirect yet
    }

    // Normal redirect for non-parent users
    const redirect = route.query.redirect as string | undefined
    router.push(redirect || { name: 'home' })
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } }, message?: string }
    error.value = e.response?.data?.detail || e.message || 'Кіру қатесі. Қайта көріңіз.'
    console.error('Login error:', err)
  }
}

const selectChild = async (childId: string) => {
  if (switchingProfile.value) return
  switchingProfile.value = true
  try {
    const resp = await authApi.switchProfile({ target_user_id: childId })
    if (resp.data) {
      // Update auth store with child tokens
      authStore.setAccessToken(resp.data.access_token)
      authStore.setRefreshToken(resp.data.refresh_token)
      // Update user in store and localStorage
      authStore.user = resp.data.user as unknown as UserMeResponse
      localStorage.setItem('user', JSON.stringify(resp.data.user))

      showProfileModal.value = false
      const redirect = route.query.redirect as string | undefined
      router.push(redirect || { name: 'home' })
    }
  } catch (err) {
    console.error('Failed to switch profile:', err)
    error.value = 'Профильді ауыстыру мүмкін болмады'
    showProfileModal.value = false
  } finally {
    switchingProfile.value = false
  }
}

const selectParent = () => {
  // Stay as parent, redirect to home
  showProfileModal.value = false
  const redirect = route.query.redirect as string | undefined
  router.push(redirect || { name: 'home' })
}

const cancelProfileSelection = async () => {
  // Cancel = logout and go back to login form
  showProfileModal.value = false
  await authStore.logout()
}

const handleForgotPassword = () => {
  alert('Бұл мүмкіндік жақында қосылады — Құпия сөзді қалпына келтіру')
}

const fillCredentials = (e: string, p: string) => {
  email.value = e
  password.value = p
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push({ name: 'home' })
  }
})
</script>

<style scoped>
.animate-modal-in {
  animation: modalIn 0.3s ease-out;
}

@keyframes modalIn {
  from { opacity: 0; transform: scale(0.9) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
</style>

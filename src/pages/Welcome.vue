<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <Header />

    <main class="flex-1 flex items-center justify-center py-12 px-4">
      <div class="max-w-lg w-full text-center">
        <!-- Celebration Card -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
          <!-- Success Header -->
          <div class="bg-gradient-to-br from-green-500 to-emerald-600 px-8 py-10 relative overflow-hidden">
            <!-- Decorative circles -->
            <div class="absolute top-4 left-8 w-3 h-3 rounded-full bg-white/20 animate-bounce" style="animation-delay: 0s;"></div>
            <div class="absolute top-12 right-12 w-2 h-2 rounded-full bg-white/30 animate-bounce" style="animation-delay: 0.3s;"></div>
            <div class="absolute bottom-6 left-16 w-4 h-4 rounded-full bg-white/15 animate-bounce" style="animation-delay: 0.6s;"></div>
            <div class="absolute top-8 right-24 w-2 h-2 rounded-full bg-white/25 animate-bounce" style="animation-delay: 0.9s;"></div>
            <div class="absolute bottom-4 right-8 w-3 h-3 rounded-full bg-white/20 animate-bounce" style="animation-delay: 1.2s;"></div>

            <!-- Checkmark -->
            <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-white/20 backdrop-blur mb-5">
              <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <h1 class="text-3xl font-bold text-white mb-2">Құттықтаймыз! 🎉</h1>
            <p class="text-green-100 text-sm">Сіздің жазылымыңыз сәтті рәсімделді</p>
          </div>

          <!-- Content -->
          <div class="px-8 py-8">
            <p class="text-gray-600 mb-8">
              Енді сіз барлық мүмкіндіктерге қол жеткізе аласыз. Бастау үшін төмендегі сілтемелерді пайдаланыңыз.
            </p>

            <div class="space-y-3">
              <router-link
                to="/"
                class="flex items-center justify-center gap-2 w-full py-3.5 rounded-xl text-base font-semibold text-white transition-all"
                style="background-color: #38B000;"
                onmouseover="this.style.backgroundColor='#2d8a00'"
                onmouseout="this.style.backgroundColor='#38B000'"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Дағдыларды бастау
              </router-link>

              <router-link
                to="/"
                class="flex items-center justify-center gap-2 w-full py-3 rounded-xl text-sm font-medium text-gray-600 border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                Менің кабинетім
              </router-link>
            </div>

            <!-- Auto-redirect notice -->
            <p v-if="countdown > 0" class="text-xs text-gray-400 mt-6">
              {{ countdown }} секундтан кейін автоматты түрде басты бетке бағытталасыз
            </p>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'

defineOptions({ name: 'WelcomePage' })

const router = useRouter()
const countdown = ref(10)
let timer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      if (timer) clearInterval(timer)
      router.push({ name: 'home' })
    }
  }, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

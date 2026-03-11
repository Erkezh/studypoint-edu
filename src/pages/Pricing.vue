<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <Header />

    <main class="flex-1 container mx-auto px-4 py-12 max-w-6xl">
      <!-- Title -->
      <div class="text-center mb-12">
        <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 mb-3">Жазылым жоспарын таңдаңыз</h1>
        <p class="text-gray-500 text-lg max-w-2xl mx-auto">StudyPoint математика платформасына толық қолжетімділіктің ең тиімді жоспарын таңдаңыз</p>
      </div>

      <!-- Billing Toggle -->
      <div class="flex items-center justify-center gap-4 mb-10">
        <span class="text-sm font-medium" :class="billingCycle === 'monthly' ? 'text-gray-900' : 'text-gray-400'">Ай сайын</span>
        <button @click="billingCycle = billingCycle === 'monthly' ? 'yearly' : 'monthly'"
          class="relative w-14 h-7 rounded-full transition-colors"
          :class="billingCycle === 'yearly' ? 'bg-green-500' : 'bg-gray-300'">
          <span
            class="absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full shadow transition-transform"
            :class="billingCycle === 'yearly' ? 'translate-x-7' : ''"
          ></span>
        </button>
        <span class="text-sm font-medium" :class="billingCycle === 'yearly' ? 'text-gray-900' : 'text-gray-400'">
          Жыл сайын
          <span class="ml-1 inline-block bg-green-100 text-green-700 text-xs font-bold px-2 py-0.5 rounded-full">-20%</span>
        </span>
      </div>

      <!-- Plan Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        <!-- Family Plan -->
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm hover:shadow-lg transition-shadow overflow-hidden flex flex-col">
          <div class="p-6 flex-1">
            <div class="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center mb-4">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-1">Семейный</h3>
            <p class="text-sm text-gray-500 mb-4">1 бала үшін жеке жоспар</p>

            <div class="mb-6">
              <span class="text-3xl font-bold text-gray-900">{{ billingCycle === 'monthly' ? '₸1,990' : '₸1,590' }}</span>
              <span class="text-gray-400 text-sm">/ай</span>
              <p v-if="billingCycle === 'yearly'" class="text-xs text-green-600 mt-1 font-medium">₸19,080 / жыл</p>
            </div>

            <ul class="space-y-3 text-sm text-gray-600">
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                1 оқушы аккаунты
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                Барлық математика тақырыптары
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                Шектеусіз жаттығулар
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                Прогресс талдауы
              </li>
            </ul>
          </div>
          <div class="px-6 pb-6">
            <button
              @click="selectPlan('family')"
              class="w-full py-3 rounded-xl text-sm font-semibold border-2 border-gray-200 text-gray-700 hover:border-green-500 hover:text-green-700 hover:bg-green-50 transition-all"
            >
              Таңдау
            </button>
          </div>
        </div>

        <!-- Classroom Plan (Recommended) -->
        <div class="relative bg-white rounded-2xl border-2 border-green-500 shadow-lg hover:shadow-xl transition-shadow overflow-hidden flex flex-col">
          <div class="absolute top-0 right-0 bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-bl-xl">
            ТАНЫМАЛ
          </div>

          <div class="p-6 flex-1">
            <div class="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center mb-4">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-2 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-1">Классный</h3>
            <p class="text-sm text-gray-500 mb-4">Мұғалім + 30 оқушыға дейін</p>

            <div class="mb-6">
              <span class="text-3xl font-bold text-gray-900">{{ billingCycle === 'monthly' ? '₸9,990' : '₸7,990' }}</span>
              <span class="text-gray-400 text-sm">/ай</span>
              <p v-if="billingCycle === 'yearly'" class="text-xs text-green-600 mt-1 font-medium">₸95,880 / жыл</p>
            </div>

            <ul class="space-y-3 text-sm text-gray-600">
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                30 оқушы аккаунты
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                Мұғалім панелі
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                Барлық математика тақырыптары
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                Класс прогресс талдауы
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                Тапсырмалар жүйесі
              </li>
            </ul>
          </div>
          <div class="px-6 pb-6">
            <button
              @click="selectPlan('classroom')"
              class="w-full py-3 rounded-xl text-sm font-semibold text-white transition-all"
              style="background-color: #38B000;"
              onmouseover="this.style.backgroundColor='#2d8a00'"
              onmouseout="this.style.backgroundColor='#38B000'"
            >
              Таңдау
            </button>
          </div>
        </div>

        <!-- School Plan -->
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm hover:shadow-lg transition-shadow overflow-hidden flex flex-col">
          <div class="p-6 flex-1">
            <div class="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center mb-4">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-1">Мектеп</h3>
            <p class="text-sm text-gray-500 mb-4">Мектеп + 500 оқушыға дейін</p>

            <div class="mb-6">
              <span class="text-3xl font-bold text-gray-900">{{ billingCycle === 'monthly' ? '₸49,990' : '₸39,990' }}</span>
              <span class="text-gray-400 text-sm">/ай</span>
              <p v-if="billingCycle === 'yearly'" class="text-xs text-green-600 mt-1 font-medium">₸479,880 / жыл</p>
            </div>

            <ul class="space-y-3 text-sm text-gray-600">
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                500 оқушы аккаунты
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                Мектеп админ панелі
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                Барлық математика тақырыптары
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                Мектеп деңгейінде талдау
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                Бейіндеу мүмкіндігі
              </li>
            </ul>
          </div>
          <div class="px-6 pb-6">
            <button
              @click="selectPlan('school')"
              class="w-full py-3 rounded-xl text-sm font-semibold border-2 border-gray-200 text-gray-700 hover:border-green-500 hover:text-green-700 hover:bg-green-50 transition-all"
            >
              Таңдау
            </button>
          </div>
        </div>
      </div>

      <!-- Skip link for authenticated users -->
      <div v-if="authStore.isAuthenticated" class="text-center mt-8">
        <router-link to="/" class="text-sm text-gray-500 hover:text-gray-700 underline transition-colors">
          Кейінірек таңдаймын — Басты бетке оралу
        </router-link>
      </div>

      <!-- FAQ Section -->
      <div class="max-w-2xl mx-auto mt-16">
        <h2 class="text-2xl font-bold text-gray-900 text-center mb-8">Жиі қойылатын сұрақтар</h2>
        <div class="space-y-4">
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h3 class="font-semibold text-gray-900 mb-2">Жазылымды бас тарта аламын ба?</h3>
            <p class="text-sm text-gray-600">Иә, жазылымды кез келген уақытта тоқтата аласыз. Ағымдағы кезеңнің соңына дейін қолжетімділік сақталады.</p>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h3 class="font-semibold text-gray-900 mb-2">Тегін сынақ кезеңі бар ма?</h3>
            <p class="text-sm text-gray-600">Иә, барлық пайдаланушылар тіркелу кезінде бірнеше тегін сұрақтарды шешу мүмкіндігін алады.</p>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h3 class="font-semibold text-gray-900 mb-2">Классный жоспардан мектеп жоспарға ауыса аламын ба?</h3>
            <p class="text-sm text-gray-600">Иә, кез келген уақытта жоспарды жоғары деңгейге ауыстыра аласыз. Төлем айырмашылығы автоматты есептеледі.</p>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'

defineOptions({ name: 'PricingPage' })

const router = useRouter()
const authStore = useAuthStore()

const billingCycle = ref<'monthly' | 'yearly'>('monthly')

const selectPlan = (plan: string) => {
  router.push({ name: 'payment', query: { plan, billing: billingCycle.value } })
}
</script>

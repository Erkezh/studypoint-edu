<template>
  <div class="min-h-screen bg-gradient-to-br from-cyan-50 via-white to-lime-50">
    <Header />
    <main class="container mx-auto px-4 py-8 max-w-6xl">
      <div class="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <p class="text-sm font-bold uppercase tracking-wider text-green-600">Менің профилім</p>
          <h1 class="text-3xl font-black text-slate-900">Профиль</h1>
        </div>
        <Button @click="handleLogout" variant="danger">Шығу</Button>
      </div>

      <div v-if="authStore.user" class="grid gap-6 lg:grid-cols-[1.35fr_0.9fr]">
        <section class="rounded-[28px] border border-amber-100 bg-white p-5 shadow-xl shadow-amber-100/50">
          <div class="relative overflow-hidden rounded-[24px] bg-gradient-to-br from-amber-100 via-orange-50 to-yellow-100 p-6">
            <div class="absolute right-5 top-5 grid h-12 w-12 place-items-center rounded-xl border border-amber-200 bg-white/60 text-xl shadow-sm">
              ↗
            </div>

            <div class="flex flex-wrap items-center gap-6">
              <div class="flex items-end gap-1">
                <span class="text-7xl font-black leading-none text-transparent [-webkit-text-stroke:2px_#fb923c]">
                  {{ displayStreak }}
                </span>
                <img class="mb-3 h-12 w-12 object-contain" src="/assets/streak-fire.png" alt="Streak" />
              </div>

              <div class="min-w-0 flex-1">
                <h2 class="text-4xl font-black text-slate-900">күндік streak!</h2>
                <p class="mt-3 text-2xl leading-snug text-slate-800">
                  Әр күн маңызды. Қарқыныңды сақта!
                </p>
              </div>

              <div class="grid h-24 w-24 place-items-center rounded-full bg-violet-100 shadow-md ring-4 ring-white">
                <span class="text-4xl font-black text-slate-900">{{ userInitial }}</span>
              </div>
            </div>

            <div class="mt-8 grid grid-cols-7 gap-2">
              <div v-for="day in streakDays" :key="day.label" class="text-center">
                <div
                  class="mb-2 text-lg font-black"
                  :class="day.today ? 'mx-auto grid h-10 w-10 place-items-center rounded-full bg-blue-700 text-white' : 'text-gray-500'"
                >
                  {{ day.label }}
                </div>
                <div
                  class="grid h-14 place-items-center rounded-2xl"
                  :class="day.done ? 'bg-orange-100 shadow-inner' : 'border-2 border-violet-400 bg-white/55 text-xl'"
                >
                  <img v-if="day.done" class="h-10 w-10 object-contain" src="/assets/streak-fire.png" alt="Streak" />
                  <span v-else>○</span>
                </div>
              </div>
            </div>
          </div>

          <p class="mt-6 text-2xl font-semibold text-slate-800">Бүгін есеп шығарып streak-ті ұзарт!</p>
          <div class="mt-4 rounded-2xl border border-gray-200 bg-white p-5">
            <div class="mb-4 flex items-center justify-between gap-4">
              <strong class="text-xl text-slate-800">Бүгінгі мақсат</strong>
              <span class="text-3xl font-black text-slate-900">{{ todayProgress }}/10 <small class="text-base font-bold">есеп</small></span>
            </div>
            <div class="h-4 overflow-hidden rounded-full bg-orange-100">
              <i class="block h-full rounded-full bg-gradient-to-r from-orange-400 to-yellow-300" :style="{ width: `${todayGoalPercent}%` }"></i>
            </div>
          </div>

          <router-link
            to="/topics"
            class="mt-6 flex min-h-14 items-center justify-center rounded-2xl bg-indigo-600 px-6 text-xl font-black text-white shadow-lg shadow-indigo-200 transition hover:bg-indigo-700"
          >
            Streak ұзарту
          </router-link>
        </section>

        <aside class="space-y-6">
          <section class="rounded-[24px] border border-cyan-100 bg-slate-950 p-5 text-white shadow-xl shadow-cyan-100">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <p class="text-sm font-bold uppercase tracking-wider text-cyan-300">Ойын статистикасы</p>
                <h2 class="text-2xl font-black">{{ gamification.level }}-деңгей</h2>
              </div>
              <span class="grid h-12 w-12 place-items-center rounded-2xl bg-cyan-400/15 text-2xl">★</span>
            </div>
            <div class="mb-5">
              <div class="mb-2 flex justify-between text-sm font-bold text-slate-300">
                <span>XP</span>
                <span>{{ gamification.xp }} / {{ gamification.nextLevelXp }}</span>
              </div>
              <div class="h-3 overflow-hidden rounded-full bg-slate-700">
                <i class="block h-full rounded-full bg-gradient-to-r from-cyan-400 via-green-400 to-yellow-300" :style="{ width: `${gamification.xpProgress}%` }"></i>
              </div>
            </div>
            <div class="grid grid-cols-3 gap-3">
              <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
                <span class="text-xl text-yellow-300">●</span>
                <strong class="mt-1 block text-xl">{{ gamification.coins.toLocaleString() }}</strong>
                <small class="text-slate-400">монета</small>
              </div>
              <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
                <img class="h-7 w-7 object-contain" src="/assets/streak-fire.png" alt="Streak" />
                <strong class="mt-1 block text-xl">{{ gamification.dailyStreak }}</strong>
                <small class="text-slate-400">streak</small>
              </div>
              <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
                <span class="text-xl">⚡</span>
                <strong class="mt-1 block text-xl">{{ gamification.comboStreak }}</strong>
                <small class="text-slate-400">комбо</small>
              </div>
            </div>
          </section>

          <section class="rounded-[24px] border border-gray-100 bg-white p-6 shadow-xl shadow-gray-100">
            <h2 class="mb-4 text-xl font-black text-slate-900">Жеке ақпарат</h2>
            <div class="space-y-4">
              <div>
                <span class="text-sm text-gray-500">Аты-жөні:</span>
                <p class="text-lg font-bold text-slate-900">{{ authStore.user.full_name }}</p>
              </div>
              <div>
                <span class="text-sm text-gray-500">Email:</span>
                <p class="text-lg font-bold text-slate-900">{{ authStore.user.email }}</p>
              </div>
              <div>
                <span class="text-sm text-gray-500">Рөл:</span>
                <p class="text-lg font-bold text-slate-900">{{ getRoleText(authStore.user.role) }}</p>
              </div>
              <div v-if="authStore.user.profile">
                <span class="text-sm text-gray-500">Сынып:</span>
                <p class="text-lg font-bold text-slate-900">{{ authStore.user.profile.grade_level }}</p>
              </div>
              <div v-if="authStore.user.subscription">
                <span class="text-sm text-gray-500">Жазылым:</span>
                <p class="text-lg font-bold text-slate-900">
                  {{ authStore.user.subscription.plan === 'PREMIUM' ? 'Премиум' : 'Тегін' }}
                  <span
                    :class="[
                      'ml-2 rounded px-2 py-1 text-xs',
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
          </section>
        </aside>
      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useGamificationStore } from '@/stores/gamification'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import type { UserRole } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()
const gamification = useGamificationStore()

const userInitial = computed(() => (authStore.user?.full_name || 'A')[0].toUpperCase())
const displayStreak = computed(() => Math.max(1, gamification.dailyStreak || 1))
const todayProgress = computed(() => Math.min(10, gamification.totalProblemsSolved % 11))
const todayGoalPercent = computed(() => Math.min(100, (todayProgress.value / 10) * 100))
const streakDays = computed(() => {
  const labels = ['Д', 'С', 'С', 'Б', 'Ж', 'С', 'Ж']
  const today = new Date().getDay()
  const mondayBasedToday = today === 0 ? 6 : today - 1
  return labels.map((label, index) => ({
    label,
    today: index === mondayBasedToday,
    done: index <= mondayBasedToday && index < Math.min(7, displayStreak.value),
  }))
})

onMounted(() => {
  gamification.fetchGamification().catch(() => {
    // Profile still renders with default gamification values.
  })
})

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

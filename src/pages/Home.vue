<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8">
      <GamificationBar v-if="isStudent" />
      <div
        class="mt-6 mb-6 grid gap-5"
        :class="{ 'lg:grid-cols-[minmax(0,1fr)_360px] lg:items-stretch': isStudent }"
      >
        <section class="study-hero">
          <div>
            <p class="study-hero__eyebrow">StudyPoint University</p>
            <h1>Оқу жолы</h1>
            <p>Сыныбыңды таңдап, тапсырма орында. Дұрыс жауаптар XP береді, ал coin жинасаң гаражда жаңа көлік пен стиль аша аласың.</p>
          </div>
        </section>

        <button v-if="isStudent" type="button" class="garage-entry" :aria-label="gameTitle" @click="openGameSelection">
          <span class="garage-entry__shine" aria-hidden="true"></span>
          <span class="garage-entry__icon" aria-hidden="true">
            <img v-if="gameSettings.isCarGame" src="/assets/garage-card-car.png" alt="" />
            <span v-else class="text-6xl text-white" aria-hidden="true">◉</span>
          </span>
          <span class="garage-entry__content">
            <small>Coin reward</small>
            <strong>{{ gameTitle }}</strong>
            <span>{{ gameSettings.isCarGame ? 'Жинаған coin арқылы көлігіңді ашып, безендір.' : 'Кейіпкеріңе шаш, киім және аксессуар таңда.' }}</span>
          </span>
          <span class="garage-entry__arrow" aria-hidden="true">
            <svg viewBox="0 0 20 20" fill="none">
              <path d="M7 4.5 12.5 10 7 15.5" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
        </button>
      </div>

      <div v-if="catalogStore.loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600">Жүктелуде...</p>
      </div>

      <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {{ error }}
      </div>

      <div v-else>
        <h2 class="text-2xl font-semibold mb-4">Қолжетімді сыныптар</h2>

        <div v-if="grades.length === 0" class="text-center py-12 text-gray-600">
          <p>Сыныптар табылмады</p>
        </div>

        <div v-else class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
          <button
            v-for="grade in grades"
            :key="grade.id"
            :class="[
              'relative flex h-[64px] w-full items-center rounded-full border-2 bg-white pl-16 pr-3 text-left transition-all duration-200 hover:-translate-y-0.5 hover:shadow-sm',
              getGradeCardClasses(grade.number).card,
            ]"
            @click="navigateToClass(grade.number)"
          >
            <span
              :class="[
                'absolute -left-2 top-1/2 flex h-[48px] w-[48px] -translate-y-1/2 items-center justify-center rounded-full font-bold text-white',
                getGradeBadgeTextClass(grade.label),
                getGradeCardClasses(grade.number).badge,
              ]"
            >
              {{ grade.label }}
            </span>
            <span
              :class="[
                'min-w-0 flex-1 truncate text-[14px] sm:text-[15px] font-medium leading-none',
                getGradeCardClasses(grade.number).text,
              ]"
            >
              {{ formatGradeTitle(grade) }}
            </span>
            <span
              :class="[
                'ml-2 inline-flex shrink-0 items-center justify-center',
                getGradeCardClasses(grade.number).arrow,
              ]"
              aria-hidden="true"
            >
              <svg viewBox="0 0 20 20" fill="none" class="h-5 w-5">
                <path
                  d="M7 4.5L12.5 10L7 15.5"
                  stroke="currentColor"
                  stroke-width="2.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </span>
          </button>
        </div>
      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCatalogStore } from '@/stores/catalog'
import { useGamificationStore } from '@/stores/gamification'
import { useGameSettingsStore } from '@/stores/gameSettings'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import GamificationBar from '@/components/gamification/GamificationBar.vue'

defineOptions({ name: 'HomePage' })

const router = useRouter()
const authStore = useAuthStore()
const catalogStore = useCatalogStore()
const gamificationStore = useGamificationStore()
const gameSettings = useGameSettingsStore()

const grades = ref(catalogStore.grades)
const error = ref<string | null>(null)
const isStudent = computed(() => authStore.user?.role === 'STUDENT')
const gameTitle = computed(() => (
  gameSettings.isCarGame
    ? 'Көлік гаражы'
    : gameSettings.isCharacterGame
      ? 'Кейіпкер әлемі'
      : 'Ойынды таңдау'
))

const openGameSelection = () => {
  void router.push({
    name: gameSettings.isCarGame
      ? 'garage'
      : gameSettings.isCharacterGame
        ? 'avatar-demo'
        : 'game-select',
  })
}

const gradeCardPalette = [
  {
    card: 'border-cyan-500',
    badge: 'bg-cyan-500',
    text: 'text-cyan-600',
    arrow: 'text-cyan-500',
  },
  {
    card: 'border-orange-500',
    badge: 'bg-orange-500',
    text: 'text-orange-500',
    arrow: 'text-orange-500',
  },
  {
    card: 'border-lime-500',
    badge: 'bg-lime-500',
    text: 'text-lime-600',
    arrow: 'text-lime-500',
  },
  {
    card: 'border-orange-600',
    badge: 'bg-orange-600',
    text: 'text-orange-600',
    arrow: 'text-orange-600',
  },
  {
    card: 'border-sky-500',
    badge: 'bg-sky-500',
    text: 'text-sky-500',
    arrow: 'text-sky-500',
  },
  {
    card: 'border-violet-500',
    badge: 'bg-violet-500',
    text: 'text-violet-500',
    arrow: 'text-violet-500',
  },
  {
    card: 'border-emerald-500',
    badge: 'bg-emerald-500',
    text: 'text-emerald-500',
    arrow: 'text-emerald-500',
  },
  {
    card: 'border-green-700',
    badge: 'bg-green-700',
    text: 'text-green-700',
    arrow: 'text-green-700',
  },
  {
    card: 'border-amber-500',
    badge: 'bg-amber-500',
    text: 'text-amber-500',
    arrow: 'text-amber-500',
  },
  {
    card: 'border-purple-600',
    badge: 'bg-purple-600',
    text: 'text-purple-600',
    arrow: 'text-purple-600',
  },
  {
    card: 'border-rose-600',
    badge: 'bg-rose-600',
    text: 'text-rose-600',
    arrow: 'text-rose-600',
  },
  {
    card: 'border-blue-600',
    badge: 'bg-blue-600',
    text: 'text-blue-600',
    arrow: 'text-blue-600',
  },
  {
    card: 'border-teal-500',
    badge: 'bg-teal-500',
    text: 'text-teal-500',
    arrow: 'text-teal-500',
  },
]

const getGradeCardClasses = (gradeNumber: number) => {
  const paletteIndex = Math.max(0, Math.min(gradeCardPalette.length - 1, gradeNumber + 1))
  return gradeCardPalette[paletteIndex]
}

const formatGradeTitle = (grade: { number: number; title: string }) => {
  return grade.title
}

const getGradeBadgeTextClass = (label: string) => {
  if (label.length > 2) return 'text-[12px] leading-none'
  return 'text-[18px]'
}

const navigateToClass = (gradeNumber: number) => {
  router.push({ name: 'class', params: { gradeId: gradeNumber } })
}

onMounted(async () => {
  gamificationStore.fetchProfile()
  if (isStudent.value) gameSettings.fetchGameSettings().catch(() => {})
  try {
    const fetchedGrades = await catalogStore.getGrades()
    grades.value = fetchedGrades
  } catch (err: unknown) {
    const e = err as { message?: string }
    error.value = e.message || 'Сыныптарды жүктеу мүмкін болмады'
    console.error('Failed to load grades:', err)
  }
})
</script>

<style scoped>
.study-hero {
  position: relative;
  display: flex;
  min-height: 190px;
  overflow: hidden;
  border-radius: 24px;
  background: #2dd4bf;
  color: #fff;
  padding: clamp(24px, 4vw, 36px);
  box-shadow: 0 24px 54px rgba(45, 212, 191, 0.2);
}

.study-hero h1 {
  margin: 0;
  font-size: clamp(32px, 5vw, 56px);
  font-weight: 950;
  line-height: 0.95;
}

.study-hero p {
  max-width: 680px;
  margin-top: 14px;
  color: rgba(255, 255, 255, 0.86);
  font-size: 16px;
  line-height: 1.6;
}

.study-hero__eyebrow {
  margin: 0 0 10px;
  color: rgba(236, 253, 245, 0.86);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0;
  text-transform: uppercase;
}

.garage-entry {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 16px;
  align-items: center;
  min-height: 190px;
  overflow: hidden;
  border: 1px solid rgba(245, 158, 11, 0.34);
  border-radius: 24px;
  background: #fcd34d;
  color: #1f2937;
  padding: 22px;
  width: 100%;
  font: inherit;
  text-align: left;
  cursor: pointer;
  box-shadow: 0 22px 48px rgba(217, 119, 6, 0.16);
  transition:
    transform 0.22s ease,
    box-shadow 0.22s ease,
    border-color 0.22s ease;
}

.garage-entry:hover {
  transform: translateY(-3px);
  border-color: rgba(245, 158, 11, 0.7);
  box-shadow: 0 28px 58px rgba(217, 119, 6, 0.24);
}

.garage-entry__shine {
  position: absolute;
  inset: -40% auto auto -30%;
  width: 180px;
  height: 300px;
  background: rgba(255, 255, 255, 0.52);
  transform: rotate(24deg);
  pointer-events: none;
}

.garage-entry__icon {
  position: relative;
  display: grid;
  place-items: center;
  width: 74px;
  height: 74px;
  border-radius: 22px;
  color: #f59e0b;
  background: #fff;
  box-shadow: inset 0 0 0 1px rgba(245, 158, 11, 0.16), 0 14px 24px rgba(245, 158, 11, 0.18);
}

.garage-entry__icon img {
  width: 86px;
  height: 86px;
  object-fit: contain;
}

.garage-entry__content {
  position: relative;
  display: grid;
  gap: 4px;
  min-width: 0;
}

.garage-entry__content small {
  color: #0891b2;
  font-size: 11px;
  font-weight: 950;
  text-transform: uppercase;
}

.garage-entry__content strong {
  color: #111827;
  font-size: 28px;
  font-weight: 950;
  line-height: 1;
}

.garage-entry__content span {
  color: #64748b;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.45;
}

.garage-entry__arrow {
  position: relative;
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 999px;
  color: #fff;
  background: #0f766e;
}

.garage-entry__arrow svg {
  width: 22px;
  height: 22px;
}

@media (max-width: 760px) {
  .study-hero {
    min-height: 220px;
  }

  .garage-entry {
    min-height: 160px;
    grid-template-columns: auto minmax(0, 1fr);
  }

  .garage-entry__arrow {
    display: none;
  }
}
</style>

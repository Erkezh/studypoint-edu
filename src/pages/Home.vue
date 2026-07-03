<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-6">Басты бет</h1>

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
              'relative flex h-[64px] w-full items-center rounded-[14px] border-2 bg-white pl-16 pr-3 text-left transition-all duration-200 hover:-translate-y-0.5 hover:shadow-sm',
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
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'

defineOptions({ name: 'HomePage' })

const router = useRouter()
const catalogStore = useCatalogStore()

const grades = ref(catalogStore.grades)
const error = ref<string | null>(null)

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

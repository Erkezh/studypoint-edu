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

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card
            v-for="grade in grades"
            :key="grade.id"
            clickable
            class="hover:shadow-xl transition-shadow"
            @click="navigateToClass(grade.number)"
          >
            <h3 class="text-xl font-semibold mb-2">{{ grade.title }}</h3>
            <p class="text-gray-600">{{ grade.number }} сынып</p>
          </Card>
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
import Card from '@/components/ui/Card.vue'

const router = useRouter()
const catalogStore = useCatalogStore()

const grades = ref(catalogStore.grades)
const error = ref<string | null>(null)

const navigateToClass = (gradeNumber: number) => {
  router.push({ name: 'class', params: { gradeId: gradeNumber } })
}

onMounted(async () => {
  try {
    const fetchedGrades = await catalogStore.getGrades()
    grades.value = fetchedGrades
  } catch (err: any) {
    error.value = err.message || 'Сыныптарды жүктеу мүмкін болмады'
    console.error('Failed to load grades:', err)
  }
})
</script>

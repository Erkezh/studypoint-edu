<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600">Нәтижелер жүктелуде...</p>
      </div>

      <div v-else-if="session">
        <h1 class="text-3xl font-bold mb-6">Сессия нәтижелері</h1>

        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div v-if="authStore.isAuthenticated">
              <span class="text-sm text-gray-500 block mb-1">SmartScore</span>
              <p class="text-3xl font-bold text-blue-600">{{ session.smartscore }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500 block mb-1">Дұрыс</span>
              <p class="text-3xl font-bold text-green-600">{{ session.correct_count }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500 block mb-1">Қате</span>
              <p class="text-3xl font-bold text-red-600">{{ session.wrong_count }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500 block mb-1">Уақыт</span>
              <p class="text-3xl font-bold">{{ formatTime(session.time_elapsed_sec) }}</p>
            </div>
          </div>

          <div class="mb-6">
            <h2 class="text-xl font-semibold mb-2">Дәлдік</h2>
            <div class="w-full bg-gray-200 rounded-full h-4">
              <div
                class="bg-green-600 h-4 rounded-full transition-all"
                :style="{ width: `${accuracy}%` }"
              ></div>
            </div>
            <p class="mt-2 text-sm text-gray-600">{{ accuracy }}% дұрыс жауаптар</p>
          </div>

          <div class="flex gap-4">
            <Button @click="goHome" variant="primary">Басты бетке</Button>
            <Button @click="goToAnalytics" variant="outline">Талдауға өту</Button>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-12 text-gray-600">
        <p>Нәтижелер табылмады</p>
        <Button @click="goHome" class="mt-4">Басты бетке</Button>
      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePracticeStore } from '@/stores/practice'
import { useCatalogStore } from '@/stores/catalog'
import { useAuthStore } from '@/stores/auth'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'
import type { PracticeSessionResponse } from '@/types/api'

interface Props {
  sessionId: string
}

const props = defineProps<Props>()
const router = useRouter()
const practiceStore = usePracticeStore()
const catalogStore = useCatalogStore()
const authStore = useAuthStore()

const session = ref<PracticeSessionResponse | null>(null)
const loading = ref(true)

const accuracy = computed(() => {
  if (!session.value || session.value.questions_answered === 0) return 0
  return Math.round((session.value.correct_count / session.value.questions_answered) * 100)
})

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const goHome = () => {
  router.push({ name: 'home' })
}

const goToAnalytics = () => {
  router.push({ name: 'analytics' })
}

onMounted(async () => {
  try {
    const fetchedSession = await practiceStore.getSession(props.sessionId)
    session.value = fetchedSession
    
    // Обновляем статистику навыка после завершения теста
    if (fetchedSession?.skill_id) {
      try {
        await catalogStore.getSkillStats(fetchedSession.skill_id)
      } catch (err) {
        console.warn('Failed to refresh skill stats:', err)
      }
    }
  } catch (err: any) {
    console.error('Failed to load session results:', err)
  } finally {
    loading.value = false
  }
})
</script>

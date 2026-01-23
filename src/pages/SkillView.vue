<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8">
      <div class="mb-6">
        <button
          @click="router.back()"
          class="text-blue-600 hover:text-blue-800 mb-4 flex items-center gap-2"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Назад
        </button>
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600">Загрузка...</p>
      </div>

      <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {{ error }}
      </div>

      <div v-else-if="skill">
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 class="text-3xl font-bold mb-4">{{ skill.title }}</h1>
          <p class="text-gray-600 mb-4">{{ skill.description || 'Описание отсутствует' }}</p>

          <div class="flex flex-wrap gap-4 mb-4">
            <div>
              <span class="text-sm text-gray-500">Код:</span>
              <span class="ml-2 font-medium">{{ skill.code }}</span>
            </div>
            <div>
              <span class="text-sm text-gray-500">Сложность:</span>
              <span class="ml-2 font-medium">{{ skill.difficulty }}/5</span>
            </div>
          </div>

          <div v-if="skill.tags.length > 0" class="flex flex-wrap gap-2 mb-6">
            <span
              v-for="tag in skill.tags"
              :key="tag"
              class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
            >
              {{ tag }}
            </span>
          </div>

          <div class="flex gap-4">
            <Button
              @click="startPractice"
              :loading="startingPractice"
              variant="primary"
              class="text-lg px-6 py-3"
            >
              Начать практику
            </Button>
            <Button
              v-if="skill.video_url"
              @click="openVideo"
              variant="outline"
            >
              Видео урок
            </Button>
            <Button
              v-if="skill.example_url"
              @click="openExample"
              variant="outline"
            >
              Примеры
            </Button>
          </div>
        </div>

        <div v-if="stats" class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold mb-4">Ваша статистика</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div v-if="authStore.isAuthenticated">
              <span class="text-sm text-gray-500">SmartScore</span>
              <p class="text-2xl font-bold">{{ stats.smartscore || 0 }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Правильных ответов</span>
              <p class="text-2xl font-bold text-green-600">{{ stats.correct || 0 }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Всего вопросов</span>
              <p class="text-2xl font-bold">{{ stats.total || 0 }}</p>
            </div>
          </div>
        </div>
      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'
import { usePracticeStore } from '@/stores/practice'
import { useAuthStore } from '@/stores/auth'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'

interface Props {
  skillId: string
}

const props = defineProps<Props>()
const router = useRouter()
const catalogStore = useCatalogStore()
const practiceStore = usePracticeStore()
const authStore = useAuthStore()

const skill = ref(catalogStore.skillDetails.get(parseInt(props.skillId, 10)))
const stats = ref<Record<string, any> | null>(null)
const loading = ref(true)
const startingPractice = ref(false)
const error = ref<string | null>(null)

const startPractice = async () => {
  if (!skill.value) return

  startingPractice.value = true
  error.value = null
  try {
    const skillId = parseInt(String(skill.value.id), 10)
    if (isNaN(skillId)) {
      throw new Error('Неверный ID навыка')
    }
    const session = await practiceStore.createSession(skillId)
    router.push({ name: 'practice', params: { sessionId: session.id } })
  } catch (err: any) {
    let errorMessage = 'Не удалось начать практику'
    
    if (err.response?.data?.detail) {
      // Ошибка валидации от FastAPI
      if (Array.isArray(err.response.data.detail)) {
        const validationErrors = err.response.data.detail
          .map((e: any) => `${e.loc?.join('.')}: ${e.msg}`)
          .join(', ')
        errorMessage = `Ошибка валидации: ${validationErrors}`
      } else if (typeof err.response.data.detail === 'string') {
        errorMessage = err.response.data.detail
      }
    } else if (err.response?.data?.message) {
      errorMessage = err.response.data.message
    } else if (err.message) {
      errorMessage = err.message
    }
    
    error.value = errorMessage
    console.error('Failed to start practice:', err.response?.data || err)
  } finally {
    startingPractice.value = false
  }
}

const openVideo = () => {
  if (skill.value?.video_url) {
    window.open(skill.value.video_url, '_blank')
  }
}

const openExample = () => {
  if (skill.value?.example_url) {
    window.open(skill.value.example_url, '_blank')
  }
}

onMounted(async () => {
  try {
    const skillId = parseInt(props.skillId, 10)
    const fetchedSkill = await catalogStore.getSkill(skillId)
    skill.value = fetchedSkill

    try {
      const fetchedStats = await catalogStore.getSkillStats(skillId)
      stats.value = fetchedStats
    } catch (err) {
      console.error('Failed to fetch stats:', err)
      // Stats не критичны, продолжаем работу
    }
  } catch (err: any) {
    error.value = err.message || 'Не удалось загрузить навык'
    console.error('Failed to load skill:', err)
  } finally {
    loading.value = false
  }
})
</script>

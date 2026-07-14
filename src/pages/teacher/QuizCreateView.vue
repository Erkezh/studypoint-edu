<template>
  <div class="quiz-create-view-page">
    <Header />
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p class="loading-text">Жүктелуде...</p>
    </div>
    <QuizCreator
      v-else
      :initial-quiz="quiz"
      @cancel="onCancel"
      @created="onCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuizStore } from '@/stores/quiz'
import Header from '@/components/layout/Header.vue'
import QuizCreator from '@/components/teacher/QuizCreator.vue'

const props = defineProps<{
  quizId?: string
}>()

const router = useRouter()
const quizStore = useQuizStore()

const loading = ref(false)

const quiz = computed(() => {
  if (!props.quizId) return null
  return quizStore.quizzes.find(q => q.id === props.quizId) || null
})

onMounted(async () => {
  if (props.quizId && quizStore.quizzes.length === 0) {
    loading.value = true
    try {
      await quizStore.fetchQuizzes()
    } catch (e) {
      console.error('Failed to load quizzes:', e)
    } finally {
      loading.value = false
    }
  }
})

const onCancel = () => {
  router.push({ path: '/teacher', query: { tab: 'quizzes' } })
}

const onCreated = () => {
  router.push({ path: '/teacher', query: { tab: 'quizzes' } })
}
</script>

<style scoped>
.quiz-create-view-page {
  min-height: 100vh;
  background-color: #f8fafc;
}
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}
.spinner {
  border: 4px solid rgba(16, 185, 129, 0.1);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border-left-color: #10b981;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}
.loading-text {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

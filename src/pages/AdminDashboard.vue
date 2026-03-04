<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8 max-w-6xl">
      <!-- Заголовок -->
      <div class="mb-8 flex items-center gap-3">
        <svg class="w-8 h-8 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Админ панелі</h1>
          <p class="text-gray-500">Барлық басқару құралдары бір жерде</p>
        </div>
      </div>

      <!-- Ошибки / Успех -->
      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {{ error }}
      </div>
      <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
        {{ successMessage }}
      </div>

      <!-- Статистика -->
      <section class="grid grid-cols-2 gap-4 mb-8">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 flex flex-col items-center">
          <svg class="w-8 h-8 text-blue-500 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" /></svg>
          <span class="text-2xl font-bold text-gray-900">{{ stats.topics }}</span>
          <span class="text-sm text-gray-500">Тақырыптар</span>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 flex flex-col items-center">
          <svg class="w-8 h-8 text-purple-500 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" /></svg>
          <span class="text-2xl font-bold text-gray-900">{{ stats.plugins }}</span>
          <span class="text-sm text-gray-500">Плагиндер</span>
        </div>
      </section>

      <!-- Навигация по разделам -->
      <section class="mb-8">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">Басқару бөлімдері</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <router-link
            to="/admin/plugins"
            class="group bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md hover:border-green-300 transition-all"
          >
            <svg class="w-8 h-8 text-green-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
            <h3 class="font-semibold text-gray-900 group-hover:text-green-700 transition-colors">Тест жүктеу</h3>
            <p class="text-sm text-gray-500 mt-1">TSX файлдан жаңа тест жүктеу</p>
          </router-link>

          <router-link
            to="/admin/topics"
            class="group bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md hover:border-blue-300 transition-all"
          >
            <svg class="w-8 h-8 text-blue-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" /></svg>
            <h3 class="font-semibold text-gray-900 group-hover:text-blue-700 transition-colors">Тақырыптар</h3>
            <p class="text-sm text-gray-500 mt-1">Тақырыптарды қосу және редакциялау</p>
          </router-link>

          <router-link
            to="/admin/questions/list"
            class="group bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md hover:border-purple-300 transition-all"
          >
            <svg class="w-8 h-8 text-purple-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <h3 class="font-semibold text-gray-900 group-hover:text-purple-700 transition-colors">Сұрақтар</h3>
            <p class="text-sm text-gray-500 mt-1">Тесттер мен сұрақтарды басқару, өңдеу, жою</p>
          </router-link>

          <router-link
            to="/admin/grades"
            class="group bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md hover:border-indigo-300 transition-all"
          >
            <svg class="w-8 h-8 text-indigo-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-2 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
            <h3 class="font-semibold text-gray-900 group-hover:text-indigo-700 transition-colors">Сыныптар</h3>
            <p class="text-sm text-gray-500 mt-1">Сыныптарды қосу, өңдеу және жою</p>
          </router-link>

          <router-link
            to="/admin/users"
            class="group bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md hover:border-teal-300 transition-all"
          >
            <svg class="w-8 h-8 text-teal-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354v.001A4.355 4.355 0 0012 13h.001A4.355 4.355 0 0012 4.355zM6 21.646C6 17.481 9.387 15 12 15s6 2.481 6 6.646v.354H6v-.354z" /></svg>
            <h3 class="font-semibold text-gray-900 group-hover:text-teal-700 transition-colors">Пайдаланушылар</h3>
            <p class="text-sm text-gray-500 mt-1">Рөлдерді тағайындау және тіркелгілерді басқару</p>
          </router-link>
        </div>
      </section>

      <!-- Быстрое управление темами -->
      <section class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" /></svg>
            <h2 class="text-xl font-semibold text-gray-800">Тақырыптар</h2>
          </div>
          <button
            @click="showTopicForm = !showTopicForm"
            class="flex items-center gap-1.5 text-sm px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors font-medium"
          >
            <svg v-if="!showTopicForm" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            {{ showTopicForm ? 'Жабу' : 'Жаңа тақырып' }}
          </button>
        </div>

        <!-- Форма создания темы -->
        <div v-if="showTopicForm" class="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-200">
          <form @submit.prevent="handleCreateTopic" class="flex flex-wrap gap-3 items-end">
            <div class="flex-1 min-w-[140px]">
              <label class="block text-xs font-medium text-gray-600 mb-1">Slug *</label>
              <input
                v-model="topicForm.slug"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-400 focus:border-green-400 outline-none"
                placeholder="arithmetic"
              />
            </div>
            <div class="flex-1 min-w-[140px]">
              <label class="block text-xs font-medium text-gray-600 mb-1">Атауы *</label>
              <input
                v-model="topicForm.title"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-400 focus:border-green-400 outline-none"
                placeholder="Арифметика"
              />
            </div>
            <div class="w-20">
              <label class="block text-xs font-medium text-gray-600 mb-1">Иконка</label>
              <input
                v-model="topicForm.icon"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-400 focus:border-green-400 outline-none"
                placeholder="📐"
              />
            </div>
            <button
              type="submit"
              :disabled="creatingTopic"
              class="flex items-center gap-1.5 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
              {{ creatingTopic ? '...' : 'Қосу' }}
            </button>
          </form>
        </div>

        <!-- Список тем -->
        <div v-if="loadingTopics" class="text-center py-6">
          <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
        </div>

        <div v-else-if="topicsList.length === 0" class="text-center py-6 text-gray-400">
          Тақырыптар жоқ. Жаңа тақырып қосыңыз!
        </div>

        <div v-else class="space-y-2">
          <div
            v-for="topic in topicsList"
            :key="topic.id"
            class="flex items-center justify-between px-4 py-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-center gap-3">
              <span class="text-xl">{{ topic.icon || '📁' }}</span>
              <div>
                <span class="font-medium text-gray-900">{{ topic.title }}</span>
                <span class="text-xs text-gray-400 ml-2">{{ topic.slug }}</span>
                <span
                  v-if="!topic.is_published"
                  class="inline-flex items-center gap-1 text-xs text-yellow-600 ml-2"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
                  жарияланбаған
                </span>
              </div>
            </div>
            <div class="flex gap-2">
              <router-link
                :to="'/admin/topics'"
                class="flex items-center gap-1 text-xs px-3 py-1.5 rounded border border-gray-200 hover:bg-gray-100 transition-colors text-gray-600"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                Өңдеу
              </router-link>
              <button
                @click="handleDeleteTopic(topic)"
                :disabled="deletingTopicId === topic.id"
                class="flex items-center gap-1 text-xs px-3 py-1.5 rounded border border-red-200 hover:bg-red-50 transition-colors text-red-600 disabled:opacity-50"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                {{ deletingTopicId === topic.id ? '...' : 'Жою' }}
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Header from '@/components/layout/Header.vue'
import { adminApi, type TopicListItem } from '@/api/admin'

const authStore = useAuthStore()
const router = useRouter()

const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const loadingTopics = ref(false)
const creatingTopic = ref(false)
const deletingTopicId = ref<number | null>(null)
const showTopicForm = ref(false)

const stats = ref({
  topics: 0,
  skills: 0,
  plugins: 0,
  questions: 0,
})

const topicsList = ref<TopicListItem[]>([])

const topicForm = ref({
  slug: '',
  title: '',
  icon: '',
})

// --- Load data ---

const loadStats = async () => {
  try {
    const [topicsRes, skillsRes, questionsRes] = await Promise.all([
      adminApi.listTopics(),
      adminApi.listSkills(),
      adminApi.listQuestions(),
    ])
    stats.value = {
      topics: Array.isArray(topicsRes.data) ? topicsRes.data.length : 0,
      skills: Array.isArray(skillsRes.data) ? skillsRes.data.length : 0,
      plugins: Array.isArray(questionsRes.data) ? questionsRes.data.length : 0,
      questions: Array.isArray(questionsRes.data) ? questionsRes.data.length : 0,
    }
  } catch (e) {
    console.error('Failed to load stats:', e)
  }
}

const loadTopics = async () => {
  loadingTopics.value = true
  try {
    const res = await adminApi.listTopics()
    topicsList.value = (res.data || []) as TopicListItem[]
  } catch (e) {
    console.error('Failed to load topics:', e)
    error.value = 'Тақырыптарды жүктеу қатесі'
  } finally {
    loadingTopics.value = false
  }
}

// --- Topic CRUD ---

const handleCreateTopic = async () => {
  if (!topicForm.value.slug || !topicForm.value.title) return
  creatingTopic.value = true
  error.value = null
  try {
    await adminApi.createTopic({
      slug: topicForm.value.slug,
      title: topicForm.value.title,
      icon: topicForm.value.icon || undefined,
      order: topicsList.value.length,
      is_published: true,
    })
    topicForm.value = { slug: '', title: '', icon: '' }
    successMessage.value = 'Тақырып сәтті қосылды!'
    setTimeout(() => { successMessage.value = null }, 3000)
    await Promise.all([loadTopics(), loadStats()])
  } catch (e: unknown) {
    console.error('Create topic error:', e)
    const err = e as { response?: { data?: { detail?: string } } }
    error.value = err.response?.data?.detail || 'Тақырыпты қосу қатесі'
  } finally {
    creatingTopic.value = false
  }
}

const handleDeleteTopic = async (topic: TopicListItem) => {
  if (!confirm(`"${topic.title}" тақырыбын жойғыңыз келе ме?`)) return
  deletingTopicId.value = topic.id
  error.value = null
  try {
    await adminApi.deleteTopic(topic.id)
    topicsList.value = topicsList.value.filter(t => t.id !== topic.id)
    stats.value.topics = topicsList.value.length
    successMessage.value = `"${topic.title}" тақырыбы жойылды`
    setTimeout(() => { successMessage.value = null }, 3000)
  } catch (e: unknown) {
    console.error('Delete topic error:', e)
    const err = e as { response?: { data?: { detail?: string } } }
    error.value = err.response?.data?.detail || 'Тақырыпты жою қатесі'
  } finally {
    deletingTopicId.value = null
  }
}

// --- Init ---

onMounted(async () => {
  if (!authStore.isAuthenticated || authStore.user?.role !== 'ADMIN') {
    router.push({ name: 'home' })
    return
  }
  await Promise.all([loadStats(), loadTopics()])
})
</script>

<template>
    <div class="min-h-screen bg-gray-50">
        <Header />
        <main class="container mx-auto px-4 py-8 max-w-4xl">
            <div class="mb-6">
                <h1 class="text-3xl font-bold mb-2">Тақырыптарды басқару</h1>
                <p class="text-gray-600">
                    Тақырыптар (категориялар) құру және редакциялау. Тақырыптар навыктарды топтастыру үшін қолданылады.
                </p>
            </div>

            <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                {{ error }}
            </div>

            <div v-if="successMessage"
                class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
                {{ successMessage }}
            </div>

            <!-- Форма создания/редактирования темы -->
            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
                <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
                    <span v-if="isEditing" class="flex items-center gap-2">
                        <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                        Тақырыпты өңдеу
                    </span>
                    <span v-else class="flex items-center gap-2">
                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
                        Жаңа тақырып қосу
                    </span>
                </h2>

                <form @submit.prevent="handleSubmit" class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- Slug -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Slug <span class="text-red-500">*</span>
                            </label>
                            <input v-model="formData.slug" type="text" required
                                class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                                placeholder="arithmetic" />
                            <p class="text-xs text-gray-500 mt-1">URL үшін бірегей идентификатор (латын әріптері)</p>
                        </div>

                        <!-- Название -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Атауы <span class="text-red-500">*</span>
                            </label>
                            <input v-model="formData.title" type="text" required
                                class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                                placeholder="Арифметика" />
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- Иконка -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Иконка (emoji)
                            </label>
                            <input v-model="formData.icon" type="text"
                                class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                                placeholder="📐" />
                        </div>

                        <!-- Порядок -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Реттілік
                            </label>
                            <input v-model.number="formData.order" type="number" min="0"
                                class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                                placeholder="0" />
                        </div>
                    </div>

                    <!-- Описание -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            Сипаттама
                        </label>
                        <textarea v-model="formData.description" rows="2"
                            class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                            placeholder="Тақырып сипаттамасы..."></textarea>
                    </div>

                    <!-- Опубликован -->
                    <div class="flex items-center gap-2">
                        <input v-model="formData.is_published" type="checkbox" id="is_published"
                            class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                        <label for="is_published" class="text-sm text-gray-700">Жарияланған</label>
                    </div>

                    <!-- Кнопки -->
                    <div class="flex gap-4 pt-2">
                        <Button type="submit" variant="primary" :loading="submitting" class="flex items-center gap-2">
                            <span v-if="isEditing" class="flex items-center gap-2">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" /></svg>
                                Сақтау
                            </span>
                            <span v-else class="flex items-center gap-2">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
                                Қосу
                            </span>
                        </Button>
                        <Button v-if="isEditing" type="button" variant="outline" @click="cancelEdit" class="flex items-center gap-2">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                            Болдырмау
                        </Button>
                        <Button type="button" variant="outline" @click="resetForm" class="flex items-center gap-2">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                            Тазалау
                        </Button>
                    </div>
                </form>
            </div>

            <!-- Список тем -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-xl font-semibold flex items-center gap-2">
                        <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
                        Барлық тақырыптар
                    </h2>
                    <Button @click="loadTopics" variant="outline" :loading="loading" class="flex items-center gap-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                        Жаңарту
                    </Button>
                </div>

                <div v-if="loading" class="text-center py-8">
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <p class="mt-2 text-gray-600">Жүктелуде...</p>
                </div>

                <div v-else-if="topicsList.length === 0" class="text-center py-8 text-gray-500">
                    Тақырыптар табылмады. Жаңа тақырып қосыңыз!
                </div>

                <div v-else class="space-y-3">
                    <div v-for="topic in topicsList" :key="topic.id"
                        class="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors">
                        <div class="flex items-center gap-3">
                            <span class="text-2xl" v-if="topic.icon">{{ topic.icon }}</span>
                            <svg v-else class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" /></svg>
                            <div>
                                <h3 class="font-semibold text-gray-900">{{ topic.title }}</h3>
                                <p class="text-sm text-gray-500 flex items-center gap-2">
                                    slug: {{ topic.slug }} | реттілік: {{ topic.order }}
                                    <span v-if="!topic.is_published" class="text-yellow-600 ml-2 flex items-center gap-1">
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
                                        жарияланбаған
                                    </span>
                                </p>
                            </div>
                        </div>
                        <div class="flex gap-2">
                            <Button @click="editTopic(topic)" variant="outline" class="text-blue-600 flex items-center gap-1">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                            </Button>
                            <Button @click="confirmDelete(topic)" variant="outline" class="text-red-600 hover:bg-red-50 flex items-center gap-1"
                                :loading="deletingTopicId === topic.id">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Модальное окно подтверждения удаления -->
            <div v-if="topicToDelete" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                @click.self="topicToDelete = null">
                <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                    <h3 class="text-xl font-semibold mb-4">Тақырыпты жою?</h3>
                    <p class="text-gray-600 mb-6">
                        <strong>"{{ topicToDelete.title }}"</strong> тақырыбын жойғыңыз келе ме?
                        Бұл тақырыпқа тіркелген навыктар тақырыпсыз қалады.
                    </p>
                    <div class="flex gap-4">
                        <Button @click="deleteTopic" variant="primary" class="bg-red-600 hover:bg-red-700 flex items-center gap-2"
                            :loading="deletingTopicId !== null">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                            Жою
                        </Button>
                        <Button @click="topicToDelete = null" variant="outline">
                            Болдырмау
                        </Button>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Header from '@/components/layout/Header.vue'
import Button from '@/components/ui/Button.vue'
import { adminApi, type TopicListItem, type TopicCreate, type TopicUpdate } from '@/api/admin'

const authStore = useAuthStore()
const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

const topicsList = ref<TopicListItem[]>([])
const topicToDelete = ref<TopicListItem | null>(null)
const deletingTopicId = ref<number | null>(null)

const isEditing = ref(false)
const editingTopicId = ref<number | null>(null)

const formData = ref({
    slug: '',
    title: '',
    description: '',
    icon: '',
    order: 0,
    is_published: true,
})

const resetForm = () => {
    formData.value = {
        slug: '',
        title: '',
        description: '',
        icon: '',
        order: 0,
        is_published: true,
    }
    isEditing.value = false
    editingTopicId.value = null
    error.value = null
    successMessage.value = null
}

const cancelEdit = () => {
    resetForm()
}

const loadTopics = async () => {
    loading.value = true
    error.value = null
    try {
        const response = await adminApi.listTopics()
        topicsList.value = response.data || []
    } catch (e: unknown) {
        console.error('Failed to load topics:', e)
        error.value = 'Тақырыптарды жүктеу қатесі'
    } finally {
        loading.value = false
    }
}

const editTopic = (topic: TopicListItem) => {
    isEditing.value = true
    editingTopicId.value = topic.id
    formData.value = {
        slug: topic.slug,
        title: topic.title,
        description: topic.description || '',
        icon: topic.icon || '',
        order: topic.order,
        is_published: topic.is_published,
    }
    window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleSubmit = async () => {
    submitting.value = true
    error.value = null
    successMessage.value = null

    if (!authStore.isAuthenticated || authStore.user?.role !== 'ADMIN') {
        error.value = 'Тек әкімшілер тақырып қоса алады!'
        submitting.value = false
        return
    }

    if (!formData.value.slug || !formData.value.title) {
        error.value = 'Slug және атауы міндетті!'
        submitting.value = false
        return
    }

    try {
        if (isEditing.value && editingTopicId.value) {
            // Обновление
            const updateData: TopicUpdate = {
                slug: formData.value.slug,
                title: formData.value.title,
                description: formData.value.description,
                icon: formData.value.icon || null,
                order: formData.value.order,
                is_published: formData.value.is_published,
            }
            const response = await adminApi.updateTopic(editingTopicId.value, updateData)

            // Обновляем локальный список без перезагрузки (избегаем race condition)
            if (response.data) {
                const index = topicsList.value.findIndex(t => t.id === editingTopicId.value)
                if (index !== -1) {
                    topicsList.value.splice(index, 1, response.data)
                }
            }

            successMessage.value = 'Тақырып сәтті жаңартылды!'
        } else {
            // Создание
            const createData: TopicCreate = {
                slug: formData.value.slug,
                title: formData.value.title,
                description: formData.value.description,
                icon: formData.value.icon || undefined,
                order: formData.value.order,
                is_published: formData.value.is_published,
            }
            const response = await adminApi.createTopic(createData)

            // Добавляем в локальный список
            if (response.data) {
                topicsList.value.push(response.data)
                // Сортируем по order
                topicsList.value.sort((a, b) => a.order - b.order)
            }

            successMessage.value = 'Тақырып сәтті қосылды!'
        }

        resetForm()
        // await loadTopics() - Removed to avoid race condition
    } catch (e: unknown) {
        console.error('Failed to save topic:', e)
        const err = e as { response?: { data?: { detail?: string } } }
        error.value = err.response?.data?.detail || 'Тақырыпты сақтау қатесі'
    } finally {
        submitting.value = false
    }
}

const confirmDelete = (topic: TopicListItem) => {
    topicToDelete.value = topic
}

const deleteTopic = async () => {
    if (!topicToDelete.value) return

    const deletedId = topicToDelete.value.id
    const deletedTitle = topicToDelete.value.title
    deletingTopicId.value = deletedId
    error.value = null

    try {
        await adminApi.deleteTopic(deletedId)
        // Удаляем из локального списка сразу (не перезагружаем, чтобы избежать race condition)
        topicsList.value = topicsList.value.filter(t => t.id !== deletedId)
        successMessage.value = `"${deletedTitle}" тақырыбы жойылды`
        topicToDelete.value = null
    } catch (e: unknown) {
        console.error('Failed to delete topic:', e)
        const err = e as { response?: { data?: { detail?: string } } }
        error.value = err.response?.data?.detail || 'Тақырыпты жою қатесі'
    } finally {
        deletingTopicId.value = null
    }
}

onMounted(async () => {
    if (!authStore.isAuthenticated || authStore.user?.role !== 'ADMIN') {
        router.push({ name: 'home' })
        return
    }
    await loadTopics()
})
</script>

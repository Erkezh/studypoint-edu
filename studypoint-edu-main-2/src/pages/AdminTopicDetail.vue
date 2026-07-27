<template>
    <div class="min-h-screen bg-gray-50">
        <Header />
        <main class="container mx-auto px-4 py-8 max-w-5xl">
            <!-- Back button -->
            <button @click="router.push({ name: 'admin-topics' })"
                class="mb-6 flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
                Тақырыптарға қайту
            </button>

            <div v-if="loading" class="text-center py-12">
                <div class="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
                <p class="mt-3 text-gray-600">Жүктелуде...</p>
            </div>

            <div v-else-if="!topic" class="text-center py-12 text-gray-500">
                Тақырып табылмады
            </div>

            <template v-else>
                <!-- Theme Header -->
                <div class="bg-white rounded-xl shadow-sm p-6 mb-6 border border-gray-200">
                    <div class="flex flex-col sm:flex-row items-start justify-between gap-4">
                        <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                            <span class="text-4xl" v-if="topic.icon">{{ topic.icon }}</span>
                            <div>
                                <h1 class="text-2xl font-bold text-gray-900 leading-tight">{{ topic.title }}</h1>
                                <p class="text-xs text-gray-500 mt-1">slug: {{ topic.slug }} · реттілік: {{ topic.order }}</p>
                                <p v-if="topic.description" class="text-sm text-gray-600 mt-2">{{ topic.description }}</p>
                            </div>
                        </div>
                        <span :class="topic.is_published ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                            class="text-xs font-medium px-2.5 py-1 rounded-full shrink-0">
                            {{ topic.is_published ? 'Жарияланған' : 'Жарияланбаған' }}
                        </span>
                    </div>
                </div>

                <!-- Error / Success -->
                <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-4">{{ error }}</div>
                <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg mb-4">{{ successMessage }}</div>

                <!-- Create Subtheme Form -->
                <div class="bg-white rounded-xl shadow-sm p-6 mb-6 border border-gray-200">
                    <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
                        <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
                        {{ editingSubthemeId ? 'Ішкі тақырыпты өңдеу' : 'Жаңа ішкі тақырып қосу' }}
                    </h2>
                    <form @submit.prevent="handleSubthemeSubmit" class="flex flex-col sm:flex-row flex-wrap gap-4 items-end">
                        <div class="w-full sm:flex-1 min-w-[150px]">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Slug *</label>
                            <input v-model="subForm.slug" type="text" required
                                class="w-full p-2.5 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
                                placeholder="addition" />
                        </div>
                        <div class="w-full sm:flex-1 min-w-[150px]">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Атауы *</label>
                            <input v-model="subForm.title" type="text" required
                                class="w-full p-2.5 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
                                placeholder="Қосу" />
                        </div>
                        <div class="w-full sm:w-24">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Реттілік</label>
                            <input v-model.number="subForm.order" type="number" min="0"
                                class="w-full p-2.5 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
                                placeholder="0" />
                        </div>
                        <div class="flex gap-2">
                            <Button type="submit" variant="primary" :loading="submitting" class="whitespace-nowrap">
                                {{ editingSubthemeId ? 'Сақтау' : 'Қосу' }}
                            </Button>
                            <Button v-if="editingSubthemeId" type="button" variant="outline" @click="resetSubForm">
                                Болдырмау
                            </Button>
                        </div>
                    </form>
                </div>

                <!-- Unassigned Skills (direct on theme - need to be moved to subthemes) -->
                <div v-if="directSkills.length > 0" class="bg-white rounded-xl shadow-sm p-6 mb-6 border border-orange-200">
                    <h2 class="text-lg font-semibold mb-3 text-orange-700 flex items-center gap-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
                        Тесттер (ішкі тақырыпсыз) — {{ directSkills.length }} тест
                    </h2>
                    <p class="text-sm text-gray-500 mb-3">Бұл тесттер тікелей тақырыпқа тіркелген, бірақ ішкі тақырыпқа бөлінбеген. Әрбір тесті ішкі тақырыпқа тасымалдау үшін таңдаңыз:</p>
                    <div class="space-y-2">
                        <div v-for="skill in directSkills" :key="skill.id"
                            class="flex flex-col sm:flex-row items-start sm:items-center justify-between py-3 px-3 rounded-lg bg-orange-50 border border-orange-100 gap-3">
                            <div class="flex items-center gap-3">
                                <span class="text-xs font-mono text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">{{ skill.code }}</span>
                                <span class="text-sm text-gray-700">{{ skill.title }}</span>
                                <span class="text-xs text-gray-400">grade_id: {{ skill.grade_id }}</span>
                            </div>
                            <div class="flex items-center gap-2 w-full sm:w-auto" v-if="subthemes.length > 0">
                                <select v-model="moveTargets[skill.id]"
                                    class="text-xs p-1.5 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:outline-none flex-1 sm:flex-none">
                                    <option :value="undefined">-- Ішкі тақырыпқа --</option>
                                    <option v-for="sub in subthemes" :key="sub.id" :value="sub.id">{{ sub.title }}</option>
                                </select>
                                <button @click="moveSkillToSubtheme(skill.id)"
                                    :disabled="!moveTargets[skill.id]"
                                    class="text-sm text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed px-3 py-1.5 rounded-lg transition-colors shrink-0">
                                    →
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Subthemes List -->
                <div v-if="subthemes.length === 0" class="bg-white rounded-xl shadow-sm p-8 text-center text-gray-500 border border-gray-200">
                    Ішкі тақырыптар жоқ. Жоғарыда жаңасын қосыңыз!
                </div>
                <div v-else class="space-y-4">
                    <div v-for="sub in subthemes" :key="sub.id"
                        class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                        <!-- Subtheme Header -->
                        <div class="flex items-center justify-between p-4 bg-gray-50 border-b border-gray-100 cursor-pointer"
                            @click="toggleSubtheme(sub.id)">
                            <div class="flex items-center gap-3">
                                <svg :class="expandedSubs.has(sub.id) ? 'rotate-90' : ''" class="w-4 h-4 text-gray-400 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                                <div>
                                    <h3 class="font-semibold text-gray-800">{{ sub.title }}</h3>
                                    <p class="text-xs text-gray-500">slug: {{ sub.slug }} · реттілік: {{ sub.order }} · {{ sub.skills?.length || 0 }} тест</p>
                                </div>
                            </div>
                            <div class="flex gap-2" @click.stop>
                                <button @click="editSubtheme(sub)" class="text-blue-600 hover:text-blue-800 p-1.5 rounded hover:bg-blue-50" title="Өңдеу">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                                </button>
                                <button @click="confirmDeleteSubtheme(sub)" class="text-red-600 hover:text-red-800 p-1.5 rounded hover:bg-red-50" title="Жою">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                                </button>
                            </div>
                        </div>

                        <!-- Skills inside subtheme (expanded) -->
                        <div v-if="expandedSubs.has(sub.id)" class="p-4">
                            <!-- Assign existing skill to this subtheme -->
                            <div class="mb-4 flex flex-wrap gap-3 items-end p-3 bg-blue-50 rounded-lg">
                                <div class="flex-[3] min-w-[250px]">
                                    <label class="block text-xs font-medium text-gray-600 mb-1">Бар тестті қосу</label>
                                    <select v-model.number="assignSkillSelects[sub.id]"
                                        class="w-full p-2 text-sm border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white">
                                        <option :value="0">-- Тест таңдаңыз --</option>
                                        <option v-for="skill in availableSkills" :key="skill.id" :value="skill.id">
                                            [{{ skill.code }}] {{ skill.title }} (grade: {{ skill.grade_id }})
                                        </option>
                                    </select>
                                </div>
                                <Button @click="assignSkillToSubtheme(sub.id)" variant="primary" class="text-sm whitespace-nowrap"
                                    :loading="addingSkillToSub === sub.id"
                                    :disabled="!assignSkillSelects[sub.id]">
                                    + Тестті қосу
                                </Button>
                            </div>

                            <!-- Skills list -->
                            <div v-if="!sub.skills || sub.skills.length === 0" class="text-center text-gray-400 text-sm py-4">
                                Тесттер жоқ
                            </div>
                            <div v-else class="space-y-1">
                                <div v-for="(skill, idx) in sub.skills" :key="skill.id"
                                    class="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50 group transition-colors">
                                    <div class="flex items-center gap-3">
                                        <span class="text-xs font-medium text-gray-400 w-5 text-right">{{ idx + 1 }}</span>
                                        <span class="text-xs font-mono text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">{{ skill.code }}</span>
                                        <span class="text-sm text-gray-700">{{ skill.title }}</span>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <span class="text-xs text-gray-400">grade: {{ skill.grade_id }}</span>
                                        <button @click="unassignSkill(skill.id)"
                                            class="text-red-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity p-1" title="Алып тастау">
                                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </template>

            <!-- Delete Confirmation Modal -->
            <div v-if="subToDelete" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="subToDelete = null">
                <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                    <h3 class="text-xl font-semibold mb-4">Ішкі тақырыпты жою?</h3>
                    <p class="text-gray-600 mb-6"><strong>"{{ subToDelete.title }}"</strong> ішкі тақырыбын жойғыңыз келе ме?</p>
                    <div class="flex gap-4">
                        <Button @click="deleteSubtheme" variant="primary" class="bg-red-600 hover:bg-red-700" :loading="deletingSubId !== null">Жою</Button>
                        <Button @click="subToDelete = null" variant="outline">Болдырмау</Button>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCatalogStore } from '@/stores/catalog'
import Header from '@/components/layout/Header.vue'
import Button from '@/components/ui/Button.vue'
import { adminApi } from '@/api/admin'
import { catalogApi } from '@/api/catalog'

interface SkillData {
    id: number
    subject_id: number
    grade_id: number
    topic_id: number | null
    code: string
    title: string
    difficulty: number
    tags: string[]
    is_published: boolean
}

interface SubthemeData {
    id: number
    slug: string
    title: string
    description: string
    icon: string | null
    order: number
    is_published: boolean
    parent_id: number | null
    skills: SkillData[]
}

interface TopicDetailData {
    id: number
    slug: string
    title: string
    description: string
    icon: string | null
    order: number
    is_published: boolean
    parent_id: number | null
    subthemes: SubthemeData[]
    skills: SkillData[]
}

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const catalogStore = useCatalogStore()

const topicId = computed(() => parseInt(route.params.topicId as string, 10))
const loading = ref(true)
const submitting = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

const topic = ref<TopicDetailData | null>(null)
const subthemes = ref<SubthemeData[]>([])
const directSkills = ref<SkillData[]>([])
const expandedSubs = ref<Set<number>>(new Set())
const grades = ref<{ id: number; number: number; title: string }[]>([])

// All skills in the system (for assigning to subthemes)
const allSkills = ref<SkillData[]>([])

// Subtheme form
const editingSubthemeId = ref<number | null>(null)
const subForm = ref({ slug: '', title: '', order: 0 })

// Assign existing skill selects per subtheme
const assignSkillSelects = reactive<Record<number, number>>({})
const addingSkillToSub = ref<number | null>(null)

// Move targets for direct skills
const moveTargets = reactive<Record<number, number | undefined>>({})

// Delete state
const subToDelete = ref<SubthemeData | null>(null)
const deletingSubId = ref<number | null>(null)

// Computed: skills that are not yet in any subtheme (available for assignment)
const availableSkills = computed(() => {
    const assignedIds = new Set<number>()
    subthemes.value.forEach(s => {
        s.skills?.forEach(sk => assignedIds.add(sk.id))
    })
    directSkills.value.forEach(sk => assignedIds.add(sk.id))
    // Show skills that are NOT already in a subtheme of this theme
    return allSkills.value.filter(sk => !assignedIds.has(sk.id))
})

const toggleSubtheme = (subId: number) => {
    if (expandedSubs.value.has(subId)) {
        expandedSubs.value.delete(subId)
    } else {
        expandedSubs.value.add(subId)
        if (!assignSkillSelects[subId]) {
            assignSkillSelects[subId] = 0
        }
    }
}

const resetSubForm = () => {
    subForm.value = { slug: '', title: '', order: 0 }
    editingSubthemeId.value = null
}

const loadTopic = async () => {
    loading.value = true
    error.value = null
    try {
        const resp = await adminApi.getTopicDetail(topicId.value)
        const data = resp.data as unknown as TopicDetailData
        topic.value = data
        subthemes.value = data.subthemes || []
        directSkills.value = data.skills || []

        // Expand all and init assign selects
        subthemes.value.forEach(s => {
            expandedSubs.value.add(s.id)
            if (!assignSkillSelects[s.id]) {
                assignSkillSelects[s.id] = 0
            }
        })
    } catch (e: unknown) {
        console.error('Failed to load topic detail:', e)
        error.value = 'Тақырыпты жүктеу қатесі'
    } finally {
        loading.value = false
    }
}

const loadAllSkills = async () => {
    try {
        const resp = await catalogApi.getSkills({ page_size: 500 })
        allSkills.value = (resp.data as unknown as SkillData[]) || []
    } catch (e) {
        console.error('Failed to load skills:', e)
    }
}

const handleSubthemeSubmit = async () => {
    if (!subForm.value.slug || !subForm.value.title) {
        error.value = 'Slug және атауы міндетті!'
        return
    }
    submitting.value = true
    error.value = null
    successMessage.value = null

    try {
        if (editingSubthemeId.value) {
            await adminApi.updateTopic(editingSubthemeId.value, {
                slug: subForm.value.slug,
                title: subForm.value.title,
                order: subForm.value.order,
                parent_id: topicId.value,
            })
            successMessage.value = 'Ішкі тақырып жаңартылды!'
        } else {
            await adminApi.createTopic({
                slug: subForm.value.slug,
                title: subForm.value.title,
                order: subForm.value.order,
                is_published: true,
                parent_id: topicId.value,
            })
            successMessage.value = 'Ішкі тақырып қосылды!'
        }
        resetSubForm()
        await loadTopic()
    } catch (e: unknown) {
        const err = e as { response?: { data?: { detail?: string } } }
        error.value = err.response?.data?.detail || 'Ішкі тақырыпты сақтау қатесі'
    } finally {
        submitting.value = false
    }
}

const editSubtheme = (sub: SubthemeData) => {
    editingSubthemeId.value = sub.id
    subForm.value = { slug: sub.slug, title: sub.title, order: sub.order }
    window.scrollTo({ top: 0, behavior: 'smooth' })
}

const confirmDeleteSubtheme = (sub: SubthemeData) => {
    subToDelete.value = sub
}

const deleteSubtheme = async () => {
    if (!subToDelete.value) return
    deletingSubId.value = subToDelete.value.id
    try {
        await adminApi.deleteTopic(subToDelete.value.id)
        subToDelete.value = null
        successMessage.value = 'Ішкі тақырып жойылды!'
        await loadTopic()
    } catch (e: unknown) {
        const err = e as { response?: { data?: { detail?: string } } }
        error.value = err.response?.data?.detail || 'Ішкі тақырыпты жою қатесі'
    } finally {
        deletingSubId.value = null
    }
}

const assignSkillToSubtheme = async (subId: number) => {
    const skillId = assignSkillSelects[subId]
    if (!skillId) return
    addingSkillToSub.value = subId
    error.value = null
    try {
        await adminApi.updateSkill(skillId, { topic_id: subId })
        assignSkillSelects[subId] = 0
        successMessage.value = 'Тест ішкі тақырыпқа қосылды!'
        await loadTopic()
        await loadAllSkills()
    } catch (e: unknown) {
        const err = e as { response?: { data?: { detail?: string; error?: { message?: string } } } }
        error.value = err.response?.data?.error?.message || err.response?.data?.detail || 'Тестті қосу қатесі'
    } finally {
        addingSkillToSub.value = null
    }
}

const moveSkillToSubtheme = async (skillId: number) => {
    const targetSubId = moveTargets[skillId]
    if (!targetSubId) return
    error.value = null
    try {
        await adminApi.updateSkill(skillId, { topic_id: targetSubId })
        moveTargets[skillId] = undefined
        successMessage.value = 'Тест ішкі тақырыпқа тасымалданды!'
        await loadTopic()
        await loadAllSkills()
    } catch (e: unknown) {
        console.error(e)
        error.value = 'Тестті тасымалдау қатесі'
    }
}

const unassignSkill = async (skillId: number) => {
    try {
        // Move skill back to the parent theme (not null, but to the theme itself)
        await adminApi.updateSkill(skillId, { topic_id: topicId.value })
        successMessage.value = 'Тест алып тасталды'
        await loadTopic()
        await loadAllSkills()
    } catch (e: unknown) {
        console.error(e)
        error.value = 'Тестті алып тастау қатесі'
    }
}

onMounted(async () => {
    if (!authStore.isAuthenticated || authStore.user?.role !== 'ADMIN') {
        router.push({ name: 'home' })
        return
    }
    // Load grades
    await catalogStore.getGrades()
    grades.value = catalogStore.grades.map(g => ({ id: g.id, number: g.number, title: g.title }))

    await Promise.all([loadTopic(), loadAllSkills()])
})
</script>

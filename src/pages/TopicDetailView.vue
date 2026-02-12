<template>
  <div class="min-h-screen bg-white font-sans flex flex-col">
    <Header />

    <!-- View Toggle -->
    <div class="bg-white border-b border-gray-200">
       <ViewByToggle />
    </div>

    <main class="flex flex-1 relative">
      <!-- Sidebar (Topics List) -->
      <aside class="relative shrink-0 w-48 z-30 hidden md:block border-r border-gray-200 bg-gray-50">
        <div class="sticky top-0 h-[calc(100vh-120px)] overflow-y-auto py-4">
             <div class="px-4 mb-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Тақырыптар</div>
             <nav class="flex flex-col gap-0.5 px-2">
                <router-link
                  v-for="(topic, index) in topics"
                  :key="topic.id"
                  :to="{ name: 'topic-detail', params: { topicSlug: topic.slug } }"
                  class="flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  :class="[
                    currentTopicSlug === topic.slug
                      ? 'bg-white text-green-700 shadow-sm border border-gray-100 font-bold'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  ]"
                >
                  <!-- Color Dot -->
                  <div :class="['w-2.5 h-2.5 rounded-full mr-2.5 shrink-0', getColorClass(index)]"></div>
                  <span class="truncate">{{ topic.title }}</span>
                </router-link>
             </nav>
        </div>
      </aside>

      <!-- Main Content -->
      <div class="flex-1 w-full px-6 lg:px-10 py-8">

        <div v-if="loading" class="flex justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
        </div>

        <div v-else-if="currentTopic">
            <!-- Hero Header -->
            <div class="mb-8">
                <h1 class="text-3xl font-bold text-green-700 mb-3">{{ currentTopic.title }}</h1>
                <p class="text-gray-600 text-base max-w-4xl leading-relaxed">
                    {{ currentTopic.description || `Мұнда "${currentTopic.title}" тақырыбына қатысты барлық дағдылар тізімі берілген. Бұл дағдылар сынып бойынша топтастырылған. Кез келген дағды атауына басып, жаттығуды бастаңыз.` }}
                </p>
            </div>

            <!-- Skills Grouped by Grade (Masonry Columns) -->
            <div class="columns-1 md:columns-2 lg:columns-3 gap-8">
                <div v-for="gradeGroup in gradeGroups" :key="gradeGroup.gradeId" class="break-inside-avoid mb-8">
                    <h2 :class="['text-lg font-bold mb-3', gradeGroup.colorClass]">
                         {{ gradeGroup.title }}
                    </h2>

                    <div class="space-y-0.5 pl-1">
                        <div v-for="(skill, idx) in gradeGroup.skills" :key="skill.id"
                          class="group/skill flex items-start gap-2 py-0.5 px-1 rounded hover:bg-green-50 cursor-pointer transition-colors"
                          @click="navigateToSkill(skill.id)">
                            <span class="text-sm font-medium text-gray-400 w-5 text-right shrink-0 pt-px">{{ idx + 1 }}</span>
                            <div class="flex-1 flex items-center justify-between min-w-0 gap-2">
                                <span class="text-sm text-gray-700 group-hover/skill:text-green-700 group-hover/skill:underline decoration-green-700/50 underline-offset-2 leading-snug truncate">
                                    {{ skill.title }}
                                </span>
                                <!-- Admin Edit Button -->
                                <button v-if="authStore.user?.role === 'ADMIN'"
                                  @click.stop="openEditModal(skill)"
                                  class="text-gray-300 hover:text-blue-500 opacity-0 group-hover/skill:opacity-100 transition-opacity shrink-0"
                                  title="Edit Skill">
                                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="gradeGroups.length === 0" class="text-center py-12 text-gray-500">
                Бұл тақырып бойынша дағдылар әлі қосылмаған.
            </div>
        </div>

        <div v-else class="text-center py-12 text-red-500">
            Тақырып табылмады.
        </div>

      </div>

      <!-- Edit Skill Modal -->
      <EditSkillModal
        :is-visible="isEditModalOpen"
        :skill="editingSkill"
        @close="closeEditModal"
        @save="onSkillSaved"
      />
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'
import { useAuthStore } from '@/stores/auth'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import ViewByToggle from '@/components/ui/ViewByToggle.vue'
import EditSkillModal from '@/components/catalog/EditSkillModal.vue'
import type { SkillListItem } from '@/types/api'

const route = useRoute()
const router = useRouter()
const catalogStore = useCatalogStore()
const authStore = useAuthStore()

const isEditModalOpen = ref(false)
const editingSkill = ref<SkillListItem | null>(null)

const currentTopicSlug = computed(() => route.params.topicSlug as string)
const topics = computed(() => catalogStore.topics)
const loading = computed(() => catalogStore.loading)

const currentTopic = computed(() => {
    return topics.value.find(t => t.slug === currentTopicSlug.value)
})

// Build a map of grade_id -> grade info for proper titles
const gradeMap = computed(() => {
    const map = new Map<number, { number: number; title: string }>()
    for (const g of catalogStore.grades) {
        map.set(g.id, { number: g.number, title: g.title })
    }
    return map
})

const getKazakhGradeTitle = (gradeNumber: number): string => {
    if (gradeNumber === -1) return 'Мектепалды даярлық дағдылары'
    if (gradeNumber === 0) return 'Даярлық сынып дағдылары'
    const mapping: Record<number, string> = {
        1: 'Бірінші',
        2: 'Екінші',
        3: 'Үшінші',
        4: 'Төртінші',
        5: 'Бесінші',
        6: 'Алтыншы',
        7: 'Жетінші',
        8: 'Сегізінші',
        9: 'Тоғызыншы',
        10: 'Оныншы',
        11: 'Он бірінші'
    }
    return `${mapping[gradeNumber] || gradeNumber}-сынып дағдылары`
}

// Group skills by grade, produce array of groups sorted by grade number
const gradeGroups = computed(() => {
    const grouped: Record<string, SkillListItem[]> = {}

    const sortedSkills = [...catalogStore.skills].sort((a, b) => {
        if (a.grade_id !== b.grade_id) return a.grade_id - b.grade_id
        return a.code.localeCompare(b.code, undefined, { numeric: true })
    })

    sortedSkills.forEach(skill => {
        const key = skill.grade_id.toString()
        if (!grouped[key]) grouped[key] = []
        grouped[key].push(skill)
    })

    const gradeColors = [
        'text-sky-600', 'text-green-600', 'text-orange-600',
        'text-purple-600', 'text-teal-600', 'text-red-600',
        'text-blue-600', 'text-lime-600', 'text-indigo-600'
    ]

    return Object.entries(grouped).map(([gradeIdStr, skills], idx) => {
        const gradeId = parseInt(gradeIdStr)
        const gradeInfo = gradeMap.value.get(gradeId)
        const gradeNumber = gradeInfo?.number ?? gradeId
        const title = getKazakhGradeTitle(gradeNumber)

        return {
            gradeId,
            gradeNumber,
            title,
            skills,
            colorClass: gradeColors[idx % gradeColors.length]
        }
    }).sort((a, b) => a.gradeNumber - b.gradeNumber)
})

const navigateToSkill = (skillId: number) => {
    router.push({ name: 'skill', params: { skillId } })
}

const fetchTopicData = async () => {
    // Load grades for proper grade titles
    if (catalogStore.grades.length === 0) {
        await catalogStore.getGrades()
    }

    if (topics.value.length === 0) {
        await catalogStore.getTopics()
    }

    if (currentTopic.value) {
        await catalogStore.getSkills({ topic_id: currentTopic.value.id }, true)
    }
}

onMounted(() => {
    fetchTopicData()
})

watch(currentTopicSlug, () => {
    fetchTopicData()
})

// Helpers
const getColorClass = (index: number) => {
    const colors = ['bg-orange-400', 'bg-teal-400', 'bg-purple-400', 'bg-lime-400', 'bg-red-400', 'bg-blue-400', 'bg-indigo-400']
    return colors[index % colors.length]
}

const openEditModal = (skill: SkillListItem) => {
  editingSkill.value = skill
  isEditModalOpen.value = true
}

const closeEditModal = () => {
  isEditModalOpen.value = false
  editingSkill.value = null
}

const onSkillSaved = async () => {
    // Refresh skills for current topic
    // if (currentTopic.value) {
    //     await catalogStore.getSkills({ topic_id: currentTopic.value.id }, true)
    // }
    // No need to refetch, store is updated optimistically
}
</script>

<template>
  <div class="min-h-screen bg-white font-sans flex flex-col">
    <Header />

    <!-- View Toggle -->
    <div class="bg-white border-b border-gray-200">
       <ViewByToggle />
    </div>

    <main class="flex flex-1 relative">
      <!-- Sidebar (Topics List) -->
      <aside class="relative shrink-0 w-64 z-30 hidden md:block border-r border-gray-200 bg-gray-50">
        <div class="sticky top-0 h-[calc(100vh-120px)] overflow-y-auto py-4">
             <div class="px-4 mb-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Topics</div>
             <nav class="flex flex-col gap-1 px-2">
                <router-link
                  v-for="(topic, index) in topics"
                  :key="topic.id"
                  :to="{ name: 'topic-detail', params: { topicSlug: topic.slug } }"
                  class="flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  :class="[
                    currentTopicSlug === topic.slug
                      ? 'bg-white text-sky-600 shadow-sm border border-gray-100'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  ]"
                >
                  <!-- Color Dot -->
                  <div :class="['w-2 h-2 rounded-full mr-3', getColorClass(index)]"></div>
                  {{ topic.title }}
                </router-link>
             </nav>
        </div>
      </aside>

      <!-- Main Content -->
      <div class="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        <div v-if="loading" class="flex justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600"></div>
        </div>

        <div v-else-if="currentTopic">
            <!-- Hero Header -->
            <div class="mb-10">
                <h1 class="text-4xl font-bold text-sky-600 mb-4">{{ currentTopic.title }}</h1>
                <p class="text-gray-600 text-lg max-w-3xl">
                    {{ currentTopic.description || `Here is a list of all of the skills that cover ${currentTopic.title.toLowerCase()}! These skills are organized by grade, and you can move your mouse over any skill name to preview the skill.` }}
                </p>
            </div>

            <!-- Skills Grouped by Grade -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-12">
                <div v-for="(skills, gradeKey) in skillsByGrade" :key="gradeKey" class="break-inside-avoid mb-8">
                    <h2 :class="['text-xl font-bold mb-4', getGradeColorClass(gradeKey)]">
                         {{ getGradeTitle(gradeKey) }}
                    </h2>

                    <ul class="space-y-2">
                        <li v-for="skill in skills" :key="skill.id" class="group relative pl-6">
                            <span class="absolute left-0 text-xs font-medium text-gray-400 w-5 pt-1">{{ skill.code }}</span>
                            <router-link :to="{ name: 'skill', params: { skillId: skill.id } }"
                                class="text-gray-700 hover:text-sky-600 hover:underline decoration-sky-600 decoration-1 underline-offset-2 leading-tight block">
                                {{ skill.title }}
                            </router-link>

                            <!-- Preview Popover (Placeholder) -->
                            <!-- Actual implementation would require complex hovering logic -->
                        </li>
                    </ul>
                </div>
            </div>

            <div v-if="Object.keys(skillsByGrade).length === 0" class="text-center py-12 text-gray-500">
                No skills found for this topic yet.
            </div>
        </div>

        <div v-else class="text-center py-12 text-red-500">
            Topic not found.
        </div>

      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import ViewByToggle from '@/components/ui/ViewByToggle.vue'
import type { SkillListItem } from '@/types/api'

const route = useRoute()
const catalogStore = useCatalogStore()

const currentTopicSlug = computed(() => route.params.topicSlug as string)
const topics = computed(() => catalogStore.topics)
const loading = computed(() => catalogStore.loading)

const currentTopic = computed(() => {
    return topics.value.find(t => t.slug === currentTopicSlug.value)
})

// Group skills by grade
const skillsByGrade = computed(() => {
    // This assumes we fetch ALL skills for the topic.
    // In reality we might need a specific endpoint or simply filter if we already have them.
    // For now we'll rely on catalogStore.skills if appropriately fetched.
    const grouped: Record<string, SkillListItem[]> = {}

    // Sort skills by grade, then by code
    const sortedSkills = [...catalogStore.skills].sort((a, b) => {
        if (a.grade_id !== b.grade_id) return a.grade_id - b.grade_id
        return a.code.localeCompare(b.code)
    })

    sortedSkills.forEach(skill => {
        // Since we fetch skills filtered by topic_id from API, we can trust they belong here.
        // We still check just in case, but relax it or remove strictly if API is trusted.
        // Actually, let's trust the API result for now to debug visibility issues.
        const key = skill.grade_id.toString()
        if (!grouped[key]) grouped[key] = []
        grouped[key].push(skill)
    })

    return grouped
})

const fetchTopicData = async () => {
    if (topics.value.length === 0) {
        await catalogStore.getTopics()
    }

    if (currentTopic.value) {
        // Fetch all skills for this topic across all grades
        // We use topic_id parameter. 'grade_number' is omitted to get all grades.
        await catalogStore.getSkills({ topic_id: currentTopic.value.id } as any, true)
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

const getGradeColorClass = (gradeKey: string) => {
    // Map arbitrary keys to colors for variety
    const num = parseInt(gradeKey)
    const colors = ['text-orange-600', 'text-teal-600', 'text-purple-600', 'text-lime-600', 'text-red-600', 'text-blue-600']
    return colors[num % colors.length] || 'text-gray-700'
}

const getGradeTitle = (gradeKey: string) => {
    const num = parseInt(gradeKey)
    if (num === -1) return 'Pre-K skills'
    if (num === 0) return 'Kindergarten skills'
    if (num === 1) return 'First-grade skills'
    if (num === 2) return 'Second-grade skills'
    if (num === 3) return 'Third-grade skills'
    if (num === 4) return 'Fourth-grade skills'
    if (num === 5) return 'Fifth-grade skills'

    // Fallback logic
    const mapping: Record<number, string> = {
        6: 'Sixth-grade', 7: 'Seventh-grade', 8: 'Eighth-grade',
        9: 'Ninth-grade', 10: 'Tenth-grade', 11: 'Eleventh-grade'
    }
    return (mapping[num] || `${num}th-grade`) + ' skills'
}
</script>

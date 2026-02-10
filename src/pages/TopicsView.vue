<template>
  <div class="min-h-screen bg-sky-50 font-sans">
    <Header />

    <!-- View Toggle -->
    <div class="bg-white border-b border-gray-200">
       <ViewByToggle />
    </div>

    <!-- Hero Banner -->
    <div class="relative bg-gradient-to-b from-sky-100 to-sky-200 py-12 px-6 overflow-hidden">
      <!-- Background Decorations (Clouds, Lighthouse mock) -->
      <div class="absolute inset-0 opacity-30 pointer-events-none">
        <svg class="absolute left-10 bottom-0 text-blue-300 w-32 h-32" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L2 22h20L12 2zm0 3.5L18.5 20h-13L12 5.5z"/></svg>
        <svg class="absolute right-20 top-10 text-white w-24 h-16" fill="currentColor" viewBox="0 0 24 24"><path d="M18.5 5c-1.7 0-3.2.9-4 2.3-.8-1.4-2.3-2.3-4-2.3-3 0-5.5 2.5-5.5 5.5 0 4.5 9.5 11.5 9.5 11.5s9.5-7 9.5-11.5c0-3-2.5-5.5-5.5-5.5z"/></svg>
      </div>

      <div class="relative z-10 max-w-4xl mx-auto text-center">
        <h1 class="text-4xl md:text-5xl font-bold text-sky-600 mb-4">IXL Math</h1>
        <p class="text-lg text-gray-700 max-w-2xl mx-auto">
          Gain fluency and confidence in math! IXL helps students master essential skills at their own pace through fun and interactive questions, built in support, and motivating awards.
        </p>
      </div>
    </div>

    <!-- Topics Grid -->
    <main class="max-w-7xl mx-auto px-4 py-8">
      <div class="grid grid-cols-1 gap-6">

        <!-- Topic Card -->
        <div v-for="topic in broadTopics" :key="topic.title"
             class="bg-white rounded-lg shadow-sm overflow-hidden flex flex-col md:flex-row border border-gray-100 hover:shadow-md transition-shadow">
          <!-- Colored Header Strip on Desktop, Top on Mobile -->
          <div :class="['md:w-2 shrink-0', getColorClasses(topic.color).bg]"></div>

          <div class="p-6 flex-1 flex flex-col md:flex-row items-start md:items-center gap-4">
             <div class="flex-1">
               <h2 :class="['text-2xl font-bold mb-2', getColorClasses(topic.color).text]">{{ topic.title }}</h2>
               <p class="text-gray-600 text-sm">
                 <span class="font-bold text-gray-500 uppercase text-xs mr-1">Includes:</span>
                 {{ topic.description }}
               </p>
             </div>

             <router-link :to="{ name: 'topic-detail', params: { topicSlug: topic.slug || topic.title.toLowerCase() } }"
                 :class="['shrink-0 px-6 py-2 rounded font-bold text-white transition-colors shadow-sm inline-block text-center', getColorClasses(topic.color).btn]">
               See skills ›
             </router-link>
          </div>
        </div>

      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import ViewByToggle from '@/components/ui/ViewByToggle.vue'
import { onMounted, computed } from 'vue'
import { useCatalogStore } from '@/stores/catalog'

const catalogStore = useCatalogStore()

interface TopicViewModel {
  slug: string
  title: string
  description: string
  color: string
}

// Map real topic to view model
const broadTopics = computed<TopicViewModel[]>(() => {
  return (catalogStore.topics || []).map((topic, index) => {
    // Cyclic colors based on index
    const colors = ['orange', 'teal', 'purple', 'lime', 'red', 'blue', 'indigo']
    const color = colors[index % colors.length] || 'orange'

    return {
      slug: topic.slug,
      title: topic.title,
      description: topic.description || 'Practice essential skills in this topic.',
      color: color,
      // count: 0 // We don't have count yet
    }
  })
})

onMounted(() => {
  catalogStore.getTopics()
})

const getColorClasses = (color: string) => {
  const map = {
    orange: { bg: 'bg-orange-400', text: 'text-orange-500', btn: 'bg-orange-400 hover:bg-orange-500' },
    teal: { bg: 'bg-teal-400', text: 'text-teal-500', btn: 'bg-teal-400 hover:bg-teal-500' },
    purple: { bg: 'bg-purple-400', text: 'text-purple-500', btn: 'bg-purple-400 hover:bg-purple-500' },
    lime: { bg: 'bg-lime-400', text: 'text-lime-500', btn: 'bg-lime-400 hover:bg-lime-500' },
    red: { bg: 'bg-red-400', text: 'text-red-500', btn: 'bg-red-400 hover:bg-red-500' },
    blue: { bg: 'bg-blue-400', text: 'text-blue-500', btn: 'bg-blue-400 hover:bg-blue-500' },
    indigo: { bg: 'bg-indigo-400', text: 'text-indigo-500', btn: 'bg-indigo-400 hover:bg-indigo-500' }
  } as const
  return map[color as keyof typeof map] || map.orange
}
</script>

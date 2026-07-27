<template>
  <div class="flex items-center bg-white border-b border-gray-200 px-4 select-none">
    <span class="text-gray-600 mr-4 font-medium">View by:</span>

    <div class="flex">
      <!-- Grades Tab -->
      <router-link :to="{ name: 'class', params: { gradeId: currentGradeId || 6 } }"
        custom v-slot="{ navigate }">
        <div @click="navigate"
             class="relative px-6 py-2 cursor-pointer transition-colors"
             :class="isGradesActive ? 'bg-sky-400 text-white font-bold' : 'text-sky-500 hover:text-sky-600 font-medium'">
          Grades
          <!-- Arrow Down for Active State -->
          <div v-if="isGradesActive" class="absolute top-full left-0 right-0 flex justify-center overflow-hidden h-2.5 z-10 w-full">
             <div class="w-5 h-5 bg-sky-400 rotate-45 -mt-3.5 transform origin-center shadow-sm"></div>
          </div>
        </div>
      </router-link>

      <!-- Topics Tab -->
      <router-link :to="{ name: 'topics' }"
        custom v-slot="{ navigate, isActive }">
        <div @click="navigate"
             class="relative px-6 py-2 cursor-pointer transition-colors"
             :class="isActive ? 'bg-sky-400 text-white font-bold' : 'text-sky-500 hover:text-sky-600 font-medium'">
          Topics
          <!-- Arrow Down for Active State -->
          <div v-if="isActive" class="absolute top-full left-0 right-0 flex justify-center overflow-hidden h-2.5 z-10 w-full">
             <div class="w-5 h-5 bg-sky-400 rotate-45 -mt-3.5 transform origin-center shadow-sm"></div>
          </div>
        </div>
      </router-link>

      <!-- Placeholders Removed -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const isGradesActive = computed(() => {
  return route.name === 'class'
})

const currentGradeId = computed(() => {
  return route.params.gradeId ? parseInt(route.params.gradeId as string) : null
})
</script>

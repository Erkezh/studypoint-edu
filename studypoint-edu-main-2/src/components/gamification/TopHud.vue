<template>
  <div class="flex items-center justify-between bg-white rounded-2xl p-4 shadow-sm mb-6 border border-gray-100">
    <!-- Level & XP -->
    <div class="flex items-center space-x-4 flex-1">
      <div class="bg-blue-600 text-white font-bold rounded-xl w-12 h-12 flex items-center justify-center text-xl shadow-lg shadow-blue-200">
        {{ gamification.level }}
      </div>
      <div class="flex-1 max-w-md">
        <div class="flex justify-between text-sm mb-1 font-semibold text-gray-700">
          <span>Level {{ gamification.level }}</span>
          <span class="text-gray-400">{{ gamification.xp }} / {{ gamification.nextLevelXp }} XP</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-3">
          <div class="bg-green-500 h-3 rounded-full transition-all duration-1000 ease-out" :style="{ width: progressPercent + '%' }"></div>
        </div>
      </div>
    </div>
    
    <!-- Streak -->
    <div class="flex items-center mx-6">
      <div class="bg-orange-100 text-orange-600 font-bold px-4 py-2 rounded-xl flex items-center space-x-2">
        <span class="text-xl">🔥</span>
        <span>{{ gamification.streak }} Days</span>
      </div>
    </div>

    <!-- Coins -->
    <div class="flex items-center">
      <div class="bg-yellow-100 text-yellow-700 font-bold px-4 py-2 rounded-xl flex items-center space-x-2 shadow-sm shadow-yellow-100 border border-yellow-200">
        <img class="h-6 w-6 object-contain" src="/assets/coin-icon.svg" alt="" aria-hidden="true" />
        <span>{{ gamification.coins }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useGamificationStore } from '@/stores/gamification'

const gamification = useGamificationStore()

const progressPercent = computed(() => {
  if (gamification.nextLevelXp === 0) return 0
  return Math.min(100, Math.round((gamification.xp / gamification.nextLevelXp) * 100))
})
</script>

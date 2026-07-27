<template>
  <div class="min-h-screen bg-indigo-900 text-white flex flex-col items-center py-10 px-4">
    <!-- Battle Header -->
    <div class="w-full max-w-4xl flex justify-between items-center bg-indigo-800 rounded-3xl p-6 shadow-2xl mb-8 border-4 border-indigo-700">
      <div class="flex items-center space-x-4">
        <div class="w-16 h-16 bg-blue-500 rounded-full border-4 border-white flex justify-center items-center font-bold text-xl shadow-[0_0_15px_rgba(59,130,246,0.8)]">YOU</div>
        <div>
          <div class="font-bold text-lg">Hero King</div>
          <div class="w-48 bg-gray-900 rounded-full h-4 mt-1 border-2 border-gray-700">
            <div class="bg-green-500 h-full rounded-full" :style="{ width: myHp + '%' }"></div>
          </div>
          <div class="text-sm mt-1 text-green-300 font-bold">{{ myHp }} HP</div>
        </div>
      </div>

      <div class="text-3xl font-black text-yellow-400 drop-shadow-[0_0_10px_rgba(250,204,21,0.8)]">
        {{ timer }}s
      </div>

      <div class="flex items-center space-x-4 text-right">
        <div>
          <div class="font-bold text-lg">Rival King</div>
          <div class="w-48 bg-gray-900 rounded-full h-4 mt-1 border-2 border-gray-700 flex justify-end">
            <div class="bg-red-500 h-full rounded-full" :style="{ width: enemyHp + '%' }"></div>
          </div>
          <div class="text-sm mt-1 text-red-300 font-bold">{{ enemyHp }} HP</div>
        </div>
        <div class="w-16 h-16 bg-red-600 rounded-full border-4 border-white flex justify-center items-center font-bold text-xl shadow-[0_0_15px_rgba(220,38,38,0.8)]">FOE</div>
      </div>
    </div>

    <!-- The Battlefield -->
    <div class="w-full max-w-4xl h-64 bg-indigo-950 rounded-3xl mb-8 relative border-4 border-indigo-800 overflow-hidden shadow-inset-2xl flex justify-between items-end pb-8 px-12">
      <!-- Your side -->
      <div class="w-24 h-32 bg-blue-400 rounded-t-full relative flex items-center justify-center transition-transform" :class="{ 'translate-x-32 scale-110': attacking }">
        <span class="text-3xl">🤺</span>
      </div>

      <!-- Enemy side -->
      <div class="w-24 h-32 bg-red-400 rounded-t-full relative flex items-center justify-center">
        <span class="text-3xl">🐉</span>
      </div>
    </div>

    <!-- Question Zone -->
    <div class="w-full max-w-2xl bg-white text-gray-900 p-8 rounded-[32px] shadow-[0_20px_50px_rgba(0,0,0,0.5)]">
      <h2 class="text-2xl font-bold mb-6 text-center text-indigo-900 border-b-2 border-indigo-100 pb-4">
        What is 15 &times; 12 ?
      </h2>
      <div class="grid grid-cols-2 gap-4">
        <button v-for="opt in [180, 160, 150, 200]" :key="opt" 
          @click="submitAnswer(opt === 180)"
          class="bg-indigo-50 hover:bg-indigo-600 hover:text-white text-indigo-900 font-bold py-6 rounded-2xl text-xl transition-all duration-200 active:scale-95 shadow-[0_4px_0_rgba(199,210,254,1)] hover:shadow-[0_4px_0_rgba(67,56,202,1)]">
          {{ opt }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const myHp = ref(100)
const enemyHp = ref(100)
const timer = ref(150)
const attacking = ref(false)

const ws: WebSocket | null = null

const sendBattleEvent = (payload: string) => {
  const socket = ws as WebSocket | null
  socket?.send(payload)
}

const submitAnswer = (isCorrect: boolean) => {
  if (isCorrect) {
    attacking.value = true
    setTimeout(() => {
      attacking.value = false
      enemyHp.value = Math.max(0, enemyHp.value - 15)
      sendBattleEvent(JSON.stringify({ action: 'attack' }))
    }, 300)
  } else {
    myHp.value = Math.max(0, myHp.value - 10)
  }
}

onMounted(() => {
  // Mocking WS for MVP UI feel
  setInterval(() => {
    if (timer.value > 0) timer.value--
  }, 1000)
})
</script>

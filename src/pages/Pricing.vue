<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <Header />

    <main class="flex-1 container mx-auto px-4 py-12 max-w-5xl">
      <!-- Title -->
      <div class="text-center mb-12 px-4">
        <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 mb-4 leading-tight">
          <span class="text-[#38B000]">StudyPoint</span> — бұл жекелендірілген оқыту
        </h1>
        <p class="text-gray-600 text-base sm:text-lg max-w-2xl mx-auto font-normal">
          Математика — кез келген уақытта, кез келген жерде
        </p>
      </div>

      <!-- Plan Cards (Family & Classroom) -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        <!-- Family Plan -->
        <div class="bg-white rounded-[24px] shadow-md border border-gray-200 overflow-hidden flex flex-col hover:shadow-lg transition-shadow duration-300">
          <div class="p-8 flex-1 flex flex-col items-center">
            <h3 class="text-3xl font-bold text-[#38B000] mb-8">Отбасылық</h3>
            
            <div class="w-48 h-32 mb-8 flex items-center justify-center">
              <svg class="w-full h-full text-[#38B000]" viewBox="0 0 200 120" fill="none" xmlns="http://www.w3.org/2000/svg">
                <!-- Couch -->
                <path d="M40 80C40 74.4772 44.4772 70 50 70H150C155.523 70 160 74.4772 160 80V100C160 105.523 155.523 110 150 110H50C44.4772 110 40 105.523 40 100V80Z" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="2"/>
                <path d="M50 70V55C50 49.4772 54.4772 45 60 45H140C145.523 45 150 49.4772 150 55V70" stroke="currentColor" stroke-width="2"/>
                <path d="M40 85H160" stroke="currentColor" stroke-width="2"/>
                <path d="M55 110V115M145 110V115" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <!-- Parent Reading -->
                <circle cx="80" cy="30" r="12" stroke="currentColor" stroke-width="2"/>
                <path d="M70 45C70 45 80 40 90 45C95 47.5 95 65 95 65H65C65 65 65 47.5 70 45Z" stroke="currentColor" stroke-width="2"/>
                <!-- Child -->
                <circle cx="115" cy="40" r="9" stroke="currentColor" stroke-width="2"/>
                <path d="M106 52C106 52 115 48 124 52C127 54 127 65 127 65H103C103 65 103 54 106 52Z" stroke="currentColor" stroke-width="2"/>
                <!-- Book -->
                <path d="M85 55L100 60L115 55L100 50L85 55Z" fill="currentColor" fill-opacity="0.2" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                <path d="M100 50V60" stroke="currentColor" stroke-width="2"/>
                <!-- Lamp -->
                <path d="M140 15L130 35H150L140 15Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                <path d="M140 35V45" stroke="currentColor" stroke-width="2"/>
                <path d="M135 45H145" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <!-- Decorative stars -->
                <path d="M30 30L34 26M34 34L30 26" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M160 50L164 46M164 50L160 46" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>

            <div class="w-full space-y-3 mt-auto">
              <button
                @click="selectPlan('family')"
                class="w-full py-3.5 px-6 rounded-xl text-lg font-bold text-white transition-colors shadow-sm hover:brightness-95 active:scale-95 cursor-pointer"
                style="background-color: #38B000;"
              >
                Қазір қосылу
              </button>
              <button
                class="w-full py-3.5 px-6 rounded-xl text-lg font-semibold border-2 transition-colors hover:bg-gray-50 active:scale-95 cursor-pointer"
                style="color: #38B000; border-color: #38B000;"
              >
                Толығырақ білу
              </button>
            </div>
          </div>
        </div>

        <!-- Classroom Plan -->
        <div class="bg-white rounded-[24px] shadow-md border border-gray-200 overflow-hidden flex flex-col hover:shadow-lg transition-shadow duration-300">
          <div class="p-8 flex-1 flex flex-col items-center">
            <h3 class="text-3xl font-bold text-[#00b2b2] mb-8">Сыныптық</h3>
            
            <div class="w-48 h-32 mb-8 flex items-center justify-center">
              <svg class="w-full h-full text-[#00b2b2]" viewBox="0 0 200 120" fill="none" xmlns="http://www.w3.org/2000/svg">
                <!-- Whiteboard/Blackboard -->
                <rect x="50" y="10" width="100" height="40" rx="2" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="2"/>
                <path d="M55 40H145" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <circle cx="100" cy="30" r="10" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 2"/>
                <path d="M85 30H115M100 15V45" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 2"/>
                <!-- Teacher -->
                <circle cx="40" cy="40" r="10" stroke="currentColor" stroke-width="2"/>
                <path d="M30 55C30 55 40 50 50 55C53 56.5 53 85 53 85H27C27 85 27 56.5 30 55Z" stroke="currentColor" stroke-width="2"/>
                <path d="M45 65L65 55" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <!-- Left Student -->
                <circle cx="85" cy="70" r="8" stroke="currentColor" stroke-width="2"/>
                <path d="M75 80C75 80 85 76 95 80C97 81 97 95 97 95H73C73 95 73 81 75 80Z" stroke="currentColor" stroke-width="2"/>
                <rect x="70" y="90" width="30" height="20" rx="2" fill="white" stroke="currentColor" stroke-width="2"/>
                <path d="M75 90V85H95V90" stroke="currentColor" stroke-width="1.5"/>
                <!-- Right Student -->
                <circle cx="130" cy="65" r="8" stroke="currentColor" stroke-width="2"/>
                <path d="M120 75C120 75 130 71 140 75C142 76 142 90 142 90H118C118 90 118 76 120 75Z" stroke="currentColor" stroke-width="2"/>
                <rect x="115" y="85" width="30" height="20" rx="2" fill="white" stroke="currentColor" stroke-width="2"/>
                <path d="M120 85V80H140V85" stroke="currentColor" stroke-width="1.5"/>
                <!-- Middle Bottom Student -->
                <circle cx="105" cy="95" r="9" stroke="currentColor" stroke-width="2"/>
                <path d="M93 107C93 107 105 102 117 107V120H93V107Z" stroke="currentColor" stroke-width="2"/>
                <rect x="88" y="115" width="34" height="5" rx="1" fill="white" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>

            <div class="w-full space-y-3 mt-auto">
              <button
                @click="selectPlan('classroom')"
                class="w-full py-3.5 px-6 rounded-xl text-lg font-bold text-white transition-colors shadow-sm hover:brightness-95 active:scale-95 cursor-pointer"
                style="background-color: #00b2b2;"
              >
                Жазылуды бастау
              </button>
              <button
                class="w-full py-3.5 px-6 rounded-xl text-lg font-semibold border-2 transition-colors hover:bg-gray-50 active:scale-95 cursor-pointer"
                style="color: #00b2b2; border-color: #00b2b2;"
              >
                Толығырақ білу
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <div class="mt-auto bg-white border-t border-gray-200">
      <Footer />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'

defineOptions({ name: 'PricingPage' })

const router = useRouter()

const selectPlan = (plan: string) => {
  router.push({ name: 'payment', query: { plan } })
}
</script>

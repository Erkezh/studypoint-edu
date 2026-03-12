<template>
  <div class="min-h-screen flex flex-col" style="background: linear-gradient(135deg, #65c100 0%, #48d8d1 100%);">
    <Header />

    <main class="flex-1 container mx-auto px-4 py-16 max-w-6xl">
      <!-- Title -->
      <div class="text-center mb-16 px-4">
        <h1 class="text-3xl sm:text-5xl font-light text-white mb-6">
          <span class="font-bold">StudyPoint</span> — бұл жекелендірілген оқыту
        </h1>
        <p class="text-white/90 text-base sm:text-lg max-w-4xl mx-auto font-light">
          Математика • Ағылшын тілі • Жаратылыстану • Қоғамтану • Испан тілі • Мектепке дейінгі-12 сынып
        </p>
      </div>

      <!-- Plan Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
        <!-- Family Plan -->
        <div class="bg-white rounded-[24px] shadow-lg overflow-hidden flex flex-col transform hover:-translate-y-1 transition-transform duration-300">
          <div class="p-8 flex-1 flex flex-col items-center">
            <h3 class="text-3xl font-light text-[#5ba100] mb-8">Отбасылық</h3>
            
            <div class="w-48 h-32 mb-8 flex items-center justify-center">
              <svg class="w-full h-full text-[#5ba100]" viewBox="0 0 200 120" fill="none" xmlns="http://www.w3.org/2000/svg">
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
                class="w-full py-3 px-6 rounded-lg text-lg font-medium text-white transition-colors shadow-md"
                style="background-color: #5ba100;"
                onmouseover="this.style.backgroundColor='#4a8400'"
                onmouseout="this.style.backgroundColor='#5ba100'"
              >
                Қазір қосылу
              </button>
              <button
                class="w-full py-3 px-6 rounded-lg text-lg font-medium border-2 transition-colors"
                style="color: #5ba100; border-color: #e5e7eb;"
                onmouseover="this.style.borderColor='#5ba100'"
                onmouseout="this.style.borderColor='#e5e7eb'"
              >
                Толығырақ білу
              </button>
            </div>
          </div>
        </div>

        <!-- Classroom Plan -->
        <div class="bg-white rounded-[24px] shadow-lg overflow-hidden flex flex-col transform hover:-translate-y-1 transition-transform duration-300">
          <div class="p-8 flex-1 flex flex-col items-center">
            <h3 class="text-3xl font-light text-[#00b2b2] mb-8">Сыныптық</h3>
            
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
                class="w-full py-3 px-6 rounded-lg text-lg font-medium text-white transition-colors"
                style="background-color: #00b2b2;"
                onmouseover="this.style.backgroundColor='#009999'"
                onmouseout="this.style.backgroundColor='#00b2b2'"
              >
                Сынақ нұсқасын бастау
              </button>
              <button
                class="w-full py-3 px-6 rounded-lg text-lg font-medium text-white transition-colors"
                style="background-color: #00b2b2;"
                onmouseover="this.style.backgroundColor='#009999'"
                onmouseout="this.style.backgroundColor='#00b2b2'"
              >
                Баға ұсынысын алу
              </button>
              <button
                class="w-full py-3 px-6 rounded-lg text-lg font-medium border-2 transition-colors"
                style="color: #00b2b2; border-color: #e5e7eb;"
                onmouseover="this.style.borderColor='#00b2b2'"
                onmouseout="this.style.borderColor='#e5e7eb'"
              >
                Толығырақ білу
              </button>
            </div>
          </div>
        </div>

        <!-- School Plan -->
        <div class="bg-white rounded-[24px] shadow-lg overflow-hidden flex flex-col transform hover:-translate-y-1 transition-transform duration-300">
          <div class="p-8 flex-1 flex flex-col items-center">
            <h3 class="text-3xl font-light text-[#009ee3] mb-8 text-center leading-tight">Мектептер мен<br>аудандар</h3>
            
            <div class="w-48 h-32 mb-8 flex items-center justify-center">
              <svg class="w-full h-full text-[#009ee3]" viewBox="0 0 200 120" fill="none" xmlns="http://www.w3.org/2000/svg">
                <!-- Clouds -->
                <path d="M40 35C40 32.2 42.2 30 45 30C45.9 30 46.7 30.2 47.5 30.6C49.1 27.9 52.1 26 55.5 26C59.8 26 63.4 28.9 64.3 32.9C64.5 32.8 64.8 32.8 65 32.8C68.9 32.8 72 36 72 39.8C72 43.7 68.9 46.8 65 46.8H45C42.2 46.8 40 44.6 40 41.8C40 40.7 40.3 39.7 40.9 38.9C40.4 37.8 40 36.5 40 35Z" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="1.5"/>
                <path d="M165 25C165 22.8 166.8 21 169 21C169.7 21 170.4 21.2 171 21.5C172.3 20.3 174.1 19.5 176 19.5C179.6 19.5 182.5 22.4 182.5 26C182.5 26.5 182.4 27.1 182.3 27.6C184.5 28.2 186 30.1 186 32.5C186 35.5 183.5 38 180.5 38H169C166.8 38 165 36.2 165 34C165 33.1 165.3 32.3 165.7 31.7C165.3 30.8 165 29.7 165 28.6V25Z" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="1.5"/>
                <!-- Base & Trees -->
                <path d="M30 110L20 120H180L170 110H30Z" fill="currentColor" fill-opacity="0.2" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                <path d="M15 120C15 110 25 105 35 110V120H15Z" fill="currentColor" fill-opacity="0.3" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
                <path d="M185 120C185 105 170 100 160 110V120H185Z" fill="currentColor" fill-opacity="0.3" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
                <!-- Main building -->
                <rect x="40" y="70" width="120" height="40" fill="white" stroke="currentColor" stroke-width="2"/>
                <rect x="75" y="40" width="50" height="30" fill="white" stroke="currentColor" stroke-width="2"/>
                <path d="M35 70L45 55H155L165 70" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M70 40L100 15L130 40" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <!-- Bell tower -->
                <rect x="92" y="5" width="16" height="15" fill="white" stroke="currentColor" stroke-width="2"/>
                <path d="M92 5H108M100 5V0M100 5V15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <circle cx="100" cy="10" r="3" stroke="currentColor" stroke-width="1.5"/>
                <!-- Columns & Windows -->
                <rect x="85" y="45" width="6" height="65" fill="white" stroke="currentColor" stroke-width="2"/>
                <rect x="97" y="45" width="6" height="65" fill="white" stroke="currentColor" stroke-width="2"/>
                <rect x="109" y="45" width="6" height="65" fill="white" stroke="currentColor" stroke-width="2"/>
                <rect x="50" y="80" width="10" height="15" stroke="currentColor" stroke-width="1.5"/>
                <path d="M50 87.5H60M55 80V95" stroke="currentColor" stroke-width="1.5"/>
                <rect x="65" y="80" width="10" height="15" stroke="currentColor" stroke-width="1.5"/>
                <path d="M65 87.5H75M70 80V95" stroke="currentColor" stroke-width="1.5"/>
                <rect x="125" y="80" width="10" height="15" stroke="currentColor" stroke-width="1.5"/>
                <path d="M125 87.5H135M130 80V95" stroke="currentColor" stroke-width="1.5"/>
                <rect x="140" y="80" width="10" height="15" stroke="currentColor" stroke-width="1.5"/>
                <path d="M140 87.5H150M145 80V95" stroke="currentColor" stroke-width="1.5"/>
              </svg>
            </div>

            <div class="w-full space-y-3 mt-auto">
              <button
                class="w-full py-3 px-6 rounded-lg text-lg font-medium text-white transition-colors"
                style="background-color: #009ee3;"
                onmouseover="this.style.backgroundColor='#0088cc'"
                onmouseout="this.style.backgroundColor='#009ee3'"
              >
                Баға ұсынысын алу
              </button>
              <button
                class="w-full py-3 px-6 rounded-lg text-lg font-medium border-2 transition-colors"
                style="color: #009ee3; border-color: #e5e7eb;"
                onmouseover="this.style.borderColor='#009ee3'"
                onmouseout="this.style.borderColor='#e5e7eb'"
              >
                Толығырақ білу
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <div class="mt-auto bg-white">
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

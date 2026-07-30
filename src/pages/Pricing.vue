<template>
  <div class="min-h-screen bg-gray-50 flex flex-col font-sans">
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
        <div class="bg-white rounded-[24px] shadow-md border border-gray-200 overflow-hidden flex flex-col hover:shadow-lg transition-shadow duration-300 relative">
          <!-- Discount Badge -->
          <div v-if="familyPricing.discountPercent > 0" class="absolute top-4 right-4 bg-amber-400 text-amber-950 font-bold text-xs px-3 py-1.5 rounded-full shadow-sm">
            {{ familyPricing.discountLabel || `-${familyPricing.discountPercent}% Скидка` }}
          </div>

          <div class="p-8 flex-1 flex flex-col items-center">
            <h3 class="text-3xl font-bold text-[#38B000] mb-4">Отбасылық</h3>
            
            <!-- Price Display -->
            <div class="text-center mb-6">
              <div class="flex items-baseline justify-center gap-2">
                <span class="text-3xl sm:text-4xl font-extrabold text-gray-900">{{ familyPricing.monthlyPrice.toLocaleString() }} ₸</span>
                <span class="text-gray-500 font-medium text-sm">/ ай</span>
              </div>
              <p v-if="familyPricing.discountPercent > 0" class="text-xs text-gray-400 line-through mt-1">
                {{ Math.round(familyPricing.monthlyPrice / (1 - familyPricing.discountPercent / 100)).toLocaleString() }} ₸
              </p>
            </div>

            <div class="w-full h-64 sm:h-72 md:h-80 mb-6 flex items-center justify-center overflow-hidden rounded-2xl shadow-sm border border-gray-100">
              <img :src="familyImage" alt="Отбасылық" class="w-full h-full object-cover rounded-2xl hover:scale-105 transition-transform duration-500" />
            </div>

            <div class="w-full space-y-3 mt-auto">
              <button
                @click="selectPlan('family')"
                class="w-full py-3.5 px-6 rounded-xl text-lg font-bold text-white transition-colors shadow-sm hover:brightness-95 active:scale-95 cursor-pointer"
                style="background-color: #38B000;"
              >
                Қазір қосылу
              </button>
            </div>
          </div>
        </div>

        <!-- Classroom Plan -->
        <div class="bg-white rounded-[24px] shadow-md border border-gray-200 overflow-hidden flex flex-col hover:shadow-lg transition-shadow duration-300 relative">
          <!-- Discount Badge -->
          <div v-if="classroomPricing.discountPercent > 0" class="absolute top-4 right-4 bg-teal-400 text-teal-950 font-bold text-xs px-3 py-1.5 rounded-full shadow-sm z-10">
            {{ classroomPricing.discountLabel || `-${classroomPricing.discountPercent}% Скидка` }}
          </div>

          <div class="p-8 flex-1 flex flex-col items-center">
            <h3 class="text-3xl font-bold text-[#00b2b2] mb-4">Сыныптық</h3>

            <!-- Price Display -->
            <div class="text-center mb-6">
              <div class="flex items-baseline justify-center gap-2">
                <span class="text-3xl sm:text-4xl font-extrabold text-gray-900">{{ classroomPricing.monthlyPrice.toLocaleString() }} ₸</span>
                <span class="text-gray-500 font-medium text-sm">/ ай</span>
              </div>
              <p v-if="classroomPricing.discountPercent > 0" class="text-xs text-gray-400 line-through mt-1">
                {{ Math.round(classroomPricing.monthlyPrice / (1 - classroomPricing.discountPercent / 100)).toLocaleString() }} ₸
              </p>
            </div>

            <div class="w-full h-64 sm:h-72 md:h-80 mb-6 flex items-center justify-center overflow-hidden rounded-2xl shadow-sm border border-gray-100">
              <img :src="classroomImage" alt="Сыныптық" class="w-full h-full object-cover rounded-2xl hover:scale-105 transition-transform duration-500" />
            </div>

            <div class="w-full space-y-3 mt-auto">
              <button
                @click="selectPlan('classroom')"
                class="w-full py-3.5 px-6 rounded-xl text-lg font-bold text-white transition-colors shadow-sm hover:brightness-95 active:scale-95 cursor-pointer"
                style="background-color: #00b2b2;"
              >
                Жазылуды бастау
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
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePricingStore } from '@/stores/pricingStore'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import familyImage from '@/assets/images/pricing-family.png'
import classroomImage from '@/assets/images/pricing-classroom.png'

defineOptions({ name: 'PricingPage' })

const router = useRouter()
const pricingStore = usePricingStore()

const familyPricing = computed(() => pricingStore.pricing.FAMILY || { monthlyPrice: 1990, discountPercent: 0, discountLabel: '' })
const classroomPricing = computed(() => pricingStore.pricing.CLASSROOM || { monthlyPrice: 14990, discountPercent: 0, discountLabel: '' })

const selectPlan = (plan: string) => {
  router.push({ name: 'payment', query: { plan } })
}
</script>

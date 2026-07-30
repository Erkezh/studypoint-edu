<template>
  <div class="min-h-screen bg-gray-50 font-sans">
    <Header />
    <main class="container mx-auto px-4 py-8 max-w-6xl">
      <!-- Back to Dashboard -->
      <router-link to="/admin" class="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors mb-6 font-medium">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
        Админ панелі
      </router-link>

      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-4">
        <div>
          <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Бағалар мен Промокодтар</h1>
          <p class="text-sm text-gray-500 mt-1">Тарифтер бағасын, жеңілдіктерді және промокодтарды басқару</p>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex border-b border-gray-200 mb-6 space-x-4">
        <button
          @click="activeAdminTab = 'pricing'"
          :class="['pb-3 px-4 text-sm font-semibold border-b-2 transition-colors cursor-pointer', activeAdminTab === 'pricing' ? 'border-green-600 text-green-600' : 'border-transparent text-gray-500 hover:text-gray-700']"
        >
          🏷️ Тарифтер мен Бағалар (Жеңілдіктер)
        </button>
        <button
          @click="activeAdminTab = 'promocodes'"
          :class="['pb-3 px-4 text-sm font-semibold border-b-2 transition-colors cursor-pointer', activeAdminTab === 'promocodes' ? 'border-green-600 text-green-600' : 'border-transparent text-gray-500 hover:text-gray-700']"
        >
          🎟️ Промокодтар ({{ pricingStore.promoCodes.length }})
        </button>
      </div>

      <!-- Notifications -->
      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-xl mb-6 text-sm flex items-center justify-between">
        <span>{{ error }}</span>
        <button @click="error = null" class="font-bold text-lg">&times;</button>
      </div>
      <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-xl mb-6 text-sm flex items-center justify-between">
        <span>{{ successMessage }}</span>
        <button @click="successMessage = null" class="font-bold text-lg">&times;</button>
      </div>

      <!-- TAB 1: PRICING & DISCOUNTS (Family & Classroom) -->
      <div v-if="activeAdminTab === 'pricing'" class="space-y-6">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-bold text-gray-900 mb-2">Тарифтер бағасын және жеңілдіктерді өңдеу</h2>
          <p class="text-sm text-gray-500 mb-6">Мұнда өзгертілген бағалар мен жеңілдіктер сайттың төлем жасау бетінде (`/pricing` және `/payment`) бірден көрсетіледі.</p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- FAMILY PLAN EDIT -->
            <div class="border border-gray-200 rounded-xl p-5 bg-gray-50/50 space-y-4">
              <div class="flex items-center justify-between border-b border-gray-200 pb-3">
                <h3 class="font-bold text-gray-900 text-base">Отбасылық (FAMILY)</h3>
                <span class="text-xs bg-green-100 text-green-700 px-2.5 py-0.5 rounded-full font-bold">Негізгі</span>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Айлық баға (₸ / ай)</label>
                <input v-model.number="pricingForm.FAMILY.monthlyPrice" type="number" class="w-full p-2.5 border border-gray-300 rounded-lg text-sm bg-white font-semibold" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Жылдық баға тариф ставкасы (₸ / ай)</label>
                <input v-model.number="pricingForm.FAMILY.yearlyPrice" type="number" class="w-full p-2.5 border border-gray-300 rounded-lg text-sm bg-white font-semibold" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Жеңілдік пайызы (% скидки)</label>
                <input v-model.number="pricingForm.FAMILY.discountPercent" type="number" min="0" max="100" class="w-full p-2.5 border border-gray-300 rounded-lg text-sm bg-white font-semibold" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Акция / Жеңілдік лейблі</label>
                <input v-model="pricingForm.FAMILY.discountLabel" type="text" placeholder="Отбасылық жеңілдік -20%" class="w-full p-2.5 border border-gray-300 rounded-lg text-sm bg-white" />
              </div>
            </div>

            <!-- CLASSROOM PLAN EDIT -->
            <div class="border border-gray-200 rounded-xl p-5 bg-gray-50/50 space-y-4">
              <div class="flex items-center justify-between border-b border-gray-200 pb-3">
                <h3 class="font-bold text-gray-900 text-base">Сыныптық (CLASSROOM)</h3>
                <span class="text-xs bg-teal-100 text-teal-700 px-2.5 py-0.5 rounded-full font-bold">Мұғалімдер</span>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Айлық баға (₸ / ай)</label>
                <input v-model.number="pricingForm.CLASSROOM.monthlyPrice" type="number" class="w-full p-2.5 border border-gray-300 rounded-lg text-sm bg-white font-semibold" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Жылдық баға тариф ставкасы (₸ / ай)</label>
                <input v-model.number="pricingForm.CLASSROOM.yearlyPrice" type="number" class="w-full p-2.5 border border-gray-300 rounded-lg text-sm bg-white font-semibold" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Жеңілдік пайызы (% скидки)</label>
                <input v-model.number="pricingForm.CLASSROOM.discountPercent" type="number" min="0" max="100" class="w-full p-2.5 border border-gray-300 rounded-lg text-sm bg-white font-semibold" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Акция / Жеңілдік лейблі</label>
                <input v-model="pricingForm.CLASSROOM.discountLabel" type="text" placeholder="Сыныптық арнайы баға" class="w-full p-2.5 border border-gray-300 rounded-lg text-sm bg-white" />
              </div>
            </div>
          </div>

          <div class="mt-6 flex justify-end">
            <button @click="savePlanPricingChanges" class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl shadow-sm transition-all text-sm cursor-pointer">
              Бағалар мен Жеңілдіктерді сақтау ✓
            </button>
          </div>
        </div>
      </div>

      <!-- TAB 2: PROMOCODES -->
      <div v-else-if="activeAdminTab === 'promocodes'" class="space-y-6">
        <!-- Add Promo Code Form -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span>🎟️</span> Жаңа Промокод жасау
          </h2>

          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Промокод атауы (Код) *</label>
              <input v-model="newPromo.code" type="text" placeholder="e.g. STUDY2026, OFF50" class="w-full p-2.5 border border-gray-300 rounded-lg text-sm uppercase font-mono font-bold" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Жеңілдік түрі *</label>
              <select v-model="newPromo.discountType" class="w-full p-2.5 border border-gray-300 rounded-lg text-sm bg-white">
                <option value="percent">Пайыз (%)</option>
                <option value="fixed">Тікелей сома (₸)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Жеңілдік мөлшері *</label>
              <input v-model.number="newPromo.discountValue" type="number" min="1" placeholder="20 немесе 1000" class="w-full p-2.5 border border-gray-300 rounded-lg text-sm font-semibold" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Қолданылу лимиті (0 = шексіз)</label>
              <input v-model.number="newPromo.usageLimit" type="number" min="0" placeholder="100" class="w-full p-2.5 border border-gray-300 rounded-lg text-sm" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Мерзімі (Срок действия)</label>
              <input v-model="newPromo.expiresAt" type="date" class="w-full p-2.5 border border-gray-300 rounded-lg text-sm" />
            </div>
            <div class="flex items-end">
              <button @click="handleCreatePromoCode" :disabled="!newPromo.code || !newPromo.discountValue" class="w-full py-2.5 px-4 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-lg text-sm transition-all disabled:opacity-50 cursor-pointer">
                Промокод жасау +
              </button>
            </div>
          </div>
        </div>

        <!-- Promo Codes List Table -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h3 class="font-bold text-gray-900 text-base">Барлық Промокодтар</h3>
            <span class="text-xs text-gray-500 font-medium">Жалпы саны: {{ pricingStore.promoCodes.length }}</span>
          </div>

          <div v-if="pricingStore.promoCodes.length === 0" class="p-8 text-center text-gray-400">
            Промокодтар әлі жасалмаған
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm border-collapse">
              <thead class="bg-gray-50 border-b border-gray-100 whitespace-nowrap">
                <tr>
                  <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Промокод</th>
                  <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Жеңілдік</th>
                  <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Қолданылуы</th>
                  <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Мерзімі</th>
                  <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Мәртебесі</th>
                  <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Әрекеттер</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr v-for="promo in pricingStore.promoCodes" :key="promo.id" class="hover:bg-gray-50 transition-colors">
                  <td class="px-4 py-3">
                    <div class="flex items-center gap-2">
                      <span class="font-mono font-bold text-gray-900 bg-purple-50 text-purple-700 px-2.5 py-1 rounded-lg border border-purple-200">{{ promo.code }}</span>
                      <button @click="copyPromoCodeText(promo.code)" class="text-xs text-gray-400 hover:text-gray-600 font-medium cursor-pointer">📋</button>
                    </div>
                  </td>
                  <td class="px-4 py-3 font-semibold text-gray-800">
                    <span v-if="promo.discountType === 'percent'">-{{ promo.discountValue }}%</span>
                    <span v-else>-{{ promo.discountValue.toLocaleString() }} ₸</span>
                  </td>
                  <td class="px-4 py-3 text-gray-600 text-xs">
                    {{ promo.usageCount }} / {{ promo.usageLimit > 0 ? promo.usageLimit : '∞' }} рет
                  </td>
                  <td class="px-4 py-3 text-gray-600 text-xs">
                    {{ promo.expiresAt ? formatDate(promo.expiresAt) : 'Шексіз' }}
                  </td>
                  <td class="px-4 py-3">
                    <button @click="pricingStore.updatePromoCode(promo.id, { isActive: !promo.isActive })" class="inline-flex items-center gap-1.5 text-xs font-bold px-2.5 py-1 rounded-full cursor-pointer" :class="promo.isActive ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-100 text-gray-500'">
                      <span class="w-1.5 h-1.5 rounded-full" :class="promo.isActive ? 'bg-emerald-500' : 'bg-gray-400'"></span>
                      {{ promo.isActive ? 'Белсенді' : 'Белсенді емес' }}
                    </button>
                  </td>
                  <td class="px-4 py-3 text-right">
                    <button @click="pricingStore.deletePromoCode(promo.id)" class="text-xs text-rose-600 hover:text-rose-800 font-semibold px-2 py-1 rounded hover:bg-rose-50 transition-colors cursor-pointer">
                      Жою
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePricingStore } from '@/stores/pricingStore'
import Header from '@/components/layout/Header.vue'

defineOptions({ name: 'AdminSubscriptions' })

const authStore = useAuthStore()
const pricingStore = usePricingStore()
const router = useRouter()

const activeAdminTab = ref<'pricing' | 'promocodes'>('pricing')

const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

// Pricing Form local reactive state
const pricingForm = ref(JSON.parse(JSON.stringify(pricingStore.pricing)))

// New Promo Code Form
const newPromo = ref({
  code: '',
  discountType: 'percent' as 'percent' | 'fixed',
  discountValue: 20,
  usageLimit: 100,
  expiresAt: '',
  isActive: true,
})

const formatDate = (iso: string) => {
  try {
    return new Date(iso).toLocaleDateString('kk-KZ', { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return iso
  }
}

const savePlanPricingChanges = () => {
  Object.keys(pricingForm.value).forEach(plan => {
    pricingStore.updatePlanPricing(plan, pricingForm.value[plan])
  })
  successMessage.value = 'Тариф бағалары мен жеңілдіктері сәтті сақталды!'
  setTimeout(() => { successMessage.value = null }, 3000)
}

const handleCreatePromoCode = () => {
  if (!newPromo.value.code || !newPromo.value.discountValue) return
  pricingStore.addPromoCode({
    code: newPromo.value.code,
    discountType: newPromo.value.discountType,
    discountValue: newPromo.value.discountValue,
    usageLimit: newPromo.value.usageLimit || 0,
    expiresAt: newPromo.value.expiresAt || null,
    isActive: newPromo.value.isActive,
  })
  newPromo.value = {
    code: '',
    discountType: 'percent',
    discountValue: 20,
    usageLimit: 100,
    expiresAt: '',
    isActive: true,
  }
  successMessage.value = 'Промокод сәтті жасалды!'
  setTimeout(() => { successMessage.value = null }, 3000)
}

const copyPromoCodeText = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    successMessage.value = `Промокод «${text}» көшірілді!`
    setTimeout(() => { successMessage.value = null }, 2000)
  } catch {
    // ignore
  }
}

onMounted(() => {
  if (!authStore.isAuthenticated || authStore.user?.role !== 'ADMIN') {
    router.push({ name: 'home' })
  }
})
</script>

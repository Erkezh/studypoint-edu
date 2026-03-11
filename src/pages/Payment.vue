<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <Header />

    <main class="flex-1 container mx-auto px-4 py-12 max-w-5xl">
      <!-- Back link -->
      <router-link to="/pricing" class="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors mb-8">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
        Жоспарларға оралу
      </router-link>

      <h1 class="text-3xl font-bold text-gray-900 mb-8">Төлем</h1>

      <div class="grid grid-cols-1 lg:grid-cols-5 gap-8">
        <!-- Billing Form (left) -->
        <div class="lg:col-span-3">
          <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 sm:p-8">
            <h2 class="text-lg font-semibold text-gray-900 mb-6">Төлем деректері</h2>

            <form @submit.prevent="handlePayment" class="space-y-5">
              <!-- Cardholder Name -->
              <div>
                <label for="pay-name" class="block text-sm font-medium text-gray-700 mb-1.5">Карта иесінің аты</label>
                <input
                  id="pay-name"
                  v-model="cardName"
                  type="text"
                  required
                  placeholder="Есімі Тегі"
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                />
              </div>

              <!-- Card Number -->
              <div>
                <label for="pay-card" class="block text-sm font-medium text-gray-700 mb-1.5">Карта нөмірі</label>
                <div class="relative">
                  <input
                    id="pay-card"
                    v-model="cardNumber"
                    type="text"
                    required
                    maxlength="19"
                    placeholder="1234 5678 9012 3456"
                    @input="formatCardNumber"
                    class="w-full pl-4 pr-14 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all font-mono tracking-wider"
                  />
                  <div class="absolute inset-y-0 right-0 pr-4 flex items-center gap-1.5 pointer-events-none">
                    <svg class="w-8 h-5 text-gray-300" viewBox="0 0 32 20" fill="currentColor">
                      <rect width="32" height="20" rx="3" fill="#1A1F71"/>
                      <text x="16" y="13" text-anchor="middle" fill="white" font-size="8" font-weight="bold">VISA</text>
                    </svg>
                  </div>
                </div>
              </div>

              <!-- Expiry + CVC row -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label for="pay-expiry" class="block text-sm font-medium text-gray-700 mb-1.5">Мерзімі</label>
                  <input
                    id="pay-expiry"
                    v-model="expiry"
                    type="text"
                    required
                    maxlength="5"
                    placeholder="MM/YY"
                    @input="formatExpiry"
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all font-mono"
                  />
                </div>
                <div>
                  <label for="pay-cvc" class="block text-sm font-medium text-gray-700 mb-1.5">CVC</label>
                  <input
                    id="pay-cvc"
                    v-model="cvc"
                    type="text"
                    required
                    maxlength="4"
                    placeholder="123"
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all font-mono"
                  />
                </div>
              </div>

              <!-- Divider -->
              <div class="relative py-2">
                <div class="absolute inset-0 flex items-center">
                  <div class="w-full border-t border-gray-200"></div>
                </div>
                <div class="relative flex justify-center text-xs">
                  <span class="bg-white px-3 text-gray-400 uppercase tracking-wide">немесе</span>
                </div>
              </div>

              <!-- Alternative payment methods -->
              <div class="grid grid-cols-3 gap-3">
                <button type="button" @click="handleAltPayment('paypal')"
                  class="flex items-center justify-center gap-2 px-3 py-3 border border-gray-300 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors">
                  <svg class="w-5 h-5" viewBox="0 0 24 24" fill="#003087">
                    <path d="M7.076 21.337H2.47a.641.641 0 01-.633-.74L4.944.901C5.026.382 5.474 0 5.998 0h7.46c2.57 0 4.578.543 5.69 1.81 1.01 1.15 1.304 2.42 1.012 4.287-.023.143-.047.288-.077.437-.983 5.05-4.349 6.797-8.647 6.797h-2.19c-.524 0-.968.382-1.05.9l-1.12 7.106z"/>
                  </svg>
                  PayPal
                </button>
                <button type="button" @click="handleAltPayment('apple')"
                  class="flex items-center justify-center gap-2 px-3 py-3 border border-gray-300 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors">
                  <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
                  </svg>
                   Pay
                </button>
                <button type="button" @click="handleAltPayment('google')"
                  class="flex items-center justify-center gap-2 px-3 py-3 border border-gray-300 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors">
                  <svg class="w-5 h-5" viewBox="0 0 24 24">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                  </svg>
                  Pay
                </button>
              </div>

              <!-- Submit -->
              <button
                type="submit"
                :disabled="processing"
                class="w-full py-3.5 rounded-xl text-base font-semibold text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-4"
                style="background-color: #38B000;"
                onmouseover="if(!this.disabled)this.style.backgroundColor='#2d8a00'"
                onmouseout="this.style.backgroundColor='#38B000'"
              >
                <span v-if="processing" class="inline-flex items-center gap-2">
                  <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
                  Өңделуде...
                </span>
                <span v-else>Жазылымды бастау</span>
              </button>

              <!-- Security note -->
              <p class="text-center text-xs text-gray-400 flex items-center justify-center gap-1.5 mt-3">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                Сіздің деректеріңіз қауіпсіз шифрланған
              </p>
            </form>
          </div>
        </div>

        <!-- Order Summary (right) -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 sm:p-8 sticky top-8">
            <h2 class="text-lg font-semibold text-gray-900 mb-6">Тапсырыс мәліметтері</h2>

            <div class="space-y-4">
              <div class="flex items-center gap-3 pb-4 border-b border-gray-100">
                <div class="w-10 h-10 rounded-lg flex items-center justify-center"
                  :class="planInfo.iconBg">
                  <svg class="w-5 h-5" :class="planInfo.iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="planInfo.iconPath" />
                  </svg>
                </div>
                <div>
                  <p class="font-semibold text-gray-900">{{ planInfo.name }}</p>
                  <p class="text-xs text-gray-500">{{ billingLabel }}</p>
                </div>
              </div>

              <div class="space-y-3 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-500">Жоспар</span>
                  <span class="text-gray-900 font-medium">{{ planInfo.name }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">Бағасы</span>
                  <span class="text-gray-900 font-medium">{{ planInfo.price }}/ай</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">Төлем кезеңі</span>
                  <span class="text-gray-900 font-medium">{{ billingLabel }}</span>
                </div>
              </div>

              <div class="border-t border-gray-100 pt-4">
                <div class="flex justify-between items-center">
                  <span class="text-base font-semibold text-gray-900">Барлығы</span>
                  <span class="text-xl font-bold text-gray-900">{{ planInfo.total }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'

defineOptions({ name: 'PaymentPage' })

const router = useRouter()
const route = useRoute()

const cardName = ref('')
const cardNumber = ref('')
const expiry = ref('')
const cvc = ref('')
const processing = ref(false)

const plan = computed(() => (route.query.plan as string) || 'family')
const billing = computed(() => (route.query.billing as string) || 'monthly')
const billingLabel = computed(() => billing.value === 'yearly' ? 'Жыл сайын' : 'Ай сайын')

const plans: Record<string, { name: string; monthly: string; yearly: string; yearlyTotal: string; monthlyTotal: string; iconBg: string; iconColor: string; iconPath: string }> = {
  family: {
    name: 'Семейный',
    monthly: '₸1,990', yearly: '₸1,590',
    monthlyTotal: '₸1,990', yearlyTotal: '₸19,080',
    iconBg: 'bg-blue-100', iconColor: 'text-blue-600',
    iconPath: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
  },
  classroom: {
    name: 'Классный',
    monthly: '₸9,990', yearly: '₸7,990',
    monthlyTotal: '₸9,990', yearlyTotal: '₸95,880',
    iconBg: 'bg-green-100', iconColor: 'text-green-600',
    iconPath: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-2 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
  },
  school: {
    name: 'Мектеп',
    monthly: '₸49,990', yearly: '₸39,990',
    monthlyTotal: '₸49,990', yearlyTotal: '₸479,880',
    iconBg: 'bg-purple-100', iconColor: 'text-purple-600',
    iconPath: 'M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z',
  },
}

const planInfo = computed(() => {
  const p = plans[plan.value] || plans.family
  return {
    ...p,
    price: billing.value === 'yearly' ? p.yearly : p.monthly,
    total: billing.value === 'yearly' ? p.yearlyTotal : p.monthlyTotal,
  }
})

const formatCardNumber = () => {
  const digits = cardNumber.value.replace(/\D/g, '')
  cardNumber.value = digits.replace(/(.{4})/g, '$1 ').trim()
}

const formatExpiry = () => {
  const digits = expiry.value.replace(/\D/g, '')
  if (digits.length >= 2) {
    expiry.value = digits.slice(0, 2) + '/' + digits.slice(2, 4)
  }
}

const handlePayment = () => {
  processing.value = true
  // Simulate payment processing
  setTimeout(() => {
    processing.value = false
    router.push({ name: 'welcome' })
  }, 2000)
}

const handleAltPayment = (method: string) => {
  alert(`${method.charAt(0).toUpperCase() + method.slice(1)} Pay мүмкіндігі жақында қосылады`)
}
</script>

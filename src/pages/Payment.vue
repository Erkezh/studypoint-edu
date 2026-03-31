<template>
  <div class="min-h-screen bg-[#f3fbfb] flex flex-col font-sans">
    <Header />

    <main class="flex-1 flex flex-col">
      <!-- Top Progress Bar overlaying a white header section -->
      <div class="bg-white border-b border-gray-100 py-6">
        <div class="max-w-4xl mx-auto px-4 w-full flex items-center justify-between relative">
          
          <!-- Desktop Lines -->
          <div class="hidden sm:block absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3/4 h-[2px] bg-gray-200 -z-10"></div>
          
          <!-- Step 1 -->
          <div class="flex items-center gap-2 bg-white px-2">
            <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-colors"
                 :class="currentStep === 1 ? 'bg-[#00a6c0] text-white' : (currentStep > 1 ? 'border-2 border-[#00a6c0] text-[#00a6c0]' : 'border-2 border-gray-300 text-gray-400')">
              <span v-if="currentStep > 1">✓</span>
              <span v-else>1</span>
            </div>
            <span class="font-medium text-[15px] hidden sm:block"
                  :class="currentStep === 1 ? 'text-[#00a6c0]' : (currentStep > 1 ? 'text-[#00a6c0]' : 'text-gray-400')">
              Жазылушы болу
            </span>
          </div>

          <!-- Step 2 -->
          <div class="flex items-center gap-2 bg-white px-2">
            <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-colors"
                 :class="currentStep === 2 ? 'border-2 border-[#ffba00] text-[#ffba00]' : (currentStep > 2 ? 'bg-[#00a6c0] text-white' : 'border-2 border-gray-300 text-gray-400')">
              <span v-if="currentStep > 2">✓</span>
              <span v-else>2</span>
            </div>
            <span class="font-medium text-[15px] hidden sm:block"
                  :class="currentStep === 2 ? 'text-[#ffba00]' : (currentStep > 2 ? 'text-[#00a6c0]' : 'text-gray-400')">
              Аккаунтты баптау
            </span>
          </div>

          <!-- Step 3 -->
          <div class="flex items-center gap-2 bg-white px-2">
            <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-colors"
                 :class="currentStep === 3 ? 'border-2 border-[#00a6c0] text-[#00a6c0]' : 'border-2 border-gray-300 text-gray-400'">
              3
            </div>
            <span class="font-medium text-[15px] hidden sm:block"
                  :class="currentStep === 3 ? 'text-[#00a6c0]' : 'text-gray-400'">
              Қош келдіңіз
            </span>
          </div>
          
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="flex-1 max-w-5xl mx-auto w-full px-4 py-12">
        
        <!-- STEP 1: Plan Selection & Payment -->
        <div v-if="currentStep === 1" class="space-y-12 animate-fade-in">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
            
            <!-- Choose Plan -->
            <div>
              <h2 class="text-2xl font-semibold text-[#1a365d] mb-6">Жоспарды таңдаңыз</h2>
              
              <div class="relative flex border border-gray-300 rounded overflow-hidden mt-6 bg-white">
                <button 
                  @click="billingCycle = 'monthly'"
                  class="flex-1 py-3 px-4 text-center font-medium transition-colors border-r border-gray-300"
                  :class="billingCycle === 'monthly' ? 'bg-[#25b8c6] text-white' : 'text-gray-600 hover:bg-gray-50'"
                >
                  Ай сайын
                </button>
                <div class="flex-1 relative">
                  <button 
                    @click="billingCycle = 'yearly'"
                    class="w-full h-full py-3 px-4 text-center font-medium transition-colors"
                    :class="billingCycle === 'yearly' ? 'bg-[#25b8c6] text-white' : 'text-gray-600 hover:bg-gray-50'"
                  >
                    Жыл сайын
                  </button>
                  <!-- Save Badge -->
                  <div class="absolute -top-6 -right-2 bg-[#ffc107] text-[#1a365d] text-xs font-bold px-3 py-1 shadow-sm shrink-0 whitespace-nowrap transform rotate-2">
                    20% үнемдеңіз!
                    <div class="absolute -bottom-1 right-2 w-2 h-2 bg-[#d39e00] transform rotate-45 -z-10"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Choose Children (Family Only) -->
            <div v-if="planType === 'family'">
              <h2 class="text-2xl font-semibold text-[#1a365d] mb-6">Балалар санын таңдаңыз</h2>
              <div class="flex items-center gap-4">
                <div class="flex bg-white border border-gray-300 rounded overflow-hidden">
                  <button 
                    @click="childrenCount > 1 ? childrenCount-- : null"
                    class="w-12 h-12 flex items-center justify-center text-gray-500 hover:bg-gray-50 border-r border-gray-300"
                    :class="{'opacity-50 cursor-not-allowed': childrenCount <= 1}"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/></svg>
                  </button>
                  <div class="w-16 h-12 flex items-center justify-center font-semibold text-lg text-gray-800">
                    {{ childrenCount }}
                  </div>
                  <button 
                    @click="childrenCount < 10 ? childrenCount++ : null"
                    class="w-12 h-12 flex items-center justify-center text-gray-500 hover:bg-gray-50 border-l border-gray-300"
                    :class="{'opacity-50 cursor-not-allowed': childrenCount >= 10}"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                  </button>
                </div>
                <div class="text-sm text-gray-500">
                  Әр қосымша бала үшін небәрі 1990₸!
                </div>
              </div>
            </div>
            
          </div>

          <!-- Divider -->
          <hr class="border-gray-200">

          <!-- Order Summary and Pay -->
          <div class="bg-white p-8 rounded border border-gray-200 shadow-sm max-w-xl mx-auto text-center">
            <h3 class="text-xl font-medium text-[#1a365d] mb-4">Тапсырыс мәліметтері</h3>
            <div class="text-4xl font-bold text-[#1a365d] mb-2">
              ₸{{ calculatedPrice.toLocaleString() }}
            </div>
            <p class="text-gray-500 mb-8 border-b border-gray-100 pb-8">
              {{ billingCycle === 'monthly' ? 'ай сайын төленеді' : 'жылына бір рет төленеді' }}
              <span v-if="planType === 'family'">({{ childrenCount }} бала үшін)</span>
              <span v-else>(1 мұғалім және оқушылар үшін)</span>
            </p>

            <div v-if="processing" class="py-4 flex flex-col items-center justify-center space-y-3">
              <div class="animate-spin rounded-full h-10 w-10 border-4 border-gray-200 border-t-[#f14635]"></div>
              <p class="text-gray-600 font-medium text-sm">Kaspi арқылы төлем өңделуде...</p>
            </div>
            <button v-else
              @click="processPayment"
              class="w-full py-4 px-6 rounded text-lg font-bold text-white shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-3 transform hover:-translate-y-0.5"
              style="background-color: #f14635;"
            >
              <svg class="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.5v-9l6 4.5-6 4.5z"/>
              </svg>
              Kaspi арқылы төлеу
            </button>
            <p class="mt-4 text-xs text-gray-400">Kaspi қосымшасы ашылады. Төлемнен кейін сіз қайта ораласыз.</p>
          </div>
        </div>

        <!-- STEP 2: Registration -->
        <div v-if="currentStep === 2" class="max-w-2xl mx-auto bg-white p-8 md:p-10 rounded border border-gray-200 shadow-sm animate-fade-in">
          <div class="text-center mb-8">
            <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-100 text-green-500 mb-4">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
            </div>
            <h2 class="text-2xl font-semibold text-[#1a365d] mb-2">Төлеміңіз сәтті өтті!</h2>
            <p class="text-gray-600">Енді оқушылардың аккаунттарын құрамыз.</p>
          </div>

          <!-- Error message -->
          <div v-if="registrationError" class="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start gap-3">
            <svg class="w-5 h-5 text-red-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-sm text-red-700">{{ registrationError }}</p>
          </div>

          <form @submit.prevent="submitRegistration" class="space-y-8">
            <!-- Account Info -->
            <div class="bg-[#f8fafc] p-6 rounded border border-gray-200">
              <h3 class="text-lg font-medium text-[#1a365d] mb-4">
                {{ planType === 'family' ? 'Ата-ана туралы ақпарат' : 'Мұғалім туралы ақпарат' }}
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Толық аты-жөніңіз</label>
                  <input v-model="regData.parentName" type="text" required class="w-full px-4 py-2 rounded border border-gray-300 focus:outline-none focus:border-[#25b8c6] focus:ring-1 focus:ring-[#25b8c6]">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Электрондық пошта</label>
                  <input v-model="regData.parentEmail" type="email" required class="w-full px-4 py-2 rounded border border-gray-300 focus:outline-none focus:border-[#25b8c6] focus:ring-1 focus:ring-[#25b8c6]">
                </div>
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Құпия сөз</label>
                  <input v-model="regData.parentPassword" type="password" required minlength="8" class="w-full px-4 py-2 rounded border border-gray-300 focus:outline-none focus:border-[#25b8c6] focus:ring-1 focus:ring-[#25b8c6]">
                  <p class="text-xs text-gray-400 mt-1">Ең аз 8 таңба: бас әріп, кіші әріп, сан және арнайы таңба (!@#$%)</p>
                </div>
              </div>
            </div>

            <!-- Children Info (Family Only) -->
            <div v-if="planType === 'family'" class="space-y-4">
              <h3 class="text-lg font-medium text-[#1a365d]">Балалар туралы ақпарат</h3>
              
              <div v-for="index in childrenCount" :key="index" class="p-6 rounded border border-gray-200 relative">
                <span class="absolute -top-3 left-4 bg-white px-2 text-sm font-bold text-gray-500">Бала {{ index }}</span>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Есімі</label>
                    <input v-model="regData.children[index-1].name" type="text" required class="w-full px-4 py-2 rounded border border-gray-300 focus:outline-none focus:border-[#25b8c6] focus:ring-1 focus:ring-[#25b8c6]">
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Сыныбы</label>
                    <select v-model="regData.children[index-1].grade" required class="w-full px-4 py-2 rounded border border-gray-300 focus:outline-none focus:border-[#25b8c6] focus:ring-1 focus:ring-[#25b8c6] bg-white">
                      <option value="" disabled selected>Сыныпты таңдаңыз</option>
                      <option v-for="n in 12" :key="n" :value="n">{{ n }}-сынып</option>
                      <option value="pre-k">Мектепке дейінгі</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <button type="submit" :disabled="submittingRegistration" class="w-full py-3 px-6 rounded text-lg font-medium text-white transition-colors bg-[#5ba100] hover:bg-[#4a8400] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
              <div v-if="submittingRegistration" class="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
              {{ submittingRegistration ? 'Тіркелуде...' : 'Жалғастыру' }}
            </button>
          </form>
        </div>

        <!-- STEP 3: Welcome -->
        <div v-if="currentStep === 3" class="max-w-xl mx-auto bg-white p-12 rounded border border-gray-200 shadow-sm text-center animate-fade-in">
          <div class="w-20 h-20 bg-[#5ba100] rounded-full mx-auto flex items-center justify-center mb-6">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
          </div>
          <h2 class="text-3xl font-semibold text-[#1a365d] mb-4">Қош келдіңіз!</h2>
          <p class="text-gray-600 mb-8 text-lg">
            Сіздің {{ planType === 'family' ? 'отбасылық' : 'мұғалімдік' }} аккаунтыңыз сәтті құрылды. Енді сіз платформаның барлық мүмкіндіктерін пайдалана аласыз.
          </p>
          <button @click="router.push('/')" class="py-3 px-8 rounded font-medium text-white transition-colors bg-[#00a6c0] hover:bg-[#008f9c]">
            Бастау
          </button>
        </div>

      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import type { ApiResponse, AuthTokensResponse } from '@/types/api'
import { UserRole } from '@/types/api'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'

defineOptions({ name: 'PaymentPage' })

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const planType = computed(() => route.query.plan === 'classroom' ? 'classroom' : 'family')

// Current Step
const currentStep = ref(1)

// Step 1 State: Selection
const billingCycle = ref<'monthly' | 'yearly'>('monthly')
const childrenCount = ref(1)
const processing = ref(false)

const baseMonthlyPrice = 1990
const baseYearlyPrice = 1590

const classroomMonthlyPrice = 14990
const classroomYearlyPrice = 12990

const calculatedPrice = computed(() => {
  if (planType.value === 'classroom') {
    return billingCycle.value === 'monthly' ? classroomMonthlyPrice : classroomYearlyPrice * 12
  } else {
    return billingCycle.value === 'monthly' ? baseMonthlyPrice * childrenCount.value : baseYearlyPrice * 12 * childrenCount.value
  }
})

const processPayment = () => {
  processing.value = true
  setTimeout(() => {
    processing.value = false
    currentStep.value = 2
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, 2000)
}

// Step 2 State: Registration
interface ChildData {
  name: string
  grade: string | number
}

const regData = ref({
  parentName: '',
  parentEmail: '',
  parentPassword: '',
  children: [{ name: '', grade: '' }] as ChildData[]
})

const registrationError = ref<string | null>(null)
const submittingRegistration = ref(false)

watch(childrenCount, (newCount) => {
  const currentLen = regData.value.children.length
  if (newCount > currentLen) {
    for (let i = currentLen; i < newCount; i++) {
      regData.value.children.push({ name: '', grade: '' })
    }
  } else if (newCount < currentLen) {
    regData.value.children.splice(newCount)
  }
})

const submitRegistration = async () => {
  if (submittingRegistration.value) return
  registrationError.value = null
  submittingRegistration.value = true

  try {
    let resp: ApiResponse<AuthTokensResponse>;
    if (planType.value === 'classroom') {
      resp = await authApi.register({
        email: regData.value.parentEmail,
        password: regData.value.parentPassword,
        full_name: regData.value.parentName,
        role: UserRole.TEACHER,
        grade_level: 1, // default
      })
    } else {
      resp = await authApi.registerFamily({
        parent_email: regData.value.parentEmail,
        parent_password: regData.value.parentPassword,
        parent_name: regData.value.parentName,
        children: regData.value.children.map(c => ({
          name: c.name,
          grade_level: typeof c.grade === 'number' ? c.grade : parseInt(String(c.grade)) || 1,
        })),
      })
    }

    if (resp.data) {
      // Log in as parent
      authStore.setAccessToken(resp.data.access_token)
      authStore.setRefreshToken(resp.data.refresh_token)
      authStore.user = resp.data.user
      localStorage.setItem('user', JSON.stringify(resp.data.user))

      currentStep.value = 3
      window.scrollTo({ top: 0, behavior: 'smooth' })

      // Auto-redirect to home after 3 seconds since user is already logged in
      setTimeout(() => {
        router.push('/')
      }, 3000)
    }
  } catch (err: unknown) {
    console.error('Family registration error:', err)
    const axiosErr = err as { response?: { data?: { detail?: any; message?: string }, status?: number }, message?: string }
    const resp = axiosErr.response
    
    if (resp?.status === 422 && Array.isArray(resp.data?.detail)) {
      // Pydantic validation errors - translate common ones to Kazakh
      const messages = resp.data.detail.map((e: any) => {
        const msg = String(e.msg || e.message || '')
        if (msg.includes('mixed case')) return 'Құпия сөзде үлкен және кіші әріптер болуы керек'
        if (msg.includes('digit')) return 'Құпия сөзде кемінде 1 сан болуы керек'
        if (msg.includes('at least 8')) return 'Құпия сөз кемінде 8 таңба болуы керек'
        if (msg.includes('special character')) return 'Құпия сөзде кемінде 1 арнайы таңба болуы керек (!@#$%)'
        if (msg.includes('valid email')) return 'Дұрыс email мекенжайын енгізіңіз'
        return msg
      })
      registrationError.value = messages.join('. ')
    } else if (resp?.data?.message) {
      registrationError.value = resp.data.message
    } else {
      registrationError.value = axiosErr.message || 'Тіркелу қатесі. Қайта көріңіз.'
    }
  } finally {
    submittingRegistration.value = false
  }
}

</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

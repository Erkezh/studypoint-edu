import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface PlanPricing {
  monthlyPrice: number
  yearlyPrice: number
  discountPercent: number
  discountLabel: string
}

export interface PromoCode {
  id: string
  code: string
  discountType: 'percent' | 'fixed'
  discountValue: number
  usageLimit: number
  usageCount: number
  expiresAt: string | null
  isActive: boolean
  createdAt: string
}

const STORAGE_KEY_PRICING = 'studypoint_admin_plan_pricing'
const STORAGE_KEY_PROMOCODES = 'studypoint_admin_promocodes'

const defaultPricing: Record<string, PlanPricing> = {
  FAMILY: {
    monthlyPrice: 1990,
    yearlyPrice: 1590,
    discountPercent: 20,
    discountLabel: 'Отбасылық жеңілдік -20%',
  },
  CLASSROOM: {
    monthlyPrice: 14990,
    yearlyPrice: 12990,
    discountPercent: 15,
    discountLabel: 'Сыныптық арнайы баға',
  },
  SCHOOL: {
    monthlyPrice: 49990,
    yearlyPrice: 42990,
    discountPercent: 25,
    discountLabel: 'Мектептік корпоративтік',
  },
}

const defaultPromoCodes: PromoCode[] = [
  {
    id: '1',
    code: 'STUDY2026',
    discountType: 'percent',
    discountValue: 20,
    usageLimit: 100,
    usageCount: 14,
    expiresAt: '2026-12-31',
    isActive: true,
    createdAt: new Date().toISOString(),
  },
  {
    id: '2',
    code: 'WELCOME1000',
    discountType: 'fixed',
    discountValue: 1000,
    usageLimit: 50,
    usageCount: 8,
    expiresAt: '2026-10-01',
    isActive: true,
    createdAt: new Date().toISOString(),
  },
]

export const usePricingStore = defineStore('pricing', () => {
  const pricing = ref<Record<string, PlanPricing>>(loadPricing())
  const promoCodes = ref<PromoCode[]>(loadPromoCodes())

  function loadPricing(): Record<string, PlanPricing> {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_PRICING)
      return saved ? { ...defaultPricing, ...JSON.parse(saved) } : { ...defaultPricing }
    } catch {
      return { ...defaultPricing }
    }
  }

  function loadPromoCodes(): PromoCode[] {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_PROMOCODES)
      return saved ? JSON.parse(saved) : [...defaultPromoCodes]
    } catch {
      return [...defaultPromoCodes]
    }
  }

  function savePricing() {
    localStorage.setItem(STORAGE_KEY_PRICING, JSON.stringify(pricing.value))
  }

  function savePromoCodes() {
    localStorage.setItem(STORAGE_KEY_PROMOCODES, JSON.stringify(promoCodes.value))
  }

  function updatePlanPricing(plan: string, data: Partial<PlanPricing>) {
    if (!pricing.value[plan]) {
      pricing.value[plan] = { monthlyPrice: 0, yearlyPrice: 0, discountPercent: 0, discountLabel: '' }
    }
    pricing.value[plan] = { ...pricing.value[plan], ...data }
    savePricing()
  }

  function addPromoCode(codeData: Omit<PromoCode, 'id' | 'createdAt' | 'usageCount'>) {
    const newCode: PromoCode = {
      id: Date.now().toString(),
      ...codeData,
      code: codeData.code.toUpperCase().trim(),
      usageCount: 0,
      createdAt: new Date().toISOString(),
    }
    promoCodes.value.unshift(newCode)
    savePromoCodes()
  }

  function updatePromoCode(id: string, updates: Partial<PromoCode>) {
    const idx = promoCodes.value.findIndex(p => p.id === id)
    if (idx !== -1) {
      promoCodes.value[idx] = { ...promoCodes.value[idx], ...updates }
      savePromoCodes()
    }
  }

  function deletePromoCode(id: string) {
    promoCodes.value = promoCodes.value.filter(p => p.id !== id)
    savePromoCodes()
  }

  function validatePromoCode(code: string): { valid: boolean; promo?: PromoCode; error?: string } {
    if (!code || !code.trim()) {
      return { valid: false, error: 'Промокодты енгізіңіз' }
    }
    const formatted = code.toUpperCase().trim()
    const found = promoCodes.value.find(p => p.code === formatted)

    if (!found) {
      return { valid: false, error: 'Промокод табылмады' }
    }
    if (!found.isActive) {
      return { valid: false, error: 'Бұл промокод белсенді емес' }
    }
    if (found.usageLimit > 0 && found.usageCount >= found.usageLimit) {
      return { valid: false, error: 'Промокодтың қолдану лимиті таусылды' }
    }
    if (found.expiresAt) {
      const exp = new Date(found.expiresAt)
      if (exp < new Date()) {
        return { valid: false, error: 'Промокодтың мерзімі аяқталған' }
      }
    }

    return { valid: true, promo: found }
  }

  function calculateDiscountedPrice(originalPrice: number, promoCode?: string): { finalPrice: number; discountAmount: number; promoApplied?: PromoCode } {
    if (!promoCode) {
      return { finalPrice: originalPrice, discountAmount: 0 }
    }
    const val = validatePromoCode(promoCode)
    if (!val.valid || !val.promo) {
      return { finalPrice: originalPrice, discountAmount: 0 }
    }

    const promo = val.promo
    let discount = 0
    if (promo.discountType === 'percent') {
      discount = Math.round((originalPrice * promo.discountValue) / 100)
    } else {
      discount = promo.discountValue
    }

    const finalPrice = Math.max(0, originalPrice - discount)
    return { finalPrice, discountAmount: discount, promoApplied: promo }
  }

  function usePromoCode(code: string) {
    const val = validatePromoCode(code)
    if (val.valid && val.promo) {
      updatePromoCode(val.promo.id, { usageCount: val.promo.usageCount + 1 })
    }
  }

  return {
    pricing,
    promoCodes,
    updatePlanPricing,
    addPromoCode,
    updatePromoCode,
    deletePromoCode,
    validatePromoCode,
    calculateDiscountedPrice,
    usePromoCode,
  }
})

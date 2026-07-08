import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { gamificationApi } from '@/api/gamification'
import type { GamificationGarageItem, GamificationProfile, GamificationReward, GamificationVehicle } from '@/types/api'

const defaultVehicles: GamificationVehicle[] = [
  { id: 'skateboard', name: 'Скейтборд', slug: 'skateboard', unlock_level: 1, unlock_xp: 0, coin_price: 0, is_unlocked: true, is_owned: true, is_selected: true },
  { id: 'e2f-scooter-yellow', name: 'E2F скутері', slug: 'scooter', unlock_level: 2, unlock_xp: 200, coin_price: 300, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'btwin-triban-100-bike', name: 'BTWIN Triban 100 велосипеді', slug: 'bicycle', unlock_level: 3, unlock_xp: 500, coin_price: 700, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'ducati-streetfighter-v4-s', name: 'Ducati Streetfighter V4 S мотоциклі', slug: 'motorbike', unlock_level: 4, unlock_xp: 900, coin_price: 1500, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'suzuki-quadzilla-500', name: 'Suzuki Quadzilla 500 квадроциклі', slug: 'quad-bike', unlock_level: 5, unlock_xp: 1500, coin_price: 3000, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'mini-car-low-poly-v02', name: 'Mini Car Low Poly', slug: 'city-car', unlock_level: 6, unlock_xp: 2400, coin_price: 5000, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'ford-mustang-shelby-cobra-gt500', name: 'Ford Mustang Shelby Cobra GT500', slug: 'suv', unlock_level: 7, unlock_xp: 3500, coin_price: 8000, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'jaguar-project-7', name: 'Project 7 көлігі', slug: 'sports-car', unlock_level: 8, unlock_xp: 5000, coin_price: 12000, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'mclaren-720s-spider', name: 'McLaren 720S Spider', slug: 'supercar', unlock_level: 9, unlock_xp: 7000, coin_price: 18000, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'porsche-963-lmdh-hypercar', name: 'Porsche 963 LMDh', slug: 'hypercar', unlock_level: 10, unlock_xp: 10000, coin_price: 30000, is_unlocked: false, is_owned: false, is_selected: false },
]

export const useGamificationStore = defineStore('gamification', () => {
  const xp = ref(0)
  const coins = ref(0)
  const level = ref(1)
  const comboStreak = ref(0)
  const dailyStreak = ref(0)
  const totalProblemsSolved = ref(0)
  const nextLevelXp = ref(200)
  const vehicles = ref<GamificationVehicle[]>(defaultVehicles)
  const ownedVehicles = ref<string[]>(['skateboard'])
  const selectedVehicle = ref('skateboard')
  const shopItems = ref<GamificationGarageItem[]>([])
  const lastReward = ref<GamificationReward | null>(null)
  const isLoading = ref(false)
  const isSaving = ref(false)

  const xpProgress = computed(() => {
    if (nextLevelXp.value <= 0) return 100
    return Math.min(100, Math.round((xp.value / nextLevelXp.value) * 100))
  })
  const streak = computed(() => dailyStreak.value)

  function applyProfile(profile: GamificationProfile) {
    xp.value = profile.xp
    coins.value = profile.coins
    level.value = profile.level
    comboStreak.value = profile.combo_streak
    dailyStreak.value = profile.daily_streak
    totalProblemsSolved.value = profile.total_problems_solved
    nextLevelXp.value = profile.next_level_xp
    vehicles.value = profile.vehicles ?? []
    ownedVehicles.value = profile.owned_vehicles ?? []
    selectedVehicle.value = profile.selected_vehicle ?? 'skateboard'
    shopItems.value = profile.shop_items ?? []
  }

  async function fetchGamification() {
    isLoading.value = true
    try {
      const response = await gamificationApi.getMe()
      if (response.data) applyProfile(response.data)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchProfile() {
    await fetchGamification()
  }

  async function submitAnswer(data: {
    question_id: number | string
    correct: boolean
    difficulty: 'easy' | 'medium' | 'hard'
  }) {
    const response = await gamificationApi.submitAnswerResult(data)
    if (response.data) {
      lastReward.value = response.data
      await fetchGamification()
    }
    return response.data ?? null
  }

  async function buyVehicle(vehicleId: string) {
    isSaving.value = true
    try {
      const response = await gamificationApi.buyVehicle(vehicleId)
      if (response.data) applyProfile(response.data)
    } finally {
      isSaving.value = false
    }
  }

  async function selectVehicle(vehicleId: string) {
    isSaving.value = true
    try {
      const response = await gamificationApi.selectVehicle(vehicleId)
      if (response.data) applyProfile(response.data)
    } finally {
      isSaving.value = false
    }
  }

  async function buyItem(itemId: string) {
    isSaving.value = true
    try {
      const response = await gamificationApi.buyItem(itemId)
      if (response.data) applyProfile(response.data)
    } finally {
      isSaving.value = false
    }
  }

  async function equipItem(vehicleId: string, itemType: string, itemId?: string | null) {
    isSaving.value = true
    try {
      const response = await gamificationApi.equipItem({
        vehicle_id: vehicleId,
        item_type: itemType,
        item_id: itemId ?? null,
      })
      if (response.data) applyProfile(response.data)
    } finally {
      isSaving.value = false
    }
  }

  function applyReward(reward?: GamificationReward | null) {
    if (!reward) return
    lastReward.value = reward
    xp.value += reward.xp_gained
    coins.value += reward.coins_gained
    comboStreak.value = reward.combo_streak
    level.value = reward.new_level
    if (reward.daily_streak !== undefined) dailyStreak.value = reward.daily_streak
  }

  return {
    xp,
    coins,
    level,
    comboStreak,
    dailyStreak,
    totalProblemsSolved,
    nextLevelXp,
    vehicles,
    ownedVehicles,
    selectedVehicle,
    shopItems,
    lastReward,
    isLoading,
    isSaving,
    xpProgress,
    streak,
    fetchGamification,
    fetchProfile,
    submitAnswer,
    buyVehicle,
    selectVehicle,
    buyItem,
    equipItem,
    applyReward,
  }
})

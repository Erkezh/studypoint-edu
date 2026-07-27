import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { gamificationApi } from '@/api/gamification'
import type { GamificationGarageItem, GamificationProfile, GamificationReward, GamificationVehicle } from '@/types/api'

const defaultVehicles: GamificationVehicle[] = [
  { id: 'skateboard', name: 'Скейтборд', slug: 'skateboard', type: 'skateboard', unlock_level: 1, level_required: 1, unlock_xp: 0, xp_required: 0, coin_price: 100, price: 100, is_unlocked: true, is_owned: true, is_selected: true },
  { id: 'e2f-scooter-yellow', name: 'Скутер', slug: 'scooter', type: 'scooter', unlock_level: 2, level_required: 2, unlock_xp: 300, xp_required: 300, coin_price: 250, price: 250, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'btwin-triban-100-bike', name: 'Велосипед', slug: 'bike', type: 'bike', unlock_level: 3, level_required: 3, unlock_xp: 700, xp_required: 700, coin_price: 500, price: 500, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'vino', name: 'Vino көлігі', slug: 'vino', type: 'car', unlock_level: 4, level_required: 4, unlock_xp: 1200, xp_required: 1200, coin_price: 900, price: 900, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'free-concept-sport-bike', name: 'Спорт мотоцикл', slug: 'concept-sport-bike', type: 'motorbike', unlock_level: 5, level_required: 5, unlock_xp: 1800, xp_required: 1800, coin_price: 1400, price: 1400, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'ducati-streetfighter-v4-s', name: 'Мотоцикл', slug: 'motorbike', type: 'motorbike', unlock_level: 6, level_required: 6, unlock_xp: 2500, xp_required: 2500, coin_price: 2100, price: 2100, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'suzuki-quadzilla-500', name: 'Квадроцикл', slug: 'quad-bike', type: 'quad-bike', unlock_level: 7, level_required: 7, unlock_xp: 3300, xp_required: 3300, coin_price: 3000, price: 3000, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'mini-car-low-poly-v02', name: 'Шағын көлік', slug: 'small-car', type: 'small-car', unlock_level: 8, level_required: 8, unlock_xp: 4300, xp_required: 4300, coin_price: 4200, price: 4200, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'ford-mustang-shelby-cobra-gt500', name: 'Көлік', slug: 'car', type: 'car', unlock_level: 9, level_required: 9, unlock_xp: 5500, xp_required: 5500, coin_price: 6000, price: 6000, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'jaguar-project-7', name: 'Спорт көлік', slug: 'sport-car', type: 'sport-car', unlock_level: 10, level_required: 10, unlock_xp: 7000, xp_required: 7000, coin_price: 8500, price: 8500, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'mclaren-720s-spider', name: 'Суперкөлік', slug: 'supercar', type: 'supercar', unlock_level: 11, level_required: 11, unlock_xp: 8800, xp_required: 8800, coin_price: 11000, price: 11000, is_unlocked: false, is_owned: false, is_selected: false },
  { id: 'porsche-963-lmdh-hypercar', name: 'Гиперкөлік', slug: 'hypercar', type: 'hypercar', unlock_level: 12, level_required: 12, unlock_xp: 10900, xp_required: 10900, coin_price: 13500, price: 13500, is_unlocked: false, is_owned: false, is_selected: false },
]

const levelXpThresholds = [0, 300, 700, 1200, 1800, 2500, 3300, 4300, 5500, 7000, 8800, 10900]

export const useGamificationStore = defineStore('gamification', () => {
  const xp = ref(0)
  const coins = ref(0)
  const level = ref(1)
  const comboStreak = ref(0)
  const dailyStreak = ref(0)
  const totalProblemsSolved = ref(0)
  const nextLevelXp = ref(300)
  const vehicles = ref<GamificationVehicle[]>(defaultVehicles)
  const ownedVehicles = ref<string[]>(['skateboard'])
  const selectedVehicle = ref('skateboard')
  const shopItems = ref<GamificationGarageItem[]>([])
  const lastReward = ref<GamificationReward | null>(null)
  const isLoading = ref(false)
  const isSaving = ref(false)

  const xpProgress = computed(() => {
    const previousLevelXp = levelXpThresholds[Math.max(0, level.value - 1)] ?? 0
    const nextXp = nextLevelXp.value
    if (nextXp <= previousLevelXp) return 100
    return Math.min(100, Math.round(((xp.value - previousLevelXp) / (nextXp - previousLevelXp)) * 100))
  })
  const streak = computed(() => dailyStreak.value)

  function applyProfile(profile: GamificationProfile) {
    xp.value = profile.xp
    coins.value = profile.coins
    level.value = profile.level
    comboStreak.value = profile.combo_streak
    dailyStreak.value = profile.streak ?? profile.daily_streak
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
    topic_id?: number
    smartscore_before?: number
    smartscore_after?: number
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

import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { gameSettingsApi } from '@/api/gameSettings'
import type { GameSettings, GameType } from '@/types/api'

export const useGameSettingsStore = defineStore('game-settings', () => {
  const activeGame = ref<GameType | null>(null)
  const gameSelectedAt = ref<string | null>(null)
  const lastGameSwitchAt = ref<string | null>(null)
  const canSwitch = ref(false)
  const nextSwitchAvailableAt = ref<string | null>(null)
  const isLoading = ref(false)
  const loaded = ref(false)
  const error = ref<string | null>(null)

  const isCarGame = computed(() => activeGame.value === 'car')
  const isCharacterGame = computed(() => activeGame.value === 'character')
  const hasSelectedGame = computed(() => activeGame.value !== null)
  const activeGameLabel = computed(() => isCarGame.value ? 'Car Garage' : isCharacterGame.value ? 'Character World' : 'Not selected')

  function apply(settings: GameSettings) {
    activeGame.value = settings.active_game
    gameSelectedAt.value = settings.game_selected_at
    lastGameSwitchAt.value = settings.last_game_switch_at
    canSwitch.value = settings.can_switch
    nextSwitchAvailableAt.value = settings.next_switch_available_at
    loaded.value = true
  }

  async function run(request: () => ReturnType<typeof gameSettingsApi.get>) {
    isLoading.value = true
    error.value = null
    try {
      const response = await request()
      if (response.data.data) apply(response.data.data)
      return response.data.data
    } catch (cause: any) {
      error.value = cause?.response?.data?.error?.message || cause?.message || 'Unable to load game settings.'
      throw cause
    } finally {
      isLoading.value = false
    }
  }

  const fetchGameSettings = (force = false) => {
    if (loaded.value && !force) return Promise.resolve(null)
    return run(() => gameSettingsApi.get())
  }
  const selectGame = (game: GameType) => run(() => gameSettingsApi.select(game))
  const switchGame = (game: GameType) => run(() => gameSettingsApi.switch(game))
  const reset = () => {
    activeGame.value = null
    loaded.value = false
    error.value = null
  }

  return {
    activeGame, gameSelectedAt, lastGameSwitchAt, canSwitch, nextSwitchAvailableAt,
    isLoading, loaded, error, isCarGame, isCharacterGame, hasSelectedGame, activeGameLabel,
    fetchGameSettings, selectGame, switchGame, reset,
  }
})

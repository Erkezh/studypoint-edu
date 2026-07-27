import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGameSettingsStore } from '@/stores/gameSettings'
import type { GameType } from '@/types/api'

const STORAGE_KEY = 'studypoint-game-trials'

function readTriedGames(): GameType[] {
  try {
    const value = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || '[]')
    return Array.isArray(value) ? value.filter(game => game === 'car' || game === 'character') : []
  } catch {
    return []
  }
}

export function useGameTrial(game: GameType) {
  const route = useRoute()
  const router = useRouter()
  const gameSettings = useGameSettingsStore()
  const triedGames = ref<GameType[]>(readTriedGames())
  const isTrial = computed(() => route.query.trial === '1')
  const hasTriedBoth = computed(() => triedGames.value.includes('car') && triedGames.value.includes('character'))
  const otherGame = computed<GameType>(() => game === 'car' ? 'character' : 'car')

  onMounted(() => {
    if (!isTrial.value || triedGames.value.includes(game)) return
    triedGames.value = [...triedGames.value, game]
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(triedGames.value))
  })

  async function tryOtherGame() {
    await router.push({
      name: otherGame.value === 'car' ? 'garage' : 'avatar-demo',
      query: { trial: '1' },
    })
  }

  async function chooseGame() {
    if (!hasTriedBoth.value) return
    await gameSettings.selectGame(game)
    sessionStorage.removeItem(STORAGE_KEY)
    await router.replace({ name: game === 'car' ? 'garage' : 'avatar-demo' })
  }

  function backToSelection() {
    return router.push({ name: 'game-select' })
  }

  return reactive({
    isTrial,
    hasTriedBoth,
    isChoosing: computed(() => gameSettings.isLoading),
    tryOtherGame,
    chooseGame,
    backToSelection,
  })
}

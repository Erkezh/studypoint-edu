import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import {
  defaultGarageSelection,
  garageCategories,
  garageParts,
  type GarageCategoryId,
  type GaragePart,
  type GarageSelection,
} from '@/config/garage'
import { garageApi } from '@/api/garageApi'

export const useGarageStore = defineStore('garage', () => {
  const player = ref({
    username: 'Aya',
    level: 7,
    xp: 68,
    coins: 2840,
    gems: 42,
    avatar: 'A',
  })
  const categories = ref(garageCategories)
  const parts = ref<Record<string, GaragePart[]>>(garageParts)
  const selection = ref<GarageSelection>({ ...defaultGarageSelection })
  const activeCategory = ref<GarageCategoryId>('body')
  const isFinished = ref(false)
  const isSaving = ref(false)

  const activeMeta = computed(() => categories.value.find((item) => item.id === activeCategory.value))
  const activeOptions = computed(() => {
    const control = activeMeta.value?.control
    if (control === 'paint') return parts.value.paint ?? []
    if (control === 'rims') return parts.value.rims ?? []
    if (control === 'windows') return parts.value.windows ?? []
    if (control === 'stickerColor') return parts.value.stickerColor ?? parts.value.stickerColors ?? []
    return parts.value[activeCategory.value] ?? []
  })

  const bodyPart = computed(() => findPart('body', selection.value.body))
  const wheelPart = computed(() => findPart('wheels', selection.value.wheels ?? 'wheel4'))
  const paintColor = computed(() => findPart('paint', selection.value.paint)?.value)
  const rimColor = computed(() => findPart('rims', selection.value.rimColor)?.value ?? '#d7f4ff')
  const windowTint = computed(() => findPart('windows', selection.value.windowTint))
  const stickerColor = computed(() => findPart('stickerColors', selection.value.stickerColor)?.value ?? '#f2f0e8')

  const findPart = (category: string, id: string) => parts.value[category]?.find((part) => part.id === id)

  const load = async () => {
    const [config, playerSelection] = await Promise.all([
      garageApi.getConfig(),
      garageApi.getPlayerCar(),
    ])
    const configPayload = config as {
      categories?: typeof garageCategories
      parts?: Record<string, GaragePart[]>
      defaults?: GarageSelection
    }
    categories.value = configPayload.categories ?? garageCategories
    parts.value = configPayload.parts ?? garageParts
    const nextSelection = { ...(configPayload.defaults ?? defaultGarageSelection), ...playerSelection }
    if (!parts.value.stickerColors?.some((part) => part.id === nextSelection.stickerColor)) {
      nextSelection.stickerColor = defaultGarageSelection.stickerColor
    }
    selection.value = nextSelection
  }

  const selectCategory = (category: GarageCategoryId) => {
    activeCategory.value = category
  }

  const selectOption = (option: GaragePart) => {
    const control = activeMeta.value?.control
    if (control === 'paint') {
      selection.value.paint = option.id
    } else if (control === 'rims') {
      selection.value.rimColor = option.id
      selection.value.rims = option.id
    } else if (control === 'windows') {
      selection.value.windowTint = option.id
      selection.value.windows = option.id
    } else if (control === 'stickerColor') {
      selection.value.stickerColor = option.id
    } else {
      ;(selection.value[activeCategory.value as keyof GarageSelection] as string) = option.id
    }
  }

  const randomize = async () => {
    selection.value = await garageApi.randomize(selection.value)
  }

  const reset = () => {
    selection.value = { ...defaultGarageSelection }
    isFinished.value = false
  }

  const finish = async () => {
    isSaving.value = true
    try {
      await garageApi.save(selection.value)
      isFinished.value = true
    } finally {
      isSaving.value = false
    }
  }

  return {
    player,
    categories,
    parts,
    selection,
    activeCategory,
    activeMeta,
    activeOptions,
    bodyPart,
    wheelPart,
    paintColor,
    rimColor,
    windowTint,
    stickerColor,
    isFinished,
    isSaving,
    load,
    selectCategory,
    selectOption,
    randomize,
    reset,
    finish,
  }
})

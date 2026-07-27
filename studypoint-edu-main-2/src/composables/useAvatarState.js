import { computed, ref, watch } from 'vue'
import {
  ACTIVE_CATEGORY_IDS,
  AVATAR_STORAGE_KEY,
  DEFAULT_ITEM_NAMES,
  REQUIRED_CATEGORY_IDS,
} from '@/data/avatarDefaults'

const EXCLUSIVE_CATEGORY_GROUPS = [
  ['top', 'overall'],
  ['bottom', 'overall'],
]

function clearConflictingCategories(selections, categoryId) {
  const next = { ...selections }
  for (const group of EXCLUSIVE_CATEGORY_GROUPS) {
    if (!group.includes(categoryId)) continue
    for (const conflict of group) {
      if (conflict !== categoryId) next[conflict] = null
    }
  }
  return next
}

function findDefaultItem(groups, categoryId) {
  const items = groups?.[categoryId] || []
  const preferredName = DEFAULT_ITEM_NAMES[categoryId]
  return items.find((item) => item.sourceName === preferredName) || items[0] || null
}

function readSavedState() {
  try {
    const saved = JSON.parse(localStorage.getItem(AVATAR_STORAGE_KEY) || '{}')
    if (!saved || typeof saved !== 'object') return { selections: {}, colorOverrides: {} }
    return saved.selections
      ? { selections: saved.selections, colorOverrides: saved.colorOverrides || {} }
      : { selections: saved, colorOverrides: {} }
  } catch {
    return { selections: {}, colorOverrides: {} }
  }
}

export function useAvatarState(manifest) {
  const selectedIds = ref({})
  const colorOverrides = ref({})
  const savedAt = ref('')

  const selectedItems = computed(() => {
    const groups = manifest.value?.groups || {}
    const items = {}

    for (const [categoryId, id] of Object.entries(selectedIds.value)) {
      if (!ACTIVE_CATEGORY_IDS.includes(categoryId)) continue
      if (!id) continue
      const item = groups[categoryId]?.find((candidate) => candidate.id === id)
      if (item) items[categoryId] = colorOverrides.value[categoryId]
        ? { ...item, presetColors: colorOverrides.value[categoryId] }
        : item
    }

    return items
  })

  const selectedPreset = computed(() =>
    manifest.value?.groups?.characters?.find((preset) => preset.id === selectedIds.value.characters) || null,
  )

  const visibleItems = computed(() =>
    ACTIVE_CATEGORY_IDS.map((categoryId) => selectedItems.value[categoryId]).filter(Boolean),
  )

  function buildDefaults() {
    const groups = manifest.value?.groups || {}
    const next = {}

    for (const categoryId of REQUIRED_CATEGORY_IDS) {
      const item = findDefaultItem(groups, categoryId)
      if (item) next[categoryId] = item.id
    }

    return next
  }

  function applySelections(nextSelections) {
    const groups = manifest.value?.groups || {}
    const defaults = buildDefaults()
    let next = { ...defaults }

    for (const [categoryId, id] of Object.entries(nextSelections || {})) {
      if (!ACTIVE_CATEGORY_IDS.includes(categoryId)) continue
      if (id === null) {
        next[categoryId] = null
        continue
      }

      const exists = groups[categoryId]?.some((item) => item.id === id)
      if (exists) {
        next = clearConflictingCategories(next, categoryId)
        next[categoryId] = id
      }
    }

    selectedIds.value = next
  }

  function restore() {
    const saved = readSavedState()
    colorOverrides.value = saved.colorOverrides
    applySelections(saved.selections)
    if (saved.selections.characters) {
      selectedIds.value = { ...selectedIds.value, characters: saved.selections.characters }
    }
  }

  function reset() {
    colorOverrides.value = {}
    selectedIds.value = buildDefaults()
  }

  function selectItem(categoryId, itemId) {
    colorOverrides.value = { ...colorOverrides.value, [categoryId]: null }
    selectedIds.value = {
      ...clearConflictingCategories(selectedIds.value, categoryId),
      characters: null,
      [categoryId]: itemId,
    }
  }

  function setEyeColor(hex) {
    if (!/^#[0-9a-f]{6}$/i.test(hex)) return
    const eyeItem = selectedItems.value.eyes
    if (!eyeItem) return
    const rgb = {
      r: Number.parseInt(hex.slice(1, 3), 16) / 255,
      g: Number.parseInt(hex.slice(3, 5), 16) / 255,
      b: Number.parseInt(hex.slice(5, 7), 16) / 255,
      a: 1,
    }
    const colors = [...(colorOverrides.value.eyes || eyeItem.presetColors || [])]
    colors[0] = rgb
    colors[2] = { r: rgb.r * 0.28, g: rgb.g * 0.28, b: rgb.b * 0.28, a: 1 }
    colorOverrides.value = { ...colorOverrides.value, eyes: colors }
    selectedIds.value = { ...selectedIds.value, characters: null }
  }

  function applyPreset(presetId) {
    const groups = manifest.value?.groups || {}
    const preset = groups.characters?.find((candidate) => candidate.id === presetId)
    if (!preset) return

    let next = Object.fromEntries(ACTIVE_CATEGORY_IDS.map((categoryId) => [categoryId, null]))
    next = { ...next, ...buildDefaults(), characters: preset.id }
    const nextColors = {}

    for (const outfit of preset.outfits || []) {
      const sourceName = outfit.sourceName.toLowerCase()
      const item = Object.values(groups).flat().find((candidate) => candidate.sourceName?.toLowerCase() === sourceName)
      if (!item || !ACTIVE_CATEGORY_IDS.includes(item.category)) {
        if (import.meta.env.DEV) console.warn('[bozo-preset] Outfit is unavailable in the web manifest', {
          preset: preset.name,
          outfit: outfit.outfitPath,
        })
        continue
      }
      next = clearConflictingCategories(next, item.category)
      next[item.category] = item.id
      nextColors[item.category] = outfit.colors
    }

    colorOverrides.value = nextColors
    selectedIds.value = next
  }

  function randomize() {
    colorOverrides.value = {}
    const groups = manifest.value?.groups || {}
    const next = { ...selectedIds.value }
    next.characters = null

    const randomCategories = ACTIVE_CATEGORY_IDS.filter(
      (categoryId) => !['overall', 'underUpper', 'underLower'].includes(categoryId),
    )
    for (const categoryId of randomCategories) {
      const items = groups[categoryId] || []
      if (!items.length) continue
      next[categoryId] = items[Math.floor(Math.random() * items.length)].id
    }

    selectedIds.value = next
  }

  function save() {
    localStorage.setItem(AVATAR_STORAGE_KEY, JSON.stringify({
      selections: selectedIds.value,
      colorOverrides: colorOverrides.value,
    }))
    savedAt.value = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  watch(
    manifest,
    (value) => {
      if (value) restore()
    },
    { immediate: true },
  )

  return {
    selectedIds,
    selectedItems,
    selectedPreset,
    visibleItems,
    savedAt,
    selectItem,
    setEyeColor,
    applyPreset,
    reset,
    randomize,
    save,
    restore,
  }
}

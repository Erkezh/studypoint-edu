import { computed, onMounted, ref } from 'vue'
import { loadAvatarManifest } from '@/services/avatarAssetService'
import { ACTIVE_CATEGORY_IDS, CATEGORY_DEFINITIONS, CHARACTER_PRESET_CATEGORY } from '@/data/avatarDefaults'

export function useAvatarAssets() {
  const loading = ref(false)
  const error = ref('')
  const manifest = ref(null)

  const categories = computed(() => {
    const groups = manifest.value?.groups || {}
    return Object.values(CATEGORY_DEFINITIONS)
      .filter((category) => groups[category.id]?.length)
      .map((category) => ({
        ...category,
        count: groups[category.id].length,
        active: ACTIVE_CATEGORY_IDS.includes(category.id),
      }))
  })

  const activeCategories = computed(() => {
    const assetCategories = ACTIVE_CATEGORY_IDS.map((id) => categories.value.find((category) => category.id === id)).filter(Boolean)
    const presetCount = manifest.value?.groups?.characters?.length || 0
    return presetCount
      ? [{ ...CHARACTER_PRESET_CATEGORY, count: presetCount, active: true }, ...assetCategories]
      : assetCategories
  })

  async function load() {
    loading.value = true
    error.value = ''
    try {
      manifest.value = await loadAvatarManifest()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Кейіпкер ресурстарын жүктеу мүмкін болмады.'
    } finally {
      loading.value = false
    }
  }

  onMounted(load)

  return {
    loading,
    error,
    manifest,
    categories,
    activeCategories,
    reload: load,
  }
}

<template>
  <div class="avatar-page">
    <Header />

    <aside v-if="trial.isTrial" class="trial-toolbar">
      <div><strong>Сынақ режимі: Кейіпкер әлемі</strong><span>Кейіпкерді еркін өзгертіп көр. Таңдау әзірге бекітілмейді.</span></div>
      <button type="button" class="trial-toolbar__secondary" @click="trial.tryOtherGame">Көлікті де байқап көру</button>
      <button type="button" class="trial-toolbar__primary" :disabled="!trial.hasTriedBoth || trial.isChoosing" @click="trial.chooseGame">
        {{ trial.hasTriedBoth ? (trial.isChoosing ? 'Таңдалуда…' : 'Осы ойынды таңдау') : 'Алдымен екі ойынды да байқап көр' }}
      </button>
      <button type="button" class="trial-toolbar__close" aria-label="Ойын таңдау бетіне қайту" @click="trial.backToSelection">×</button>
    </aside>

    <main class="avatar-page__main">
      <GamificationBar class="avatar-page__progress" />

      <div v-if="assetsError" class="avatar-page__notice">
        <strong>Ресурстарды жүктеу қатесі</strong>
        <p>{{ assetsError }}</p>
        <button type="button" @click="reload">Қайталау</button>
      </div>

      <div v-else class="avatar-page__workspace">
        <AvatarViewer
          :selected-items="selectedItems"
          :preset-shapes="selectedPreset"
        />

        <AvatarCustomizer
          v-if="manifest"
          :categories="visibleCategories"
          :groups="progressionGroups"
          :selected-ids="selectedIds"
          :selected-items="selectedItems"
          :saved-at="savedAt"
          :player-level="gamification.level"
          :coins="gamification.coins"
          @select="handleSelect"
          @buy="buyItem"
          @eye-color="setEyeColor"
          @reset="reset"
          @randomize="randomize"
          @save="saveAvatar"
        />

        <section v-else class="avatar-page__panel-loading">
          <strong>BoZo ресурстары жүктелуде</strong>
          <span>{{ assetsLoading ? 'Кейіпкер деректері оқылуда' : 'Дайындалуда' }}</span>
        </section>
      </div>

    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import { computed, ref } from 'vue'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import GamificationBar from '@/components/gamification/GamificationBar.vue'
import AvatarViewer from '@/components/avatar/AvatarViewer.vue'
import AvatarCustomizer from '@/components/avatar/AvatarCustomizer.vue'
import { useAvatarAssets } from '@/composables/useAvatarAssets'
import { useAvatarState } from '@/composables/useAvatarState'
import { useGameTrial } from '@/composables/useGameTrial'
import { useGamificationStore } from '@/stores/gamification'
import { gameShopApi } from '@/api/gameShop'
import { avatarItemProgression } from '@/utils/avatarProgression'

defineOptions({ name: 'AvatarDemo' })

const trial = useGameTrial('character')
const gamification = useGamificationStore()
const ownedItemIds = ref(new Set())
const {
  loading: assetsLoading,
  error: assetsError,
  manifest,
  activeCategories,
  reload,
} = useAvatarAssets()
const visibleCategories = computed(() =>
  activeCategories.value.filter((category) => !['head', 'body'].includes(category.id)),
)
const progressionGroups = computed(() => Object.fromEntries(
  Object.entries(manifest.value?.groups || {}).map(([category, items]) => [category, items.map((item) => {
    const progression = avatarItemProgression(item)
    const owned = progression.isFree || ownedItemIds.value.has(item.id)
    return {
      ...item,
      ...progression,
      owned,
      locked: !owned && gamification.level < progression.requiredLevel,
    }
  })]),
))
const {
  selectedIds,
  selectedItems,
  selectedPreset,
  savedAt,
  selectItem,
  applyPreset,
  setEyeColor,
  reset,
  randomize,
  save,
} = useAvatarState(manifest)

function handleSelect(categoryId, itemId) {
  if (categoryId === 'characters') applyPreset(itemId)
  else selectItem(categoryId, itemId)
}

async function loadEconomy() {
  await gamification.fetchGamification()
  const response = await gameShopApi.inventory()
  ownedItemIds.value = new Set(response.data.data?.character_inventory || [])
}

async function buyItem(item) {
  if (trial.isTrial || item.locked || item.owned) return
  await gameShopApi.buyCharacterAsset(item)
  await loadEconomy()
}

function saveAvatar() {
  const unowned = Object.values(selectedIds.value).find((id) => {
    if (!id) return false
    const item = Object.values(progressionGroups.value).flat().find((candidate) => candidate.id === id)
    return item && !item.owned
  })
  if (unowned) {
    window.alert('Кейіпкерді сақтау үшін таңдалған заттарды сатып алу керек.')
    return
  }
  save()
}

void loadEconomy().catch(() => {
  // Avatar preview remains available if the wallet endpoint is temporarily unavailable.
})

</script>

<style scoped>
.avatar-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 9% 18%, rgb(36 210 190 / 18%), transparent 31rem),
    radial-gradient(circle at 88% 12%, rgb(100 92 255 / 16%), transparent 34rem),
    linear-gradient(145deg, #f8fbff 0%, #f2f6ff 48%, #fff9ee 100%);
  background-attachment: fixed;
}

.trial-toolbar { position: fixed; z-index: 900; top: 78px; left: 50%; display: flex; width: min(1050px, calc(100% - 24px)); align-items: center; gap: 12px; padding: 12px 54px 12px 18px; transform: translateX(-50%); border: 1px solid rgb(255 255 255 / 32%); border-radius: 18px; background: rgb(30 32 67 / 94%); color: white; box-shadow: 0 14px 38px rgb(0 0 0 / 28%); backdrop-filter: blur(12px); }
.trial-toolbar div { margin-right: auto; }.trial-toolbar strong,.trial-toolbar span { display: block; }.trial-toolbar strong { font-size: 14px; }.trial-toolbar span { margin-top: 2px; color: #ded2ff; font-size: 11px; }.trial-toolbar button { border: 0; border-radius: 11px; padding: 11px 15px; color: white; font-weight: 900; cursor: pointer; }.trial-toolbar__secondary { background: #38546a; }.trial-toolbar__primary { background: linear-gradient(90deg, #7040d3, #9557e3); }.trial-toolbar__primary:disabled { opacity: .52; cursor: not-allowed; }.trial-toolbar .trial-toolbar__close { position: absolute; right: 10px; width: 34px; padding: 6px; background: rgb(255 255 255 / 12%); font-size: 21px; }
@media (max-width: 760px) { .trial-toolbar { top: 66px; flex-wrap: wrap; padding: 10px 46px 10px 12px; }.trial-toolbar div { width: 100%; }.trial-toolbar button { flex: 1; font-size: 11px; } }

.avatar-page__main {
  width: min(1540px, calc(100% - 2rem));
  margin: 0 auto;
  padding: 1rem 0 2rem;
}

.avatar-page__progress {
  margin-bottom: 0.75rem;
}

.avatar-page__workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.38fr) minmax(28rem, 0.82fr);
  gap: 1.25rem;
  align-items: start;
  min-width: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  padding: 0;
  box-shadow: none;
}

.avatar-page__workspace > * {
  min-width: 0;
  max-width: 100%;
}

.avatar-page__panel-loading,
.avatar-page__notice {
  border: 1px solid #dfeadc;
  border-radius: 24px;
  background: white;
  padding: 1.2rem;
  box-shadow: 0 18px 48px rgb(24 48 32 / 8%);
}

.avatar-page__panel-loading {
  display: grid;
  place-items: center;
  text-align: center;
  color: #315238;
  font-weight: 800;
}

.avatar-page__panel-loading strong {
  color: #13231b;
  font-size: 1.1rem;
}

.avatar-page__notice {
  display: grid;
  gap: 0.5rem;
}

.avatar-page__notice strong {
  color: #9b1c1c;
}

.avatar-page__notice p {
  margin: 0;
  color: #5f7462;
  font-weight: 700;
}

.avatar-page__notice button {
  justify-self: start;
  min-height: 2.4rem;
  border: 0;
  border-radius: 999px;
  background: #38b000;
  color: #fff;
  padding: 0 1rem;
  font-weight: 900;
}

@media (max-width: 1020px) {
  .avatar-page__workspace {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .avatar-page__main {
    width: min(100% - 1rem, 1440px);
    padding-top: 1rem;
  }
}
</style>

<template>
  <main class="garage-page" :class="{ 'garage-page--finished': garage.isFinished }">
    <GarageScene
      :body="garage.bodyPart"
      :body-options="garage.parts.body"
      :wheel="garage.wheelPart"
      :paint-color="garage.paintColor"
      :rim-color="garage.rimColor"
      :window-color="showWindowCategory ? garage.windowTint?.value : undefined"
      :window-opacity="showWindowCategory ? garage.windowTint?.opacity : undefined"
      :sticker-color="garage.stickerColor"
      :locked-preview="isActiveVehicleLocked"
      :finished="garage.isFinished"
    />

    <div class="garage-vignette"></div>

    <header class="garage-topbar" v-if="!garage.isFinished">
      <section class="garage-statsbar">
        <div class="garage-statsbar__level">
          <img class="garage-statsbar__icon" src="/assets/level-star.svg" alt="" aria-hidden="true" />
          <strong>{{ displayLevel }}-деңгей</strong>
        </div>
        <div class="garage-statsbar__xp">
          <div class="garage-statsbar__label">
            <span>XP</span>
            <strong>{{ displayXp.toLocaleString() }} / {{ displayNextLevelXp.toLocaleString() }}</strong>
          </div>
          <div class="garage-statsbar__track">
            <i :style="{ width: `${displayXpProgress}%` }"></i>
          </div>
        </div>
        <div class="garage-statsbar__stat">
          <img class="garage-statsbar__icon" src="/assets/coin-icon.svg" alt="" aria-hidden="true" />
          <div>
            <small>Coins</small>
            <strong>{{ displayCoins.toLocaleString() }}</strong>
          </div>
        </div>
        <div class="garage-statsbar__stat">
          <img
            class="garage-statsbar__icon garage-statsbar__icon--streak"
            src="/assets/streak-fire-character.png"
            alt=""
            aria-hidden="true"
          />
          <div>
            <small>Streak</small>
            <strong>{{ displayDailyStreak }}</strong>
          </div>
        </div>
      </section>
    </header>

    <aside class="garage-left" v-if="!garage.isFinished">
      <button
        v-for="category in visibleCategories"
        :key="category.id"
        type="button"
        class="category-button"
        :class="{
          'category-button--active': garage.activeCategory === category.id,
          'category-button--disabled': customizationDisabled && category.id !== 'body',
        }"
        :disabled="customizationDisabled && category.id !== 'body'"
        @click="selectCategory(category.id)"
      >
        <span>
          <img v-if="category.icon.startsWith('/')" :src="category.icon" alt="" aria-hidden="true" />
          <template v-else>{{ category.icon }}</template>
        </span>
        <strong>{{ category.label }}</strong>
      </button>
      <div class="garage-motivation">
        <strong>Жақсы жұмыс!</strong>
        <p>Көбірек есеп шешіп, жаңа монеталар жинап, керемет көліктерді аш.</p>
        <router-link to="/topics">Есептерге өту</router-link>
      </div>
    </aside>

    <aside class="garage-right" v-if="!garage.isFinished">
      <span class="panel-kicker">Баптау орны</span>
      <h2>{{ garage.activeMeta?.label }}</h2>
      <p>{{ panelCopy }}</p>

      <ColorPicker
        v-if="garage.activeMeta?.control === 'paint'"
        :options="garage.activeOptions"
        :value="garage.selection.paint"
        :disabled="customizationDisabled"
        @select="garage.selectOption"
      />
      <ColorPicker
        v-else-if="garage.activeMeta?.control === 'rims'"
        :options="garage.activeOptions"
        :value="garage.selection.rimColor"
        :disabled="customizationDisabled"
        @select="garage.selectOption"
      />
      <ColorPicker
        v-else-if="garage.activeMeta?.control === 'stickerColor'"
        :options="garage.activeOptions"
        :value="garage.selection.stickerColor"
        :disabled="customizationDisabled"
        @select="garage.selectOption"
      />

      <div v-if="customizationDisabled && garage.activeCategory !== 'body'" class="vehicle-purchase vehicle-purchase--locked">
        <strong>Алдымен көлікті сатып ал</strong>
        <small>Осы көліктің бояуын және бөлшектерін сатып алғаннан кейін ғана өзгерте аласың.</small>
      </div>

      <div v-if="garage.activeCategory === 'body' && activeVehicle" class="vehicle-purchase">
        <div>
          <strong>{{ vehicleStatusLabel }}</strong>
          <small v-if="!activeVehicle.is_owned">
            {{ vehiclePriceLabel }}
            · {{ vehicleUnlockLabel }}
          </small>
        </div>
        <button
          v-if="!activeVehicle.is_owned"
          type="button"
          class="done-button"
          :disabled="!activeVehicle.is_unlocked || gamification.isSaving"
          @click="buyActiveVehicle"
        >
          {{ activeVehicle.is_unlocked ? 'Сатып алу' : 'Жабық' }}
        </button>
        <button
          v-else
          type="button"
          class="done-button"
          :disabled="activeVehicle.is_selected || gamification.isSaving"
          @click="selectActiveVehicle"
        >
          {{ activeVehicle.is_selected ? 'Таңдалған' : 'Таңдау' }}
        </button>
      </div>

      <div v-if="statusMessage" class="vehicle-status-message" :class="{ 'vehicle-status-message--error': statusIsError }">
        {{ statusMessage }}
      </div>

      <div class="garage-actions">
        <button class="random-button" type="button" @click="randomize">Кездейсоқ көлік</button>
        <button class="reset-button" type="button" @click="garage.reset">Қалпына келтіру</button>
      </div>
      <button class="done-button" type="button" :disabled="garage.isSaving || isActiveVehicleLocked" @click="finish">
        {{ garage.isSaving ? 'Сақталуда...' : isActiveVehicleLocked ? 'Алдымен ашу керек' : 'Дайын' }}
      </button>
    </aside>

    <CustomizationPanel
      v-if="!garage.isFinished"
      :title="garage.activeMeta?.label ?? 'Бөлшектер'"
      :options="garage.activeOptions"
      :selection="garage.selection"
      :player-level="displayLevel"
      :control="garage.activeMeta?.control"
      :locked-ids="lockedOptionIds"
      :locked-labels="lockedOptionLabels"
      :allow-locked-preview="garage.activeCategory === 'body'"
      :disabled="customizationDisabled && garage.activeCategory !== 'body'"
      @select="garage.selectOption"
    />

    <FinishScreen v-if="garage.isFinished" @customize="garage.isFinished = false" />
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import confetti from 'canvas-confetti'
import GarageScene from './GarageScene.vue'
import CustomizationPanel from './CustomizationPanel.vue'
import ColorPicker from './ColorPicker.vue'
import FinishScreen from './FinishScreen.vue'
import { useGarageStore } from '@/stores/garage'
import { useGamificationStore } from '@/stores/gamification'
import type { GarageCategoryId } from '@/config/garage'

const garage = useGarageStore()
const gamification = useGamificationStore()
const statusMessage = ref('')
const statusIsError = ref(false)
const noWindowVehicleIds = new Set([
  'skateboard',
  'e2f-scooter-yellow',
  'btwin-triban-100-bike',
  'vino',
  'free-concept-sport-bike',
  'ducati-streetfighter-v4-s',
  'suzuki-quadzilla-500',
])

onMounted(() => {
  garage.load()
  gamification.fetchGamification().catch(() => {
    // Garage still works in preview mode without auth.
  })
})

const displayLevel = computed(() => gamification.level || garage.player.level)
const displayCoins = computed(() => gamification.coins || garage.player.coins)
const displayXp = computed(() => gamification.xp || Math.round((garage.player.xp / 100) * 500))
const displayNextLevelXp = computed(() => gamification.nextLevelXp || 500)
const displayXpProgress = computed(() => gamification.xpProgress || garage.player.xp)
const displayDailyStreak = computed(() => gamification.dailyStreak || 1)
const activeVehicle = computed(() => gamification.vehicles.find((vehicle) => vehicle.id === garage.selection.body))
const showWindowCategory = computed(() => !noWindowVehicleIds.has(garage.selection.body))
const visibleCategories = computed(() => {
  if (showWindowCategory.value) return garage.categories
  return garage.categories.filter((category) => category.id !== 'windows')
})
const activeVehiclePrice = computed(() => activeVehicle.value?.price ?? activeVehicle.value?.coin_price ?? 0)
const activeVehicleLevel = computed(() => activeVehicle.value?.level_required ?? activeVehicle.value?.unlock_level ?? 1)
const activeVehicleXp = computed(() => activeVehicle.value?.xp_required ?? activeVehicle.value?.unlock_xp ?? 0)
const isActiveVehicleLocked = computed(() => Boolean(activeVehicle.value && !activeVehicle.value.is_unlocked))
const customizationDisabled = computed(() => Boolean(activeVehicle.value && !activeVehicle.value.is_owned))
const lockedOptionIds = computed(() => {
  if (garage.activeCategory !== 'body') return []
  return gamification.vehicles.filter((vehicle) => !vehicle.is_unlocked).map((vehicle) => vehicle.id)
})
const lockedOptionLabels = computed(() => {
  if (garage.activeCategory !== 'body') return {}
  return Object.fromEntries(
    gamification.vehicles
      .filter((vehicle) => !vehicle.is_unlocked)
      .map((vehicle) => [vehicle.id, `${vehicle.name} ашу үшін ${vehicle.level_required ?? vehicle.unlock_level}-деңгейге жет`])
  )
})
const vehiclePriceLabel = computed(() => `${activeVehiclePrice.value.toLocaleString()} монета`)
const vehicleUnlockLabel = computed(() => `${activeVehicleLevel.value}-деңгей · ${activeVehicleXp.value.toLocaleString()} XP`)
const vehicleStatusLabel = computed(() => {
  if (!activeVehicle.value) return ''
  if (activeVehicle.value.is_selected) return 'Қазір таңдалған көлік'
  if (activeVehicle.value.is_owned) return 'Сатып алынған'
  if (!activeVehicle.value.is_unlocked) return `${activeVehicle.value.name} ашу үшін ${activeVehicleLevel.value}-деңгейге жет`
  if (gamification.coins < activeVehiclePrice.value) return `Тағы ${(activeVehiclePrice.value - gamification.coins).toLocaleString()} монета керек`
  return 'Ашылды, сатып алуға болады'
})

const panelCopy = computed(() => {
  if (customizationDisabled.value && garage.activeMeta?.id !== 'body') return 'Бұл көлікті сатып алғаннан кейін ғана бөлшектерін өзгерте аласың.'
  if (garage.activeMeta?.control === 'paint') return 'Көлігіңе ұнайтын жылтыр түсті таңда.'
  if (garage.activeMeta?.control === 'stickerColor') return 'Тек стикердің түсін өзгерт.'
  return 'Бөлшектерді бірден ауыстыр. Жабық сыйлықтар деңгей өскен сайын ашылады.'
})

watch(
  () => garage.selection.body,
  () => {
    if (!showWindowCategory.value && garage.activeCategory === 'windows') {
      garage.selectCategory('paint')
    }
  }
)

const blip = (frequency = 320, duration = 0.06) => {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext
  if (!AudioContextClass) return
  const context = new AudioContextClass()
  const oscillator = context.createOscillator()
  const gain = context.createGain()
  oscillator.frequency.value = frequency
  oscillator.type = 'sine'
  gain.gain.value = 0.025
  oscillator.connect(gain)
  gain.connect(context.destination)
  oscillator.start()
  oscillator.stop(context.currentTime + duration)
}

const selectCategory = (category: GarageCategoryId) => {
  if (customizationDisabled.value && category !== 'body') return
  blip(280)
  garage.selectCategory(category)
}

const randomize = async () => {
  blip(520, 0.09)
  await garage.randomize()
}

const finish = async () => {
  blip(660, 0.12)
  await garage.finish()
  confetti({ particleCount: 120, spread: 72, origin: { y: 0.72 }, scalar: 0.9 })
}

const buyActiveVehicle = async () => {
  if (!activeVehicle.value) return
  statusMessage.value = ''
  statusIsError.value = false
  if (!activeVehicle.value.is_unlocked) {
    statusMessage.value = `${activeVehicle.value.name} ашу үшін ${activeVehicleLevel.value}-деңгейге жет`
    statusIsError.value = true
    return
  }
  if (gamification.coins < activeVehiclePrice.value) {
    statusMessage.value = `Тағы ${(activeVehiclePrice.value - gamification.coins).toLocaleString()} монета керек`
    statusIsError.value = true
    return
  }
  blip(560, 0.1)
  try {
    await gamification.buyVehicle(activeVehicle.value.id)
    statusMessage.value = 'Сәтті сатып алынды'
  } catch (error: unknown) {
    statusIsError.value = true
    statusMessage.value = (error as { message?: string }).message || 'Сатып алу сәтсіз аяқталды'
  }
}

const selectActiveVehicle = async () => {
  if (!activeVehicle.value) return
  statusMessage.value = ''
  statusIsError.value = false
  blip(440, 0.08)
  try {
    await gamification.selectVehicle(activeVehicle.value.id)
    statusMessage.value = 'Көлік таңдалды'
  } catch (error: unknown) {
    statusIsError.value = true
    statusMessage.value = (error as { message?: string }).message || 'Таңдау сәтсіз аяқталды'
  }
}
</script>

<style scoped>
.vehicle-status-message {
  margin-top: 0.75rem;
  border: 1px solid rgba(34, 197, 94, 0.35);
  border-radius: 8px;
  background: rgba(240, 253, 244, 0.92);
  color: #166534;
  font-weight: 700;
  padding: 0.75rem 0.9rem;
}

.vehicle-status-message--error {
  border-color: rgba(248, 113, 113, 0.45);
  background: rgba(254, 242, 242, 0.94);
  color: #991b1b;
}
</style>

<template>
  <main class="garage-page" :class="{ 'garage-page--finished': garage.isFinished }">
    <GarageScene
      :body="garage.bodyPart"
      :body-options="garage.parts.body"
      :wheel="garage.wheelPart"
      :paint-color="garage.paintColor"
      :rim-color="garage.rimColor"
      :window-color="garage.windowTint?.value"
      :window-opacity="garage.windowTint?.opacity"
      :sticker-color="garage.stickerColor"
      :locked-preview="isActiveVehicleLocked"
      :finished="garage.isFinished"
    />

    <div class="garage-vignette"></div>

    <header class="garage-topbar" v-if="!garage.isFinished">
      <section class="garage-statsbar">
        <div class="garage-statsbar__level">
          <span>★</span>
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
        <div class="garage-statsbar__stat"><span>●</span><strong>{{ displayCoins.toLocaleString() }}</strong></div>
        <div class="garage-statsbar__stat"><span>🔥</span><strong>{{ displayDailyStreak }}</strong></div>
        <div class="garage-statsbar__stat"><span>⚡</span><strong>{{ displayComboStreak }}</strong></div>
      </section>
    </header>

    <aside class="garage-left" v-if="!garage.isFinished">
      <button
        v-for="category in garage.categories"
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
        <span>{{ category.icon }}</span>
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
            {{ activeVehicle.coin_price ? `${activeVehicle.coin_price.toLocaleString()} монета` : 'Тегін' }}
            · {{ activeVehicle.unlock_level }}-деңгей
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
import { computed, onMounted } from 'vue'
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
const displayComboStreak = computed(() => gamification.comboStreak || 9)
const activeVehicle = computed(() => gamification.vehicles.find((vehicle) => vehicle.id === garage.selection.body))
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
      .map((vehicle) => [vehicle.id, `${vehicle.unlock_xp.toLocaleString()} XP керек`])
  )
})
const vehicleStatusLabel = computed(() => {
  if (!activeVehicle.value) return ''
  if (activeVehicle.value.is_selected) return 'Қазір таңдалған көлік'
  if (activeVehicle.value.is_owned) return 'Сатып алынған'
  if (activeVehicle.value.is_unlocked) return 'Ашылды, сатып алуға болады'
  return `${activeVehicle.value.unlock_xp.toLocaleString()} XP керек`
})

const panelCopy = computed(() => {
  if (customizationDisabled.value && garage.activeMeta?.id !== 'body') return 'Бұл көлікті сатып алғаннан кейін ғана бөлшектерін өзгерте аласың.'
  if (garage.activeMeta?.control === 'paint') return 'Көлігіңе ұнайтын жылтыр түсті таңда.'
  if (garage.activeMeta?.control === 'stickerColor') return 'Тек стикердің түсін өзгерт.'
  return 'Бөлшектерді бірден ауыстыр. Жабық сыйлықтар деңгей өскен сайын ашылады.'
})

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
  blip(560, 0.1)
  await gamification.buyVehicle(activeVehicle.value.id)
}

const selectActiveVehicle = async () => {
  if (!activeVehicle.value) return
  blip(440, 0.08)
  await gamification.selectVehicle(activeVehicle.value.id)
}
</script>

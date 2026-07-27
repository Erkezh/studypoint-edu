<template>
  <Teleport to="body">
    <div v-if="show && reward" :key="animationKey" class="reward-burst" aria-live="polite">
      <div v-if="hasCoins" class="reward-burst__stage">
        <span class="reward-burst__glow"></span>
        <span class="reward-burst__wallet-ping">
          <img src="/assets/coin-icon.svg" alt="" aria-hidden="true" />
        </span>

        <span
          v-for="coin in coins"
          :key="coin"
          class="reward-burst__coin"
          :style="coinStyle(coin)"
        >
          <img src="/assets/coin-icon.svg" alt="" aria-hidden="true" />
        </span>

        <span
          v-for="sparkle in sparkles"
          :key="sparkle"
          class="reward-burst__sparkle"
          :style="sparkleStyle(sparkle)"
        ></span>
      </div>

      <div class="reward-burst__summary" :class="{ 'reward-burst__summary--coins': hasCoins }">
        <strong v-if="reward.coins_gained">+{{ reward.coins_gained }}</strong>
        <strong v-else>+{{ reward.xp_gained }}</strong>
        <span>{{ reward.coins_gained ? 'монета' : 'XP' }}</span>
        <i v-if="reward.xp_gained && reward.coins_gained">+{{ reward.xp_gained }} XP</i>
        <i v-if="reward.milestone_rewards?.length">SmartScore milestone</i>
        <i v-if="reward.level_bonus">Level reward +{{ reward.level_bonus }}</i>
        <i v-if="reward.streak_bonus">7-day streak +{{ reward.streak_bonus }}</i>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, watch } from 'vue'
import type { GamificationReward } from '@/types/api'

const props = defineProps<{
  show: boolean
  reward?: GamificationReward | null
}>()

const emit = defineEmits<{
  close: []
}>()

let closeTimer: number | undefined
let soundContext: AudioContext | undefined
const soundTimers: number[] = []

const hasCoins = computed(() => (props.reward?.coins_gained ?? 0) > 0)

const animationKey = computed(() => {
  const reward = props.reward
  if (!reward) return 'empty'
  return `${reward.coins_gained}-${reward.xp_gained}-${reward.new_level}-${reward.daily_streak}`
})

const coins = computed(() => {
  const amount = props.reward?.coins_gained ?? 0
  if (amount <= 0) return []
  return Array.from({ length: Math.min(24, Math.max(1, amount)) }, (_, index) => index)
})

const sparkles = computed(() => {
  if (!hasCoins.value) return []
  return Array.from({ length: 12 }, (_, index) => index)
})

const coinStyle = (index: number) => {
  const startX = -104 + (index % 6) * 42
  const startY = 82 + Math.floor(index / 6) * 12
  const popX = startX * 0.52
  const popY = -118 - (index % 4) * 20
  const hoverX = -38 + (index % 5) * 19
  const hoverY = -82 - (index % 3) * 14
  const targetX = 43 + (index % 4) * 1.8
  const targetY = -45 - (index % 3) * 2.5
  const size = 42 + (index % 3) * 5

  return {
    '--delay': `${0.05 + index * 0.085}s`,
    '--start-x': `${startX}px`,
    '--start-y': `${startY}px`,
    '--pop-x': `${popX}px`,
    '--pop-y': `${popY}px`,
    '--hover-x': `${hoverX}px`,
    '--hover-y': `${hoverY}px`,
    '--target-x': `${targetX}vw`,
    '--target-y': `${targetY}vh`,
    '--near-target-x': `${(targetX * 0.78).toFixed(1)}vw`,
    '--near-target-y': `${(targetY * 0.82).toFixed(1)}vh`,
    '--size': `${size}px`,
    '--spin': `${520 + index * 62}deg`,
    '--tilt': `${index % 2 === 0 ? '-' : ''}${8 + (index % 5) * 5}deg`,
    '--hover-tilt': `${index % 2 === 0 ? '' : '-'}${8 + (index % 5) * 5}deg`,
  }
}

const sparkleStyle = (index: number) => {
  const angle = index * 31
  const distance = 62 + (index % 4) * 34
  const radians = (angle * Math.PI) / 180

  return {
    '--delay': `${0.08 + index * 0.07}s`,
    '--x': `${(Math.cos(radians) * distance).toFixed(1)}px`,
    '--y': `${(Math.sin(radians) * distance).toFixed(1)}px`,
  }
}

const stopCoinSounds = () => {
  while (soundTimers.length) {
    const timer = soundTimers.pop()
    if (timer) window.clearTimeout(timer)
  }
}

const playCoinSound = (index: number) => {
  const AudioContextCtor = window.AudioContext || (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
  if (!AudioContextCtor) return
  soundContext ??= new AudioContextCtor()
  if (soundContext.state === 'suspended') {
    soundContext.resume().catch(() => {})
  }

  const startAt = soundContext.currentTime
  const output = soundContext.createGain()
  output.gain.setValueAtTime(0.7, startAt)
  output.connect(soundContext.destination)

  const click = soundContext.createBufferSource()
  const clickBuffer = soundContext.createBuffer(1, Math.max(1, Math.floor(soundContext.sampleRate * 0.035)), soundContext.sampleRate)
  const clickData = clickBuffer.getChannelData(0)
  for (let i = 0; i < clickData.length; i += 1) {
    const t = i / clickData.length
    clickData[i] = (Math.random() * 2 - 1) * (1 - t) * 0.45
  }
  const clickFilter = soundContext.createBiquadFilter()
  const clickGain = soundContext.createGain()
  click.buffer = clickBuffer
  clickFilter.type = 'bandpass'
  clickFilter.frequency.setValueAtTime(3200, startAt)
  clickFilter.Q.setValueAtTime(5, startAt)
  clickGain.gain.setValueAtTime(0.0001, startAt)
  clickGain.gain.linearRampToValueAtTime(0.1, startAt + 0.004)
  clickGain.gain.exponentialRampToValueAtTime(0.0001, startAt + 0.045)
  click.connect(clickFilter)
  clickFilter.connect(clickGain)
  clickGain.connect(output)

  const pluck = soundContext.createOscillator()
  const pluckGain = soundContext.createGain()
  const pluckFilter = soundContext.createBiquadFilter()
  const base = 1040 + (index % 6) * 45
  pluck.type = 'triangle'
  pluck.frequency.setValueAtTime(base, startAt)
  pluck.frequency.exponentialRampToValueAtTime(base * 1.42, startAt + 0.07)
  pluckFilter.type = 'lowpass'
  pluckFilter.frequency.setValueAtTime(5200, startAt)
  pluckGain.gain.setValueAtTime(0.0001, startAt)
  pluckGain.gain.linearRampToValueAtTime(0.16, startAt + 0.012)
  pluckGain.gain.exponentialRampToValueAtTime(0.0001, startAt + 0.18)
  pluck.connect(pluckFilter)
  pluckFilter.connect(pluckGain)
  pluckGain.connect(output)

  const chime = soundContext.createOscillator()
  const chimeGain = soundContext.createGain()
  chime.type = 'sine'
  chime.frequency.setValueAtTime(base * 2.05, startAt + 0.035)
  chime.frequency.exponentialRampToValueAtTime(base * 2.45, startAt + 0.13)
  chimeGain.gain.setValueAtTime(0.0001, startAt)
  chimeGain.gain.linearRampToValueAtTime(0.08, startAt + 0.045)
  chimeGain.gain.exponentialRampToValueAtTime(0.0001, startAt + 0.23)
  chime.connect(chimeGain)
  chimeGain.connect(output)

  click.start(startAt)
  pluck.start(startAt)
  chime.start(startAt + 0.035)
  click.stop(startAt + 0.04)
  pluck.stop(startAt + 0.19)
  chime.stop(startAt + 0.24)
}

const playCoinSounds = () => {
  stopCoinSounds()
  coins.value.forEach((_, index) => {
    const timer = window.setTimeout(() => playCoinSound(index), 80 + index * 85)
    soundTimers.push(timer)
  })
}

watch(
  () => props.show,
  (visible) => {
    if (closeTimer) window.clearTimeout(closeTimer)
    stopCoinSounds()
    if (!visible) return
    if (hasCoins.value) playCoinSounds()
    const duration = hasCoins.value ? 1180 + coins.value.length * 85 : 1600
    closeTimer = window.setTimeout(() => emit('close'), Math.min(3800, duration))
  }
)

onBeforeUnmount(() => {
  if (closeTimer) window.clearTimeout(closeTimer)
  stopCoinSounds()
  soundContext?.close().catch(() => {})
})
</script>

<style scoped>
.reward-burst {
  position: fixed;
  inset: 0;
  z-index: 90;
  pointer-events: none;
  overflow: hidden;
}

.reward-burst__stage {
  position: absolute;
  left: 50%;
  top: 55%;
  width: 1px;
  height: 1px;
  transform: translate(-50%, -50%);
}

.reward-burst__glow {
  position: absolute;
  width: 240px;
  height: 240px;
  margin: -120px;
  border-radius: 999px;
  background:
    radial-gradient(circle, rgba(254, 240, 138, 0.42), rgba(251, 191, 36, 0.16) 42%, transparent 70%);
  animation: reward-glow 1.5s ease-out forwards;
}

.reward-burst__coin {
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: rgba(255, 214, 64, 0.18);
  border: 2px solid rgba(255, 240, 138, 0.88);
  box-shadow:
    0 16px 30px rgba(180, 83, 9, 0.32),
    0 0 18px rgba(250, 204, 21, 0.34),
    inset 0 -5px 0 rgba(146, 64, 14, 0.22);
}

.reward-burst__coin img,
.reward-burst__wallet-ping img {
  width: 82%;
  height: 82%;
  object-fit: contain;
  filter:
    drop-shadow(0 4px 2px rgba(146, 64, 14, 0.2))
    drop-shadow(0 0 7px rgba(255, 247, 173, 0.58));
}

.reward-burst__wallet-ping {
  position: absolute;
  right: -46.5vw;
  top: -45.5vh;
  display: grid;
  place-items: center;
  width: 62px;
  height: 62px;
  border-radius: 999px;
  background: rgba(250, 204, 21, 0.12);
  border: 2px solid rgba(255, 240, 138, 0.9);
  box-shadow:
    0 0 0 0 rgba(250, 204, 21, 0.38),
    0 0 28px rgba(250, 204, 21, 0.42),
    inset 0 -4px 0 rgba(146, 64, 14, 0.16);
  opacity: 0;
  animation: wallet-ping 2.7s ease forwards;
}

.reward-burst__coin {
  position: absolute;
  width: var(--size);
  height: var(--size);
  margin: calc(var(--size) / -2);
  opacity: 0;
  transform: translate(var(--start-x), var(--start-y)) scale(0.28) rotate(0deg) rotateY(0deg);
  animation: coin-flight 1.18s cubic-bezier(0.2, 0.78, 0.16, 1) forwards;
  animation-delay: var(--delay);
}

.reward-burst__sparkle {
  position: absolute;
  width: 9px;
  height: 9px;
  margin: -4px;
  border-radius: 999px;
  background: #fff7ad;
  box-shadow: 0 0 14px rgba(250, 204, 21, 0.82);
  opacity: 0;
  animation: reward-sparkle 1.2s ease-out forwards;
  animation-delay: var(--delay);
}

.reward-burst__summary {
  position: absolute;
  left: 50%;
  top: 55%;
  min-width: 160px;
  border: 1px solid rgba(250, 204, 21, 0.48);
  border-radius: 999px;
  padding: 13px 22px 14px;
  color: #fff7ed;
  background:
    radial-gradient(circle at top, rgba(254, 240, 138, 0.28), transparent 52%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.92));
  box-shadow:
    0 24px 56px rgba(15, 23, 42, 0.32),
    0 0 0 8px rgba(250, 204, 21, 0.08);
  text-align: center;
  transform: translate(-50%, -50%);
  animation: reward-pop 2.35s ease forwards;
}

.reward-burst__summary--coins {
  animation-name: coin-summary-pop;
}

.reward-burst__summary strong {
  display: block;
  font-size: 42px;
  line-height: 1;
  color: #facc15;
  text-shadow: 0 4px 0 rgba(146, 64, 14, 0.22);
}

.reward-burst__summary span,
.reward-burst__summary i {
  display: block;
  margin-top: 2px;
  color: #cbd5e1;
  font-size: 12px;
  font-style: normal;
  font-weight: 800;
}

.reward-burst__summary i {
  color: #67e8f9;
}

@keyframes coin-flight {
  0% {
    opacity: 0;
    transform: translate(var(--start-x), var(--start-y)) scale(0.28) rotate(-12deg) rotateY(0deg);
    filter: blur(1px);
  }
  14% {
    opacity: 1;
    transform: translate(var(--start-x), 34px) scale(1.28) rotate(var(--tilt)) rotateY(130deg);
    filter: blur(0);
  }
  32% {
    opacity: 1;
    transform: translate(var(--pop-x), var(--pop-y)) scale(1.02) rotate(var(--tilt)) rotateY(330deg);
  }
  52% {
    opacity: 1;
    transform: translate(var(--hover-x), var(--hover-y)) scale(0.96) rotate(var(--hover-tilt)) rotateY(470deg);
  }
  78% {
    opacity: 1;
    transform: translate(var(--near-target-x), var(--near-target-y)) scale(0.62) rotate(var(--spin)) rotateY(680deg);
  }
  100% {
    opacity: 0;
    transform: translate(var(--target-x), var(--target-y)) scale(0.18) rotate(var(--spin)) rotateY(920deg);
    filter: blur(1px);
  }
}

@keyframes wallet-ping {
  0% {
    opacity: 0;
    transform: scale(0.8);
    box-shadow:
      0 0 0 0 rgba(250, 204, 21, 0),
      inset 0 -4px 0 rgba(146, 64, 14, 0.28);
  }
  16%,
  84% {
    opacity: 1;
    transform: scale(1);
    box-shadow:
      0 0 0 13px rgba(250, 204, 21, 0.16),
      0 0 30px rgba(250, 204, 21, 0.46),
      inset 0 -4px 0 rgba(146, 64, 14, 0.16);
  }
  48% {
    opacity: 1;
    transform: scale(1.18);
    box-shadow:
      0 0 0 22px rgba(250, 204, 21, 0.1),
      0 0 42px rgba(250, 204, 21, 0.58),
      inset 0 -4px 0 rgba(146, 64, 14, 0.16);
  }
  100% {
    opacity: 0;
    transform: scale(1.16);
    box-shadow:
      0 0 0 24px rgba(250, 204, 21, 0),
      inset 0 -4px 0 rgba(146, 64, 14, 0.16);
  }
}

@keyframes reward-sparkle {
  0% {
    opacity: 0;
    transform: translate(0, 0) scale(0.2);
  }
  30% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translate(var(--x), var(--y)) scale(0);
  }
}

@keyframes reward-glow {
  0% {
    opacity: 0;
    transform: scale(0.45);
  }
  24%,
  64% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: scale(1.45);
  }
}

@keyframes reward-pop {
  0% {
    opacity: 0;
    transform: translate(-50%, calc(-50% + 14px)) scale(0.9);
  }
  15%,
  78% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, calc(-50% - 8px)) scale(0.96);
  }
}

@keyframes coin-summary-pop {
  0% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.64);
  }
  12% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.14);
  }
  22%,
  76% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -76%) scale(0.92);
  }
}

@media (max-width: 760px) {
  .reward-burst__stage,
  .reward-burst__summary {
    top: 58%;
  }

  .reward-burst__summary strong {
    font-size: 34px;
  }
}
</style>

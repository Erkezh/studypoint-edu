<template>
  <Teleport to="body">
    <div v-if="show && reward" class="reward-burst" aria-live="polite">
      <div class="reward-burst__trail">
        <span
          v-for="coin in coins"
          :key="coin"
          class="reward-burst__coin"
          :style="coinStyle(coin)"
        >
          ₸
        </span>
      </div>

      <div class="reward-burst__summary">
        <strong>+{{ reward.coins_gained }}</strong>
        <span>монета</span>
        <i v-if="reward.xp_gained">+{{ reward.xp_gained }} XP</i>
        <i v-if="reward.combo_bonus">Комбо +{{ reward.combo_bonus }}</i>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import type { GamificationReward } from '@/types/api'

const props = defineProps<{
  show: boolean
  reward?: GamificationReward | null
}>()

const emit = defineEmits<{
  close: []
}>()

const coins = computed(() => {
  const amount = props.reward?.coins_gained ?? 0
  return Array.from({ length: Math.min(14, Math.max(6, amount)) }, (_, index) => index)
})

const coinStyle = (index: number) => {
  const column = index % 5
  const row = Math.floor(index / 5)
  return {
    '--delay': `${index * 0.055}s`,
    '--x': `${(column - 2) * 36 + (row % 2) * 18}px`,
    '--y': `${-120 - row * 34}px`,
    '--spin': `${220 + index * 24}deg`,
  }
}

watch(
  () => props.show,
  (visible) => {
    if (!visible) return
    window.setTimeout(() => emit('close'), 1600)
  }
)
</script>

<style scoped>
.reward-burst {
  position: fixed;
  right: clamp(18px, 7vw, 120px);
  top: clamp(92px, 18vh, 190px);
  z-index: 90;
  width: 260px;
  height: 220px;
  pointer-events: none;
}

.reward-burst__trail {
  position: absolute;
  right: 84px;
  bottom: 42px;
  width: 1px;
  height: 1px;
}

.reward-burst__coin {
  position: absolute;
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  margin: -21px;
  border-radius: 999px;
  color: #fff8c7;
  font-size: 24px;
  font-weight: 950;
  background:
    radial-gradient(circle at 34% 28%, #fff8b8 0 12%, transparent 13%),
    radial-gradient(circle at 50% 50%, #ffd84d 0 48%, #f59e0b 49% 70%, #b45309 71% 100%);
  border: 3px solid #ffe681;
  box-shadow:
    0 8px 18px rgba(180, 83, 9, 0.28),
    inset 0 -4px 0 rgba(180, 83, 9, 0.28),
    inset 0 3px 0 rgba(255, 255, 255, 0.5);
  opacity: 0;
  transform: translate(0, 0) scale(0.72) rotate(0deg);
  animation: coin-flight 1.2s cubic-bezier(0.12, 0.82, 0.26, 1) forwards;
  animation-delay: var(--delay);
}

.reward-burst__summary {
  position: absolute;
  right: 0;
  bottom: 0;
  min-width: 178px;
  border: 1px solid rgba(250, 204, 21, 0.38);
  border-radius: 16px;
  padding: 12px 14px;
  color: #fff7ed;
  background:
    radial-gradient(circle at top right, rgba(250, 204, 21, 0.26), transparent 46%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.9));
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.28);
  animation: reward-pop 1.45s ease forwards;
}

.reward-burst__summary strong {
  display: block;
  font-size: 30px;
  line-height: 1;
  color: #facc15;
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
    transform: translate(0, 0) scale(0.5) rotate(0deg);
    filter: blur(2px);
  }
  14% {
    opacity: 1;
    filter: blur(0);
  }
  72% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translate(var(--x), var(--y)) scale(1.05) rotate(var(--spin));
    filter: blur(0.8px);
  }
}

@keyframes reward-pop {
  0% {
    opacity: 0;
    transform: translateY(14px) scale(0.9);
  }
  15%,
  78% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-8px) scale(0.96);
  }
}

@media (max-width: 760px) {
  .reward-burst {
    right: 14px;
    top: 78px;
    transform: scale(0.88);
    transform-origin: top right;
  }
}
</style>

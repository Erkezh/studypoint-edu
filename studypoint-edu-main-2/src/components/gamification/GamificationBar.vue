<template>
  <section class="gamification-bar">
    <div class="gamification-bar__level">
      <img class="gamification-bar__icon" src="/assets/level-star.svg" alt="" aria-hidden="true" />
      <strong>{{ store.level }}-деңгей</strong>
    </div>

    <div class="gamification-bar__xp">
      <div class="gamification-bar__label">
        <span>XP</span>
        <strong>{{ store.xp }} / {{ store.nextLevelXp }}</strong>
      </div>
      <div class="gamification-bar__track">
        <i :style="{ width: `${store.xpProgress}%` }"></i>
      </div>
    </div>

    <div class="gamification-bar__stat">
      <img class="gamification-bar__icon" src="/assets/coin-icon.svg" alt="" aria-hidden="true" />
      <div>
        <small>Монета</small>
        <strong>{{ store.coins.toLocaleString() }}</strong>
      </div>
    </div>
    <div class="gamification-bar__stat">
      <img
        class="gamification-bar__icon gamification-bar__icon--streak"
        src="/assets/streak-fire-character.png"
        alt=""
        aria-hidden="true"
      />
      <div>
        <small>Серия</small>
        <strong>{{ store.dailyStreak }}</strong>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useGamificationStore } from '@/stores/gamification'

const store = useGamificationStore()

onMounted(() => {
  store.fetchGamification().catch(() => {
    // Guest practice can still work without a gamification profile.
  })
})
</script>

<style scoped>
.gamification-bar {
  display: grid;
  grid-template-columns: auto minmax(180px, 1fr) auto auto;
  gap: 12px;
  align-items: center;
  border: 1px solid rgba(79, 70, 229, 0.18);
  border-radius: 16px;
  background: #4f46e5;
  color: #f8fafc;
  padding: 12px;
  box-shadow: 0 18px 45px rgba(79, 70, 229, 0.18);
}

.gamification-bar__level,
.gamification-bar__stat {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 42px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.78);
  border: 1px solid rgba(148, 163, 184, 0.2);
  padding: 0 14px;
}

.gamification-bar__icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
  flex: 0 0 auto;
}

.gamification-bar__icon--streak {
  width: 42px;
  height: 42px;
  margin: -5px -7px -5px -9px;
  object-fit: cover;
  object-position: center;
}

.gamification-bar__stat small {
  display: block;
  color: #94a3b8;
  font-size: 10px;
  line-height: 1;
}

.gamification-bar__xp {
  min-width: 0;
}

.gamification-bar__label {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #cbd5e1;
  font-size: 13px;
  margin-bottom: 6px;
}

.gamification-bar__track {
  height: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.24);
}

.gamification-bar__track i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #a7f3d0;
  transition: width 0.45s ease;
}

@media (max-width: 760px) {
  .gamification-bar {
    grid-template-columns: 1fr 1fr;
  }

  .gamification-bar__xp {
    grid-column: 1 / -1;
    order: 3;
  }
}
</style>

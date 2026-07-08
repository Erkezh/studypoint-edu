<template>
  <section class="gamification-bar">
    <div class="gamification-bar__level">
      <span>★</span>
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
      <span>●</span>
      <strong>{{ store.coins.toLocaleString() }}</strong>
    </div>
    <div class="gamification-bar__stat">
      <span>🔥</span>
      <strong>{{ store.dailyStreak }}</strong>
    </div>
    <div class="gamification-bar__stat">
      <span>⚡</span>
      <strong>{{ store.comboStreak }}</strong>
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
  grid-template-columns: auto minmax(180px, 1fr) auto auto auto;
  gap: 12px;
  align-items: center;
  border: 1px solid rgba(34, 211, 238, 0.28);
  border-radius: 16px;
  background:
    radial-gradient(circle at top left, rgba(34, 211, 238, 0.2), transparent 34%),
    linear-gradient(135deg, #08111f, #101827);
  color: #f8fafc;
  padding: 12px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.18);
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

.gamification-bar__level span {
  color: #67e8f9;
}

.gamification-bar__stat span:first-child {
  color: #facc15;
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
  background: linear-gradient(90deg, #22d3ee, #4ade80, #facc15);
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

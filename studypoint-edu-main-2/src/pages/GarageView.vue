<template>
  <Header />
  <aside v-if="trial.isTrial" class="trial-toolbar">
    <div><strong>Сынақ режимі: Көлік гаражы</strong><span>Көлікті еркін өзгертіп көр. Таңдау әзірге сақталмайды.</span></div>
    <button type="button" class="trial-toolbar__secondary" @click="trial.tryOtherGame">Кейіпкерді де байқап көру</button>
    <button type="button" class="trial-toolbar__primary" :disabled="!trial.hasTriedBoth || trial.isChoosing" @click="trial.chooseGame">
      {{ trial.hasTriedBoth ? (trial.isChoosing ? 'Таңдалуда…' : 'Осы ойынды таңдау') : 'Алдымен екі ойынды да байқап көр' }}
    </button>
    <button type="button" class="trial-toolbar__close" aria-label="Ойын таңдау бетіне қайту" @click="trial.backToSelection">×</button>
  </aside>
  <GarageUI />
</template>

<script setup lang="ts">
import Header from '@/components/layout/Header.vue'
import GarageUI from '@/components/Garage/GarageUI.vue'
import { useGameTrial } from '@/composables/useGameTrial'

const trial = useGameTrial('car')
</script>

<style scoped>
.trial-toolbar { position: fixed; z-index: 900; top: 78px; left: 50%; display: flex; width: min(1050px, calc(100% - 24px)); align-items: center; gap: 12px; padding: 12px 54px 12px 18px; transform: translateX(-50%); border: 1px solid rgba(255,255,255,.32); border-radius: 18px; background: rgba(9,35,49,.94); color: white; box-shadow: 0 14px 38px rgba(0,0,0,.28); backdrop-filter: blur(12px); }
.trial-toolbar div { margin-right: auto; }.trial-toolbar strong,.trial-toolbar span { display: block; }.trial-toolbar strong { font-size: 14px; }.trial-toolbar span { margin-top: 2px; color: #bfe8da; font-size: 11px; }.trial-toolbar button { border: 0; border-radius: 11px; padding: 11px 15px; color: white; font-weight: 900; cursor: pointer; }.trial-toolbar__secondary { background: #38546a; }.trial-toolbar__primary { background: #08a755; }.trial-toolbar__primary:disabled { opacity: .52; cursor: not-allowed; }.trial-toolbar .trial-toolbar__close { position: absolute; right: 10px; width: 34px; padding: 6px; background: rgba(255,255,255,.12); font-size: 21px; }
@media (max-width: 760px) { .trial-toolbar { top: 66px; flex-wrap: wrap; padding: 10px 46px 10px 12px; }.trial-toolbar div { width: 100%; }.trial-toolbar button { flex: 1; font-size: 11px; } }
</style>

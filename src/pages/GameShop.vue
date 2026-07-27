<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50 via-white to-cyan-50">
    <Header />
    <main class="mx-auto max-w-7xl px-4 py-8">
      <header class="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p class="text-sm font-black uppercase tracking-widest text-green-600">{{ settings.activeGameLabel }}</p>
          <h1 class="text-4xl font-black text-slate-950">Game Shop</h1>
          <p class="mt-2 text-slate-600">Level unlocks permission to buy. Items are never granted automatically.</p>
        </div>
        <router-link :to="settings.isCarGame ? '/garage' : '/character-customization'" class="rounded-xl bg-green-600 px-5 py-3 font-black text-white">
          {{ settings.isCarGame ? 'Open Garage' : 'Open Wardrobe' }}
        </router-link>
      </header>

      <nav v-if="categories.length" class="mt-7 flex gap-2 overflow-x-auto pb-2" aria-label="Shop categories">
        <button v-for="category in categories" :key="category" type="button" class="whitespace-nowrap rounded-full border px-4 py-2 font-bold capitalize" :class="activeCategory === category ? 'border-green-600 bg-green-600 text-white' : 'border-green-200 bg-white text-slate-700'" @click="activeCategory = category">{{ category }}</button>
      </nav>

      <div v-if="loading" class="mt-10 rounded-3xl bg-white p-10 text-center font-bold text-slate-500">Loading shop…</div>
      <div v-else-if="error" role="alert" class="mt-10 rounded-3xl border border-red-200 bg-red-50 p-6 text-center font-bold text-red-700">{{ error }}</div>
      <div v-else-if="!filteredItems.length" class="mt-10 rounded-3xl border border-green-100 bg-white p-10 text-center">
        <h2 class="text-2xl font-black text-slate-900">No items in this category yet</h2>
        <p class="mt-2 text-slate-500">Your existing inventory remains saved while new products are added.</p>
      </div>
      <section v-else class="mt-7 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <article v-for="item in filteredItems" :key="item.id" class="overflow-hidden rounded-3xl border border-green-100 bg-white shadow-lg shadow-green-100/50">
          <div class="grid h-44 place-items-center bg-green-50">
            <img v-if="item.asset_url || item.thumbnail_url" :src="item.asset_url || item.thumbnail_url || ''" :alt="item.name" class="h-full w-full object-contain p-4" />
            <span v-else class="text-5xl text-green-300">◇</span>
          </div>
          <div class="p-5">
            <h2 class="text-xl font-black text-slate-900">{{ item.name }}</h2>
            <p class="mt-1 text-sm font-semibold text-slate-500">Required Level: {{ requiredLevel(item) }}</p>
            <button class="mt-4 w-full rounded-xl px-4 py-3 font-black" :class="item.owned ? 'bg-slate-100 text-slate-500' : item.locked ? 'bg-slate-200 text-slate-500' : 'bg-green-600 text-white'" type="button" :disabled="item.owned || item.locked || buyingId === item.id" @click="buy(item)">
              {{ item.equipped ? 'Equipped' : item.owned ? 'Owned' : item.locked ? `Reach Level ${requiredLevel(item)}` : buyingId === item.id ? 'Buying…' : `Buy for ${price(item)} coins` }}
            </button>
          </div>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import Header from '@/components/layout/Header.vue'
import { gameShopApi, type GameShopItem } from '@/api/gameShop'
import { useGameSettingsStore } from '@/stores/gameSettings'
import { useGamificationStore } from '@/stores/gamification'

const settings = useGameSettingsStore()
const gamification = useGamificationStore()
const items = ref<GameShopItem[]>([])
const activeCategory = ref('all')
const loading = ref(true)
const error = ref('')
const buyingId = ref<string | null>(null)
const categories = computed(() => ['all', ...new Set(items.value.map((item) => item.category || item.item_type || 'accessories'))])
const filteredItems = computed(() => activeCategory.value === 'all' ? items.value : items.value.filter((item) => (item.category || item.item_type || 'accessories') === activeCategory.value))
const requiredLevel = (item: GameShopItem) => item.required_level ?? item.unlock_level ?? 1
const price = (item: GameShopItem) => item.price ?? item.coin_price ?? 0

async function load() {
  loading.value = true
  error.value = ''
  try {
    const response = await gameShopApi.list()
    items.value = response.data.data || []
  } catch (cause: any) {
    error.value = cause?.response?.data?.error?.message || 'Unable to load the shop.'
  } finally {
    loading.value = false
  }
}

async function buy(item: GameShopItem) {
  buyingId.value = item.id
  error.value = ''
  try {
    if (settings.isCarGame) await gameShopApi.buyCarItem(item.id)
    else await gameShopApi.buyCharacterItem(item.id)
    await Promise.all([load(), gamification.fetchGamification()])
  } catch (cause: any) {
    error.value = cause?.response?.data?.error?.message || 'Purchase failed.'
  } finally {
    buyingId.value = null
  }
}

onMounted(load)
</script>

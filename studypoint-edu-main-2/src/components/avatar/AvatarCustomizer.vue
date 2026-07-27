<template>
  <aside class="avatar-customizer">
    <div class="avatar-customizer__header">
      <div>
        <p>Киімдер</p>
        <h2>{{ activeCategory?.label || 'Кейіпкерді өзгерту' }}</h2>
      </div>
      <span class="avatar-customizer__wallet">
        {{ playerLevel }}-деңгей · {{ coins.toLocaleString() }}
        <img src="/assets/coin-icon.svg" alt="" aria-hidden="true" />
      </span>
    </div>

    <div class="avatar-customizer__actions">
      <button type="button" @click="$emit('reset')">Қалпына келтіру</button>
      <button type="button" @click="$emit('randomize')">Кездейсоқ таңдау</button>
      <button class="avatar-customizer__save" type="button" @click="$emit('save')">Сақтау</button>
    </div>

    <p v-if="savedAt" class="avatar-customizer__saved">Сақталған уақыты: {{ savedAt }}</p>

    <section v-if="activeCategoryId === 'eyes'" class="avatar-customizer__eye-colors">
      <div>
        <strong>Көздің түсі</strong>
        <span>Көз қарашығының түсін таңда</span>
      </div>
      <label class="avatar-customizer__eye-picker" title="Көздің жеке түсі">
        <input
          type="color"
          :value="activeEyeColor"
          aria-label="Көздің жеке түсін таңдау"
          @input="$emit('eye-color', $event.target.value)"
        />
        <span :style="{ background: activeEyeColor }" />
      </label>
      <button
        v-for="color in eyeColors"
        :key="color"
        class="avatar-customizer__eye-swatch"
        :class="{ 'is-active': color === activeEyeColor }"
        type="button"
        :style="{ '--eye-color': color }"
        :aria-label="`Көз түсін ${color} етіп орнату`"
        @click="$emit('eye-color', color)"
      />
    </section>

    <section
      v-if="activeItem && !activeItem.owned"
      class="avatar-customizer__purchase"
      :class="{ 'avatar-customizer__purchase--locked': activeItem.locked }"
    >
      <div>
        <strong v-if="activeItem.locked">
          {{ activeItem.name }} алу үшін {{ activeItem.requiredLevel }}-деңгейге жет
        </strong>
        <strong v-else>{{ activeItem.name }} сатып алуға болады</strong>
        <small>
          <span class="avatar-customizer__coin-price">
            {{ Number(activeItem.price || 0).toLocaleString() }}
            <img src="/assets/coin-icon.svg" alt="" aria-hidden="true" />
          </span>
          · {{ activeItem.requiredLevel }}-деңгей
          · {{ requiredXp.toLocaleString() }} XP
        </small>
      </div>
      <button
        type="button"
        :disabled="activeItem.locked || coins < activeItem.price"
        @click="$emit('buy', activeItem)"
      >
        {{ activeItem.locked ? 'Жабық' : coins < activeItem.price ? 'Монета жеткіліксіз' : 'Сатып алу' }}
      </button>
    </section>

    <div class="avatar-customizer__inventory">
      <div class="avatar-customizer__items">
        <AvatarItemCard
          v-if="activeCategory?.optional"
          :selected="selectedIds[activeCategoryId] === null"
          is-none
          @select="$emit('select', activeCategoryId, null)"
        />

        <AvatarItemCard
          v-for="item in currentItems"
          :key="item.id"
          :item="item"
          :selected="selectedIds[activeCategoryId] === item.id"
          @select="$emit('select', activeCategoryId, item.id)"
          @buy="$emit('buy', item)"
        />
      </div>

      <AvatarCategoryTabs v-model="activeCategoryId" :categories="categories" />
    </div>
  </aside>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import { computed, ref, watch } from 'vue'
import AvatarCategoryTabs from '@/components/avatar/AvatarCategoryTabs.vue'
import AvatarItemCard from '@/components/avatar/AvatarItemCard.vue'

const props = defineProps({
  categories: {
    type: Array,
    required: true,
  },
  groups: {
    type: Object,
    required: true,
  },
  selectedIds: {
    type: Object,
    required: true,
  },
  selectedItems: {
    type: Object,
    required: true,
  },
  savedAt: {
    type: String,
    default: '',
  },
  playerLevel: { type: Number, default: 1 },
  coins: { type: Number, default: 0 },
})

defineEmits(['select', 'buy', 'eye-color', 'reset', 'randomize', 'save'])

const activeCategoryId = ref('')

const totalItems = computed(() =>
  props.categories.reduce((total, category) => total + (category.count || 0), 0),
)
const activeCategory = computed(() =>
  props.categories.find((category) => category.id === activeCategoryId.value),
)
const currentItems = computed(() => [...(props.groups[activeCategoryId.value] || [])].sort((first, second) => {
  const firstFree = first.isFree || first.price === 0
  const secondFree = second.isFree || second.price === 0
  if (firstFree !== secondFree) return firstFree ? -1 : 1

  const levelDifference = (first.requiredLevel || 1) - (second.requiredLevel || 1)
  if (levelDifference) return levelDifference

  const priceDifference = (first.price || 0) - (second.price || 0)
  if (priceDifference) return priceDifference

  return String(first.name || '').localeCompare(String(second.name || ''))
}))
const eyeColors = ['#6e4be8', '#2f82e8', '#26b8b1', '#45a85a', '#d4a72c', '#e46b35', '#d94f86', '#7a4a2f']

function colorToHex(color) {
  if (!color) return '#ff6234'
  const component = (value) => Math.round(Math.min(1, Math.max(0, value || 0)) * 255).toString(16).padStart(2, '0')
  return `#${component(color.r)}${component(color.g)}${component(color.b)}`
}

const activeEyeColor = computed(() => colorToHex(props.selectedItems.eyes?.presetColors?.[0]))
const levelXp = [0, 0, 300, 700, 1200, 1800, 2500, 3300, 4300, 5500, 7000, 8800, 10900]
const activeItem = computed(() => {
  const selectedId = props.selectedIds[activeCategoryId.value]
  if (!selectedId) return null
  return currentItems.value.find((item) => item.id === selectedId) || null
})
const requiredXp = computed(() => levelXp[activeItem.value?.requiredLevel || 1] || 0)

watch(
  () => props.categories,
  (categories) => {
    if (!categories.length) return
    if (!categories.some((category) => category.id === activeCategoryId.value)) {
      activeCategoryId.value = categories[0].id
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.avatar-customizer {
  display: flex;
  flex-direction: column;
  height: min(45rem, calc(100vh - 9rem));
  min-height: 0;
  border: 1px solid #d9e4ff;
  border-radius: 18px;
  background: linear-gradient(155deg, rgb(255 255 255 / 98%), rgb(246 248 255 / 96%));
  padding: 0.8rem;
  box-shadow: 0 22px 60px rgb(69 78 130 / 15%);
  width: 100%;
  min-width: 0;
}

.avatar-customizer__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.65rem;
}

.avatar-customizer__header p {
  margin: 0 0 0.1rem;
  color: #4f46e5;
  font-size: 0.78rem;
  font-weight: 900;
  text-transform: uppercase;
}

.avatar-customizer__header h2 {
  margin: 0;
  color: #111827;
  font-size: 1.35rem;
  font-weight: 950;
}

.avatar-customizer__header span {
  border-radius: 999px;
  border: 1px solid #cfd7ff;
  background: #eeefff;
  color: #3730a3;
  padding: 0.4rem 0.65rem;
  font-size: 0.78rem;
  font-weight: 900;
  white-space: nowrap;
}

.avatar-customizer__header .avatar-customizer__wallet,
.avatar-customizer__coin-price {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.avatar-customizer__wallet img,
.avatar-customizer__coin-price img {
  width: 1.05rem;
  height: 1.05rem;
  object-fit: contain;
}

.avatar-customizer__actions {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.55rem;
  margin-bottom: 0.65rem;
}

.avatar-customizer__actions button {
  min-height: 2.55rem;
  border: 1px solid #cdd8f5;
  border-radius: 999px;
  background: #fff;
  color: #1f2a44;
  font-weight: 900;
}

.avatar-customizer__actions .avatar-customizer__save {
  border-color: #4f7cff;
  background: linear-gradient(135deg, #23c7dc, #5563f5);
  color: #fff;
}

.avatar-customizer__saved {
  margin: -0.35rem 0 0.75rem;
  color: #667085;
  font-size: 0.82rem;
  font-weight: 700;
}

.avatar-customizer__inventory {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 3.55rem;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  border: 1px solid #d9e4ff;
  border-radius: 14px;
  background: #f2f5ff;
}

.avatar-customizer__eye-colors {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.65rem;
  border: 1px solid #d7def5;
  border-radius: 12px;
  background: #fff;
  padding: 0.55rem;
}

.avatar-customizer__purchase {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 0.65rem;
  border: 1px solid #ffd166;
  border-radius: 14px;
  background: #fff4c7;
  padding: 0.65rem;
  color: #10182f;
}

.avatar-customizer__purchase--locked {
  border-color: #ffd166;
  background: #fff4c7;
}

.avatar-customizer__purchase strong,
.avatar-customizer__purchase small {
  display: block;
}

.avatar-customizer__purchase strong {
  font-size: 0.78rem;
  font-weight: 950;
}

.avatar-customizer__purchase small {
  margin-top: 0.2rem;
  color: #465367;
  font-size: 0.66rem;
  font-weight: 750;
}

.avatar-customizer__purchase button {
  min-width: 6.5rem;
  min-height: 2.35rem;
  border: 0;
  border-radius: 13px;
  background: #0eb468;
  color: #182033;
  font-size: 0.75rem;
  font-weight: 950;
  cursor: pointer;
}

.avatar-customizer__purchase button:disabled {
  background: #a6d4ae;
  cursor: not-allowed;
}

.avatar-customizer__eye-colors > div {
  display: grid;
  min-width: 7rem;
  margin-right: auto;
}

.avatar-customizer__eye-colors strong {
  color: #fff;
  font-size: 0.78rem;
}

.avatar-customizer__eye-colors div span {
  color: #667085;
  font-size: 0.62rem;
}

.avatar-customizer__eye-picker,
.avatar-customizer__eye-swatch {
  position: relative;
  flex: 0 0 1.8rem;
  width: 1.8rem;
  height: 1.8rem;
  border: 2px solid #fff;
  border-radius: 50%;
  background: var(--eye-color, transparent);
  box-shadow: 0 2px 10px rgb(47 55 92 / 18%);
  cursor: pointer;
}

.avatar-customizer__eye-picker {
  overflow: hidden;
}

.avatar-customizer__eye-picker input {
  position: absolute;
  inset: -0.5rem;
  opacity: 0;
  cursor: pointer;
}

.avatar-customizer__eye-picker span {
  display: block;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.avatar-customizer__eye-swatch.is-active {
  border-color: #fff;
  box-shadow: 0 0 0 3px #5b67f1;
}

.avatar-customizer__items {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  grid-auto-rows: minmax(7.25rem, 1fr);
  align-content: start;
  flex: 1;
  min-height: 0;
  gap: 0.45rem;
  overflow-y: auto;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
  margin-top: 0;
  padding: 0.55rem;
}

.avatar-customizer__items :deep(.avatar-item) {
  min-height: 0;
  border-color: #d7e0f3;
  border-radius: 11px;
  background: #fff;
  padding: 0.35rem;
  box-shadow: 0 5px 14px rgb(68 79 125 / 8%);
}

.avatar-customizer__items :deep(.avatar-item--selected) {
  border-color: #5468f3;
  box-shadow: 0 0 0 3px rgb(84 104 243 / 16%);
}

.avatar-customizer__items :deep(.avatar-thumbnail) {
  border-radius: 8px;
  background: linear-gradient(145deg, #e9f9ff, #dce7ff);
}


.avatar-customizer__items::-webkit-scrollbar {
  width: 0.55rem;
}

.avatar-customizer__items::-webkit-scrollbar-track {
  border-radius: 999px;
  background: #dde4f4;
}

.avatar-customizer__items::-webkit-scrollbar-thumb {
  border: 2px solid #dde4f4;
  border-radius: 999px;
  background: linear-gradient(#32cee0, #5b67f1);
}

@media (max-width: 480px) {
  .avatar-customizer__items {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    grid-auto-rows: 10rem;
  }
}

@media (max-width: 900px) {
  .avatar-customizer {
    height: auto;
    border-radius: 20px;
  }

  .avatar-customizer__inventory {
    grid-template-columns: 1fr;
    grid-template-rows: minmax(20rem, 1fr) 3.6rem;
  }

  .avatar-customizer__items {
    max-height: 27rem;
  }
}
</style>

<template>
  <div
    class="avatar-item"
    :class="{ 'avatar-item--selected': selected, 'avatar-item--none': isNone, 'avatar-item--locked': item?.locked }"
  >
    <button class="avatar-item__preview" :aria-label="isNone ? 'Таңдалған затты алып тастау' : `${title} таңдау`" :title="isNone ? 'Таңдалған затты алып тастау' : title" type="button" @click="$emit('select')">
      <span v-if="isNone" class="avatar-item__none-icon" aria-hidden="true">×</span>
      <AvatarItemThumbnail v-else :item="item" />
    </button>
    <template v-if="!isNone">
      <span v-if="item.owned" class="avatar-item__status avatar-item__status--owned">✓</span>
      <span v-else-if="item.locked" class="avatar-item__status">{{ item.requiredLevel }}</span>
      <button v-else class="avatar-item__buy" type="button" @click.stop="$emit('buy')">
        <span>{{ Number(item.price || 0).toLocaleString() }}</span>
        <img src="/assets/coin-icon.svg" alt="" aria-hidden="true" />
      </button>
    </template>
    <span v-if="!isNone && item.locked" class="avatar-item__lock" aria-hidden="true">
      <svg viewBox="0 0 64 64" focusable="false">
        <path d="M18 28h28a6 6 0 0 1 6 6v16a6 6 0 0 1-6 6H18a6 6 0 0 1-6-6V34a6 6 0 0 1 6-6Z" />
        <path d="M22 28v-8a10 10 0 0 1 20 0v8h-6v-8a4 4 0 0 0-8 0v8h-6Z" />
        <path d="M32 38a4 4 0 0 1 2 7.46V50h-4v-4.54A4 4 0 0 1 32 38Z" />
      </svg>
    </span>
  </div>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import { computed } from 'vue'
import AvatarItemThumbnail from '@/components/avatar/AvatarItemThumbnail.vue'

const props = defineProps({
  item: {
    type: Object,
    default: null,
  },
  selected: {
    type: Boolean,
    default: false,
  },
  isNone: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['select', 'buy'])

const title = computed(() => (props.isNone ? 'Жоқ' : props.item?.name || 'Белгісіз'))
</script>

<style scoped>
.avatar-item {
  display: block;
  width: 100%;
  height: 100%;
  min-height: 12rem;
  border: 1px solid #e0ebdc;
  border-radius: 16px;
  background: #fff;
  padding: 0.7rem;
  text-align: left;
  box-shadow: 0 8px 20px rgb(24 48 32 / 6%);
  transition:
    border-color 0.18s ease,
    box-shadow 0.18s ease,
    transform 0.18s ease;
}
.avatar-item__preview { width: 100%; height: 100%; border: 0; background: transparent; padding: 0; cursor: pointer; }

.avatar-item :deep(.avatar-thumbnail) {
  height: 100%;
  aspect-ratio: auto;
}

.avatar-item:hover {
  transform: translateY(-1px);
  border-color: #38b000;
  box-shadow: 0 14px 28px rgb(24 48 32 / 10%);
}

.avatar-item--selected {
  border-color: #38b000;
  box-shadow: 0 0 0 3px rgb(56 176 0 / 16%);
}

.avatar-item__none-icon {
  display: grid;
  width: 100%;
  height: 100%;
  place-items: center;
  border-radius: 14px;
  background: linear-gradient(145deg, #e7f8dd, #c9f0ba);
  color: #1e5c1c;
  font-size: 0.8rem;
  font-weight: 900;
}

.avatar-item--none .avatar-item__none-icon {
  background: #f3f6f2;
  color: #71806d;
}

.avatar-item--none {
  min-height: 12rem;
}
.avatar-item__status { position: absolute; top: .35rem; right: .35rem; z-index: 5; border-radius: 999px; background: rgb(9 27 46 / 88%); padding: .22rem .4rem; color: #fff; font-size: .65rem; font-weight: 950; }.avatar-item__status--owned { background: #079653; }.avatar-item__buy { position: absolute; z-index: 3; right: .3rem; bottom: .3rem; display: inline-flex; align-items: center; gap: .28rem; border: 1px solid rgb(255 255 255 / 35%); border-radius: 999px; background: #0aa558; padding: .3rem .5rem; color: white; font-size: .65rem; font-weight: 950; cursor: pointer; }
.avatar-item__buy img { width: 1rem; height: 1rem; object-fit: contain; }
.avatar-item__lock {
  position: absolute;
  inset: 8px;
  z-index: 4;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 14px;
  background: transparent;
  pointer-events: none;
}
.avatar-item__lock svg {
  width: 38px;
  height: 38px;
  padding: 7px;
  border-radius: 12px;
  background: rgb(238 247 255 / 78%);
  fill: #64748b;
  filter: drop-shadow(0 5px 10px rgb(0 0 0 / 28%));
}
.avatar-item--locked .avatar-item__preview { filter: none; opacity: 1; }
.avatar-item--locked { border-color: #c8d1df; background: linear-gradient(155deg, #edf1f6, #dfe6ef); }
.avatar-item--locked:hover { border-color: #aeb9cb; box-shadow: inset 0 0 0 1px rgb(255 255 255 / 55%); }
.avatar-item { position: relative; overflow: hidden; }
</style>

<template>
  <div class="avatar-tabs" role="tablist" aria-label="Кейіпкер санаттары">
    <button
      v-for="category in categories"
      :key="category.id"
      class="avatar-tab"
      :class="{ 'avatar-tab--active': category.id === modelValue }"
      type="button"
      role="tab"
      :aria-selected="category.id === modelValue"
      @click="$emit('update:modelValue', category.id)"
    >
      <img :src="categoryIcon(category.id)" alt="" aria-hidden="true" />
      <span>{{ category.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
defineProps({
  categories: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: String,
    required: true,
  },
})

defineEmits(['update:modelValue'])

const icons = {
  characters: 'Expression', body: 'Body', head: 'Head', eyes: 'Eyes', eyeBrows: 'EyeBrows',
  eyeLashes: 'EyeLashes', pupil: 'Pupil', eyeShine: 'EyeShine', hairFront: 'HairFront',
  hairBack: 'HairBack', top: 'Top', bottom: 'Bottom', overall: 'Overall', feet: 'Feet',
  socks: 'Socks', gloves: 'Hands', headAcc: 'HeadAcc', upperFace: 'UpperFace',
  lowerFace: 'LowerFace', neck: 'Neck', faceDetails: 'FaceDetails', makeUpCheeks: 'MakeUpCheeks',
  makeUpLips: 'MakeUpLips', leggings: 'Leggings', underLower: 'UnderLower', underUpper: 'UnderUpper',
}

function categoryIcon(id) {
  return `/assets/characters/bozo/ui-icons/UI_Icon_${icons[id] || 'Body'}.png`
}
</script>

<style scoped>
.avatar-tabs {
  display: grid;
  grid-auto-rows: 3rem;
  gap: 0.3rem;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0.3rem;
  scrollbar-width: thin;
  width: 100%;
  max-width: 100%;
  border-left: 1px solid #d9e4ff;
  background: #edf2ff;
}

.avatar-tab {
  position: relative;
  display: grid;
  place-items: center;
  align-items: center;
  gap: 0.45rem;
  min-width: 2.8rem;
  min-height: 2.8rem;
  border: 1px solid #d3dcf5;
  border-radius: 12px;
  background: #fff;
  color: #45506a;
  padding: 0;
  font-weight: 800;
  white-space: nowrap;
  transition:
    background 0.18s ease,
    color 0.18s ease,
    border-color 0.18s ease,
    transform 0.18s ease;
}

.avatar-tab:hover {
  transform: translateX(-2px);
  border-color: #5b67f1;
}

.avatar-tab img {
  width: 2rem;
  height: 2rem;
  object-fit: contain;
  filter: brightness(0) saturate(100%) invert(38%) sepia(92%) saturate(1364%) hue-rotate(215deg) brightness(96%) contrast(98%);
  opacity: 0.9;
}

.avatar-tab > span {
  position: absolute;
  right: calc(100% + 0.55rem);
  z-index: 4;
  display: none;
  border-radius: 8px;
  background: #232b49;
  color: white;
  padding: 0.35rem 0.55rem;
  font-size: 0.72rem;
  box-shadow: 0 6px 18px rgb(4 21 35 / 28%);
}

.avatar-tab:hover > span,
.avatar-tab:focus-visible > span {
  display: block;
}

.avatar-tab--active {
  border-color: #72e8f6;
  background: linear-gradient(145deg, #25c9dd, #5964f2);
  color: white;
  box-shadow: 0 10px 24px rgb(78 91 222 / 24%);
}

.avatar-tab--active img {
  filter: brightness(0) invert(1);
  opacity: 1;
}

@media (max-width: 900px) {
  .avatar-tabs {
    display: flex;
    overflow-x: auto;
    overflow-y: hidden;
    border-left: 0;
    border-top: 1px solid #d9e4ff;
  }

  .avatar-tab {
    flex: 0 0 3rem;
  }

  .avatar-tab:hover {
    transform: translateY(-1px);
  }

  .avatar-tab > span {
    display: none !important;
  }
}

</style>

<template>
  <section class="garage-bottom" :class="{ 'garage-bottom--disabled': disabled }">
    <div class="garage-bottom__title">
      <span>{{ title }}</span>
      <strong>{{ options.length }} нұсқа</strong>
    </div>

    <div class="garage-carousel">
      <button
        v-for="option in options"
        :key="option.id"
        class="garage-option"
        :class="{
          'garage-option--selected': isSelected(option.id),
          'garage-option--locked': locked(option),
          'garage-option--previewable': locked(option) && allowLockedPreview,
        }"
        type="button"
        :disabled="disabled || (locked(option) && !allowLockedPreview)"
        @click="selectOption(option)"
      >
        <span class="garage-option__preview" :style="previewStyle(option)">
          <span v-if="option.model && !option.value" class="garage-option__model">3D</span>
        </span>
        <span class="garage-option__name">{{ option.name }}</span>
        <small>{{ locked(option) ? lockedLabel(option) : rarityLabel(option.rarity) }}</small>
        <span v-if="locked(option)" class="garage-option__lock" aria-hidden="true">
          <svg viewBox="0 0 64 64" focusable="false">
            <path d="M18 28h28a6 6 0 0 1 6 6v16a6 6 0 0 1-6 6H18a6 6 0 0 1-6-6V34a6 6 0 0 1 6-6Z" />
            <path d="M22 28v-8a10 10 0 0 1 20 0v8h-6v-8a4 4 0 0 0-8 0v8h-6Z" />
            <path d="M32 38a4 4 0 0 1 2 7.46V50h-4v-4.54A4 4 0 0 1 32 38Z" />
          </svg>
        </span>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { GaragePart, GarageSelection } from '@/config/garage'

const props = defineProps<{
  title: string
  options: GaragePart[]
  selection: GarageSelection
  playerLevel: number
  control?: string
  lockedIds?: string[]
  lockedLabels?: Record<string, string>
  allowLockedPreview?: boolean
  disabled?: boolean
}>()

const emit = defineEmits<{
  select: [option: GaragePart]
}>()

const locked = (option: GaragePart) => props.lockedIds?.includes(option.id) ?? false

const lockedLabel = (option: GaragePart) => props.lockedLabels?.[option.id] ?? `${option.unlockLevel ?? 1}-деңгей`

const selectOption = (option: GaragePart) => {
  if (props.disabled) return
  if (locked(option) && !props.allowLockedPreview) return
  emit('select', option)
}

const rarityLabel = (rarity?: string) => {
  if (rarity === 'legendary') return 'аңызға айналған'
  if (rarity === 'epic') return 'эпикалық'
  if (rarity === 'rare') return 'сирек'
  if (rarity === 'common') return 'қарапайым'
  return 'бар'
}

const isSelected = (id: string) => {
  if (props.control === 'paint') return props.selection.paint === id
  if (props.control === 'rims') return props.selection.rimColor === id
  if (props.control === 'windows') return props.selection.windowTint === id
  if (props.control === 'stickerColor') return props.selection.stickerColor === id
  return Object.values(props.selection).includes(id)
}

const previewStyle = (option: GaragePart) => {
  if (props.control === 'stickerColor' && option.value) return stickerColorPreview(option.value)
  if (option.value && option.value.startsWith('#')) {
    return { background: option.value }
  }
  return option.preview ? { backgroundImage: `url(${option.preview})` } : {}
}

const stickerColorPreview = (color: string) => {
  return {
    background: `linear-gradient(135deg, ${color} 0 36%, #0f172a 37% 43%, ${color} 44% 66%, #0f172a 67% 73%, ${color} 74%)`,
  }
}
</script>

<template>
  <div class="garage-swatches">
    <button
      v-for="option in options"
      :key="option.id"
      type="button"
      class="garage-swatch"
      :class="{ 'garage-swatch--active': option.id === value }"
      :style="{ background: option.value ?? 'linear-gradient(135deg, #073b2f 0%, #073b2f 55%, #cfd3d4 56%, #cfd3d4 72%, #111827 73%)' }"
      :title="option.name"
      :disabled="disabled"
      @click="selectOption(option)"
    />
  </div>
</template>

<script setup lang="ts">
import type { GaragePart } from '@/config/garage'

const props = defineProps<{
  options: GaragePart[]
  value: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  select: [option: GaragePart]
}>()

const selectOption = (option: GaragePart) => {
  if (props.disabled) return
  emit('select', option)
}
</script>

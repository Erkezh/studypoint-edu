<template>
  <svg class="game-select-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path v-for="(path, index) in paths" :key="index" :d="path" />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ name: string }>()

const iconPaths: Record<string, string[]> = {
  car: ['M4 16v-3l2-5h12l2 5v3', 'M3 13h18v5H3z', 'M6 18v2M18 18v2', 'M7 8l1.5 5h7L17 8', 'M7 16h.01M17 16h.01'],
  person: ['M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z', 'M4.5 21a7.5 7.5 0 0 1 15 0'],
  vehicles: ['M4 16v-3l2-4h12l2 4v3', 'M3 13h18v5H3z', 'M6 18v2M18 18v2'],
  wrench: ['M14.5 6.5a4 4 0 0 0-5-5l2.3 2.3-2 2-2.3-2.3a4 4 0 0 0 5 5L20 16l-4 4-7.5-7.5'],
  palette: ['M12 3a9 9 0 0 0 0 18h1.5a2 2 0 0 0 0 0-4H12a2 2 0 0 1 0-4h3a6 6 0 0 0 0-3-10Z', 'M7.5 9h.01M10 6.5h.01M14 6.5h.01M17 9h.01'],
  trophy: ['M8 4h8v5a4 4 0 0 1-8 0V4Z', 'M8 6H4v1a4 4 0 0 0 4 4M16 6h4v1a4 4 0 0 1-4 4', 'M12 13v4M8 21h8M9 17h6'],
  shirt: ['M8 4l4 2 4-2 5 3-3 5-2-1v9H8v-9l-2 1-3-5 5-3Z'],
  hair: ['M5 12a7 7 0 0 1 14 0v8l-3-4-1 5-3-5-3 5-1-5-3 4v-8Z', 'M7 10c2-1 3-3 4-5 1 2 3 4 6 5'],
  shoe: ['M4 15V9h5l2 5 8 2c1 .3 2 1.2 2 2.3V20H4v-5Z', 'M11 14l2-2M14 15l2-2'],
  star: ['m12 3 2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9L12 3Z'],
  check: ['M5 12.5 10 17l9-10'],
  gamepad: ['M7 8h10a5 5 0 0 1 4.6 7l-1.1 2.6a2.4 2.4 0 0 1-3.8.9L15 17H9l-1.7 1.5a2.4 2.4 0 0 1-3.8-.9L2.4 15A5 5 0 0 1 7 8Z', 'M7 11v4M5 13h4M16 12h.01M18 15h.01'],
  diamond: ['m12 3 8 7-8 11-8-11 8-7Z', 'm4 10h16M9 3l-2 7 5 11 5-11-2-7'],
}

const paths = computed(() => iconPaths[props.name] || iconPaths.star)
</script>

<style scoped>
.game-select-icon {
  width: 1em;
  height: 1em;
  overflow: visible;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}
</style>

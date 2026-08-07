<template>
  <span ref="host" class="vehicle-card-preview" aria-hidden="true">
    <img :src="`/assets/garage-thumbnails/${vehicleId}.png`" alt="" />
    <canvas ref="canvas"></canvas>
  </span>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { mountVehicleCardModel } from './vehicleCardPreview3d'

const props = defineProps<{ vehicleId: string; model: string }>()
const host = ref<HTMLElement | null>(null)
const canvas = ref<HTMLCanvasElement | null>(null)
let observer: IntersectionObserver | null = null
let stopPreview: (() => void) | null = null
let previewVersion = 0

const stop = () => {
  previewVersion += 1
  stopPreview?.()
  stopPreview = null
}

const start = async () => {
  if (!canvas.value || stopPreview) return
  const version = ++previewVersion
  const cleanup = await mountVehicleCardModel(canvas.value, props.model)
  if (version !== previewVersion) cleanup()
  else stopPreview = cleanup
}

onMounted(() => {
  observer = new IntersectionObserver(([entry]) => {
    if (entry?.isIntersecting) void start()
    else stop()
  }, { threshold: 0.1 })
  if (host.value) observer.observe(host.value)
})

watch(() => props.model, () => {
  stop()
  void start()
})

onBeforeUnmount(() => {
  observer?.disconnect()
  stop()
})
</script>

<style scoped>
.vehicle-card-preview {
  position: relative;
  z-index: 2;
  display: grid;
  width: 100%;
  height: 50px;
  place-items: center;
  overflow: hidden;
  border-radius: 13px;
  background: radial-gradient(circle at 50% 62%, rgba(255, 255, 255, 0.96), rgba(224, 242, 254, 0.5) 68%, transparent 82%);
}

.vehicle-card-preview img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
  transform: translateY(7px);
}

.vehicle-card-preview canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  transform: translateY(7px);
}

@media (max-width: 720px) {
  .vehicle-card-preview {
    height: 42px;
  }
}
</style>

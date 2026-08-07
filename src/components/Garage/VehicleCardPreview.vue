<template>
  <span class="vehicle-card-preview" aria-hidden="true">
    <img v-if="thumbnail" :src="thumbnail" alt="" />
  </span>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { getVehicleCardThumbnail } from './vehicleCardThumbnail'

const props = defineProps<{ model: string }>()
const thumbnail = ref('')
let loadToken = 0

const loadThumbnail = async () => {
  const token = ++loadToken
  try {
    const image = await getVehicleCardThumbnail(props.model)
    if (token === loadToken) thumbnail.value = image
  } catch {
    if (token === loadToken) thumbnail.value = ''
  }
}

onMounted(loadThumbnail)
watch(() => props.model, loadThumbnail)
</script>

<style scoped>
.vehicle-card-preview {
  position: absolute;
  inset: 2px 4px 42px;
  z-index: 1;
  display: grid;
  place-items: center;
  overflow: hidden;
  border-radius: 12px;
  background: radial-gradient(circle at 50% 62%, rgba(255, 255, 255, 0.96), rgba(224, 242, 254, 0.5) 62%, transparent 76%);
}

.vehicle-card-preview img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
}
</style>

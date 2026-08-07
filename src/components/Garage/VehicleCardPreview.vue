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
}

@media (max-width: 720px) {
  .vehicle-card-preview {
    height: 42px;
  }
}
</style>

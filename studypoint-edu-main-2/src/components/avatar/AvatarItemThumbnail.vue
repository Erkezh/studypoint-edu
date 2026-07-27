<template>
  <span class="avatar-thumbnail" :class="{ 'avatar-thumbnail--loading': loading }">
    <img v-if="src" :src="src" :alt="`${item.name} preview`" />
    <span v-else aria-hidden="true">{{ loading ? '…' : initials }}</span>
  </span>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import { computed, ref, watch } from 'vue'
import { getAvatarItemThumbnail } from '@/services/avatarThumbnailService'

const props = defineProps({ item: { type: Object, required: true } })
const src = ref('')
const loading = ref(false)
let requestId = 0

const initials = computed(() => String(props.item?.name || '?').slice(0, 2).toUpperCase())

watch(
  () => props.item,
  async (item) => {
    const currentRequest = ++requestId
    src.value = item?.thumbnailPath || ''
    if (src.value || !item) return
    loading.value = true
    try {
      const result = await getAvatarItemThumbnail(item)
      if (currentRequest === requestId) src.value = result
    } catch (error) {
      if (import.meta.env.DEV) console.warn('[avatar-thumbnail] Unable to render preview', item.id, error)
    } finally {
      if (currentRequest === requestId) loading.value = false
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.avatar-thumbnail {
  display: grid;
  width: 100%;
  aspect-ratio: 1;
  place-items: center;
  overflow: hidden;
  border-radius: 14px;
  background: linear-gradient(145deg, #f4fbf1, #e2f3dc);
  color: #4d6d4c;
  font-weight: 900;
}

.avatar-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.avatar-thumbnail--loading span {
  animation: avatar-thumbnail-pulse 1s ease-in-out infinite alternate;
}

@keyframes avatar-thumbnail-pulse {
  to { opacity: 0.35; }
}
</style>


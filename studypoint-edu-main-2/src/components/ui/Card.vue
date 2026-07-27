<template>
  <div
    :class="[
      'bg-white rounded-lg shadow-md p-6',
      {
        'cursor-pointer hover:shadow-lg transition-shadow': clickable,
      },
      className,
    ]"
    @click="clickable && $emit('click', $event)"
  >
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
interface Props {
  clickable?: boolean
  className?: string
}

withDefaults(defineProps<Props>(), {
  clickable: false,
  className: '',
})

defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

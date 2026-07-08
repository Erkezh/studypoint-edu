<template>
  <div class="finish-screen">
    <div class="finish-screen__glow"></div>
    <div class="finish-screen__content">
      <span class="finish-screen__badge">Дайын</span>
      <h1>Көлігің дайын!</h1>
      <p>StudyPoint гаражына сақталды.</p>
      <button type="button" @click="$emit('customize')">Тағы баптау</button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  customize: []
}>()
</script>

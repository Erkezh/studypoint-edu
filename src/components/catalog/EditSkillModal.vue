<template>
  <Modal :is-open="isVisible" title="Edit Skill" @close="close">
    <template #content>
      <div class="space-y-4">
        <!-- Grade Select -->
        <div>
           <label class="block text-sm font-medium text-gray-700">Grade</label>
           <select v-model.number="form.grade_id" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
              <option v-for="grade in catalogStore.grades" :key="grade.id" :value="grade.id">
                {{ grade.title }}
              </option>
           </select>
        </div>

        <!-- Topic Select -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Topic</label>
          <select v-model.number="form.topic_id" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
             <option :value="null">No Topic</option>
             <option v-for="topic in catalogStore.topics" :key="topic.id" :value="topic.id">
               {{ topic.title }}
             </option>
          </select>
        </div>

        <!-- Code Input -->
        <div>
           <label class="block text-sm font-medium text-gray-700">Code</label>
           <input type="text" v-model="form.code" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
        </div>

        <!-- Title Input -->
        <div>
           <label class="block text-sm font-medium text-gray-700">Title</label>
           <input type="text" v-model="form.title" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
        </div>
      </div>
    </template>

    <template #actions>
      <Button variant="outline" @click="close">Cancel</Button>
      <Button variant="primary" @click="save" :loading="isLoading">
        Save
      </Button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import Modal from '@/components/ui/Modal.vue'
import Button from '@/components/ui/Button.vue'
import { useCatalogStore } from '@/stores/catalog'
import type { SkillListItem } from '@/types/api'

const props = defineProps<{
  isVisible: boolean
  skill: SkillListItem | null
}>()

const emit = defineEmits(['close', 'save'])

const catalogStore = useCatalogStore()
const isLoading = ref(false)

const form = ref({
  grade_id: 0,
  topic_id: null as number | null,
  code: '',
  title: ''
})

watch(() => props.skill, (newSkill) => {
  if (newSkill) {
    form.value = {
      grade_id: newSkill.grade_id,
      topic_id: newSkill.topic_id || null,
      code: newSkill.code,
      title: newSkill.title
    }
  }
}, { immediate: true })

onMounted(() => {
    if (catalogStore.grades.length === 0) catalogStore.getGrades()
    if (catalogStore.topics.length === 0) catalogStore.getTopics()
})

const close = () => {
  emit('close')
}

const save = async () => {
  if (!props.skill) return
  isLoading.value = true
  try {
    await catalogStore.updateSkill(props.skill.id, form.value)
    emit('save')
    close()
  } catch (e) {
    console.error(e)
    alert('Failed to save skill')
  } finally {
    isLoading.value = false
  }
}
</script>

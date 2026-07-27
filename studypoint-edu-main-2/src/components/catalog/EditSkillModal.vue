<template>
  <Modal :is-open="isVisible" :title="isDuplicate ? 'Тестті көшіру' : 'Тестті өңдеу'" @close="close">
    <template #content>
      <div class="space-y-4">
        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Атауы</label>
          <input type="text" v-model="form.title" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
        </div>

        <!-- Grade -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Сынып</label>
          <select v-model.number="form.grade_id" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
            <option v-for="grade in catalogStore.grades" :key="grade.id" :value="grade.id">
              {{ grade.title }}
            </option>
          </select>
        </div>

        <!-- Topic / Subtopic -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Тақырып</label>
          <select
            v-model="selectedThemeId"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option :value="null">Тақырыпсыз</option>
            <option v-for="theme in parentThemes" :key="theme.id" :value="theme.id">
              {{ theme.icon ? `${theme.icon} ` : '' }}{{ theme.title }}
            </option>
          </select>
        </div>

        <div v-if="selectedThemeId !== null && currentSubthemes.length > 0">
          <label class="block text-sm font-medium text-gray-700">Ішкі тақырып</label>
          <select
            v-model="selectedSubthemeId"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option :value="null">Ішкі тақырыпсыз (тек тақырып)</option>
            <option v-for="sub in currentSubthemes" :key="sub.id" :value="sub.id">
              {{ sub.title }}
            </option>
          </select>
        </div>

        <p
          v-if="selectedThemeId !== null && currentSubthemes.length === 0"
          class="text-sm text-gray-500"
        >
          Бұл тақырыпта ішкі тақырыптар жоқ. Тест осы тақырыптың өзіне байланысады.
        </p>

        <!-- Code -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Код</label>
          <input type="text" v-model="form.code" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
        </div>
      </div>
    </template>

    <template #actions>
      <Button variant="outline" @click="close">Болдырмау</Button>
      <Button variant="primary" @click="save" :loading="isLoading">Сақтау</Button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import Modal from '@/components/ui/Modal.vue'
import Button from '@/components/ui/Button.vue'
import { useCatalogStore } from '@/stores/catalog'
import { adminApi } from '@/api/admin'
import type { SkillListItem } from '@/types/api'

const props = defineProps<{
  isVisible: boolean
  skill: SkillListItem | null
  isDuplicate?: boolean
}>()

const emit = defineEmits(['close', 'save'])

const catalogStore = useCatalogStore()
const isLoading = ref(false)

const parentThemes = computed(() =>
  catalogStore.topics.filter(t => !t.parent_id).sort((a, b) => a.order - b.order)
)

const getSubthemes = (themeId: number) =>
  catalogStore.topics.filter(t => t.parent_id === themeId).sort((a, b) => a.order - b.order)

const selectedThemeId = ref<number | null>(null)
const selectedSubthemeId = ref<number | null>(null)

const currentSubthemes = computed(() =>
  selectedThemeId.value !== null ? getSubthemes(selectedThemeId.value) : []
)

const hydrateSelection = (skill: SkillListItem | null) => {
  if (!skill) {
    selectedThemeId.value = null
    selectedSubthemeId.value = null
    return
  }

  if (!skill.topic_id) {
    selectedThemeId.value = null
    selectedSubthemeId.value = null
    return
  }

  const topic = catalogStore.topics.find(t => t.id === skill.topic_id)
  if (!topic) {
    selectedThemeId.value = null
    selectedSubthemeId.value = null
    return
  }

  if (topic.parent_id) {
    selectedThemeId.value = topic.parent_id
    selectedSubthemeId.value = topic.id
    return
  }

  selectedThemeId.value = topic.id
  selectedSubthemeId.value = null
}

const form = ref({
  grade_id: 0,
  topic_id: null as number | null,
  code: '',
  title: ''
})

watch(
  [() => props.skill, () => catalogStore.topics.length],
  ([newSkill]) => {
    if (newSkill) {
    form.value = {
      grade_id: newSkill.grade_id,
      topic_id: newSkill.topic_id || null,
      code: newSkill.code,
      title: props.isDuplicate ? `${newSkill.title} (Көшірме)` : newSkill.title
    }
      hydrateSelection(newSkill)
    } else {
      form.value = {
        grade_id: 0,
        topic_id: null,
        code: '',
        title: ''
      }
      hydrateSelection(null)
    }
  },
  { immediate: true }
)

watch(selectedThemeId, (themeId) => {
  if (themeId === null) {
    selectedSubthemeId.value = null
    form.value.topic_id = null
    return
  }

  const hasSelectedSubtheme = currentSubthemes.value.some(sub => sub.id === selectedSubthemeId.value)
  if (!hasSelectedSubtheme) {
    selectedSubthemeId.value = null
  }

  form.value.topic_id = selectedSubthemeId.value ?? themeId
})

watch(selectedSubthemeId, (subthemeId) => {
  if (selectedThemeId.value === null) {
    form.value.topic_id = null
    return
  }

  form.value.topic_id = subthemeId ?? selectedThemeId.value
})

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
    if (props.isDuplicate) {
      await adminApi.duplicateSkill(props.skill.id, {
        subject_id: props.skill.subject_id,
        grade_id: form.value.grade_id,
        topic_id: form.value.topic_id,
        code: form.value.code,
        title: form.value.title,
        is_published: true
      })
    } else {
      await catalogStore.updateSkill(props.skill.id, form.value)
    }
    emit('save')
    close()
  } catch (e) {
    console.error(e)
    alert('Сақтау қатесі')
  } finally {
    isLoading.value = false
  }
}
</script>

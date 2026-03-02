<template>
  <Modal :is-open="isVisible" title="Тестті өңдеу" @close="close">
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

        <!-- Drill-down Topic/Subtheme -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Тақырып / Ішкі тақырып</label>

          <!-- Current selection display -->
          <div v-if="selectedTheme || selectedSubtheme" class="flex items-center gap-2 mb-2 text-sm">
            <span v-if="selectedTheme" class="px-2 py-1 bg-blue-100 text-blue-700 rounded flex items-center gap-1">
              {{ selectedTheme.icon || '' }} {{ selectedTheme.title }}
              <button @click="clearTheme" class="ml-1 text-blue-400 hover:text-blue-700">&times;</button>
            </span>
            <span v-if="selectedSubtheme" class="text-gray-400">→</span>
            <span v-if="selectedSubtheme" class="px-2 py-1 bg-purple-100 text-purple-700 rounded flex items-center gap-1">
              {{ selectedSubtheme.title }}
              <button @click="clearSubtheme" class="ml-1 text-purple-400 hover:text-purple-700">&times;</button>
            </span>
          </div>

          <!-- Dropdown -->
          <div class="relative">
            <button type="button" @click="dropdownOpen = !dropdownOpen"
              class="w-full text-left px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm hover:bg-gray-50 flex items-center justify-between">
              <span v-if="!selectedTheme" class="text-gray-500">Тақырыпты таңдаңыз</span>
              <span v-else-if="!selectedSubtheme" class="text-gray-500">Ішкі тақырыпты таңдаңыз</span>
              <span v-else class="text-gray-700">{{ selectedSubtheme.title }}</span>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
            </button>

            <div v-if="dropdownOpen" class="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-y-auto">
              <!-- No theme selected → show themes -->
              <template v-if="!selectedTheme">
                <button @click="form.topic_id = null; dropdownOpen = false"
                  class="w-full text-left px-3 py-2 text-sm text-gray-500 hover:bg-gray-50 border-b border-gray-100">
                  Тақырыпсыз
                </button>
                <button v-for="theme in parentThemes" :key="theme.id"
                  @click="selectTheme(theme)"
                  class="w-full text-left px-3 py-2 text-sm hover:bg-blue-50 flex items-center gap-2">
                  <span>{{ theme.icon || '📁' }}</span>
                  <span>{{ theme.title }}</span>
                  <svg v-if="getSubthemes(theme.id).length > 0" class="w-3 h-3 text-gray-400 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                </button>
              </template>

              <!-- Theme selected → show subthemes -->
              <template v-else>
                <button @click="clearTheme"
                  class="w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 border-b border-gray-100 flex items-center gap-1 font-medium">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
                  ← {{ selectedTheme.title }}
                </button>
                <button @click="selectThemeOnly"
                  class="w-full text-left px-3 py-2 text-sm text-gray-500 hover:bg-gray-50 border-b border-gray-100">
                  Ішкі тақырыпсыз (тек тақырып)
                </button>
                <button v-for="sub in currentSubthemes" :key="sub.id"
                  @click="selectSubtheme(sub)"
                  class="w-full text-left px-3 py-2 text-sm hover:bg-purple-50">
                  {{ sub.title }}
                </button>
                <div v-if="currentSubthemes.length === 0" class="px-3 py-2 text-sm text-gray-400">
                  Ішкі тақырыптар жоқ
                </div>
              </template>
            </div>
          </div>
        </div>

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
import type { SkillListItem } from '@/types/api'

interface TopicItem {
  id: number
  title: string
  icon?: string | null
  parent_id?: number | null
  order: number
}

const props = defineProps<{
  isVisible: boolean
  skill: SkillListItem | null
}>()

const emit = defineEmits(['close', 'save'])

const catalogStore = useCatalogStore()
const isLoading = ref(false)
const dropdownOpen = ref(false)

const parentThemes = computed(() =>
  catalogStore.topics.filter(t => !t.parent_id).sort((a, b) => a.order - b.order)
)

const getSubthemes = (themeId: number) =>
  catalogStore.topics.filter(t => t.parent_id === themeId).sort((a, b) => a.order - b.order)

const selectedTheme = ref<TopicItem | null>(null)
const selectedSubtheme = ref<TopicItem | null>(null)

const currentSubthemes = computed(() =>
  selectedTheme.value ? getSubthemes(selectedTheme.value.id) : []
)

const form = ref({
  grade_id: 0,
  topic_id: null as number | null,
  code: '',
  title: ''
})

// When the skill prop changes, set form + resolve theme/subtheme
watch(() => props.skill, (newSkill) => {
  if (newSkill) {
    form.value = {
      grade_id: newSkill.grade_id,
      topic_id: newSkill.topic_id || null,
      code: newSkill.code,
      title: newSkill.title
    }
    // Resolve which theme/subtheme is selected
    if (newSkill.topic_id) {
      const topic = catalogStore.topics.find(t => t.id === newSkill.topic_id)
      if (topic) {
        if (topic.parent_id) {
          // It's a subtheme
          selectedTheme.value = catalogStore.topics.find(t => t.id === topic.parent_id) as TopicItem || null
          selectedSubtheme.value = topic as TopicItem
        } else {
          // It's a theme
          selectedTheme.value = topic as TopicItem
          selectedSubtheme.value = null
        }
      } else {
        selectedTheme.value = null
        selectedSubtheme.value = null
      }
    } else {
      selectedTheme.value = null
      selectedSubtheme.value = null
    }
  }
  dropdownOpen.value = false
}, { immediate: true })

const selectTheme = (theme: TopicItem) => {
  selectedTheme.value = theme
  selectedSubtheme.value = null
  const subs = getSubthemes(theme.id)
  if (subs.length === 0) {
    // No subthemes → select theme directly
    form.value.topic_id = theme.id
    dropdownOpen.value = false
  }
  // Otherwise stay open to pick subtheme
}

const selectThemeOnly = () => {
  if (selectedTheme.value) {
    form.value.topic_id = selectedTheme.value.id
    selectedSubtheme.value = null
  }
  dropdownOpen.value = false
}

const selectSubtheme = (sub: TopicItem) => {
  selectedSubtheme.value = sub
  form.value.topic_id = sub.id
  dropdownOpen.value = false
}

const clearTheme = () => {
  selectedTheme.value = null
  selectedSubtheme.value = null
  form.value.topic_id = null
}

const clearSubtheme = () => {
  selectedSubtheme.value = null
  if (selectedTheme.value) {
    form.value.topic_id = selectedTheme.value.id
  }
}

onMounted(() => {
  if (catalogStore.grades.length === 0) catalogStore.getGrades()
  if (catalogStore.topics.length === 0) catalogStore.getTopics()
})

const close = () => {
  dropdownOpen.value = false
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
    alert('Сақтау қатесі')
  } finally {
    isLoading.value = false
  }
}
</script>

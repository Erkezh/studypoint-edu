<template>
  <div class="progress-section">
    <h2 class="section-header flex items-center gap-2">
      <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
      Прогресс
    </h2>

    <div class="progress-stats">
      <div class="progress-card">
        <span class="progress-value">{{ analyticsStore.accuracy }}%</span>
        <span class="progress-label">Дәлдік</span>
      </div>
      <div class="progress-card">
        <span class="progress-value">{{ completedTopics.length }}</span>
        <span class="progress-label">Меңгерілген дағдылар</span>
      </div>
      <div class="progress-card">
        <span class="progress-value">{{ analyticsStore.totalQuestions }}</span>
        <span class="progress-label">Жауап берілген сұрақтар</span>
      </div>
    </div>

    <div v-if="completedTopics.length > 0" class="mastered-skills">
      <h3>Меңгерілген дағдылар (SmartScore = 100)</h3>
      <div class="skills-grid">
        <div v-for="topic in completedTopics" :key="topic.skill_id" class="mastered-skill-card">
          <span class="skill-name">{{ topic.name }}</span>
          <span class="skill-score">{{ topic.best_smartscore }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'

const props = defineProps<{
  gradeFrom: number
  gradeTo: number
  skillNames: Map<number, string>
}>()

const analyticsStore = useAnalyticsStore()

const completedTopics = computed(() => {
  return analyticsStore.skills
    .filter(skill => {
      if ((skill.best_smartscore || 0) < 100) return false
      const gradeNumber = (skill as Record<string, unknown>).grade_number as number | undefined
      if (gradeNumber !== undefined) {
        return gradeNumber >= props.gradeFrom && gradeNumber <= props.gradeTo
      }
      return true
    })
    .map(skill => {
      const apiName = (skill as Record<string, unknown>).skill_name as string | undefined
      return {
        skill_id: skill.skill_id,
        name: apiName || props.skillNames.get(skill.skill_id) || `Дағды ${skill.skill_id}`,
        best_smartscore: skill.best_smartscore || 0,
        total_questions: skill.total_questions || 0,
        accuracy_percent: skill.accuracy_percent || 0,
        last_practiced: skill.last_practiced_at || '',
      }
    })
})
</script>

<style scoped>
.progress-section {
  background: white;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.progress-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.progress-card {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  padding: 24px;
  border-radius: 12px;
  text-align: center;
}

.progress-value {
  display: block;
  font-size: 36px;
  font-weight: 600;
  color: #1976d2;
}

.progress-label {
  display: block;
  font-size: 13px;
  color: #555;
  margin-top: 8px;
}

.mastered-skills h3 {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 16px;
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.mastered-skill-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #e8f5e9;
  padding: 12px 16px;
  border-radius: 8px;
}

.mastered-skill-card .skill-name {
  font-size: 14px;
  color: #333;
}

.mastered-skill-card .skill-score {
  font-size: 14px;
  font-weight: 600;
  color: #4CAF50;
}

.section-header {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>

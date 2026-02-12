<template>
  <div>
    <div class="summary-header">
      <h1 class="summary-title">ҚИЫНДЫҚТАР</h1>
      <button class="print-btn" @click="printReport">
        <svg class="print-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z" />
        </svg>
      </button>
    </div>

    <p class="trouble-subtitle" v-if="troubleSpotSkills.length > 0">Көмектесу жолдары...</p>

    <div v-if="troubleSpotSkills.length === 0" class="empty-state success">
      <span class="success-icon flex items-center justify-center">
        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
      </span>
      <p class="success-text">Керемет! Қателер жоқ!</p>
      <p class="success-subtext">Барлық сұрақтарға дұрыс жауап бердіңіз.</p>
    </div>

    <div v-else class="trouble-skills-list">
      <div v-for="skill in troubleSpotSkills" :key="skill.skillId" class="trouble-skill-card">
        <div class="trouble-skill-header">
          <span class="trouble-skill-name">{{ skill.grade }} сынып · {{ skill.skillName }}</span>
        </div>

        <div class="trouble-question-preview">
          <div class="trouble-preview-label">ҚАТЕ ЖІБЕРІЛГЕН СҰРАҚТАР</div>
          <div class="trouble-preview-carousel">
            <button class="trouble-nav-btn" @click="navigateTroubleQuestion(skill.skillId, -1)"
              :disabled="(troubleQuestionIndex[skill.skillId] || 0) <= 0">
              <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
            </button>
            <div class="trouble-question-content">
              <p class="trouble-question-text">
                {{ skill.questions[troubleQuestionIndex[skill.skillId] || 0]?.prompt || 'Сұрақ' }}
              </p>
            </div>
            <button class="trouble-nav-btn" @click="navigateTroubleQuestion(skill.skillId, 1)"
              :disabled="(troubleQuestionIndex[skill.skillId] || 0) >= skill.questions.length - 1">
              <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z"/></svg>
            </button>
          </div>
        </div>

        <div class="trouble-skill-footer">
          <div class="trouble-footer-item">
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16" class="trouble-star"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
            <span>SmartScore: <strong>{{ skill.smartscore }}</strong></span>
          </div>
          <div class="trouble-footer-item trouble-footer-warning">
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>
            <span><strong>{{ skill.missedCount }}</strong> қате жіберілген сұрақ</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'

const analyticsStore = useAnalyticsStore()

const printReport = () => {
  window.print()
}

const troubleQuestionIndex = ref<Record<number, number>>({})

const troubleSpotSkills = computed(() => {
  const questions = analyticsStore.allQuestions || []
  if (questions.length === 0) return []

  const skillInfoMap = new Map<number, { name: string; grade: number; smartscore: number }>()
  for (const s of analyticsStore.skills) {
    const rec = s as Record<string, unknown>
    skillInfoMap.set(rec.skill_id as number, {
      name: (rec.skill_name as string) || 'Белгісіз',
      grade: (rec.grade_number as number) || 0,
      smartscore: (rec.best_smartscore as number) || 0,
    })
  }

  const skillMissed = new Map<number, Array<Record<string, unknown>>>()
  for (const q of questions) {
    const rec = q as Record<string, unknown>
    if (rec.is_correct) continue
    const skillId = rec.skill_id as number
    if (!skillMissed.has(skillId)) skillMissed.set(skillId, [])
    skillMissed.get(skillId)!.push(rec)
  }

  const result = Array.from(skillMissed.entries()).map(([skillId, qs]) => {
    const info = skillInfoMap.get(skillId) || { name: 'Белгісіз', grade: 0, smartscore: 0 }
    return {
      skillId,
      skillName: info.name,
      grade: info.grade,
      smartscore: info.smartscore,
      missedCount: qs.length,
      questions: qs.map(q => ({
        prompt: (q.question_prompt as string) || '',
        userAnswer: q.user_answer,
        correctAnswer: q.correct_answer as string,
      })),
    }
  })

  result.sort((a, b) => b.missedCount - a.missedCount)
  return result
})

const navigateTroubleQuestion = (skillId: number, direction: number) => {
  const skill = troubleSpotSkills.value.find(s => s.skillId === skillId)
  if (!skill) return
  const current = troubleQuestionIndex.value[skillId] || 0
  const next = current + direction
  if (next >= 0 && next < skill.questions.length) {
    troubleQuestionIndex.value[skillId] = next
  }
}
</script>

<style scoped>
.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.summary-title {
  font-size: 28px;
  font-weight: 400;
  color: #333;
}

.print-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  color: #999;
  transition: color 0.2s;
}

.print-btn:hover {
  color: #333;
}

.print-icon {
  width: 20px;
  height: 20px;
}

.trouble-subtitle {
  font-size: 24px;
  font-weight: 300;
  color: #555;
  margin: 16px 0 28px;
}

.trouble-skills-list {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.trouble-skill-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.trouble-skill-header {
  background: #4DB6AC;
  padding: 14px 20px;
  color: white;
}

.trouble-skill-name {
  font-size: 14px;
  font-weight: 700;
}

.trouble-question-preview {
  padding: 24px 20px;
  border-bottom: 1px solid #eee;
}

.trouble-preview-label {
  font-size: 11px;
  font-weight: 700;
  color: #999;
  letter-spacing: 0.05em;
  margin-bottom: 16px;
}

.trouble-preview-carousel {
  display: flex;
  align-items: center;
  gap: 12px;
}

.trouble-nav-btn {
  width: 36px;
  height: 36px;
  border: 1px solid #e0e0e0;
  border-radius: 50%;
  background: white;
  color: #bbb;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s;
}

.trouble-nav-btn:hover:not(:disabled) {
  border-color: #999;
  color: #666;
}

.trouble-nav-btn:disabled {
  opacity: 0.3;
  cursor: default;
}

.trouble-question-content {
  flex: 1;
  text-align: center;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.trouble-question-text {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  line-height: 1.5;
}

.trouble-skill-footer {
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 14px 20px;
  border-top: 1px solid #eee;
  font-size: 13px;
  color: #666;
}

.trouble-footer-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.trouble-star {
  color: #FFB300;
}

.trouble-footer-warning svg {
  color: #FF9800;
}

.empty-state {
  text-align: center;
  padding: 48px;
  color: #888;
}

.empty-state.success {
  background: #e8f5e9;
  border-radius: 12px;
  padding: 40px;
}

.success-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.success-text {
  font-size: 18px;
  font-weight: 500;
  color: #2e7d32;
}

.success-subtext {
  font-size: 14px;
  color: #666;
  margin-top: 8px;
}
</style>

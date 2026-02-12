<template>
  <div class="questions-section">
    <h2 class="section-header flex items-center gap-2">
      <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
      Барлық сұрақтар
    </h2>

    <div v-if="analyticsStore.allQuestions.length === 0" class="empty-state">
      <p>Әзірге сұрақтар жоқ</p>
    </div>

    <div v-else class="questions-list">
      <div v-for="question in analyticsStore.allQuestions" :key="question.attempt_id"
        :class="['question-card', question.is_correct ? 'correct' : 'incorrect']">
        <div class="question-header">
          <span :class="['status-badge flex items-center gap-1', question.is_correct ? 'success' : 'error']">
            <svg v-if="question.is_correct" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
            <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            {{ question.is_correct ? 'Дұрыс' : 'Қате' }}
          </span>
          <span class="question-date">{{ formatDate(question.answered_at) }}</span>
        </div>
        <p v-if="question.question_prompt" class="question-text">{{ question.question_prompt }}</p>
        <div class="answer-row">
          <div class="answer-box">
            <span class="answer-label">Сіздің жауабыңыз:</span>
            <span class="answer-value">{{ formatAnswer(question.user_answer) }}</span>
          </div>
          <div class="answer-box correct">
            <span class="answer-label">Дұрыс жауап:</span>
            <span class="answer-value">{{ formatAnswer(question.correct_answer) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAnalyticsStore } from '@/stores/analytics'

const analyticsStore = useAnalyticsStore()

const formatDate = (dateString: string): string => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

const tryParseJson = (str: string): unknown => {
  if (!str || typeof str !== 'string') return str
  const trimmed = str.trim()
  if ((trimmed.startsWith('{') && trimmed.endsWith('}')) ||
    (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
    try {
      return JSON.parse(trimmed)
    } catch {
      return str
    }
  }
  return str
}

const formatAnswer = (answer: unknown): string => {
  if (answer === null || answer === undefined) return '-'
  if (typeof answer === 'string') {
    const parsed = tryParseJson(answer)
    if (parsed !== answer && typeof parsed === 'object') {
      return formatAnswer(parsed)
    }
    return answer || '-'
  }
  if (typeof answer === 'number') return String(answer)
  if (typeof answer === 'boolean') return answer ? 'Иә' : 'Жоқ'
  if (typeof answer === 'object' && answer !== null) {
    const obj = answer as Record<string, unknown>
    if (obj.userAnswer !== undefined) return String(obj.userAnswer)
    if (obj.correctAnswer !== undefined) return String(obj.correctAnswer)
    if (obj.value !== undefined) return String(obj.value)
    if (obj.text !== undefined) return String(obj.text)
    return JSON.stringify(answer)
  }
  return String(answer)
}
</script>

<style scoped>
.section-header {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.questions-section {
  background: white;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-card {
  border-radius: 8px;
  padding: 20px;
}

.question-card.correct {
  background: #e8f5e9;
  border: 1px solid #a5d6a7;
}

.question-card.incorrect {
  background: #ffebee;
  border: 1px solid #ef9a9a;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.status-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
}

.status-badge.success {
  background: #c8e6c9;
  color: #2e7d32;
}

.status-badge.error {
  background: #ffcdd2;
  color: #c62828;
}

.question-date {
  font-size: 12px;
  color: #888;
}

.question-text {
  font-size: 15px;
  color: #333;
  margin-bottom: 16px;
}

.answer-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.answer-box {
  background: rgba(255, 255, 255, 0.7);
  padding: 12px;
  border-radius: 8px;
}

.answer-box .answer-label {
  color: #666;
}

.answer-box .answer-value {
  color: #333;
}

.answer-box.correct .answer-label {
  color: #2e7d32;
}

.answer-box.correct .answer-value {
  color: #2e7d32;
}

.empty-state {
  text-align: center;
  padding: 48px;
  color: #888;
}
</style>

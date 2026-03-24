<template>
  <div class="skill-analysis-tab">
    <div class="summary-header">
      <h1 class="summary-title">ДАҒДЫЛАРДЫҢ ТАЛДАУЫ: {{ userName }}</h1>
      <button class="print-btn" @click="printReport">
        <svg class="print-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z" />
        </svg>
      </button>
    </div>
    
    <div class="empty-state">
      <p>Бұл бет әзірлеу үстінде...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useTeacherStore } from '@/stores/teacher'

const props = defineProps<{
  gradeFrom: number
  gradeTo: number
  dateRange: { start: Date | null; end: Date | null }
}>()

const authStore = useAuthStore()
const teacherStore = useTeacherStore()

const isTeacher = computed(() => authStore.isTeacher)

const userName = computed(() => {
  if (isTeacher.value) {
    try {
      const state = JSON.parse(localStorage.getItem('analytics_view_state') || '{}')
      if (state.selectedStudentId && teacherStore.students) {
        const student = teacherStore.students.find((s: Record<string, unknown>) => s.id === state.selectedStudentId)
        if (student) return student.full_name as string
      }
    } catch { }
  }
  return authStore.user?.full_name || 'Сіздің'
})

const printReport = () => {
  window.print()
}
</script>

<style scoped>
.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
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
}
.print-btn:hover { color: #333; }
.print-icon { width: 20px; height: 20px; }
.empty-state {
  text-align: center;
  padding: 64px;
  color: #888;
  font-size: 18px;
}
</style>

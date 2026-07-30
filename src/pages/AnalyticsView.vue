<template>
  <div class="analytics-page">
    <Header />

    <!-- IXL-style Header with Tabs -->
    <div class="analytics-header">
      <nav class="analytics-tabs scrollbar-hide">
        <div v-for="tab in tabs" :key="tab.id" class="tab-item-group"
             @mouseenter="hoverTab = tab.id" @mouseleave="hoverTab = null">
          <button @click="tab.dropdown ? (activeTab = tab.dropdown[0].id, hoverTab = null) : (activeTab = tab.id)"
            :class="['tab-item', { active: activeTab === tab.id || (tab.dropdown && tab.dropdown.some(d => d.id === activeTab)) }]">
            <span class="tab-icon">
              <svg v-if="tab.id === 'summary' && !isTeacher" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
              <svg v-else-if="tab.id === 'students_dropdown' && isTeacher" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
              <svg v-else-if="tab.id === 'usage'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <svg v-else-if="tab.id === 'skills_dropdown' || tab.id === 'skills_practiced'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" /></svg>
              <svg v-else-if="tab.id === 'trouble' || tab.id === 'trouble_dropdown'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
              <svg v-else-if="tab.id === 'scores_dropdown' || tab.id === 'scores_student'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" /></svg>
              <svg v-else-if="tab.id === 'questions'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
              <svg v-else-if="tab.id === 'progress'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
              <svg v-else-if="tab.id === 'quizzes'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
            </span>
            {{ tab.label }}
            <svg v-if="tab.dropdown" class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </button>

          <div v-if="tab.dropdown && hoverTab === tab.id" class="tab-dropdown">
            <button v-for="sub in tab.dropdown" :key="sub.id"
              @click.stop="activeTab = sub.id; hoverTab = null"
              :class="['dropdown-item', { active: activeTab === sub.id }]">
              {{ sub.label }}
            </button>
          </div>
        </div>
      </nav>
    </div>

    <div v-if="activeTab !== 'scores_grid' && activeTab !== 'scores_student' && activeTab !== 'scores_skill' && activeTab !== 'quizzes'" class="filters-bar">
      <div class="filters-bar-inner flex items-center gap-6">
        <!-- Teacher: Student Picker -->
        <!-- Teacher: Student Picker moved to content -->
        <div class="filter-group grade-range-filter">
          <label @click="toggleGradeDropdown" class="filter-label clickable">
            СЫНЫП ДЕҢГЕЙІ: {{ gradeRangeLabel }}
            <svg class="dropdown-arrow w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </label>
          <div v-if="showGradeDropdown" class="grade-dropdown-popup">
            <p class="dropdown-title">Осы сыныптардағы дағдыларды көрсету:</p>
            <div class="grade-range-selectors">
              <select v-model="gradeFrom" class="filter-select small">
                <option :value="-1">Б-а</option>
                <option :value="0">Б</option>
                <option v-for="n in 12" :key="n" :value="n">{{ n }}</option>
              </select>
              <span class="range-separator">-</span>
              <select v-model="gradeTo" class="filter-select small">
                <option :value="-1">Б-а</option>
                <option :value="0">Б</option>
                <option v-for="n in 12" :key="n" :value="n">{{ n }}</option>
              </select>
            </div>
            <button @click="applyGradeFilter" class="apply-btn">Дайын</button>
          </div>
        </div>
        <div class="filter-group date-range-filter">
          <label @click="toggleDateDropdown" class="filter-label clickable">
            УАҚЫТ АРАЛЫҒЫ: {{ dateRangeLabel }}
            <svg class="dropdown-arrow w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </label>
          <div v-if="showDateDropdown" class="date-dropdown-popup">
            <button
              v-for="option in dateOptions"
              :key="option.id"
              @click="selectDateRange(option.id)"
              :class="['date-option', { active: selectedDateOption === option.id }]"
            >
              {{ option.label }}
            </button>
          </div>
        </div>
      </div>
    </div>



    <main class="analytics-content">
      <!-- Stale Data Warning Banner -->
      <div v-if="analyticsStore.isStale" class="stale-warning-banner">
        <div class="warning-message">
          <span class="warning-icon">⚠️</span>
          <span class="warning-text">
            Соңғы сақталған деректер көрсетілуде (жаңартылған уақыты: {{ formatLastUpdated(analyticsStore.lastUpdated) }}). Желі қосылымын тексеріңіз.
          </span>
        </div>
        <button @click="refreshDataSilently" :disabled="analyticsStore.loading" class="refresh-btn">
          <span v-if="analyticsStore.loading" class="btn-spinner"></span>
          {{ analyticsStore.loading ? 'Жаңартылуда...' : 'Қазір жаңарту' }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="activeTab !== 'quizzes' && analyticsStore.loading && !analyticsStore.overview" class="loading-state">
        <div class="spinner"></div>
        <p>Жүктелуде...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="activeTab !== 'quizzes' && analyticsStore.error && !analyticsStore.overview" class="error-state">
        <p class="error-title">Талдауды жүктеу қатесі:</p>
        <p>{{ analyticsStore.error }}</p>
      </div>

      <!-- Teacher Needs Selection State -->
      <div v-else-if="isTeacher && !selectedStudentId && activeTab !== 'students_quickview' && activeTab !== 'trouble_class' && activeTab !== 'skills_practiced' && activeTab !== 'skill_analysis' && activeTab !== 'scores_grid' && activeTab !== 'scores_skill' && activeTab !== 'quizzes'" class="empty-state teacher-select-prompt">
        <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
        <h3 class="text-xl font-medium text-gray-700 mb-2">Оқушыны таңдаңыз</h3>

        <div class="student-carousel-container mt-6">
          <button @click="prevStudent" class="carousel-arrow" :disabled="teacherStudents.length === 0">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
          </button>
          <div class="carousel-select-wrapper">
            <span class="carousel-label">ОҚУШЫ:</span>
            <select v-model="selectedStudentId" @change="onStudentChange" class="carousel-select">
              <option value="" disabled>Оқушыны таңдаңыз...</option>
              <option v-for="s in teacherStudents" :key="s.id" :value="s.id">{{ s.full_name }}</option>
            </select>
          </div>
          <button @click="nextStudent" class="carousel-arrow" :disabled="teacherStudents.length === 0">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </button>
        </div>
      </div>

      <div v-else>
        <!-- Teacher Student Carousel for active views (Usage, Summary) - HIDDEN on Quickview -->
        <div v-if="isTeacher && selectedStudentId && activeTab !== 'students_quickview' && activeTab !== 'trouble_class' && activeTab !== 'skills_practiced' && activeTab !== 'skill_analysis' && activeTab !== 'scores_grid' && activeTab !== 'scores_skill' && activeTab !== 'quizzes'" class="student-carousel-container active-view-carousel">
          <button @click="prevStudent" class="carousel-arrow">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
          </button>
          <div class="carousel-select-wrapper">
            <span class="carousel-label">ОҚУШЫ:</span>
            <select v-model="selectedStudentId" @change="onStudentChange" class="carousel-select">
              <option v-for="s in teacherStudents" :key="s.id" :value="s.id">{{ s.full_name }}</option>
            </select>
          </div>
          <button @click="nextStudent" class="carousel-arrow">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </button>
        </div>
        <div v-if="activeTab === 'students_quickview'" class="quickview-tab-content">
          <div class="quickview-summary-dashboard">
            <UsageTab
              :grade-from="gradeFrom"
              :grade-to="gradeTo"
              :date-range="dateRange"
              :period="selectedDateOption"
              :accomplishments-title="accomplishmentsTitle"
              :hide-header="true"
              :hide-sessions="true"
            />
          </div>

          <!-- Per-Student Breakdown -->
          <div class="students-breakdown" v-if="displayStudentsBreakdown.length > 0">
            <div v-for="student in displayStudentsBreakdown" :key="student.student_id" class="student-card">
              <table class="student-unified-table">
                <thead>
                  <tr class="header-summary-row">
                    <td colspan="2" class="student-name-column">
                      <div class="student-avatar-grid">
                        <svg viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="currentColor"/></svg>
                      </div>
                      <span class="student-name-grid">{{ student.full_name }}</span>
                    </td>
                    <td class="stat-align-column questions">
                      <div class="align-wrapper">
                        <span class="icon-space">
                          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
                        </span>
                        {{ student.total_questions }} questions
                      </div>
                    </td>
                    <td class="stat-align-column time">
                      <div class="align-wrapper">
                        <span class="icon-space">
                          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z"/></svg>
                        </span>
                         {{ formatTimeQuickview(student.total_time_sec).replace(' мин', ' minute') }}
                      </div>
                    </td>
                    <td class="stat-align-column practiced">
                      <div class="align-wrapper">
                        <span class="icon-space">
                          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM9 10H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2z"/></svg>
                        </span>
                        Practiced {{ formatLastPracticedQuickview(student.last_practiced_at) }}
                      </div>
                    </td>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="skill in student.skills" :key="skill.skill_id" class="skill-row">
                    <td class="skill-grade-cell">{{ skill.grade_label }} ({{ skill.skill_code }})</td>
                    <td class="skill-name-cell">
                      <router-link :to="`/skill/${skill.skill_id}`" class="skill-link">{{ skill.skill_name }}</router-link>
                      <span class="skill-sub-code">{{ skill.skill_code.slice(0, 3) }}</span>
                    </td>
                    <td class="stat-align-column">
                      <div class="align-wrapper">
                        <span class="icon-space"></span>
                        {{ skill.total_questions }}
                      </div>
                    </td>
                    <td class="stat-align-column">
                      <div class="align-wrapper">
                        <span class="icon-space"></span>
                        {{ formatTimeQuickview(skill.total_time_seconds) }}
                      </div>
                    </td>
                    <td class="stat-align-column row-score">
                      <div class="align-wrapper">
                         <span class="icon-space"></span>
                         <div class="skill-score-flex">
                          <span class="score-start">0</span>
                          <div class="score-arrow-horizontal">
                            <svg viewBox="0 0 20 10" preserveAspectRatio="none"><path d="M0 5 H15 M15 5 L12 2 M15 5 L12 8" stroke="currentColor" fill="none" stroke-width="1.5"/></svg>
                          </div>
                          <div class="smartscore-bar-container">
                            <div class="smartscore-bar-bg"></div>
                            <div class="smartscore-bar-fill" :style="{ width: getSkillEffectiveScore(skill) + '%' }"></div>
                          </div>
                          <span class="score-end" :class="smartScoreColorClass(getSkillEffectiveScore(skill))">{{ getSkillEffectiveScore(skill) }}</span>
                        </div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div class="student-card-footer">
                <span class="footer-stat">
                  <svg class="footer-icon mastered" viewBox="0 0 24 24" fill="currentColor"><path d="M18 2H6c-1.1 0-2 .9-2 2v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V4c0-1.1-.9-2-2-2zm-1 14.86c-1.35-.35-2.59-.95-3.69-1.78l-.31-.24-.31.24c-1.1.83-2.34 1.43-3.69 1.78V10h8v6.86zM12 8c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"/></svg>
                  {{ student.mastered_count }} Mastered
                </span>
                <span class="footer-stat">
                  <svg class="footer-icon proficient" viewBox="0 0 24 24" fill="currentColor"><path d="M17 3H7c-1.1 0-2 .9-2 2v16l7-3 7 3V5c0-1.1-.9-2-2-2z"/></svg>
                  {{ student.proficient_count }} Proficient
                </span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>Таңдалған уақыт пен сынып аралығында оқушылардың практика мәліметтері табылмады.</p>
          </div>
        </div>

        <SummaryTab v-else-if="activeTab === 'summary'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :date-range="dateRange" :skill-names="skillNames"
          :accomplishments-title="accomplishmentsTitle" />

        <UsageTab v-else-if="activeTab === 'usage'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :date-range="dateRange" :period="selectedDateOption"
          :accomplishments-title="accomplishmentsTitle" />

        <SkillsPracticedTab v-else-if="activeTab === 'skills_practiced'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :date-range="dateRange"
          :date-label="dateRangeLabel"
          :all-students-data="displayStudentsBreakdown"
          @navigate="handleTabNavWithContext" />

        <SkillAnalysisTab v-else-if="activeTab === 'skill_analysis'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :date-range="dateRange"
          :date-label="dateRangeLabel"
          :all-students-data="displayStudentsBreakdown"
          @navigate="handleTabNavWithContext" />

        <TroubleTab v-else-if="activeTab === 'trouble' || activeTab === 'trouble_class'"
          :is-class-wide="activeTab === 'trouble_class'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :date-range="dateRange"
          :all-students-data="activeTab === 'trouble_class' ? displayStudentsBreakdown : []"
          @select-student="handleTroubleStudentSelect" />

        <ScoreGridTab v-else-if="activeTab === 'scores_grid'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :date-range="dateRange"
          :date-label="dateRangeLabel"
          :all-students-data="displayStudentsBreakdown"
          @navigate="handleTabNavWithContext" />

        <ScoresTab v-else-if="activeTab === 'scores_student'" />

        <SkillScoreChartTab v-else-if="activeTab === 'scores_skill'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :date-range="dateRange"
          :date-label="dateRangeLabel"
          :all-students-data="displayStudentsBreakdown" />

        <QuestionsTab v-else-if="activeTab === 'questions'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :date-range="dateRange" />

        <ProgressTab v-else-if="activeTab === 'progress'"
          :grade-from="gradeFrom" :grade-to="gradeTo" :skill-names="skillNames" :date-range="dateRange" />

        <QuizzesTab v-else-if="activeTab === 'quizzes'" />
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAnalyticsStore } from '@/stores/analytics'
import { useAuthStore } from '@/stores/auth'
import { useTeacherStore } from '@/stores/teacher'
import { storeToRefs } from 'pinia'
import { teacherApi } from '@/api/teacher'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import SummaryTab from '@/components/analytics/SummaryTab.vue'
import UsageTab from '@/components/analytics/UsageTab.vue'
import ScoresTab from '@/components/analytics/ScoresTab.vue'
import TroubleTab from '@/components/analytics/TroubleTab.vue'
import SkillsPracticedTab from '@/components/analytics/SkillsPracticedTab.vue'
import SkillAnalysisTab from '@/components/analytics/SkillAnalysisTab.vue'
import QuestionsTab from '@/components/analytics/QuestionsTab.vue'
import ProgressTab from '@/components/analytics/ProgressTab.vue'
import ScoreGridTab from '@/components/analytics/ScoreGridTab.vue'
import SkillScoreChartTab from '@/components/analytics/SkillScoreChartTab.vue'
import QuizzesTab from '@/components/analytics/QuizzesTab.vue'

interface SkillBreakdown {
  skill_id: number
  skill_name: string
  skill_code: string
  grade_number: number
  grade_label: string
  total_questions: number
  total_time_seconds: number
  best_smartscore: number
  last_smartscore: number
}

interface StudentBreakdown {
  student_id: string
  full_name: string
  total_questions: number
  total_time_sec: number
  last_practiced_at: string | null
  mastered_count: number
  proficient_count: number
  skills: SkillBreakdown[]
}

const analyticsStore = useAnalyticsStore()
const authStore = useAuthStore()
const teacherStore = useTeacherStore()
const { students: teacherStudents } = storeToRefs(teacherStore)

const isTeacher = computed(() => authStore.isTeacher)

/* === Local Storage Persistence === */
const SAVED_STATE_KEY = 'analytics_view_state'
const loadState = () => {
  try {
    const saved = localStorage.getItem(SAVED_STATE_KEY)
    return saved ? JSON.parse(saved) : {}
  } catch {
    return {}
  }
}
const initialState = loadState()

// Teacher student selection — only restore from localStorage if user is a teacher
const selectedStudentId = ref(initialState.selectedStudentId || '')
const studentAnalyticsLoading = ref(false)
const hoverTab = ref<string | null>(null)
const studentsBreakdown = ref<StudentBreakdown[]>([])

const displayStudentsBreakdown = computed<StudentBreakdown[]>(() => {
  if (!studentsBreakdown.value || studentsBreakdown.value.length === 0) {
    return []
  }

  const startDate = dateRange.value.start
  const endDate = dateRange.value.end || new Date()

  return studentsBreakdown.value
    .map(student => {
      // Find questions answered by this student
      const studentQuestions = (analyticsStore.allQuestions || []).filter(q => {
        const qUserId = String(q.user_id || '')
        if (qUserId !== String(student.student_id)) return false

        // Grade filter
        const skill = analyticsStore.skills.find(s => Number(s.skill_id) === Number(q.skill_id))
        const gradeNum = (skill as Record<string, unknown>)?.grade_number as number | undefined
        if (gradeNum !== undefined) {
          if (!((gradeNum >= gradeFrom.value && gradeNum <= gradeTo.value) || (gradeFrom.value === -1 && gradeTo.value === 12))) {
            return false
          }
        }

        // Date range filter
        if (startDate) {
          const ts = (q.answered_at || (q as Record<string, unknown>).created_at) as string | undefined
          if (!ts) return false
          const d = new Date(ts)
          if (d < startDate || d > endDate) return false
        }

        return true
      })

      if (!startDate) {
        // When 'all' time is selected, return student skills filtered by grade range
        const filteredSkills = student.skills.filter(s => {
          const g = s.grade_number
          if (g !== undefined) {
            return (g >= gradeFrom.value && g <= gradeTo.value) || (gradeFrom.value === -1 && gradeTo.value === 12)
          }
          return true
        })
        return {
          ...student,
          skills: filteredSkills,
        }
      }

      // When Date Filter IS ACTIVE:
      const totalQuestions = studentQuestions.length
      const totalTimeSec = studentQuestions.reduce((sum, q) => {
        return sum + Number(q.time_spent_seconds || (q as Record<string, unknown>).time_spent_sec || 0)
      }, 0)

      let lastPracticedAt: string | null = null
      if (studentQuestions.length > 0) {
        const sortedTs = studentQuestions
          .map(q => (q.answered_at || (q as Record<string, unknown>).created_at) as string)
          .filter(Boolean)
          .sort((a, b) => new Date(b).getTime() - new Date(a).getTime())
        if (sortedTs.length > 0) {
          lastPracticedAt = sortedTs[0]
        }
      }

      // Group studentQuestions by skill_id
      const skillMap = new Map<number, typeof studentQuestions>()
      studentQuestions.forEach(q => {
        const skId = Number(q.skill_id)
        if (!skillMap.has(skId)) skillMap.set(skId, [])
        skillMap.get(skId)!.push(q)
      })

      const filteredSkills: SkillBreakdown[] = []
      let masteredCount = 0
      let proficientCount = 0

      skillMap.forEach((qs, skId) => {
        const baseSkill = student.skills.find(s => Number(s.skill_id) === skId)
        const skQuestions = qs.length
        const skTime = qs.reduce((sum, q) => sum + Number(q.time_spent_seconds || (q as Record<string, unknown>).time_spent_sec || 0), 0)

        const scores = qs.map(q => Number(q.smartscore_after || q.smartscore_before || 0))
        const maxScore = scores.length > 0 ? Math.max(...scores) : (baseSkill?.best_smartscore || 0)
        const lastScore = scores.length > 0 ? scores[0] : (baseSkill?.last_smartscore || 0)

        if (maxScore >= 90) masteredCount++
        else if (maxScore >= 70) proficientCount++

        filteredSkills.push({
          skill_id: skId,
          skill_name: baseSkill?.skill_name || (qs[0] as Record<string, unknown>).skill_name as string || `Дағды ${skId}`,
          skill_code: baseSkill?.skill_code || '',
          grade_number: baseSkill?.grade_number || 0,
          grade_label: baseSkill?.grade_label || (baseSkill?.grade_number ? `${baseSkill.grade_number} сынып` : ''),
          total_questions: skQuestions,
          total_time_seconds: skTime,
          best_smartscore: maxScore,
          last_smartscore: lastScore,
        })
      })

      return {
        ...student,
        total_questions: totalQuestions,
        total_time_sec: totalTimeSec,
        last_practiced_at: lastPracticedAt,
        mastered_count: masteredCount,
        proficient_count: proficientCount,
        skills: filteredSkills,
      }
    })
    .filter(student => {
      if (startDate) {
        return student.total_questions > 0
      }
      return true
    })
})

// Carousel Logic
const prevStudent = () => {
  if (teacherStudents.value.length === 0) return
  const currentIndex = teacherStudents.value.findIndex((s: { id: string }) => s.id === selectedStudentId.value)
  if (currentIndex <= 0) {
    // Wrap to end or stay at 0
    selectedStudentId.value = teacherStudents.value[teacherStudents.value.length - 1].id
  } else {
    selectedStudentId.value = teacherStudents.value[currentIndex - 1].id
  }
  onStudentChange()
}

const nextStudent = () => {
  if (teacherStudents.value.length === 0) return
  const currentIndex = teacherStudents.value.findIndex((s: { id: string }) => s.id === selectedStudentId.value)
  if (currentIndex === -1 || currentIndex === teacherStudents.value.length - 1) {
    // Wrap to start
    selectedStudentId.value = teacherStudents.value[0].id
  } else {
    selectedStudentId.value = teacherStudents.value[currentIndex + 1].id
  }
  onStudentChange()
}

const tabsThatNeedQuestionData = new Set([
  'usage',
  'summary',
  'trouble',
  'trouble_class',
  'questions',
  'progress',
  'students_quickview',
  'skills_practiced',
  'skill_analysis',
  'scores_grid',
  'scores_student',
  'scores_skill'
])
const ownQuestionsLoaded = ref(false)
const quickviewQuestionsLoaded = ref(false)
const quickviewQuestionsLoading = ref(false)
let teacherQuickviewRequestVersion = 0

const shouldLoadQuestionData = () => {
  return tabsThatNeedQuestionData.has(activeTab.value) || selectedDateOption.value !== 'all'
}

const formatTimeQuickview = (seconds: unknown): string => {
  const sec = Number(seconds) || 0
  if (sec === 0) return '<1 мин'
  const mins = Math.floor(sec / 60)
  if (mins < 1) return '<1 мин'
  if (mins >= 60) {
    const hrs = Math.floor(mins / 60)
    const rem = mins % 60
    return rem > 0 ? `${hrs} сағ ${rem} мин` : `${hrs} сағ`
  }
  return `${mins} мин`
}

const formatLastPracticedQuickview = (dateStr: unknown): string => {
  if (!dateStr) return ''
  const date = new Date(String(dateStr))
  const now = new Date()
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
  if (diffDays === 0) return 'today'
  if (diffDays === 1) return 'yesterday'
  return `${diffDays} days ago`
}

const getSkillEffectiveScore = (skill: { best_smartscore?: number; last_smartscore?: number } | null | undefined): number => {
  if (!skill) return 0
  return Math.max(Number(skill.best_smartscore || 0), Number(skill.last_smartscore || 0))
}

const smartScoreColorClass = (score: unknown): string => {
  const s = Number(score) || 0
  if (s >= 100) return 'score-mastered'
  if (s >= 80) return 'score-proficient'
  if (s >= 50) return 'score-medium'
  return 'score-low'
}

// Load own analytics (for any user)
const loadOwnAnalytics = async (includeQuestions = shouldLoadQuestionData()) => {
  analyticsStore.loading = true
  try {
    const requests: Promise<unknown>[] = [
      analyticsStore.getOverview(true),
      analyticsStore.getSkills(true),
    ]

    if (includeQuestions) {
      requests.push(analyticsStore.getAllQuestions(true))
    } else {
      analyticsStore.allQuestions = []
    }

    await Promise.all(requests)
    ownQuestionsLoaded.value = includeQuestions
  } finally {
    analyticsStore.loading = false
  }
}

const loadTeacherQuickviewQuestions = async (requestVersion = teacherQuickviewRequestVersion) => {
  quickviewQuestionsLoading.value = true
  try {
    const resp = await teacherApi.getTeacherQuickviewQuestions()
    if (requestVersion !== teacherQuickviewRequestVersion || (activeTab.value !== 'students_quickview' && activeTab.value !== 'trouble_class' && activeTab.value !== 'skills_practiced' && activeTab.value !== 'skill_analysis')) {
      return
    }
    const rawData = resp.data as unknown
    const qList = Array.isArray(rawData) ? rawData : (Array.isArray((rawData as { data?: unknown })?.data) ? (rawData as { data: Array<Record<string, unknown>> }).data : [])
    if (qList.length > 0) {
      analyticsStore.allQuestions = qList as typeof analyticsStore.allQuestions
    }
    quickviewQuestionsLoaded.value = true
  } catch (err) {
    if (requestVersion !== teacherQuickviewRequestVersion) {
      return
    }
    quickviewQuestionsLoaded.value = false
    if (import.meta.env.DEV) {
      console.error('Failed to load teacher quickview question log:', err)
    }
  } finally {
    if (requestVersion === teacherQuickviewRequestVersion) {
      quickviewQuestionsLoading.value = false
    }
  }
}

const loadTeacherQuickviewAnalytics = async () => {
  const requestVersion = ++teacherQuickviewRequestVersion
  analyticsStore.loading = true
  analyticsStore.isStale = false
  studentAnalyticsLoading.value = true
  quickviewQuestionsLoaded.value = false
  quickviewQuestionsLoading.value = false
  try {
    const resp = await teacherApi.getTeacherQuickviewAnalytics(true)
    if (requestVersion !== teacherQuickviewRequestVersion) {
      return
    }
    const data = resp.data.data as { overview: Record<string, unknown>; skills: Array<Record<string, unknown>>; all_questions?: Array<Record<string, unknown>>; students_breakdown?: Array<Record<string, unknown>> }
    analyticsStore.overview = data.overview as typeof analyticsStore.overview
    analyticsStore.skills = (data.skills || []) as typeof analyticsStore.skills
    if (data.all_questions && data.all_questions.length > 0) {
      analyticsStore.allQuestions = data.all_questions as typeof analyticsStore.allQuestions
      quickviewQuestionsLoaded.value = true
    }
    studentsBreakdown.value = (data.students_breakdown || []) as unknown as StudentBreakdown[]
    analyticsStore.error = null
  } catch (err: unknown) {
    if (requestVersion !== teacherQuickviewRequestVersion) {
      return
    }
    const e = err as { response?: { data?: { message?: string } } }
    analyticsStore.error = e.response?.data?.message || 'Оқушылардың жалпы аналитикасын жүктеу мүмкін болмады'
    return
  } finally {
    if (requestVersion === teacherQuickviewRequestVersion) {
      analyticsStore.loading = false
      studentAnalyticsLoading.value = false
    }
  }

  if (requestVersion === teacherQuickviewRequestVersion && shouldLoadQuestionData() && !quickviewQuestionsLoaded.value) {
    void loadTeacherQuickviewQuestions(requestVersion)
  }
}

const handleTroubleStudentSelect = (studentId: string) => {
  selectedStudentId.value = studentId
  activeTab.value = 'trouble'
}

const handleTabNavWithContext = (route: string, context?: Record<string, unknown>) => {
  activeTab.value = route
  if (route === 'questions' && context?.studentId) {
    selectedStudentId.value = String(context.studentId)
    onStudentChange()
  } else if (route === 'trouble_class') {
    selectedStudentId.value = ''
    onStudentChange()
  }
}

const onStudentChange = async () => {
  if (!selectedStudentId.value || !isTeacher.value) {
    selectedStudentId.value = ''
    if (isTeacher.value && (activeTab.value === 'students_quickview' || activeTab.value === 'trouble_class' || activeTab.value === 'skills_practiced' || activeTab.value === 'skill_analysis' || activeTab.value === 'scores_grid' || activeTab.value === 'scores_skill')) {
      await loadTeacherQuickviewAnalytics()
    } else {
      await loadOwnAnalytics()
    }
    return
  }

  // Teacher selected a specific student
  studentAnalyticsLoading.value = true
  analyticsStore.loading = true
  analyticsStore.isStale = false
  try {
    const includeQuestions = shouldLoadQuestionData()
    const resp = await teacherApi.getStudentAnalytics(selectedStudentId.value, includeQuestions)
    const data = resp.data.data as { overview: Record<string, unknown>; skills: Array<Record<string, unknown>>; all_questions: Array<Record<string, unknown>> }
    // Inject student data into the shared store so all tabs use it
    analyticsStore.overview = data.overview as typeof analyticsStore.overview
    analyticsStore.skills = (data.skills || []) as typeof analyticsStore.skills
    analyticsStore.allQuestions = (includeQuestions ? (data.all_questions || []) : []) as typeof analyticsStore.allQuestions
    analyticsStore.error = null
  } catch (err: unknown) {
    const e = err as { response?: { data?: { message?: string } } }
    analyticsStore.error = e.response?.data?.message || 'Оқушы аналитикасын жүктеу мүмкін болмады'
  } finally {
    analyticsStore.loading = false
    studentAnalyticsLoading.value = false
  }
}


interface TabItem {
  id: string
  label: string
  dropdown?: { id: string; label: string }[]
}

const showQuizzesTab = computed(() => {
  if (isTeacher.value) {
    return true
  }

  // Student accounts created by a teacher have teacher_id set
  // Student accounts created by a parent have parent_id set (and no teacher_id)
  const isTeacherCreatedStudent = !!authStore.user?.teacher_id
  const isParentCreatedStudent = !!authStore.user?.parent_id && !authStore.user?.teacher_id

  if (isParentCreatedStudent) {
    return false
  }

  return isTeacherCreatedStudent
})

// Tab configuration
const tabs = computed<TabItem[]>(() => {
  if (isTeacher.value) {
    const teacherTabs: TabItem[] = [
      {
        id: 'students_dropdown',
        label: 'Оқушылар',
        dropdown: [
          { id: 'students_quickview', label: 'Оқушылардың қысқаша көрінісі' },
          { id: 'usage', label: 'Оқушының қолдануы' },
          { id: 'summary', label: 'Оқушының қорытындысы' },
        ]
      },
      {
        id: 'trouble_dropdown',
        label: 'Қиындықтар',
        dropdown: [
          { id: 'trouble_class', label: 'Жалпы қиындықтар' },
          { id: 'trouble', label: 'Оқушы бойынша қиындықтар' },
        ]
      },
      {
        id: 'skills_dropdown',
        label: 'Дағдылар',
        dropdown: [
          { id: 'skills_practiced', label: 'Орындалған дағдылар' },
          { id: 'skill_analysis', label: 'Дағдылардың талдауы' },
        ]
      },
      {
        id: 'scores_dropdown',
        label: 'Ұпайлар',
        dropdown: [
          { id: 'scores_grid', label: 'Ұпай торы' },
          { id: 'scores_student', label: 'Оқушы ұпайлары' },
          { id: 'scores_skill', label: 'Дағды ұпайлары' },
        ]
      },
      { id: 'questions', label: 'Сұрақтар' },
      { id: 'progress', label: 'Прогресс' },
    ]
    if (showQuizzesTab.value) {
      teacherTabs.push({ id: 'quizzes', label: 'Квиздер' })
    }
    return teacherTabs
  }

  const userTabs: TabItem[] = [
    { id: 'summary', label: 'Қорытынды' },
    { id: 'usage', label: 'Қолдану' },
    { id: 'trouble', label: 'Қиындықтар' },
    { id: 'scores_student', label: 'Ұпайлар' },
    { id: 'questions', label: 'Сұрақтар' },
    { id: 'progress', label: 'Прогресс' },
  ]
  if (showQuizzesTab.value) {
    userTabs.push({ id: 'quizzes', label: 'Квиздер' })
  }
  return userTabs
})

const route = useRoute()
const router = useRouter()

const tabToSlugMap: Record<string, string> = {
  summary: 'summary',
  students_quickview: 'students-quickview',
  usage: 'student-usage',
  skills_practiced: 'skills-practiced',
  skill_analysis: 'skill-analysis',
  trouble: 'trouble-spots',
  trouble_class: 'class-trouble-spots',
  scores_grid: 'score-grid',
  scores_student: 'scores-student',
  scores_skill: 'scores-skill',
  questions: 'questions-log',
  progress: 'progress',
  quizzes: 'quizzes',
}

const slugToTabMap: Record<string, string> = {
  'summary': 'summary',
  'students-quickview': 'students_quickview',
  'students_quickview': 'students_quickview',
  'student-usage': 'usage',
  'usage': 'usage',
  'skills-practiced': 'skills_practiced',
  'skills_practiced': 'skills_practiced',
  'skill-analysis': 'skill_analysis',
  'skill_analysis': 'skill_analysis',
  'trouble-spots': 'trouble',
  'trouble': 'trouble',
  'class-trouble-spots': 'trouble_class',
  'trouble_class': 'trouble_class',
  'score-grid': 'scores_grid',
  'scores-grid': 'scores_grid',
  'scores_grid': 'scores_grid',
  'scores-student': 'scores_student',
  'scores_student': 'scores_student',
  'scores-skill': 'scores_skill',
  'scores_skill': 'scores_skill',
  'questions-log': 'questions',
  'questions': 'questions',
  'progress': 'progress',
  'quizzes': 'quizzes',
}

const defaultTeacherTab = 'students_quickview'

const resolveTabFromRoute = (tabParam?: string, queryTab?: string): string => {
  const raw = tabParam || queryTab
  if (raw && slugToTabMap[raw]) {
    return slugToTabMap[raw]
  }
  if (initialState.activeTab && slugToTabMap[initialState.activeTab]) {
    return slugToTabMap[initialState.activeTab]
  }
  return isTeacher.value ? defaultTeacherTab : 'summary'
}

const initialActiveTab = resolveTabFromRoute(route.params.tab as string, route.query.tab as string)
const activeTab = ref<string>(initialActiveTab === 'quizzes' && !showQuizzesTab.value ? (isTeacher.value ? defaultTeacherTab : 'summary') : initialActiveTab)

watch(
  () => [route.params.tab, route.query.tab],
  ([newParam, newQuery]) => {
    const resolved = resolveTabFromRoute(newParam as string, newQuery as string)
    if (resolved && activeTab.value !== resolved) {
      if (resolved === 'quizzes' && !showQuizzesTab.value) return
      activeTab.value = resolved
    }
  }
)

const analyticsTabTitleMap: Record<string, string> = {
  summary: 'Қорытынды',
  students_quickview: 'Қысқаша көрініс',
  usage: 'Оқу уақыты',
  skills_practiced: 'Орындалған дағдылар',
  skill_analysis: 'Дағдылар талдауы',
  trouble: 'Қиындықтар',
  trouble_class: 'Сынып қиындықтары',
  scores_grid: 'Ұпай торы',
  scores_student: 'Ұпайлар',
  scores_skill: 'Дағды ұпайлары',
  questions: 'Сұрақтар журналы',
  progress: 'Прогресс',
  quizzes: 'Квиздер',
}

watch(
  activeTab,
  (newTab) => {
    const slug = tabToSlugMap[newTab] || newTab
    const currentParam = route.params.tab as string
    if (currentParam !== slug) {
      router.push({ path: `/analytics/${slug}`, query: route.query })
    }
    if (analyticsTabTitleMap[newTab]) {
      document.title = analyticsTabTitleMap[newTab]
    }
  },
  { immediate: true }
)
const gradeFrom = ref<number>(initialState.gradeFrom !== undefined ? initialState.gradeFrom : -1)
const gradeTo = ref<number>(initialState.gradeTo !== undefined ? initialState.gradeTo : 12)
const showGradeDropdown = ref<boolean>(false)
const skillNames = computed(() => {
  return new Map(
    analyticsStore.skills.map(skill => [
      Number(skill.skill_id),
      (skill as Record<string, unknown>).skill_name as string || `Дағды ${skill.skill_id}`,
    ])
  )
})

// Grade range label for display
const gradeRangeLabel = computed(() => {
  const formatGrade = (g: number) => g === -1 ? 'Б-а' : g === 0 ? 'Б' : g
  if (gradeFrom.value === -1 && gradeTo.value === 12) {
    return 'Барлық сыныптар'
  }
  if (gradeFrom.value === gradeTo.value) {
    if (gradeFrom.value === -1) return 'Б-а (Балабақша алды)'
    if (gradeFrom.value === 0) return 'Б (Балабақша)'
    return `${formatGrade(gradeFrom.value)} сынып`
  }
  return `${formatGrade(gradeFrom.value)} - ${formatGrade(gradeTo.value)} сынып`
})

const toggleGradeDropdown = () => {
  showGradeDropdown.value = !showGradeDropdown.value
}

const applyGradeFilter = () => {
  if (gradeFrom.value > gradeTo.value) {
    const temp = gradeFrom.value
    gradeFrom.value = gradeTo.value
    gradeTo.value = temp
  }
  showGradeDropdown.value = false
}

// Date Range Logic
const dateRangeLabel = ref<string>('Барлық уақыт')
const showDateDropdown = ref<boolean>(false)
const selectedDateOption = ref<string>(initialState.selectedDateOption || 'last7')

const dateRange = ref<{ start: Date | null; end: Date | null }>({
  start: null,
  end: null
})

const dateOptions = [
  { id: 'today', label: 'Бүгін' },
  { id: 'yesterday', label: 'Кеше' },
  { id: 'week', label: 'Осы апта' },
  { id: 'last7', label: 'Соңғы 7 күн' },
  { id: 'month', label: 'Осы ай' },
  { id: 'last30', label: 'Соңғы 30 күн' },
  { id: 'year', label: 'Осы оқу жылы' },
  { id: 'all', label: 'Барлық уақыт' },
]

// Dynamic accomplishments title based on student name + time period
const accomplishmentsTitle = computed(() => {
  // Determine the subject name
  let subjectName = ''
  if (isTeacher.value) {
    if (activeTab.value === 'students_quickview' || activeTab.value === 'trouble_class' || !selectedStudentId.value) {
      subjectName = 'оқушыларыңыз'
    } else {
      const student = teacherStudents.value.find((s: { id: string }) => s.id === selectedStudentId.value)
      subjectName = student ? (student as { full_name: string }).full_name : ''
    }
  } else {
    subjectName = authStore.user?.full_name || ''
  }

  // Determine the period phrase
  const periodOption = dateOptions.find(o => o.id === selectedDateOption.value)
  const periodLabel = periodOption ? periodOption.label.toLowerCase() : ''

  if (selectedDateOption.value === 'all') {
    // "Нұрсәт — StudyPoint жетістіктері" or "Оқушыларыңыздың StudyPoint жетістіктері"
    if (isTeacher.value && (activeTab.value === 'students_quickview' || activeTab.value === 'trouble_class' || !selectedStudentId.value)) {
      return 'Оқушыларыңыздың StudyPoint жетістіктері'
    }
    return `${subjectName} — StudyPoint жетістіктері`
  }

  // "Соңғы 30 күн ішінде Нұрсәт..." or "Соңғы 30 күн ішінде оқушыларыңыз..."
  const capitalPeriod = periodLabel.charAt(0).toUpperCase() + periodLabel.slice(1)
  return `${capitalPeriod} ішінде ${subjectName}...`
})

const toggleDateDropdown = () => {
  showDateDropdown.value = !showDateDropdown.value
}

const selectDateRange = (optionId: string) => {
  selectedDateOption.value = optionId
  const option = dateOptions.find(o => o.id === optionId)
  dateRangeLabel.value = option ? option.label : 'Теңшелетін'
  showDateDropdown.value = false

  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())

  switch (optionId) {
    case 'today':
      dateRange.value = { start: today, end: new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59) }
      break
    case 'yesterday':
      const yesterday = new Date(today)
      yesterday.setDate(yesterday.getDate() - 1)
      const yesterdayEnd = new Date(yesterday)
      yesterdayEnd.setHours(23, 59, 59)
      dateRange.value = { start: yesterday, end: yesterdayEnd }
      break
    case 'week':
      // This week (starting Monday)
      const day = today.getDay() || 7 // 1 (Mon) to 7 (Sun)
      const monday = new Date(today)
      monday.setHours(0, 0, 0, 0)
      monday.setDate(monday.getDate() - day + 1)
      dateRange.value = { start: monday, end: new Date() }
      break
    case 'last7':
      const last7 = new Date(today)
      last7.setDate(last7.getDate() - 6)
      dateRange.value = { start: last7, end: new Date() }
      break
    case 'month':
      const firstDayMonth = new Date(today.getFullYear(), today.getMonth(), 1)
      dateRange.value = { start: firstDayMonth, end: new Date() }
      break
    case 'last30':
      const last30 = new Date(today)
      last30.setDate(last30.getDate() - 29)
      dateRange.value = { start: last30, end: new Date() }
      break
    case 'year':
      // Academic year: Sep 1 – Jun 30
      // If current month < September (0-indexed: 8), academic year started last year
      const academicYearStart = today.getMonth() < 8
        ? new Date(today.getFullYear() - 1, 8, 1)  // Sep 1 of previous year
        : new Date(today.getFullYear(), 8, 1)       // Sep 1 of current year
      dateRange.value = { start: academicYearStart, end: new Date() }
      break
    case 'all':
    default:
      dateRange.value = { start: null, end: null }
      break
  }
}

// Watch state changes and save to local storage
watch(
  [activeTab, gradeFrom, gradeTo, selectedDateOption, selectedStudentId],
  () => {
    localStorage.setItem(SAVED_STATE_KEY, JSON.stringify({
      activeTab: activeTab.value,
      gradeFrom: gradeFrom.value,
      gradeTo: gradeTo.value,
      selectedDateOption: selectedDateOption.value,
      selectedStudentId: selectedStudentId.value
    }))
  },
  { deep: true }
)

// Automatically load quickview data when returning to the quickview tab,
// or auto-select first student when switching to a student-specific tab
watch(activeTab, async (newVal) => {
  if (isTeacher.value && (newVal === 'students_quickview' || newVal === 'trouble_class')) {
    selectedStudentId.value = ''
    await loadTeacherQuickviewAnalytics()
    return
  }

  if (isTeacher.value && (newVal === 'skills_practiced' || newVal === 'skill_analysis' || newVal === 'scores_grid' || newVal === 'scores_skill')) {
    selectedStudentId.value = ''
    // Only fetch if we don't already have the class-wide data
    if (studentsBreakdown.value.length === 0) {
      await loadTeacherQuickviewAnalytics()
    }
    return
  }

  // Quizzes tab is self-contained — no analytics data needed
  if (newVal === 'quizzes') {
    return
  }

  if (isTeacher.value && selectedStudentId.value && shouldLoadQuestionData() && analyticsStore.allQuestions.length === 0) {
    await onStudentChange()
    return
  }

  if (isTeacher.value && newVal !== 'students_quickview' && newVal !== 'trouble_class' && newVal !== 'skills_practiced' && newVal !== 'skill_analysis' && newVal !== 'scores_grid' && newVal !== 'scores_skill' && newVal !== 'quizzes' && !selectedStudentId.value && teacherStudents.value.length > 0) {
    selectedStudentId.value = teacherStudents.value[0].id
    await onStudentChange()
    return
  }

  if (!isTeacher.value && shouldLoadQuestionData() && !ownQuestionsLoaded.value) {
    analyticsStore.loading = true
    try {
      await analyticsStore.getAllQuestions(true)
      ownQuestionsLoaded.value = true
    } finally {
      analyticsStore.loading = false
    }
  }
})

watch(selectedDateOption, async () => {
  if (isTeacher.value && (activeTab.value === 'students_quickview' || activeTab.value === 'trouble_class') && !quickviewQuestionsLoaded.value && !quickviewQuestionsLoading.value) {
    void loadTeacherQuickviewQuestions(teacherQuickviewRequestVersion)
    return
  }

  if (isTeacher.value && selectedStudentId.value && shouldLoadQuestionData() && analyticsStore.allQuestions.length === 0) {
    await onStudentChange()
    return
  }

  if (!isTeacher.value && shouldLoadQuestionData() && !ownQuestionsLoaded.value) {
    analyticsStore.loading = true
    try {
      await analyticsStore.getAllQuestions(true)
      ownQuestionsLoaded.value = true
    } finally {
      analyticsStore.loading = false
    }
  }
})

const formatLastUpdated = (timestamp: number | null): string => {
  if (!timestamp) return 'белгісіз уақыт'
  const date = new Date(timestamp)
  return date.toLocaleTimeString() + ' ' + date.toLocaleDateString()
}

const refreshDataSilently = async () => {
  try {
    if (isTeacher.value && selectedStudentId.value && activeTab.value !== 'students_quickview' && activeTab.value !== 'trouble_class' && activeTab.value !== 'skills_practiced' && activeTab.value !== 'skill_analysis' && activeTab.value !== 'scores_grid' && activeTab.value !== 'scores_skill') {
      await onStudentChange()
    } else if (isTeacher.value && (activeTab.value === 'students_quickview' || activeTab.value === 'trouble_class' || activeTab.value === 'skills_practiced' || activeTab.value === 'skill_analysis' || activeTab.value === 'scores_grid' || activeTab.value === 'scores_skill')) {
      await loadTeacherQuickviewAnalytics()
    } else {
      await loadOwnAnalytics(true)
    }
  } catch (err) {
    console.error('Failed to manually refresh analytics:', err)
  }
}

onMounted(async () => {
  // Initialize date range from saved state
  selectDateRange(selectedDateOption.value)

  // If teacher, load student list for the picker
  if (isTeacher.value && teacherStudents.value.length === 0) {
    await teacherStore.fetchStudents()
  }

  // Auto-select first student if teacher has no student selected and not on quickview
  if (isTeacher.value && !selectedStudentId.value && activeTab.value !== 'students_quickview' && activeTab.value !== 'trouble_class' && activeTab.value !== 'skills_practiced' && activeTab.value !== 'skill_analysis' && activeTab.value !== 'scores_grid' && activeTab.value !== 'scores_skill' && activeTab.value !== 'quizzes' && teacherStudents.value.length > 0) {
    selectedStudentId.value = teacherStudents.value[0].id
  }

  try {
    if (isTeacher.value && selectedStudentId.value && activeTab.value !== 'students_quickview' && activeTab.value !== 'trouble_class' && activeTab.value !== 'skills_practiced' && activeTab.value !== 'skill_analysis' && activeTab.value !== 'scores_grid' && activeTab.value !== 'scores_skill' && activeTab.value !== 'quizzes') {
      // Teacher has a student selected and specific tab — load that student's data
      await onStudentChange()
    } else if (isTeacher.value && (activeTab.value === 'students_quickview' || activeTab.value === 'trouble_class' || activeTab.value === 'skills_practiced' || activeTab.value === 'skill_analysis' || activeTab.value === 'scores_grid' || activeTab.value === 'scores_skill')) {
      // Teacher is on class-wide page - load aggregate data
      await loadTeacherQuickviewAnalytics()
    } else if (activeTab.value === 'quizzes') {
      // Quizzes tab is self-contained — QuizzesTab component loads its own data
      // No analytics loading needed
    } else {
      // Student or teacher with no selection — load own data
      await loadOwnAnalytics()
    }
  } catch (err) {
    console.error('Failed to load analytics:', err)
  }
})
</script>

<style scoped>
.analytics-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* Header & Tabs */
.analytics-header {
  background: linear-gradient(135deg, #00BCD4 0%, #00ACC1 100%);
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.analytics-tabs {
  display: flex;
  gap: 0;
  max-width: 1200px;
  margin: 0 auto;
  overflow: visible;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 24px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  border-bottom: 3px solid transparent;
}

.tab-item:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.tab-item.active {
  color: white;
  background: rgba(255, 255, 255, 0.15);
  border-bottom-color: white;
}

.tab-icon {
  font-size: 16px;
}

/* Student Options Carousel */
.student-carousel-container {
  display: flex;
  align-items: center;
  gap: 16px;
  max-width: fit-content;
}

.student-carousel-container.mt-6 {
  margin-top: 24px;
  justify-content: center;
  margin-left: auto;
  margin-right: auto;
}

.active-view-carousel {
  margin-bottom: 24px;
}

.carousel-arrow {
  background: transparent;
  border: none;
  color: #00BCD4;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.carousel-arrow:hover:not(:disabled) {
  background-color: #e0f7fa;
}

.carousel-arrow:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.carousel-select-wrapper {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 16px;
  gap: 8px;
}

.carousel-label {
  font-size: 12px;
  font-weight: 700;
  color: #888;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.carousel-select {
  border: none;
  background: transparent;
  font-size: 16px;
  color: #555;
  font-weight: 500;
  cursor: pointer;
  outline: none;
  min-width: 250px;
  appearance: none;
  padding-right: 24px;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%22%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23999%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.4-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right center;
  background-size: 12px auto;
}

.carousel-select:hover {
  text-decoration: underline;
}

/* Quickview Styles */
.quickview-tab-content {
  padding: 0;
}

.quickview-container {
  padding: 24px 0;
}

.quickview-student-select {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 4px;
  gap: 12px;
}

.quickview-select-label {
  font-size: 14px;
  color: #888;
  font-style: italic;
}

.quickview-select {
  border: none;
  background: transparent;
  font-size: 14px;
  color: #333;
  font-weight: 500;
  cursor: pointer;
  outline: none;
  min-width: 200px;
  appearance: none;
  padding-right: 24px;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%22%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23999%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.4-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right center;
  background-size: 12px auto;
}

.print-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  color: #999;
  transition: color 0.2s;
  display: flex;
  align-items: center;
}

.print-btn:hover {
  color: #333;
}

.print-icon {
  width: 20px;
  height: 20px;
}

/* Filters */
.filters-bar {
  display: flex;
  gap: 24px;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  max-width: 1200px;
  margin: 0 auto;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
}

.filter-select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  background: white;
  cursor: pointer;
}

.filter-select.small {
  padding: 8px 16px;
  min-width: 70px;
}

/* Grade Range Filter */
.grade-range-filter {
  position: relative;
}

.filter-label.clickable {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  color: #00AEEF;
  font-weight: 600;
}

.filter-label.clickable:hover {
  background: #f5f5f5;
}

.dropdown-arrow {
  font-size: 10px;
  color: #666;
}

.grade-dropdown-popup {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 16px;
  z-index: 100;
  min-width: 240px;
  margin-top: 4px;
}

.dropdown-title {
  font-size: 13px;
  color: #666;
  margin: 0 0 12px 0;
}

.grade-range-selectors {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.range-separator {
  font-size: 16px;
  color: #666;
}

.apply-btn {
  display: block;
  width: 100%;
  padding: 8px 16px;
  background: transparent;
  color: #00ACC1;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
}

.apply-btn:hover {
  color: #00838F;
}

/* Content */
.analytics-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* Loading & Error */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e0e0e0;
  border-top-color: #00BCD4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-state {
  background: #ffebee;
  border: 1px solid #f44336;
  border-radius: 8px;
  padding: 20px;
  color: #c62828;
}

.error-title {
  font-weight: 600;
  margin-bottom: 8px;
}

/* Date Range Filter */
.date-range-filter {
  position: relative;
}

.date-dropdown-popup {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 8px 0;
  z-index: 100;
  min-width: 200px;
  margin-top: 4px;
}

.date-option {
  display: block;
  width: 100%;
  text-align: left;
  padding: 10px 16px;
  background: transparent;
  border: none;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: background-color 0.1s;
}

.date-option:hover {
  background-color: #f5f5f5;
}

.date-option.active {
  color: #00ACC1;
  background-color: #e0f7fa;
  font-weight: 500;
}

.date-option.custom {
  border-top: 1px solid #eee;
  margin-top: 4px;
  padding-top: 12px;
}

/* Dropdown Menu */
.tab-item-group {
  position: relative;
  display: flex;
}

.tab-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  min-width: 240px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  border-radius: 0 0 8px 8px;
  overflow: hidden;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  border: 1px solid #eee;
  border-top: none;
}

.dropdown-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 14px 20px;
  border: none;
  background: white;
  color: #555;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.dropdown-item:hover {
  background: #f8f9fa;
  color: #333;
}

.dropdown-item.active {
  background: #e0f7fa;
  color: #00838F;
  border-left: 3px solid #00ACC1;
  padding-left: 17px;
}

/* Quickview Styles */
.quickview-tab-content {
  padding: 0;
}

.quickview-summary-dashboard {
  margin-bottom: 40px;
}

/* Students Breakdown */
.students-breakdown {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 24px;
}

.student-card {
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.student-unified-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

/* Header Row Styling */
.header-summary-row {
  background: #fafafa;
  border-bottom: 1px solid #e0e6ed;
  height: 48px;
}

.student-name-column {
  padding: 8px 16px;
  vertical-align: middle;
}

.student-avatar-grid {
  display: inline-flex;
  width: 28px;
  height: 28px;
  background: #8CBA3D;
  color: white;
  border-radius: 50%;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  vertical-align: middle;
}

.student-avatar-grid svg {
  width: 16px;
  height: 16px;
}

.student-name-grid {
  font-size: 15px;
  font-weight: 600;
  color: #039BE5;
  vertical-align: middle;
}

/* Common cell alignment logic */
.align-wrapper {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.icon-space {
  display: inline-flex;
  width: 24px; /* Matches the space taken by icons for perfect stacking */
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 6px;
}

.icon-space svg {
  width: 16px;
  height: 16px;
}

.stat-align-column {
  padding: 8px 16px;
  font-size: 12px;
  color: #666;
  text-align: left;
  vertical-align: middle;
}

.stat-align-column.questions { width: 100px; color: #8CBA3D; }
.stat-align-column.time { width: 120px; color: #00B0FF; }
.stat-align-column.practiced { width: 220px; color: #5C6BC0; }

.skill-row {
  border-bottom: 1px solid #f0f0f0;
}

.skill-row:nth-child(even) {
  background: #f9f9f9;
}

.skill-row td {
  padding: 10px 16px;
  font-size: 13px;
  color: #444;
  vertical-align: middle;
}

.skill-grade-cell {
  width: 120px;
  color: #717171;
  font-weight: 500;
}

.skill-name-cell {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.skill-link {
  color: #333;
  text-decoration: none;
}

.skill-link:hover { text-decoration: underline; color: #00838F; }

.skill-sub-code {
  color: #cfd8dc;
  font-size: 11px;
  margin-left: 8px;
  text-transform: uppercase;
}

.skill-score-flex {
  display: flex !important;
  align-items: center;
  justify-content: flex-start;
  gap: 10px;
}

.score-arrow-horizontal {
  color: #8CBA3D;
  width: 25px;
  display: flex;
  align-items: center;
}

.score-arrow-horizontal svg {
  width: 100%;
  height: 8px;
}

.smartscore-bar-container {
  position: relative;
  width: 60px;
  height: 3px;
}

.smartscore-bar-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #eee;
  border-radius: 2px;
}

.smartscore-bar-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: #8BC34A;
  border-radius: 2px;
}

.score-start {
  font-size: 12px;
  color: #bbb;
  width: 15px;
  text-align: right;
}

.score-end {
  font-size: 13px;
  font-weight: 700;
  width: 25px;
}

.score-blue { color: #039BE5; }
.score-gold { color: #FFD600; }
.score-green { color: #8BC34A; }
.score-gray { color: #999; }

.smartscore-bar-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #eee;
  border-radius: 2px;
}

.smartscore-bar-fill {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  background: #8BC34A;
  border-radius: 2px;
}

.smartscore-arrow {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 10px;
  height: 10px;
  color: #8BC34A;
}

.score-start {
  color: #ccc;
  font-weight: 400;
  font-size: 12px;
}

.score-end {
  font-size: 14px;
  min-width: 20px;
  text-align: right;
}

.score-end.score-mastered { color: #FFB300; }
.score-end.score-proficient { color: #03A9F4; }
.score-end.score-medium { color: #4CAF50; }
.score-end.score-low { color: #333; }

.student-card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 24px;
  padding: 10px 20px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
}

.footer-stat {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 500;
  color: #666;
}

.footer-icon {
  width: 14px;
  height: 14px;
}

.footer-icon.mastered { color: #FFB300; }
.footer-icon.proficient { color: #03A9F4; }

/* Responsive */
@media (max-width: 768px) {
  .analytics-header {
    padding: 0;
  }
  .analytics-tabs {
    padding: 0 16px;
    gap: 0;
    overflow-x: auto;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
  }
  .tab-item {
    flex: 0 0 auto;
    justify-content: center;
    gap: 6px;
    padding: 12px 14px;
    font-size: 13px;
    white-space: nowrap;
  }
  .tab-icon { margin-right: 0; }
  .tab-icon svg { width: 18px; height: 18px; }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
    padding: 12px 16px;
    gap: 8px;
  }
  .filter-group { width: 100%; }
  .filter-label.clickable { width: 100%; justify-content: space-between; }

  .analytics-content { padding: 16px; }

  .student-carousel-container {
    padding: 16px 8px;
    gap: 8px;
  }
  .carousel-arrow svg { width: 24px; height: 24px; }
  .carousel-select { font-size: 16px; padding: 8px; }
  .carousel-label { font-size: 10px; }

  .date-dropdown-popup {
    right: 0;
    left: 0;
    width: 100%;
  }

  /* Quickview Table Adjustments */
  .header-summary-row { height: auto; }
  .student-unified-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .student-name-column { min-width: 150px; }
  .stat-align-column.questions, 
  .stat-align-column.time, 
  .stat-align-column.practiced { min-width: 100px; padding: 8px; }
  
  .skill-grade-cell { min-width: 80px; font-size: 11px; }
  .skill-name-cell { min-width: 150px; }
  .skill-score-flex { gap: 6px; }
  .smartscore-bar-container { width: 40px; }
}

@media (max-width: 480px) {
  .student-card-footer { flex-direction: column; gap: 8px; align-items: flex-start; }
}

/* ===== PRINT STYLES ===== */
@media print {
  /* Hide navigation, filters and footer */
  :deep(header),
  :deep(nav),
  :deep(footer),
  .analytics-header,
  .filters-bar,
  .tab-icon {
    display: none !important;
  }

  /* Reset page background */
  .analytics-page {
    background: white !important;
    min-height: unset;
  }

  /* Full-width content, no padding trimming */
  .analytics-content {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  /* Notebook-style: clean white, no shadows, pages break nicely */
  * {
    box-shadow: none !important;
    text-shadow: none !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  /* Page setup */
  @page {
    size: A4 portrait;
    margin: 15mm 15mm 15mm 15mm;
  }

  /* Avoid breaking inside cards/sections */
  section,
  .card,
  table,
  tr {
    page-break-inside: avoid;
  }
}

/* Warning Banner Styles */
.stale-warning-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  background-color: #fff9e6;
  border: 1px solid #ffeeba;
  border-radius: 8px;
  padding: 12px 20px;
  margin-bottom: 24px;
  color: #856404;
  font-size: 14px;
}

.warning-message {
  display: flex;
  align-items: center;
  gap: 10px;
}

.warning-icon {
  font-size: 18px;
}

.warning-text {
  font-weight: 500;
  line-height: 1.4;
}

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background-color: #ffc107;
  color: #212529;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
  white-space: nowrap;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #e0a800;
}

.refresh-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.refresh-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #212529;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spinner-spin 0.8s linear infinite;
}

@keyframes spinner-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

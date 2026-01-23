import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { analyticsApi } from '@/api/analytics'
import type { AnalyticsOverview, AnalyticsSkills } from '@/types/api'

const CACHE_TTL = 5 * 60 * 1000 // 5 минут

export const useAnalyticsStore = defineStore('analytics', () => {
  const overview = ref<AnalyticsOverview | null>(null)
  const skills = ref<AnalyticsSkills>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastFetch = ref<number>(0)

  const isStale = computed(() => {
    return Date.now() - lastFetch.value > CACHE_TTL
  })

  const totalTime = computed(() => {
    return overview.value?.total_time_sec || overview.value?.total_time || 0
  })

  const totalQuestions = computed(() => {
    return overview.value?.total_questions_answered || overview.value?.total_questions || 0
  })

  const accuracy = computed(() => {
    // Используем avg_accuracy_percent из API, если доступен
    if (overview.value?.avg_accuracy_percent !== undefined) {
      return overview.value.avg_accuracy_percent
    }
    // Иначе вычисляем из total и correct_count
    const total = totalQuestions.value
    const correct = overview.value?.correct_count || 0
    if (total === 0) return 0
    return Math.round((correct / total) * 100)
  })

  const studiedTopics = computed(() => {
    return overview.value?.studied_topics || []
  })

  const bestScores = computed(() => {
    return overview.value?.best_scores || {}
  })

  const getOverview = async (force = false) => {
    if (!force && !isStale.value && overview.value) {
      return overview.value
    }

    loading.value = true
    error.value = null
    try {
      console.log('AnalyticsStore: Fetching overview...')
      const response = await analyticsApi.getOverview()
      console.log('AnalyticsStore: Overview response:', response)
      if (response.data) {
        overview.value = response.data
        lastFetch.value = Date.now()

        // Сохраняем в localStorage для кэша
        localStorage.setItem('analytics_overview', JSON.stringify(response.data))
        localStorage.setItem('analytics_overview_time', lastFetch.value.toString())
      } else {
        console.warn('AnalyticsStore: No data in overview response')
        overview.value = null
      }
      return overview.value
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to fetch overview'
      error.value = errorMsg
      console.error('AnalyticsStore: Failed to fetch analytics overview:', {
        error: err,
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
      })

      // Пробуем загрузить из localStorage
      const cached = localStorage.getItem('analytics_overview')
      if (cached) {
        try {
          overview.value = JSON.parse(cached)
          return overview.value
        } catch (e) {
          console.error('Failed to parse cached overview', e)
        }
      }

      throw err
    } finally {
      loading.value = false
    }
  }

  const getSkills = async (force = false) => {
    if (!force && !isStale.value && skills.value.length > 0) {
      return skills.value
    }

    loading.value = true
    error.value = null
    try {
      console.log('AnalyticsStore: Fetching skills...')
      const response = await analyticsApi.getSkills()
      console.log('AnalyticsStore: Skills response:', response)
      if (response.data) {
        skills.value = response.data
        lastFetch.value = Date.now()

        localStorage.setItem('analytics_skills', JSON.stringify(response.data))
        localStorage.setItem('analytics_skills_time', lastFetch.value.toString())
      } else {
        console.warn('AnalyticsStore: No data in skills response')
        skills.value = []
      }
      return skills.value
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to fetch skills'
      error.value = errorMsg
      console.error('AnalyticsStore: Failed to fetch analytics skills:', {
        error: err,
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
      })

      const cached = localStorage.getItem('analytics_skills')
      if (cached) {
        try {
          skills.value = JSON.parse(cached)
          return skills.value
        } catch (e) {
          console.error('Failed to parse cached skills', e)
        }
      }

      throw err
    } finally {
      loading.value = false
    }
  }

  // Инициализация из localStorage
  const init = () => {
    try {
      const cachedOverview = localStorage.getItem('analytics_overview')
      const cachedSkills = localStorage.getItem('analytics_skills')
      const overviewTime = localStorage.getItem('analytics_overview_time')
      const skillsTime = localStorage.getItem('analytics_skills_time')

      if (cachedOverview && overviewTime) {
        const age = Date.now() - parseInt(overviewTime, 10)
        if (age < CACHE_TTL) {
          overview.value = JSON.parse(cachedOverview)
          lastFetch.value = parseInt(overviewTime, 10)
        }
      }

      if (cachedSkills && skillsTime) {
        const age = Date.now() - parseInt(skillsTime, 10)
        if (age < CACHE_TTL) {
          skills.value = JSON.parse(cachedSkills)
        }
      }
    } catch (error) {
      console.error('Failed to init analytics from cache', error)
    }
  }

  init()

  const allQuestions = ref<Array<Record<string, any>>>([])

  const getAllQuestions = async (force = false) => {
    if (!force && !isStale.value && allQuestions.value.length > 0) {
      return allQuestions.value
    }

    loading.value = true
    error.value = null
    try {
      console.log('AnalyticsStore: Fetching all questions...')
      const response = await analyticsApi.getAllQuestions()
      console.log('AnalyticsStore: All questions response:', response)
      if (response.data) {
        allQuestions.value = response.data
        lastFetch.value = Date.now()
      } else {
        console.warn('AnalyticsStore: No data in all questions response')
        allQuestions.value = []
      }
      return allQuestions.value
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to fetch all questions'
      error.value = errorMsg
      console.error('AnalyticsStore: Failed to fetch all questions:', {
        error: err,
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
      })
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    overview,
    skills,
    allQuestions,
    loading,
    error,
    isStale,
    totalTime,
    totalQuestions,
    accuracy,
    studiedTopics,
    bestScores,
    getOverview,
    getSkills,
    getAllQuestions,
  }
})

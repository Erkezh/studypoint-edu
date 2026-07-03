import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { analyticsApi } from '@/api/analytics'
import type { AnalyticsOverview, AnalyticsSkills } from '@/types/api'

const isDev = import.meta.env.DEV

export const useAnalyticsStore = defineStore('analytics', () => {
  const overview = ref<AnalyticsOverview | null>(null)
  const skills = ref<AnalyticsSkills>([])
  const allQuestions = ref<Array<Record<string, unknown>>>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastFetch = ref<number>(0)
  const lastUpdated = ref<number | null>(null)
  const isStale = ref(false)

  const getUserId = (): string => {
    try {
      const userJson = localStorage.getItem('user')
      if (userJson) {
        const user = JSON.parse(userJson)
        return user.id || ''
      }
    } catch {
      // ignore
    }
    return ''
  }

  const loadCache = () => {
    const userId = getUserId()
    if (!userId) return

    const cachedOverview = localStorage.getItem(`analytics_${userId}_overview`)
    const cachedSkills = localStorage.getItem(`analytics_${userId}_skills`)
    const cachedQuestions = localStorage.getItem(`analytics_${userId}_questions`)
    const cachedLastUpdated = localStorage.getItem(`analytics_${userId}_last_updated`)

    if (cachedOverview && !overview.value) {
      try {
        overview.value = JSON.parse(cachedOverview)
      } catch (e) {
        console.error('Failed to parse cached overview', e)
      }
    }
    if (cachedSkills && skills.value.length === 0) {
      try {
        skills.value = JSON.parse(cachedSkills)
      } catch (e) {
        console.error('Failed to parse cached skills', e)
      }
    }
    if (cachedQuestions && allQuestions.value.length === 0) {
      try {
        allQuestions.value = JSON.parse(cachedQuestions)
      } catch (e) {
        console.error('Failed to parse cached questions', e)
      }
    }
    if (cachedLastUpdated) {
      lastUpdated.value = parseInt(cachedLastUpdated, 10)
    }
  }

  const saveCache = (key: string, data: unknown) => {
    const userId = getUserId()
    if (!userId) return
    localStorage.setItem(`analytics_${userId}_${key}`, JSON.stringify(data))
    localStorage.setItem(`analytics_${userId}_last_updated`, Date.now().toString())
    lastUpdated.value = Date.now()
  }

  const totalTime = computed(() => {
    return overview.value?.total_time_sec || overview.value?.total_time || 0
  })

  const totalQuestions = computed(() => {
    return overview.value?.total_questions_answered || overview.value?.total_questions || 0
  })

  const accuracy = computed(() => {
    if (overview.value?.avg_accuracy_percent !== undefined) {
      return overview.value.avg_accuracy_percent
    }
    const total = (totalQuestions.value as number) || 0
    const correct = (overview.value?.correct_count as number) || 0
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
    loadCache()

    if (!force && overview.value && !isStale.value) {
      return overview.value
    }

    loading.value = true
    error.value = null
    try {
      if (isDev) {
        console.log('AnalyticsStore: Fetching overview...')
      }
      const response = await analyticsApi.getOverview()
      if (response.data) {
        overview.value = response.data
        saveCache('overview', response.data)
        isStale.value = false
      } else {
        overview.value = null
      }
      lastFetch.value = Date.now()
      return overview.value
    } catch (err: unknown) {
      if (overview.value) {
        isStale.value = true
        console.warn('AnalyticsStore: API error, showing cached overview data', err)
        return overview.value
      } else {
        const axiosErr = err as { response?: { data?: { detail?: string; message?: string } }; message?: string }
        const errorMsg = axiosErr.response?.data?.detail || axiosErr.response?.data?.message || axiosErr.message || 'Failed to fetch overview'
        error.value = errorMsg
        throw err
      }
    } finally {
      loading.value = false
    }
  }

  const getSkills = async (force = false) => {
    loadCache()

    if (!force && skills.value.length > 0 && !isStale.value) {
      return skills.value
    }

    loading.value = true
    error.value = null
    try {
      if (isDev) {
        console.log('AnalyticsStore: Fetching skills...')
      }
      const response = await analyticsApi.getSkills()
      if (response.data) {
        skills.value = response.data
        saveCache('skills', response.data)
        isStale.value = false
      } else {
        skills.value = []
      }
      lastFetch.value = Date.now()
      return skills.value
    } catch (err: unknown) {
      if (skills.value.length > 0) {
        isStale.value = true
        console.warn('AnalyticsStore: API error, showing cached skills data', err)
        return skills.value
      } else {
        const axiosErr = err as { response?: { data?: { detail?: string; message?: string } }; message?: string }
        const errorMsg = axiosErr.response?.data?.detail || axiosErr.response?.data?.message || axiosErr.message || 'Failed to fetch skills'
        error.value = errorMsg
        throw err
      }
    } finally {
      loading.value = false
    }
  }

  const getAllQuestions = async (force = false) => {
    loadCache()

    if (!force && allQuestions.value.length > 0 && !isStale.value) {
      return allQuestions.value
    }

    loading.value = true
    error.value = null
    try {
      if (isDev) {
        console.log('AnalyticsStore: Fetching all questions...')
      }
      const response = await analyticsApi.getAllQuestions()
      if (response.data) {
        allQuestions.value = response.data
        saveCache('questions', response.data)
        isStale.value = false
      } else {
        allQuestions.value = []
      }
      lastFetch.value = Date.now()
      return allQuestions.value
    } catch (err: unknown) {
      if (allQuestions.value.length > 0) {
        isStale.value = true
        console.warn('AnalyticsStore: API error, showing cached questions data', err)
        return allQuestions.value
      } else {
        const axiosErr = err as { response?: { data?: { detail?: string; message?: string } }; message?: string }
        const errorMsg = axiosErr.response?.data?.detail || axiosErr.response?.data?.message || axiosErr.message || 'Failed to fetch all questions'
        error.value = errorMsg
        throw err
      }
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
    lastUpdated,
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

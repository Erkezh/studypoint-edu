import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { catalogApi } from '@/api/catalog'
import type {
  SubjectResponse,
  GradeResponse,
  SkillListItem,
  SkillDetailResponse,
} from '@/types/api'

const CACHE_TTL = 5 * 60 * 1000 // 5 минут

export const useCatalogStore = defineStore('catalog', () => {
  const subjects = ref<SubjectResponse[]>([])
  const grades = ref<GradeResponse[]>([])
  const skills = ref<SkillListItem[]>([])
  const skillDetails = ref<Map<number, SkillDetailResponse>>(new Map())
  // Кэш навыков по параметрам (ключ - строка параметров)
  const skillsCache = ref<Map<string, SkillListItem[]>>(new Map())

  const loading = ref(false)
  const lastFetch = ref<Map<string, number>>(new Map())

  const isStale = (key: string) => {
    const lastTime = lastFetch.value.get(key)
    if (!lastTime) return true
    return Date.now() - lastTime > CACHE_TTL
  }

  // Создает ключ кэша из параметров
  const getCacheKey = (params?: {
    subject_slug?: string | null
    grade_number?: number | null
    q?: string | null
    page?: number
    page_size?: number
  }): string => {
    if (!params) return 'all'
    const parts: string[] = []
    if (params.subject_slug) parts.push(`subject:${params.subject_slug}`)
    if (params.grade_number !== null && params.grade_number !== undefined) parts.push(`grade:${params.grade_number}`)
    if (params.q) parts.push(`q:${params.q}`)
    if (params.page) parts.push(`page:${params.page}`)
    if (params.page_size) parts.push(`size:${params.page_size}`)
    return parts.length > 0 ? parts.join('|') : 'all'
  }

  const getSubjects = async (force = false) => {
    if (!force && !isStale('subjects') && subjects.value.length > 0) {
      return subjects.value
    }

    loading.value = true
    try {
      const response = await catalogApi.getSubjects()
      if (response.data) {
        subjects.value = response.data
        lastFetch.value.set('subjects', Date.now())

        // Сохраняем в localStorage для кэша
        localStorage.setItem('catalog_subjects', JSON.stringify(response.data))
        localStorage.setItem('catalog_subjects_time', Date.now().toString())
      }
      return subjects.value
    } catch (error) {
      console.error('Failed to fetch subjects:', error)
      // Пробуем загрузить из localStorage при ошибке
      const cached = localStorage.getItem('catalog_subjects')
      if (cached) {
        try {
          subjects.value = JSON.parse(cached)
          return subjects.value
        } catch (e) {
          console.error('Failed to parse cached subjects', e)
        }
      }
      throw error
    } finally {
      loading.value = false
    }
  }

  const getGrades = async (force = false) => {
    if (!force && !isStale('grades') && grades.value.length > 0) {
      return grades.value
    }

    loading.value = true
    try {
      const response = await catalogApi.getGrades()
      if (response.data) {
        grades.value = response.data
        lastFetch.value.set('grades', Date.now())

        localStorage.setItem('catalog_grades', JSON.stringify(response.data))
        localStorage.setItem('catalog_grades_time', Date.now().toString())
      }
      return grades.value
    } catch (error) {
      console.error('Failed to fetch grades:', error)
      const cached = localStorage.getItem('catalog_grades')
      if (cached) {
        try {
          grades.value = JSON.parse(cached)
          return grades.value
        } catch (e) {
          console.error('Failed to parse cached grades', e)
        }
      }
      throw error
    } finally {
      loading.value = false
    }
  }

  const getSkills = async (params?: {
    subject_slug?: string | null
    grade_number?: number | null
    q?: string | null
    page?: number
    page_size?: number
  }, force = false) => {
    // Если force=true, игнорируем кэш и всегда загружаем с сервера
    if (!force && !isStale('skills') && skills.value.length > 0) {
      return skills.value
    }

    loading.value = true
    try {
      console.log('CatalogStore: Fetching skills with params:', params)
      const response = await catalogApi.getSkills(params)
      console.log('CatalogStore: Skills response:', response)
      if (response.data) {
        skills.value = response.data
        lastFetch.value.set('skills', Date.now())
      }
      return skills.value
    } catch (error: any) {
      console.error('CatalogStore: Failed to fetch skills:', {
        error,
        params,
        response: error.response?.data,
        status: error.response?.status,
        code: error.code,
        message: error.message,
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const getSkill = async (skillId: number, force = false) => {
    if (!force && skillDetails.value.has(skillId)) {
      return skillDetails.value.get(skillId)!
    }

    loading.value = true
    try {
      const response = await catalogApi.getSkill(skillId)
      if (response.data) {
        skillDetails.value.set(skillId, response.data)
        return response.data
      }
      throw new Error('Skill not found')
    } catch (error) {
      console.error('Failed to fetch skill:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const getSkillStats = async (skillId: number) => {
    try {
      const response = await catalogApi.getSkillStats(skillId)
      return response.data || {}
    } catch (error) {
      console.error('Failed to fetch skill stats:', error)
      throw error
    }
  }

  const clearSkillsCache = () => {
    skills.value = []
    skillsCache.value.clear()
    lastFetch.value.delete('skills')
  }

  // Удаляет навык из кэша по ID (для оптимистичного обновления UI)
  const removeSkillFromCache = (skillId: number) => {
    skills.value = skills.value.filter(s => s.id !== skillId)
    // Также очищаем из skillsCache если есть
    skillsCache.value.forEach((cachedSkills, key) => {
      const filtered = cachedSkills.filter(s => s.id !== skillId)
      if (filtered.length !== cachedSkills.length) {
        skillsCache.value.set(key, filtered)
      }
    })
    // Удаляем детали навыка если есть
    skillDetails.value.delete(skillId)
  }

  // Инициализация из localStorage при создании store
  const init = () => {
    try {
      const cachedSubjects = localStorage.getItem('catalog_subjects')
      const cachedGrades = localStorage.getItem('catalog_grades')
      const subjectsTime = localStorage.getItem('catalog_subjects_time')
      const gradesTime = localStorage.getItem('catalog_grades_time')

      if (cachedSubjects && subjectsTime) {
        const age = Date.now() - parseInt(subjectsTime, 10)
        if (age < CACHE_TTL) {
          subjects.value = JSON.parse(cachedSubjects)
          lastFetch.value.set('subjects', parseInt(subjectsTime, 10))
        }
      }

      if (cachedGrades && gradesTime) {
        const age = Date.now() - parseInt(gradesTime, 10)
        if (age < CACHE_TTL) {
          grades.value = JSON.parse(cachedGrades)
          lastFetch.value.set('grades', parseInt(gradesTime, 10))
        }
      }
    } catch (error) {
      console.error('Failed to init catalog from cache', error)
    }
  }

  init()

  return {
    subjects,
    grades,
    skills,
    skillDetails,
    loading,
    getSubjects,
    getGrades,
    getSkills,
    getSkill,
    getSkillStats,
    clearSkillsCache,
    removeSkillFromCache,
  }
})

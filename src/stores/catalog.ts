import { defineStore } from 'pinia'
import { ref } from 'vue'
import { catalogApi } from '@/api/catalog'
import type {
  GradeResponse,
  SkillDetailResponse,
  SkillListItem,
  SkillStatsResponse,
  SubjectResponse,
  TopicResponse,
} from '@/types/api'

const CACHE_TTL = 5 * 60 * 1000
const isDev = import.meta.env.DEV
const STORAGE_KEYS = {
  subjects: 'catalog_subjects',
  grades: 'catalog_grades',
  topics: 'catalog_topics',
}
const STORAGE_TIME_KEYS = {
  subjects: 'catalog_subjects_time',
  grades: 'catalog_grades_time',
  topics: 'catalog_topics_time',
}

type SkillsQueryParams = {
  subject_slug?: string | null
  grade_number?: number | null
  topic_id?: number | null
  topic_ids?: number[] | null
  q?: string | null
  page?: number
  page_size?: number
}

const parseStorage = <T>(key: string): T | null => {
  if (typeof window === 'undefined') return null
  const rawValue = localStorage.getItem(key)
  if (!rawValue) return null
  try {
    return JSON.parse(rawValue) as T
  } catch {
    localStorage.removeItem(key)
    return null
  }
}

export const useCatalogStore = defineStore('catalog', () => {
  const subjects = ref<SubjectResponse[]>([])
  const grades = ref<GradeResponse[]>([])
  const topics = ref<TopicResponse[]>([])
  const skills = ref<SkillListItem[]>([])
  const skillDetails = ref<Map<number, SkillDetailResponse>>(new Map())
  const skillsCache = ref<Map<string, SkillListItem[]>>(new Map())

  const loading = ref(false)
  const lastFetch = ref<Map<string, number>>(new Map())

  let pendingRequests = 0
  const inFlightRequests = new Map<string, Promise<unknown>>()

  const isStale = (key: string) => {
    const lastTime = lastFetch.value.get(key)
    return !lastTime || Date.now() - lastTime > CACHE_TTL
  }

  const withLoading = async <T>(factory: () => Promise<T>) => {
    pendingRequests += 1
    loading.value = true
    try {
      return await factory()
    } finally {
      pendingRequests = Math.max(0, pendingRequests - 1)
      loading.value = pendingRequests > 0
    }
  }

  const runRequest = async <T>(key: string, factory: () => Promise<T>) => {
    const existing = inFlightRequests.get(key) as Promise<T> | undefined
    if (existing) {
      return existing
    }

    const request = withLoading(factory).finally(() => {
      inFlightRequests.delete(key)
    }) as Promise<T>

    inFlightRequests.set(key, request as Promise<unknown>)
    return request
  }

  const saveListCache = <T>(key: keyof typeof STORAGE_KEYS, data: T) => {
    if (typeof window === 'undefined') return
    const timestamp = Date.now()
    localStorage.setItem(STORAGE_KEYS[key], JSON.stringify(data))
    localStorage.setItem(STORAGE_TIME_KEYS[key], timestamp.toString())
    lastFetch.value.set(key, timestamp)
  }

  const loadListCache = <T>(key: keyof typeof STORAGE_KEYS): T | null => {
    if (typeof window === 'undefined') return null
    const cachedAt = localStorage.getItem(STORAGE_TIME_KEYS[key])
    if (!cachedAt) return null

    const timestamp = Number.parseInt(cachedAt, 10)
    if (Number.isNaN(timestamp) || Date.now() - timestamp > CACHE_TTL) {
      localStorage.removeItem(STORAGE_KEYS[key])
      localStorage.removeItem(STORAGE_TIME_KEYS[key])
      return null
    }

    const parsed = parseStorage<T>(STORAGE_KEYS[key])
    if (parsed) {
      lastFetch.value.set(key, timestamp)
    }
    return parsed
  }

  const normalizeSkillsParams = (params?: SkillsQueryParams) => ({
    subject_slug: params?.subject_slug ?? null,
    grade_number: params?.grade_number ?? null,
    topic_id: params?.topic_id ?? null,
    topic_ids: params?.topic_ids?.length ? [...params.topic_ids].sort((a, b) => a - b) : null,
    q: params?.q?.trim() || null,
    page: params?.page ?? 1,
    page_size: params?.page_size ?? 20,
  })

  const getSkillsCacheKey = (params?: SkillsQueryParams) => {
    return JSON.stringify(normalizeSkillsParams(params))
  }

  const clearSkillQueryCache = () => {
    skillsCache.value.clear()
    for (const key of Array.from(lastFetch.value.keys())) {
      if (key.startsWith('skills:')) {
        lastFetch.value.delete(key)
      }
    }
  }

  const getSubjects = async (force = false) => {
    if (!force && !isStale('subjects') && subjects.value.length > 0) {
      return subjects.value
    }

    return runRequest('catalog:subjects', async () => {
      const response = await catalogApi.getSubjects()
      subjects.value = response.data || []
      saveListCache('subjects', subjects.value)
      return subjects.value
    })
  }

  const getGrades = async (force = false) => {
    if (!force && !isStale('grades') && grades.value.length > 0) {
      return grades.value
    }

    return runRequest('catalog:grades', async () => {
      const response = await catalogApi.getGrades()
      grades.value = response.data || []
      saveListCache('grades', grades.value)
      return grades.value
    })
  }

  const getTopics = async (force = false) => {
    if (!force && !isStale('topics') && topics.value.length > 0) {
      return topics.value
    }

    return runRequest('catalog:topics', async () => {
      const response = await catalogApi.getTopics()
      topics.value = response.data || []
      saveListCache('topics', topics.value)
      return topics.value
    })
  }

  const getSkills = async (params?: SkillsQueryParams, force = false) => {
    const normalizedParams = normalizeSkillsParams(params)
    const cacheKey = getSkillsCacheKey(normalizedParams)
    const fetchKey = `skills:${cacheKey}`

    if (!force && !isStale(fetchKey)) {
      const cachedSkills = skillsCache.value.get(cacheKey)
      if (cachedSkills) {
        skills.value = [...cachedSkills]
        return skills.value
      }
    }

    return runRequest(`catalog:${fetchKey}`, async () => {
      if (isDev) {
        console.log('CatalogStore: Fetching skills with params:', normalizedParams)
      }

      const response = await catalogApi.getSkills(normalizedParams)
      const nextSkills = response.data || []
      skills.value = nextSkills
      skillsCache.value.set(cacheKey, nextSkills)
      lastFetch.value.set(fetchKey, Date.now())
      return skills.value
    })
  }

  const getSkill = async (skillId: number, force = false) => {
    if (!force && skillDetails.value.has(skillId)) {
      return skillDetails.value.get(skillId)!
    }

    return runRequest(`catalog:skill:${skillId}`, async () => {
      const response = await catalogApi.getSkill(skillId)
      if (!response.data) {
        throw new Error('Skill not found')
      }

      skillDetails.value.set(skillId, response.data)
      return response.data
    })
  }

  const getSkillStats = async (skillId: number) => {
    const response = await catalogApi.getSkillStats(skillId)
    return response.data || ({
      best_smartscore: 0,
      last_smartscore: 0,
      last_practiced_at: null,
      total_questions: 0,
      accuracy_percent: 0,
    } satisfies SkillStatsResponse)
  }

  const getSkillStatsBatch = async (skillIds: number[]) => {
    const uniqueSkillIds = Array.from(new Set(skillIds.filter(skillId => Number.isFinite(skillId))))
    if (uniqueSkillIds.length === 0) {
      return {} as Record<number, SkillStatsResponse>
    }

    const response = await catalogApi.getSkillStatsBatch(uniqueSkillIds)
    const payload = response.data || {}
    return Object.fromEntries(
      Object.entries(payload).map(([skillId, stats]) => [Number.parseInt(skillId, 10), stats])
    ) as Record<number, SkillStatsResponse>
  }

  const clearSkillsCache = () => {
    skills.value = []
    clearSkillQueryCache()
  }

  const removeSkillFromCache = (skillId: number) => {
    skills.value = skills.value.filter(skill => skill.id !== skillId)
    for (const [cacheKey, cachedSkills] of skillsCache.value.entries()) {
      const filteredSkills = cachedSkills.filter(skill => skill.id !== skillId)
      if (filteredSkills.length !== cachedSkills.length) {
        skillsCache.value.set(cacheKey, filteredSkills)
      }
    }
    skillDetails.value.delete(skillId)
  }

  const updateSkill = async (
    skillId: number,
    data: { grade_id?: number; topic_id?: number | null; code?: string; title?: string }
  ) => {
    const response = await catalogApi.updateSkill(skillId, data)
    if (!response.data) {
      throw new Error('Failed to update skill')
    }

    const updatedSkill = response.data
    skillDetails.value.set(skillId, updatedSkill)

    const skillIndex = skills.value.findIndex(skill => skill.id === skillId)
    if (skillIndex !== -1) {
      skills.value[skillIndex] = {
        ...skills.value[skillIndex],
        grade_id: updatedSkill.grade_id,
        topic_id: updatedSkill.topic_id,
        topic_title: updatedSkill.topic_title,
        code: updatedSkill.code,
        title: updatedSkill.title,
      } as SkillListItem
    }

    clearSkillQueryCache()
    return updatedSkill
  }

  const init = () => {
    try {
      const cachedSubjects = loadListCache<SubjectResponse[]>('subjects')
      if (cachedSubjects) {
        subjects.value = cachedSubjects
      }

      const cachedGrades = loadListCache<GradeResponse[]>('grades')
      if (cachedGrades) {
        const hasLabel = cachedGrades.length === 0 || 'label' in cachedGrades[0]
        if (hasLabel) {
          grades.value = cachedGrades
        } else if (typeof window !== 'undefined') {
          localStorage.removeItem(STORAGE_KEYS.grades)
          localStorage.removeItem(STORAGE_TIME_KEYS.grades)
        }
      }

      const cachedTopics = loadListCache<TopicResponse[]>('topics')
      if (cachedTopics) {
        topics.value = cachedTopics
      }
    } catch (error) {
      if (isDev) {
        console.error('Failed to init catalog from cache', error)
      }
    }
  }

  init()

  return {
    subjects,
    grades,
    topics,
    skills,
    skillDetails,
    loading,
    getSubjects,
    getGrades,
    getTopics,
    getSkills,
    getSkill,
    getSkillStats,
    getSkillStatsBatch,
    clearSkillsCache,
    removeSkillFromCache,
    updateSkill,
  }
})

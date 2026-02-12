import apiClient from './client'
import type { ApiResponse } from '@/types/api'

export interface InteractiveQuestionCreate {
  skill_id: number
  prompt: string
  component_code: string
  correct_answer?: Record<string, unknown>
  explanation?: string
  level?: number
  metadata?: Record<string, unknown>
}

export interface SkillCreate {
  subject_id: number
  grade_id: number
  topic_id?: number | null
  code: string
  title: string
  description?: string
  tags?: string[]
  difficulty?: number
  example_url?: string
  video_url?: string
  is_published?: boolean
  generator_code?: string
  generator_metadata?: Record<string, unknown>
}

export interface TopicCreate {
  slug: string
  title: string
  description?: string
  icon?: string | null
  order?: number
  is_published?: boolean
}

export interface TopicUpdate {
  slug?: string
  title?: string
  description?: string
  icon?: string | null
  order?: number
  is_published?: boolean
}

export interface TopicListItem {
  id: number
  slug: string
  title: string
  description: string
  icon: string | null
  order: number
  is_published: boolean
}

export interface SkillListItem {
  id: number
  subject_id: number
  grade_id: number
  topic_id: number | null
  topic_title: string | null
  code: string
  title: string
  difficulty: number
  tags: string[]
}

export interface QuestionListItem {
  id: number
  skill_id: number
  skill_title?: string
  type: string
  prompt: string
  data: Record<string, unknown>
  correct_answer: Record<string, unknown>
  explanation: string | null
  level: number
  created_at?: string
}

export const adminApi = {
  async createInteractiveQuestion(
    data: InteractiveQuestionCreate
  ): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await apiClient.post<ApiResponse<Record<string, unknown>>>(
      '/admin/questions/interactive',
      data
    )
    return response.data
  },

  async createSkill(
    data: SkillCreate
  ): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await apiClient.post<ApiResponse<Record<string, unknown>>>(
      '/admin/skills',
      data
    )
    return response.data
  },

  async listSkills(
    page: number = 1,
    pageSize: number = 50
  ): Promise<ApiResponse<SkillListItem[]>> {
    const response = await apiClient.get<ApiResponse<SkillListItem[]>>(
      '/admin/skills',
      {
        params: { page, page_size: pageSize },
      }
    )
    return response.data
  },

  async deleteSkill(skillId: number): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await apiClient.delete<ApiResponse<Record<string, unknown>>>(
      `/admin/skills/${skillId}`
    )
    return response.data
  },

  async updateSkill(
    skillId: number,
    data: { grade_id?: number; topic_id?: number | null; code?: string; title?: string }
  ): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await apiClient.patch<ApiResponse<Record<string, unknown>>>(
      `/admin/skills/${skillId}`,
      data
    )
    return response.data
  },

  // --- Topic CRUD ---

  async createTopic(
    data: TopicCreate
  ): Promise<ApiResponse<TopicListItem>> {
    const response = await apiClient.post<ApiResponse<TopicListItem>>(
      '/admin/topics',
      data
    )
    return response.data
  },

  async listTopics(
    page: number = 1,
    pageSize: number = 50
  ): Promise<ApiResponse<TopicListItem[]>> {
    const response = await apiClient.get<ApiResponse<TopicListItem[]>>(
      '/admin/topics',
      {
        params: { page, page_size: pageSize },
      }
    )
    return response.data
  },

  async updateTopic(
    topicId: number,
    data: TopicUpdate
  ): Promise<ApiResponse<TopicListItem>> {
    const response = await apiClient.patch<ApiResponse<TopicListItem>>(
      `/admin/topics/${topicId}`,
      data
    )
    return response.data
  },

  async deleteTopic(topicId: number): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await apiClient.delete<ApiResponse<Record<string, unknown>>>(
      `/admin/topics/${topicId}`
    )
    return response.data
  },

  async uploadPlugin(file: File): Promise<ApiResponse<Record<string, unknown>>> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post<ApiResponse<Record<string, unknown>>>(
      '/admin/plugins/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  async listPlugins(): Promise<ApiResponse<Array<Record<string, unknown>>>> {
    const response = await apiClient.get<ApiResponse<Array<Record<string, unknown>>>>(
      '/admin/plugins'
    )
    return response.data
  },

  async publishPlugin(
    pluginId: string,
    isPublished: boolean
  ): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await apiClient.post<ApiResponse<Record<string, unknown>>>(
      `/admin/plugins/${pluginId}/publish?is_published=${isPublished}`,
      null
    )
    return response.data
  },

  async deletePlugin(pluginId: string): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await apiClient.delete<ApiResponse<Record<string, unknown>>>(
      `/admin/plugins/${pluginId}`
    )
    return response.data
  },

  async createPluginQuestion(data: {
    skill_id: number
    plugin_id: string
    plugin_version?: string
  }): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await apiClient.post<ApiResponse<Record<string, unknown>>>(
      '/admin/questions/plugin',
      data
    )
    return response.data
  },

  async addPluginToTest(data: {
    grade_id: number
    topic_id?: number | null
    plugin_id: string
    plugin_version?: string
  }): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await apiClient.post<ApiResponse<Record<string, unknown>>>(
      '/admin/plugins/add-to-test',
      data
    )
    return response.data
  },

  async uploadTsxPlugin(
    file: File,
    pluginName?: string,
    gradeId?: number
  ): Promise<ApiResponse<Record<string, unknown>>> {
    const formData = new FormData()
    formData.append('file', file)
    if (pluginName) {
      formData.append('plugin_name', pluginName)
    }
    if (gradeId) {
      formData.append('grade_id', gradeId.toString())
    }
    const response = await apiClient.post<ApiResponse<Record<string, unknown>>>(
      '/admin/plugins/upload-tsx',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  async updateTsxPlugin(
    pluginId: string,
    file: File
  ): Promise<ApiResponse<Record<string, unknown>>> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.put<ApiResponse<Record<string, unknown>>>(
      `/admin/plugins/${pluginId}/update-tsx`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  async listQuestions(params?: {
    skill_id?: number
    search?: string
    sort_order?: 'asc' | 'desc'
    page?: number
    page_size?: number
  }): Promise<ApiResponse<QuestionListItem[]>> {
    const response = await apiClient.get<ApiResponse<QuestionListItem[]>>(
      '/admin/questions',
      {
        params,
      }
    )
    return response.data
  },

  async deleteQuestion(questionId: number): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await apiClient.delete<ApiResponse<Record<string, unknown>>>(
      `/admin/questions/${questionId}`
    )
    return response.data
  },
}

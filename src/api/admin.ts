import apiClient from './client'
import type { ApiResponse } from '@/types/api'

export interface InteractiveQuestionCreate {
  skill_id: number
  prompt: string
  component_code: string
  correct_answer?: Record<string, any>
  explanation?: string
  level?: number
  metadata?: Record<string, any>
}

export interface SkillCreate {
  subject_id: number
  grade_id: number
  code: string
  title: string
  description?: string
  tags?: string[]
  difficulty?: number
  example_url?: string
  video_url?: string
  is_published?: boolean
  generator_code?: string
  generator_metadata?: Record<string, any>
}

export interface SkillListItem {
  id: number
  subject_id: number
  grade_id: number
  code: string
  title: string
  difficulty: number
  tags: string[]
}

export const adminApi = {
  async createInteractiveQuestion(
    data: InteractiveQuestionCreate
  ): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.post<ApiResponse<Record<string, any>>>(
      '/admin/questions/interactive',
      data
    )
    return response.data
  },

  async createSkill(
    data: SkillCreate
  ): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.post<ApiResponse<Record<string, any>>>(
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

  async deleteSkill(skillId: number): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.delete<ApiResponse<Record<string, any>>>(
      `/admin/skills/${skillId}`
    )
    return response.data
  },

  async uploadPlugin(file: File): Promise<ApiResponse<Record<string, any>>> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post<ApiResponse<Record<string, any>>>(
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

  async listPlugins(): Promise<ApiResponse<Array<Record<string, any>>>> {
    const response = await apiClient.get<ApiResponse<Array<Record<string, any>>>>(
      '/admin/plugins'
    )
    return response.data
  },

  async publishPlugin(
    pluginId: string,
    isPublished: boolean
  ): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.post<ApiResponse<Record<string, any>>>(
      `/admin/plugins/${pluginId}/publish?is_published=${isPublished}`,
      null
    )
    return response.data
  },

  async deletePlugin(pluginId: string): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.delete<ApiResponse<Record<string, any>>>(
      `/admin/plugins/${pluginId}`
    )
    return response.data
  },
}

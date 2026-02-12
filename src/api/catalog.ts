import apiClient from './client'
import type {
  ApiResponse,
  SubjectResponse,
  GradeResponse,
  TopicResponse,
  SkillListItem,
  SkillDetailResponse,
} from '@/types/api'

export const catalogApi = {
  async getSubjects(): Promise<ApiResponse<SubjectResponse[]>> {
    const response = await apiClient.get<ApiResponse<SubjectResponse[]>>('/subjects')
    return response.data
  },

  async getGrades(): Promise<ApiResponse<GradeResponse[]>> {
    const response = await apiClient.get<ApiResponse<GradeResponse[]>>('/grades')
    return response.data
  },

  async getTopics(): Promise<ApiResponse<TopicResponse[]>> {
    const response = await apiClient.get<ApiResponse<TopicResponse[]>>('/topics')
    return response.data
  },

  async getSkills(params?: {
    subject_slug?: string | null
    grade_number?: number | null
    topic_id?: number | null
    q?: string | null
    page?: number
    page_size?: number
  }): Promise<ApiResponse<SkillListItem[]>> {
    const response = await apiClient.get<ApiResponse<SkillListItem[]>>('/skills', {
      params,
    })
    return response.data
  },

  async getSkill(skillId: number): Promise<ApiResponse<SkillDetailResponse>> {
    const response = await apiClient.get<ApiResponse<SkillDetailResponse>>(
      `/skills/${skillId}`
    )
    return response.data
  },

  async getSkillStats(skillId: number): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await apiClient.get<ApiResponse<Record<string, unknown>>>(
      `/skills/${skillId}/stats`
    )
    return response.data
  },

  async updateSkill(skillId: number, data: { grade_id?: number; topic_id?: number | null; code?: string; title?: string }): Promise<ApiResponse<SkillDetailResponse>> {
    const response = await apiClient.patch<ApiResponse<SkillDetailResponse>>(
      `/skills/${skillId}`,
      data
    )
    return response.data
  }
}

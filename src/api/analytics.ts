import apiClient from './client'
import type { ApiResponse, AnalyticsOverview, AnalyticsSkills } from '@/types/api'

export const analyticsApi = {
  async getOverview(): Promise<ApiResponse<AnalyticsOverview>> {
    const response = await apiClient.get<ApiResponse<AnalyticsOverview>>(
      '/analytics/overview'
    )
    return response.data
  },

  async getSkills(): Promise<ApiResponse<AnalyticsSkills>> {
    const response = await apiClient.get<ApiResponse<AnalyticsSkills>>('/analytics/skills')
    return response.data
  },

  async getAllQuestions(): Promise<ApiResponse<Array<Record<string, any>>>> {
    const response = await apiClient.get<ApiResponse<Array<Record<string, any>>>>('/analytics/all-questions')
    return response.data
  },
}

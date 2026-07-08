import apiClient from './client'
import type { ApiResponse, GamificationProfile, GamificationReward } from '@/types/api'

export const gamificationApi = {
  async getMe(): Promise<ApiResponse<GamificationProfile>> {
    const response = await apiClient.get<ApiResponse<GamificationProfile>>('/gamification/me')
    return response.data
  },

  async submitAnswerResult(data: {
    question_id: number | string
    correct: boolean
    difficulty: 'easy' | 'medium' | 'hard'
  }): Promise<ApiResponse<GamificationReward>> {
    const response = await apiClient.post<ApiResponse<GamificationReward>>('/gamification/answer-result', data)
    return response.data
  },

  async buyVehicle(vehicleId: string): Promise<ApiResponse<GamificationProfile>> {
    const response = await apiClient.post<ApiResponse<GamificationProfile>>(`/garage/buy-vehicle/${vehicleId}`)
    return response.data
  },

  async selectVehicle(vehicleId: string): Promise<ApiResponse<GamificationProfile>> {
    const response = await apiClient.post<ApiResponse<GamificationProfile>>(`/garage/select-vehicle/${vehicleId}`)
    return response.data
  },

  async buyItem(itemId: string): Promise<ApiResponse<GamificationProfile>> {
    const response = await apiClient.post<ApiResponse<GamificationProfile>>(`/garage/buy-item/${itemId}`)
    return response.data
  },

  async equipItem(data: {
    vehicle_id: string
    item_type: string
    item_id?: string | null
  }): Promise<ApiResponse<GamificationProfile>> {
    const response = await apiClient.post<ApiResponse<GamificationProfile>>('/garage/equip-item', data)
    return response.data
  },
}

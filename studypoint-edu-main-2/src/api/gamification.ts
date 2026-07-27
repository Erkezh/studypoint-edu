import apiClient from './client'
import type { ApiResponse, GamificationProfile, GamificationReward, GamificationVehicle } from '@/types/api'

export const gamificationApi = {
  async getMe(): Promise<ApiResponse<GamificationProfile>> {
    const response = await apiClient.get<ApiResponse<GamificationProfile>>('/gamification/me')
    return response.data
  },

  async submitAnswerResult(data: {
    question_id: number | string
    correct: boolean
    difficulty: 'easy' | 'medium' | 'hard'
    topic_id?: number
    smartscore_before?: number
    smartscore_after?: number
  }): Promise<ApiResponse<GamificationReward>> {
    const response = await apiClient.post<ApiResponse<GamificationReward>>('/gamification/reward/question-result', data)
    return response.data
  },

  async getWallet(): Promise<ApiResponse<Pick<GamificationProfile, 'coins' | 'xp' | 'level' | 'active_vehicle'>>> {
    const response = await apiClient.get<ApiResponse<Pick<GamificationProfile, 'coins' | 'xp' | 'level' | 'active_vehicle'>>>('/gamification/wallet')
    return response.data
  },

  async getVehicles(): Promise<ApiResponse<GamificationVehicle[]>> {
    const response = await apiClient.get<ApiResponse<GamificationVehicle[]>>('/gamification/vehicles')
    return response.data
  },

  async buyVehicle(vehicleId: string): Promise<ApiResponse<GamificationProfile>> {
    const response = await apiClient.post<ApiResponse<GamificationProfile>>(`/gamification/vehicles/${vehicleId}/buy`)
    return response.data
  },

  async selectVehicle(vehicleId: string): Promise<ApiResponse<GamificationProfile>> {
    const response = await apiClient.post<ApiResponse<GamificationProfile>>(`/gamification/vehicles/${vehicleId}/select`)
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

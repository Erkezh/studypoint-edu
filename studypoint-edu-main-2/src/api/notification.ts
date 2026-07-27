import apiClient from './client'
import type { ApiResponse, NotificationResponse } from '@/types/api'

export const notificationApi = {
  getNotifications: async (): Promise<ApiResponse<NotificationResponse[]>> => {
    const { data } = await apiClient.get<ApiResponse<NotificationResponse[]>>('/notifications')
    return data
  },

  markAsRead: async (notificationId: string): Promise<ApiResponse<boolean>> => {
    const { data } = await apiClient.post<ApiResponse<boolean>>(`/notifications/${notificationId}/read`)
    return data
  },

  markAllAsRead: async (): Promise<ApiResponse<boolean>> => {
    const { data } = await apiClient.post<ApiResponse<boolean>>('/notifications/read-all')
    return data
  }
}

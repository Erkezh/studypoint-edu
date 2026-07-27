import apiClient from '@/api/client'
import type { ApiResponse, GameSettings, GameType } from '@/types/api'

export const gameSettingsApi = {
  get: () => apiClient.get<ApiResponse<GameSettings>>('/me/game-settings'),
  select: (game: GameType) => apiClient.post<ApiResponse<GameSettings>>('/me/game-settings/select', { game }),
  switch: (game: GameType) => apiClient.post<ApiResponse<GameSettings>>('/me/game-settings/switch', { game }),
}

import apiClient from '@/api/client'
import type { ApiResponse } from '@/types/api'

export interface GameShopItem {
  id: string
  name: string
  category?: string
  item_type?: string
  price?: number
  coin_price?: number
  required_level?: number
  unlock_level?: number
  asset_url?: string | null
  thumbnail_url?: string | null
  owned?: boolean
  equipped?: boolean
  locked?: boolean
}

export const gameShopApi = {
  list: () => apiClient.get<ApiResponse<GameShopItem[]>>('/gamification/shop'),
  inventory: () => apiClient.get<ApiResponse<{ car_inventory: string[]; character_inventory: string[] }>>('/gamification/inventory'),
  buyCarItem: (id: string) => apiClient.post(`/gamification/garage/buy-item/${id}`),
  buyCharacterItem: (id: string) => apiClient.post(`/gamification/shop/character/${id}/buy`),
  buyCharacterAsset: (item: { id: string; name: string; category: string; modelPath?: string }) =>
    apiClient.post('/gamification/shop/character-asset/buy', {
      item_key: item.id,
      name: item.name,
      category: item.category,
      asset_url: item.modelPath || null,
    }),
}

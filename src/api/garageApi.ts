import apiClient from './client'
import {
  defaultGarageSelection,
  garageCategories,
  garageParts,
  type GarageSelection,
} from '@/config/garage'

const unwrap = <T>(response: { data: { data?: T } | T }): T => {
  const payload = response.data as { data?: T }
  return payload.data ?? (response.data as T)
}

export const garageApi = {
  async getConfig() {
    try {
      return unwrap(await apiClient.get('/garage/config'))
    } catch {
      return { categories: garageCategories, parts: garageParts, defaults: defaultGarageSelection }
    }
  },

  async getParts() {
    try {
      return unwrap(await apiClient.get('/garage/parts'))
    } catch {
      return garageParts
    }
  },

  async getPlayerCar(): Promise<GarageSelection> {
    try {
      return unwrap(await apiClient.get('/garage/player-car'))
    } catch {
      return defaultGarageSelection
    }
  },

  async save(selection: GarageSelection) {
    try {
      return unwrap(await apiClient.post('/garage/save', { selection }))
    } catch {
      localStorage.setItem('studypoint.garage.selection', JSON.stringify(selection))
      return { selection, savedOffline: true }
    }
  },

  async randomize(selection: GarageSelection): Promise<GarageSelection> {
    try {
      const result = unwrap<{ selection: GarageSelection }>(
        await apiClient.post('/garage/randomize', { selection })
      )
      return result.selection
    } catch {
      const choose = (category: string) => {
        const items = garageParts[category] ?? []
        return items[Math.floor(Math.random() * items.length)]?.id ?? selection[category as keyof GarageSelection]
      }

      return {
        ...selection,
        body: choose('body') as string,
        rims: choose('rims') as string,
        rimColor: choose('rims') as string,
        paint: choose('paint') as string,
        windowTint: choose('windows') as string,
        stickerColor: choose('stickerColors') as string,
      }
    }
  },
}

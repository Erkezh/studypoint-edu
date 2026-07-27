import body from './body.json'
import wheels from './wheels.json'
import colors from './colors.json'

export type GarageCategoryId =
  | 'body'
  | 'rims'
  | 'windows'
  | 'paint'
  | 'stickerColor'

export type GaragePart = {
  id: string
  name: string
  model?: string | null
  preview?: string | null
  unlockLevel?: number
  rarity?: string
  value?: string
  opacity?: number
}

export type GarageSelection = {
  body: string
  wheels: string
  rims: string
  windows: string
  paint: string
  rimColor: string
  windowTint: string
  stickerColor: string
}

export const garageCategories: Array<{
  id: GarageCategoryId
  label: string
  icon: string
  control: 'parts' | 'paint' | 'rims' | 'windows' | 'stickerColor'
}> = [
  { id: 'body', label: 'Көлік', icon: '/assets/garage-category-car.png', control: 'parts' },
  { id: 'rims', label: 'Диск түсі', icon: '◉', control: 'rims' },
  { id: 'windows', label: 'Әйнек', icon: '▱', control: 'windows' },
  { id: 'paint', label: 'Бояу', icon: '◒', control: 'paint' },
  { id: 'stickerColor', label: 'Стикер түсі', icon: '★', control: 'stickerColor' },
]

export const garageParts: Record<string, GaragePart[]> = {
  body,
  wheels,
  rims: colors.rims,
  windows: colors.windows,
  paint: colors.paint,
  stickerColors: colors.stickerColors,
  stickerColor: colors.stickerColors,
}

export const defaultGarageSelection: GarageSelection = {
  body: 'skateboard',
  wheels: 'wheel4',
  rims: 'ice',
  windows: 'clear',
  paint: 'original',
  rimColor: 'ice',
  windowTint: 'clear',
  stickerColor: 'sticker-black',
}

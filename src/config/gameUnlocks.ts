import type { GameType } from '@/types/api'

export const GAME_UNLOCKS: Record<number, Record<GameType, string>> = {
  1: { car: 'Skateboard and basic parts', character: 'Basic clothes' },
  2: { car: 'Scooter and scooter parts', character: 'Hats' },
  3: { car: 'Bicycle and bicycle parts', character: 'Hairstyles' },
  4: { car: 'Motorbike and motorbike parts', character: 'Shoes' },
  5: { car: 'Quad bike and premium parts', character: 'Premium outfits' },
  6: { car: 'Car and car customization', character: 'Special accessories' },
  7: { car: 'Sports car and advanced parts', character: 'Legendary outfits' },
}

export function nextGameUnlock(game: GameType, level: number) {
  const nextLevel = Object.keys(GAME_UNLOCKS).map(Number).find((candidate) => candidate > level)
  return nextLevel ? { level: nextLevel, label: GAME_UNLOCKS[nextLevel][game] } : null
}

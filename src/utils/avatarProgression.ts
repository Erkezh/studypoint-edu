const presetLevels: Record<string, number> = {
  'default-boy': 1, 'default-girl': 1, glover: 3, hana: 4, kenji: 5,
  jayda: 6, zell: 7, myriad: 9, jackal: 12,
}

const ranges: Record<string, [number, number]> = {
  body: [1, 1], head: [1, 1], eyes: [1, 1],
  hairFront: [1, 12], hairBack: [1, 12], top: [1, 12], bottom: [1, 12], feet: [1, 12],
  eyeBrows: [2, 5], eyeLashes: [2, 5], pupil: [2, 5], eyeShine: [2, 5],
  socks: [3, 9], gloves: [3, 9], leggings: [4, 8],
  headAcc: [5, 10], upperFace: [5, 10], lowerFace: [5, 10], neck: [5, 10], faceDetails: [5, 10],
  overall: [6, 12], makeUpCheeks: [7, 10], makeUpLips: [7, 10],
  underLower: [1, 3], underUpper: [1, 3],
}

const freeItems = new Set([
  'default-boy', 'default-girl', 'Body_BasicBody', 'Head_Young', 'Eyes_Eyes01',
  'Brows_BasicBrows', 'Eyelashes_LongLashes', 'HairFront_ShotaFringe',
  'HairBack_MessyHair', 'Top_TankTop', 'Bottom_SimpleShorts',
])

// Character rewards follow the same 12-level economy as Garage vehicles.
const basePrice = [0, 100, 250, 500, 900, 1400, 2100, 3000, 4200, 6000, 8500, 11000, 13500]

export function avatarItemProgression(item: { id: string; category: string }) {
  const hash = [...item.id].reduce((total, character, index) => total + character.charCodeAt(0) * (index + 1), 0)
  const level = item.category === 'characters'
    ? (presetLevels[item.id] ?? 12)
    : (() => {
        const [minimum, maximum] = ranges[item.category] ?? [2, 12]
        return minimum + (hash % (maximum - minimum + 1))
      })()
  const isFree = freeItems.has(item.id)
  return { requiredLevel: level, price: isFree ? 0 : basePrice[level], isFree }
}

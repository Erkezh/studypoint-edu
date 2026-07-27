export const AVATAR_STORAGE_KEY = 'studypoint-avatar-demo-v2'

export const AVATAR_MANIFEST_URL = '/assets/characters/bozo/manifests/avatar-assets.json'
export const CANONICAL_SKELETON_URL = '/assets/characters/bozo/manifests/canonical-skeleton.json'

export const REQUIRED_CATEGORY_IDS = [
  'body',
  'head',
  'eyes',
  'hairFront',
  'hairBack',
  'top',
  'bottom',
]

export const OPTIONAL_CATEGORY_IDS = [
  'eyeBrows',
  'eyeLashes',
  'socks',
  'gloves',
  'headAcc',
  'upperFace',
  'lowerFace',
  'neck',
  'faceDetails',
  'makeUpCheeks',
  'makeUpLips',
  'pupil',
  'eyeShine',
  'leggings',
]

export const ACTIVE_CATEGORY_IDS = [
  'body',
  'head', 'eyes', 'eyeBrows', 'eyeLashes', 'pupil', 'eyeShine',
  'hairFront', 'hairBack', 'top', 'bottom', 'overall', 'feet', 'socks',
  'gloves', 'headAcc', 'upperFace', 'lowerFace', 'neck',
  'faceDetails', 'makeUpCheeks', 'makeUpLips', 'leggings', 'underLower', 'underUpper',
]

export const CHARACTER_PRESET_CATEGORY = {
  id: 'characters',
  label: 'Кейіпкерлер',
  optional: false,
}

export const CATEGORY_DEFINITIONS = {
  body: { id: 'body', manifestType: 'Body', label: 'Дене', optional: false },
  head: { id: 'head', manifestType: 'Head', label: 'Бас', optional: false },
  eyes: { id: 'eyes', manifestType: 'Eyes', label: 'Көздер', optional: false },
  eyeBrows: { id: 'eyeBrows', manifestType: 'EyeBrows', label: 'Қастар', optional: true },
  eyeLashes: { id: 'eyeLashes', manifestType: 'EyeLashes', label: 'Кірпіктер', optional: true },
  hairFront: { id: 'hairFront', manifestType: 'HairFront', label: 'Алдыңғы шаш', optional: false },
  hairBack: { id: 'hairBack', manifestType: 'HairBack', label: 'Артқы шаш', optional: false },
  top: { id: 'top', manifestType: 'Top', label: 'Үстіңгі киім', optional: false },
  bottom: { id: 'bottom', manifestType: 'Bottom', label: 'Астыңғы киім', optional: false },
  feet: { id: 'feet', manifestType: 'Feet', label: 'Аяқкиім', optional: true },
  socks: { id: 'socks', manifestType: 'Socks', label: 'Шұлықтар', optional: true },
  gloves: { id: 'gloves', manifestType: 'Gloves', label: 'Қолғаптар', optional: true },
  headAcc: { id: 'headAcc', manifestType: 'HeadAcc', label: 'Бас аксессуарлары', optional: true },
  upperFace: { id: 'upperFace', manifestType: 'UpperFace', label: 'Көзілдіріктер', optional: true },
  lowerFace: { id: 'lowerFace', manifestType: 'LowerFace', label: 'Бет аксессуарлары', optional: true },
  neck: { id: 'neck', manifestType: 'Neck', label: 'Мойын аксессуарлары', optional: true },
  faceDetails: { id: 'faceDetails', manifestType: 'FaceDetails', label: 'Бет бөлшектері', optional: true },
  makeUpCheeks: { id: 'makeUpCheeks', manifestType: 'MakeUpCheeks', label: 'Бет әрлеуі', optional: true },
  makeUpLips: { id: 'makeUpLips', manifestType: 'MakeUpLips', label: 'Ерін әрлеуі', optional: true },
  pupil: { id: 'pupil', manifestType: 'Pupil', label: 'Қарашық', optional: true },
  eyeShine: { id: 'eyeShine', manifestType: 'EyeShine', label: 'Көз жарқылы', optional: true },
  leggings: { id: 'leggings', manifestType: 'Leggings', label: 'Легинстер', optional: true },
  overall: { id: 'overall', manifestType: 'Overall', label: 'Толық киім', optional: true },
  underLower: { id: 'underLower', manifestType: 'UnderLower', label: 'Ішкі астыңғы киім', optional: true },
  underUpper: { id: 'underUpper', manifestType: 'UnderUpper', label: 'Ішкі үстіңгі киім', optional: true },
  modular: { id: 'modular', manifestType: 'modular', label: 'Біріктірілген', optional: true },
}

export const DEFAULT_ITEM_NAMES = {
  body: 'Body_BasicBody',
  head: 'Head_Young',
  eyes: 'Eyes_Eyes01',
  eyeBrows: 'Brows_BasicBrows',
  eyeLashes: 'Eyelashes_LongLashes',
  hairFront: 'HairFront_ShotaFringe',
  hairBack: 'HairBack_MessyHair',
  top: 'Top_TankTop',
  bottom: 'Bottom_SimpleShorts',
}

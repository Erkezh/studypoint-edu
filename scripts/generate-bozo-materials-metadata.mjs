import fs from 'node:fs'
import path from 'node:path'

const unityAssets = process.env.BOZO_UNITY_ASSETS || '/Users/ayaulyzhumakan/CharacterCustomization/Assets'
const packageRoot = path.join(unityAssets, 'BoZo_ModularAnimeCharacters')
const manifestPath = 'public/assets/characters/bozo/manifests/avatar-assets.json'
const outputPath = 'public/assets/characters/bozo/manifests/materials.json'
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'))

function walk(folder, extension, result = []) {
  for (const entry of fs.readdirSync(folder, { withFileTypes: true })) {
    const file = path.join(folder, entry.name)
    if (entry.isDirectory()) walk(file, extension, result)
    else if (file.endsWith(extension)) result.push(file)
  }
  return result
}

const wanted = new Set(manifest.assets.flatMap((asset) => asset.materials || []))
const materialFiles = new Map()
for (const file of walk(packageRoot, '.mat')) {
  const text = fs.readFileSync(file, 'utf8')
  for (const name of [...text.matchAll(/^  m_Name: (.+)$/gm)].map((match) => match[1].trim()).filter(Boolean)) {
    if (wanted.has(name)) materialFiles.set(name, { file, text })
  }
}

function rgbHex(color) {
  const values = ['r', 'g', 'b'].map((key) => Math.round(Math.max(0, Math.min(1, color[key])) * 255))
  return `#${values.map((value) => value.toString(16).padStart(2, '0')).join('')}`
}

function parseMaterial(name, source) {
  const colors = Object.fromEntries(
    [...source.text.matchAll(/^    - (_[A-Za-z0-9_]+): \{r: ([^,]+), g: ([^,]+), b: ([^,]+), a: ([^}]+)\}$/gm)].map((match) => {
      const value = { r: +match[2], g: +match[3], b: +match[4], a: +match[5] }
      return [match[1], { ...value, hex: rgbHex(value) }]
    }),
  )
  const floats = Object.fromEntries(
    [...source.text.matchAll(/^    - (_[A-Za-z0-9_]+): (-?[0-9.]+)$/gm)].map((match) => [match[1], +match[2]]),
  )
  const textures = manifest.assets.filter((entry) => entry.materials?.includes(name)).flatMap((entry) => entry.textures || [])
  const textureFor = (property) => {
    const marker = `__${property.replace(/^_/, '')}_`
    return textures.find((file) => file.split('/').pop()?.startsWith(`${name}${marker}`))
      || textures.find((file) => file.includes(marker))
      || ''
  }
  const hasKeyword = (keyword) => source.text.includes(`  - ${keyword}`)
  const useCustomTexture = floats._UseCustomTexture ?? (hasKeyword('_USECUSTOMTEXTURE') ? 1 : 0)
  return {
    material: name,
    sourceMaterial: source.file.slice(unityAssets.length + 1).replaceAll('\\', '/'),
    shader: 'BoZo/BMAC_Toon',
    baseTexture: textureFor('_Texture2D'),
    normalTexture: textureFor('_NormalMap'),
    maskTexture: textureFor('_IDMap'),
    colorChannels: Object.fromEntries(Array.from({ length: 9 }, (_, index) => {
      const key = `_Color_${index + 1}`
      return [key, colors[key] || { r: 0, g: 0, b: 0, a: 0, hex: '#000000' }]
    })),
    baseColor: colors._BaseColor || { r: 1, g: 1, b: 1, a: 0, hex: '#ffffff' },
    alphaMode: 'MASK',
    alphaCutoff: 0.5,
    doubleSided: (floats._Culling ?? 2) === 0 || /\/(HairFront|HairBack|EyeLashes)\//.test(source.file.replaceAll('\\', '/')),
    vertexColors: useCustomTexture !== 0,
    flipY: /\/(HairFront|HairBack|EyeLashes)\//.test(source.file.replaceAll('\\', '/')),
    useCustomTexture: useCustomTexture !== 0,
    useNormalMap: (floats._UseNormalMap ?? (hasKeyword('_USENORMALMAP') ? 1 : 0)) !== 0,
    pattern: {
      enabled: (floats._PatternBlend ?? 0) > 0,
      blend: floats._PatternBlend ?? 0,
      uvSet: floats._PatternUVSet ?? 0,
      texture: textureFor('_PatternMap'),
      colors: ['_PatternColor_1', '_PatternColor_2', '_PatternColor_3'].map((key) => colors[key]).filter(Boolean),
    },
    decal: {
      enabled: (floats._DecalBlend ?? 0) > 0,
      blend: floats._DecalBlend ?? 0,
      uvSet: floats._DecalUVSet ?? 0,
      texture: textureFor('_DecalMap'),
      colors: ['_DecalColor_1', '_DecalColor_2', '_DecalColor_3'].map((key) => colors[key]).filter(Boolean),
    },
  }
}

const materials = {}
for (const name of [...wanted].sort()) {
  const source = materialFiles.get(name)
  if (source) materials[name] = parseMaterial(name, source)
}

fs.writeFileSync(outputPath, `${JSON.stringify({ generatedUtc: new Date().toISOString(), shaderModel: 'BoZo/BMAC_Toon', materials }, null, 2)}\n`)
console.log(`Wrote ${Object.keys(materials).length} BoZo materials to ${outputPath}`)

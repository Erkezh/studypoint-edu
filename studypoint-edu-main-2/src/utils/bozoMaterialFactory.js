import * as THREE from 'three'

const metadataUrl = '/assets/characters/bozo/manifests/materials.json'
const textureLoader = new THREE.TextureLoader()
const textureCache = new Map()
let metadataPromise = null

function loadMetadata() {
  if (!metadataPromise) {
    const url = import.meta.env.DEV ? `${metadataUrl}?v=${Date.now()}` : metadataUrl
    metadataPromise = fetch(url).then((response) => {
      if (!response.ok) throw new Error(`Unable to load BoZo material metadata (${response.status})`)
      return response.json()
    })
  }
  return metadataPromise
}

function loadTexture(path, colorSpace, flipY = false) {
  if (!path) return Promise.resolve(null)
  const cacheKey = `${path}|flip:${flipY}`
  if (!textureCache.has(cacheKey)) {
    textureCache.set(cacheKey, textureLoader.loadAsync(path).then((texture) => {
      texture.userData.avatarCached = true
      texture.flipY = flipY
      texture.colorSpace = colorSpace
      texture.wrapS = THREE.RepeatWrapping
      texture.wrapT = THREE.RepeatWrapping
      return texture
    }))
  }
  return textureCache.get(cacheKey)
}

function colorValue(metadata, index, presetColors) {
  const preset = presetColors?.[index - 1]
  if (preset) return new THREE.Color(preset.r ?? 0, preset.g ?? 0, preset.b ?? 0)
  const value = metadata.colorChannels?.[`_Color_${index}`] || {}
  return new THREE.Color(value.r || 0, value.g || 0, value.b || 0)
}

function installBoZoShader(material, metadata, channelTexture, presetColors) {
  const colors = Array.from({ length: 9 }, (_, index) => colorValue(metadata, index + 1, presetColors))
  material.map = null
  material.color.set(0xffffff)
  material.vertexColors = false
  material.alphaTest = metadata.alphaCutoff ?? 0.5
  material.transparent = metadata.alphaMode === 'BLEND'
  material.side = metadata.doubleSided ? THREE.DoubleSide : THREE.FrontSide
  material.userData.bozoMaterial = metadata
  material.onBeforeCompile = (shader) => {
    shader.uniforms.bozoChannelMap = { value: channelTexture }
    colors.forEach((color, index) => { shader.uniforms[`bozoColor${index + 1}`] = { value: color } })
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', '#include <common>\nattribute vec4 color;\nvarying vec4 vBoZoColor;\nvarying vec2 vBoZoUv;')
      .replace('#include <begin_vertex>', '#include <begin_vertex>\nvBoZoColor = color;\nvBoZoUv = uv;')
    const colorReconstruction = metadata.useCustomTexture ? `
vec4 bozoMask = texture2D(bozoChannelMap, vBoZoUv);
vec3 bozoGroup1 = bozoMask.r * bozoColor1 + bozoMask.g * bozoColor2 + bozoMask.b * bozoColor3;
vec3 bozoGroup2 = bozoMask.r * bozoColor4 + bozoMask.g * bozoColor5 + bozoMask.b * bozoColor6;
vec3 bozoGroup3 = bozoMask.r * bozoColor7 + bozoMask.g * bozoColor8 + bozoMask.b * bozoColor9;
vec3 bozoLayer1 = bozoGroup1 * vBoZoColor.r;
vec3 bozoLayer2 = mix(bozoLayer1, bozoGroup2, vBoZoColor.g);
vec3 bozoFinal = mix(bozoLayer2, bozoGroup3, vBoZoColor.b);
diffuseColor = vec4(bozoFinal, bozoMask.a);
` : 'diffuseColor = texture2D(bozoChannelMap, vBoZoUv);'
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', `#include <common>
uniform sampler2D bozoChannelMap;
varying vec4 vBoZoColor;
varying vec2 vBoZoUv;
${colors.map((_, index) => `uniform vec3 bozoColor${index + 1};`).join('\n')}`)
      .replace('#include <map_fragment>', colorReconstruction)
  }
  material.customProgramCacheKey = () => `bozo-bmac-toon-v1-${metadata.material}`
  material.needsUpdate = true
}

export async function applyBoZoMaterials(root, item) {
  const metadataManifest = await loadMetadata()
  const jobs = []
  root.traverse((object) => {
    if ((!object.isMesh && !object.isSkinnedMesh) || !object.material) return
    const vertexColors = object.geometry?.getAttribute?.('color')
    if (vertexColors && (vertexColors.array instanceof Uint8Array || vertexColors.array instanceof Uint16Array)) {
      vertexColors.normalized = true
      vertexColors.needsUpdate = true
    }
    const materials = Array.isArray(object.material) ? object.material : [object.material]
    for (const material of materials) {
      const metadata = metadataManifest.materials?.[material.name]
      if (!metadata) {
        console.error('[bozo-material] Missing exported metadata', { itemId: item.id, meshName: object.name, materialName: material.name })
        continue
      }
      jobs.push(Promise.all([
        // These PNGs are sampled by GLB-authored UVs. TextureLoader's image
        // convention must therefore match GLTFLoader: do not vertically flip.
        loadTexture(metadata.baseTexture, THREE.NoColorSpace, false),
        loadTexture(metadata.normalTexture, THREE.NoColorSpace, false),
      ]).then(([channelTexture, normalTexture]) => {
        if (!channelTexture) throw new Error(`${item.id}/${material.name}: missing _Texture2D channel texture`)
        installBoZoShader(material, metadata, channelTexture, item.presetColors)
        material.normalMap = normalTexture
        if (import.meta.env.DEV) console.info('[bozo-material]', {
          itemId: item.id,
          meshName: object.name || object.type,
          materialName: material.name,
          shader: metadata.shader,
          sourceMaterial: metadata.sourceMaterial,
          channelTexture: metadata.baseTexture,
          idMap: metadata.maskTexture,
          colors: metadata.colorChannels,
          presetColors: item.presetColors || null,
          vertexColorRole: 'selects BoZo color group 1/2/3',
          alphaMode: metadata.alphaMode,
          alphaCutoff: metadata.alphaCutoff,
          doubleSided: metadata.doubleSided,
        })
      }))
    }
  })
  await Promise.all(jobs)
}

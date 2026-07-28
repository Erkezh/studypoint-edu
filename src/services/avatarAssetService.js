import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { clone as cloneSkeleton } from 'three/addons/utils/SkeletonUtils.js'
import { AVATAR_MANIFEST_URL, CANONICAL_SKELETON_URL, CATEGORY_DEFINITIONS } from '@/data/avatarDefaults'

const browserAssetPrefix = '/assets/characters/bozo/'
const characterPresetsUrl = `${browserAssetPrefix}presets/character-presets.json`
const categoryByManifestType = new Map(
  Object.values(CATEGORY_DEFINITIONS).map((category) => [category.manifestType, category]),
)

let manifestPromise = null
let loader = null
const gltfCache = new Map()

// Keep broken or unsuitable exports out of the student-facing selector without
// modifying the original BoZo package or deleting its runtime files.
const HIDDEN_SELECTOR_ASSETS = new Set([
  'UpperFace_MedicalEyePatch',
])

function getLoader() {
  if (!loader) loader = new GLTFLoader()
  return loader
}

function warn(message, value) {
  if (import.meta.env.DEV) {
    console.warn(`[avatar-assets] ${message}`, value)
  }
}

function makeId(value) {
  return String(value || '')
    .trim()
    .replace(/[^a-zA-Z0-9_-]+/g, '-')
}

function normalizePath(path, folder) {
  if (typeof path !== 'string' || !path) return ''
  if (path.startsWith(browserAssetPrefix)) return path
  const normalized = path.replace(/\\/g, '/')
  const marker = `${folder}/`
  const index = normalized.indexOf(marker)
  return index === -1 ? normalized : `${browserAssetPrefix}${normalized.slice(index)}`
}

function normalizeRecord(record, index) {
  const category = categoryByManifestType.get(record.outfitType || record.kind)
  const modelPath = normalizePath(record.modelPath, 'models')
  const hasLocalAbsolutePath = modelPath.startsWith('/Users/') || modelPath.startsWith('/Volumes/')

  if (!record.name || !category || !modelPath || hasLocalAbsolutePath) {
    warn('Skipping malformed manifest item', { index, record })
    return null
  }

  const texturePaths = Array.isArray(record.textures)
    ? record.textures.map((texture) => normalizePath(texture, 'textures')).filter(Boolean)
    : []

  return {
    id: makeId(record.name),
    name: record.outfitName || record.name,
    sourceName: record.name,
    category: category.id,
    categoryLabel: category.label,
    modelPath,
    texturePaths,
    materialName: Array.isArray(record.materials) ? record.materials[0] || '' : '',
    compatibleBodyType: record.compatibleBodyType || '',
    thumbnailPath: normalizePath(record.thumbnailPath, 'textures') || '',
    metadata: {
      kind: record.kind || '',
      outfitType: record.outfitType || '',
      attachPoint: record.attachPoint || '',
      supportsDecals: Boolean(record.supportsDecals),
      supportsPatterns: Boolean(record.supportsPatterns),
      rendererCount: record.rendererCount || 0,
      skinnedMeshCount: record.skinnedMeshCount || 0,
      blendShapeCount: record.blendShapeCount || 0,
      colorChannels: Array.isArray(record.colorChannels) ? record.colorChannels : [],
      tags: Array.isArray(record.tags) ? record.tags : [],
      sourcePath: record.sourcePath || '',
      materials: Array.isArray(record.materials) ? record.materials : [],
      canonicalSkeletonId: record.canonicalSkeletonId || '',
      jointCount: record.jointCount || 0,
      requiredBones: Array.isArray(record.requiredBones) ? record.requiredBones : [],
      validationStatus: record.validationStatus || '',
      attachment: record.attachment || null,
      hideCategories: Array.isArray(record.hideCategories) ? record.hideCategories : [],
      hideItems: Array.isArray(record.hideItems) ? record.hideItems : [],
      compatibleHair: Array.isArray(record.compatibleHair) ? record.compatibleHair : [],
      incompatibleHair: Array.isArray(record.incompatibleHair) ? record.incompatibleHair : [],
      hatFit: record.hatFit || null,
    },
  }
}

function groupItems(items) {
  const groups = {}
  for (const item of items) {
    if (!groups[item.category]) groups[item.category] = []
    groups[item.category].push(item)
  }

  for (const group of Object.values(groups)) {
    group.sort((a, b) => a.name.localeCompare(b.name))
  }

  return groups
}

export async function loadAvatarManifest() {
  if (manifestPromise) return manifestPromise

  manifestPromise = fetch(AVATAR_MANIFEST_URL)
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`Unable to load avatar manifest (${response.status})`)
      }
      return response.json()
    })
    .then(async (manifest) => {
      if (!manifest || !Array.isArray(manifest.assets)) {
        throw new Error('Avatar manifest is missing an assets array')
      }

      const items = manifest.assets
        // Only Unity Resources prefabs are selectable modular parts. The raw
        // export also contains complete preview/capture prefabs whose inferred
        // outfitType is HairFront; loading those stacks an entire second avatar.
        .filter((record) => record.sourcePath?.replace(/\\/g, '/').includes('/Resources/'))
        .filter((record) => !HIDDEN_SELECTOR_ASSETS.has(record.name))
        .map((record, index) => normalizeRecord(record, index))
        .filter(Boolean)
        .filter((item) => item.metadata.validationStatus === 'passed')
        .filter((item) => item.metadata.rendererCount > 0)

      const skeletonResponse = await fetch(`${CANONICAL_SKELETON_URL}?v=${encodeURIComponent(manifest.generatedUtc || '1')}`)
      if (!skeletonResponse.ok) throw new Error(`Unable to load canonical skeleton (${skeletonResponse.status})`)
      const canonicalSkeleton = await skeletonResponse.json()
      if (canonicalSkeleton.id !== 'BoZo.Body_BasicBody.Canonical.v1' || canonicalSkeleton.jointCount !== 122) {
        throw new Error('Canonical skeleton metadata is invalid')
      }

      const presetsResponse = await fetch(characterPresetsUrl)
      if (!presetsResponse.ok) throw new Error(`Unable to load BoZo character presets (${presetsResponse.status})`)
      const presetManifest = await presetsResponse.json()
      const presets = (presetManifest.presets || []).map((preset) => ({
        ...preset,
        category: 'characters',
        categoryLabel: 'Characters',
        thumbnailPath: preset.thumbnail,
      }))
      const groups = groupItems(items)
      groups.characters = presets

      return {
        url: AVATAR_MANIFEST_URL,
        generatedUtc: manifest.generatedUtc || '',
        version: manifest.generatedUtc || '1',
        canonicalSkeleton,
        items,
        presets,
        groups,
        rawCount: manifest.assets.length,
      }
    })

  return manifestPromise
}

export async function loadAvatarGltf(modelPath, onProgress) {
  if (!modelPath?.startsWith(browserAssetPrefix)) {
    throw new Error(`Invalid avatar model path: ${modelPath}`)
  }

  const manifest = await loadAvatarManifest()
  const versionedPath = import.meta.env.DEV
    ? `${modelPath}${modelPath.includes('?') ? '&' : '?'}v=${encodeURIComponent(manifest.version)}`
    : modelPath
  if (!gltfCache.has(versionedPath)) {
    const promise = getLoader().loadAsync(versionedPath, onProgress)
    gltfCache.set(versionedPath, promise)
  }

  return gltfCache.get(versionedPath)
}

export async function cloneAvatarScene(modelPath, onProgress) {
  const gltf = await loadAvatarGltf(modelPath, onProgress)
  const scene = cloneSkeleton(gltf.scene)
  scene.traverse((object) => {
    if (!object.isMesh && !object.isSkinnedMesh) return
    if (object.geometry) object.geometry = object.geometry.clone()
    if (Array.isArray(object.material)) {
      object.material = object.material.map((material) => material?.clone?.() || material)
    } else if (object.material) {
      object.material = object.material.clone()
    }
  })
  scene.userData.animations = gltf.animations || []
  return scene
}

export function getAvatarCacheInfo() {
  return {
    entries: [...gltfCache.keys()],
    size: gltfCache.size,
  }
}

export function clearAvatarGltfCache() {
  gltfCache.clear()
}

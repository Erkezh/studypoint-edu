<!-- @vue-ignore -->
<template>
  <div ref="host" class="garage-scene" aria-label="StudyPoint 3D гаражы">
    <div v-if="!finished" class="garage-scene__hint">айналдыру үшін сүйре • жақындату үшін скролл</div>
  </div>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'
import { clone as cloneSkeleton } from 'three/examples/jsm/utils/SkeletonUtils.js'
import type { GaragePart } from '@/config/garage'

const props = defineProps<{
  body?: GaragePart
  bodyOptions?: GaragePart[]
  wheel?: GaragePart
  paintColor?: string
  rimColor: string
  windowColor?: string
  windowOpacity?: number
  stickerColor: string
  lockedPreview?: boolean
  finished: boolean
}>()

const emit = defineEmits<{
  ready: []
}>()

const host = ref<HTMLDivElement | null>(null)
const bodyModel = ref<THREE.Object3D | null>(null)
const wheelModel = ref<THREE.Object3D | null>(null)

let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let controls: OrbitControls | null = null
let frameId = 0
let resizeObserver: ResizeObserver | null = null
let carRig: THREE.Group | null = null
let wheelRig: THREE.Group | null = null
let platform: THREE.Group | null = null
let loader: GLTFLoader | null = null
let clock: THREE.Clock | null = null
let bodyLoadVersion = 0
let preloadVersion = 0
let lastSceneWidth = 0

const modelCache = new Map<string, Promise<THREE.Object3D>>()

const materialTargets = computed(() => ({
  paint: props.paintColor ? new THREE.Color(props.paintColor) : null,
  rim: new THREE.Color(props.rimColor),
  window: new THREE.Color(props.windowColor ?? '#bdefff'),
  sticker: new THREE.Color(props.stickerColor),
}))

const isBikeBody = computed(() => {
  const label = `${props.body?.id ?? ''} ${props.body?.model ?? ''}`.toLowerCase()
  return (
    label.includes('bike') ||
    label.includes('btwin') ||
    label.includes('triban') ||
    label.includes('ducati') ||
    label.includes('streetfighter') ||
    label.includes('suzuki') ||
    label.includes('quadzilla') ||
    label.includes('scooter') ||
    label.includes('e2f') ||
    label.includes('sport-bike') ||
    label.includes('sport_bike') ||
    label.includes('concept-sport') ||
    label.includes('skateboard') ||
    label.includes('motobike') ||
    label.includes('motorbike')
  )
})

const isSkateboardBody = computed(() => {
  const label = `${props.body?.id ?? ''} ${props.body?.model ?? ''}`.toLowerCase()
  return label.includes('skateboard')
})

const isScooterBody = computed(() => {
  const label = `${props.body?.id ?? ''} ${props.body?.model ?? ''}`.toLowerCase()
  return label.includes('scooter') || label.includes('e2f')
})

const isDucatiBody = computed(() => {
  const label = `${props.body?.id ?? ''} ${props.body?.model ?? ''}`.toLowerCase()
  return label.includes('ducati') || label.includes('streetfighter')
})

const isSuzukiBody = computed(() => {
  const label = `${props.body?.id ?? ''} ${props.body?.model ?? ''}`.toLowerCase()
  return label.includes('suzuki') || label.includes('quadzilla')
})

const isMustangBody = computed(() => {
  const label = `${props.body?.id ?? ''} ${props.body?.model ?? ''}`.toLowerCase()
  return label.includes('mustang') || label.includes('cobra') || label.includes('gt500')
})

const isMiniCarBody = computed(() => {
  const label = `${props.body?.id ?? ''} ${props.body?.model ?? ''}`.toLowerCase()
  return label.includes('mini-car') || label.includes('mini_car') || label.includes('low-poly')
})

const isVinoBody = computed(() => {
  const label = `${props.body?.id ?? ''} ${props.body?.model ?? ''}`.toLowerCase()
  return label.includes('vino')
})

const isConceptSportBikeBody = computed(() => {
  const label = `${props.body?.id ?? ''} ${props.body?.model ?? ''}`.toLowerCase()
  return label.includes('sport-bike') || label.includes('sport_bike') || label.includes('concept-sport')
})

const isMcLarenBody = computed(() => {
  const label = `${props.body?.id ?? ''} ${props.body?.model ?? ''}`.toLowerCase()
  return label.includes('mclaren') || label.includes('720s')
})

const isPorscheBody = computed(() => {
  const label = `${props.body?.id ?? ''} ${props.body?.model ?? ''}`.toLowerCase()
  return label.includes('porsche') || label.includes('963') || label.includes('lmdh')
})

type GarageMaterialRole = 'paint' | 'rim' | 'window' | 'sticker' | 'other'

type OriginalMaterialState = {
  color: THREE.Color
  map: THREE.Texture | null
  opacity: number
  transparent: boolean
  roughness?: number
  metalness?: number
  envMapIntensity?: number
}

const stickerMaskCache = new WeakMap<THREE.Texture, Map<string, THREE.Texture | null>>()
const cleanPaintTextureCache = new WeakMap<THREE.Texture, THREE.Texture | null>()

onMounted(() => {
  if (!host.value) return

  scene = new THREE.Scene()
  scene.background = new THREE.Color('#ecebff')
  scene.fog = new THREE.Fog('#ecebff', 9, 24)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' })
  const sceneWidth = host.value.getBoundingClientRect().width
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, sceneWidth <= 720 ? 1.25 : 2))
  renderer.shadowMap.enabled = sceneWidth > 720
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 0.88
  renderer.outputColorSpace = THREE.SRGBColorSpace
  host.value.appendChild(renderer.domElement)

  camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100)
  camera.position.set(4.9, 2.45, 7.35)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.08
  controls.minDistance = 4.8
  controls.maxDistance = 10.5
  controls.maxPolarAngle = Math.PI * 0.49
  controls.target.set(0, 0.25, 0)

  const pmrem = new THREE.PMREMGenerator(renderer)
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture
  scene.environmentIntensity = 0.35

  loader = new GLTFLoader()
  clock = new THREE.Clock()
  carRig = new THREE.Group()
  wheelRig = new THREE.Group()
  platform = new THREE.Group()
  scene.add(platform, carRig, wheelRig)

  buildGarage(scene, platform)
  loadBody()
  preloadBodyModels()
  loadWheels()

  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(host.value)
  resize()
  animate()
  emit('ready')
})

onBeforeUnmount(() => {
  cancelAnimationFrame(frameId)
  resizeObserver?.disconnect()
  controls?.dispose()
  renderer?.dispose()
  if (renderer?.domElement.parentElement) renderer.domElement.parentElement.removeChild(renderer.domElement)
})

watch(
  () => props.body?.model,
  () => {
    loadBody()
    preloadBodyModels()
    loadWheels()
  }
)
watch(() => props.bodyOptions, preloadBodyModels)
watch(() => props.wheel?.model, loadWheels)
watch(materialTargets, applyMaterials)
watch(() => props.lockedPreview, applyMaterials)
watch(() => props.finished, moveCameraForFinish)

function buildGarage(targetScene: THREE.Scene, targetPlatform: THREE.Group) {
  const ambient = new THREE.HemisphereLight('#ffffff', '#c7d2fe', 0.72)
  targetScene.add(ambient)

  const key = new THREE.DirectionalLight('#ffffff', 1.38)
  key.position.set(5, 6, 4)
  key.castShadow = true
  key.shadow.mapSize.set(2048, 2048)
  targetScene.add(key)

  const fill = new THREE.DirectionalLight('#99f6e4', 0.36)
  fill.position.set(-4, 3, 2)
  targetScene.add(fill)

  const rim = new THREE.DirectionalLight('#c7c4ff', 0.24)
  rim.position.set(0, 2, -5)
  targetScene.add(rim)

  buildPodium(targetPlatform)

  const particles = new THREE.BufferGeometry()
  const positions = new Float32Array(180 * 3)
  for (let i = 0; i < positions.length; i += 3) {
    positions[i] = (Math.random() - 0.5) * 10
    positions[i + 1] = Math.random() * 4
    positions[i + 2] = (Math.random() - 0.5) * 8
  }
  particles.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  targetScene.add(
    new THREE.Points(
      particles,
      new THREE.PointsMaterial({ color: '#14b8a6', size: 0.014, transparent: true, opacity: 0.16 })
    )
  )
}

function buildPodium(targetPlatform: THREE.Group) {
  const podiumBody = new THREE.MeshStandardMaterial({
    color: '#c7c4ff',
    metalness: 0.24,
    roughness: 0.54,
  })
  const podiumTop = new THREE.MeshStandardMaterial({
    color: '#fff1b8',
    metalness: 0.18,
    roughness: 0.46,
  })
  const accent = new THREE.MeshBasicMaterial({ color: '#14b8a6' })

  const ground = new THREE.Mesh(
    new THREE.CircleGeometry(5.5, 64),
    new THREE.MeshStandardMaterial({ color: '#d9f7f3', metalness: 0.08, roughness: 0.72 })
  )
  ground.rotation.x = -Math.PI / 2
  ground.position.y = -0.84
  ground.receiveShadow = true
  targetPlatform.add(ground)

  const base = new THREE.Mesh(new THREE.CylinderGeometry(3.15, 3.45, 0.22, 48), podiumBody)
  base.position.y = -0.73
  base.castShadow = true
  base.receiveShadow = true
  targetPlatform.add(base)

  const stem = new THREE.Mesh(new THREE.CylinderGeometry(2.15, 2.65, 0.55, 48), podiumBody)
  stem.position.y = -0.345
  stem.castShadow = true
  targetPlatform.add(stem)

  const top = new THREE.Mesh(new THREE.CylinderGeometry(2.45, 2.45, 0.12, 64), podiumTop)
  top.position.y = -0.06
  top.castShadow = true
  top.receiveShadow = true
  targetPlatform.add(top)

  const edgeRing = new THREE.Mesh(new THREE.TorusGeometry(2.45, 0.022, 8, 64), accent)
  edgeRing.rotation.x = Math.PI / 2
  edgeRing.position.y = 0.015
  targetPlatform.add(edgeRing)

  const underGlow = new THREE.Mesh(
    new THREE.TorusGeometry(2.48, 0.012, 8, 64),
    new THREE.MeshBasicMaterial({ color: '#14b8a6', transparent: true, opacity: 0.24 })
  )
  underGlow.rotation.x = Math.PI / 2
  underGlow.position.y = -0.08
  targetPlatform.add(underGlow)
}

async function loadBody() {
  if (!loader || !carRig || !props.body?.model) return
  const activeLoad = ++bodyLoadVersion
  const body = props.body
  try {
    const model = cloneSkeleton(await ensureCachedModel(props.body.model, loader))
    if (activeLoad !== bodyLoadVersion) return
    bodyModel.value = model
    normalizeModel(
      model,
      isSkateboardBody.value
        ? 2.75
        : isScooterBody.value
          ? 1.55
          : isDucatiBody.value
            ? 2.35
            : isSuzukiBody.value
              ? 2.65
              : isMiniCarBody.value
                ? 2.15
                : isVinoBody.value
                  ? 2.55
                  : isConceptSportBikeBody.value
                    ? 2.35
                    : isMcLarenBody.value
                      ? 3.25
                      : isPorscheBody.value
                        ? 2.65
                        : isMustangBody.value
                          ? 3.35
                          : isBikeBody.value
                            ? 2.9
                            : 3.55
    )
    placeModelOnPodium(model, isBikeBody.value ? 0.08 : 0.04)
    model.traverse((node) => {
      if (node instanceof THREE.Mesh) {
        node.castShadow = true
        node.receiveShadow = true
      }
    })
    clearGroup(carRig)
    carRig.add(model)
    resetGarageView()
    preserveOriginalMaterials(model)
    applyMaterials()
  } catch {
    if (activeLoad !== bodyLoadVersion) return
    bodyModel.value = null
    clearGroup(carRig)
    console.warn(`Garage body failed to load: ${body.name}`)
  }
}

async function ensureCachedModel(modelPath: string, activeLoader: GLTFLoader) {
  if (!modelCache.has(modelPath)) {
    modelCache.set(
      modelPath,
      activeLoader.loadAsync(modelPath).then((gltf) => gltf.scene)
    )
  }
  const source = await modelCache.get(modelPath)
  if (!source) throw new Error(`Missing cached model: ${modelPath}`)
  return source
}

async function preloadBodyModels() {
  if (!loader) return
  const models = buildPreloadQueue()
  if (!models.length) return
  const activePreload = ++preloadVersion

  for (const modelPath of models) {
    if (activePreload !== preloadVersion) return
    try {
      await ensureCachedModel(modelPath, loader)
    } catch {
      // A failed preload should not block the visible garage.
    }
  }
}

function buildPreloadQueue() {
  const bodyOptions = props.bodyOptions ?? []
  const currentModel = props.body?.model
  const modelPaths = bodyOptions.map((part) => part.model).filter((model): model is string => Boolean(model))
  const currentIndex = modelPaths.findIndex((model) => model === currentModel)
  const orderedModels: string[] = []
  const priorityModels = modelPaths.filter(
    (modelPath) =>
      modelPath !== currentModel &&
      (modelPath.includes('porsche_963_lmdh_hypercar') || modelPath.includes('mclaren_720s_spider'))
  )

  orderedModels.push(...priorityModels)

  if (currentIndex >= 0) {
    for (let distance = 1; distance < modelPaths.length; distance += 1) {
      const next = modelPaths[currentIndex + distance]
      const previous = modelPaths[currentIndex - distance]
      if (next) orderedModels.push(next)
      if (previous) orderedModels.push(previous)
    }
  } else {
    orderedModels.push(...modelPaths)
  }

  return [...new Set(orderedModels)].filter((modelPath) => modelPath !== currentModel && !modelCache.has(modelPath))
}

async function loadWheels() {
  if (!wheelRig) return
  clearGroup(wheelRig)
  wheelModel.value = null
}

function normalizeModel(model: THREE.Object3D, targetSize: number) {
  const box = new THREE.Box3().setFromObject(model)
  const size = box.getSize(new THREE.Vector3())
  const maxAxis = Math.max(size.x, size.y, size.z)
  if (maxAxis > 0) model.scale.multiplyScalar(targetSize / maxAxis)
  box.setFromObject(model)
  const center = box.getCenter(new THREE.Vector3())
  model.position.sub(center)
}

function placeModelOnPodium(model: THREE.Object3D, clearance: number) {
  const box = new THREE.Box3().setFromObject(model)
  model.position.y += clearance - box.min.y
}

function resetGarageView() {
  if (carRig) carRig.rotation.y = 0
  if (!camera || !controls) return
  fitCameraToScene()
  controls.update()
}

function fitCameraToScene() {
  if (!host.value || !camera || !controls) return
  const { width } = host.value.getBoundingClientRect()
  const isPhone = width <= 720
  const isNarrowPhone = width <= 430

  if (isPhone) {
    camera.fov = isNarrowPhone ? 31 : 33
    camera.position.set(2.05, 1.35, isNarrowPhone ? 4.35 : 4.75)
    controls.target.set(0, 0.48, 0)
    controls.minDistance = 3.6
    controls.maxDistance = 8.2
  } else {
    camera.fov = 35
    camera.position.set(4.9, 2.45, 7.35)
    controls.target.set(0, 0.25, 0)
    controls.minDistance = 4.8
    controls.maxDistance = 10.5
  }

  camera.updateProjectionMatrix()
}

function preserveOriginalMaterials(root: THREE.Object3D) {
  const paintMeshes: THREE.Mesh[] = []

  root.traverse((node) => {
    if (!(node instanceof THREE.Mesh)) return
    node.material = cloneMeshMaterials(node.material, node.name)
    if (hasPaintMaterial(node.material)) paintMeshes.push(node)
  })

  paintMeshes.forEach(addStickerOverlay)
}

function applyMaterials() {
  const targets = materialTargets.value
  bodyModel.value?.traverse((node) => {
    if (!(node instanceof THREE.Mesh)) return
    if (node.userData.isStickerOverlay) {
      applyStickerOverlay(node, targets)
      return
    }
    applyMaterialList(node.material, (material) => applyGarageMaterial(material, targets))
  })

  wheelRig?.traverse((node) => {
    if (node instanceof THREE.Mesh) applyMaterialList(node.material, (material) => applyGarageMaterial(material, targets))
  })
}

function cloneMeshMaterials(material: THREE.Material | THREE.Material[], meshName: string) {
  if (Array.isArray(material)) return material.map((item) => cloneGarageMaterial(item, meshName))
  return cloneGarageMaterial(material, meshName)
}

function cloneGarageMaterial(material: THREE.Material, meshName: string) {
  const clone = material.clone()
  setupGarageMaterial(clone, meshName)
  return clone
}

function setupGarageMaterial(material: THREE.Material, meshName: string) {
  if (!(material instanceof THREE.MeshStandardMaterial)) return
  const role = getMaterialRole(meshName, material.name)
  material.userData.garageRole = role
  material.userData.isBikePaint = isBikePaintMaterial(meshName, material.name)
  material.userData.originalState = {
    color: material.color.clone(),
    map: material.map,
    opacity: material.opacity,
    transparent: material.transparent,
    roughness: material.roughness,
    metalness: material.metalness,
    envMapIntensity: material.envMapIntensity,
  } satisfies OriginalMaterialState

  if (material.map?.colorSpace) material.map.colorSpace = THREE.SRGBColorSpace
  if (material.emissiveMap?.colorSpace) material.emissiveMap.colorSpace = THREE.SRGBColorSpace
  stripEmissive(material)

  if (role === 'paint') {
    material.envMapIntensity = 0.28
  } else if (role === 'window') {
    material.envMapIntensity = material.userData.originalState.envMapIntensity ?? 0.55
  } else if (isGlossyDetail(meshName, material.name)) {
    material.envMapIntensity = 0.45
  } else {
    material.envMapIntensity = 0.38
  }

  material.needsUpdate = true
}

function applyMaterialList(
  material: THREE.Material | THREE.Material[],
  apply: (material: THREE.MeshStandardMaterial) => void
) {
  const materials = Array.isArray(material) ? material : [material]
  materials.forEach((item) => {
    if (item instanceof THREE.MeshStandardMaterial) apply(item)
  })
}

function applyGarageMaterial(
  material: THREE.MeshStandardMaterial,
  targets: {
    paint: THREE.Color | null
    rim: THREE.Color
    window: THREE.Color
    sticker: THREE.Color
  }
) {
  const role = material.userData.garageRole as GarageMaterialRole | undefined
  const original = material.userData.originalState as OriginalMaterialState | undefined
  if (original) {
    material.color.copy(original.color)
    material.map = original.map
    material.opacity = original.opacity
    material.transparent = original.transparent
    if (original.roughness !== undefined) material.roughness = original.roughness
    if (original.metalness !== undefined) material.metalness = original.metalness
    if (original.envMapIntensity !== undefined) material.envMapIntensity = original.envMapIntensity
  }

  if (props.lockedPreview) {
    material.color.set('#8b929c')
    material.map = null
    material.roughness = Math.max(material.roughness ?? 0.5, 0.72)
    material.metalness = Math.min(material.metalness ?? 0.1, 0.12)
    material.envMapIntensity = 0.18
  } else if (role === 'paint' && targets.paint) {
    material.color.copy(targets.paint)
    material.map = null
    material.envMapIntensity = 0.3
  } else if (role === 'paint' && original?.map && !material.userData.isBikePaint) {
    material.map = getCleanPaintTexture(original.map) ?? original.map
    material.envMapIntensity = 0.3
  } else if (role === 'rim') {
    material.color.copy(targets.rim)
    material.envMapIntensity = 0.42
  } else if (role === 'window') {
    material.color.copy(targets.window)
    material.transparent = true
    material.opacity = props.windowOpacity ?? original?.opacity ?? 0.28
    material.roughness = 0.04
    material.metalness = 0
    material.envMapIntensity = 0.6
  } else if (role === 'sticker') {
    material.color.copy(targets.sticker)
    material.envMapIntensity = 0.45
  }

  stripEmissive(material)
  material.needsUpdate = true
}

function hasPaintMaterial(material: THREE.Material | THREE.Material[]) {
  const materials = Array.isArray(material) ? material : [material]
  return materials.some((item) => item instanceof THREE.MeshStandardMaterial && item.userData.garageRole === 'paint')
}

function addStickerOverlay(mesh: THREE.Mesh) {
  const paintMaterial = getPaintMaterial(mesh.material)
  const original = paintMaterial?.userData.originalState as OriginalMaterialState | undefined
  if (!original?.map) return

  const stickerMap = paintMaterial?.userData.isBikePaint
    ? getBikeStickerMaskTexture(original.map)
    : getStickerMaskTexture(original.map, 'factory-kit')
  if (!stickerMap) return

  const stickerMaterial = new THREE.MeshStandardMaterial({
    color: props.stickerColor,
    map: stickerMap,
    transparent: true,
    alphaTest: 0.08,
    depthWrite: false,
    metalness: 0,
    roughness: 0.34,
    polygonOffset: true,
    polygonOffsetFactor: -1,
    polygonOffsetUnits: -1,
  })
  stickerMaterial.name = 'StickerOverlay'
  stickerMaterial.side = paintMaterial.side
  stickerMaterial.userData.stickerSourceMap = original.map
  stickerMaterial.userData.isBikeStickerOverlay = paintMaterial.userData.isBikePaint

  const overlay = new THREE.Mesh(mesh.geometry, stickerMaterial)
  overlay.name = `${mesh.name}_StickerOverlay`
  overlay.renderOrder = 2
  overlay.castShadow = false
  overlay.receiveShadow = false
  overlay.userData.isStickerOverlay = true
  mesh.add(overlay)
}

function getPaintMaterial(material: THREE.Material | THREE.Material[]) {
  const materials = Array.isArray(material) ? material : [material]
  return materials.find(
    (item): item is THREE.MeshStandardMaterial =>
      item instanceof THREE.MeshStandardMaterial && item.userData.garageRole === 'paint'
  )
}

function applyStickerOverlay(
  mesh: THREE.Mesh,
  targets: {
    paint: THREE.Color | null
    rim: THREE.Color
    window: THREE.Color
    sticker: THREE.Color
  }
) {
  applyMaterialList(mesh.material, (material) => {
    if (props.lockedPreview) {
      material.color.set('#6b7280')
      material.opacity = 0.26
      material.needsUpdate = true
      return
    }

    const sourceMap = material.userData.stickerSourceMap as THREE.Texture | undefined
    if (sourceMap) {
      material.map = material.userData.isBikeStickerOverlay
        ? getBikeStickerMaskTexture(sourceMap)
        : getStickerMaskTexture(sourceMap, 'factory-kit')
    }
    material.color.copy(targets.sticker)
    material.needsUpdate = true
  })
}

function getStickerMaskTexture(texture: THREE.Texture, pattern: string) {
  const cachedByPattern = stickerMaskCache.get(texture)
  if (cachedByPattern?.has(pattern)) return cachedByPattern.get(pattern) ?? null

  const image = texture.image as CanvasImageSource | undefined
  if (!image) {
    setStickerMaskCache(texture, pattern, null)
    return null
  }

  const width = Number('width' in image ? image.width : 0)
  const height = Number('height' in image ? image.height : 0)
  if (!width || !height) {
    setStickerMaskCache(texture, pattern, null)
    return null
  }

  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const context = canvas.getContext('2d')
  if (!context) {
    setStickerMaskCache(texture, pattern, null)
    return null
  }

  context.drawImage(image, 0, 0, width, height)
  const imageData = context.getImageData(0, 0, width, height)
  const data = imageData.data

  for (let i = 0; i < data.length; i += 4) {
    const red = data[i]
    const green = data[i + 1]
    const blue = data[i + 2]
    const max = Math.max(red, green, blue)
    const min = Math.min(red, green, blue)
    const isSticker = max > 145 && max - min < 55 && matchesStickerPattern(pattern, (i / 4) % width, Math.floor(i / 4 / width), width, height)

    data[i] = 255
    data[i + 1] = 255
    data[i + 2] = 255
    data[i + 3] = isSticker ? Math.min(255, Math.max(0, (max - 145) * 2.3)) : 0
  }

  context.putImageData(imageData, 0, 0)

  const stickerTexture = new THREE.CanvasTexture(canvas)
  stickerTexture.colorSpace = THREE.SRGBColorSpace
  stickerTexture.flipY = texture.flipY
  stickerTexture.wrapS = texture.wrapS
  stickerTexture.wrapT = texture.wrapT
  stickerTexture.repeat.copy(texture.repeat)
  stickerTexture.offset.copy(texture.offset)
  stickerTexture.center.copy(texture.center)
  stickerTexture.rotation = texture.rotation
  stickerTexture.needsUpdate = true

  setStickerMaskCache(texture, pattern, stickerTexture)
  return stickerTexture
}

function getBikeStickerMaskTexture(texture: THREE.Texture) {
  const pattern = 'bike-decals'
  const cachedByPattern = stickerMaskCache.get(texture)
  if (cachedByPattern?.has(pattern)) return cachedByPattern.get(pattern) ?? null

  const image = texture.image as CanvasImageSource | undefined
  if (!image) {
    setStickerMaskCache(texture, pattern, null)
    return null
  }

  const width = Number('width' in image ? image.width : 0)
  const height = Number('height' in image ? image.height : 0)
  if (!width || !height) {
    setStickerMaskCache(texture, pattern, null)
    return null
  }

  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const context = canvas.getContext('2d')
  if (!context) {
    setStickerMaskCache(texture, pattern, null)
    return null
  }

  context.drawImage(image, 0, 0, width, height)
  const imageData = context.getImageData(0, 0, width, height)
  const data = imageData.data

  for (let i = 0; i < data.length; i += 4) {
    const red = data[i]
    const green = data[i + 1]
    const blue = data[i + 2]
    const max = Math.max(red, green, blue)
    const min = Math.min(red, green, blue)
    const isDarkDecal = max < 78 && max - min < 42

    data[i] = 255
    data[i + 1] = 255
    data[i + 2] = 255
    data[i + 3] = isDarkDecal ? 245 : 0
  }

  context.putImageData(imageData, 0, 0)

  const stickerTexture = new THREE.CanvasTexture(canvas)
  stickerTexture.colorSpace = THREE.SRGBColorSpace
  stickerTexture.flipY = texture.flipY
  stickerTexture.wrapS = texture.wrapS
  stickerTexture.wrapT = texture.wrapT
  stickerTexture.repeat.copy(texture.repeat)
  stickerTexture.offset.copy(texture.offset)
  stickerTexture.center.copy(texture.center)
  stickerTexture.rotation = texture.rotation
  stickerTexture.needsUpdate = true

  setStickerMaskCache(texture, pattern, stickerTexture)
  return stickerTexture
}

function getCleanPaintTexture(texture: THREE.Texture) {
  if (cleanPaintTextureCache.has(texture)) return cleanPaintTextureCache.get(texture) ?? null

  const image = texture.image as CanvasImageSource | undefined
  if (!image) {
    cleanPaintTextureCache.set(texture, null)
    return null
  }

  const width = Number('width' in image ? image.width : 0)
  const height = Number('height' in image ? image.height : 0)
  if (!width || !height) {
    cleanPaintTextureCache.set(texture, null)
    return null
  }

  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const context = canvas.getContext('2d')
  if (!context) {
    cleanPaintTextureCache.set(texture, null)
    return null
  }

  context.drawImage(image, 0, 0, width, height)
  const imageData = context.getImageData(0, 0, width, height)
  const data = imageData.data

  for (let i = 0; i < data.length; i += 4) {
    const red = data[i]
    const green = data[i + 1]
    const blue = data[i + 2]
    const max = Math.max(red, green, blue)
    const min = Math.min(red, green, blue)
    const isStickerPixel = max > 145 && max - min < 55

    if (isStickerPixel) {
      data[i] = 7
      data[i + 1] = 59
      data[i + 2] = 47
    }
  }

  context.putImageData(imageData, 0, 0)

  const cleanTexture = new THREE.CanvasTexture(canvas)
  cleanTexture.colorSpace = THREE.SRGBColorSpace
  cleanTexture.flipY = texture.flipY
  cleanTexture.wrapS = texture.wrapS
  cleanTexture.wrapT = texture.wrapT
  cleanTexture.repeat.copy(texture.repeat)
  cleanTexture.offset.copy(texture.offset)
  cleanTexture.center.copy(texture.center)
  cleanTexture.rotation = texture.rotation
  cleanTexture.needsUpdate = true

  cleanPaintTextureCache.set(texture, cleanTexture)
  return cleanTexture
}

function setStickerMaskCache(texture: THREE.Texture, pattern: string, mask: THREE.Texture | null) {
  const cachedByPattern = stickerMaskCache.get(texture) ?? new Map<string, THREE.Texture | null>()
  cachedByPattern.set(pattern, mask)
  stickerMaskCache.set(texture, cachedByPattern)
}

function matchesStickerPattern(pattern: string, x: number, y: number, width: number, height: number) {
  const u = x / width
  const v = y / height
  const hoodStripes = u > 0.12 && u < 0.24 && v > 0.31 && v < 0.88
  const sideRoundels = u > 0.58 && u < 0.78 && v > 0.22 && v < 0.9
  const longRaceBand = u < 0.05 && v > 0.35 && v < 0.83
  const smallAccent = u > 0.12 && u < 0.18 && ((v > 0.31 && v < 0.4) || (v > 0.79 && v < 0.88))

  if (pattern === 'hood-stripes') return hoodStripes
  if (pattern === 'side-roundels') return sideRoundels
  if (pattern === 'race-band') return longRaceBand || hoodStripes
  if (pattern === 'clean-pop') return sideRoundels || smallAccent
  return true
}

function getMaterialRole(meshName: string, materialName: string): GarageMaterialRole {
  const label = garageMaterialLabel(meshName, materialName)
  if (label.includes('skateboard low') || label.endsWith(' skateboard')) return 'paint'
  if (label.includes('wheel low') || label.endsWith(' wheel')) return 'rim'
  if (label.includes('detail low') || label.endsWith(' detail')) return 'sticker'
  if (label.includes('main body')) return 'paint'
  if (
    label.includes('centredroue') ||
    label.includes('rotor render') ||
    label === 'chrome' ||
    label.includes('caliper')
  ) {
    return 'rim'
  }
  if (label.includes('glass') || label.includes('clearled')) return 'window'
  if (
    label.includes('carbon') ||
    label.includes('963') ||
    label.includes('red') ||
    label.includes('gelb') ||
    label.includes('glow') ||
    label.includes('lights') ||
    label.includes('mirror') ||
    label.includes('fuelcap')
  ) {
    return 'sticker'
  }
  if (label.includes('car paint')) return 'paint'
  if (
    label.includes('break disc') ||
    label.includes('brushed aluminium') ||
    label.includes('rim')
  ) {
    return 'rim'
  }
  if (label.includes('glass') || label.includes('windshield')) return 'window'
  if (
    label.includes('carbon') ||
    label.includes('chrome') ||
    label.includes('light') ||
    label.includes('bulb') ||
    label.includes('mirror')
  ) {
    return 'sticker'
  }
  if (label.includes('new body d albedo')) return 'paint'
  if (label.includes('jantes')) return 'rim'
  if (label.includes('vitres') || label.includes('phare vitre')) return 'window'
  if (
    label.includes('plaque') ||
    label.includes('chrome go') ||
    label.includes('feux') ||
    label.includes('phare') ||
    label.includes('ceramiks')
  ) {
    return 'sticker'
  }
  if (label.includes('frame') && label.includes('material.002')) return 'paint'
  if (label.includes('back wheel') || label.includes('front wheel')) return 'rim'
  if (label.includes('various bike parts') && label.includes('material.007')) return 'sticker'
  if (label.includes('ducati') && label.includes('carpaint')) return 'paint'
  if (label.includes('tires hub')) return 'rim'
  if (
    label.includes('mat details ext') ||
    label.includes('mat details add') ||
    label.includes('mat alpha')
  ) {
    return 'sticker'
  }
  if (label.includes('color 24813')) return 'paint'
  if (label.includes('color 12568524')) return 'rim'
  if (label.includes('color 16768282')) return 'sticker'
  if (
    label.includes('for exportblinn2sg') ||
    label.includes('aistandardsurface4sg') ||
    label.includes('aistandardsurface6sg') ||
    label.includes('blinn2sg') ||
    label.includes('phong1sg')
  ) {
    return 'paint'
  }
  if (
    label.includes('for exportaistandardsurface5sg') ||
    label.includes('aistandardsurface5sg') ||
    label.includes('for exportblinn1sg')
  ) {
    return 'rim'
  }
  if (
    label.includes('for exportblinn3sg') ||
    label.includes('for exportlambert2sg') ||
    label.includes('for exportphong3sg') ||
    label.includes('lambert4sg') ||
    label.includes('phong2sg') ||
    label.includes('aistandardsurface3sg')
  ) {
    return 'sticker'
  }
  if (label.includes('cobra gt500') && label.includes('chassis')) return 'paint'
  if (label.includes('cobra gt500') && (label.includes('livery') || label.includes('badges'))) return 'sticker'
  if (label.includes('cobra gt500') && label.includes('wheel')) return 'rim'
  if (label.includes('cobra gt500') && (label.includes('windows') || label.includes('glass'))) return 'window'
  if (label.includes('carpaint')) return 'paint'
  if (label.includes('jagrim') || label.includes('rim')) return 'rim'
  if (
    label.includes('jagwindos') ||
    label.includes('window') ||
    label.includes('windshield') ||
    label.includes('windscreen')
  ) {
    return 'window'
  }
  return 'other'
}

function isBikePaintMaterial(meshName: string, materialName: string) {
  const label = garageMaterialLabel(meshName, materialName)
  return label.includes('frame') && label.includes('material.002')
}

function isGlossyDetail(meshName: string, materialName: string) {
  const label = garageMaterialLabel(meshName, materialName)
  return label.includes('carbon') || label.includes('badge') || label.includes('light') || label.includes('mirror')
}

function garageMaterialLabel(meshName: string, materialName: string) {
  return `${meshName} ${materialName}`.toLowerCase().replace(/[_-]+/g, ' ')
}

function stripEmissive(material: THREE.MeshStandardMaterial) {
  if (!material?.emissive) return
  material.emissive.setHex(0x000000)
  material.emissiveIntensity = 0
}

function moveCameraForFinish() {
  if (!camera || !controls) return
  if (props.finished) {
    controls.autoRotate = true
    controls.autoRotateSpeed = 1.3
  } else {
    controls.autoRotate = false
  }
}

function animate() {
  frameId = requestAnimationFrame(animate)
  const elapsed = clock?.getElapsedTime() ?? 0
  if (carRig) carRig.rotation.y += props.finished ? 0.007 : 0
  if (wheelRig) wheelRig.position.y += Math.sin(elapsed * 2.2) * 0.0009

  if (props.finished && camera && controls) {
    camera.position.lerp(new THREE.Vector3(2.8, 1.55, 4.4), 0.025)
    controls.target.lerp(new THREE.Vector3(0, 0.32, 0), 0.03)
  }

  controls?.update()
  renderer?.render(scene!, camera!)
}

function resize() {
  if (!host.value || !renderer || !camera) return
  const { width, height } = host.value.getBoundingClientRect()
  renderer.setSize(width, height, false)
  camera.aspect = width / height
  if (Math.abs(width - lastSceneWidth) > 24) {
    lastSceneWidth = width
    fitCameraToScene()
  }
  camera.updateProjectionMatrix()
}

function clearGroup(group: THREE.Group) {
  while (group.children.length) {
    const child = group.children.pop()
    child?.traverse((node) => {
      if (node instanceof THREE.Mesh) {
        node.geometry.dispose()
      }
    })
  }
}

</script>

<!-- @vue-ignore -->
<template>
  <span ref="host" class="vehicle-card-preview" aria-hidden="true"></span>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'

const props = defineProps<{
  model: string
}>()

const host = ref<HTMLElement | null>(null)
let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let modelRoot: THREE.Object3D | null = null
let resizeObserver: ResizeObserver | null = null
let loadToken = 0

const loader = new GLTFLoader()
const modelCache = new Map<string, Promise<THREE.Object3D>>()

onMounted(() => {
  initScene()
  loadModel()
})

watch(
  () => props.model,
  () => {
    loadModel()
  }
)

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  renderer?.dispose()
  renderer?.domElement.remove()
  renderer = null
  scene = null
  camera = null
  modelRoot = null
})

function initScene() {
  if (!host.value || renderer) return

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100)
  camera.position.set(3.25, 1.8, 5.4)
  camera.lookAt(0, -0.05, 0)

  renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'low-power' })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.2
  host.value.appendChild(renderer.domElement)

  scene.add(new THREE.HemisphereLight('#ffffff', '#94a3b8', 2.8))
  const keyLight = new THREE.DirectionalLight('#ffffff', 4.2)
  keyLight.position.set(4, 5, 6)
  scene.add(keyLight)
  const fillLight = new THREE.DirectionalLight('#dbeafe', 2.2)
  fillLight.position.set(-4, 3, 2)
  scene.add(fillLight)
  const rimLight = new THREE.DirectionalLight('#fef3c7', 1.4)
  rimLight.position.set(1, 2, -5)
  scene.add(rimLight)

  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(host.value)
  resize()
}

async function loadModel() {
  if (!scene) return
  const token = ++loadToken

  try {
    const source = await cachedModel(props.model)
    if (token !== loadToken || !scene) return

    if (modelRoot) scene.remove(modelRoot)
    modelRoot = source.clone(true)
    normalizeModel(modelRoot)
    scene.add(modelRoot)
    renderPreview()
  } catch {
    // Empty preview is better than blocking the garage card.
  }
}

async function cachedModel(path: string) {
  if (!modelCache.has(path)) {
    modelCache.set(path, loader.loadAsync(path).then((gltf) => gltf.scene))
  }
  const model = await modelCache.get(path)
  if (!model) throw new Error(`Model not found: ${path}`)
  return model
}

function normalizeModel(model: THREE.Object3D) {
  const box = new THREE.Box3().setFromObject(model)
  const size = box.getSize(new THREE.Vector3())
  const maxAxis = Math.max(size.x, size.y, size.z)
  if (maxAxis > 0) model.scale.multiplyScalar(2.2 / maxAxis)

  box.setFromObject(model)
  const center = box.getCenter(new THREE.Vector3())
  model.position.sub(center)
  model.position.y = -0.08
  model.rotation.y = Math.PI * 0.68
}

function resize() {
  if (!host.value || !renderer || !camera) return
  const rect = host.value.getBoundingClientRect()
  const width = Math.max(1, Math.floor(rect.width))
  const height = Math.max(1, Math.floor(rect.height))
  renderer.setSize(width, height, false)
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderPreview()
}

function renderPreview() {
  if (renderer && scene && camera) renderer.render(scene, camera)
}
</script>

<style scoped>
.vehicle-card-preview {
  position: absolute;
  inset: 2px 4px 42px;
  z-index: 1;
  opacity: 1;
  overflow: hidden;
  border-radius: 12px;
  background: radial-gradient(circle at 50% 62%, rgba(255, 255, 255, 0.96), rgba(224, 242, 254, 0.5) 62%, transparent 76%);
}

.vehicle-card-preview :deep(canvas) {
  width: 100%;
  height: 100%;
  display: block;
}
</style>

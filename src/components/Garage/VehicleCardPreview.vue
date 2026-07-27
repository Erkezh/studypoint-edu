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
let frameId = 0
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
  cancelAnimationFrame(frameId)
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
  camera = new THREE.PerspectiveCamera(36, 1, 0.1, 100)
  camera.position.set(2.9, 1.15, 6.2)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'low-power' })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  host.value.appendChild(renderer.domElement)

  scene.add(new THREE.HemisphereLight('#ffffff', '#cbd5e1', 2.15))
  const keyLight = new THREE.DirectionalLight('#ffffff', 2.85)
  keyLight.position.set(3, 4, 5)
  scene.add(keyLight)
  const fillLight = new THREE.DirectionalLight('#e0f2fe', 1.45)
  fillLight.position.set(-4, 2, -2)
  scene.add(fillLight)

  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(host.value)
  resize()
  animate()
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
  if (maxAxis > 0) model.scale.multiplyScalar(1.85 / maxAxis)

  box.setFromObject(model)
  const center = box.getCenter(new THREE.Vector3())
  model.position.sub(center)
  model.position.y = -0.34
  model.rotation.y = -0.55
}

function resize() {
  if (!host.value || !renderer || !camera) return
  const rect = host.value.getBoundingClientRect()
  const width = Math.max(1, Math.floor(rect.width))
  const height = Math.max(1, Math.floor(rect.height))
  renderer.setSize(width, height, false)
  camera.aspect = width / height
  camera.updateProjectionMatrix()
}

function animate() {
  frameId = requestAnimationFrame(animate)
  if (modelRoot) modelRoot.rotation.y += 0.004
  if (renderer && scene && camera) renderer.render(scene, camera)
}
</script>

<style scoped>
.vehicle-card-preview {
  position: absolute;
  inset: 3px 5px 30px;
  z-index: 0;
  opacity: 1;
}

.vehicle-card-preview :deep(canvas) {
  width: 100%;
  height: 100%;
  display: block;
}
</style>

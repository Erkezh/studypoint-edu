import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'

const loader = new GLTFLoader()
const modelCache = new Map<string, Promise<THREE.Object3D>>()
const thumbnailCache = new Map<string, Promise<string>>()
let renderQueue: Promise<unknown> = Promise.resolve()
let renderer: THREE.WebGLRenderer | null = null

export function getVehicleCardThumbnail(path: string): Promise<string> {
  const cached = thumbnailCache.get(path)
  if (cached) return cached

  const thumbnail = renderQueue.then(() => renderThumbnail(path))
  renderQueue = thumbnail.catch(() => undefined)
  thumbnailCache.set(path, thumbnail)
  return thumbnail
}

async function renderThumbnail(path: string): Promise<string> {
  const source = await loadModel(path)
  const model = source.clone(true)
  normalizeModel(model)

  const scene = new THREE.Scene()
  scene.add(model)
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

  const camera = new THREE.PerspectiveCamera(30, 2.5, 0.1, 100)
  camera.position.set(3.25, 1.8, 5.4)
  camera.lookAt(0, -0.05, 0)

  const sharedRenderer = getRenderer()
  sharedRenderer.render(scene, camera)
  return sharedRenderer.domElement.toDataURL('image/png')
}

function getRenderer(): THREE.WebGLRenderer {
  if (renderer) return renderer
  renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, preserveDrawingBuffer: true, powerPreference: 'low-power' })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))
  renderer.setSize(300, 120, false)
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.2
  return renderer
}

function loadModel(path: string): Promise<THREE.Object3D> {
  let model = modelCache.get(path)
  if (!model) {
    model = loader.loadAsync(path).then((gltf) => gltf.scene)
    modelCache.set(path, model)
  }
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

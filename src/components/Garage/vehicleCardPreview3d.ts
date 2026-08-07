// Three.js types are intentionally omitted by this project's lightweight shim.
// @ts-nocheck
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'

const loader = new GLTFLoader()
const modelCache = new Map<string, Promise<THREE.Object3D>>()

export async function mountVehicleCardModel(canvas: HTMLCanvasElement, path: string): Promise<() => void> {
  let disposed = false
  const source = await loadModel(path)
  if (disposed) return () => undefined

  const model = source.clone(true)
  const baseRotation = previewRotation(path)
  normalizeModel(model, path, baseRotation)

  const scene = new THREE.Scene()
  scene.add(model)
  scene.add(new THREE.HemisphereLight('#ffffff', '#94a3b8', 2.8))

  const keyLight = new THREE.DirectionalLight('#ffffff', 4.2)
  keyLight.position.set(4, 5, 6)
  scene.add(keyLight)

  const fillLight = new THREE.DirectionalLight('#dbeafe', 2.2)
  fillLight.position.set(-4, 3, 2)
  scene.add(fillLight)

  const camera = new THREE.PerspectiveCamera(30, 2.5, 0.1, 100)
  camera.position.set(3.25, 1.8, 5.4)
  camera.lookAt(0, -0.05, 0)

  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))
  renderer.setSize(300, 120, false)
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.2

  let frame = 0
  const startedAt = performance.now()
  const render = () => {
    if (disposed) return
    const elapsed = (performance.now() - startedAt) / 1000
    model.rotation.y = baseRotation + Math.sin(elapsed * 0.7) * 0.12
    renderer.render(scene, camera)
    frame = requestAnimationFrame(render)
  }
  render()

  return () => {
    disposed = true
    cancelAnimationFrame(frame)
    renderer.dispose()
    renderer.forceContextLoss()
  }
}

function loadModel(path: string): Promise<THREE.Object3D> {
  let model = modelCache.get(path)
  if (!model) {
    model = loader.loadAsync(path).then((gltf) => gltf.scene)
    modelCache.set(path, model)
  }
  return model
}

function previewRotation(path: string): number {
  const filename = path.toLowerCase()
  if (
    filename.includes('btwin_triban') ||
    filename.includes('ducati_streetfighter')
  ) return Math.PI * 0.18
  return Math.PI * 0.68
}

function normalizeModel(model: THREE.Object3D, path: string, rotation: number) {
  const box = new THREE.Box3().setFromObject(model)
  const size = box.getSize(new THREE.Vector3())
  const maxAxis = Math.max(size.x, size.y, size.z)
  const filename = path.toLowerCase()
  const targetSize = filename.includes('mustang') || filename.includes('mclaren')
    ? 4.2
    : filename.includes('mini_car')
      ? 3.4
      : 3.7
  if (maxAxis > 0) model.scale.multiplyScalar(targetSize / maxAxis)

  box.setFromObject(model)
  const center = box.getCenter(new THREE.Vector3())
  model.position.sub(center)
  model.position.y = -0.08
  model.rotation.y = rotation
}

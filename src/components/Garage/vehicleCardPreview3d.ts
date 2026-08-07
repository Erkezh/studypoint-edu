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
  const render = () => {
    if (disposed) return
    model.rotation.y += 0.004
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

function normalizeModel(model: THREE.Object3D) {
  const box = new THREE.Box3().setFromObject(model)
  const size = box.getSize(new THREE.Vector3())
  const maxAxis = Math.max(size.x, size.y, size.z)
  if (maxAxis > 0) model.scale.multiplyScalar(4.1 / maxAxis)

  box.setFromObject(model)
  const center = box.getCenter(new THREE.Vector3())
  model.position.sub(center)
  model.position.y = -0.08
  model.rotation.y = Math.PI * 0.68
}

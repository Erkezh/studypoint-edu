import * as THREE from 'three'
import { cloneAvatarScene } from '@/services/avatarAssetService'
import { applyBoZoMaterials } from '@/utils/bozoMaterialFactory'

const thumbnailCache = new Map()
let renderQueue = Promise.resolve()
let renderer = null

function getRenderer() {
  if (!renderer) {
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, preserveDrawingBuffer: true })
    renderer.setPixelRatio(1)
    renderer.setSize(256, 256, false)
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.setClearColor(0xf1f8ee, 0)
  }
  return renderer
}

function disposePreview(root) {
  root.traverse((object) => {
    object.geometry?.dispose?.()
    const materials = Array.isArray(object.material) ? object.material : [object.material]
    materials.filter(Boolean).forEach((material) => material.dispose?.())
  })
}

async function renderThumbnail(item) {
  const root = await cloneAvatarScene(item.modelPath)
  await applyBoZoMaterials(root, item)
  root.updateMatrixWorld(true)

  const bounds = new THREE.Box3().setFromObject(root, true)
  if (bounds.isEmpty()) throw new Error(`${item.id}: preview bounds are empty`)

  const center = bounds.getCenter(new THREE.Vector3())
  const size = bounds.getSize(new THREE.Vector3())
  root.position.sub(center)
  root.updateMatrixWorld(true)

  const scene = new THREE.Scene()
  scene.add(root)
  scene.add(new THREE.HemisphereLight(0xffffff, 0x6d8268, 2.4))
  const keyLight = new THREE.DirectionalLight(0xffffff, 3.2)
  keyLight.position.set(2, 3, 4)
  scene.add(keyLight)

  const camera = new THREE.PerspectiveCamera(26, 1, 0.01, 100)
  const maxSize = Math.max(size.x, size.y, size.z, 0.1)
  const distance = (maxSize / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)))) * 1.25
  camera.position.set(0, size.y * 0.05, distance)
  camera.lookAt(0, 0, 0)
  camera.updateProjectionMatrix()

  const activeRenderer = getRenderer()
  activeRenderer.render(scene, camera)
  const dataUrl = activeRenderer.domElement.toDataURL('image/png')
  scene.remove(root)
  disposePreview(root)
  return dataUrl
}

export function getAvatarItemThumbnail(item) {
  if (!item?.modelPath) return Promise.resolve('')
  if (!thumbnailCache.has(item.modelPath)) {
    const job = renderQueue.then(() => renderThumbnail(item))
    renderQueue = job.catch(() => undefined)
    thumbnailCache.set(item.modelPath, job)
  }
  return thumbnailCache.get(item.modelPath)
}


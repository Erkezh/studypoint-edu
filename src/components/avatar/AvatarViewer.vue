<template>
  <section class="avatar-viewer">
    <div ref="canvasHost" class="avatar-viewer__canvas" />

    <div v-if="loading" class="avatar-viewer__overlay">
      <div class="avatar-viewer__loader">
        <span />
        <strong>Кейіпкер жүктелуде</strong>
        <small>{{ progressLabel }}</small>
      </div>
    </div>

    <div v-if="error" class="avatar-viewer__error">
      <strong>Кейіпкерді жүктеу мүмкін болмады</strong>
      <p>{{ error }}</p>
      <button type="button" @click="rebuildAvatar">Қайталау</button>
    </div>
  </section>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { cloneAvatarScene, getAvatarCacheInfo } from '@/services/avatarAssetService'
import {
  collectBonesByName,
  findRenderableMeshes,
  findSkinnedMeshes,
  pruneDuplicateArmatures,
  rebindSkinnedMeshToBaseSkeleton,
} from '@/utils/avatarSkeleton'
import { disposeObject3D } from '@/utils/disposeThreeObject'
import { applyBoZoMaterials } from '@/utils/bozoMaterialFactory'
import { attachRigidAccessory, isRigidAttachment } from '@/utils/avatarAccessoryAttachment'
import {
  addHatDebugHelpers,
  assertSingleActiveHat,
  attachRigidHat,
  classifyHatAsset,
  makeHatOpaque,
  occludeHairInsideHat,
  validateHatWorldTransform,
} from '@/utils/bozoHatAttachment'

const hatDebugEnabled = import.meta.env.DEV
  && new URLSearchParams(window.location.search).get('bozoHatDebug') === '1'

const props = defineProps({
  selectedItems: {
    type: Object,
    required: true,
  },
  presetShapes: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['inspector-update'])

const canvasHost = ref(null)
const loading = ref(false)
const error = ref('')
const loadedCount = ref(0)
const totalCount = ref(0)
const activeScenes = shallowRef({})

let renderer = null
let scene = null
let camera = null
let controls = null
let resizeObserver = null
let animationFrame = 0
let characterGroup = null
let platform = null
let buildId = 0

function handleCanvasWheel(event) {
  if (event.ctrlKey || event.metaKey) return
  event.stopImmediatePropagation()
  window.scrollBy({ top: event.deltaY, left: 0, behavior: 'auto' })
}

const progressLabel = computed(() => {
  if (!totalCount.value) return 'Модельдер дайындалуда'
  return `${loadedCount.value} / ${totalCount.value} модель`
})

function setupScene() {
  if (!canvasHost.value || renderer) return

  scene = new THREE.Scene()
  scene.background = null

  camera = new THREE.PerspectiveCamera(38, 1, 0.01, 100)
  camera.position.set(0, 1.45, 4.2)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setClearColor(0x000000, 0)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFShadowMap
  canvasHost.value.appendChild(renderer.domElement)
  renderer.domElement.addEventListener('wheel', handleCanvasWheel, { capture: true, passive: true })

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enablePan = false
  controls.enableDamping = true
  controls.minDistance = 1.2
  controls.maxDistance = 7
  controls.target.set(0, 1.05, 0)

  const hemi = new THREE.HemisphereLight('#f8fff4', '#87a884', 2.35)
  scene.add(hemi)

  const key = new THREE.DirectionalLight('#ffffff', 2.6)
  key.position.set(3, 5, 4)
  key.castShadow = true
  key.shadow.mapSize.set(1024, 1024)
  scene.add(key)

  const fill = new THREE.DirectionalLight('#cfead0', 1.1)
  fill.position.set(-3, 2.5, -2)
  scene.add(fill)

  characterGroup = new THREE.Group()
  characterGroup.name = 'BoZoAvatarAssembly'
  scene.add(characterGroup)

  const platformGeometry = new THREE.CylinderGeometry(1.35, 1.35, 0.045, 96)
  const platformMaterial = new THREE.MeshStandardMaterial({
    color: '#dff0dd',
    roughness: 0.88,
    metalness: 0,
  })
  platform = new THREE.Mesh(platformGeometry, platformMaterial)
  platform.name = 'AvatarGroundPlatform'
  platform.receiveShadow = true
  platform.position.y = -0.035
  scene.add(platform)
  resizeObserver = new ResizeObserver(resizeRenderer)
  resizeObserver.observe(canvasHost.value)
  resizeRenderer()
  animate()
}

function animate() {
  animationFrame = requestAnimationFrame(animate)
  controls?.update()
  renderer?.render(scene, camera)
}

function resizeRenderer() {
  if (!canvasHost.value || !renderer || !camera) return
  const { width, height } = canvasHost.value.getBoundingClientRect()
  const safeWidth = Math.max(1, width)
  const safeHeight = Math.max(1, height)
  renderer.setSize(safeWidth, safeHeight, false)
  camera.aspect = safeWidth / safeHeight
  camera.updateProjectionMatrix()
  frameCharacter()
}

function computeSafeBounds(root) {
  const box = new THREE.Box3()
  const meshBox = new THREE.Box3()
  root.updateWorldMatrix(true, true)
  root.traverse((object) => {
    if ((!object.isMesh && !object.isSkinnedMesh) || !object.geometry) return
    if (!object.geometry.boundingBox) object.geometry.computeBoundingBox()
    if (!object.geometry.boundingBox) return
    meshBox.copy(object.geometry.boundingBox).applyMatrix4(object.matrixWorld)
    box.union(meshBox)
  })
  return box
}

function frameCharacter() {
  if (!characterGroup || !camera || !controls) return
  const box = computeSafeBounds(characterGroup)
  if (box.isEmpty()) return

  const size = box.getSize(new THREE.Vector3())
  const center = box.getCenter(new THREE.Vector3())
  const minY = box.min.y
  characterGroup.position.y -= minY
  center.y -= minY

  const maxSize = Math.max(size.x, size.y, size.z, 1)
  const distance = maxSize / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)))
  const framedDistance = distance * 1.25
  camera.position.set(center.x, center.y + size.y * 0.04, center.z + framedDistance)
  camera.near = Math.max(0.01, framedDistance / 100)
  camera.far = framedDistance * 100
  camera.updateProjectionMatrix()
  controls.target.set(center.x, center.y, center.z)
  controls.update()
}

function clearAvatar() {
  if (!characterGroup) return
  for (const child of [...characterGroup.children]) {
    characterGroup.remove(child)
    disposeObject3D(child)
  }
  activeScenes.value = {}
}

function applyPresetShapes(root, preset) {
  if (!preset) return
  const shapes = { ...(preset.bodyShapes || {}), ...(preset.faceShapes || {}) }
  root.traverse((object) => {
    if (!object.morphTargetDictionary || !object.morphTargetInfluences) return
    for (const [name, value] of Object.entries(shapes)) {
      const index = object.morphTargetDictionary[name]
      if (index !== undefined) object.morphTargetInfluences[index] = THREE.MathUtils.clamp(Number(value) / 100, 0, 1)
    }
  })
}

function validateActiveAssembly() {
  if (!import.meta.env.DEV || !characterGroup) return
  const rootsByCategory = new Map()
  const objectNames = new Map()
  characterGroup.traverse((object) => {
    if (object.name?.startsWith('avatar-')) {
      const category = object.name.split('-')[1] || 'unknown'
      rootsByCategory.set(category, (rootsByCategory.get(category) || 0) + 1)
    }
    if (!object.name) return
    objectNames.set(object.name, (objectNames.get(object.name) || 0) + 1)
  })
  const duplicateObjectNames = [...objectNames].filter(([, count]) => count > 1).map(([name, count]) => ({ name, count }))
  for (const category of Object.keys(props.selectedItems)) {
    const actualActiveItemCount = rootsByCategory.get(category) || 0
    console.info('[bozo-assembly-check]', {
      category,
      expectedActiveItemCount: props.selectedItems[category] ? 1 : 0,
      actualActiveItemCount,
      duplicateObjectNames,
    })
  }
}

function attachItemToBone(itemRoot, item, baseRoot) {
  if (!item.metadata.attachPoint) return false
  const target = baseRoot.getObjectByName(item.metadata.attachPoint)
  if (!target) {
    throw new Error(`${item.sourceName}: attach point "${item.metadata.attachPoint}" was not found on the canonical body`)
  }
  // The Unity exports bake static accessory vertices in character/world axes,
  // while the canonical skeleton bones use rotated local axes. Preserve the
  // baked orientation and place the exported origin at the requested bone.
  baseRoot.updateMatrixWorld(true)
  const attachmentRoot = baseRoot.parent || characterGroup
  const skeletonPosition = target.getWorldPosition(new THREE.Vector3())
  baseRoot.worldToLocal(skeletonPosition)
  // The exported canonical armature is Z-up even though static mesh vertices
  // are glTF Y-up. Convert the bone anchor into the mesh coordinate system.
  const attachmentPosition = new THREE.Vector3(
    skeletonPosition.x,
    skeletonPosition.z,
    -skeletonPosition.y,
  )
  baseRoot.localToWorld(attachmentPosition)
  attachmentRoot.worldToLocal(attachmentPosition)
  itemRoot.position.copy(attachmentPosition)
  itemRoot.quaternion.identity()
  itemRoot.scale.set(1, 1, 1)
  attachmentRoot.add(itemRoot)
  itemRoot.userData.avatarAttachment = item.metadata.attachPoint
  return true
}

function convertHeadAttachedHairToStatic(itemRoot, item) {
  if (!['hairFront', 'hairBack'].includes(item.category) || item.metadata.attachPoint !== 'head') return

  for (const skinnedMesh of findSkinnedMeshes(itemRoot)) {
    const mesh = new THREE.Mesh(skinnedMesh.geometry, skinnedMesh.material)
    mesh.name = skinnedMesh.name
    mesh.position.copy(skinnedMesh.position)
    mesh.quaternion.copy(skinnedMesh.quaternion)
    mesh.scale.copy(skinnedMesh.scale)
    mesh.visible = skinnedMesh.visible
    mesh.renderOrder = skinnedMesh.renderOrder
    mesh.castShadow = skinnedMesh.castShadow
    mesh.receiveShadow = skinnedMesh.receiveShadow
    mesh.frustumCulled = skinnedMesh.frustumCulled
    mesh.userData = { ...skinnedMesh.userData, bozoBindPoseAttachment: true }
    skinnedMesh.parent?.add(mesh)
    skinnedMesh.parent?.remove(skinnedMesh)
  }
}

const BODY_COVERAGE_MESHES = {
  CoverAnkles: ['ankles'],
  CoverBack: ['back'],
  CoverChest: ['chest'],
  CoverFeet: ['feet'],
  CoverGroin: ['hips'],
  CoverHands: ['hands'],
  CoverHips: ['hips'],
  CoverLowerArms: ['LowerArm'],
  CoverLowerLegs: ['lowerlegs'],
  CoverShoulders: ['Shoulder'],
  CoverUpperArms: ['upperarm'],
  CoverUpperLegs: ['upperlegs'],
  CoverWaist: ['waist'],
}

function applyBodyCoverage(bodyRoot, items) {
  const hiddenNames = new Set()
  for (const item of items) {
    for (const tag of item.metadata.tags || []) {
      for (const meshName of BODY_COVERAGE_MESHES[tag] || []) hiddenNames.add(meshName)
    }
  }
  bodyRoot.traverse((object) => {
    if ((object.isMesh || object.isSkinnedMesh) && hiddenNames.has(object.name)) object.visible = false
  })
  if (import.meta.env.DEV) console.info('[bozo-body-coverage]', { hiddenMeshes: [...hiddenNames] })
}

function summarizeScene(root, item, skeletonResult) {
  const objectNames = []
  const materialNames = new Set()
  const morphTargetNames = new Set()
  const skinnedMeshNames = []
  const boneNames = new Set()

  root.traverse((object) => {
    if (object.name) objectNames.push(object.name)
    if (object.isBone && object.name) boneNames.add(object.name)
    if (object.isSkinnedMesh) {
      skinnedMeshNames.push(object.name || object.type)
      Object.keys(object.morphTargetDictionary || {}).forEach((name) => morphTargetNames.add(name))
    }
    if (object.material) {
      const materials = Array.isArray(object.material) ? object.material : [object.material]
      materials.forEach((material) => material?.name && materialNames.add(material.name))
    }
  })

  return {
    id: item.id,
    category: item.category,
    name: item.name,
    modelPath: item.modelPath,
    objectNames,
    skinnedMeshNames,
    boneNames: [...boneNames],
    materialNames: [...materialNames],
    texturePaths: item.texturePaths,
    morphTargetNames: [...morphTargetNames],
    animationNames: root.userData.animations?.map((clip) => clip.name).filter(Boolean) || [],
    missingBones: skeletonResult?.missingBones || [],
    rebound: Boolean(skeletonResult?.rebound),
    baseBoneCount: skeletonResult?.baseBoneCount || 0,
    itemBoneCount: skeletonResult?.itemBoneCount || boneNames.size,
    duplicateBoneNames: skeletonResult?.duplicateBoneNames || [],
    importedArmaturesRemoved: skeletonResult?.importedArmaturesRemoved || [],
  }
}


async function rebuildAvatar() {
  if (!characterGroup) return

  const currentBuild = ++buildId
  loading.value = true
  error.value = ''
  loadedCount.value = 0

  const selected = Object.values(props.selectedItems).filter(Boolean)
  totalCount.value = selected.length
  clearAvatar()

  try {
    const body = props.selectedItems.body || selected[0]
    if (!body) {
      loading.value = false
      return
    }

    const summaries = []
    const bodyRoot = await cloneAvatarScene(body.modelPath)
    if (currentBuild !== buildId) return
    bodyRoot.name = `avatar-${body.category}-${body.id}`
    await applyBoZoMaterials(bodyRoot, body)
    characterGroup.add(bodyRoot)
    loadedCount.value += 1
    summaries.push(summarizeScene(bodyRoot, body, { rebound: true, missingBones: [] }))

    for (const item of selected) {
      if (item.id === body.id) continue
      const itemRoot = await cloneAvatarScene(item.modelPath)
      if (currentBuild !== buildId) return

      itemRoot.name = `avatar-${item.category}-${item.id}`
      await applyBoZoMaterials(itemRoot, item)
      convertHeadAttachedHairToStatic(itemRoot, item)
      const skinnedMeshes = findSkinnedMeshes(itemRoot)
      let skeletonResult = { rebound: false, missingBones: [], itemSkinnedMeshCount: skinnedMeshes.length }

      if (skinnedMeshes.length) {
        skeletonResult = rebindSkinnedMeshToBaseSkeleton(itemRoot, bodyRoot)
        if (!skeletonResult.rebound) {
          throw new Error(`${item.sourceName}: canonical skeleton rebind failed; missing bones: ${skeletonResult.missingBones.join(', ') || 'unknown'}`)
        }
        skeletonResult.importedArmaturesRemoved = pruneDuplicateArmatures(itemRoot)
      }

      for (const mesh of findRenderableMeshes(itemRoot)) {
        mesh.castShadow = true
        mesh.receiveShadow = true
      }

      const hatStructure = item.category === 'hat' ? classifyHatAsset(item, itemRoot) : null
      if (item.category === 'hat') makeHatOpaque(itemRoot)
      const attachedToBone = item.category === 'hat' && hatStructure?.classification === 'rigid'
        ? attachRigidHat(itemRoot, bodyRoot, item.metadata.hatFit || item.metadata)
        : isRigidAttachment(item.metadata.attachment)
          ? attachRigidAccessory(itemRoot, bodyRoot, item.metadata.attachment)
          : attachItemToBone(itemRoot, item, bodyRoot)
      if (!attachedToBone) characterGroup.add(itemRoot)
      if (import.meta.env.DEV && item.category === 'hat') {
        const diagnostic = {
          itemId: item.id,
          displayName: item.name,
          sourcePath: item.metadata.sourcePath,
          importedMeshCount: hatStructure.meshes.length,
          importedSkinnedMeshCount: hatStructure.skinnedMeshes.length,
          importedBoneCount: hatStructure.bones.length,
          ...validateHatWorldTransform(itemRoot, bodyRoot),
        }
        console.info('[bozo-hat-fit]', diagnostic)
        console.info('[bozo-hat-fit-json]', JSON.stringify(diagnostic))
        if (hatDebugEnabled) {
          addHatDebugHelpers(itemRoot, bodyRoot)
          console.table({
            hat: item.id,
            classification: diagnostic.classification,
            parent: diagnostic.currentParent,
            attachmentBone: diagnostic.attachmentBone,
            activeHatCount: assertSingleActiveHat(characterGroup),
            importedArmatureCount: diagnostic.importedBoneCount ? 1 : 0,
          })
        }
      }
      loadedCount.value += 1
      summaries.push(summarizeScene(itemRoot, item, skeletonResult))
    }

    const selectedHat = selected.find((item) => item.category === 'hat')
    if (selectedHat) occludeHairInsideHat(characterGroup, selectedHat)
    if (import.meta.env.DEV) assertSingleActiveHat(characterGroup)
    applyBodyCoverage(bodyRoot, selected.filter((item) => item.id !== body.id))
    applyPresetShapes(characterGroup, props.presetShapes)

    await nextTick()
    frameCharacter()
    activeScenes.value = summaries.reduce((acc, summary) => {
      acc[summary.category] = summary
      return acc
    }, {})
    validateActiveAssembly()
    emitInspector(summaries, [])
  } catch (err) {
    if (import.meta.env.DEV) console.error('Avatar assembly failed', err)
    error.value = err instanceof Error ? err.message : 'The avatar could not be assembled.'
    emitInspector([], [error.value])
  } finally {
    if (currentBuild === buildId) loading.value = false
  }
}

function emitInspector(summaries, loadingErrors) {
  emit('inspector-update', {
    manifestUrl: '/assets/characters/bozo/manifests/avatar-assets.json',
    activeItemIds: Object.fromEntries(
      Object.entries(props.selectedItems).map(([category, item]) => [category, item?.id]),
    ),
    loadedModelUrls: summaries.map((summary) => summary.modelPath),
    objectNames: summaries.flatMap((summary) => summary.objectNames),
    skinnedMeshNames: summaries.flatMap((summary) => summary.skinnedMeshNames),
    boneNames: [...new Set(summaries.flatMap((summary) => summary.boneNames))],
    missingBones: [...new Set(summaries.flatMap((summary) => summary.missingBones))],
    materialNames: [...new Set(summaries.flatMap((summary) => summary.materialNames))],
    texturePaths: [...new Set(summaries.flatMap((summary) => summary.texturePaths))],
    morphTargetNames: [...new Set(summaries.flatMap((summary) => summary.morphTargetNames))],
    animationNames: [...new Set(summaries.flatMap((summary) => summary.animationNames))],
    cacheEntries: getAvatarCacheInfo().entries,
    loadingErrors,
    rendererMemory: renderer?.info?.memory || {},
    skeletonSummary: summaries.map((summary) => ({
      category: summary.category,
      name: summary.name,
      rebound: summary.rebound,
      baseBoneCount: summary.baseBoneCount,
      itemBoneCount: summary.itemBoneCount,
      reboundSkinnedMeshes: summary.skinnedMeshNames,
      importedArmaturesRemoved: summary.importedArmaturesRemoved,
      duplicateBoneNames: summary.duplicateBoneNames,
      missingBones: summary.missingBones,
    })),
    baseBones: characterGroup ? [...collectBonesByName(characterGroup).keys()] : [],
  })
}

watch(
  () => [props.selectedItems, props.presetShapes],
  () => rebuildAvatar(),
  { deep: true },
)

onMounted(() => {
  setupScene()
  rebuildAvatar()
})

onBeforeUnmount(() => {
  buildId += 1
  cancelAnimationFrame(animationFrame)
  resizeObserver?.disconnect()
  controls?.dispose()
  clearAvatar()
  if (platform) disposeObject3D(platform)
  renderer?.domElement?.removeEventListener('wheel', handleCanvasWheel, { capture: true })
  renderer?.dispose()
  renderer?.domElement?.remove()
  renderer = null
  scene = null
  camera = null
  controls = null
})
</script>

<style scoped>
.avatar-viewer {
  position: relative;
  min-height: min(45rem, calc(100vh - 9rem));
  overflow: visible;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.avatar-viewer__canvas {
  width: 100%;
  height: 100%;
  min-height: inherit;
}

.avatar-viewer__canvas :deep(canvas) {
  display: block;
  width: 100%;
  height: 100%;
}

.avatar-viewer__overlay,
.avatar-viewer__error {
  position: absolute;
  inset: 1rem;
  display: grid;
  place-items: center;
  pointer-events: none;
}

.avatar-viewer__loader,
.avatar-viewer__error {
  border: 1px solid rgb(255 255 255 / 70%);
  border-radius: 22px;
  background: rgb(255 255 255 / 86%);
  padding: 1rem 1.15rem;
  text-align: center;
  box-shadow: 0 18px 45px rgb(32 72 42 / 12%);
}

.avatar-viewer__loader {
  display: grid;
  gap: 0.35rem;
}

.avatar-viewer__loader span {
  width: 2rem;
  height: 2rem;
  margin: 0 auto 0.2rem;
  border: 4px solid #d9efcf;
  border-top-color: #38b000;
  border-radius: 999px;
  animation: spin 0.8s linear infinite;
}

.avatar-viewer__loader strong,
.avatar-viewer__error strong {
  color: #14251c;
  font-weight: 950;
}

.avatar-viewer__loader small,
.avatar-viewer__error p {
  margin: 0;
  color: #5f7462;
  font-weight: 700;
}

.avatar-viewer__error {
  pointer-events: auto;
  align-self: center;
  justify-self: center;
  max-width: min(28rem, calc(100% - 2rem));
}

.avatar-viewer__error button {
  margin-top: 0.8rem;
  min-height: 2.5rem;
  border: 0;
  border-radius: 999px;
  background: #38b000;
  color: white;
  padding: 0 1.1rem;
  font-weight: 900;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 900px) {
  .avatar-viewer {
    min-height: 31rem;
  }
}
</style>

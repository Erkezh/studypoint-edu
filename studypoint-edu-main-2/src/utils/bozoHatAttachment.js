import * as THREE from 'three'
import { findBoneByName, removeImportedArmature } from '@/utils/avatarAccessoryAttachment'

export function inspectHatStructure(itemRoot) {
  const meshes = []
  const skinnedMeshes = []
  const bones = []
  itemRoot.traverse((object) => {
    if (object.isSkinnedMesh) skinnedMeshes.push(object)
    else if (object.isMesh) meshes.push(object)
    if (object.isBone) bones.push(object)
  })
  return { meshes, skinnedMeshes, bones }
}

export function classifyHatAsset(item, itemRoot) {
  const structure = inspectHatStructure(itemRoot)
  const declaredSkinnedCount = item?.metadata?.skinnedMeshCount || 0
  const classification = structure.skinnedMeshes.length || declaredSkinnedCount ? 'skinned' : 'rigid'
  return { classification, ...structure }
}

export function makeHatOpaque(itemRoot) {
  itemRoot.traverse((object) => {
    if (!object.isMesh || !object.material) return
    const materials = Array.isArray(object.material) ? object.material : [object.material]
    for (const material of materials) {
      material.transparent = false
      material.opacity = 1
      // BoZo hat diffuse alpha is shader-channel data, not transparency.
      material.alphaTest = 0
      material.depthTest = true
      material.depthWrite = true
      material.needsUpdate = true
    }
    object.renderOrder = 2
  })
}

export function occludeHairInsideHat(assemblyRoot, hatItem) {
  const layers = [
    { prefix: 'avatar-hairBack-', crownLimit: 0.065, flatten: false },
    { prefix: 'avatar-hairFront-', crownLimit: 0.12, flatten: true },
  ]

  for (const { prefix, crownLimit, flatten } of layers) {
    const hairRoot = assemblyRoot.children.find((child) => child.name.startsWith(prefix))
    if (!hairRoot) continue
    hairRoot.traverse((object) => {
      if (!object.isMesh || !object.geometry?.index) return
      const geometry = object.geometry.clone()
      const position = geometry.getAttribute('position')
      const index = geometry.index.array
      const kept = []

      if (flatten) {
        for (let vertex = 0; vertex < position.count; vertex += 1) {
          if (position.getY(vertex) > crownLimit) position.setY(vertex, crownLimit)
        }
        position.needsUpdate = true
      }

      for (let offset = 0; offset < index.length; offset += 3) {
        const a = index[offset]
        const b = index[offset + 1]
        const c = index[offset + 2]
        const averageY = (position.getY(a) + position.getY(b) + position.getY(c)) / 3
        if (flatten || averageY <= crownLimit) kept.push(a, b, c)
      }

      geometry.setIndex(kept)
      geometry.computeVertexNormals()
      geometry.computeBoundingSphere()
      object.geometry = geometry
      object.userData.bozoHatOcclusion = { crownLimit }
    })
  }

  const headRoot = assemblyRoot.children.find((child) => child.name.startsWith('avatar-head-'))
  if (!headRoot) return
  headRoot.traverse((object) => {
    if ((!object.isMesh && !object.isSkinnedMesh) || !object.geometry?.index) return
    const geometry = object.geometry.clone()
    const position = geometry.getAttribute('position')
    geometry.computeBoundingBox()
    const bounds = geometry.boundingBox
    const scalpCutoff = bounds.max.y - (bounds.max.y - bounds.min.y) * 0.42
    const index = geometry.index.array
    const kept = []

    for (let offset = 0; offset < index.length; offset += 3) {
      const a = index[offset]
      const b = index[offset + 1]
      const c = index[offset + 2]
      const averageY = (position.getY(a) + position.getY(b) + position.getY(c)) / 3
      if (averageY <= scalpCutoff) kept.push(a, b, c)
    }

    geometry.setIndex(kept)
    geometry.computeBoundingSphere()
    object.geometry = geometry
    object.userData.bozoHatHeadOcclusion = { scalpCutoff, hat: hatItem?.sourceName }
  })
}

function meshSpaceHeadPosition(baseRoot, headBone, targetParent) {
  baseRoot.updateMatrixWorld(true)
  const skeletonPosition = headBone.getWorldPosition(new THREE.Vector3())
  baseRoot.worldToLocal(skeletonPosition)
  const meshPosition = new THREE.Vector3(skeletonPosition.x, skeletonPosition.z, -skeletonPosition.y)
  baseRoot.localToWorld(meshPosition)
  targetParent.worldToLocal(meshPosition)
  return meshPosition
}

export function attachRigidHat(itemRoot, canonicalAvatar, metadata = {}) {
  const attachmentBone = metadata.attachmentBone || metadata.attachPoint || 'head'
  const headBone = findBoneByName(canonicalAvatar, attachmentBone)
  if (!headBone) throw new Error(`Hat attachment bone "${attachmentBone}" was not found`)

  const assemblyRoot = canonicalAvatar.parent
  if (!assemblyRoot) throw new Error('Canonical avatar has no equipment container')

  const exportedTransform = {
    position: itemRoot.position.clone(),
    quaternion: itemRoot.quaternion.clone(),
    scale: itemRoot.scale.clone(),
  }

  removeImportedArmature(itemRoot)
  assemblyRoot.add(itemRoot)
  itemRoot.position.copy(meshSpaceHeadPosition(canonicalAvatar, headBone, assemblyRoot))
  itemRoot.position.add(exportedTransform.position)
  itemRoot.quaternion.copy(exportedTransform.quaternion)
  itemRoot.scale.copy(exportedTransform.scale)
  itemRoot.updateMatrixWorld(true)
  headBone.attach(itemRoot)
  itemRoot.userData.avatarAttachment = attachmentBone
  itemRoot.userData.attachmentSource = 'bozo-hat-metadata'
  itemRoot.userData.hatClassification = 'rigid'
  itemRoot.userData.transformTrace = {
    exportedRoot: {
      position: exportedTransform.position.toArray(),
      quaternion: exportedTransform.quaternion.toArray(),
      scale: exportedTransform.scale.toArray(),
    },
    importedArmatureRemoved: true,
    meshSpaceHeadAnchorApplied: true,
    reparentedPreservingWorldMatrix: true,
  }
  itemRoot.userData.exportedRootTransform = {
    position: exportedTransform.position.toArray(),
    quaternion: exportedTransform.quaternion.toArray(),
    scale: exportedTransform.scale.toArray(),
  }
  return true
}

export function validateHatWorldTransform(hatRoot, avatarRoot) {
  hatRoot.updateMatrixWorld(true)
  const box = new THREE.Box3().setFromObject(hatRoot)
  const headBone = findBoneByName(avatarRoot, 'head')
  const headBox = new THREE.Box3()
  const assemblyRoot = avatarRoot.parent
  const headRoot = assemblyRoot?.children.find((child) => child.name.startsWith('avatar-head-'))
  if (headRoot) headBox.setFromObject(headRoot)
  const meshes = []
  hatRoot.traverse((object) => {
    if (!object.isMesh && !object.isSkinnedMesh) return
    meshes.push({
      name: object.name,
      type: object.type,
      localMatrix: object.matrix.toArray(),
      bindMatrix: object.isSkinnedMesh ? object.bindMatrix.toArray() : null,
    })
  })
  return {
    classification: hatRoot.userData.hatClassification,
    attachmentBone: hatRoot.userData.avatarAttachment,
    currentParent: hatRoot.parent?.name || null,
    localPosition: hatRoot.position.toArray(),
    localQuaternion: hatRoot.quaternion.toArray(),
    localScale: hatRoot.scale.toArray(),
    worldPosition: hatRoot.getWorldPosition(new THREE.Vector3()).toArray(),
    worldQuaternion: hatRoot.getWorldQuaternion(new THREE.Quaternion()).toArray(),
    worldScale: hatRoot.getWorldScale(new THREE.Vector3()).toArray(),
    headWorldPosition: headBone?.getWorldPosition(new THREE.Vector3()).toArray() || null,
    headWorldQuaternion: headBone?.getWorldQuaternion(new THREE.Quaternion()).toArray() || null,
    headWorldScale: headBone?.getWorldScale(new THREE.Vector3()).toArray() || null,
    headBoundingBox: headBox.isEmpty() ? null : { min: headBox.min.toArray(), max: headBox.max.toArray() },
    hatBoundingBox: { min: box.min.toArray(), max: box.max.toArray() },
    meshes,
    transformTrace: hatRoot.userData.transformTrace,
  }
}

export function addHatDebugHelpers(hatRoot, avatarRoot) {
  const assemblyRoot = avatarRoot.parent
  const headBone = findBoneByName(avatarRoot, 'head')
  if (!assemblyRoot || !headBone) return null

  const helpers = new THREE.Group()
  helpers.name = 'BoZoHatDebugHelpers'
  const hatBox = new THREE.Box3().setFromObject(hatRoot)
  const hatBoxHelper = new THREE.Box3Helper(hatBox, 0xff5a36)
  hatBoxHelper.name = 'HatBoundingBoxHelper'
  helpers.add(hatBoxHelper)

  const headRoot = assemblyRoot.children.find((child) => child.name.startsWith('avatar-head-'))
  if (headRoot) {
    const headBoxHelper = new THREE.Box3Helper(new THREE.Box3().setFromObject(headRoot), 0x38b000)
    headBoxHelper.name = 'HeadBoundingBoxHelper'
    helpers.add(headBoxHelper)
  }

  headBone.add(new THREE.AxesHelper(0.18))
  hatRoot.add(new THREE.AxesHelper(0.18))
  const pivot = new THREE.Mesh(
    new THREE.SphereGeometry(0.018, 12, 8),
    new THREE.MeshBasicMaterial({ color: 0xff00ff, depthTest: false }),
  )
  pivot.name = 'HatPivotMarker'
  hatRoot.add(pivot)
  assemblyRoot.add(helpers)
  return helpers
}

export function assertSingleActiveHat(assemblyRoot) {
  const hats = []
  assemblyRoot.traverse((object) => {
    if (object.name?.startsWith('avatar-hat-')) hats.push(object)
  })
  if (hats.length > 1) throw new Error(`Expected at most one active hat, found ${hats.length}`)
  return hats.length
}

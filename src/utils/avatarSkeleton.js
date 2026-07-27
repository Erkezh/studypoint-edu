import * as THREE from 'three'

export function collectBonesByName(root) {
  const bones = new Map()
  root?.traverse((object) => {
    if (object.isBone && object.name && !bones.has(object.name)) {
      bones.set(object.name, object)
    }
  })
  return bones
}

function bonePath(bone) {
  const names = []
  let current = bone
  while (current?.isBone) {
    names.unshift(current.name)
    current = current.parent
  }
  return names.join('/')
}

function exportedBoneName(name) {
  return String(name || '').replace(/_\d+$/, '')
}

export function collectSkeletonDiagnostics(root) {
  const byName = new Map()
  const byPath = new Map()
  root?.traverse((object) => {
    if (!object.isBone || !object.name) return
    const matches = byName.get(object.name) || []
    matches.push(object)
    byName.set(object.name, matches)
    byPath.set(bonePath(object), object)
  })
  for (const mesh of findSkinnedMeshes(root)) {
    for (const bone of mesh.skeleton?.bones || []) {
      if (!bone?.name) continue
      const matches = byName.get(bone.name) || []
      if (!matches.includes(bone)) matches.push(bone)
      byName.set(bone.name, matches)
      const path = bonePath(bone)
      if (path) byPath.set(path, bone)
    }
  }
  return {
    byName,
    byPath,
    duplicateBoneNames: [...byName].filter(([, matches]) => matches.length > 1).map(([name]) => name),
  }
}

export function findSkinnedMeshes(root) {
  const meshes = []
  root?.traverse((object) => {
    if (object.isSkinnedMesh) meshes.push(object)
  })
  return meshes
}

export function findRenderableMeshes(root) {
  const meshes = []
  root?.traverse((object) => {
    if ((object.isMesh || object.isSkinnedMesh) && object.geometry) meshes.push(object)
  })
  return meshes
}

export function validateSkeletonCompatibility(baseRoot, itemRoot) {
  const { byName: baseBones, byPath: basePaths, duplicateBoneNames } = collectSkeletonDiagnostics(baseRoot)
  const missingBones = new Set()
  const skinnedMeshes = findSkinnedMeshes(itemRoot)

  for (const mesh of skinnedMeshes) {
    for (const bone of mesh.skeleton?.bones || []) {
      const verifiedName = exportedBoneName(bone?.name)
      if (bone?.name && !basePaths.has(bonePath(bone)) && !baseBones.has(bone.name) && !baseRoot.getObjectByName(bone.name) && !baseBones.has(verifiedName) && !baseRoot.getObjectByName(verifiedName)) {
        missingBones.add(bonePath(bone) || bone.name)
      }
    }
  }

  return {
    compatible: missingBones.size === 0,
    missingBones: [...missingBones],
    baseBoneCount: basePaths.size,
    itemBoneCount: new Set(skinnedMeshes.flatMap((mesh) => mesh.skeleton?.bones || [])).size,
    duplicateBoneNames,
    itemSkinnedMeshCount: skinnedMeshes.length,
  }
}

export function rebindSkinnedMeshToBaseSkeleton(itemRoot, baseRoot) {
  const { byName: baseBones, byPath: basePaths } = collectSkeletonDiagnostics(baseRoot)
  const result = validateSkeletonCompatibility(baseRoot, itemRoot)

  if (!result.compatible) {
    return { ...result, rebound: false }
  }

  for (const mesh of findSkinnedMeshes(itemRoot)) {
    const sourceBones = mesh.skeleton?.bones || []
    const reboundBones = sourceBones.map(
      (bone) => basePaths.get(bonePath(bone)) || baseBones.get(bone.name)?.[0] || baseRoot.getObjectByName(bone.name) || baseBones.get(exportedBoneName(bone.name))?.[0] || baseRoot.getObjectByName(exportedBoneName(bone.name)),
    )
    const skeleton = new THREE.Skeleton(reboundBones, mesh.skeleton?.boneInverses)
    mesh.bind(skeleton, mesh.bindMatrix)
    mesh.bindMatrixInverse.copy(mesh.bindMatrix).invert()
  }

  return { ...result, rebound: true }
}

export function pruneDuplicateArmatures(root) {
  const removable = []
  root.traverse((object) => {
    if (object.isBone || object.name?.toLowerCase().includes('armature')) {
      removable.push(object)
    }
  })

  for (const object of removable) {
    if (!object.parent) continue
    const hasRenderableChild = object.children.some((child) => child.isMesh || child.isSkinnedMesh)
    if (!hasRenderableChild) object.parent.remove(object)
  }
  return removable.filter((object) => !object.parent).map((object) => object.name || object.type)
}

import * as THREE from 'three'

export function findBoneByName(baseRoot, boneName) {
  if (!baseRoot || !boneName) return null
  const exact = baseRoot.getObjectByName(boneName)
  if (exact?.isBone) return exact
  const normalized = String(boneName).toLowerCase()
  let match = null
  baseRoot.traverse((object) => {
    if (!match && object.isBone && object.name?.toLowerCase() === normalized) match = object
  })
  return match
}

export function applyAttachmentTransform(object, attachment) {
  const position = attachment?.position || [0, 0, 0]
  const quaternion = attachment?.rotationQuaternion || [0, 0, 0, 1]
  const scale = attachment?.scale || [1, 1, 1]
  object.matrixAutoUpdate = true
  object.position.fromArray(position)
  object.quaternion.fromArray(quaternion).normalize()
  object.scale.fromArray(scale)
  object.updateMatrix()
}

export function removeImportedArmature(itemRoot) {
  const removable = []
  itemRoot.traverse((object) => {
    if (object.isBone || object.name?.toLowerCase().includes('armature')) removable.push(object)
  })
  for (const object of removable) {
    if (object.parent) object.parent.remove(object)
  }
  return removable.length
}

export function attachRigidAccessory(itemRoot, baseRoot, attachment) {
  const targetBone = findBoneByName(baseRoot, attachment?.bone)
  if (!targetBone) {
    console.error('[bozo-accessory] Missing attachment bone', {
      item: itemRoot?.name,
      bone: attachment?.bone,
    })
    return false
  }
  removeImportedArmature(itemRoot)
  targetBone.add(itemRoot)
  applyAttachmentTransform(itemRoot, attachment)
  itemRoot.userData.avatarAttachment = attachment.bone
  itemRoot.userData.attachmentSource = 'unity-manifest'
  return true
}

export function isRigidAttachment(attachment) {
  return attachment?.type === 'bone' && Boolean(attachment.bone)
}


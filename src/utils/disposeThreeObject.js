export function disposeObject3D(root) {
  if (!root) return

  root.traverse((object) => {
    if (object.geometry) {
      object.geometry.dispose()
    }

    const materials = Array.isArray(object.material) ? object.material : [object.material]
    for (const material of materials) {
      if (!material) continue

      for (const value of Object.values(material)) {
        if (value && typeof value === 'object' && value.isTexture && !value.userData?.avatarCached) {
          value.dispose()
        }
      }

      material.dispose?.()
    }
  })

  root.clear?.()
}

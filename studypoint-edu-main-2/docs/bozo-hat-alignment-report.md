# BoZo hat alignment report

Date: 2026-07-17

## Finding

The nine exported Hat GLBs do not contain the original Unity prefab or renderer attachment transform. Every scene root and every hat mesh node has identity position, rotation, and scale; there are no `extras`, skins, root bones, bind matrices, or hat-specific bones. Each file also contains an unused copy of `CanonicalArmature`, but the rigid hat mesh is a sibling of that armature and is not influenced by it.

Consequently the web runtime knows only `attachPoint: "head"`. It can identify the target bone, but it cannot reproduce the original per-prefab local position, quaternion, or scale. Geometry-bound alignment is not an acceptable substitute for the missing Unity values and has been removed.

## Classification and exported structure

All hats are class **B: rigid accessory attached to the canonical `head` bone**. None is skinned and none uses additional hat bones.

| Item ID | Model | Unity prefab | Mesh | Exported mesh transform | Root bone / skin | Required bone | Current correction requirement |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Hat_BallCap` | `Hat_BallCap.glb` | `Prefabs/Base/Resources/Hat/Hat_BallCap.prefab` | `Hat_BallCap` | position `[0,0,0]`, quaternion `[0,0,0,1]`, scale `[1,1,1]` | none | `head` | export prefab local transform |
| `Hat_BucketHat` | `Hat_BucketHat.glb` | `Prefabs/Base/Resources/Hat/Hat_BucketHat.prefab` | `Hat_BucketHat` | identity | none | `head` | export prefab local transform |
| `Hat_Fedora` | `Hat_Fedora.glb` | `Prefabs/Base/Resources/Hat/Hat_Fedora.prefab` | `Hat_Fedora` | identity | none | `head` | export prefab local transform |
| `Hat_KittyWoolie` | `Hat_KittyWoolie.glb` | `Prefabs/Base/Resources/Hat/Hat_KittyWoolie.prefab` | `Hat_KittyWoolie` | identity | none | `head` | export prefab local transform |
| `Hat_MilitaryHat` | `Hat_MilitaryHat.glb` | `Prefabs/Base/Resources/Hat/Hat_MilitaryHat.prefab` | `Hat_MilitaryHat` | identity | none | `head` | export prefab local transform |
| `Hat_NewsBoyCap` | `Hat_NewsBoyCap.glb` | `Prefabs/Base/Resources/Hat/Hat_NewsBoyCap.prefab` | `Hat_NewsBoyCap` | identity | none | `head` | export prefab local transform |
| `Hat_Beanie` | `Hat_Beanie.glb` | `Prefabs/Base/Resources/Hat/Hat_Beanie.prefab` | `Hat_Beanie` | identity | none | `head` | export prefab local transform |
| `Hat_SummerCap` | `Hat_SummerCap.glb` | `Prefabs/Base/Resources/Hat/Hat_SummerCap.prefab` | `Hat_SummerHat` | identity | none | `head` | export prefab local transform |
| `Hat_SunHat` | `Hat_SunHat.glb` | `Prefabs/Base/Resources/Hat/Hat_SunHat.prefab` | `Hat_SunHat` | identity | none | `head` | export prefab local transform |

## Exact reason for incorrect placement

The export flattened the hat renderer into head-local-looking vertex coordinates but discarded the prefab transform that positioned those vertices relative to the Unity Head object. The copied armature cannot restore that information because the hat has no skin and no parent relationship to its `head` node. Applying the canonical head transform plus a geometry-derived offset therefore cannot guarantee Unity-equivalent position, rotation, or scale.

## Required Unity exporter metadata

The Unity exporter must read the actual instantiated hat renderer transform relative to the canonical Head transform and write:

```json
"attachment": {
  "type": "bone",
  "bone": "head",
  "position": [0, 0, 0],
  "rotationEuler": [0, 0, 0],
  "rotationQuaternion": [0, 0, 0, 1],
  "scale": [1, 1, 1]
}
```

The numbers above illustrate the schema only; they must be replaced with values read from Unity and must not be guessed. Compatibility fields should likewise be exported only when present in BoZo source data: `hideCategories`, `hideItems`, `compatibleHair`, and `incompatibleHair`.

## Web runtime

`src/utils/avatarAccessoryAttachment.js` now provides an exact-once attachment path. When `attachment` exists, it removes the unused imported armature, parents the rigid accessory directly to the named canonical bone, and applies the exported local position, quaternion, and scale once. The legacy coordinate-conversion path remains only for manifests that lack attachment metadata and is explicitly not Unity-exact.

## Blocker

No Unity project, `.prefab`, `.mat`, custom exporter `.cs` file, or source package exists in this workspace. Therefore the original local transforms and hair compatibility rules cannot be recovered or truthfully added to `avatar-assets.json` here. The five requested visual comparisons cannot meet the “matches Unity” acceptance criterion until the Unity exporter is run against the original package and the regenerated manifest is synced into StudyPoint.

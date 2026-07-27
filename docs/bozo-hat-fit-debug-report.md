# BoZo hat fit diagnostic

## Source availability

The copied web workspace contains the BoZo GLBs and generated JSON manifests, but it does **not** contain `Assets/BoZo_ModularAnimeCharacters`, Unity prefabs, FBX files, `.mat` files, `Packages/manifest.json`, `ProjectSettings`, or the Unity exporter source. Consequently, Unity renderer transforms, bind poses, `OutfitFollowUp` rules, and the exact Unity body/head blend values cannot be recovered or re-exported here. Unknown Unity values below are intentionally not guessed.

## Root cause

The three validation hats are rigid meshes. Each GLB contains one ordinary mesh (`skins: 0`, no `JOINTS_0`) plus a copied 122-bone armature which is not referenced by the mesh. The former web path treated `attachPoint: head` through the generic static-accessory fallback: it removed the hat from its exported hierarchy, reset root rotation and scale, calculated a head position in converted mesh axes, and left the result under the avatar assembly root. It therefore did not have an explicit renderer classification or a true Head-bone parent.

No GLB root or mesh scale is present to be doubled: all three exported mesh nodes use position `[0,0,0]`, quaternion `[0,0,0,1]`, and scale `[1,1,1]`. The defect is missing attachment semantics/Unity metadata, not a demonstrated double-scale in the GLB.

The corrected path classifies the actual loaded object, removes the unused imported armature, preserves the exported root transform, establishes the mesh-space Head anchor once, and uses `Head.attach()` to parent the rigid hat while preserving its world transform. There is no bounding-box normalization or per-hat guessed offset/scale.

## Test hat comparison

### `Hat_Beanie` — Simple Beanie

| Property | Unity | Exported GLB | Corrected Three.js |
|---|---|---|---|
| Prefab | `Assets/BoZo_ModularAnimeCharacters/Prefabs/Base/Resources/Hat/Hat_Beanie.prefab` | recorded in manifest | recorded in `hatFit` |
| Renderer/mesh | unavailable | `Hat_Beanie` / `BSMC_Outfit_Hat_Beanie` | same mesh |
| Renderer type | unavailable | rigid `Mesh` | rigid `Mesh` |
| Root position | unavailable | `[0,0,0]` | preserved, then Head anchor applied once |
| Root rotation | unavailable | `[0,0,0,1]` | preserved |
| Root scale | unavailable | `[1,1,1]` | preserved |
| Mesh position | unavailable | `[0,0,0]` | preserved |
| Mesh rotation | unavailable | `[0,0,0,1]` | preserved |
| Mesh scale | unavailable | `[1,1,1]` | preserved |
| Root bone | unavailable | none | none |
| Attachment bone | unavailable | manifest `head` | canonical `head` |
| Bind matrix | unavailable | none | none |
| Classification | unavailable | rigid; 0 skins | rigid |
| Mesh bounds | unavailable | min `[-0.132555,0.058678,-0.159216]`, max `[0.132461,0.265900,0.142749]` | unchanged |

### `Hat_SummerCap` — Summer Cap

| Property | Unity | Exported GLB | Corrected Three.js |
|---|---|---|---|
| Prefab | `Assets/BoZo_ModularAnimeCharacters/Prefabs/Base/Resources/Hat/Hat_SummerCap.prefab` | recorded in manifest | recorded in `hatFit` |
| Renderer/mesh | unavailable | `Hat_SummerHat` / `Hat_SummerCap` | same mesh |
| Renderer type | unavailable | rigid `Mesh` | rigid `Mesh` |
| Root position / rotation / scale | unavailable | `[0,0,0]` / `[0,0,0,1]` / `[1,1,1]` | preserved |
| Root bone / bind matrix | unavailable | none / none | none / none |
| Attachment bone | unavailable | manifest `head` | canonical `head` |
| Classification | unavailable | rigid; 0 skins | rigid |
| Mesh bounds | unavailable | min `[-0.151611,0.056220,-0.171499]`, max `[0.149607,0.279269,0.216716]` | unchanged |

### `Hat_SunHat` — Sun Hat

| Property | Unity | Exported GLB | Corrected Three.js |
|---|---|---|---|
| Prefab | `Assets/BoZo_ModularAnimeCharacters/Prefabs/Base/Resources/Hat/Hat_SunHat.prefab` | recorded in manifest | recorded in `hatFit` |
| Renderer/mesh | unavailable | `Hat_SunHat` / `BSMC_Outfit_Hat_SunHat` | same mesh |
| Renderer type | unavailable | rigid `Mesh` | rigid `Mesh` |
| Root position / rotation / scale | unavailable | `[0,0,0]` / `[0,0,0,1]` / `[1,1,1]` | preserved |
| Root bone / bind matrix | unavailable | none / none | none / none |
| Attachment bone | unavailable | manifest `head` | canonical `head` |
| Classification | unavailable | rigid; 0 skins | rigid |
| Mesh bounds | unavailable | min `[-0.262002,-0.046109,-0.278563]`, max `[0.278140,0.258274,0.291411]` | unchanged |

## Normalization and assembly audit

- Modular GLBs are not centered, grounded, or scaled independently.
- `frameCharacter()` frames and grounds only the completed `characterGroup`.
- Hat geometry bounds are used only by development diagnostics, never to alter transforms.
- `clearAvatar()` disposes the old assembly before rebuilding.
- Development `assertSingleActiveHat()` enforces zero or one active hat root.
- Development logging reports classification, imported mesh/skinned-mesh/bone counts, final local/world transforms, Head world position, and renderer bounds.

## Hair and head compatibility

The previous screenshot-derived hair crown trimming has been removed because it was not backed by Unity compatibility metadata. The copied manifest has no `OutfitFollowUp`, `HeadHide`, compatible-hair list, hat hair blend shape, or reference body/head blend values. The three new `hatFit` records leave compatibility arrays empty rather than inventing rules.

To reproduce Unity hair interaction exactly, the real Unity project/exporter must add renderer hierarchy/local transforms and the package's hat/hair follow-up rules. The web loader already accepts the `hatFit` object, so corrected copied metadata can replace the provisional GLB-derived classification without changing generic clothing logic.

## Required Unity-side follow-up

When the Unity project is available, export these fields without modifying vendor prefabs: renderer type and hierarchy path; prefab and renderer local position/quaternion/scale; root bone and bone paths; bind matrices for skinned hats; classification; hair hide/compatibility rules; and the reference body/head blend values. Re-export only Simple Beanie, Summer Cap, and Sun Hat, sync the copied assets, and update the manifest version to invalidate the GLTF cache.

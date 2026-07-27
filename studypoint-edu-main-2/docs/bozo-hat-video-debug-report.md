# BoZo hat video debug report

## Scope and reference

This pass is limited to `Hat_SunHat.glb`, `Hat_Beanie.glb`, and `Hat_SummerCap.glb`. The Unity source is read-only and was not modified. The comparison uses `Body_BasicBody`, the default web head/body preset, and the hair selected by the avatar demo. The exact Unity head/body blendshape preset is not present in the current web manifest, so an exact numerical skull-shape comparison is not yet possible.

## Exact root cause

The exported hats are rigid meshes, but every GLB also contains an unused 122-joint `CanonicalArmature`. The mesh is not skinned and has no `skin` index. The current web exporter does not serialize the original renderer hierarchy or attachment matrix. Consequently, the runtime has to convert the canonical `head` bone position from the exported Z-up skeleton basis into the Y-up static-mesh basis.

The visibly incorrect placement began in the web attachment path when an already converted mesh-space head anchor was treated as if it were ordinary Head-local coordinates. Direct `Head.add(hat)` is also invalid for these existing GLBs: the rigid mesh and canonical armature were exported in different bases. The safe temporary web reconstruction is therefore:

1. preserve the GLB renderer/root transform;
2. remove the unused imported armature;
3. calculate the head anchor once in static-mesh space;
4. place the rigid mesh at that bind-space anchor;
5. use `Head.attach()` only to reparent while preserving that world matrix;
6. never center, ground, rescale, or fit the modular hat independently.

`Object3D.attach()` does not apply another placement transform; it calculates the inverse parent matrix so the existing world matrix is preserved. The transform trace is emitted in development builds.

## Source/export/runtime comparison

### Sun Hat

| Property | Unity source | Exported GLB | Current Three.js |
|---|---|---|---|
| Prefab | `Assets/BoZo_ModularAnimeCharacters/Prefabs/Base/Resources/Hat/Hat_SunHat.prefab` | `/assets/characters/bozo/models/Hat_SunHat.glb` | same GLB |
| Renderer type | rigid renderer; `originalRootBone: null` | mesh node, no `skin` | rigid |
| Root parent | Outfit prefab root | `Hat_SunHat_WebExportRoot/Hat_SunHat` | canonical `head` after bind-space placement |
| Root bone | none | none | none |
| Local position | `[0,0,0]` | `[0,0,0]` | derived bind-space local matrix under Head |
| Local rotation | `[0,0,0,1]` | `[0,0,0,1]` | derived by world-preserving reparent |
| Local scale | `[1,1,1]` | `[1,1,1]` | preserved |
| Bind matrix | n/a | n/a | n/a |
| Mesh bounds | source model | min `[-0.262002,-0.046109,-0.278563]`, max `[0.278140,0.258274,0.291411]` | logged at runtime |
| Pivot | prefab origin | mesh origin | bind-space head anchor |

### Simple Beanie

| Property | Unity source | Exported GLB | Current Three.js |
|---|---|---|---|
| Prefab | `Assets/BoZo_ModularAnimeCharacters/Prefabs/Base/Resources/Hat/Hat_Beanie.prefab` | `/assets/characters/bozo/models/Hat_Beanie.glb` | same GLB |
| Renderer type | rigid renderer; `originalRootBone: null` | mesh node, no `skin` | rigid |
| Root parent | Outfit prefab root | `Hat_Beanie_WebExportRoot/Hat_Beanie` | canonical `head` after bind-space placement |
| Local position / rotation / scale | `[0,0,0]` / identity / `[1,1,1]` | identity | renderer transform preserved |
| Bind matrix | n/a | n/a | n/a |
| Mesh bounds | source model | min `[-0.132555,0.058678,-0.159216]`, max `[0.132461,0.265900,0.142749]` | logged at runtime |
| Pivot | prefab origin | mesh origin | bind-space head anchor |

### Summer Cap

| Property | Unity source | Exported GLB | Current Three.js |
|---|---|---|---|
| Prefab | `Assets/BoZo_ModularAnimeCharacters/Prefabs/Base/Resources/Hat/Hat_SummerCap.prefab` | `/assets/characters/bozo/models/Hat_SummerCap.glb` | same GLB |
| Renderer type | rigid renderer; `originalRootBone: null` | mesh node, no `skin` | rigid |
| Root parent | Outfit prefab root | `Hat_SummerCap_WebExportRoot/Hat_SummerCap/Hat_SummerHat` | canonical `head` after bind-space placement |
| Local position / rotation / scale | `[0,0,0]` / identity / `[1,1,1]` | identity | renderer transform preserved |
| Bind matrix | n/a | n/a | n/a |
| Mesh bounds | source model | min `[-0.151611,0.056220,-0.171499]`, max `[0.149607,0.279269,0.216716]` | logged at runtime |
| Pivot | prefab origin | mesh origin | bind-space head anchor |

## Normalization audit

No per-item Box3 centering, target-height scaling, grounding, `normalizeModelScale()`, or camera fitting occurs in the modular loading path. `frameCharacter()` operates on the complete assembled avatar only. Hat geometry is not scaled or translated from its bounds.

## Development diagnostics

Open `/avatar-demo?bozoHatDebug=1` in development. Each loaded hat logs item ID, classification, current parent, attachment bone, local/world position, quaternion and scale, mesh matrix, bind matrix (when applicable), imported bone count, head/hat bounds, active-hat count, and the ordered transform trace. The mode also displays Head/hat axes, both bounding boxes, and a pivot marker. It is excluded from production behavior.

## Hair and head visibility

The source prefabs declare no `HideTypes`, compatible-hair list, alternate hat hair, or extra bones for these three hats. The current GLBs therefore cannot reproduce BoZo `OutfitFollowUp` compatibility exactly. The web fallback trims only the crown-intersecting region of the selected HairFront/HairBack and scalp; it does not globally hide all hair.

## Missing export metadata

The current Unity inventory contains only `attachPoint`, renderer count, and skin count. It does not contain renderer path, root-bone path, renderer transform, bind matrix, bounds, follow-up rules, or validation preset. The web manifest now records the verified identity prefab transform for the three test hats, but the authoritative fix is to export an `attachment` block from a copy/custom exporter. The original BoZo source package was deliberately not modified.

Recommended exporter fields: `classification`, `sourcePrefabPath`, `rendererPath`, `rootBonePath`, `attachmentBonePath`, `localPosition`, `localRotationQuaternion`, `localScale`, `preserveRendererTransform`, `removeImportedArmature`, renderer bounds, required/extra bones, hair/head hiding rules, and the validation head/body preset.

## Remaining limitations

- Exact Unity parity cannot be certified until the same head/body blendshape values and runtime hat/hair follow-up metadata are exported.
- Only Sun Hat, Simple Beanie, and Summer Cap are included in this strict diagnostic pass.
- Other hats remain unsupported by this report and require the same source-metadata validation before being marked complete.

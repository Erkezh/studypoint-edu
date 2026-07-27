# BoZo material diagnostic

Date: 2026-07-17

## Finding

The red/green output is exported `COLOR_0` vertex data being used as the final material color. It is not an ID-mask PNG incorrectly bound to `baseColorTexture`: the GLBs contain no `images` or `textures` arrays and no material texture assignments at all.

For example, `Body_BasicBody.glb` exports `COLOR_0` as unsigned-byte `VEC4` data. Sample vertices include `[255, 0, 0, 255]`; `Feet_SimpleSneakers.glb` includes `[0, 255, 0, 255]`. The glTF accessors also omit `normalized: true`. GLTFLoader enables vertex colors because `COLOR_0` exists, so Three.js multiplies the otherwise-white PBR material by those red/green values.

The source PNG ID maps are not currently used by the GLBs. They are separate files listed by the manifest.

## Representative GLB inspection

| GLB | Mesh | Material | glTF material state | External textures listed by manifest |
| --- | --- | --- | --- | --- |
| `Body_BasicBody.glb` | `ankles_CanonicalWeights` and 13 other body parts | `Body` | No textures; white base-color default; metallic 0; `COLOR_0`; opaque; front side | `Body__IDMap_BasicBody_ID.png` (mask), `Body__NormalMap_StandardNormal.png`, `Body__Texture2D_Body_BasicBody_v2.png` (diffuse) |
| `Head_Young.glb` | `Combined_Skinned_Mesh_CanonicalWeights` | `Head_Head_v2` | No textures; `COLOR_0`; opaque; front side | `Head_Head_v2__IDMap_Head_HeadYoung_v2_ID.png`, `Head_Head_v2__NormalMap_StandardNormal.png`, `Head_Head_v2__Texture2D_Head_HeadYoung_v2.png` |
| `HairFront_ShotaFringe.glb` | `HairFront_ShotaFringe_CanonicalWeights` | `HairFront_ShotaFringe_Mat` | No textures; `COLOR_0`; alpha and double-sided state lost | `HairFront_ShotaFringe_Mat__NormalMap_StandardNormal.png`, `HairFront_ShotaFringe_Mat__Texture2D_HairFront_ShotaFringe_D.png` |
| `HairBack_MessyHair.glb` | `HairBack_MessyHair` | `HairBack_MessyHair_Mat` | No textures; `COLOR_0`; alpha and double-sided state lost | `HairBack_MessyHair_Mat__NormalMap_StandardNormal.png`, `HairBack_MessyHair_Mat__Texture2D_Hairback_MessyHair_D.png` |
| `Top_Tshirt.glb` | `BMAC_Shirt_CanonicalWeights` | `BMAC_Top_Tshirt` | No textures; `COLOR_0`; opaque; front side | `BMAC_Top_Tshirt__NormalMap_Top_Shirt_N.png`, `BMAC_Top_Tshirt__Texture2D_Top_Shirt_D.png` |
| `Bottom_SimpleShorts.glb` | `Bottom_SimpleShorts_CanonicalWeights` | `Bottom_SimpleShorts_Mat` | No textures; `COLOR_0`; opaque; front side | `Bottom_SimpleShorts_Mat__IDMap_Bottom_SimpleShorts_ID.png` (mask), `Bottom_SimpleShorts_Mat__NormalMap_Bottom_SimpleShorts_N.png`, `Bottom_SimpleShorts_Mat__Texture2D_Bottom_SimpleShorts_D.png` (diffuse) |
| `Feet_SimpleSneakers.glb` | `Feet_SimpleSneakers_CanonicalWeights` | `Feet_SimpleSneakers_Mat` | No textures; `COLOR_0`; opaque; front side | `Feet_SimpleSneakers_Mat__IDMap_Feet_SimpleSneakers.png` (mask), `Feet_SimpleSneakers_Mat__NormalMap_Feet_SimpleSneakers_N.png`, `Feet_SimpleSneakers_Mat__Texture2D_Feet_SimpleSneakers_D.png` (diffuse) |

No tested material contains a metallic-roughness, emissive, or alpha texture assignment. All tested meshes use `TEXCOORD_0`; no second UV channel is present. `baseColorFactor`, `alphaMode`, and `doubleSided` are omitted, so glTF defaults apply.

## Unity comparison and lost data

The original Unity package, `.mat` files, Shader Graphs, and shader sources are not present in this workspace. Therefore the original Unity shader name and serialized color values cannot be truthfully recovered here. The available manifest preserves material names, texture paths, color-channel labels, and decal/pattern capability booleans, but not the actual Unity material properties.

Lost during export:

- all texture-to-shader property bindings;
- original shader name and keywords;
- base/channel colors and channel-mask interpretation;
- alpha cutoff and render mode;
- culling/double-sided state;
- smoothness, metallic, emission, normal scale, and other numeric properties;
- decal and pattern parameters;
- whether/how vertex colors participate in the Unity shader.

## Temporary web reconstruction

The avatar demo now follows the safest evidence-backed path:

1. choose the manifest texture named `Texture2D` or ending `_D.png` as `material.map`;
2. choose `NormalMap` or `_N.png` as `material.normalMap`;
3. set diffuse textures to sRGB and normal maps to no color space;
4. set the material multiplier to white;
5. disable `vertexColors` because the exported channel data is proven to be the visible red/green failure;
6. never bind an `IDMap` as the base color;
7. use alpha clipping and double-sided rendering for hair and eyelashes while retaining opaque/front-side rendering elsewhere.

This preserves distinct skin, head, eye, hair, and clothing diffuse artwork. It does not guess shader channel colors or emulate decals/patterns.

## Recommended exporter fix

The durable fix belongs in the Unity export pipeline. Each manifest material entry should include `shaderName`, `baseColorTexture`, `normalTexture`, `maskTexture`, `maskChannelColors` (RGBA values in linear/sRGB space as applicable), `metallic`, `roughness` or `smoothness`, `normalScale`, `alphaMode`, `alphaCutoff`, `doubleSided`, `usesVertexColors`, shader keywords, decal parameters, and pattern parameters. The GLB should bind standard diffuse/normal/alpha properties directly and omit `COLOR_0` unless it has documented runtime semantics.

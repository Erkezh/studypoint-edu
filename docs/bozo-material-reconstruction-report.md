# BoZo material reconstruction report

Date: 2026-07-17

## Exact shader behavior

The original materials use `BoZo/BMAC_Toon` from `Shaders/BMAC_Toon.shader`. Their `_Texture2D` files are not conventional albedo maps: they store RGB channel weights and alpha coverage. Mesh `COLOR_0` is also intentional; its R/G/B values select one of three color groups.

The original core shader computes:

```text
group1 = tex.r * Color1 + tex.g * Color2 + tex.b * Color3
group2 = tex.r * Color4 + tex.g * Color5 + tex.b * Color6
group3 = tex.r * Color7 + tex.g * Color8 + tex.b * Color9
layer1 = group1 * vertexColor.r
layer2 = lerp(layer1, group2, vertexColor.g)
final  = lerp(layer2, group3, vertexColor.b)
alpha  = tex.a; clip(alpha - 0.5)
```

The separate `_IDMap` property is declared by the shader but is not sampled anywhere in `BMAC_Toon.shader`. It is metadata/customization input, not the displayed base color. Patterns and decals are optional passes applied after the core color reconstruction.

## Tested default materials

All tested GLBs omit texture assignments and material properties, so their previous web appearance was the raw `_Texture2D` channel image or raw vertex colors.

| Item | Mesh | Material / Unity path | Mask inputs | Default colors and expected appearance | Wrong appearance and reason |
| --- | --- | --- | --- | --- | --- |
| `Body_BasicBody` | 14 `*_CanonicalWeights` body meshes | `Body`; `Models/Common/Body/Body.mat` | `_Texture2D`: `Body__Texture2D_Body_BasicBody_v2.png`; `_IDMap`: `Body__IDMap_BasicBody_ID.png`; `COLOR_0`; UV0 | `_Color_1 #f5cab0`, `_Color_2 #ea774d`, `_Color_3 #802200`, groups 2/3 include lighter skin, nail and line colors; natural skin | Bright red because `_Texture2D` is predominantly its red channel, not finished skin albedo |
| `Head_Young` / `Head_Young_v2` | `Combined_Skinned_Mesh_CanonicalWeights` | `Head_Head_v2`; `Models/Common/Head/Head_Young/Head_Head_v2.mat` | head `_Texture2D`, `_IDMap`, `COLOR_0`, UV0 | Skin palette matching body, with facial line/detail colors | Red/black channel data displayed directly |
| `Eyes_Eyes01` | exported eye mesh | `EyesMaterial`; `Models/Common/Eyes/EyesMaterial.mat` | `EyesMaterial__Texture2D_Eyes_01.png`, `COLOR_0`, UV0 | `_Color_1 #ff6234`, `_Color_2 #000000`, `_Color_3 #430500`, white secondary group; alpha clip | Raw channel colors and missing alpha reconstruction |
| `HairFront_ShotaFringe` | `HairFront_ShotaFringe_CanonicalWeights` | `HairFront_ShotaFringe_Mat`; `Models/Base/HairFront/HairFront_ShotaFringe/HairFront_ShotaFringe_Mat.mat` | `HairFront_ShotaFringe…_D.png`, `COLOR_0`, UV0 | colors `#745271`, `#84a8c2`, `#946990`; purple/mauve hair with clipped edges | Yellow/green gradient because mask RGB was displayed directly |
| `HairBack_MessyHair` | `HairBack_MessyHair` | `HairBack_MessyHair_Mat`; `Models/Base/HairBack/HairBack_MessyHair/HairBack_MessyHair_Mat.mat` | `HairBack_MessyHair…_D.png`, `COLOR_0`, UV0 | primary `#745271`; matching back hair | Raw mask gradient and missing alpha clip |
| `Top_Tshirt` | `BMAC_Shirt_CanonicalWeights` | `BMAC_Top_Tshirt`; `Models/Base/Top/Top_TShirt/BMAC_Top_Tshirt.mat` | `BMAC_Top_Tshirt…_D.png`, `COLOR_0`, UV0; normal map enabled | primary `#d7d7d7`, secondary `#ea2b2b`, dark third group; gray/red shirt | Bright red/green because region weights were treated as albedo |
| `Bottom_SimpleShorts` | `Bottom_SimpleShorts_CanonicalWeights` | `Bottom_SimpleShorts_Mat`; `Models/Base/Bottom/Bottom_SimpleShorts/Bottom_SimpleShorts_Mat.mat` | `_Texture2D`, `_IDMap`, `COLOR_0`, UV0 | `#584b36`, `#634221`, `#9f8217`, `#a09672`; brown/tan shorts | Raw RGB mask |
| `Feet_SimpleSneakers` | `Feet_SimpleSneakers_CanonicalWeights` | `Feet_SimpleSneakers_Mat`; `Models/Base/Feet/Feet_SimpleSneakers/Feet_SimpleSneakers_Mat.mat` | `_Texture2D`, `_IDMap`, `COLOR_0`, UV0 | `#c20c34`, `#e7e7e7`, `#222222`, plus gray secondary group; red/white/dark sneakers | Raw green/red region weights |

The complete exact values, source paths, texture bindings, alpha settings, culling state, normal flags, pattern parameters, and decal parameters for all 100 referenced materials are in `public/assets/characters/bozo/manifests/materials.json`.

## Web reconstruction

`src/utils/bozoMaterialFactory.js` reproduces the shader’s nine-color/three-vertex-group algorithm with `MeshStandardMaterial.onBeforeCompile`. It keeps `_Texture2D`, normal maps, and ID maps in `NoColorSpace`; the resulting shader colors participate in Three.js lighting. It retains the original alpha cutoff, culling state, and normal-map assignments from exported metadata. A material whose Unity keyword disables `_USECUSTOMTEXTURE` uses `_Texture2D` directly instead.

All external PNGs are loaded with `flipY = false`, matching `GLTFLoader` UV orientation. The exported metadata's former `flipY = true` value described the Unity-side image convention and must not be applied again in Three.js. An audit of every standalone hair GLB showed that unflipped UV sampling hits opaque coverage for essentially every hair vertex, while flipped sampling hits alpha 0 for every vertex; this was the reason many hair choices disappeared completely.

Patterns, decals, the exact Unity toon-light ramp, outline/stencil passes, rim light, multiple-light tuning, fog behavior, and Unity shadow-edge controls are recorded but not yet reproduced.

## Duplicate prevention

Avatar rebuilds remove and dispose every prior category root before adding the new assembly. There is no static fallback. Development builds now log one `[bozo-assembly-check]` record per selected category containing expected/actual active root counts and duplicate object names.

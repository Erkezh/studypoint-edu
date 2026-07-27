# Package overview

Requested package: "BoZo: Modular Anime Characters - Base Pack".

Workspace inspected: `/Users/ayaulyzhumakan/Downloads/studypoint-edu-main-2`.

Important finding: this workspace is not a Unity project. It does not contain `Assets/BoZo_ModularAnimeCharacters/`, `Packages/manifest.json`, `Packages/packages-lock.json`, `ProjectSettings/`, Unity scenes, prefabs, C# scripts, ScriptableObjects, `.mat` files, or `.fbx` files. Because those Unity files are absent, the BoZo-specific architecture cannot be fully inspected from this workspace.

Available character asset in this web app: `public/assets/characters/fantasy/`, extracted from `Modular Character Outfits - Fantasy[Standard].zip`. This appears to be the Quaternius "Modular Character Outfits - Fantasy" standard/free package, not the BoZo Unity package.

# Important folders and files

| Path | Status | Notes |
| --- | --- | --- |
| `Assets/BoZo_ModularAnimeCharacters/` | Missing | Required for the requested BoZo Unity analysis. |
| `Packages/manifest.json` | Missing | No Unity package manifest is present in this workspace. |
| `Packages/packages-lock.json` | Missing | No Unity package lockfile is present. |
| `ProjectSettings/` | Missing | No Unity project settings are present. |
| `public/assets/characters/fantasy/Outfits/` | Present | Complete outfit glTF files for Male/Female Peasant/Ranger. |
| `public/assets/characters/fantasy/ModularParts/` | Present | Separate skinned glTF parts for arms, body, legs, feet, hood, and pauldrons. |
| `public/assets/characters/fantasy/Readme.txt` | Present | States these outfits work with Universal Base Character kit and usually require only the base character head. |
| `public/assets/characters/fantasy/License_Standard.txt` | Present | States CC0 1.0 and identifies models by Quaternius. |

# Main character prefab

Blocked for BoZo. No Unity prefab files are present.

For the available Fantasy glTF asset, there is no main web prefab. The closest equivalents are complete outfit files:

- `public/assets/characters/fantasy/Outfits/Female_Peasant.gltf`
- `public/assets/characters/fantasy/Outfits/Female_Ranger.gltf`
- `public/assets/characters/fantasy/Outfits/Male_Peasant.gltf`
- `public/assets/characters/fantasy/Outfits/Male_Ranger.gltf`

# Skeleton hierarchy

The available glTF files each use one skin named `Armature` with 65 joints. The modular parts also include their own `Armature` skin with 65 joints, so the likely web strategy is to load parts that already carry compatible skeleton data or retarget/rebind them to a shared base skeleton after validating matching joint names.

The exact BoZo skeleton hierarchy cannot be inspected without the Unity package.

# Character construction flow

BoZo construction flow is blocked because the C# implementation and prefabs are absent.

For the available Fantasy glTF asset:

1. Load a base/head character from the Universal Base Character kit, which is not included in this workspace.
2. Load selected outfit part glTF files from `ModularParts/`, or load a complete outfit from `Outfits/`.
3. Use matching armature/joint names to attach skinned meshes under one preview scene.
4. Keep hidden body geometry out of the final character to avoid clipping, as recommended by the asset readme.

# Outfit equip flow

BoZo equip/unequip logic is blocked because no Unity scripts are present.

Recommended web equip flow for the available Fantasy asset:

1. Represent each item as `{ id, category, bodyStyle, modelPath, materialIds, texturePaths }`.
2. Keep one active item per mutually exclusive category: body, arms, legs, feet, hood/head, shoulder accessory.
3. On equip, unload or hide the previous item in that category.
4. Load the new glTF with Three.js `GLTFLoader`.
5. Normalize material color/texture settings to `MeshStandardMaterial`.
6. Attach the part to the avatar preview group.
7. Save only item IDs and color selections, not copied model data.

# Outfit category table

| internal ID | display name | category | asset path | prefab path | model path | material path | texture paths | renderer type | skeleton reference | compatible body style | blendshapes | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `female_peasant_complete` | Female Peasant | complete_outfit | `public/assets/characters/fantasy/Outfits/Female_Peasant.gltf` | N/A | same as asset path | embedded glTF material `MI_Peasant` | `T_Peasant_Normal.png`, `T_Peasant_BaseColor.png`, `T_Peasant_ORM.png` | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | female | none detected | Meshes: arms, body, feet, legs. |
| `female_ranger_complete` | Female Ranger | complete_outfit | `public/assets/characters/fantasy/Outfits/Female_Ranger.gltf` | N/A | same as asset path | embedded glTF materials `MI_Ranger`, `MI_Regular_Female` | Ranger + regular female textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | female | none detected | Includes pauldrons, hood, bracer, belts. |
| `male_peasant_complete` | Male Peasant | complete_outfit | `public/assets/characters/fantasy/Outfits/Male_Peasant.gltf` | N/A | same as asset path | embedded glTF materials `MI_Peasant`, `MI_Regular_Male` | Peasant + regular male textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | male | none detected | Meshes: arms, body, feet, legs. |
| `male_ranger_complete` | Male Ranger | complete_outfit | `public/assets/characters/fantasy/Outfits/Male_Ranger.gltf` | N/A | same as asset path | embedded glTF materials `MI_Ranger`, `MI_Regular_Male` | Ranger + regular male textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | male | none detected | Includes pauldron, hood, bracer, belts. |
| `female_peasant_arms` | Female Peasant Arms | arms | `public/assets/characters/fantasy/ModularParts/Female_Peasant_Arms.gltf` | N/A | same as asset path | `MI_Peasant` | Peasant textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | female | none detected | Separate modular part. |
| `female_peasant_body` | Female Peasant Body | body | `public/assets/characters/fantasy/ModularParts/Female_Peasant_Body.gltf` | N/A | same as asset path | `MI_Peasant` | Peasant textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | female | none detected | Contains `Jog_Fwd_Loop` animation. |
| `female_peasant_feet` | Female Peasant Feet | feet | `public/assets/characters/fantasy/ModularParts/Female_Peasant_Feet.gltf` | N/A | same as asset path | `MI_Peasant` | Peasant textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | female | none detected | Separate modular part. |
| `female_peasant_legs` | Female Peasant Legs | legs | `public/assets/characters/fantasy/ModularParts/Female_Peasant_Legs.gltf` | N/A | same as asset path | `MI_Peasant` | Peasant textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | female | none detected | Separate modular part. |
| `female_ranger_pauldrons` | Female Ranger Pauldrons | shoulder_accessory | `public/assets/characters/fantasy/ModularParts/Female_Ranger_Acc_Pauldrons.gltf` | N/A | same as asset path | `MI_Ranger` | Ranger textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | female | none detected | Accessory part. |
| `female_ranger_arms` | Female Ranger Arms | arms | `public/assets/characters/fantasy/ModularParts/Female_Ranger_Arms.gltf` | N/A | same as asset path | `MI_Ranger`, `MI_Regular_Female` | Ranger + regular female textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | female | none detected | Includes bracer mesh. |
| `female_ranger_body` | Female Ranger Body | body | `public/assets/characters/fantasy/ModularParts/Female_Ranger_Body.gltf` | N/A | same as asset path | `MI_Ranger` | Ranger textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | female | none detected | Includes belt meshes. |
| `female_ranger_feet` | Female Ranger Feet | feet | `public/assets/characters/fantasy/ModularParts/Female_Ranger_Feet.gltf` | N/A | same as asset path | `MI_Ranger` | Ranger textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | female | none detected | Separate modular part. |
| `female_ranger_hood` | Female Ranger Hood | headwear | `public/assets/characters/fantasy/ModularParts/Female_Ranger_Head_Hood.gltf` | N/A | same as asset path | `MI_Ranger` | Ranger textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | female | none detected | Hood part, not a face/head mesh. |
| `female_ranger_legs` | Female Ranger Legs | legs | `public/assets/characters/fantasy/ModularParts/Female_Ranger_Legs.gltf` | N/A | same as asset path | `MI_Ranger` | Ranger textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | female | none detected | Separate modular part. |
| `male_peasant_arms` | Male Peasant Arms | arms | `public/assets/characters/fantasy/ModularParts/Male_Peasant_Arms.gltf` | N/A | same as asset path | `MI_Peasant`, `MI_Regular_Male` | Peasant + regular male textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | male | none detected | Separate modular part. |
| `male_peasant_body` | Male Peasant Body | body | `public/assets/characters/fantasy/ModularParts/Male_Peasant_Body.gltf` | N/A | same as asset path | `MI_Peasant` | Peasant textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | male | none detected | Separate modular part. |
| `male_peasant_feet` | Male Peasant Feet | feet | `public/assets/characters/fantasy/ModularParts/Male_Peasant_Feet.gltf` | N/A | same as asset path | `MI_Peasant` | Peasant textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | male | none detected | Separate modular part. |
| `male_peasant_legs` | Male Peasant Legs | legs | `public/assets/characters/fantasy/ModularParts/Male_Peasant_Legs.gltf` | N/A | same as asset path | `MI_Peasant` | Peasant textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | male | none detected | Separate modular part. |
| `male_ranger_pauldron` | Male Ranger Pauldron | shoulder_accessory | `public/assets/characters/fantasy/ModularParts/Male_Ranger_Acc_Pauldron.gltf` | N/A | same as asset path | `MI_Ranger` | Ranger textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | male | none detected | Accessory part. |
| `male_ranger_arms` | Male Ranger Arms | arms | `public/assets/characters/fantasy/ModularParts/Male_Ranger_Arms.gltf` | N/A | same as asset path | `MI_Ranger`, `MI_Regular_Male` | Ranger + regular male textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | male | none detected | Separate modular part. |
| `male_ranger_body` | Male Ranger Body | body | `public/assets/characters/fantasy/ModularParts/Male_Ranger_Body.gltf` | N/A | same as asset path | `MI_Ranger` | Ranger textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | male | none detected | Includes belt meshes. |
| `male_ranger_boots` | Male Ranger Boots | feet | `public/assets/characters/fantasy/ModularParts/Male_Ranger_Feet_Boots.gltf` | N/A | same as asset path | `MI_Ranger` | Ranger textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | male | none detected | Separate modular part. |
| `male_ranger_hood` | Male Ranger Hood | headwear | `public/assets/characters/fantasy/ModularParts/Male_Ranger_Head_Hood.gltf` | N/A | same as asset path | `MI_Ranger` | Ranger textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | male | none detected | Hood part, not a face/head mesh. |
| `male_ranger_legs` | Male Ranger Legs | legs | `public/assets/characters/fantasy/ModularParts/Male_Ranger_Legs.gltf` | N/A | same as asset path | `MI_Ranger` | Ranger textures | SkinnedMeshRenderer equivalent | `Armature`, 65 joints | male | none detected | Separate modular part. |

# Body and facial customization

BoZo body/facial blendshape customization is blocked because the BoZo models and scripts are absent.

In the available Fantasy glTF files, no morph targets/blendshapes were detected. There are no face, eye, eyebrow, eyelash, front hair, back hair, facial proportion, or body proportion controls in the inspected files.

# Materials and shaders

The available glTF files use standard glTF material data with these material names:

- `MI_Peasant`
- `MI_Ranger`
- `MI_Regular_Female`
- `MI_Regular_Male`

Texture sets:

- Peasant: base color, normal, ORM.
- Ranger: base color, normal, ORM.
- Regular female: dark base color, normal, roughness.
- Regular male: dark base color, normal, roughness.

No Unity Shader Graph or Unity material files were present. For Three.js, map glTF materials to `MeshStandardMaterial`; ORM maps can be split or assigned according to glTF loader interpretation.

# Save JSON format

BoZo save JSON format is blocked because `CharacterSaves`, save/load scripts, and demo scene files are absent.

Recommended web save shape for the available Fantasy asset:

```json
{
  "bodyStyle": "female",
  "equipped": {
    "completeOutfit": null,
    "arms": "female_ranger_arms",
    "body": "female_ranger_body",
    "legs": "female_ranger_legs",
    "feet": "female_ranger_feet",
    "headwear": "female_ranger_hood",
    "shoulderAccessory": "female_ranger_pauldrons"
  },
  "colors": {},
  "version": 1
}
```

# Character merge system

BoZo merge system is blocked because the Unity scripts are absent.

For the available Fantasy asset, no runtime merge system was found. In Three.js, keep parts as separate `SkinnedMesh` objects first. Consider merging only after confirming all parts share identical skeleton/joint ordering and compatible materials.

# Animations and humanoid rig

The available Fantasy glTF files use a 65-joint `Armature`. Only one inspected file includes animation:

- `public/assets/characters/fantasy/ModularParts/Female_Peasant_Body.gltf`: `Jog_Fwd_Loop`

Most outfit and part files contain no animation clips. For a web avatar system, use a separate animation source with the same rig, or retarget animations in Three.js after validating bone names.

# Export risks

- The requested BoZo Unity export analysis cannot be completed without the Unity project files.
- The available Fantasy asset references a separate Universal Base Character kit for heads/base characters. That base kit is not included in this workspace.
- The readme says full body plus clothing can clip; hidden body parts should be removed.
- Large textures may be heavy for mobile. Convert to KTX2/Basis later for production.
- Modular glTF parts include their own armature. Sharing a single skeleton needs validation.

# Web compatibility issues

- This asset is already in glTF, so it is more directly usable in Three.js than a Unity-only package.
- There are no detected blendshapes for facial/body customization.
- There are no included front/back hair categories, eyes, brows, lashes, socks, gloves, hats, neck accessories, or face accessories beyond ranger hood/pauldron-style accessories.
- Texture size is high for mobile and should be optimized.

# Recommended Three.js architecture

Use a data-driven avatar system:

- `AvatarAssetManifest`: item IDs, categories, body style, model path, texture path, unlock metadata.
- `AvatarLoader`: wraps `GLTFLoader`, caches loaded glTF scenes, clones skinned assets safely.
- `AvatarRig`: owns the preview scene, camera, lights, controls, and equipped parts.
- `AvatarInventoryStore`: stores locked/unlocked/equipped IDs and coin shop state.
- `AvatarSave`: serializes only IDs and color values.

Start with whole outfit previews, then move to modular part swapping after validating skeleton sharing.

# Recommended export strategy

For the available Fantasy asset:

1. Keep vendor assets in `public/assets/characters/fantasy/`.
2. Add a local manifest file that describes categories and compatible body styles.
3. Load whole outfit glTF files first for stable preview.
4. Add modular part equip once base head/body assets are available.
5. Optimize textures before production.

For the requested BoZo Unity package:

1. Open the real Unity project containing `Assets/BoZo_ModularAnimeCharacters/`.
2. Do not alter vendor files.
3. Add exporter and documentation only under `Assets/BozoWebExport/`.
4. Inspect C# scripts, prefabs, ScriptableObjects, materials, shaders, and demo scenes before writing an exporter.
5. Export sample characters to glTF only after confirming rig, blendshape, material, and merge behavior.

# Required manual steps

To complete the original BoZo request, provide or open the actual Unity project folder containing:

- `Assets/BoZo_ModularAnimeCharacters/`
- `Packages/manifest.json`
- `ProjectSettings/`

Without those files, BoZo-specific questions about prefabs, save JSON, merge system, Magica Cloth, Shader Graph, and demo warnings cannot be answered reliably.

# Unity warnings and their impact

No Unity warnings can be inspected in this workspace because Unity project logs, scenes, prefabs, and package metadata are absent.

For the available Fantasy glTF asset, no web load errors were found during static inspection. This report did not run Unity.

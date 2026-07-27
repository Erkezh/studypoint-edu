# Avatar Skeleton Debug Report

Generated from local inspection of `public/assets/characters/bozo/models/*.glb` and `public/assets/characters/bozo/manifests/avatar-assets.json`. No renderer, exporter, or asset files were modified.

## Executive diagnosis

The failing Front Hair, Back Hair, and Shoes assets fail because their exported skinning data is invalid for Three.js and glTF skinning. In every failing skinned GLB inspected here, `JOINTS_0` and `WEIGHTS_0` load as two-component skin attributes, and the weighted joint indices include values outside the asset skeleton, commonly `65535`, `65532`, or other large values. Three.js throws `Cannot read properties of undefined (reading 'matrixWorld')` when skinned bounds evaluation reaches one of those invalid joint indices.

Working skinned assets use four-component skin attributes and have all weighted joint indices below the skeleton bone count. Static back-hair models with no SkinnedMesh also load because they do not exercise skinning. `SkeletonUtils.clone()` is not the primary cause: the bad assets can be cloned structurally, but the cloned scene still carries invalid skin attributes. `GLTFLoader` is also not the primary cause; it is exposing the JOINTS/WEIGHTS data present in the GLB.

## Body_BasicBody baseline

- File: `Body_BasicBody.glb`
- Skeleton bones: 90
- Bone names: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ring_01_l, ring_02_l, ring_03_l, thumb_01_l, thumb_02_l, thumb_03_l, lowerarm_twist_01_l, lowerarm_twist_02_l, shoulder_twist_l, upperarm_twist_01_l, upperarm_twist_02_l, clavicle_r, upperarm_r, lowerarm_r, hand_r, index_metacarpal_r, index_01_r, index_02_r, index_03_r, middle_metacarpal_r, middle_01_r, middle_02_r, middle_03_r, pinky_metacarpal_r, pinky_01_r, pinky_02_r, pinky_03_r, ring_metacarpal_r, ring_01_r, ring_02_r, ring_03_r, thumb_01_r, thumb_02_r, thumb_03_r, lowerarm_twist_01_r, lowerarm_twist_02_r, shoulder_twist_r, upperarm_twist_01_r, upperarm_twist_02_r, neck_01, neck_02, head, eyeRoot_l, eyeSocket_l, eye_l, eyeRoot_r, eyeSocket_r, eye_r, Jaw, thigh_l, calf_l, calf_twist_01_l, calf_twist_01_l1, foot_l, ball_l, thigh_twist_01_l, thigh_twist_01_l1, thigh_r, calf_r, calf_twist_01_r, calf_twist_01_r1, foot_r, ball_r, thigh_twist_01_r, thigh_twist_01_r1
- Runtime result: Cannot read properties of undefined (reading 'matrixWorld')
- Note: even the baseline body has invalid weighted skin indices in the `ankles` and `feet` submeshes, while the rest of its body submeshes are in range. That makes exact whole-character bounds fragile until the body export is cleaned too.

| Body mesh | Bones | Inverse bind matrices | Max skin index | Invalid weighted indices |
|---|---:|---:|---:|---:|
| ankles | 90 | 90 | 64904 | 8 |
| back | 90 | 90 | 71 | 0 |
| chest | 90 | 90 | 73 | 0 |
| feet | 90 | 90 | 65405 | 6 |
| hands | 90 | 90 | 70 | 0 |
| hips | 90 | 90 | 85 | 0 |
| LowerArm | 90 | 90 | 56 | 0 |
| lowerlegs | 90 | 90 | 88 | 0 |
| neck | 90 | 90 | 71 | 0 |
| Shoulder | 90 | 90 | 71 | 0 |
| upperarm | 90 | 90 | 71 | 0 |
| upperlegs | 90 | 90 | 85 | 0 |
| waist | 90 | 90 | 82 | 0 |
| wrist | 90 | 90 | 67 | 0 |

## Working assets

These assets either have valid skinned data or are static meshes with no SkinnedMesh skinning data.

### HairFront

- `HairFront_AsymmetricalFringe.glb`: HairFront_AsymmetricalFringe_3, 7 bones, max skin index 5, VEC4/VEC4 skin attrs
- `HairFront_EmoBangs.glb`: HairFront_EmoBangs_3, 7 bones, max skin index 5, VEC4/VEC4 skin attrs
- `HairFront_HimeCut.glb`: HairFront_HimeCut_3, 7 bones, max skin index 6, VEC4/VEC4 skin attrs
- `HairFront_Messy.glb`: HairFront_MessyFringe, 7 bones, max skin index 5, VEC4/VEC4 skin attrs
- `HairFront_ShotaFringe.glb`: HairFront_ShotaFringe_3, 7 bones, max skin index 5, VEC4/VEC4 skin attrs
- `HairFront_Shoujo.glb`: HairFront_Shoujo_3, 7 bones, max skin index 5, VEC4/VEC4 skin attrs

### HairBack

- `HairBack_LongPonyTail.glb`: HairBack_LongPonyTail_3, 4 bones, max skin index 3, VEC4/VEC4 skin attrs
- `HairBack_LongStreight.glb`: HairBack_LongStreight_3, 5 bones, max skin index 3, VEC4/VEC4 skin attrs
- `HairBack_MessyHair.glb`: static mesh / no SkinnedMesh
- `HairBack_PineappleCut.glb`: static mesh / no SkinnedMesh
- `HairBack_RoundBob.glb`: static mesh / no SkinnedMesh
- `HairBack_ShotaCut.glb`: static mesh / no SkinnedMesh
- `HairBack_SweaptDreads.glb`: static mesh / no SkinnedMesh
- `HairBack_TiedBun.glb`: static mesh / no SkinnedMesh
- `HairBack_TwinBuns.glb`: static mesh / no SkinnedMesh
- `HairBack_TwinLongTails.glb`: HairBack_TwinLongTails_3, 7 bones, max skin index 6, VEC4/VEC4 skin attrs
- `HairBack_WildLocks.glb`: static mesh / no SkinnedMesh

### Feet

- `Feet_HighLaceShoe.glb`: Feet_HighLaceShoe_3, 14 bones, max skin index 13, VEC4/VEC4 skin attrs
- `Feet_OfficeLoafer.glb`: Feet_OfficeLoafer_4, 8 bones, max skin index 7, VEC4/VEC4 skin attrs
- `Feet_SimpleSneakers.glb`: Feet_SimpleSneakers_4, 10 bones, max skin index 9, VEC4/VEC4 skin attrs
- `Feet_SockedBalletFlats.glb`: Feet_SockedBalletFlats_3, 14 bones, max skin index 13, VEC4/VEC4 skin attrs

## Manifest outliers

`BMAC_CharacterBase.glb` and `OutfitIconCapture.glb` appear in the manifest with `HairFront`, but they are not modular front-hair choices. I excluded them from the attachment diagnosis tables because the failure set requested here is the modular Front Hair, Back Hair, and Shoes assets.

## Category status tables

### Front Hair

| Status | File | Mesh/material | Bones | Skin attrs | Max skin index | Invalid weighted indices | Runtime result |
|---|---|---|---:|---|---:|---:|---|
| working | HairFront_AsymmetricalFringe.glb | HairFront_AsymmetricalFringe_3 / HairFront_AsymmetricalFringe_Mat | 7 | VEC4/VEC4 | 5 | 0 | ok |
| failing | HairFront_CurtainBangs.glb | HairFront_CurtainBangs_3 / HairFront_CurtainBangs_Mat | 5 | VEC2/VEC2 | 65328 | 8 | Cannot read properties of undefined (reading 'matrixWorld') |
| working | HairFront_EmoBangs.glb | HairFront_EmoBangs_3 / HairFront_EmoBangs_Mat | 7 | VEC4/VEC4 | 5 | 0 | ok |
| working | HairFront_HimeCut.glb | HairFront_HimeCut_3 / HairFront_HimeCut_Mat | 7 | VEC4/VEC4 | 6 | 0 | ok |
| failing | HairFront_LynxFringe.glb | HairFront_LynxFringe_3 / HairFront_LynxFringe_Mat | 7 | VEC2/VEC2 | 65532 | 14 | Cannot read properties of undefined (reading 'matrixWorld') |
| working | HairFront_Messy.glb | HairFront_MessyFringe / HairFront_Messy_Mat | 7 | VEC4/VEC4 | 5 | 0 | ok |
| failing | HairFront_MinorFringe.glb | HairFront_MinorFringe_3 / HairFront_MinorFringe_Mat | 3 | VEC2/VEC2 | 65531 | 10 | Cannot read properties of undefined (reading 'matrixWorld') |
| working | HairFront_ShotaFringe.glb | HairFront_ShotaFringe_3 / HairFront_ShotaFringe_Mat | 7 | VEC4/VEC4 | 5 | 0 | ok |
| working | HairFront_Shoujo.glb | HairFront_Shoujo_3 / HairFront_Shoujo_Mat | 7 | VEC4/VEC4 | 5 | 0 | ok |
| failing | HairFront_SideSwept.glb | HairFront_SideSwept_3 / HairFront_SideSwept_Mat | 3 | VEC2/VEC2 | 65535 | 5 | Cannot read properties of undefined (reading 'matrixWorld') |
| failing | HairFront_SweaptBack.glb | HairFront_SweaptBack_3 / HairFront_SweaptBack_Mat | 5 | VEC2/VEC2 | 9 | 1 | Cannot read properties of undefined (reading 'matrixWorld') |

### Back Hair

| Status | File | Mesh/material | Bones | Skin attrs | Max skin index | Invalid weighted indices | Runtime result |
|---|---|---|---:|---|---:|---:|---|
| failing | HairBack_CasualFlow.glb | HairBack_CasualFlow_3 / HairBack_CasualFlow_Mat | 3 | VEC2/VEC2 | 65535 | 29 | Cannot read properties of undefined (reading 'matrixWorld') |
| failing | HairBack_Flare.glb | HairBack_Flare_3 / HairBack_Flare_Mat | 3 | VEC2/VEC2 | 65535 | 85 | Cannot read properties of undefined (reading 'matrixWorld') |
| failing | HairBack_HeroTie.glb | HairBack_HeroTie_3 / HairBack_HeroTie_Mat | 5 | VEC2/VEC2 | 65514 | 23 | Cannot read properties of undefined (reading 'matrixWorld') |
| working | HairBack_LongPonyTail.glb | HairBack_LongPonyTail_3 / HairBack_PonyTail_Mat | 4 | VEC4/VEC4 | 3 | 0 | ok |
| working | HairBack_LongStreight.glb | HairBack_LongStreight_3 / HairBack_LongStreight_Mat | 5 | VEC4/VEC4 | 3 | 0 | ok |
| working | HairBack_MessyHair.glb | static mesh or load error | 0 | none |  | 0 | ok |
| working | HairBack_PineappleCut.glb | static mesh or load error | 0 | none |  | 0 | ok |
| working | HairBack_RoundBob.glb | static mesh or load error | 0 | none |  | 0 | ok |
| failing | HairBack_ShinryuCut.glb | Hairback_ShinryuCut_1 / Hairback_ShinryuCut_Mat | 3 | VEC2/VEC2 | 65532 | 46 | Cannot read properties of undefined (reading 'matrixWorld') |
| failing | HairBack_ShortPonyTail.glb | HairBack_ShortPonyTail_3 / HairBack_PonyTail_Mat | 3 | VEC2/VEC2 | 65522 | 15 | Cannot read properties of undefined (reading 'matrixWorld') |
| working | HairBack_ShotaCut.glb | static mesh or load error | 0 | none |  | 0 | ok |
| working | HairBack_SweaptDreads.glb | static mesh or load error | 0 | none |  | 0 | ok |
| working | HairBack_TiedBun.glb | static mesh or load error | 0 | none |  | 0 | ok |
| working | HairBack_TwinBuns.glb | static mesh or load error | 0 | none |  | 0 | ok |
| working | HairBack_TwinLongTails.glb | HairBack_TwinLongTails_3 / HairBack_TwinTails_Mat | 7 | VEC4/VEC4 | 6 | 0 | ok |
| failing | HairBack_TwinShortTails.glb | HairBack_ShortPigTails / HairBack_TwinTails_Mat | 5 | VEC2/VEC2 | 65535 | 20 | Cannot read properties of undefined (reading 'matrixWorld') |
| working | HairBack_WildLocks.glb | static mesh or load error | 0 | none |  | 0 | ok |
| failing | HairBack_WildTail.glb | HairBack_WildTail_3 / HairBack_WildTail_Mat | 3 | VEC2/VEC2 | 65535 | 38 | Cannot read properties of undefined (reading 'matrixWorld') |
| failing | HairBack_YokaiMane.glb | HairBack_YokaiCut / HairBack_YokaiMane_Mat | 3 | VEC2/VEC2 | 65535 | 18 | Cannot read properties of undefined (reading 'matrixWorld') |

### Shoes

| Status | File | Mesh/material | Bones | Skin attrs | Max skin index | Invalid weighted indices | Runtime result |
|---|---|---|---:|---|---:|---:|---|
| failing | Feet_AthleticMidTop.glb | Feet_AthleticMidTop1 / Feet_AthleticMidTop_Mat | 90 | VEC2/VEC2 | 65261 | 39 | Cannot read properties of undefined (reading 'matrixWorld') |
| failing | Feet_BalletFlats.glb | Feet_BalletFlats_4 / Feet_BalletFlats_Mat | 8 | VEC2/VEC2 | 65532 | 86 | Cannot read properties of undefined (reading 'matrixWorld') |
| failing | Feet_ClassyLoafers.glb | Feet_ClassyLoafers_4 / Feet_ClassyLoafers_Mat | 10 | VEC2/VEC2 | 65535 | 17 | Cannot read properties of undefined (reading 'matrixWorld') |
| failing | Feet_FlowerFlipFlops.glb | Feet_SimpleFlipFlops_1 / Feet_FlowerFlipFlops_Mat | 8 | VEC2/VEC2 | 65535 | 26 | Cannot read properties of undefined (reading 'matrixWorld') |
| working | Feet_HighLaceShoe.glb | Feet_HighLaceShoe_3 / Feet_HighLaceShoe_Mat | 14 | VEC4/VEC4 | 13 | 0 | ok |
| failing | Feet_OfficeHeels.glb | Feet_OfficeHeels_4 / Feet_OfficeHeels_Mat | 8 | VEC2/VEC2 | 65535 | 22 | Cannot read properties of undefined (reading 'matrixWorld') |
| working | Feet_OfficeLoafer.glb | Feet_OfficeLoafer_4 / Feet_OfficeLoafer_Mat | 8 | VEC4/VEC4 | 7 | 0 | ok |
| failing | Feet_SimpleFlipFlops.glb | Feet_SimpleFlipFlops1_1 / Feet_SimpleFlipFlops_Mat | 8 | VEC2/VEC2 | 65535 | 27 | Cannot read properties of undefined (reading 'matrixWorld') |
| working | Feet_SimpleSneakers.glb | Feet_SimpleSneakers_4 / Feet_SimpleSneakers_Mat | 10 | VEC4/VEC4 | 9 | 0 | ok |
| working | Feet_SockedBalletFlats.glb | Feet_SockedBalletFlats_3 / Feet_SockedBalletFlats_Mat | 14 | VEC4/VEC4 | 13 | 0 | ok |
| failing | Feet_StrappedSandals.glb | Feet_StrappedSandals_4 / Feet_StrappedSandals_Mat | 10 | VEC2/VEC2 | 65534 | 106 | Cannot read properties of undefined (reading 'matrixWorld') |
| failing | Feet_WorkBoots.glb | Feet_WorkBoots_4 / Feet_WorkBoots_Mat | 10 | VEC2/VEC2 | 65535 | 43 | Cannot read properties of undefined (reading 'matrixWorld') |

## Failing assets

## HairFront failures

### HairFront_CurtainBangs.glb

- Status: failing
- Armature name: Hair_Right
- Skeleton root: HairFront_CurtainBangs_2
- SkinnedMeshRenderer structure: HairFront_CurtainBangs_3 (SkinnedMesh), vertices 460, materials HairFront_CurtainBangs_Mat
- Mesh names: HairFront_CurtainBangs_3
- Material names: HairFront_CurtainBangs_Mat
- Bone names: HaiFront, Hair_Left, Hair_Left1, Hair_Right, Hair_Right_1
- Missing bones versus Body_BasicBody: HaiFront, Hair_Left, Hair_Left1, Hair_Right, Hair_Right_1
- Extra Body_BasicBody bones not used by this item: 90 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 5 inverse bind matrices for 5 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65328; 8 weighted indices point outside the 5-bone skeleton; bad weight values 0; samples: v4:slot0->7730@0.03723; v25:slot0->6@0.000031; v59:slot0->15742@0.343927; v64:slot0->44500@0.71476.
- Node hierarchy: Group:HairFront_CurtainBangs > Object3D:HairFront_CurtainBangs_1 > Object3D:HairFront_CurtainBangs_2 > Bone:HaiFront > Bone:Hair_Left > Bone:Hair_Left1 > Bone:Hair_Right > Bone:Hair_Right_1 > SkinnedMesh:HairFront_CurtainBangs_3
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### HairFront_LynxFringe.glb

- Status: failing
- Armature name: Hair_Right
- Skeleton root: HairFront_LynxFringe_2
- SkinnedMeshRenderer structure: HairFront_LynxFringe_3 (SkinnedMesh), vertices 789, materials HairFront_LynxFringe_Mat
- Mesh names: HairFront_LynxFringe_3
- Material names: HairFront_LynxFringe_Mat
- Bone names: HairFront, Hair_Left, Hair_Left1, Hair_Front, Hair_Front1, Hair_Right, Hair_Right1
- Missing bones versus Body_BasicBody: HairFront, Hair_Left, Hair_Left1, Hair_Front, Hair_Front1, Hair_Right, Hair_Right1
- Extra Body_BasicBody bones not used by this item: 90 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 7 inverse bind matrices for 7 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65532; 14 weighted indices point outside the 7-bone skeleton; bad weight values 0; samples: v12:slot0->65507@0.964784; v19:slot0->65113@0.545224; v39:slot0->65508@0.98066; v119:slot0->4841@0.008097.
- Node hierarchy: Group:HairFront_LynxFringe > Object3D:HairFront_LynxFringe_1 > Object3D:HairFront_LynxFringe_2 > Bone:HairFront > Bone:Hair_Front > Bone:Hair_Front1 > Bone:Hair_Left > Bone:Hair_Left1 > Bone:Hair_Right > Bone:Hair_Right1 > SkinnedMesh:HairFront_LynxFringe_3
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### HairFront_MinorFringe.glb

- Status: failing
- Armature name: (none named armature)
- Skeleton root: HairFront_MinorFringe_2
- SkinnedMeshRenderer structure: HairFront_MinorFringe_3 (SkinnedMesh), vertices 384, materials HairFront_MinorFringe_Mat
- Mesh names: HairFront_MinorFringe_3
- Material names: HairFront_MinorFringe_Mat
- Bone names: HairFront, Hair_Front, Hair_Front1
- Missing bones versus Body_BasicBody: HairFront, Hair_Front, Hair_Front1
- Extra Body_BasicBody bones not used by this item: 90 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 3 inverse bind matrices for 3 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65531; 10 weighted indices point outside the 3-bone skeleton; bad weight values 0; samples: v36:slot0->65531@0.839081; v55:slot0->90@0.001325; v63:slot0->26919@0.269519; v190:slot0->56@0.00048.
- Node hierarchy: Group:HairFront_MinorFringe > Object3D:HairFront_MinorFringe_1 > Object3D:HairFront_MinorFringe_2 > Bone:HairFront > Bone:Hair_Front > Bone:Hair_Front1 > SkinnedMesh:HairFront_MinorFringe_3
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### HairFront_SideSwept.glb

- Status: failing
- Armature name: (none named armature)
- Skeleton root: HairFront_SideSwept_2
- SkinnedMeshRenderer structure: HairFront_SideSwept_3 (SkinnedMesh), vertices 368, materials HairFront_SideSwept_Mat
- Mesh names: HairFront_SideSwept_3
- Material names: HairFront_SideSwept_Mat
- Bone names: HairFront, Hair_Left, Hair_Left1
- Missing bones versus Body_BasicBody: HairFront, Hair_Left, Hair_Left1
- Extra Body_BasicBody bones not used by this item: 90 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 3 inverse bind matrices for 3 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65535; 5 weighted indices point outside the 3-bone skeleton; bad weight values 0; samples: v50:slot0->506@0.005661; v52:slot0->559@0.006143; v208:slot0->2098@0.01717; v270:slot0->3@0.000027.
- Node hierarchy: Group:HairFront_SideSwept > Object3D:HairFront_SideSwept_1 > Object3D:HairFront_SideSwept_2 > Bone:HairFront > Bone:Hair_Left > Bone:Hair_Left1 > SkinnedMesh:HairFront_SideSwept_3
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### HairFront_SweaptBack.glb

- Status: failing
- Armature name: Hair_Right
- Skeleton root: HairFront_SweaptBack_2
- SkinnedMeshRenderer structure: HairFront_SweaptBack_3 (SkinnedMesh), vertices 528, materials HairFront_SweaptBack_Mat
- Mesh names: HairFront_SweaptBack_3
- Material names: HairFront_SweaptBack_Mat
- Bone names: HairFront, Hair_Left, Hair_Left1, Hair_Right, Hair_Right1
- Missing bones versus Body_BasicBody: HairFront, Hair_Left, Hair_Left1, Hair_Right, Hair_Right1
- Extra Body_BasicBody bones not used by this item: 90 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 5 inverse bind matrices for 5 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 9; 1 weighted indices point outside the 5-bone skeleton; bad weight values 0; samples: v466:slot0->9@0.000046.
- Node hierarchy: Group:HairFront_SweaptBack > Object3D:HairFront_SweaptBack_1 > Object3D:HairFront_SweaptBack_2 > Bone:HairFront > Bone:Hair_Left > Bone:Hair_Left1 > Bone:Hair_Right > Bone:Hair_Right1 > SkinnedMesh:HairFront_SweaptBack_3
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

## HairBack failures

### HairBack_CasualFlow.glb

- Status: failing
- Armature name: (none named armature)
- Skeleton root: CasualFlow1
- SkinnedMeshRenderer structure: HairBack_CasualFlow_3 (SkinnedMesh), vertices 941, materials HairBack_CasualFlow_Mat
- Mesh names: HairBack_CasualFlow_3
- Material names: HairBack_CasualFlow_Mat
- Bone names: HairBack, Hair_Back, Hair_Back1
- Missing bones versus Body_BasicBody: HairBack, Hair_Back, Hair_Back1
- Extra Body_BasicBody bones not used by this item: 90 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 3 inverse bind matrices for 3 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65535; 29 weighted indices point outside the 3-bone skeleton; bad weight values 10; samples: v142:slot0->37484@0.54285; v146:slot0->68@0.001027; v159:slot0->45474@0.370688; v183:slot0->17540@0.16878.
- Node hierarchy: Group:HairBack_CasualFlow > Object3D:HairBack_CasualFlow_1 > Object3D:HairBack_CasualFlow_2 > Object3D:CasualFlow1 > Bone:HairBack > Bone:Hair_Back > Bone:Hair_Back1 > SkinnedMesh:HairBack_CasualFlow_3
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### HairBack_Flare.glb

- Status: failing
- Armature name: (none named armature)
- Skeleton root: HairBack_Flare_2
- SkinnedMeshRenderer structure: HairBack_Flare_3 (SkinnedMesh), vertices 2021, materials HairBack_Flare_Mat
- Mesh names: HairBack_Flare_3
- Material names: HairBack_Flare_Mat
- Bone names: HairBack, Hair_Back, Hair_Back1
- Missing bones versus Body_BasicBody: HairBack, Hair_Back, Hair_Back1
- Extra Body_BasicBody bones not used by this item: 90 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 3 inverse bind matrices for 3 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65535; 85 weighted indices point outside the 3-bone skeleton; bad weight values 0; samples: v24:slot0->38579@0.396424; v26:slot0->57059@0.442871; v29:slot0->65532@0.707273; v81:slot0->1596@0.019603.
- Node hierarchy: Group:HairBack_Flare > Object3D:HairBack_Flare_1 > Object3D:HairBack_Flare_2 > Bone:HairBack > Bone:Hair_Back > Bone:Hair_Back1 > SkinnedMesh:HairBack_Flare_3
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### HairBack_HeroTie.glb

- Status: failing
- Armature name: (none named armature)
- Skeleton root: HairBack_HeroTie_2
- SkinnedMeshRenderer structure: HairBack_HeroTie_3 (SkinnedMesh), vertices 1356, materials HairBack_HeroTie_Mat
- Mesh names: HairBack_HeroTie_3
- Material names: HairBack_HeroTie_Mat
- Bone names: HairBack, Hair_Back, Hair_Back1, Hair_Pony, Hair_Pony1
- Missing bones versus Body_BasicBody: HairBack, Hair_Back, Hair_Back1, Hair_Pony, Hair_Pony1
- Extra Body_BasicBody bones not used by this item: 90 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 5 inverse bind matrices for 5 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65514; 23 weighted indices point outside the 5-bone skeleton; bad weight values 2; samples: v45:slot0->683@0.010388; v276:slot0->45138@0.3513; v310:slot0->215@0.001888; v314:slot0->683@0.009894.
- Node hierarchy: Group:HairBack_HeroTie > Object3D:HairBack_HeroTie_1 > Object3D:HairBack_HeroTie_2 > Bone:HairBack > Bone:Hair_Back > Bone:Hair_Back1 > Bone:Hair_Pony > Bone:Hair_Pony1 > SkinnedMesh:HairBack_HeroTie_3
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### HairBack_ShinryuCut.glb

- Status: failing
- Armature name: (none named armature)
- Skeleton root: Hairback_ShinryuCut
- SkinnedMeshRenderer structure: Hairback_ShinryuCut_1 (SkinnedMesh), vertices 1030, materials Hairback_ShinryuCut_Mat
- Mesh names: Hairback_ShinryuCut_1
- Material names: Hairback_ShinryuCut_Mat
- Bone names: HairBack, Hair_Back, Hair_Back1
- Missing bones versus Body_BasicBody: HairBack, Hair_Back, Hair_Back1
- Extra Body_BasicBody bones not used by this item: 90 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 3 inverse bind matrices for 3 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65532; 46 weighted indices point outside the 3-bone skeleton; bad weight values 16; samples: v8:slot0->47@0.000362; v9:slot0->70@0.000641; v10:slot0->4201@0.033893; v12:slot0->70@0.000538.
- Node hierarchy: Group:HairBack_ShinryuCut > Object3D:HairBack_ShinryuCut_1 > Object3D:Hairback_ShinryuCut > Bone:HairBack > Bone:Hair_Back > Bone:Hair_Back1 > SkinnedMesh:Hairback_ShinryuCut_1
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### HairBack_ShortPonyTail.glb

- Status: failing
- Armature name: (none named armature)
- Skeleton root: HairBack_ShortPonyTail_2
- SkinnedMeshRenderer structure: HairBack_ShortPonyTail_3 (SkinnedMesh), vertices 929, materials HairBack_PonyTail_Mat
- Mesh names: HairBack_ShortPonyTail_3
- Material names: HairBack_PonyTail_Mat
- Bone names: HairBack, Hair_Back, Hair_Back1
- Missing bones versus Body_BasicBody: HairBack, Hair_Back, Hair_Back1
- Extra Body_BasicBody bones not used by this item: 90 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 3 inverse bind matrices for 3 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65522; 15 weighted indices point outside the 3-bone skeleton; bad weight values 0; samples: v645:slot0->51972@0.461058; v669:slot0->51972@0.484452; v700:slot0->65522@0.739745; v706:slot0->65485@0.789445.
- Node hierarchy: Group:HairBack_ShortPonyTail > Object3D:HairBack_ShortPonyTail_1 > Object3D:HairBack_ShortPonyTail_2 > Bone:HairBack > Bone:Hair_Back > Bone:Hair_Back1 > SkinnedMesh:HairBack_ShortPonyTail_3
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### HairBack_TwinShortTails.glb

- Status: failing
- Armature name: Hair_BackRight
- Skeleton root: HairBack_TwinShortTails_2
- SkinnedMeshRenderer structure: HairBack_ShortPigTails (SkinnedMesh), vertices 1113, materials HairBack_TwinTails_Mat
- Mesh names: HairBack_ShortPigTails
- Material names: HairBack_TwinTails_Mat
- Bone names: HairBack, Hair_BackLeft, Hair_BackLeft1, Hair_BackRight, Hair_BackRight1
- Missing bones versus Body_BasicBody: HairBack, Hair_BackLeft, Hair_BackLeft1, Hair_BackRight, Hair_BackRight1
- Extra Body_BasicBody bones not used by this item: 90 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 5 inverse bind matrices for 5 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65535; 20 weighted indices point outside the 5-bone skeleton; bad weight values 0; samples: v622:slot0->284@0.002549; v625:slot0->261@0.002323; v629:slot0->15556@0.145256; v649:slot0->261@0.002338.
- Node hierarchy: Group:HairBack_TwinShortTails > Object3D:HairBack_TwinShortTails_1 > Object3D:HairBack_TwinShortTails_2 > Bone:HairBack > Bone:Hair_BackLeft > Bone:Hair_BackLeft1 > Bone:Hair_BackRight > Bone:Hair_BackRight1 > SkinnedMesh:HairBack_ShortPigTails
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### HairBack_WildTail.glb

- Status: failing
- Armature name: (none named armature)
- Skeleton root: HairBack_WildTail_2
- SkinnedMeshRenderer structure: HairBack_WildTail_3 (SkinnedMesh), vertices 1327, materials HairBack_WildTail_Mat
- Mesh names: HairBack_WildTail_3
- Material names: HairBack_WildTail_Mat
- Bone names: HairBack, Hair_Back, Hair_Back1
- Missing bones versus Body_BasicBody: HairBack, Hair_Back, Hair_Back1
- Extra Body_BasicBody bones not used by this item: 90 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 3 inverse bind matrices for 3 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65535; 38 weighted indices point outside the 3-bone skeleton; bad weight values 2; samples: v111:slot0->16@0.000204; v166:slot0->1217@0.011186; v172:slot0->65398@0.510863; v215:slot0->65035@0.58136.
- Node hierarchy: Group:HairBack_WildTail > Object3D:HairBack_WildTail_1 > Object3D:HairBack_WildTail_2 > Bone:HairBack > Bone:Hair_Back > Bone:Hair_Back1 > SkinnedMesh:HairBack_WildTail_3
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### HairBack_YokaiMane.glb

- Status: failing
- Armature name: (none named armature)
- Skeleton root: HairBack_YokaiMane_2
- SkinnedMeshRenderer structure: HairBack_YokaiCut (SkinnedMesh), vertices 1117, materials HairBack_YokaiMane_Mat
- Mesh names: HairBack_YokaiCut
- Material names: HairBack_YokaiMane_Mat
- Bone names: HairBack, Hair_Back, Hair_Back1
- Missing bones versus Body_BasicBody: HairBack, Hair_Back, Hair_Back1
- Extra Body_BasicBody bones not used by this item: 90 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 3 inverse bind matrices for 3 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65535; 18 weighted indices point outside the 3-bone skeleton; bad weight values 4; samples: v186:slot0->15@0.000129; v209:slot0->2395@0.031207; v215:slot0->24229@0.335491; v256:slot0->65534@0.8395.
- Node hierarchy: Group:HairBack_YokaiMane > Object3D:HairBack_YokaiMane_1 > Object3D:HairBack_YokaiMane_2 > Bone:HairBack > Bone:Hair_Back > Bone:Hair_Back1 > SkinnedMesh:HairBack_YokaiCut
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

## Feet failures

### Feet_AthleticMidTop.glb

- Status: failing
- Armature name: armature
- Skeleton root: pelvis
- SkinnedMeshRenderer structure: Feet_AthleticMidTop1 (SkinnedMesh), vertices 538, materials Feet_AthleticMidTop_Mat
- Mesh names: Feet_AthleticMidTop1
- Material names: Feet_AthleticMidTop_Mat
- Bone names: spine_01, pelvis, spine_02, spine_03, spine_04, spine_05, neck_01, neck_02, head, eyeRoot_r, eyeSocket_r, eye_r, eyeRoot_l, eyeSocket_l, eye_l, Jaw, clavicle_l, upperarm_l, upperarm_twist_01_l, upperarm_twist_02_l, lowerarm_l, lowerarm_twist_02_l, lowerarm_twist_01_l, hand_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ring_01_l, ring_02_l, ring_03_l, thumb_01_l, thumb_02_l, thumb_03_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, shoulder_twist_l, clavicle_r, upperarm_r, upperarm_twist_01_r, upperarm_twist_02_r, lowerarm_r, lowerarm_twist_02_r, lowerarm_twist_01_r, hand_r, middle_metacarpal_r, middle_01_r, middle_02_r, middle_03_r, pinky_metacarpal_r, pinky_01_r, pinky_02_r, pinky_03_r, ring_metacarpal_r, ring_01_r, ring_02_r, ring_03_r, thumb_01_r, thumb_02_r, thumb_03_r, index_metacarpal_r, index_01_r, index_02_r, index_03_r, shoulder_twist_r, breast_l, breast_r, thigh_r, thigh_twist_01_r, thigh_twist_01_r1, calf_r, calf_twist_01_r, calf_twist_01_r1, foot_r, ball_r, thigh_l, thigh_twist_01_l, thigh_twist_01_l1, calf_l, calf_twist_01_l, calf_twist_01_l1, foot_l, ball_l
- Missing bones versus Body_BasicBody: none
- Extra Body_BasicBody bones not used by this item: none
- Bind poses / inverse bind matrices: 90 inverse bind matrices for 90 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65261; 39 weighted indices point outside the 90-bone skeleton; bad weight values 10; samples: v10:slot0->56530@0.671754; v20:slot0->65135@0.874024; v24:slot0->49124@0.065675; v25:slot0->7572@0.054862.
- Node hierarchy: Group:Feet_AthleticMidTop > Object3D:Feet_AthleticMidTop_1 > Object3D:Feet_AthleticMidTop_2 > Object3D:armature > Object3D:root > Bone:pelvis > Bone:spine_01 > Bone:spine_02 > Bone:spine_03 > Bone:spine_04 > Bone:breast_l > Bone:breast_r > Bone:spine_05 > Bone:clavicle_l > Bone:upperarm_l > Bone:lowerarm_l > Bone:hand_l > Bone:index_metacarpal_l > Bone:index_01_l > Bone:index_02_l > Bone:index_03_l > Bone:middle_metacarpal_l > Bone:middle_01_l > Bone:middle_02_l > Bone:middle_03_l > Bone:pinky_metacarpal_l > Bone:pinky_01_l > Bone:pinky_02_l > Bone:pinky_03_l > Bone:ring_metacarpal_l > Bone:ring_01_l > Bone:ring_02_l > Bone:ring_03_l > Bone:thumb_01_l > Bone:thumb_02_l > Bone:thumb_03_l > Bone:lowerarm_twist_01_l > Bone:lowerarm_twist_02_l > Bone:shoulder_twist_l > Bone:upperarm_twist_01_l > Bone:upperarm_twist_02_l > Bone:clavicle_r > Bone:upperarm_r > Bone:lowerarm_r > Bone:hand_r > Bone:index_metacarpal_r > Bone:index_01_r > Bone:index_02_r > Bone:index_03_r > Bone:middle_metacarpal_r > Bone:middle_01_r > Bone:middle_02_r > Bone:middle_03_r > Bone:pinky_metacarpal_r > Bone:pinky_01_r > Bone:pinky_02_r > Bone:pinky_03_r > Bone:ring_metacarpal_r > Bone:ring_01_r > Bone:ring_02_r > Bone:ring_03_r > Bone:thumb_01_r > Bone:thumb_02_r > Bone:thumb_03_r > Bone:lowerarm_twist_01_r > Bone:lowerarm_twist_02_r > Bone:shoulder_twist_r > Bone:upperarm_twist_01_r > Bone:upperarm_twist_02_r > Bone:neck_01 > Bone:neck_02 > Bone:head > Bone:eyeRoot_l > Bone:eyeSocket_l > Bone:eye_l > Bone:eyeRoot_r > Bone:eyeSocket_r > Bone:eye_r > Bone:Jaw > Bone:thigh_l > Bone:calf_l > Bone:calf_twist_01_l > Bone:calf_twist_01_l1 > Bone:foot_l > Bone:ball_l > Bone:thigh_twist_01_l > Bone:thigh_twist_01_l1 > Bone:thigh_r > Bone:calf_r > Bone:calf_twist_01_r > Bone:calf_twist_01_r1 > Bone:foot_r > Bone:ball_r > Bone:thigh_twist_01_r > Bone:thigh_twist_01_r1 > SkinnedMesh:Feet_AthleticMidTop1
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### Feet_BalletFlats.glb

- Status: failing
- Armature name: armature
- Skeleton root: thigh_r
- SkinnedMeshRenderer structure: Feet_BalletFlats_4 (SkinnedMesh), vertices 1857, materials Feet_BalletFlats_Mat
- Mesh names: Feet_BalletFlats_4
- Material names: Feet_BalletFlats_Mat
- Bone names: calf_r, calf_twist_01_r1, foot_r, ball_r, calf_l, calf_twist_01_l1, foot_l, ball_l
- Missing bones versus Body_BasicBody: none
- Extra Body_BasicBody bones not used by this item: 82 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 8 inverse bind matrices for 8 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65532; 86 weighted indices point outside the 8-bone skeleton; bad weight values 20; samples: v4:slot0->59911@0.970821; v6:slot0->53774@0.947877; v18:slot0->28609@0.604762; v26:slot0->184@0.0007.
- Node hierarchy: Group:Feet_BalletFlats > Object3D:Feet_BalletFlats_1 > Object3D:Feet_BalletFlats_2 > Object3D:armature > Object3D:root > Object3D:pelvis > Object3D:thigh_l > Bone:calf_l > Bone:calf_twist_01_l1 > Bone:foot_l > Bone:ball_l > Object3D:thigh_r > Bone:calf_r > Bone:calf_twist_01_r1 > Bone:foot_r > Bone:ball_r > Object3D:Feet_BalletFlats_3 > SkinnedMesh:Feet_BalletFlats_4
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### Feet_ClassyLoafers.glb

- Status: failing
- Armature name: armature
- Skeleton root: thigh_r
- SkinnedMeshRenderer structure: Feet_ClassyLoafers_4 (SkinnedMesh), vertices 530, materials Feet_ClassyLoafers_Mat
- Mesh names: Feet_ClassyLoafers_4
- Material names: Feet_ClassyLoafers_Mat
- Bone names: calf_r, calf_twist_01_r, calf_twist_01_r1, foot_r, ball_r, calf_l, calf_twist_01_l, calf_twist_01_l1, foot_l, ball_l
- Missing bones versus Body_BasicBody: none
- Extra Body_BasicBody bones not used by this item: 80 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 10 inverse bind matrices for 10 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65535; 17 weighted indices point outside the 10-bone skeleton; bad weight values 0; samples: v23:slot0->303@0.000908; v46:slot0->62051@0.77067; v47:slot0->65535@0.994258; v72:slot0->65492@0.983983.
- Node hierarchy: Group:Feet_ClassyLoafers > Object3D:Feet_ClassyLoafers_1 > Object3D:Feet_ClassyLoafers_2 > Object3D:armature > Object3D:root > Object3D:pelvis > Object3D:thigh_l > Bone:calf_l > Bone:calf_twist_01_l > Bone:calf_twist_01_l1 > Bone:foot_l > Bone:ball_l > Object3D:thigh_r > Bone:calf_r > Bone:calf_twist_01_r > Bone:calf_twist_01_r1 > Bone:foot_r > Bone:ball_r > Object3D:Feet_ClassyLoafers_3 > SkinnedMesh:Feet_ClassyLoafers_4
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### Feet_FlowerFlipFlops.glb

- Status: failing
- Armature name: armature
- Skeleton root: thigh_r
- SkinnedMeshRenderer structure: Feet_SimpleFlipFlops_1 (SkinnedMesh), vertices 988, materials Feet_FlowerFlipFlops_Mat
- Mesh names: Feet_SimpleFlipFlops_1
- Material names: Feet_FlowerFlipFlops_Mat
- Bone names: calf_r, calf_twist_01_r1, foot_r, ball_r, calf_l, calf_twist_01_l1, foot_l, ball_l
- Missing bones versus Body_BasicBody: none
- Extra Body_BasicBody bones not used by this item: 82 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 8 inverse bind matrices for 8 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65535; 26 weighted indices point outside the 8-bone skeleton; bad weight values 0; samples: v12:slot0->58282@0.920282; v16:slot0->56910@0.60698; v17:slot0->55046@0.760279; v33:slot0->56910@0.550435.
- Node hierarchy: Group:Feet_FlowerFlipFlops > Object3D:Feet_FlowerFlipFlops_1 > Object3D:Feet_SimpleFlipFlops > Object3D:armature > Object3D:root > Object3D:pelvis > Object3D:thigh_l > Bone:calf_l > Bone:calf_twist_01_l1 > Bone:foot_l > Bone:ball_l > Object3D:thigh_r > Bone:calf_r > Bone:calf_twist_01_r1 > Bone:foot_r > Bone:ball_r > SkinnedMesh:Feet_SimpleFlipFlops_1
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### Feet_OfficeHeels.glb

- Status: failing
- Armature name: armature
- Skeleton root: thigh_r
- SkinnedMeshRenderer structure: Feet_OfficeHeels_4 (SkinnedMesh), vertices 964, materials Feet_OfficeHeels_Mat
- Mesh names: Feet_OfficeHeels_4
- Material names: Feet_OfficeHeels_Mat
- Bone names: calf_r, calf_twist_01_r1, foot_r, ball_r, calf_l, calf_twist_01_l1, foot_l, ball_l
- Missing bones versus Body_BasicBody: none
- Extra Body_BasicBody bones not used by this item: 82 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 8 inverse bind matrices for 8 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65535; 22 weighted indices point outside the 8-bone skeleton; bad weight values 12; samples: v76:slot0->29217@0.338008; v91:slot0->39305@0.877633; v93:slot0->903@0.003382; v107:slot0->2186@0.006461.
- Node hierarchy: Group:Feet_OfficeHeels > Object3D:Feet_OfficeHeels_1 > Object3D:Feet_OfficeHeels_2 > Object3D:armature > Object3D:root > Object3D:pelvis > Object3D:thigh_l > Bone:calf_l > Bone:calf_twist_01_l1 > Bone:foot_l > Bone:ball_l > Object3D:thigh_r > Bone:calf_r > Bone:calf_twist_01_r1 > Bone:foot_r > Bone:ball_r > Object3D:Feet_OfficeHeels_3 > SkinnedMesh:Feet_OfficeHeels_4
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### Feet_SimpleFlipFlops.glb

- Status: failing
- Armature name: armature
- Skeleton root: thigh_r
- SkinnedMeshRenderer structure: Feet_SimpleFlipFlops1_1 (SkinnedMesh), vertices 632, materials Feet_SimpleFlipFlops_Mat
- Mesh names: Feet_SimpleFlipFlops1_1
- Material names: Feet_SimpleFlipFlops_Mat
- Bone names: calf_r, calf_twist_01_r1, foot_r, ball_r, calf_l, calf_twist_01_l1, foot_l, ball_l
- Missing bones versus Body_BasicBody: none
- Extra Body_BasicBody bones not used by this item: 82 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 8 inverse bind matrices for 8 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65535; 27 weighted indices point outside the 8-bone skeleton; bad weight values 0; samples: v12:slot0->58282@0.920282; v16:slot0->56910@0.60698; v17:slot0->55046@0.760279; v33:slot0->56910@0.550435.
- Node hierarchy: Group:Feet_SimpleFlipFlops > Object3D:Feet_SimpleFlipFlops_1 > Object3D:Feet_SimpleFlipFlops_2 > Object3D:armature > Object3D:root > Object3D:pelvis > Object3D:thigh_l > Bone:calf_l > Bone:calf_twist_01_l1 > Bone:foot_l > Bone:ball_l > Object3D:thigh_r > Bone:calf_r > Bone:calf_twist_01_r1 > Bone:foot_r > Bone:ball_r > Object3D:Feet_SimpleFlipFlops1 > SkinnedMesh:Feet_SimpleFlipFlops1_1
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### Feet_StrappedSandals.glb

- Status: failing
- Armature name: armature
- Skeleton root: thigh_r
- SkinnedMeshRenderer structure: Feet_StrappedSandals_4 (SkinnedMesh), vertices 1542, materials Feet_StrappedSandals_Mat
- Mesh names: Feet_StrappedSandals_4
- Material names: Feet_StrappedSandals_Mat
- Bone names: calf_r, calf_twist_01_r, calf_twist_01_r1, foot_r, ball_r, calf_l, calf_twist_01_l, calf_twist_01_l1, foot_l, ball_l
- Missing bones versus Body_BasicBody: none
- Extra Body_BasicBody bones not used by this item: 80 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 10 inverse bind matrices for 10 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65534; 106 weighted indices point outside the 10-bone skeleton; bad weight values 20; samples: v1:slot0->65522@0.524306; v3:slot0->65272@0.703058; v27:slot0->53029@0.975543; v29:slot0->63354@0.636977.
- Node hierarchy: Group:Feet_StrappedSandals > Object3D:Feet_StrappedSandals_1 > Object3D:Feet_StrappedSandals_2 > Object3D:armature > Object3D:root > Object3D:pelvis > Object3D:thigh_l > Bone:calf_l > Bone:calf_twist_01_l > Bone:calf_twist_01_l1 > Bone:foot_l > Bone:ball_l > Object3D:thigh_r > Bone:calf_r > Bone:calf_twist_01_r > Bone:calf_twist_01_r1 > Bone:foot_r > Bone:ball_r > Object3D:Feet_StrappedSandals_3 > SkinnedMesh:Feet_StrappedSandals_4
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

### Feet_WorkBoots.glb

- Status: failing
- Armature name: armature
- Skeleton root: thigh_r
- SkinnedMeshRenderer structure: Feet_WorkBoots_4 (SkinnedMesh), vertices 978, materials Feet_WorkBoots_Mat
- Mesh names: Feet_WorkBoots_4
- Material names: Feet_WorkBoots_Mat
- Bone names: calf_r, calf_twist_01_r, calf_twist_01_r1, foot_r, ball_r, calf_l, calf_twist_01_l, calf_twist_01_l1, foot_l, ball_l
- Missing bones versus Body_BasicBody: none
- Extra Body_BasicBody bones not used by this item: 80 Body_BasicBody bones not used by this item: pelvis, spine_01, spine_02, spine_03, spine_04, breast_l, breast_r, spine_05, clavicle_l, upperarm_l, lowerarm_l, hand_l, index_metacarpal_l, index_01_l, index_02_l, index_03_l, middle_metacarpal_l, middle_01_l, middle_02_l, middle_03_l, pinky_metacarpal_l, pinky_01_l, pinky_02_l, pinky_03_l, ring_metacarpal_l, ...
- Bind poses / inverse bind matrices: 10 inverse bind matrices for 10 bones; bind matrix is [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1].
- Skin indices / weights: JOINTS_0/WEIGHTS_0 item sizes 2/2; max skin index 65535; 43 weighted indices point outside the 10-bone skeleton; bad weight values 4; samples: v59:slot0->78@0.000113; v63:slot0->53877@0.124592; v82:slot0->49597@0.946468; v156:slot0->4626@0.013549.
- Node hierarchy: Group:Feet_WorkBoots > Object3D:Feet_WorkBoots_1 > Object3D:Feet_WorkBoots_2 > Object3D:armature > Object3D:root > Object3D:pelvis > Object3D:thigh_l > Bone:calf_l > Bone:calf_twist_01_l > Bone:calf_twist_01_l1 > Bone:foot_l > Bone:ball_l > Object3D:thigh_r > Bone:calf_r > Bone:calf_twist_01_r > Bone:calf_twist_01_r1 > Bone:foot_r > Bone:ball_r > Object3D:Feet_WorkBoots_3 > SkinnedMesh:Feet_WorkBoots_4
- Exact reason it fails: The exported JOINTS_0 data contains weighted bone indices outside the skeleton array. Three.js then asks for skeleton.bones[index].matrixWorld while calculating skinned bounds, but skeleton.bones[index] is undefined.
- Recommended fix: Re-export this asset so JOINTS_0 and WEIGHTS_0 are valid VEC4 skin attributes and every weighted joint index is below the GLB skin joint count. Do not solve this by merging meshes or removing skeletons.
- Confidence: High

## Cause classification

| Possible cause | Finding | Confidence |
|---|---|---|
| Exporter / exported data | Primary cause. Failing assets contain invalid weighted JOINTS_0 values and use two-component JOINTS/WEIGHTS where working skinned assets use four-component attributes. | High |
| GLTFLoader | Not the primary cause. It loads the scene and exposes the GLB skin accessors; the out-of-range values are already in the loaded attributes. | High |
| SkeletonUtils.clone() | Not the primary cause. Clone creation succeeds for the inspected failures; the invalid skin indices remain and later fail during bounds/skinning evaluation. | High |
| clone() | Native clone is not the deciding factor. The data problem exists before clone-specific code matters. | Medium |
| Incorrect bone matching | Secondary issue for final attachment. Hair bones are not present in Body_BasicBody and must be attached/rebound to a matching hair skeleton or attachment rig. Shoes mostly use body foot/leg bones and still fail because their skin indices are corrupt. | High |
| Missing bones | Not the direct cause of the matrixWorld throw for shoes; failing shoes have no missing body bones. Hair models have hair-specific bones missing from Body_BasicBody, but working hair with the same kind of missing hair bones renders correctly when kept with its own skeleton. | High |
| Duplicate armatures | Not supported by this evidence. The failing pattern follows invalid skin attributes, not armature duplication. | Medium |
| Incompatible bind poses | Not the direct cause of these throws. Inverse bind matrix counts match bone counts in failing meshes; the failure occurs earlier from invalid skin indices. Bind pose compatibility still needs attention before final runtime rebinding. | Medium |
| Unsupported Unity feature | Possible upstream contributor only if the exporter mishandles Unity skin influences or optimization settings. The runtime symptom is standard invalid glTF skin data. | Medium |
| Incorrect Three.js implementation | Not the primary cause. Three.js is correctly failing when asked to evaluate a bone index that does not exist. Runtime can add guards, but that would mask broken assets rather than attach them correctly. | High |

## Recommended next step

Do not merge meshes, remove skeletons, or change the BoZo structure. The next decision should focus on the Unity export step: inspect why the failing SkinnedMeshRenderers are emitted with two-component JOINTS/WEIGHTS and out-of-range weighted indices. The target export shape should match the working assets: valid VEC4 JOINTS_0/WEIGHTS_0, joint indices below the skin joint count, inverse bind matrices matching the joint list, and the existing modular hierarchy preserved.

Screenshots were not useful for this diagnosis because the failing state is a data-level skinning exception before a meaningful rendered comparison.

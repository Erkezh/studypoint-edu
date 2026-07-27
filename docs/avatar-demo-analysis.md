# Avatar Demo Analysis

## Source

- Manifest: `/assets/characters/bozo/manifests/avatar-assets.json`
- Runtime asset root: `public/assets/characters/bozo/`
- Model count: 144 GLB files
- Texture count: 220 texture files
- Manifest item count: 144

## Categories

- Body: 1 item, example `Body_BasicBody`
- Bottom: 15 items, examples `Bottom_BaggyPants`, `Bottom_BeltedPants`, `Bottom_BeltedShorts`
- EyeBrows: 4 items, examples `Brows_BasicBrows`, `Brows_PillBrows`, `Brows_ThickBrows`
- EyeLashes: 2 items, examples `Eyelashes_LongLashes`, `Eyelashes_ShortLashes`
- EyeShine: 1 item, example `EyeShine_DoubleRound`
- Eyes: 1 item, example `Eyes_Eyes01`
- FaceDetails: 3 items, examples `FaceDetails_FrecklesHeavy`, `FaceDetails_FrecklesLight`, `FaceDetails_FrecklesMedium`
- Feet: 12 items, examples `Feet_AthleticMidTop`, `Feet_BalletFlats`, `Feet_ClassyLoafers`
- Gloves: 10 items, examples `Hands_ArmBands`, `Hands_ArmWarmers`, `Hands_FingerlessGloves`
- HairBack: 19 items, examples `HairBack_CasualFlow`, `HairBack_Flare`, `HairBack_HeroTie`
- HairFront: 13 items, examples `HairFront_AsymmetricalFringe`, `HairFront_CurtainBangs`, `HairFront_EmoBangs`
- Hat: 9 items, examples `Hat_BallCap`, `Hat_Beanie`, `Hat_BucketHat`
- Head: 2 items, examples `Head_Young`, `Head_Young_v2`
- HeadAcc: 4 items, examples `HeadAcc_AlienAttena`, `HeadAcc_DevilHorns`, `HeadAcc_FlufflessKittyEars`
- Leggings: 1 item, example `Leggings_Stockings`
- LowerFace: 3 items, examples `LowerFace_SharpBeard`, `LowerFace_SharpChin`, `LowerFace_SharpGoatee`
- MakeUpCheeks: 1 item, example `MakeUpCheeks_SimpleBlush`
- MakeUpLips: 1 item, example `MakeUpLips_SimpleLipStick`
- Neck: 1 item, example `Neck_RibbonBow`
- Overall: 3 items, examples `Overall_Overall`, `Overall_SmartDress`, `Overall_Sundress`
- Pupil: 4 items, examples `Pupil_HeartPupil`, `Pupil_Round`, `Pupil_Square`
- Socks: 4 items, examples `Socks_KneeHighs`, `Socks_SimpleSocks`, `Socks_ThighHigh`
- Top: 19 items, examples `Top_ComfyCartagan`, `Top_DressShirt`, `Top_FullSuit`
- UnderLower: 3 items, examples `Underlower_ShortSpats`, `UnderLower_SimpleBoxers`, `UnderLower_SimplePanties`
- UnderUpper: 2 items, examples `UnderUpper_SimpleBra`, `UnderUpper_SimpleUnderShirt`
- UpperFace: 5 items, examples `UpperFace_MedicalEyePatch`, `UpperFace_RoundGlasses`, `UpperFace_RoundGlassesLens`
- modular: 1 item, example `BMAC_MergedCharacterBase`

## Minimal Default Assembly

- Base body: `Body_BasicBody`, model `/assets/characters/bozo/models/Body_BasicBody.glb`
- Head: `Head_Young`, model `/assets/characters/bozo/models/Head_Young.glb`
- Eyes: `Eyes_Eyes01`, model `/assets/characters/bozo/models/Eyes_Eyes01.glb`
- Front hair: `HairFront_ShotaFringe`, model `/assets/characters/bozo/models/HairFront_ShotaFringe.glb`
- Back hair: `HairBack_MessyHair`, model `/assets/characters/bozo/models/HairBack_MessyHair.glb`
- Top: `Top_Tshirt`, model `/assets/characters/bozo/models/Top_Tshirt.glb`
- Bottom: `Bottom_SimpleShorts`, model `/assets/characters/bozo/models/Bottom_SimpleShorts.glb`
- Footwear: `Feet_SimpleSneakers`, model `/assets/characters/bozo/models/Feet_SimpleSneakers.glb`

The current browser demo intentionally exposes a 29-item stable milestone subset instead of all 144 manifest items. The visible switchable subset includes 2 front hair items, 7 back hair items, 7 tops, 5 bottoms, 4 footwear items, 2 heads, 1 eyes item, and 1 body item.

Example texture paths include `/assets/characters/bozo/textures/Body__Texture2D_Body_BasicBody_v2.png`, `/assets/characters/bozo/textures/EyesMaterial__Texture2D_Eyes_01.png`, `/assets/characters/bozo/textures/BMAC_Top_Tshirt__Texture2D_Top_Shirt_D.png`, `/assets/characters/bozo/textures/Bottom_SimpleShorts_Mat__Texture2D_Bottom_SimpleShorts_D.png`, and `/assets/characters/bozo/textures/Feet_SimpleSneakers_Mat__Texture2D_Feet_SimpleSneakers_D.png`.

## Skeleton And Mesh Findings

- `Body_BasicBody` contains 90 bones and many body SkinnedMesh parts including names such as `ankles`, `back`, and other body segments.
- `Head_Young` contains 90 bones and one `Combined_Skinned_Mesh`; it is compatible with the base body skeleton.
- `Eyes_Eyes01` contains 90 bones and one SkinnedMesh named `eyes01`; it references the same body skeleton names, but this GLB has `skinIndex` without `skinWeight`, so the viewer installs a guarded Three.js loader compatibility patch.
- `HairFront_ShotaFringe` contains 7 hair bones: `HairFront`, `Hair_Left`, `Hair_Left1`, `Hair_Front`, `Hair_Front1`, `Hair_Right`, and `Hair_Right1`. These bones are not present in `Body_BasicBody`.
- `HairBack_MessyHair` does not expose SkinnedMesh data in the inspected scene and can be added as a standalone renderable item.
- `Top_Tshirt` contains one SkinnedMesh named `BMAC_Shirt_1` and is compatible with the base body skeleton.
- `Bottom_SimpleShorts` contains one SkinnedMesh named `Bottom_SimpleShorts_4` and is compatible with the base body skeleton.
- `Feet_SimpleSneakers` contains 10 leg and foot bones and one SkinnedMesh named `Feet_SimpleSneakers_4`; it is compatible with the base body skeleton.
- Morph target names were not found in the inspected default GLBs, even though the manifest reports blend shape counts for some items.

## Compatibility Result

Most default body-worn modular items share exact body bone names and can be rebound to `Body_BasicBody`. Front hair does not share all required bones with the body skeleton, so it is kept as a temporary standalone fallback with its own small hair skeleton. This avoids fake success and prevents duplicate body armatures from being treated as compatible.

Browser verification found that some exported GLBs have incomplete skinning data that makes Three.js fail during precise skinned bounding-box calculation. The viewer now uses safe geometry-local bounds for camera framing and includes repairs for missing `skinWeight` attributes and missing skeleton bone objects. Items that still fail clone/bounds validation are hidden from this first milestone UI rather than being presented as working.

## Material Limitations

The current implementation relies on materials and texture references already present in the GLB. The manifest texture paths are preserved for inspection and future material customization, but the demo does not yet rebuild color channels, ID maps, decals, or pattern systems from Unity.

The browser demo applies diffuse-looking manifest textures when available, but many meshes still appear with flat red/default channel colors. This is a known material limitation of the current export because Unity color channels, ID maps, and shader logic are not yet reconstructed in Three.js.

## Recommended Assembly Strategy

Use `Body_BasicBody` as the base skeleton, clone selected GLB scenes from a source cache, rebind compatible SkinnedMesh objects by exact bone name, and remove redundant armature nodes only after a successful rebind. If an item has missing bones, keep it as a documented fallback for this milestone. For a production avatar system, Unity should export a shared complete avatar skeleton GLB, including hair accessory bones, or export all modular meshes against a single canonical skeleton.

## Future Optimizations

- Draco compression
- Meshopt compression
- KTX2 textures
- Texture resizing
- Texture atlases
- Mesh merging for fixed equipped outfits

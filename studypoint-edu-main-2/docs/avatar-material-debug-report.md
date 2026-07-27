# BoZo avatar material debug report

Updated: 2026-07-17

## Export inventory

- 144 validated GLB files reference 220 exported texture files.
- The runtime now preserves the materials and texture assignments embedded in each GLB.
- Base-color and emissive maps are treated as sRGB. Normal and data maps remain linear.
- Exported alpha modes, alpha cutoffs, and side settings are retained. Alpha-clipped materials are not unnecessarily marked transparent.
- The previous global diffuse-texture replacement, white color override, and forced `DoubleSide` override were removed.

## Safe runtime corrections

Only standard glTF/PBR corrections are applied: color-space assignment for color textures and normalization of alpha-clipped material transparency. The demo does not emulate Unity shaders.

## Metadata that is still missing

The manifest lists color-channel labels, `supportsDecals`, `supportsPatterns`, material names, and texture URLs, but it does not define the shader contract needed to reproduce the Unity customization system. In particular, it lacks:

- channel-to-ID-map numeric values and masks;
- per-channel default colors, blend modes, and allowed ranges;
- pattern texture selection, UV transforms, scale, rotation, and blend behavior;
- decal atlas coordinates, projection/UV rules, ordering, and blend modes;
- Unity shader keywords and parameter-to-glTF material mappings;
- explicit semantics for every auxiliary texture beyond filename conventions.

No arbitrary recoloring, decal emulation, or pattern emulation has been added. Those features should wait for an explicit web material schema exported alongside the manifest.

## Known presentation limitations

The web result is limited to the standard PBR data contained in each GLB. Any appearance that depended on a Unity custom shader, lighting model, channel recoloring, decal pass, or pattern pass cannot be reproduced exactly from the current metadata.

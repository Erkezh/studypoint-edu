#!/usr/bin/env bash
set -euo pipefail

SOURCE="/Users/ayaulyzhumakan/CharacterCustomization/Assets/WebExport"
DEST="public/assets/characters/bozo"

if [[ ! -d "$SOURCE" ]]; then
  echo "Error: Unity export folder is missing: $SOURCE" >&2
  exit 1
fi

for required in models textures manifests manifests/avatar-assets.json manifests/materials.json; do
  if [[ ! -e "$SOURCE/$required" ]]; then
    echo "Error: required Unity export path is missing: $SOURCE/$required" >&2
    exit 1
  fi
done

mkdir -p "$DEST/models" "$DEST/textures" "$DEST/manifests"

copied=0
skipped=0
overwritten=0

copy_tree() {
  local subdir="$1"
  local src_dir="$SOURCE/$subdir"
  local dst_dir="$DEST/$subdir"

  while IFS= read -r -d '' src; do
    rel="${src#$src_dir/}"
    dst="$dst_dir/$rel"
    mkdir -p "$(dirname "$dst")"

    if [[ -f "$dst" ]]; then
      if cmp -s "$src" "$dst"; then
        skipped=$((skipped + 1))
      else
        cp -p "$src" "$dst"
        overwritten=$((overwritten + 1))
      fi
    else
      cp -p "$src" "$dst"
      copied=$((copied + 1))
    fi
  done < <(find "$src_dir" -type f ! -name '*.meta' ! -name '.DS_Store' -print0)
}

copy_tree models
copy_tree textures
copy_tree manifests

if [[ ! -f "$DEST/manifests/avatar-assets.json" ]]; then
  echo "Error: avatar-assets.json was not copied to $DEST/manifests/avatar-assets.json" >&2
  exit 1
fi

node <<'NODE'
const fs = require('fs');
const path = require('path');

const dest = 'public/assets/characters/bozo';
const manifestPath = path.join(dest, 'manifests/avatar-assets.json');
const backupPath = path.join(dest, 'manifests/avatar-assets.original.json');
const browserPrefix = '/assets/characters/bozo/';

function normalizeRuntimePath(value, marker) {
  if (typeof value !== 'string' || value.startsWith(browserPrefix)) return value;
  const normalized = value.replace(/\\/g, '/');
  const index = normalized.indexOf(marker);
  return index === -1 ? value : browserPrefix + normalized.slice(index);
}

function localFileFromBrowserPath(value) {
  if (typeof value !== 'string' || !value.startsWith(browserPrefix)) return null;
  return path.join('public', value.slice(1));
}

const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
fs.copyFileSync(manifestPath, backupPath);

let normalizedCount = 0;
function setNormalized(target, key, value) {
  if (target[key] !== value) {
    target[key] = value;
    normalizedCount += 1;
  }
}

setNormalized(manifest, 'modelFolder', browserPrefix + 'models');
setNormalized(manifest, 'textureFolder', browserPrefix + 'textures');

const assets = Array.isArray(manifest.assets) ? manifest.assets : [];
for (const item of assets) {
  if (item.modelPath) {
    const modelPath = normalizeRuntimePath(item.modelPath, 'models/');
    setNormalized(item, 'modelPath', modelPath);
  }

  if (Array.isArray(item.textures)) {
    item.textures = item.textures.map((texture) => {
      const normalized = normalizeRuntimePath(texture, 'textures/');
      if (normalized !== texture) normalizedCount += 1;
      return normalized;
    });
  }
}

const brokenReferences = [];
for (const item of assets) {
  const label = item.name || item.id || 'asset';
  const refs = [item.modelPath, ...(Array.isArray(item.textures) ? item.textures : [])];
  for (const ref of refs) {
    const localPath = localFileFromBrowserPath(ref);
    if (!localPath || !fs.existsSync(localPath)) {
      brokenReferences.push(`${label}: ${ref}`);
    }
  }
}

if (brokenReferences.length > 0) {
  console.error('Error: manifest contains broken references:');
  for (const ref of brokenReferences) console.error(`- ${ref}`);
  process.exit(1);
}

fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + '\n');
console.log(`Normalized manifest paths: ${normalizedCount}`);
NODE

echo "BoZo assets sync complete."
echo "Copied: $copied"
echo "Skipped: $skipped"
echo "Overwritten: $overwritten"
echo "Destination: $DEST"

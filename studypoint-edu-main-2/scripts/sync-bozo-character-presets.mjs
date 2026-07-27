import { copyFile, mkdir, readdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'

const unityRoot = process.argv[2] || '/Users/ayaulyzhumakan/CharacterCustomization'
const savesDir = path.join(unityRoot, 'Assets/BoZo_ModularAnimeCharacters/CharacterSaves/Resources')
const iconsDir = path.join(unityRoot, 'Assets/BoZo_ModularAnimeCharacters/CharacterSaves/Icons')
const outputRoot = path.resolve('public/assets/characters/bozo/presets')

function numberList(source, key) {
  const match = source.match(new RegExp(`\\n    ${key}:\\n((?:    - [^\\n]+\\n)*)`))
  return match ? [...match[1].matchAll(/    - ([^\n]+)/g)].map((entry) => Number(entry[1])) : []
}

function stringList(source, key) {
  const match = source.match(new RegExp(`\\n    ${key}:\\n((?:    - [^\\n]+\\n)*)`))
  return match ? [...match[1].matchAll(/    - ([^\n]+)/g)].map((entry) => entry[1].trim()) : []
}

function parseColors(block) {
  const colorsBlock = block.match(/\n      colors:\n([\s\S]*?)(?=\n      decal:)/)?.[1] || ''
  return [...colorsBlock.matchAll(/\{r: ([^,]+), g: ([^,]+), b: ([^,]+), a: ([^}]+)\}/g)].map((entry) => ({
    r: Number(entry[1]),
    g: Number(entry[2]),
    b: Number(entry[3]),
    a: Number(entry[4]),
  }))
}

function parsePreset(source, filename) {
  const name = source.match(/\n    characterName: ([^\n]+)/)?.[1]?.trim() || path.basename(filename, '.asset')
  const outfitBlocks = source.split(/\n    - outfit: /).slice(1)
  const outfits = outfitBlocks.map((block) => {
    const outfitPath = block.slice(0, block.indexOf('\n')).trim()
    return {
      outfitPath,
      sourceName: outfitPath.split('/').pop(),
      colors: parseColors(`\n${block}`),
    }
  })
  const slug = path.basename(filename, '.asset').toLowerCase().replace(/_/g, '-')
  return {
    id: slug,
    name,
    thumbnail: `/assets/characters/bozo/presets/${slug}.png`,
    bodyShapes: Object.fromEntries(stringList(source, 'bodyIDs').map((key, index) => [key, numberList(source, 'bodyShapes')[index]])),
    faceShapes: Object.fromEntries(stringList(source, 'faceIDs').map((key, index) => [key, numberList(source, 'faceShapes')[index]])),
    outfits,
  }
}

await mkdir(outputRoot, { recursive: true })
const filenames = (await readdir(savesDir)).filter((name) => name.endsWith('.asset')).sort()
const presets = []
for (const filename of filenames) {
  const source = (await readFile(path.join(savesDir, filename), 'utf8')).replace(/\r\n/g, '\n')
  const preset = parsePreset(source, filename)
  await copyFile(path.join(iconsDir, `${path.basename(filename, '.asset')}.png`), path.join(outputRoot, `${preset.id}.png`))
  presets.push(preset)
}

await writeFile(path.join(outputRoot, 'character-presets.json'), `${JSON.stringify({ presets }, null, 2)}\n`)
console.info(`Synced ${presets.length} BoZo character presets from ${savesDir}`)

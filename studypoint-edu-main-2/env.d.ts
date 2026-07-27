/// <reference types="vite/client" />
/* eslint-disable @typescript-eslint/no-explicit-any */

interface Window {
  webkitAudioContext?: typeof AudioContext
}

declare module 'canvas-confetti'

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<object, object, unknown>
  export default component
}

declare module 'three' {
  export class Object3D {
    [key: string]: any
  }
  export class WebGLRenderer {
    [key: string]: any
  }
  export class Scene extends Object3D {
    [key: string]: any
  }
  export class PerspectiveCamera extends Object3D {
    [key: string]: any
  }
  export class Group extends Object3D {
    [key: string]: any
  }
  export class Clock {
    [key: string]: any
  }
  export class Color {
    [key: string]: any
  }
  export class Texture {
    [key: string]: any
  }
  export class Material {
    [key: string]: any
  }
  export class MeshStandardMaterial extends Material {
    [key: string]: any
  }
  export class Mesh extends Object3D {
    [key: string]: any
  }
  export const ACESFilmicToneMapping: any
  export const AmbientLight: any
  export const AnimationMixer: any
  export const Box3: any
  export const CanvasTexture: any
  export const CircleGeometry: any
  export const CylinderGeometry: any
  export const DirectionalLight: any
  export const DoubleSide: any
  export const EquirectangularReflectionMapping: any
  export const HemisphereLight: any
  export const LinearFilter: any
  export const MathUtils: any
  export const MeshBasicMaterial: any
  export const MeshPhysicalMaterial: any
  export const PCFSoftShadowMap: any
  export const PMREMGenerator: any
  export const PlaneGeometry: any
  export const RepeatWrapping: any
  export const SRGBColorSpace: any
  export const ShadowMaterial: any
  export const SphereGeometry: any
  export const Vector2: any
  export const Vector3: any
  export const Vector4: any
}

declare module 'three/examples/jsm/controls/OrbitControls.js' {
  export class OrbitControls {
    [key: string]: any
    constructor(...args: any[])
  }
}

declare module 'three/examples/jsm/loaders/GLTFLoader.js' {
  export class GLTFLoader {
    [key: string]: any
    constructor(...args: any[])
  }
}

declare module 'three/examples/jsm/environments/RoomEnvironment.js' {
  export class RoomEnvironment {
    [key: string]: any
    constructor(...args: any[])
  }
}

declare module 'three/examples/jsm/utils/SkeletonUtils.js' {
  export function clone(...args: any[]): any
}

interface ImportMetaEnv {
  readonly VITE_API_URL?: string
  readonly DEV: boolean
  readonly PROD: boolean
  readonly MODE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

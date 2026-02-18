const defaultApiBaseUrl = import.meta.env.DEV ? 'http://127.0.0.1:8001' : ''
const rawApiBaseUrl = (import.meta.env.VITE_API_URL || defaultApiBaseUrl).trim()
const normalizedApiBaseUrl = rawApiBaseUrl.replace(/\/+$/, '')
const localhostApiUrlPattern = /^https?:\/\/(?:localhost|127(?:\.\d{1,3}){3})(?::\d+)?$/i

const shouldUseSameOriginApi =
  import.meta.env.PROD && localhostApiUrlPattern.test(normalizedApiBaseUrl)

if (shouldUseSameOriginApi && typeof window !== 'undefined') {
  console.warn(
    '[api] VITE_API_URL points to localhost in production; using same-origin /api proxy.'
  )
}

export const API_BASE_URL = shouldUseSameOriginApi ? '' : normalizedApiBaseUrl

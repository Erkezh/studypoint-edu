const browserApiBaseUrl =
  typeof window !== 'undefined' && window.location.hostname
    ? `http://${window.location.hostname}:8001`
    : 'http://localhost:8001'

const defaultApiBaseUrl = import.meta.env.DEV ? browserApiBaseUrl : ''
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

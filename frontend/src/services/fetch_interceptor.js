/**
 * Global fetch interceptor that injects the user-supplied LLM headers
 * (X-User-LLM-*) on every request when configured. The user-supplied
 * config lives in localStorage (read via the Pinia store), so we lazy-
 * import the store on first use to avoid circular deps during module
 * initialization.
 *
 * This is the simplest place to wire the headers because every fetch in
 * the app (api.js, auth.js, outfit.js, recommendation.js, garment.js,
 * etc.) goes through the global `window.fetch` once it's been wrapped.
 */

import { buildUserLlmHeaders } from './user_llm'

let _originalFetch = null
let _installed = false

export function setupFetchInterceptor() {
  if (_installed) return
  if (typeof window === 'undefined' || !window.fetch) return
  _installed = true
  _originalFetch = window.fetch.bind(window)

  window.fetch = async (input, init = {}) => {
    try {
      const url = typeof input === 'string' ? input : input?.url
      const raw = typeof localStorage !== 'undefined'
        ? localStorage.getItem('l-wardrobe.user_llm')
        : null

      if (url && raw) {
        const target = new URL(url, window.location.origin)
        const apiBase = new URL((import.meta.env.VITE_API_BASE_URL || '/api/v1'), window.location.origin)
        const isApiRequest = target.origin === apiBase.origin && target.pathname.startsWith(apiBase.pathname)

        if (isApiRequest) {
          const config = JSON.parse(raw)
          const extra = buildUserLlmHeaders(config)
          if (extra && Object.keys(extra).length > 0) {
            const merged = new Headers(init.headers || (input instanceof Request ? input.headers : undefined))
            for (const [k, v] of Object.entries(extra)) merged.set(k, v)
            init = { ...init, headers: merged }
          }
        }
      }
    } catch {
      // Never break a request because the interceptor failed
    }
    return _originalFetch(input, init)
  }
}

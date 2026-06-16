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
      // Read config from localStorage directly to avoid pulling in the
      // Pinia store here (which would require Pinia to be active).
      const raw = typeof localStorage !== 'undefined'
        ? localStorage.getItem('l-wardrobe.user_llm')
        : null
      if (raw) {
        const config = JSON.parse(raw)
        const headers = buildUserLlmHeaders(config)
        if (headers && Object.keys(headers).length > 0) {
          init = { ...init, headers: { ...(init.headers || {}), ...headers } }
        }
      }
    } catch (e) {
      // Never break a request because the interceptor failed
    }
    return _originalFetch(input, init)
  }
}

/**
 * User-supplied LLM Pinia store.
 *
 * Persists the user-supplied LLM config in localStorage under
 * `l-wardrobe.user_llm`. The store also exposes a `getFetchHeaders()`
 * helper that the api fetch interceptor can use to inject the
 * X-User-LLM-* headers into every outgoing request.
 */

import { defineStore } from 'pinia'
import { buildUserLlmHeaders, testUserKey, testUserVision, listUserModels } from '../services/user_llm'

const STORAGE_KEY = 'l-wardrobe.user_llm'

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    // Defensive: ensure required shape
    if (!parsed.api_key || !parsed.base_url || !parsed.model) return null
    return {
      api_key: String(parsed.api_key),
      base_url: String(parsed.base_url),
      model: String(parsed.model),
      enabled: parsed.enabled !== false, // default true
      validated_at: parsed.validated_at || null,
    }
  } catch (e) {
    console.warn('Failed to load user_llm config from localStorage:', e)
    return null
  }
}

function saveToStorage(config) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config))
  } catch (e) {
    console.warn('Failed to save user_llm config to localStorage:', e)
  }
}

function clearStorage() {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch (e) {
    /* ignore */
  }
}

export const useUserLlmStore = defineStore('user_llm', {
  state: () => ({
    config: loadFromStorage(),
    // Transient test state (not persisted)
    isTestingKey: false,
    isTestingVision: false,
    isLoadingModels: false,
    availableModels: [],
    lastTestResult: null, // { ok: bool, message: string }
    lastVisionResult: null, // { multimodal_ok, response_text, error }
  }),

  getters: {
    isActive: (state) =>
      !!(state.config && state.config.enabled && state.config.api_key && state.config.base_url && state.config.model),
    isVisionCapable: (state) => !!state.config?.model,
  },

  actions: {
    /** Headers to attach to every fetch call (empty if not configured). */
    getFetchHeaders() {
      return buildUserLlmHeaders(this.config)
    },

    /** Pull a fresh model list for the (api_key, base_url) pair. */
    async refreshAvailableModels() {
      if (!this.config) {
        this.availableModels = []
        return []
      }
      this.isLoadingModels = true
      try {
        const resp = await listUserModels({
          api_key: this.config.api_key,
          base_url: this.config.base_url,
        })
        if (resp.available) {
          this.availableModels = resp.models || []
        } else {
          this.availableModels = []
        }
        return this.availableModels
      } catch (e) {
        console.warn('refreshAvailableModels failed:', e)
        this.availableModels = []
        return []
      } finally {
        this.isLoadingModels = false
      }
    },

    /**
     * Test the (api_key, base_url) pair. Stores the result on the store
     * for the UI to display.
     */
    async runTestKey({ api_key, base_url }) {
      this.isTestingKey = true
      this.lastTestResult = null
      try {
        const resp = await testUserKey({ api_key, base_url })
        this.lastTestResult = {
          ok: !!resp.available,
          message: resp.message || (resp.available ? 'OK' : 'Failed'),
          model_count: resp.model_count || 0,
        }
        if (resp.available) {
          this.availableModels = resp.models_sample || resp.models || []
        }
        return this.lastTestResult
      } catch (e) {
        this.lastTestResult = { ok: false, message: e.message }
        return this.lastTestResult
      } finally {
        this.isTestingKey = false
      }
    },

    /** Test that the chosen model supports multimodal input. */
    async runTestVision({ api_key, base_url, model }) {
      this.isTestingVision = true
      this.lastVisionResult = null
      try {
        const resp = await testUserVision({ api_key, base_url, model })
        this.lastVisionResult = {
          multimodal_ok: !!resp.multimodal_ok,
          response_text: resp.response_text || '',
          error: resp.error || null,
        }
        return this.lastVisionResult
      } catch (e) {
        this.lastVisionResult = { multimodal_ok: false, error: e.message }
        return this.lastVisionResult
      } finally {
        this.isTestingVision = false
      }
    },

    /** Persist a config to localStorage and update state. */
    saveConfig({ api_key, base_url, model, enabled = true }) {
      this.config = {
        api_key: String(api_key || '').trim(),
        base_url: String(base_url || '').trim().replace(/\/+$/, ''),
        model: String(model || '').trim(),
        enabled,
        validated_at: new Date().toISOString(),
      }
      saveToStorage(this.config)
    },

    /** Update the `enabled` flag without re-validating. */
    setEnabled(enabled) {
      if (!this.config) return
      this.config.enabled = !!enabled
      this.config.validated_at = new Date().toISOString()
      saveToStorage(this.config)
    },

    /** Remove the config from localStorage and reset state. */
    clearConfig() {
      this.config = null
      this.availableModels = []
      this.lastTestResult = null
      this.lastVisionResult = null
      clearStorage()
    },
  },
})

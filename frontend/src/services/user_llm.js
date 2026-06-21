/**
 * User-supplied LLM (API key) service.
 *
 * Wraps the three backend test endpoints. The actual API key never
 * lives in any persisted file on the server; it's kept in the user's
 * browser (localStorage) and transmitted per request as headers.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

/**
 * Build the three X-User-LLM-* headers from a stored config.
 * If the config is missing or disabled, returns {}.
 */
export function buildUserLlmHeaders(config) {
  if (!config || !config.enabled || !config.api_key || !config.base_url || !config.model) {
    return {}
  }
  return {
    'X-User-LLM-Enabled': '1',
    'X-User-LLM-Key': config.api_key,
    'X-User-LLM-Base': config.base_url,
    'X-User-LLM-Model': config.model,
  }
}

/**
 * Build a 1x1 transparent PNG as a Blob for the vision test upload.
 * Generated client-side so we never need a real image asset.
 */
function make1x1PngBlob() {
  // 1x1 transparent PNG, base64-encoded
  const b64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGP4//8/AwAI/AL+XJZcuwAAAABJRU5ErkJggg=='
  const binary = atob(b64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
  return new Blob([bytes], { type: 'image/png' })
}

async function _postJson(path, body) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const detail = payload?.detail || `Request failed (HTTP ${response.status})`
    throw new Error(detail)
  }
  return payload
}

/**
 * POST /user/llm/test-key — verify (api_key, base_url) by listing models.
 */
export async function testUserKey({ api_key, base_url }) {
  return _postJson('/user/llm/test-key', { api_key, base_url })
}

/**
 * POST /user/llm/test-vision — upload a 1x1 PNG and ask the model to
 * describe it, confirming multimodal support.
 */
export async function testUserVision({ api_key, base_url, model }) {
  const fd = new FormData()
  fd.append('api_key', api_key)
  fd.append('base_url', base_url)
  fd.append('model', model)
  fd.append('image', make1x1PngBlob(), 'test.png')
  const response = await fetch(`${API_BASE_URL}/user/llm/test-vision`, {
    method: 'POST',
    body: fd,
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload?.detail || `Vision test failed (HTTP ${response.status})`)
  }
  return payload
}

/**
 * POST /user/llm/models — list available models for the dropdown.
 */
export async function listUserModels({ api_key, base_url }) {
  return _postJson('/user/llm/models', { api_key, base_url })
}

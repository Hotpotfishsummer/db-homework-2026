/**
 * AI 推荐服务
 *
 * 与 AI 搭配 (outfit.js) 严格区分:
 * - 搭配: 严格限于衣橱内组合 (outfit/recommend)
 * - 推荐: 推荐新购单品 + 嵌入搭配 + 衣橱缺口 (recommend/*)
 */

import { API_BASE_URL } from './api'
import { useAuthStore } from '../stores/auth'

/**
 * 统一 fetch 封装: 注入 Bearer token, 处理 200 envelope, 抛错带后端 msg
 */
async function _request(path, init = {}) {
  const authStore = useAuthStore()
  const token = authStore.token || localStorage.getItem('token')
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init.headers || {}),
    },
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok || payload.code !== 200) {
    const message = payload?.msg || `请求失败 (HTTP ${response.status})`
    throw new Error(message)
  }
  return payload.data
}

/**
 * AI 单品推荐 (新购)
 * @param {Object} params - { scene, gapFocus? }
 * @returns {Promise<{ items, scene, weatherSummary, toolSummary, generatedBy }>}
 */
export async function generateShoppingItems({ scene, gapFocus = null } = {}) {
  return _request('/recommend/items', {
    method: 'POST',
    body: JSON.stringify({ scene, gapFocus }),
  })
}

/**
 * AI 推荐 + 嵌入搭配 (混合)
 * @param {Object} params - { scene }
 * @returns {Promise<{ outfit, weatherSummary, toolSummary, generatedBy }>}
 */
export async function generateShoppingOutfit({ scene } = {}) {
  return _request('/recommend/items/with-outfit', {
    method: 'POST',
    body: JSON.stringify({ scene }),
  })
}

/**
 * 衣橱缺口分析
 * @returns {Promise<{ report, toolSummary }>}
 */
export async function analyzeWardrobeGap() {
  return _request('/recommend/gap-analysis', {
    method: 'POST',
    body: JSON.stringify({}),
  })
}

/**
 * 推荐历史列表
 * @param {Object} params - { status?, limit?, offset? }
 * @returns {Promise<{ items, limit, offset }>}
 */
export async function listRecommendations({ status = 'pending', limit = 20, offset = 0 } = {}) {
  const qs = new URLSearchParams({ status, limit, offset }).toString()
  return _request(`/recommend/items?${qs}`)
}

/**
 * 更新推荐状态
 * @param {string} id - UUID
 * @param {string} status - 'bought' | 'dismissed' | 'wishlist' | 'pending'
 */
export async function updateRecommendationStatus(id, status) {
  return _request(`/recommend/items/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  })
}

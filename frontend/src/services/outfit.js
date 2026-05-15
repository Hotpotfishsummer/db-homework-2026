/**
 * AI 搭配 API 服务
 * 负责调用后端 AI 搭配接口
 */

import { API_BASE_URL, API_TIMEOUT } from './api'

/**
 * 获取 AI 穿搭推荐
 * @param {string} scene - 场景：commute/date/casual/sports/party
 * @param {Array} wardrobeIds - 可用衣服 ID 列表
 * @returns {Promise<Object>} 搭配结果
 */
export async function getAIOutfit(scene, wardrobeIds) {
  // 检查是否有 token
  const token = localStorage.getItem('token')
  if (!token) {
    throw new Error('未登录，请先登录')
  }

  try {
    const response = await fetch(`${API_BASE_URL}/outfit/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        scene,
        wardrobeIds
      }),
      signal: AbortSignal.timeout(API_TIMEOUT)
    })

    if (!response.ok) {
      throw new Error(`请求失败: ${response.status}`)
    }

    const result = await response.json()

    if (result.code !== 200) {
      throw new Error(result.msg || '获取推荐失败')
    }

    return result.data
  } catch (error) {
    console.error('AI 搭配请求失败:', error)
    throw error
  }
}

/**
 * 获取推荐理由（可选）
 * @param {number} outfitId - 搭配 ID
 * @returns {Promise<string>} 推荐理由
 */
export async function getOutfitReason(outfitId) {
  const token = localStorage.getItem('token')

  const response = await fetch(`${API_BASE_URL}/outfit/${outfitId}/reason`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })

  const result = await response.json()
  return result.data?.reason || ''
}

import { API_BASE_URL } from './api'
import { useAuthStore } from '../stores/auth'

/**
 * AI 搭配生成 —— 真实后端入口
 * 调 POST /api/v1/outfit/recommend，后端使用 LangChain Agent + 真实衣橱数据。
 *
 * @param {Object} params - { scene, weather, wardrobeIds }
 * @returns {Promise<{ outfits: Array }>} 统一为 outfits 数组，供 store/OutfitCard 消费
 */
export async function generateOutfit(params) {
  const { scene, wardrobeIds } = params
  const authStore = useAuthStore()
  const token = authStore.token || localStorage.getItem('token')

  const response = await fetch(`${API_BASE_URL}/outfit/recommend`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify({
      scene,
      wardrobeIds: wardrobeIds || []
    })
  })

  const payload = await response.json().catch(() => ({}))
  if (!response.ok || payload.code !== 200) {
    const message = payload?.msg || `推荐失败 (HTTP ${response.status})`
    throw new Error(message)
  }

  return { outfits: [normalizeRecommendation(payload.data, params)] }
}

/**
 * 将后端返回的单条推荐 (data) 适配为 OutfitCard 期望的 outfit 对象。
 * - 槽位 top/bottom/shoes/accessory 从 selectedItems 按 category 匹配
 * - 衣橱为空/单品不足时 selectedItems=[] 也会得到一张空卡，UI 自行处理
 */
function normalizeRecommendation(data, params) {
  const { scene, weather } = params
  const items = Array.isArray(data?.selectedItems) ? data.selectedItems : []

  const pickByCategory = (category) =>
    items.find((it) => (it?.category || '').toLowerCase() === category) || null

  const top = pickByCategory('top')
  const bottom = pickByCategory('bottom')
  const shoes = pickByCategory('shoes') || pickByCategory('outerwear')
  const accessory =
    pickByCategory('accessory') || pickByCategory('bag') || null

  const fallbackItem = items[0] || null
  const safe = (item) =>
    item
      ? {
          id: item.id,
          name: item.name || '未命名单品',
          image: item.image || '',
          category: item.category || 'other'
        }
      : null

  const weatherSummary = data?.weatherSummary || ''
  const weatherNote = weather
    ? `考虑今日${weather.temp ?? ''}°C天气，${weather.desc ?? weatherSummary ?? ''}`
    : weatherSummary || '基于您的风格偏好推荐'

  return {
    outfitId: data?.id || `AI-${Date.now().toString(36).toUpperCase()}`,
    scene: data?.scene || scene || '休闲',
    matchRate: typeof data?.matchRate === 'number' ? data.matchRate : 0,
    top: safe(top) || safe(fallbackItem),
    bottom: safe(bottom),
    shoes: safe(shoes),
    accessory: safe(accessory),
    reason: data?.reason || data?.description || '已根据您的衣橱生成搭配建议',
    weatherNote,
    name: data?.name || '',
    description: data?.description || '',
    generatedBy: data?.generatedBy || 'langchain-agent'
  }
}

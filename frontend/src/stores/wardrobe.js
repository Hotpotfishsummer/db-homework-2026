import { defineStore } from 'pinia'
import { listGarments, deleteGarment } from '../services/garment'

const normalizeImageUrl = (imageUrl) => {
  if (!imageUrl) {
    return ''
  }

  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://') || imageUrl.startsWith('data:')) {
    return imageUrl
  }

  if (imageUrl.startsWith('/static/')) {
    return imageUrl
  }

  return imageUrl.replace(/^app\/static\/?/, '/static/')
}

export const useWardrobeStore = defineStore('wardrobe', {
  state: () => ({
    clothes: [],
    loading: false,
    error: null,
    categories: [
      { id: 'all', name: '全部', icon: '📦' },
      { id: 'top', name: '上装', icon: '👕' },
      { id: 'outerwear', name: '外套', icon: '🧥' },
      { id: 'bottom', name: '下装', icon: '👖' },
      { id: 'shoes', name: '鞋靴', icon: '👟' },
      { id: 'accessory', name: '配饰', icon: '💍' },
      { id: 'bag', name: '包包', icon: '👜' }
    ],
    filterCategory: 'all'
  }),

  getters: {
    filteredClothes: (state) => {
      if (state.filterCategory === 'all') {
        return state.clothes
      }
      return state.clothes.filter(item => item.category === state.filterCategory)
    },
    // 可用衣服（排除清洗中的），用于 AI 搭配
    availableClothes: (state) => {
      return state.clothes.filter(item => item.status === 'available')
    },
    // 获取指定分类的可用衣服
    availableByCategory: (state) => (category) => {
      if (category === 'all') {
        return state.clothes.filter(item => item.status === 'available')
      }
      return state.clothes.filter(item => item.category === category && item.status === 'available')
    }
  },

  actions: {
    normalizeGarment(item) {
      const analysis = item.attributes?.tags || null
      return {
        id: item.item_id || item.id,
        name: item.attributes?.source_filename || item.attributes?.name || item.name || '未命名',
        category: item.category || 'other',
        color: item.attributes?.color || null,
        image: normalizeImageUrl(item.image_url),
        backendId: item.item_id || item.id,
        analysis,
        sourceFilename: item.attributes?.source_filename || item.name || '未命名',
        originalName: item.attributes?.original_name || item.attributes?.source_filename || item.name || '未命名',
        publicUrl: item.attributes?.public_url || normalizeImageUrl(item.image_url),
        storedPath: item.attributes?.stored_path || null,
        format: item.attributes?.format || null,
        detection: item.attributes?.detection || null,
        tags: Array.isArray(analysis?.tags) ? analysis.tags : [],
        status: item.attributes?.status || 'available',
        createdAt: item.created_at || new Date().toISOString(),
      }
    },

    addCloth(cloth) {
      this.clothes.push({
        id: cloth.backendId || cloth.id || Date.now(),
        ...cloth,
        createdAt: new Date().toISOString()
      })
    },

    removeCloth(id) {
      const index = this.clothes.findIndex(item => item.id === id)
      if (index > -1) {
        this.clothes.splice(index, 1)
      }
    },

    /**
     * 异步删除衣物：先在 UI 上移除，后端成功则保持，失败则回滚。
     * @param {string|number} id
     * @returns {Promise<{ok:boolean, msg?:string}>}
     */
    async deleteClothAsync(id) {
      const index = this.clothes.findIndex(item => item.id === id)
      if (index === -1) {
        return { ok: false, msg: '衣物不存在' }
      }

      // 软删除在后端是按 item_id 查的，优先使用 backendId
      const target = this.clothes[index]
      const backendId = target.backendId || target.id

      // 乐观更新：先从本地数组移除
      const removed = this.clothes.splice(index, 1)[0]

      const res = await deleteGarment(backendId)
      if (res.code !== 200) {
        // 回滚：把衣物放回原位置
        this.clothes.splice(index, 0, removed)
        return { ok: false, msg: res.msg || '删除失败' }
      }

      return { ok: true }
    },

    updateClothStatus(id, status) {
      const cloth = this.clothes.find(item => item.id === id)
      if (cloth) {
        cloth.status = status
      }
    },

    setFilter(category) {
      this.filterCategory = category
    },

    async refreshWardrobe() {
      this.loading = true
      this.error = null
      try {
        const res = await listGarments()
        if (res.code === 200 && res.data && Array.isArray(res.data.garments)) {
          this.clothes = res.data.garments
            .map(item => this.normalizeGarment(item))
            .sort((left, right) => new Date(right.createdAt) - new Date(left.createdAt))
        } else {
          this.error = res.msg || '获取衣物失败'
        }
      } catch (e) {
        this.error = e?.message || '未知错误'
      } finally {
        this.loading = false
      }
    },
  }
})
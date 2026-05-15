import { defineStore } from 'pinia'

export const useWardrobeStore = defineStore('wardrobe', {
  state: () => ({
    clothes: [],
    categories: [
      { id: 'all', name: '全部', icon: '📦' },
      { id: 'top', name: '上装', icon: '👕' },
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
    addCloth(cloth) {
      this.clothes.push({
        id: Date.now(),
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

    updateClothStatus(id, status) {
      const cloth = this.clothes.find(item => item.id === id)
      if (cloth) {
        cloth.status = status
      }
    },

    setFilter(category) {
      this.filterCategory = category
    },

    initMockData() {
      if (this.clothes.length === 0) {
        this.clothes = [
          { id: 1, name: '白色基础款T恤', category: 'top', color: '#FFFFFF', image: 'https://picsum.photos/200?random=1', status: 'available' },
          { id: 2, name: '黑色休闲裤', category: 'bottom', color: '#1a1a1a', image: 'https://picsum.photos/200?random=2', status: 'available' },
          { id: 3, name: '灰色卫衣', category: 'top', color: '#9ca3af', image: 'https://picsum.photos/200?random=3', status: 'washing' },
          { id: 4, name: '白色运动鞋', category: 'shoes', color: '#FFFFFF', image: 'https://picsum.photos/200?random=4', status: 'available' },
          { id: 5, name: '蓝色牛仔外套', category: 'top', color: '#3b82f6', image: 'https://picsum.photos/200?random=5', status: 'available' },
          { id: 6, name: '黑色手提包', category: 'bag', color: '#1a1a1a', image: 'https://picsum.photos/200?random=6', status: 'available' },
          { id: 7, name: '卡其色休闲裤', category: 'bottom', color: '#d4a574', image: 'https://picsum.photos/200?random=7', status: 'available' },
          { id: 8, name: '金色项链', category: 'accessory', color: '#fbbf24', image: 'https://picsum.photos/200?random=8', status: 'available' }
        ]
      }
    }
  }
})
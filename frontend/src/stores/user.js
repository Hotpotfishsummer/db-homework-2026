import { defineStore } from 'pinia'
import { uploadAvatar } from '../services/user'

export const useUserStore = defineStore('user', {
  state: () => ({
    profile: {
      avatar: null,
      nickname: '',
      skinTone: null,
      bodyType: null,
      styles: []
    },
    likedOutfits: [],
    historyOutfits: []
  }),

  getters: {
    hasProfile: (state) => {
      return state.profile.skinTone && state.profile.bodyType && state.profile.styles.length > 0
    }
  },

  actions: {
    updateProfile(data) {
      this.profile = { ...this.profile, ...data }
      this.persistProfile()
    },

    async updateAvatar(file) {
      const res = await uploadAvatar(file)
      if (res.code === 200) {
        this.profile.avatar = res.data.url
        this.persistProfile()
        return res
      }
      throw new Error(res.msg)
    },

    persistProfile() {
      localStorage.setItem('user_profile', JSON.stringify(this.profile))
    },

    loadProfile() {
      const saved = localStorage.getItem('user_profile')
      if (saved) {
        this.profile = { ...this.profile, ...JSON.parse(saved) }
      }
    },

    likeOutfit(outfit) {
      if (!this.likedOutfits.find(o => o.id === outfit.id)) {
        this.likedOutfits.push({ ...outfit, likedAt: new Date().toISOString() })
      }
    },

    unlikeOutfit(outfitId) {
      const index = this.likedOutfits.findIndex(o => o.id === outfitId)
      if (index > -1) {
        this.likedOutfits.splice(index, 1)
      }
    },

    addToHistory(outfit) {
      this.historyOutfits.unshift({ ...outfit, viewedAt: new Date().toISOString() })
      if (this.historyOutfits.length > 50) {
        this.historyOutfits.pop()
      }
    }
  }
})
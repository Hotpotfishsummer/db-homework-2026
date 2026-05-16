import { defineStore } from 'pinia'
import { uploadAvatar } from '../services/user'

export const useUserStore = defineStore('user', {
  state: () => ({
    profile: {
      avatar: null,
      nickname: '',
      // 物理档案
      height: null,      // 身高 cm
      weight: null,     // 体重 kg
      bmi: null,        // 自动计算
      skinTone: null,    // 肤色
      bodyShape: null,   // 体型
      faceFeature: null, // 面部特征
      // 风格档案
      styleAxes: {
        minimalComplex: 50,     // 极简-繁复
        vintageModern: 50,      // 复古-科技
        formalCasual: 50        // 正式-休闲
      },
      styleTags: [],            // 风格标签
      favoriteColors: [],      // 红榜
      avoidColors: [],         // 黑榜
      fitPreference: null      // 版型偏好
    },
    likedOutfits: [],
    historyOutfits: []
  }),

  getters: {
    hasProfile: (state) => {
      return state.profile.skinTone && state.profile.bodyShape && state.profile.styleTags.length > 0
    },
    profileCompleteness: (state) => {
      const fields = [
        state.profile.height,
        state.profile.weight,
        state.profile.skinTone,
        state.profile.bodyShape,
        state.profile.faceFeature,
        state.profile.styleTags.length > 0,
        state.profile.favoriteColors.length > 0,
        state.profile.fitPreference
      ]
      return Math.round(fields.filter(Boolean).length / fields.length * 100)
    },
    calculatedBMI: (state) => {
      if (state.profile.height && state.profile.weight) {
        const heightM = state.profile.height / 100
        return (state.profile.weight / (heightM * heightM)).toFixed(1)
      }
      return null
    }
  },

  actions: {
    updateProfile(data) {
      this.profile = { ...this.profile, ...data }
      // 自动计算BMI
      if (data.height && data.weight) {
        const heightM = data.height / 100
        this.profile.bmi = (data.weight / (heightM * heightM)).toFixed(1)
      }
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
        const parsed = JSON.parse(saved)
        this.profile = {
          avatar: null,
          nickname: '',
          height: null,
          weight: null,
          bmi: null,
          skinTone: null,
          bodyShape: null,
          faceFeature: null,
          styleAxes: {
            minimalComplex: 50,
            vintageModern: 50,
            formalCasual: 50
          },
          styleTags: [],
          favoriteColors: [],
          avoidColors: [],
          fitPreference: null,
          ...parsed
        }
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
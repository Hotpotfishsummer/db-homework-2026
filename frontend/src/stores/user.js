import { defineStore } from 'pinia'
import { fetchUserProfile, updateUserProfile, uploadAvatar } from '../services/user'
import {
  favoriteOutfit,
  fetchFavoriteOutfits,
  unfavoriteOutfit,
} from '../services/outfit'

const STORAGE_LIKED_OUTFITS = 'l-wardrobe.liked-outfits'
const STORAGE_HISTORY_OUTFITS = 'l-wardrobe.history-outfits'

const defaultProfile = () => ({
  avatar: null,
  coverImage: null,
  nickname: '',
  bio: '',
  gender: null,
  birthday: null,
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
  fitPreference: null
})

const toBackendProfile = (profile) => ({
  display_name: profile.nickname || null,
  avatar_url: profile.avatar || null,
  bio: profile.bio || null,
  skin_tone: profile.skinTone || null,
  body_shape: profile.bodyShape || null,
  height: profile.height,
  weight: profile.weight,
  bmi: profile.bmi,
  face_feature: profile.faceFeature || null,
  style_axes: profile.styleAxes || {},
  style_tags: profile.styleTags || [],
  favorite_colors: profile.favoriteColors || [],
  avoid_colors: profile.avoidColors || [],
  fit_preference: profile.fitPreference || null,
})

const fromBackendProfile = (data) => ({
  ...defaultProfile(),
  avatar: data.avatar_url || null,
  nickname: data.display_name || data.username || '',
  bio: data.bio || '',
  height: data.height ?? null,
  weight: data.weight ?? null,
  bmi: data.bmi ?? null,
  skinTone: data.skin_tone || null,
  bodyShape: data.body_shape || null,
  faceFeature: data.face_feature || null,
  styleAxes: data.style_axes || defaultProfile().styleAxes,
  styleTags: Array.isArray(data.style_tags) ? data.style_tags : [],
  favoriteColors: Array.isArray(data.favorite_colors) ? data.favorite_colors : [],
  avoidColors: Array.isArray(data.avoid_colors) ? data.avoid_colors : [],
  fitPreference: data.fit_preference || null,
})

export const useUserStore = defineStore('user', {
  state: () => ({
    profile: defaultProfile(),
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
    async updateProfile(data) {
      this.profile = { ...this.profile, ...data }
      // 自动计算BMI
      if (data.height && data.weight) {
        const heightM = data.height / 100
        this.profile.bmi = (data.weight / (heightM * heightM)).toFixed(1)
      }
      this.persistProfile()
      await this.syncProfileToBackend()
    },

    async updateAvatar(file) {
      const res = await uploadAvatar(file)
      if (res.code === 200) {
        this.profile.avatar = res.data.url
        this.persistProfile()
        await this.syncProfileToBackend()
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
        this.profile = { ...defaultProfile(), ...parsed }
      }
      this.loadLocalOutfitActivity()
    },

    async loadProfileFromBackend() {
      this.loadProfile()
      try {
        const data = await fetchUserProfile()
        this.profile = {
          ...this.profile,
          ...fromBackendProfile(data),
          coverImage: this.profile.coverImage,
          gender: this.profile.gender,
          birthday: this.profile.birthday,
        }
        this.persistProfile()
        await this.loadFavoriteOutfitsFromBackend()
      } catch (error) {
        console.warn('从后端加载用户档案失败，使用本地缓存:', error.message)
      }
      return this.profile
    },

    async syncProfileToBackend() {
      const data = await updateUserProfile(toBackendProfile(this.profile))
      this.profile = {
        ...this.profile,
        ...fromBackendProfile(data),
        coverImage: this.profile.coverImage,
        gender: this.profile.gender,
        birthday: this.profile.birthday,
      }
      this.persistProfile()
      return this.profile
    },

    async likeOutfit(outfit) {
      const outfitId = outfit.outfitId || outfit.id
      const recommendId = outfit.recommendId || outfit.outfitId || outfit.id
      if (!this.likedOutfits.find(o => (o.outfitId || o.id) === outfitId)) {
        this.likedOutfits.push({
          ...outfit,
          id: outfitId,
          outfitId,
          recommendId,
          likedAt: new Date().toISOString()
        })
        this.persistLocalOutfitActivity()
      }

      if (this.canSyncOutfit(recommendId)) {
        try {
          const synced = await favoriteOutfit(recommendId)
          if (synced) {
            this.upsertLikedOutfit(synced)
          }
        } catch (error) {
          console.warn('同步收藏到后端失败，已保留本地收藏:', error.message)
        }
      }
    },

    async unlikeOutfit(outfitId) {
      const target = this.likedOutfits.find(o => (o.outfitId || o.id) === outfitId || o.recommendId === outfitId)
      const recommendId = target?.recommendId || target?.outfitId || target?.id || outfitId
      const index = this.likedOutfits.findIndex(o => (o.outfitId || o.id) === outfitId || o.recommendId === outfitId)
      if (index > -1) {
        this.likedOutfits.splice(index, 1)
        this.persistLocalOutfitActivity()
      }
      if (this.canSyncOutfit(recommendId)) {
        try {
          await unfavoriteOutfit(recommendId)
        } catch (error) {
          console.warn('同步取消收藏到后端失败:', error.message)
        }
      }
    },

    addToHistory(outfit) {
      // 跳过 AI 推荐的搭配，不记录到浏览历史
      if (outfit.source === 'ai') return

      const outfitId = outfit.outfitId || outfit.id
      // 如果已存在，先删除旧记录，避免重复
      this.historyOutfits = this.historyOutfits.filter(
        item => (item.outfitId || item.id) !== outfitId
      )
      // 添加到最前面
      this.historyOutfits.unshift({ ...outfit, viewedAt: new Date().toISOString() })
      if (this.historyOutfits.length > 50) {
        this.historyOutfits.pop()
      }
      this.persistLocalOutfitActivity()
    },

    removeFromHistory(outfitId) {
      this.historyOutfits = this.historyOutfits.filter(
        item => (item.outfitId || item.id) !== outfitId
      )
      this.persistLocalOutfitActivity()
    },

    clearHistory() {
      this.historyOutfits = []
      this.persistLocalOutfitActivity()
    },

    persistLocalOutfitActivity() {
      localStorage.setItem(STORAGE_LIKED_OUTFITS, JSON.stringify(this.likedOutfits))
      localStorage.setItem(STORAGE_HISTORY_OUTFITS, JSON.stringify(this.historyOutfits))
    },

    loadLocalOutfitActivity() {
      try {
        const liked = JSON.parse(localStorage.getItem(STORAGE_LIKED_OUTFITS) || '[]')
        const history = JSON.parse(localStorage.getItem(STORAGE_HISTORY_OUTFITS) || '[]')
        this.likedOutfits = Array.isArray(liked) ? liked : []
        this.historyOutfits = Array.isArray(history) ? history : []
      } catch {
        this.likedOutfits = []
        this.historyOutfits = []
      }
    },

    async loadFavoriteOutfitsFromBackend() {
      try {
        const remoteFavorites = await fetchFavoriteOutfits()
        const localOnly = this.likedOutfits.filter(item => !this.canSyncOutfit(item.recommendId || item.outfitId || item.id))
        this.likedOutfits = [...remoteFavorites, ...localOnly]
        this.persistLocalOutfitActivity()
      } catch (error) {
        console.warn('从后端加载收藏失败，使用本地缓存:', error.message)
      }
    },

    upsertLikedOutfit(outfit) {
      const outfitId = outfit.outfitId || outfit.id
      const index = this.likedOutfits.findIndex(item => (item.outfitId || item.id) === outfitId)
      if (index > -1) {
        this.likedOutfits.splice(index, 1, outfit)
      } else {
        this.likedOutfits.unshift(outfit)
      }
      this.persistLocalOutfitActivity()
    },

    canSyncOutfit(id) {
      return typeof id === 'string'
        && /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(id)
    },

    getBodyProfilePayload() {
      this.loadProfile()
      return {
        height: this.profile.height,
        weight: this.profile.weight,
        bmi: this.profile.bmi,
        skinTone: this.profile.skinTone,
        bodyShape: this.profile.bodyShape,
        faceFeature: this.profile.faceFeature,
        styleAxes: this.profile.styleAxes,
        styleTags: this.profile.styleTags,
        favoriteColors: this.profile.favoriteColors,
        avoidColors: this.profile.avoidColors,
        fitPreference: this.profile.fitPreference,
      }
    }
  }
})

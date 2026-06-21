import { defineStore } from 'pinia'
import { generateOutfit } from '../services/outfit'
import { useWardrobeStore } from './wardrobe'
import { useUserStore } from './user'

const CURRENT_OUTFIT_KEY = 'l-wardrobe.current-outfit'

export const useOutfitStore = defineStore('outfit', {
  state: () => ({
    outfits: [],
    isGenerating: false,
    selectedScene: 'casual',
    currentState: 'input', // input | generating | results
    generationError: null,
    currentOutfit: null
  }),

  getters: {
    hasOutfits: (state) => state.outfits.length > 0,
  },

  actions: {
    selectScene(scene) {
      this.selectedScene = scene
    },

    async startGeneration(params) {
      const { scene } = params
      this.selectedScene = scene
      this.isGenerating = true
      this.currentState = 'generating'
      this.generationError = null
      this.outfits = []

      try {
        // 传入 wardrobeIds 供真实 API 使用
        const wardrobeStore = useWardrobeStore()
        const userStore = useUserStore()
        const wardrobeIds = wardrobeStore.availableClothes.map(c => c.id)
        const bodyProfile = userStore.getBodyProfilePayload()

        const result = await generateOutfit({
          scene,
          wardrobeIds,
          bodyProfile
        })
        this.outfits = result.outfits
        if (this.outfits.length > 0) {
          this.setCurrentOutfit(this.outfits[0])
        }
      } catch (error) {
        this.generationError = error.message
        throw error
      } finally {
        this.isGenerating = false
        this.currentState = 'results'
      }
    },

    setCurrentOutfit(outfit) {
      this.currentOutfit = outfit || null
      if (outfit) {
        sessionStorage.setItem(CURRENT_OUTFIT_KEY, JSON.stringify(outfit))
      } else {
        sessionStorage.removeItem(CURRENT_OUTFIT_KEY)
      }
    },

    getPersistedCurrentOutfit() {
      if (this.currentOutfit) {
        return this.currentOutfit
      }
      const raw = sessionStorage.getItem(CURRENT_OUTFIT_KEY)
      if (!raw) {
        return null
      }
      try {
        const outfit = JSON.parse(raw)
        this.currentOutfit = outfit
        return outfit
      } catch {
        sessionStorage.removeItem(CURRENT_OUTFIT_KEY)
        return null
      }
    },

    async likeOutfit(outfit) {
      const userStore = useUserStore()
      await userStore.likeOutfit(outfit)
      userStore.addToHistory(outfit)
      this.removeCurrentOutfit()
    },

    skipOutfit(outfit) {
      const userStore = useUserStore()
      userStore.addToHistory(outfit)
      this.removeCurrentOutfit()
    },

    removeCurrentOutfit() {
      this.outfits.shift()
      if (this.outfits.length === 0) {
        this.currentState = 'input'
      }
    },

    resetToInput() {
      this.outfits = []
      this.isGenerating = false
      this.currentState = 'input'
      this.generationError = null
      this.setCurrentOutfit(null)
    }
  }
})

import { defineStore } from 'pinia'
import { generateOutfit } from '../services/outfit'
import { useWardrobeStore } from './wardrobe'
import { useUserStore } from './user'

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
    currentOutfit: (state) => state.outfits[0] || null
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

        const result = await generateOutfit({
          scene,
          wardrobeIds,
          bodyProfile: userStore.profile
        })
        this.outfits = result.outfits
      } catch (error) {
        this.generationError = error.message
        throw error
      } finally {
        this.isGenerating = false
        this.currentState = 'results'
      }
    },

    likeOutfit(outfit) {
      const userStore = useUserStore()
      userStore.likeOutfit(outfit)
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
    }
  }
})

import { defineStore } from 'pinia'
import { generateOutfitService } from '../services/outfit'
import { useUserStore } from './user'

export const useOutfitStore = defineStore('outfit', {
  state: () => ({
    outfits: [],
    isGenerating: false,
    selectedScene: 'casual',
    selectedWeather: null,
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

    selectWeather(weather) {
      this.selectedWeather = weather
    },

    async startGeneration(params) {
      const { scene, weather } = params
      this.selectedScene = scene
      this.selectedWeather = weather
      this.isGenerating = true
      this.currentState = 'generating'
      this.generationError = null
      this.outfits = []

      try {
        const result = await generateOutfitService({ scene, weather })
        if (result.code === 200) {
          this.outfits = result.data.outfits
        } else {
          throw new Error(result.msg || '生成失败')
        }
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

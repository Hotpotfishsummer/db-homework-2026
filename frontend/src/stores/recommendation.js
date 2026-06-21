/**
 * AI 推荐 Pinia store
 *
 * 三种模式 (mode):
 * - 'items': 单品推荐列表 (默认)
 * - 'outfit': 嵌入新品的搭配方案
 * - 'gap': 衣橱缺口报告
 */

import { defineStore } from 'pinia'
import {
  generateShoppingItems,
  generateShoppingOutfit,
  analyzeWardrobeGap,
  updateRecommendationStatus,
} from '../services/recommendation'

export const useRecommendationStore = defineStore('recommendation', {
  state: () => ({
    // 通用
    mode: 'items', // 'items' | 'outfit' | 'gap'
    selectedScene: 'casual',
    isGenerating: false,
    generationError: null,

    // 单品列表
    items: [],
    itemsWeather: '',
    itemsGeneratedBy: '',

    // 嵌入搭配
    outfit: null, // { id, name, matchRate, slots, ... }
    outfitWeather: '',
    outfitGeneratedBy: '',
    // 最近查看的搭配(点击进详情页时设置);用于路由跳走 / 刷新后 OutfitDetailView 仍能读到
    currentOutfit: null,

    // 缺口报告
    gapReport: null, // { summary, gaps, total_items, dominant_colors, ... }
  }),

  getters: {
    hasItems: (state) => state.items.length > 0,
    hasOutfit: (state) => !!state.outfit,
    hasGapReport: (state) => !!state.gapReport,
  },

  actions: {
    selectMode(mode) {
      this.mode = mode
    },

    selectScene(scene) {
      this.selectedScene = scene
    },

    reset() {
      this.items = []
      this.outfit = null
      this.gapReport = null
      this.generationError = null
    },

    async startItemsGeneration({ scene, gapFocus = null } = {}) {
      this.isGenerating = true
      this.generationError = null
      this.items = []
      try {
        const data = await generateShoppingItems({ scene, gapFocus })
        this.items = data.items || []
        this.itemsWeather = data.weatherSummary || ''
        this.itemsGeneratedBy = data.generatedBy || 'fallback'
      } catch (err) {
        this.generationError = err.message
        throw err
      } finally {
        this.isGenerating = false
      }
    },

    async startOutfitGeneration({ scene } = {}) {
      this.isGenerating = true
      this.generationError = null
      this.outfit = null
      try {
        const data = await generateShoppingOutfit({ scene })
        this.outfit = data.outfit ? { ...data.outfit, source: 'ai' } : null
        this.outfitWeather = data.weatherSummary || ''
        this.outfitGeneratedBy = data.generatedBy || 'fallback'
      } catch (err) {
        this.generationError = err.message
        throw err
      } finally {
        this.isGenerating = false
      }
    },

    async startGapAnalysis() {
      this.isGenerating = true
      this.generationError = null
      this.gapReport = null
      try {
        const data = await analyzeWardrobeGap()
        this.gapReport = data.report || null
      } catch (err) {
        this.generationError = err.message
        throw err
      } finally {
        this.isGenerating = false
      }
    },

    async markBought(itemId) {
      await updateRecommendationStatus(itemId, 'bought')
      // Optimistic update local state
      const item = this.items.find((i) => i.id === itemId)
      if (item) item.status = 'bought'
    },

    async dismissItem(itemId) {
      await updateRecommendationStatus(itemId, 'dismissed')
      const item = this.items.find((i) => i.id === itemId)
      if (item) item.status = 'dismissed'
    },
  },
})

<template>
  <div class="outfit-match-container">
    <div class="page-header">
      <button class="header-back" @click="goBack">←</button>
      <h1 class="header-title">AI 搭配</h1>
      <div class="header-spacer"></div>
    </div>

    <!-- State A: 输入期 -->
    <div v-if="outfitStore.currentState === 'input'" class="state-input">
      <div class="intro-banner">
        <div class="banner-icon">✨</div>
        <h2 class="banner-title">AI 智能搭配</h2>
        <p class="banner-sub">选择场景与天气，让 AI 为你生成专属穿搭方案</p>
      </div>
      <MatchFilter @generate="handleGenerate" />
    </div>

    <!-- State B: 生成期 -->
    <AIThinking :visible="outfitStore.currentState === 'generating'" />

    <!-- State C: 结果展示期 -->
    <div v-if="outfitStore.currentState === 'results'" class="state-results">
      <div class="results-header">
        <span class="results-count">
          共 {{ outfitStore.outfits.length }} 套搭配
        </span>
        <button class="refresh-btn" @click="handleRegenerate">
          <span>🔄</span>
          <span>再来一次</span>
        </button>
      </div>

      <div class="card-deck">
        <TransitionGroup name="deck">
          <div
            v-for="(outfit, index) in outfitStore.outfits"
            :key="outfit.outfitId"
            class="deck-card-wrapper"
            :style="{ zIndex: outfitStore.outfits.length - index }"
          >
            <OutfitCard
              :outfit="outfit"
              @like="handleLike"
              @skip="handleSkip"
              @detail="handleDetail"
            />
          </div>
        </TransitionGroup>

        <div v-if="outfitStore.outfits.length === 0" class="deck-empty">
          <span class="empty-icon">🎉</span>
          <p class="empty-title">全部浏览完毕</p>
          <p class="empty-hint">点击「再来一次」获取新的搭配灵感</p>
          <button class="regenerate-btn" @click="handleRegenerate">
            <span>✨</span>
            <span>再来一次</span>
          </button>
        </div>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useOutfitStore } from '../stores/outfit'
import { useHaptics } from '../composables/useHaptics'
import MatchFilter from '../components/biz/MatchFilter.vue'
import AIThinking from '../components/biz/AIThinking.vue'
import OutfitCard from '../components/biz/OutfitCard.vue'
import BottomNav from '../components/BottomNav.vue'

const router = useRouter()
const authStore = useAuthStore()
const outfitStore = useOutfitStore()
const { trigger } = useHaptics()

onMounted(() => {
  authStore.checkAuth()
  if (!authStore.isAuthenticated) {
    router.push('/login')
  }
})

const handleGenerate = async (params) => {
  try {
    await outfitStore.startGeneration(params)
  } catch (err) {
    console.error('AI 搭配生成失败:', err)
  }
}

const handleLike = (outfit) => {
  trigger('success')
  outfitStore.likeOutfit(outfit)
}

const handleSkip = (outfit) => {
  trigger('light')
  outfitStore.skipOutfit(outfit)
}

const handleDetail = (outfit) => {
  trigger('medium')
  outfitStore.currentOutfit = outfit
  router.push(`/outfit/${outfit.outfitId}`)
}

const handleRegenerate = () => {
  trigger('medium')
  outfitStore.resetToInput()
}

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.outfit-match-container {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 140px;
  overflow-x: hidden;
  width: 100%;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 50px 20px 16px;
  background: var(--bg-card);
}

@media (min-width: 768px) {
  .page-header {
    position: sticky;
    top: 0;
    z-index: 50;
    padding: 20px 0 20px 30px;
  }
}

.header-back {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-secondary);
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.header-back:active {
  transform: scale(0.9);
  background: var(--border-color);
}

.header-title {
  font-size: 21px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: 0.231px;
}

.header-spacer {
  width: 36px;
}

.intro-banner {
  text-align: center;
  padding: 32px 20px 16px;
}

.banner-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.banner-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  letter-spacing: -0.374px;
}

.banner-sub {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.state-results {
  padding: 16px 20px;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.results-count {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.refresh-btn,
.regenerate-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--surface-pearl);
  border: none;
  border-radius: 11px;
  font-size: 14px;
  color: var(--ink-muted-80);
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:active,
.regenerate-btn:active {
  transform: scale(0.95);
}

.card-deck {
  position: relative;
  min-height: 520px;
}

.deck-card-wrapper {
  position: absolute;
  width: 100%;
  max-width: 380px;
  left: 50%;
  transform: translateX(-50%);
}

.deck-card-wrapper:not(:first-child) {
  transform: translateX(-50%) scale(0.95) translateY(12px);
  opacity: 0.6;
  pointer-events: none;
}

.deck-empty {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 14px;
  color: var(--text-tertiary);
  margin: 0 0 24px 0;
}

.regenerate-btn {
  display: inline-flex;
  padding: 14px 28px;
  background: var(--accent-color);
  color: var(--on-primary);
  font-size: 18px;
  font-weight: 300;
  border-radius: 9999px;
}

.deck-enter-active {
  transition: all 0.4s ease;
}

.deck-leave-active {
  transition: all 0.3s ease;
  position: absolute;
}

.deck-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(50px) scale(0.9);
}

.deck-leave-to {
  opacity: 0;
  transform: translateX(-50%) scale(0.8);
}
</style>

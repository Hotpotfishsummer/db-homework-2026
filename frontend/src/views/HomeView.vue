<template>
  <div class="home-container">
    <div class="home-header">
      <div class="header-left">
        <h1>发现穿搭灵感</h1>
        <p>AI 为你精选推荐</p>
      </div>
      <div class="header-right">
        <div class="quick-action">
          <span class="action-chip" @click="router.push('/add-cloth')">+ 录入衣服</span>
          <span class="action-chip" @click="router.push('/outfit-match')">✨ AI 搭配</span>
        </div>
      </div>
    </div>

    <div class="home-body">
      <!-- User LLM hint (shown when no user LLM is configured) -->
      <HomeViewUserLLMHint />

      <!-- Tab 切换: AI 搭配 vs AI 推荐 -->
      <div class="tabs-wrapper">
        <ModeTabs v-model="activeTab" :tabs="topTabs" />
      </div>

      <!-- AI 搭配 (现有) -->
      <template v-if="activeTab === 'outfit'">
        <SceneSelector
          :scenes="scenes"
          v-model="selectedScene"
          @update:modelValue="onSceneChange"
        />

        <OutfitRecommendSection
          :scene-name="getSceneName"
          :is-loading="isLoading"
          :outfits="outfits"
          :has-generated="outfitHasGenerated"
          @refresh="refreshOutfits"
          @like="like"
          @dislike="dislike"
          @view-detail="viewDetail"
        />
      </template>

      <!-- AI 推荐 (新) -->
      <template v-else>
        <SceneSelector
          :scenes="scenes"
          v-model="selectedScene"
          @update:modelValue="onRecSceneChange"
        />

        <div class="rec-mode-tabs">
          <ModeTabs v-model="recStore.mode" :tabs="recModeTabs" />
        </div>

        <RecommendationSection
          :mode="recStore.mode"
          :scene-name="getSceneName"
          :is-loading="recStore.isGenerating"
          :items="recStore.items"
          :outfit="recStore.outfit"
          :gap-report="recStore.gapReport"
          :generation-error="recStore.generationError"
          :has-generated="recHasGenerated"
          @refresh="onRecRefresh"
          @item-bought="onItemBought"
          @item-dismiss="onItemDismiss"
          @view-detail="viewRecOutfitDetail"
        />
      </template>
    </div>

    <BottomNav />
    <button class="daily-tip-fab" type="button" @click="openDailyTip">
      <span>💡</span>
      <strong>每日贴士</strong>
    </button>
    <DailyTipModal
      :visible="showDailyTip"
      :tip="dailyTip"
      @close="closeDailyTip"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUserStore } from '../stores/user'
import { useWardrobeStore } from '../stores/wardrobe'
import { useRecommendationStore } from '../stores/recommendation'
import { useOutfitStore } from '../stores/outfit'
import { useHaptics } from '../composables/useHaptics'
import { generateOutfit } from '../services/outfit'
import { fetchDailyTip } from '../services/dailyTip'
import BottomNav from '../components/BottomNav.vue'
import SceneSelector from '../components/biz/SceneSelector.vue'
import OutfitRecommendSection from '../components/biz/OutfitRecommendSection.vue'
import ModeTabs from '../components/biz/ModeTabs.vue'
import RecommendationSection from '../components/biz/RecommendationSection.vue'
import HomeViewUserLLMHint from '../components/HomeViewUserLLMHint.vue'
import DailyTipModal from '../components/biz/DailyTipModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const wardrobeStore = useWardrobeStore()
const recStore = useRecommendationStore()
const outfitStore = useOutfitStore()
const { trigger } = useHaptics()

const scenes = [
  { id: 'commute', name: '通勤', icon: '💼' },
  { id: 'date', name: '约会', icon: '💕' },
  { id: 'casual', name: '休闲', icon: '☕' },
  { id: 'sports', name: '运动', icon: '🏃' },
  { id: 'party', name: '派对', icon: '🎉' }
]

const topTabs = [
  { id: 'outfit', label: 'AI 搭配', icon: '👔' },
  { id: 'recommend', label: 'AI 推荐', icon: '🛍️' },
]
const recModeTabs = [
  { id: 'items', label: '单品', icon: '🛍️' },
  { id: 'outfit', label: '搭配', icon: '👔' },
  { id: 'gap', label: '衣橱', icon: '📊' },
]

const activeTab = ref('outfit') // 'outfit' | 'recommend'
const selectedScene = ref('casual')
const outfits = ref([])
const isLoading = ref(false)
const dailyTip = ref(null)
const showDailyTip = ref(false)
const dailyTipLoading = ref(false)

const dailyTipStorageKey = computed(() => {
  const userId = authStore.user?.user_id || authStore.user?.id || 'guest'
  return `l-wardrobe.daily-tip-viewed.${userId}`
})

const getTodayKey = () => new Date().toISOString().slice(0, 10)

const fallbackDailyTip = {
  tip_date: getTodayKey(),
  tip_type: 'color',
  title: '三色原则降低搭配出错率',
  content: '全身主色控制在三种以内，会让视觉更干净。新手可以先固定一个基础色，再用一个低饱和颜色制造层次。',
  example: '白色上衣 + 深蓝下装 + 黑色鞋包',
  tags: ['配色', '基础法则', '通勤'],
  generated_by: 'frontend-fallback',
}

/**
 * AI 搭配区域是否已经被显式触发过。
 * 只有用户主动点击刷新按钮后才会置 true,此后才能刷新;
 * 切换顶层 tab / 场景 / 子 mode 都不再自动调用后端 agent。
 */
const outfitHasGenerated = ref(false)

const getSceneName = computed(() => {
  const scene = scenes.find(s => s.id === selectedScene.value)
  return scene ? scene.name : '推荐'
})

onMounted(async () => {
  authStore.checkAuth()
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  await userStore.loadProfileFromBackend()
  loadDailyTip({ autoOpen: true })
  // 仅加载衣橱数据用于判断可用衣物数量,不再自动生成任何占位搭配
  await wardrobeStore.refreshWardrobe()
})

const loadDailyTip = async ({ autoOpen = false } = {}) => {
  if (dailyTipLoading.value) return
  dailyTipLoading.value = true
  try {
    const tip = await fetchDailyTip()
    dailyTip.value = tip || fallbackDailyTip
    const today = tip?.tip_date || getTodayKey()
    const viewedDate = localStorage.getItem(dailyTipStorageKey.value)
    if (autoOpen && viewedDate !== today) {
      showDailyTip.value = true
    }
  } catch (error) {
    console.warn('每日贴士加载失败:', error.message)
    dailyTip.value = fallbackDailyTip
    if (autoOpen && localStorage.getItem(dailyTipStorageKey.value) !== getTodayKey()) {
      showDailyTip.value = true
    }
  } finally {
    dailyTipLoading.value = false
  }
}

const clearDailyTipButtonFocus = (event) => {
  event?.currentTarget?.blur?.()
  if (document.activeElement instanceof HTMLElement) {
    document.activeElement.blur()
  }
}

const openDailyTip = async (event) => {
  clearDailyTipButtonFocus(event)
  trigger('light')
  if (!dailyTip.value) {
    await loadDailyTip()
  }
  if (dailyTip.value) {
    showDailyTip.value = true
  }
}

const closeDailyTip = () => {
  const today = dailyTip.value?.tip_date || getTodayKey()
  localStorage.setItem(dailyTipStorageKey.value, today)
  showDailyTip.value = false
  clearDailyTipButtonFocus()
}

/**
 * AI 搭配: 切换场景只更新 selectedScene,不会立刻调用 agent。
 * 用户必须点刷新按钮才真正向后端发起请求。
 */
const onSceneChange = (id) => {
  trigger('light')
  selectedScene.value = id
}

/**
 * AI 推荐区域是否已经被显式触发过。
 * 只有用户主动点击刷新按钮后才会置 true,此后才能刷新;
 * 切换顶层 tab / 场景 / 子 mode 都不再自动调用后端 agent。
 */
const recHasGenerated = ref(false)

/**
 * AI 推荐: 切换场景只更新 store 的 selectedScene,不会立刻调用 agent。
 * 用户必须点刷新按钮才真正向后端发起请求。
 */
const onRecSceneChange = (scene) => {
  trigger('light')
  recStore.selectScene(scene)
}

/**
 * 用户显式点击刷新按钮才会走这里。
 * - isLoading / hasGenerated 都重置,展示 loading;
 * - 调后端 agent;失败 → 进入空态让用户重试(不再静默回退 mock 占位)。
 */
const refreshOutfits = async () => {
  if (isLoading.value) return
  trigger('medium')
  isLoading.value = true
  outfits.value = []
  outfitStore.setCurrentOutfit(null)
  outfitHasGenerated.value = true

  try {
    await new Promise(resolve => setTimeout(resolve, 600))
    await loadOutfits()
  } finally {
    isLoading.value = false
  }
}

const getSceneChinese = (scene) => {
  const map = {
    commute: '通勤',
    date: '约会',
    casual: '休闲',
    sports: '运动',
    party: '派对'
  }
  return map[scene] || '休闲'
}

const loadOutfits = async () => {
  if (!wardrobeStore.clothes.length && !wardrobeStore.loading) {
    await wardrobeStore.refreshWardrobe()
  }

  const availableClothes = wardrobeStore.availableClothes
  const availableCount = availableClothes.length

  if (availableCount < 2) {
    // 衣橱不足: 不塞占位卡,留给空态组件渲染
    outfits.value = []
    return
  }

  const wardrobeIds = availableClothes.map(c => c.id)

  try {
    const result = await generateOutfit({
      scene: selectedScene.value,
      wardrobeIds,
      bodyProfile: userStore.getBodyProfilePayload()
    })
    outfits.value = (result.outfits || []).map(item => ({ ...item, clothes: availableClothes }))
    outfitStore.outfits = outfits.value
  } catch (error) {
    console.warn('搭配生成失败,等待用户重试:', error.message)
    outfits.value = []
    outfitStore.outfits = []
  }
}

const like = async (outfit) => {
  trigger('success')
  await userStore.likeOutfit(outfit)
  outfits.value = outfits.value.filter(item => (item.outfitId || item.id) !== (outfit.outfitId || outfit.id))
  outfitStore.outfits = outfits.value
}

const dislike = (index) => {
  trigger('light')
  outfits.value = outfits.value.filter((_, i) => i !== index)
  outfitStore.outfits = outfits.value
}

const viewDetail = (outfit) => {
  trigger('medium')
  outfitStore.setCurrentOutfit(outfit)
  const id = outfit.outfitId || outfit.id
  router.push(`/outfit/${id}`)
}

// ----- AI 推荐 handlers -----
/**
 * 用户显式点击刷新按钮才会走这里。
 * - 若切换了 mode,需要先清空旧数据再生成;
 * - 若切了场景但 mode 没变,store 内的 selectedScene 已经被 onRecSceneChange 更新过,直接生成即可。
 */
async function onRecRefresh() {
  trigger('medium')
  const scene = selectedScene.value
  recStore.selectScene(scene)
  recHasGenerated.value = true
  if (recStore.mode === 'items') {
    await recStore.startItemsGeneration({ scene })
  } else if (recStore.mode === 'outfit') {
    await recStore.startOutfitGeneration({ scene })
  } else {
    await recStore.startGapAnalysis()
  }
}

async function onItemBought(item) {
  if (!item.id) return
  try {
    await recStore.markBought(item.id)
    trigger('success')
  } catch (e) {
    console.warn('mark bought failed', e)
  }
}

async function onItemDismiss(item) {
  if (!item.id) return
  try {
    await recStore.dismissItem(item.id)
    trigger('light')
  } catch (e) {
    console.warn('dismiss failed', e)
  }
}

/**
 * AI 推荐 → 搭配 tab 下的"整套搭配"点击跳详情。
 * 详情页从 recStore.currentOutfit 读数据。
 */
const viewRecOutfitDetail = (outfit) => {
  trigger('medium')
  recStore.currentOutfit = outfit
  // AI 推荐生成的搭配 id 可能是临时名(如 'shopping-outfit-casual'),用 scene+name 合成一个稳定路由 id
  const id = outfit.id || `rec-${recStore.selectedScene}-${(outfit.name || 'outfit').replace(/\s+/g, '-')}`
  router.push(`/outfit/${id}`)
}

watch(() => recStore.mode, () => {
  recStore.reset()
  recHasGenerated.value = false
})

// 切回"AI 推荐"顶层 tab 时不触发,但如果是首次进入且数据为空,也不主动拉取,等用户点刷新。

</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 100px;
  overflow-x: hidden;
  width: 100%;
}

@media (min-width: 768px) {
  .home-container {
    padding-bottom: 32px;
  }

  .home-body {
    display: flex;
    flex-wrap: wrap;
  }
}

.home-header {
  padding: 28px 20px 16px;
  text-align: center;
  background: var(--accent-color);
  border-radius: 0 0 30px 30px;
}

.header-left h1 {
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 4px;
  letter-spacing: 0.5px;
}

.header-left p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 14px;
}

@media (min-width: 768px) {
  .home-header {
    position: sticky;
    top: 0;
    z-index: 50;
    padding: 20px 0 20px 30px;
    border-radius: 0;
  }
}

@media (min-width: 1024px) {
  .home-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 0 20px 30px;
    border-radius: 0;
  }

  .home-header .header-left {
    text-align: left;
  }

  .header-left h1 {
    font-size: 24px;
    margin-bottom: 6px;
  }

  .header-left p {
    font-size: 15px;
    margin-bottom: 0;
  }
}

.tabs-wrapper {
  padding: 16px 20px 0;
}

.rec-mode-tabs {
  padding: 12px 20px 0;
}

.daily-tip-fab {
  position: fixed;
  right: 18px;
  bottom: 92px;
  z-index: 120;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 44px;
  padding: 0 14px;
  border: 1px solid rgba(29, 29, 31, 0.08);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.94);
  color: var(--text-primary, #1d1d1f);
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.12);
  cursor: pointer;
  outline: none;
  user-select: none;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}

.daily-tip-fab:focus,
.daily-tip-fab:focus-visible {
  outline: none;
}

.daily-tip-fab:active {
  transform: scale(0.97);
  background: rgba(248, 248, 250, 0.98);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
}

.daily-tip-fab span {
  font-size: 18px;
}

.daily-tip-fab strong {
  font-size: 14px;
  letter-spacing: 0;
  white-space: nowrap;
}

@media (min-width: 768px) {
  .daily-tip-fab {
    right: 28px;
    bottom: 28px;
/* Quick action buttons in header */
.quick-action {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.action-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.action-chip:active {
  transform: scale(0.96);
}

/* 录入衣服 button - Blue/Purple style */
.action-chip:first-child {
  background: rgba(255, 255, 255, 0.95);
  color: var(--accent-color);
  border: 1.5px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-chip:first-child:hover {
  background: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* AI 搭配 button - Amber/Orange style to distinguish */
.action-chip:last-child {
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  color: #ffffff;
  border: 1.5px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.action-chip:last-child:hover {
  background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}

/* PC layout adjustments */
@media (min-width: 1024px) {
  .header-right {
    margin-right: 40px;
  }

  .quick-action {
    gap: 12px;
  }

  .action-chip {
    padding: 10px 22px;
    font-size: 15px;
  }
}
</style>

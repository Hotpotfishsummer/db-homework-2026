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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUserStore } from '../stores/user'
import { useWardrobeStore } from '../stores/wardrobe'
import { useRecommendationStore } from '../stores/recommendation'
import { useHaptics } from '../composables/useHaptics'
import { generateOutfit } from '../services/outfit'
import BottomNav from '../components/BottomNav.vue'
import SceneSelector from '../components/biz/SceneSelector.vue'
import OutfitRecommendSection from '../components/biz/OutfitRecommendSection.vue'
import ModeTabs from '../components/biz/ModeTabs.vue'
import RecommendationSection from '../components/biz/RecommendationSection.vue'
import HomeViewUserLLMHint from '../components/HomeViewUserLLMHint.vue'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const wardrobeStore = useWardrobeStore()
const recStore = useRecommendationStore()
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
  // 仅加载衣橱数据用于判断可用衣物数量,不再自动生成任何占位搭配
  await wardrobeStore.refreshWardrobe()
})

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
  outfitHasGenerated.value = true

  await new Promise(resolve => setTimeout(resolve, 600))
  await loadOutfits()
  isLoading.value = false
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
    const result = await generateOutfit({ scene: selectedScene.value, wardrobeIds })
    outfits.value = (result.outfits || []).map(item => ({ ...item, clothes: availableClothes }))
  } catch (error) {
    console.warn('搭配生成失败,等待用户重试:', error.message)
    outfits.value = []
  }
}

const like = (outfit) => {
  trigger('success')
  userStore.likeOutfit(outfit)
  // 收藏后清空当前结果,等待用户主动刷新;不静默补 mock
  outfits.value = []
  outfitHasGenerated.value = false
}

const dislike = (index) => {
  trigger('light')
  outfits.value = []
  outfitHasGenerated.value = false
}

const viewDetail = (outfit) => {
  trigger('medium')
  router.push(`/outfit/${outfit.id}`)
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
  padding: 50px 24px 20px;
  text-align: center;
  background: var(--accent-color);
  border-radius: 0 0 30px 30px;
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
}

.tabs-wrapper {
  padding: 16px 20px 0;
}

.rec-mode-tabs {
  padding: 12px 20px 0;
}
</style>

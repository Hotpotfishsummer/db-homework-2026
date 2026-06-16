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
          @refresh="onRecRefresh"
          @item-bought="onItemBought"
          @item-dismiss="onItemDismiss"
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
  await wardrobeStore.refreshWardrobe()
  loadMockOutfits()
})

const onSceneChange = (id) => {
  trigger('light')
  refreshOutfits()
}

const onRecSceneChange = () => {
  trigger('light')
  onRecRefresh()
}

const refreshOutfits = async () => {
  if (isLoading.value) return
  trigger('medium')
  isLoading.value = true
  outfits.value = []

  await new Promise(resolve => setTimeout(resolve, 800))
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
    outfits.value = [{
      id: 999,
      name: '衣橱空空',
      description: '快去录入衣服吧',
      scene: getSceneChinese(selectedScene.value),
      matchRate: 0,
      reason: '至少需要 2 件可用衣服才能生成搭配推荐'
    }]
    return
  }

  const wardrobeIds = availableClothes.map(c => c.id)

  try {
    const result = await generateOutfit({ scene: selectedScene.value, wardrobeIds })
    outfits.value = (result.outfits || []).map(item => ({ ...item, clothes: availableClothes }))
  } catch (error) {
    console.warn('搭配生成失败，使用 Mock 数据:', error.message)
    loadMockOutfits()
  }
}

const loadMockOutfits = () => {
  const availableClothes = wardrobeStore.availableClothes
  const availableCount = availableClothes.length

  const sceneOutfits = {
    commute: { name: '商务精英穿搭', description: '干练得体，尽显专业气质', matchRate: availableCount >= 3 ? 96 : 80, reason: '基于你的职场风格偏好推荐' },
    date: { name: '优雅约会装', description: '温柔大方，让他心动', matchRate: availableCount >= 4 ? 95 : 75, reason: '根据你的甜美风格推荐' },
    casual: { name: '周末休闲风', description: '舒适自在，随性而为', matchRate: availableCount >= 2 ? 97 : 85, reason: '与你衣橱中的基础款完美匹配' },
    sports: { name: '健身运动装', description: '透气舒适，动力满满', matchRate: availableCount >= 2 ? 95 : 78, reason: '根据你的运动频率推荐' },
    party: { name: '派对女王装', description: '闪耀全场，惊艳四方', matchRate: availableCount >= 3 ? 94 : 70, reason: '亮片设计，灯光下更耀眼' }
  }

  const sceneData = sceneOutfits[selectedScene.value]
  outfits.value = [{
    id: Date.now(),
    name: sceneData.name,
    description: sceneData.description,
    scene: getSceneChinese(selectedScene.value),
    matchRate: sceneData.matchRate,
    reason: sceneData.reason,
    clothes: availableClothes
  }]
}

const like = (outfit) => {
  trigger('success')
  userStore.likeOutfit(outfit)
  outfits.value.shift()
  if (outfits.value.length === 0) {
    setTimeout(loadMockOutfits, 500)
  }
}

const dislike = (index) => {
  trigger('light')
  outfits.value.shift()
  if (outfits.value.length === 0) {
    setTimeout(loadMockOutfits, 500)
  }
}

const viewDetail = (outfit) => {
  trigger('medium')
  router.push(`/outfit/${outfit.id}`)
}

// ----- AI 推荐 handlers -----
async function onRecRefresh() {
  trigger('medium')
  const scene = selectedScene.value
  recStore.selectScene(scene)
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

// When the rec mode changes, generate fresh data for the new mode
watch(() => recStore.mode, () => {
  onRecRefresh()
})
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

<template>
  <div class="home-container">
    <div class="home-header">
      <h1>发现穿搭灵感</h1>
      <p>AI 为你精选推荐</p>
    </div>

    <div class="scene-selector">
      <div class="scene-tabs">
        <div
          v-for="scene in scenes"
          :key="scene.id"
          class="scene-tab"
          :class="{ active: selectedScene === scene.id }"
          @click="selectScene(scene.id)"
        >
          <span class="scene-icon">{{ scene.icon }}</span>
          <span>{{ scene.name }}</span>
        </div>
      </div>
    </div>

    <div class="recommend-section">
      <div class="section-title">
        <span class="title-icon">✨</span>
        <span>{{ getSceneName }} 推荐</span>
        <button class="refresh-btn" @click="refreshOutfits" :class="{ spinning: isLoading }">
          🔄
        </button>
      </div>

      <div v-if="isLoading" class="ai-generating">
        <div class="generating-animation">
          <div class="clothes-float" v-for="i in 4" :key="i" :style="{ animationDelay: `${i * 0.2}s` }">
            {{ ['👕', '👖', '👟', '👜'][i - 1] }}
          </div>
        </div>
        <p class="generating-text">AI 正在为你生成穿搭方案...</p>
      </div>

      <div v-else class="outfit-card-container">
        <TransitionGroup name="card">
          <div
            v-for="(outfit, index) in outfits"
            :key="outfit.id"
            class="outfit-card"
            :style="{ zIndex: outfits.length - index }"
            @touchstart="onTouchStart"
            @touchmove="onTouchMove"
            @touchend="onTouchEnd(index, $event)"
          >
            <div class="card-image">
              <img :src="outfit.image" :alt="outfit.name" />
              <div class="card-tags">
                <span class="tag">{{ outfit.scene }}</span>
                <span class="match-badge">{{ outfit.matchRate }}%</span>
              </div>
            </div>
            <div class="card-info">
              <h3>{{ outfit.name }}</h3>
              <p>{{ outfit.description }}</p>
              <div class="ai-reason">
                <span class="ai-icon">🤖</span>
                <span>{{ outfit.reason }}</span>
              </div>
            </div>
            <div class="card-actions">
              <button class="action-detail" @click.stop="viewDetail(outfit)">📋</button>
              <button class="action-dislike" @click="dislike(index)">👎</button>
              <button class="action-like" @click="like(outfit)">❤️</button>
            </div>
          </div>
        </TransitionGroup>

        <div v-if="outfits.length === 0 && !isLoading" class="empty-state">
          <span class="empty-icon">👗</span>
          <p>暂无推荐</p>
          <p class="empty-hint">尝试切换其他场景</p>
        </div>
      </div>

      <div class="swipe-hint" v-if="outfits.length > 0 && !isLoading">
        <span>👈 左滑跳过 · 右滑收藏 👉</span>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUserStore } from '../stores/user'
import { useWardrobeStore } from '../stores/wardrobe'
import { useHaptics } from '../composables/useHaptics'
import { getAIOutfit } from '../services/outfit'
import BottomNav from '../components/BottomNav.vue'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const wardrobeStore = useWardrobeStore()
const { trigger } = useHaptics()

const scenes = [
  { id: 'commute', name: '通勤', icon: '💼' },
  { id: 'date', name: '约会', icon: '💕' },
  { id: 'casual', name: '休闲', icon: '☕' },
  { id: 'sports', name: '运动', icon: '🏃' },
  { id: 'party', name: '派对', icon: '🎉' }
]

const selectedScene = ref('casual')
const outfits = ref([])
const isLoading = ref(false)

const getSceneName = computed(() => {
  const scene = scenes.find(s => s.id === selectedScene.value)
  return scene ? scene.name : '推荐'
})

onMounted(() => {
  authStore.checkAuth()
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  wardrobeStore.initMockData()
  loadMockOutfits()
})

const selectScene = (id) => {
  if (id === selectedScene.value) return
  trigger('light')
  selectedScene.value = id
  refreshOutfits()
}

const refreshOutfits = async () => {
  if (isLoading.value) return
  trigger('medium')
  isLoading.value = true
  outfits.value = []

  // 模拟网络延迟
  await new Promise(resolve => setTimeout(resolve, 800))
  await loadOutfits()
  isLoading.value = false
}

// 加载推荐穿搭（优先调用 API，失败时使用 Mock）
const loadOutfits = async () => {
  const availableClothes = wardrobeStore.availableClothes
  const availableCount = availableClothes.length

  // 可用衣服太少，提示用户
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

  // 获取可用衣服的 ID 列表
  const wardrobeIds = availableClothes.map(c => c.id)

  try {
    // 优先调用后端 AI API
    const data = await getAIOutfit(selectedScene.value, wardrobeIds)
    outfits.value = [{ ...data, clothes: availableClothes }]
  } catch (error) {
    // API 调用失败时使用 Mock 数据
    console.warn('AI API 调用失败，使用 Mock 数据:', error.message)
    loadMockOutfits()
  }
}

// 获取场景中文名
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

// Mock 数据（API 不可用时的后备方案）
const loadMockOutfits = () => {
  const availableClothes = wardrobeStore.availableClothes
  const availableCount = availableClothes.length

  const sceneOutfits = {
    commute: {
      name: '商务精英穿搭',
      description: '干练得体，尽显专业气质',
      matchRate: availableCount >= 3 ? 96 : 80,
      reason: '基于你的职场风格偏好推荐'
    },
    date: {
      name: '优雅约会装',
      description: '温柔大方，让他心动',
      matchRate: availableCount >= 4 ? 95 : 75,
      reason: '根据你的甜美风格推荐'
    },
    casual: {
      name: '周末休闲风',
      description: '舒适自在，随性而为',
      matchRate: availableCount >= 2 ? 97 : 85,
      reason: '与你衣橱中的基础款完美匹配'
    },
    sports: {
      name: '健身运动装',
      description: '透气舒适，动力满满',
      matchRate: availableCount >= 2 ? 95 : 78,
      reason: '根据你的运动频率推荐'
    },
    party: {
      name: '派对女王装',
      description: '闪耀全场，惊艳四方',
      matchRate: availableCount >= 3 ? 94 : 70,
      reason: '亮片设计，灯光下更耀眼'
    }
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

let touchStartX = 0
let touchCurrentX = 0

const onTouchStart = (e) => {
  touchStartX = e.touches[0].clientX
}

const onTouchMove = (e) => {
  touchCurrentX = e.touches[0].clientX
}

const onTouchEnd = (index, e) => {
  const deltaX = touchCurrentX - touchStartX

  if (Math.abs(deltaX) > 100) {
    if (deltaX > 0) {
      like(outfits.value[0])
    } else {
      dislike(index)
    }
  }
  touchStartX = 0
  touchCurrentX = 0
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
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 100px;
}

.home-header {
  padding: 50px 24px 20px;
  text-align: center;
  background: var(--primary-gradient);
  border-radius: 0 0 30px 30px;
}

.home-header h1 {
  font-size: 24px;
  color: white;
  margin-bottom: 4px;
}

.home-header p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.scene-selector {
  padding: 0 24px;
  margin-top: -10px;
}

.scene-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 12px 0;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.scene-tabs::-webkit-scrollbar {
  display: none;
}

.scene-tab {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-card);
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px var(--shadow-color);
}

.scene-tab:active {
  transform: scale(0.95);
}

.scene-tab.active {
  background: var(--primary-gradient);
  color: white;
}

.scene-icon {
  font-size: 14px;
}

.recommend-section {
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.title-icon {
  font-size: 20px;
}

.refresh-btn {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.3s;
}

.refresh-btn.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.ai-generating {
  height: 480px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.generating-animation {
  position: relative;
  width: 200px;
  height: 100px;
}

.clothes-float {
  position: absolute;
  font-size: 32px;
  animation: floatUp 1.5s ease-in-out infinite;
  opacity: 0.8;
}

.clothes-float:nth-child(1) { left: 20%; }
.clothes-float:nth-child(2) { left: 45%; }
.clothes-float:nth-child(3) { left: 65%; }
.clothes-float:nth-child(4) { left: 85%; }

@keyframes floatUp {
  0% {
    transform: translateY(50px) rotate(0deg);
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    transform: translateY(-30px) rotate(10deg);
    opacity: 0;
  }
}

.generating-text {
  margin-top: 20px;
  color: var(--text-tertiary);
  font-size: 14px;
}

.outfit-card-container {
  position: relative;
  height: 520px;
  perspective: 1000px;
}

.outfit-card {
  position: absolute;
  width: 100%;
  max-width: 340px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-card);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 10px 40px var(--shadow-color);
  transition: transform 0.3s, opacity 0.3s;
}

.outfit-card:not(:first-child) {
  transform: translateX(-50%) scale(0.95) translateY(10px);
  opacity: 0.7;
}

.card-image {
  position: relative;
  height: 280px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-tags {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  gap: 8px;
}

.tag {
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
}

.match-badge {
  background: var(--primary-gradient);
  color: white;
  padding: 6px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.card-info {
  padding: 16px;
}

.card-info h3 {
  font-size: 18px;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.card-info p {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.ai-reason {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border-radius: 10px;
  border-left: 3px solid var(--accent-color);
}

.ai-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.ai-reason span:last-child {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.card-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding: 8px 20px 20px;
}

.card-actions button {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-detail {
  background: var(--bg-secondary);
  font-size: 18px;
}

.action-detail:active {
  background: var(--border-color);
  transform: scale(0.95);
}

.action-dislike {
  background: var(--bg-secondary);
}

.action-dislike:active {
  background: var(--border-color);
  transform: scale(0.95);
}

.action-like {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
}

.action-like:active {
  transform: scale(0.95);
}

.swipe-hint {
  text-align: center;
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 16px;
}

.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  padding: 40px;
}

.empty-icon {
  font-size: 60px;
  display: block;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 16px;
  color: var(--text-secondary);
}

.empty-hint {
  font-size: 14px !important;
  color: var(--text-tertiary) !important;
  margin-top: 8px;
}

.card-enter-active {
  transition: all 0.4s ease;
}

.card-leave-active {
  transition: all 0.3s ease;
  position: absolute;
}

.card-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(50px) scale(0.9);
}

.card-leave-to {
  opacity: 0;
  transform: translateX(-50%) scale(0.8);
}
</style>
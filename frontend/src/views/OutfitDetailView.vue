<template>
  <div class="outfit-detail">
    <div class="detail-nav">
      <button class="nav-back" @click="goBack">
        <span>←</span>
      </button>
      <span class="nav-title">穿搭详情</span>
      <button class="nav-share" @click="shareOutfit">
        📤
      </button>
    </div>

    <div class="outfit-hero">
      <img :src="outfit.image" :alt="outfit.name" />
      <div class="hero-overlay">
        <span class="scene-tag">{{ outfit.scene }}</span>
        <span class="match-tag">💫 {{ outfit.matchRate }}% 搭配度</span>
      </div>
    </div>

    <div class="outfit-info">
      <h1>{{ outfit.name }}</h1>
      <p class="description">{{ outfit.description }}</p>

      <div class="ai-reason-card">
        <div class="ai-header">
          <span class="ai-icon">🤖</span>
          <span class="ai-title">AI 分析</span>
        </div>
        <p class="ai-text">{{ outfit.reason }}</p>
      </div>
    </div>

    <div class="outfit-items-section">
      <h2 class="section-title">👗 包含单品</h2>

      <div class="items-list">
        <div
          v-for="(item, index) in outfitItems"
          :key="index"
          class="item-card"
        >
          <div class="item-image">
            <img :src="item.image" :alt="item.name" />
          </div>
          <div class="item-details">
            <h4>{{ item.name }}</h4>
            <p>{{ item.category }}</p>
          </div>
          <button class="item-action" @click="viewInWardrobe(item)">
            📍
          </button>
        </div>
      </div>
    </div>

    <div class="ai-suggestions">
      <h2 class="section-title">✨ AI 搭配建议</h2>

      <div class="suggestion-cards">
        <div class="suggestion-card" v-for="(suggest, idx) in suggestions" :key="idx">
          <div class="suggest-icon">{{ suggest.icon }}</div>
          <div class="suggest-content">
            <h4>{{ suggest.title }}</h4>
            <p>{{ suggest.desc }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="bottom-actions">
      <button class="action-btn secondary" @click="viewWardrobe">
        👗 查看衣橱
      </button>
      <button class="action-btn primary" :class="{ liked: isLiked }" @click="toggleLike">
        {{ isLiked ? '❤️ 已收藏' : '🤍 收藏' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useOutfitStore } from '../stores/outfit'
import { useHaptics } from '../composables/useHaptics'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const outfitStore = useOutfitStore()
const { trigger } = useHaptics()

const outfit = ref({
  id: 1,
  name: '都市通勤穿搭',
  description: '简约干练，适合日常上班通勤',
  scene: '通勤',
  matchRate: 96,
  reason: '这套穿搭采用了经典的蓝白配色，上衣的剪裁利落有型，裤装的版型修饰腿型，整体风格干练专业，非常适合职场穿着。',
  image: 'https://picsum.photos/400/600?random=20'
})

const outfitItems = ref([
  { id: 1, name: '白色衬衫', category: '上装', image: 'https://picsum.photos/100?random=101' },
  { id: 2, name: '深蓝色西装裤', category: '下装', image: 'https://picsum.photos/100?random=102' },
  { id: 3, name: '黑色皮鞋', category: '鞋靴', image: 'https://picsum.photos/100?random=103' },
  { id: 4, name: '皮带', category: '配饰', image: 'https://picsum.photos/100?random=104' }
])

const suggestions = ref([
  { icon: '👠', title: '配饰升级', desc: '可以搭配一条简约的银色项链，增添精致感' },
  { icon: '👜', title: '包包推荐', desc: '搭配一个黑色手提包，容量大且通勤百搭' },
  { icon: '🌈', title: '颜色变体', desc: '尝试米白色衬衫会更显温柔气质' }
])

const isLiked = computed(() => {
  return userStore.likedOutfits.some(o => o.id === outfit.value.id)
})

onMounted(() => {
  const outfitId = route.params.id
  if (outfitId) {
    loadOutfit(outfitId)
  }
  userStore.addToHistory(outfit.value)
})

const loadOutfit = (id) => {
  // 优先使用从搭配页传来的 outfit 数据
  if (outfitStore.currentOutfit && outfitStore.currentOutfit.outfitId === id) {
    const o = outfitStore.currentOutfit
    outfit.value = {
      id: o.outfitId,
      name: `${o.scene}穿搭`,
      description: o.reason,
      scene: o.scene,
      matchRate: o.matchRate,
      reason: o.reason,
      image: o.top?.image || 'https://picsum.photos/400/600?random=20'
    }
    outfitItems.value = [o.top, o.bottom, o.shoes, o.accessory].filter(Boolean).map(item => ({
      ...item,
      category: getCategoryLabel(item.category)
    }))
  } else {
    console.log('加载穿搭:', id)
  }
}

const getCategoryLabel = (cat) => {
  const map = { top: '上装', bottom: '下装', shoes: '鞋靴', accessory: '配饰', bag: '包包' }
  return map[cat] || cat
}

const goBack = () => {
  router.back()
}

const shareOutfit = () => {
  trigger('light')
  if (navigator.share) {
    navigator.share({
      title: outfit.value.name,
      text: outfit.value.description,
      url: window.location.href
    })
  }
}

const toggleLike = () => {
  trigger('success')
  if (isLiked.value) {
    userStore.unlikeOutfit(outfit.value.id)
  } else {
    userStore.likeOutfit(outfit.value)
  }
}

const viewWardrobe = () => {
  trigger('light')
  router.push('/wardrobe')
}

const viewInWardrobe = (item) => {
  trigger('light')
  router.push('/wardrobe')
}
</script>

<style scoped>
.outfit-detail {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 100px;
}

.detail-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: var(--surface-black);
  z-index: 100;
}

.nav-back,
.nav-share {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--chip-translucent);
  border: none;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  color: #ffffff;
}

.nav-back:active,
.nav-share:active {
  transform: scale(0.95);
  background: var(--border-color);
}

.nav-title {
  font-size: 17px;
  font-weight: 600;
  color: #ffffff;
  letter-spacing: -0.374px;
}

.outfit-hero {
  position: relative;
  height: 450px;
  overflow: hidden;
}

.outfit-hero img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  bottom: 20px;
  left: 20px;
  display: flex;
  gap: 10px;
}

.scene-tag {
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border-radius: 20px;
  font-size: 13px;
}

.match-tag {
  padding: 8px 16px;
  background: var(--accent-color);
  color: var(--on-primary);
  border-radius: 9999px;
  font-size: 13px;
  font-weight: 600;
}

.outfit-info {
  padding: 24px;
  background: var(--bg-card);
  border-radius: 18px 18px 0 0;
  margin-top: -24px;
  position: relative;
}

.outfit-info h1 {
  font-size: 28px;
  color: var(--text-primary);
  margin-bottom: 8px;
  font-weight: 600;
  letter-spacing: -0.374px;
}

.description {
  font-size: 17px;
  color: var(--text-secondary);
  line-height: 1.47;
  margin-bottom: 20px;
}

.ai-reason-card {
  background: var(--surface-pearl);
  border-radius: 18px;
  padding: 16px;
}

.ai-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.ai-icon {
  font-size: 18px;
}

.ai-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--accent-color);
}

.ai-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0;
}

.outfit-items-section,
.ai-suggestions {
  padding: 24px;
}

.section-title {
  font-size: 21px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  letter-spacing: 0.231px;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item-card {
  display: flex;
  align-items: center;
  background: var(--bg-card);
  padding: 12px;
  border-radius: 18px;
  border: 1px solid var(--hairline);
}

.item-image {
  width: 56px;
  height: 56px;
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-secondary);
  margin-right: 12px;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-details {
  flex: 1;
}

.item-details h4 {
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.item-details p {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0;
}

.item-action {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-secondary);
  border: none;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.item-action:active {
  transform: scale(0.9);
  background: var(--border-color);
}

.suggestion-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-card {
  display: flex;
  align-items: flex-start;
  background: var(--bg-card);
  padding: 16px;
  border-radius: 18px;
  border: 1px solid var(--hairline);
}

.suggest-icon {
  font-size: 24px;
  margin-right: 12px;
}

.suggest-content h4 {
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.suggest-content p {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.bottom-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 24px;
  padding-bottom: max(16px, env(safe-area-inset-bottom));
  background: rgba(245, 245, 247, 0.8);
  backdrop-filter: blur(20px);
  display: flex;
  gap: 12px;
}

.action-btn {
  flex: 1;
  padding: 11px 22px;
  border-radius: 9999px;
  font-size: 17px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.action-btn:active {
  transform: scale(0.98);
}

.action-btn.secondary {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.action-btn.primary {
  background: var(--accent-color);
  color: var(--on-primary);
}

.action-btn.primary.liked {
  background: #ff4d4f;
}
</style>
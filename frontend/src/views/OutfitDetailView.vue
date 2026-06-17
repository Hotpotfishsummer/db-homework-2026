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
      <img v-if="outfit.image" :src="outfit.image" :alt="outfit.name" />
      <div v-else class="hero-placeholder">👗</div>
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
            <p>{{ item.category }}<span v-if="item.needBuy" class="need-buy-tag"> 需购</span></p>
            <p v-if="item.reason" class="item-reason">{{ item.reason }}</p>
          </div>
          <button class="item-action" @click="viewInWardrobe(item)">
            {{ item.needBuy ? '🛒' : '📍' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="hasNeedBuy" class="ai-suggestions">
      <h2 class="section-title">✨ 需购单品建议</h2>
      <p class="suggestion-hint">以下单品不在你的衣橱中,点击「查看衣橱」可挑选类似的款式补齐:</p>
      <div class="suggestion-cards">
        <div
          v-for="(slot, idx) in needBuySlots"
          :key="idx"
          class="suggestion-card"
        >
          <div class="suggest-icon">🛍️</div>
          <div class="suggest-content">
            <h4>{{ slot.name }}</h4>
            <p>{{ slot.reason || `${slot.category} 类单品,适合当前场景` }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="bottom-actions">
      <button class="action-btn secondary" @click="viewWardrobe">
        👗 查看衣橱
      </button>
      <button class="action-btn primary" :class="{ liked: isLiked }" @click="toggleLike">
        {{ primaryActionLabel }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useOutfitStore } from '../stores/outfit'
import { useRecommendationStore } from '../stores/recommendation'
import { useHaptics } from '../composables/useHaptics'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const outfitStore = useOutfitStore()
const recStore = useRecommendationStore()
const { trigger } = useHaptics()

const outfit = ref({
  id: 1,
  name: '都市通勤穿搭',
  description: '简约干练，适合日常上班通勤',
  scene: '通勤',
  matchRate: 96,
  reason: '这套穿搭采用了经典的蓝白配色，上衣的剪裁利落有型，裤装的版型修饰腿型，整体风格干练专业，非常适合职场穿着。',
  image: ''
})

const outfitItems = ref([])

const suggestions = ref([
  { icon: '👠', title: '配饰升级', desc: '可以搭配一条简约的银色项链，增添精致感' },
  { icon: '👜', title: '包包推荐', desc: '搭配一个黑色手提包，容量大且通勤百搭' },
  { icon: '🌈', title: '颜色变体', desc: '尝试米白色衬衫会更显温柔气质' }
])

const isLiked = computed(() => {
  return userStore.likedOutfits.some(o => o.id === outfit.value.id)
})

const needBuySlots = computed(() => outfitItems.value.filter(i => i.needBuy))
const hasNeedBuy = computed(() => needBuySlots.value.length > 0)

const primaryActionLabel = computed(() => isLiked.value ? '❤️ 已收藏' : '🤍 收藏')

onMounted(() => {
  const outfitId = route.params.id
  if (outfitId) {
    loadOutfit(outfitId)
  }
  userStore.addToHistory(outfit.value)
})

const loadOutfit = (id) => {
  // 1. 优先使用从搭配页(AI 搭配)传来的 outfit 数据
  if (outfitStore.currentOutfit && outfitStore.currentOutfit.outfitId === id) {
    const o = outfitStore.currentOutfit
    outfit.value = {
      id: o.outfitId,
      name: `${o.scene}穿搭`,
      description: o.reason,
      scene: o.scene,
      matchRate: o.matchRate,
      reason: o.reason,
      image: o.image || o.top?.image || pickFirstOwnedImage([o.top, o.bottom, o.shoes, o.accessory])
    }
    outfitItems.value = [o.top, o.bottom, o.shoes, o.accessory].filter(Boolean).map(item => ({
      ...item,
      category: getCategoryLabel(item.category)
    }))
    return
  }

  // 2. 其次使用从 AI 推荐页传来的 currentOutfit (HomeView 合成的 id 形如 rec-<scene>-<name>)
  if (recStore.currentOutfit) {
    const o = recStore.currentOutfit
    const expectedId = o.id || `rec-${recStore.selectedScene}-${(o.name || 'outfit').replace(/\s+/g, '-')}`
    if (expectedId === id || id?.startsWith('rec-')) {
      outfit.value = {
        id,
        name: o.name || 'AI 搭配方案',
        description: o.description || o.reason || 'AI 为你挑选的整体穿搭方案',
        scene: o.scene || recStore.selectedScene || '推荐',
        matchRate: o.matchRate ?? 88,
        reason: o.reason || o.description || '混合你衣橱里已有的衣服与仍需新购的单品',
        image: o.image || pickFirstImage(o)
      }
      outfitItems.value = (o.slots || []).map(slot => ({
        id: slot.id || slot.name,
        name: slot.name,
        category: getCategoryLabel(slot.category),
        image: slot.image,
        reason: slot.reason,
        needBuy: !!slot.need_buy
      }))
      return
    }
  }

  // 3. 兜底: 使用占位数据
  console.log('未找到搭配数据, 使用占位:', id)
}

const pickFirstImage = (o) => {
  if (o?.slots?.length) {
    const slot = o.slots.find(s => !s.need_buy && s.image) || o.slots.find(s => s.image)
    if (slot?.image) return slot.image
  }
  return ''
}

const pickFirstOwnedImage = (items) => {
  const item = (items || []).find(i => i?.image)
  return item?.image || ''
}

const getCategoryLabel = (cat) => {
  const map = { top: '上装', bottom: '下装', shoes: '鞋靴', accessory: '配饰', bag: '包包', outerwear: '外套' }
  return map[cat] || cat || '单品'
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
  overflow-x: hidden;
  width: 100%;
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

.hero-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-black);
  color: rgba(255, 255, 255, 0.72);
  font-size: 72px;
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

.need-buy-tag {
  display: inline-block;
  margin-left: 6px;
  padding: 1px 6px;
  background: linear-gradient(135deg, #ff6f61 0%, #ff9061 100%);
  color: #fff;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.3px;
  vertical-align: middle;
}

.item-reason {
  font-size: 12px;
  color: var(--text-tertiary, #888);
  margin: 4px 0 0;
  line-height: 1.5;
}

.suggestion-hint {
  font-size: 12px;
  color: var(--text-tertiary, #888);
  margin: -8px 0 14px;
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

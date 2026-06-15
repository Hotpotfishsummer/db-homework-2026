<template>
  <div class="recommendation-section">
    <div class="section-title">
      <span class="title-icon">{{ modeIcon }}</span>
      <span>{{ sceneName }} {{ modeLabel }}</span>
      <button class="refresh-btn" @click="onRefresh" :class="{ spinning: isLoading }">
        🔄
      </button>
    </div>

    <div v-if="isLoading" class="ai-generating">
      <div class="generating-animation">
        <div
          class="clothes-float"
          v-for="i in 4"
          :key="i"
          :style="{ animationDelay: `${i * 0.2}s` }"
        >
          {{ modeEmojis[i - 1] }}
        </div>
      </div>
      <p class="generating-text">{{ loadingText }}</p>
    </div>

    <!-- Mode: 单品推荐 -->
    <div v-else-if="mode === 'items'" class="items-grid">
      <div v-if="!items || items.length === 0" class="empty-state">
        <span class="empty-icon">🛍️</span>
        <p>暂无单品推荐</p>
        <p class="empty-hint">点击 🔄 重新生成,或切换其他场景</p>
      </div>
      <ShoppingItemCard
        v-for="item in items"
        :key="item.id || item.name"
        :item="item"
        @bought="$emit('item-bought', item)"
        @dismiss="$emit('item-dismiss', item)"
      />
    </div>

    <!-- Mode: 嵌入搭配 -->
    <div v-else-if="mode === 'outfit' && outfit" class="shopping-outfit">
      <div class="outfit-header">
        <h3>{{ outfit.name }}</h3>
        <span class="match-badge">💫 {{ outfit.matchRate }}%</span>
      </div>
      <p v-if="outfit.description" class="outfit-desc">{{ outfit.description }}</p>
      <div class="slots-grid">
        <div
          v-for="(slot, idx) in outfit.slots"
          :key="idx"
          class="slot-card"
          :class="{ 'need-buy': slot.need_buy }"
        >
          <div class="slot-image">
            <img v-if="!slot.need_buy && slot.image" :src="slot.image" :alt="slot.name" @error="onImgError" />
            <span v-else class="placeholder-emoji">{{ slotEmoji(slot.category) }}</span>
            <span v-if="slot.need_buy" class="buy-badge">🛒 需购</span>
          </div>
          <div class="slot-info">
            <span class="slot-category">{{ slot.category }}</span>
            <h4>{{ slot.name }}</h4>
            <p v-if="slot.reason" class="slot-reason">{{ slot.reason }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="mode === 'outfit' && !outfit" class="empty-state">
      <span class="empty-icon">👔</span>
      <p>暂无搭配方案</p>
      <p class="empty-hint">点击 🔄 重新生成</p>
    </div>

    <!-- Mode: 衣橱缺口 -->
    <div v-else-if="mode === 'gap' && gapReport">
      <WardrobeGapCard :report="gapReport" />
    </div>

    <div v-else-if="mode === 'gap' && !gapReport" class="empty-state">
      <span class="empty-icon">📊</span>
      <p>暂无衣橱报告</p>
      <p class="empty-hint">点击 🔄 生成报告</p>
    </div>

    <div v-if="generationError" class="error-banner">
      ⚠️ {{ generationError }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import ShoppingItemCard from './ShoppingItemCard.vue'
import WardrobeGapCard from './WardrobeGapCard.vue'

const props = defineProps({
  mode: {
    type: String,
    default: 'items', // 'items' | 'outfit' | 'gap'
  },
  sceneName: {
    type: String,
    default: '推荐',
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
  items: {
    type: Array,
    default: () => [],
  },
  outfit: {
    type: Object,
    default: null,
  },
  gapReport: {
    type: Object,
    default: null,
  },
  generationError: {
    type: String,
    default: '',
  },
})

const emit = defineEmits([
  'refresh',
  'item-bought',
  'item-dismiss',
])

const MODE_META = {
  items: { icon: '🛍️', label: '单品', loadingText: 'AI 正在为你挑选值得新购的单品...', emojis: ['👕', '👖', '👟', '👜'] },
  outfit: { icon: '👔', label: '搭配', loadingText: 'AI 正在为你编排混合搭配方案...', emojis: ['👕', '👖', '👟', '🧥'] },
  gap: { icon: '📊', label: '衣橱体检', loadingText: 'AI 正在分析你的衣橱缺口...', emojis: ['📊', '📈', '📋', '✨'] },
}

const modeIcon = computed(() => MODE_META[props.mode]?.icon || '✨')
const modeLabel = computed(() => MODE_META[props.mode]?.label || '推荐')
const loadingText = computed(() => MODE_META[props.mode]?.loadingText || 'AI 生成中...')
const modeEmojis = computed(() => MODE_META[props.mode]?.emojis || ['✨', '🤖', '💡', '⭐'])

function onRefresh() {
  emit('refresh')
}

function onImgError(e) {
  e.target.style.display = 'none'
}

function slotEmoji(cat) {
  const map = {
    top: '👕',
    bottom: '👖',
    outerwear: '🧥',
    shoes: '👟',
    accessory: '🕶️',
    bag: '👜',
    other: '👔',
  }
  return map[cat] || '👔'
}
</script>

<style scoped>
.recommendation-section {
  padding: 20px;
  flex: 1;
}

@media (min-width: 768px) {
  .recommendation-section {
    padding: 24px;
  }
}

@media (min-width: 1280px) {
  .recommendation-section {
    padding: 32px;
  }
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #1a1a1a);
  margin-bottom: 16px;
}

@media (min-width: 768px) {
  .section-title {
    font-size: 22px;
    margin-bottom: 24px;
  }
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
  padding: 4px;
}

.refresh-btn.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.ai-generating {
  height: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
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
  0% { transform: translateY(50px) rotate(0deg); opacity: 0; }
  50% { opacity: 1; }
  100% { transform: translateY(-30px) rotate(10deg); opacity: 0; }
}

.generating-text {
  color: var(--text-secondary, #666);
  font-size: 14px;
}

.items-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

@media (min-width: 768px) {
  .items-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1280px) {
  .items-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary, #666);
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.empty-hint {
  font-size: 12px;
  color: var(--text-tertiary, #999);
  margin-top: 4px;
}

.shopping-outfit {
  background: var(--surface-card, #ffffff);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.outfit-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.outfit-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #1a1a1a);
  flex: 1;
}

.match-badge {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.outfit-desc {
  font-size: 13px;
  color: var(--text-secondary, #666);
  line-height: 1.5;
  margin: 0 0 16px;
}

.slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}

.slot-card {
  background: #fafafa;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 2px solid transparent;
  transition: border 0.2s;
}

.slot-card.need-buy {
  border-style: dashed;
  border-color: #ff9800;
  background: #fff8e1;
}

.slot-image {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  position: relative;
  overflow: hidden;
}

.slot-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-emoji {
  font-size: 48px;
}

.buy-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  background: #ff9800;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 6px;
  font-weight: 600;
}

.slot-info {
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.slot-category {
  font-size: 10px;
  color: var(--text-tertiary, #999);
  text-transform: uppercase;
}

.slot-info h4 {
  margin: 0;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary, #1a1a1a);
  line-height: 1.3;
}

.slot-reason {
  font-size: 11px;
  color: var(--text-secondary, #666);
  margin: 4px 0 0;
  line-height: 1.4;
}

.error-banner {
  margin-top: 12px;
  padding: 10px 14px;
  background: #ffebee;
  color: #c62828;
  border-radius: 8px;
  font-size: 13px;
}
</style>

<template>
  <div class="recommendation-section">
    <div class="section-title">
      <span class="title-icon">{{ modeIcon }}</span>
      <span>{{ sceneName }} {{ modeLabel }}</span>
    </div>

    <!-- 概念提示卡: 解释当前 tab 的含义 -->
    <button
      class="concept-hint"
      :class="{ expanded: showHint }"
      @click="showHint = !showHint"
      :aria-expanded="showHint"
      :aria-label="showHint ? '收起说明' : '展开说明: 单品 / 搭配 / 衣橱 是什么'"
    >
      <span class="hint-icon">💡</span>
      <span class="hint-summary">
        {{ showHint ? '收起说明' : '这三个 tab 分别是?' }}
      </span>
      <span class="hint-toggle">{{ showHint ? '▴' : '▾' }}</span>
    </button>

    <Transition name="hint-fade">
      <div v-if="showHint" class="concept-hint-panel">
        <div class="hint-row">
          <span class="hint-emoji">🛍️</span>
          <div class="hint-text">
            <strong>单品</strong> — AI 从场景出发,推荐<em>可以买</em>的具体衣物(外套、裤子、鞋等),
            告诉你为什么需要它、怎么搭。
          </div>
        </div>
        <div class="hint-row">
          <span class="hint-emoji">👔</span>
          <div class="hint-text">
            <strong>搭配</strong> — 一整套<em>上身方案</em>:
            用你衣橱里已有的 + 还需补的单品组合起来,给出每件衣服的搭配理由。
          </div>
        </div>
        <div class="hint-row">
          <span class="hint-emoji">📊</span>
          <div class="hint-text">
            <strong>衣橱</strong> — 衣橱<em>缺口分析</em>报告:
            统计你现有衣物的类别/颜色/季节覆盖情况,指出哪里重复、哪里不足。
          </div>
        </div>
      </div>
    </Transition>

    <!-- 显眼的主操作按钮: 用户唯一会触发后端 agent 的入口 -->
    <button
      class="primary-refresh"
      :class="{ spinning: isLoading, idle: isIdle }"
      :disabled="isLoading"
      @click="onRefresh"
      :aria-label="idleLabel"
    >
      <span class="primary-refresh-icon">{{ isLoading ? '⏳' : (isIdle ? '✨' : '🔄') }}</span>
      <span class="primary-refresh-text">{{ buttonLabel }}</span>
    </button>

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
        <template v-if="isIdle">
          <span class="empty-icon">✨</span>
          <p>点击上方按钮,让 AI 为你推荐「{{ sceneName }}」场景下的可购入单品</p>
          <p class="empty-hint">只有你主动点击后才会调用 AI,不会在切换 tab 时悄悄消耗额度</p>
        </template>
        <template v-else>
          <span class="empty-icon">🛍️</span>
          <p>暂无单品推荐</p>
          <p class="empty-hint">点击上方「重新生成」或切换其他场景</p>
        </template>
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
    <div
      v-else-if="mode === 'outfit' && outfit"
      class="shopping-outfit clickable"
      role="button"
      tabindex="0"
      @click="$emit('view-detail', outfit)"
      @keydown.enter="$emit('view-detail', outfit)"
    >
      <div class="outfit-header">
        <h3>{{ outfit.name }}</h3>
        <span class="match-badge">💫 {{ outfit.matchRate }}%</span>
      </div>
      <p v-if="outfit.description" class="outfit-desc">{{ outfit.description }}</p>
      <div class="slots-grid" @click.stop>
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
      <div class="outfit-detail-cta">
        <span>点击查看完整搭配详情</span>
        <span class="cta-arrow">›</span>
      </div>
    </div>

    <div v-else-if="mode === 'outfit' && !outfit" class="empty-state">
      <template v-if="isIdle">
        <span class="empty-icon">👔</span>
        <p>点击上方按钮,让 AI 编排一套「{{ sceneName }}」场景下的完整搭配</p>
        <p class="empty-hint">搭配会混合你衣橱里已有的衣服 + 仍需新购的单品</p>
      </template>
      <template v-else>
        <span class="empty-icon">👔</span>
        <p>暂无搭配方案</p>
        <p class="empty-hint">点击上方「重新生成」</p>
      </template>
    </div>

    <!-- Mode: 衣橱缺口 -->
    <div v-else-if="mode === 'gap' && gapReport">
      <WardrobeGapCard :report="gapReport" />
    </div>

    <div v-else-if="mode === 'gap' && !gapReport" class="empty-state">
      <template v-if="isIdle">
        <span class="empty-icon">📊</span>
        <p>点击上方按钮,让 AI 扫描你衣橱里的每件衣服,生成缺口分析报告</p>
        <p class="empty-hint">报告会统计类别 / 颜色 / 季节覆盖情况,指出哪里重复、哪里不足</p>
      </template>
      <template v-else>
        <span class="empty-icon">📊</span>
        <p>暂无衣橱报告</p>
        <p class="empty-hint">点击上方「重新生成」</p>
      </template>
    </div>

    <div v-if="generationError" class="error-banner">
      ⚠️ {{ generationError }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
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
  /**
   * 父级记录"用户是否已经显式点过刷新"。
   * false → 展示引导空态(首屏 / 切 mode 后的初始态),不展示"暂无数据"。
   */
  hasGenerated: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits([
  'refresh',
  'item-bought',
  'item-dismiss',
  'view-detail',
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

// 展开/收起"单品 / 搭配 / 衣橱 是什么"的解释
const showHint = ref(false)
watch(() => props.mode, () => { showHint.value = false })

// 用户尚未显式触发过 → 处于"待启动"状态
const isIdle = computed(() => !props.hasGenerated && !props.isLoading)
const idleLabel = computed(() =>
  isIdle.value
    ? '点击让 AI 为你生成' + modeLabel.value
    : (props.isLoading ? 'AI 生成中…' : '重新生成' + modeLabel.value)
)
const buttonLabel = computed(() => {
  if (props.isLoading) return '生成中…'
  if (isIdle.value) {
    return props.mode === 'gap' ? '分析我的衣橱' : '开始 AI 推荐'
  }
  return '重新生成'
})

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

/* 概念提示卡: 解释"单品 / 搭配 / 衣橱"分别是什么 */
.concept-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 14px;
  margin: -8px 0 16px;
  background: linear-gradient(135deg, #f5f0ff 0%, #ede7f6 100%);
  border: 1px solid rgba(94, 53, 177, 0.12);
  border-radius: 12px;
  color: #5e35b1;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s, transform 0.1s;
}

.concept-hint:hover {
  background: linear-gradient(135deg, #ede7f6 0%, #e1d5f5 100%);
}

.concept-hint:active {
  transform: scale(0.99);
}

.concept-hint .hint-icon {
  font-size: 15px;
}

.concept-hint .hint-summary {
  flex: 1;
}

.concept-hint .hint-toggle {
  font-size: 11px;
  opacity: 0.6;
}

.concept-hint-panel {
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border-color, #eee);
  border-radius: 12px;
  padding: 14px 16px;
  margin: -8px 0 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.concept-hint-panel .hint-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  font-size: 13px;
  line-height: 1.55;
  color: var(--text-secondary, #555);
}

.concept-hint-panel .hint-emoji {
  font-size: 18px;
  line-height: 1.4;
  flex-shrink: 0;
}

.concept-hint-panel .hint-text strong {
  color: var(--text-primary, #1a1a1a);
  font-weight: 600;
  margin-right: 2px;
}

.concept-hint-panel .hint-text em {
  font-style: normal;
  color: #5e35b1;
  font-weight: 500;
}

/* 展开/收起过渡 */
.hint-fade-enter-active,
.hint-fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
  overflow: hidden;
}

.hint-fade-enter-from,
.hint-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
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

/* 主操作按钮: 用户唯一会触发后端 agent 的入口 */
.primary-refresh {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px 20px;
  margin: 0 0 20px;
  border: none;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.3px;
  color: #ffffff;
  cursor: pointer;
  background: linear-gradient(135deg, #5e35b1 0%, #7e57c2 50%, #9575cd 100%);
  box-shadow:
    0 4px 14px rgba(94, 53, 177, 0.35),
    0 1px 2px rgba(94, 53, 177, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.18);
  transition: transform 0.12s ease, box-shadow 0.2s ease, filter 0.2s ease;
  position: relative;
  overflow: hidden;
}

.primary-refresh::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, transparent 30%, rgba(255, 255, 255, 0.25) 50%, transparent 70%);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
  pointer-events: none;
}

.primary-refresh:hover:not(:disabled)::before {
  transform: translateX(100%);
}

.primary-refresh:hover:not(:disabled) {
  box-shadow:
    0 6px 18px rgba(94, 53, 177, 0.45),
    0 2px 4px rgba(94, 53, 177, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.22);
  filter: brightness(1.05);
}

.primary-refresh:active:not(:disabled) {
  transform: translateY(1px) scale(0.99);
  box-shadow:
    0 2px 8px rgba(94, 53, 177, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.primary-refresh:disabled {
  cursor: not-allowed;
  filter: saturate(0.85);
  opacity: 0.9;
}

.primary-refresh.spinning {
  background: linear-gradient(135deg, #9575cd 0%, #b39ddb 100%);
  cursor: wait;
}

.primary-refresh.idle {
  background: linear-gradient(135deg, #ff6f00 0%, #ffa726 50%, #ffb74d 100%);
  box-shadow:
    0 4px 14px rgba(255, 111, 0, 0.35),
    0 1px 2px rgba(255, 111, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.22);
  animation: idle-pulse 2.4s ease-in-out infinite;
}

.primary-refresh.idle:hover:not(:disabled) {
  box-shadow:
    0 6px 18px rgba(255, 111, 0, 0.5),
    0 2px 4px rgba(255, 111, 0, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.25);
}

@keyframes idle-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.015); }
}

.primary-refresh-icon {
  font-size: 18px;
  line-height: 1;
  display: inline-block;
}

.primary-refresh.spinning .primary-refresh-icon {
  animation: spin 1s linear infinite;
}

.primary-refresh-text {
  white-space: nowrap;
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
  transition: transform 0.15s, box-shadow 0.15s;
}

.shopping-outfit.clickable {
  cursor: pointer;
  outline: none;
}

.shopping-outfit.clickable:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(94, 53, 177, 0.18);
}

.shopping-outfit.clickable:focus-visible {
  box-shadow: 0 0 0 3px rgba(94, 53, 177, 0.4), 0 6px 18px rgba(94, 53, 177, 0.18);
}

.outfit-detail-cta {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed var(--border-color, #eee);
  font-size: 13px;
  color: #5e35b1;
  font-weight: 500;
}

.outfit-detail-cta .cta-arrow {
  font-size: 18px;
  line-height: 1;
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

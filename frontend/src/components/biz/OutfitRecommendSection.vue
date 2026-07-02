<template>
  <div class="recommend-section">
    <div class="section-title">
      <span class="title-icon">✨</span>
      <span>{{ sceneName }} 推荐</span>
    </div>

    <!-- 显眼的主操作按钮: 用户唯一会触发后端 agent 的入口 -->
    <button
      class="primary-refresh"
      :class="{ spinning: isLoading, idle: isIdle }"
      :disabled="isLoading"
      @click="$emit('refresh')"
    >
      <span class="primary-refresh-icon">{{ isLoading ? '⏳' : (isIdle ? '✨' : '🔄') }}</span>
      <span class="primary-refresh-text">{{ buttonLabel }}</span>
    </button>

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
          :style="cardStyle(index)"
          @touchstart="onTouchStart(index, $event)"
          @touchmove="onTouchMove($event)"
          @touchend="onTouchEnd(index, $event)"
          @click="onCardClick(outfit)"
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
            <div class="detail-hint">点击查看完整详情 ›</div>
          </div>
          <div class="card-actions" @click.stop>
            <button class="action-detail" @click="emit('viewDetail', outfit)">📋</button>
            <button class="action-dislike" @click="$emit('dislike', index)">👎</button>
            <button class="action-like" @click="$emit('like', outfit)">❤️</button>
          </div>
        </div>
      </TransitionGroup>

      <div v-if="outfits.length === 0 && !isLoading" class="empty-state">
        <template v-if="isIdle">
          <span class="empty-icon">✨</span>
          <p>点击上方按钮,让 AI 为你生成「{{ sceneName }}」场景下的专属搭配</p>
          <p class="empty-hint">只有你主动点击后才会调用 AI,不会在切换 tab 时悄悄消耗额度</p>
        </template>
        <template v-else>
          <span class="empty-icon">{{ wardrobeTooSmall ? '👕' : '😔' }}</span>
          <p v-if="wardrobeTooSmall">衣橱里还没有可搭配的衣物</p>
          <p v-else>暂无搭配方案</p>
          <p v-if="wardrobeTooSmall" class="empty-hint">先到「我的衣橱」录入几件单品,AI 就能为你生成专属方案</p>
          <p v-else class="empty-hint">点击上方「重新生成」再试一次</p>
        </template>
      </div>
    </div>

    <div class="swipe-hint" v-if="outfits.length > 0 && !isLoading">
      <span>👈 左滑跳过 · 右滑收藏 👉</span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  sceneName: {
    type: String,
    default: '推荐'
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  outfits: {
    type: Array,
    default: () => []
  },
  /**
   * 父级记录"用户是否已经显式点过刷新"。
   * false → 展示引导空态(首屏 / 切 mode 后的初始态),不展示"暂无数据"。
   */
  hasGenerated: {
    type: Boolean,
    default: false
  },
  /**
   * 父级告知"用户当前可用衣物太少(< 2 件)"。
   * 用于在空态中给出"先去录入衣物"的具体指引,
   * 避免用户看到"暂无搭配方案"却不知道是衣橱空。
   */
  wardrobeTooSmall: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['refresh', 'like', 'dislike', 'viewDetail'])

// 区分"首屏尚未生成"和"已生成但失败/已消费完"
const isIdle = computed(() => !props.isLoading && !props.hasGenerated && (!props.outfits || props.outfits.length === 0))
const buttonLabel = computed(() => {
  if (props.isLoading) return 'AI 生成中...'
  if (isIdle.value) return '让 AI 帮我搭配'
  return '再来一套'
})

let touchStartX = 0
let touchCurrentX = 0
let touchStartY = 0
const activeTouchIndex = ref(null)
const dragX = ref(0)
const didSwipe = ref(false)

const cardStyle = (index) => {
  if (activeTouchIndex.value !== index || dragX.value === 0) return {}
  return {
    transform: `translateX(calc(-50% + ${dragX.value}px)) rotate(${dragX.value * 0.04}deg)`,
  }
}

const onTouchStart = (index, e) => {
  touchStartX = e.touches[0].clientX
  touchCurrentX = touchStartX
  touchStartY = e.touches[0].clientY
  activeTouchIndex.value = index
  didSwipe.value = false
  dragX.value = 0
}

const onTouchMove = (e) => {
  touchCurrentX = e.touches[0].clientX
  const deltaX = touchCurrentX - touchStartX
  const deltaY = e.touches[0].clientY - touchStartY
  if (Math.abs(deltaX) > Math.abs(deltaY)) {
    dragX.value = deltaX
  }
}

const onTouchEnd = (index, e) => {
  const deltaX = touchCurrentX - touchStartX

  if (Math.abs(deltaX) > 100) {
    didSwipe.value = true
    if (deltaX > 0) {
      emit('like', props.outfits[index])
    } else {
      emit('dislike', index)
    }
  }
  touchStartX = 0
  touchCurrentX = 0
  touchStartY = 0
  activeTouchIndex.value = null
  dragX.value = 0
}

const onCardClick = (outfit) => {
  if (didSwipe.value) {
    didSwipe.value = false
    return
  }
  emit('viewDetail', outfit)
}
</script>

<style scoped>
.recommend-section {
  padding: 20px;
  flex: 1;
}

@media (min-width: 768px) {
  .recommend-section {
    padding: 24px;
  }
}

@media (min-width: 1280px) {
  .recommend-section {
    padding: 32px;
  }
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.374px;
  color: var(--text-primary);
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

/* 显眼的主操作按钮: 用户唯一会触发后端 agent 的入口 */
.primary-refresh {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 16px 20px;
  margin: 4px 0 20px;
  background: linear-gradient(135deg, #5e35b1 0%, #7e57c2 100%);
  color: #fff;
  border: none;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.4px;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(94, 53, 177, 0.28);
  transition: transform 0.1s, box-shadow 0.15s, background 0.2s;
}

.primary-refresh:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(94, 53, 177, 0.35);
}

.primary-refresh:active {
  transform: scale(0.98);
}

.primary-refresh:disabled {
  cursor: not-allowed;
  opacity: 0.85;
}

.primary-refresh.idle {
  background: linear-gradient(135deg, #ff6f61 0%, #ff9061 100%);
  box-shadow: 0 6px 16px rgba(255, 111, 97, 0.32);
  animation: idle-pulse 2.2s ease-in-out infinite;
}

.primary-refresh.idle:hover {
  box-shadow: 0 8px 20px rgba(255, 111, 97, 0.42);
}

@keyframes idle-pulse {
  0%, 100% { box-shadow: 0 6px 16px rgba(255, 111, 97, 0.32); }
  50% { box-shadow: 0 6px 22px rgba(255, 111, 97, 0.55); }
}

.primary-refresh-icon {
  font-size: 18px;
  display: inline-block;
}

.primary-refresh.spinning .primary-refresh-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 详情提示: 整张卡片可点击,提示用户 */
.detail-hint {
  margin-top: 6px;
  font-size: 12px;
  color: #5e35b1;
  font-weight: 500;
}

.outfit-card {
  cursor: pointer;
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
  letter-spacing: -0.224px;
}

.outfit-card-container {
  position: relative;
  height: 520px;
  perspective: 1000px;
  overflow: hidden;
}

/* Desktop: horizontal layout */
@media (min-width: 768px) {
  .outfit-card-container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
    height: auto;
    perspective: none;
    padding: 0;
  }

  .swipe-hint {
    display: none;
  }

  .ai-generating {
    height: 300px;
  }
}

/* Large desktop: 3 columns */
@media (min-width: 1280px) {
  .outfit-card-container {
    grid-template-columns: repeat(3, 1fr);
    gap: 28px;
  }
}

.outfit-card {
  position: absolute;
  width: 100%;
  max-width: 340px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-card);
  border-radius: 18px;
  border: 1px solid var(--hairline);
  overflow: hidden;
  transition: transform 0.3s, opacity 0.3s;
}

@media (min-width: 768px) {
  .outfit-card {
    position: relative;
    left: auto;
    transform: none;
    border-radius: 20px;
  }

  .outfit-card:not(:first-child) {
    transform: none;
    opacity: 1;
  }
}

@media (max-width: 766px) {
  .outfit-card:not(:first-child) {
    transform: translateX(-50%) scale(0.95) translateY(10px);
    opacity: 0.7;
  }
}

.card-image {
  position: relative;
  height: 280px;
  overflow: hidden;
}

@media (min-width: 768px) {
  .card-image {
    height: 300px;
  }
}

@media (min-width: 1280px) {
  .card-image {
    height: 320px;
  }
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
  border-radius: 9999px;
  font-size: 12px;
}

.match-badge {
  background: var(--accent-color);
  color: var(--on-primary);
  padding: 6px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
}

.card-info {
  padding: 16px;
}

@media (min-width: 768px) {
  .card-info {
    padding: 20px;
  }
}

.card-info h3 {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.374px;
  color: var(--text-primary);
  margin-bottom: 4px;
}

@media (min-width: 768px) {
  .card-info h3 {
    font-size: 20px;
  }
}

.card-info p {
  font-size: 14px;
  letter-spacing: -0.224px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

@media (min-width: 768px) {
  .card-info p {
    font-size: 15px;
  }
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
  font-size: 14px;
  letter-spacing: -0.224px;
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

@media (min-width: 768px) {
  .card-actions {
    padding: 12px 24px 24px;
    gap: 28px;
  }

  .card-actions button {
    width: 52px;
    height: 52px;
  }
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

@media (min-width: 768px) {
  .card-actions button:hover {
    transform: scale(1.1);
  }
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
  letter-spacing: -0.224px;
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
  font-size: 17px;
  color: var(--text-secondary);
}

.empty-hint {
  font-size: 14px !important;
  letter-spacing: -0.224px;
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

/* Desktop: disable card stack animations */
@media (min-width: 768px) {
  .card-enter-active,
  .card-leave-active {
    transition: opacity 0.3s ease;
    position: relative;
  }

  .card-enter-from,
  .card-leave-to {
    opacity: 0;
    transform: none;
  }

  .card-enter-active {
    transition: opacity 0.3s ease;
  }

  .card-leave-active {
    transition: opacity 0.2s ease;
  }
}
</style>

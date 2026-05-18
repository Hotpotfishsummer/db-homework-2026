<template>
  <div
    class="outfit-card"
    :class="{ swiping: isSwiping, swipingRight: swipeDirection > 0, swipingLeft: swipeDirection < 0 }"
    :style="swipeStyle"
    @touchstart="onTouchStart"
    @touchmove="onTouchMove"
    @touchend="onTouchEnd"
  >
    <div class="card-header">
      <span class="scene-badge">{{ outfit.scene }}</span>
      <span class="match-badge">{{ outfit.matchRate }}% 匹配</span>
    </div>

    <div class="items-grid">
      <div class="item-cell" v-for="item in displayItems" :key="item.id">
        <div class="item-image">
          <img :src="item.image" :alt="item.name" />
        </div>
        <span class="item-category">{{ item.category }}</span>
        <span class="item-name">{{ item.name }}</span>
      </div>
    </div>

    <div class="ai-reason">
      <div class="reason-header">
        <span class="reason-icon">🤖</span>
        <span class="reason-label">AI 推荐理由</span>
      </div>
      <p class="reason-text">{{ outfit.reason }}</p>
      <p v-if="outfit.weatherNote" class="weather-note">{{ outfit.weatherNote }}</p>
    </div>

    <div class="card-actions">
      <button class="btn-skip" @click="$emit('skip', outfit)">
        <span>👎</span>
        <span>跳过</span>
      </button>
      <button class="btn-detail" @click="$emit('detail', outfit)">
        <span>📋</span>
        <span>详情</span>
      </button>
      <button class="btn-like" @click="$emit('like', outfit)">
        <span>❤️</span>
        <span>喜欢</span>
      </button>
    </div>

    <div class="swipe-indicator left" v-show="swipeDirection < 0">👎</div>
    <div class="swipe-indicator right" v-show="swipeDirection > 0">❤️</div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useHaptics } from '../../composables/useHaptics'

const props = defineProps({
  outfit: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['like', 'skip', 'detail'])

const { trigger } = useHaptics()

const displayItems = computed(() => {
  const items = []
  const { top, bottom, shoes, accessory } = props.outfit
  if (top) items.push(top)
  if (bottom) items.push(bottom)
  if (shoes) items.push(shoes)
  if (accessory) items.push(accessory)
  return items
})

const isSwiping = ref(false)
const swipeDirection = ref(0)
const swipeDelta = ref(0)

const swipeStyle = computed(() => {
  if (!isSwiping.value) return {}
  return {
    transform: `translateX(${swipeDelta.value}px) rotate(${swipeDelta.value * 0.05}deg)`,
    transition: 'none'
  }
})

let touchStartX = 0

const onTouchStart = (e) => {
  touchStartX = e.touches[0].clientX
  isSwiping.value = true
}

const onTouchMove = (e) => {
  if (!isSwiping.value) return
  const delta = e.touches[0].clientX - touchStartX
  swipeDelta.value = delta
  swipeDirection.value = delta > 0 ? 1 : -1
}

const onTouchEnd = () => {
  const threshold = 100

  if (Math.abs(swipeDelta.value) > threshold) {
    if (swipeDelta.value > 0) {
      trigger('success')
      emit('like', props.outfit)
    } else {
      trigger('light')
      emit('skip', props.outfit)
    }
  }

  resetSwipe()
}

const resetSwipe = () => {
  isSwiping.value = false
  swipeDirection.value = 0
  swipeDelta.value = 0
}
</script>

<style scoped>
.outfit-card {
  background: var(--bg-card);
  border-radius: 24px;
  padding: 16px;
  box-shadow: 0 12px 40px var(--shadow-color);
  transition: transform 0.4s ease, opacity 0.4s ease;
  position: relative;
  overflow: hidden;
  touch-action: pan-y;
  user-select: none;
}

.outfit-card.swiping {
  transition: none;
}

.swipe-indicator {
  position: absolute;
  top: 20px;
  font-size: 48px;
  z-index: 10;
  pointer-events: none;
  transition: opacity 0.15s;
}

.swipe-indicator.left {
  left: 20px;
}

.swipe-indicator.right {
  right: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.scene-badge {
  padding: 6px 14px;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.dark .scene-badge {
  background: rgba(255, 255, 255, 0.08);
}

.match-badge {
  padding: 6px 12px;
  background: var(--primary-gradient);
  color: white;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.item-cell {
  background: var(--bg-secondary);
  border-radius: 14px;
  padding: 10px;
  text-align: center;
}

.item-image {
  width: 100%;
  height: 64px;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 6px;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-category {
  display: block;
  font-size: 11px;
  color: var(--text-tertiary);
  margin-bottom: 2px;
}

.item-name {
  display: block;
  font-size: 12px;
  color: var(--text-primary);
  font-weight: 500;
}

.ai-reason {
  background: var(--bg-secondary);
  border-radius: 14px;
  padding: 10px 14px;
  border-left: 4px solid var(--accent-color);
  margin-bottom: 12px;
}

.reason-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.reason-icon {
  font-size: 16px;
}

.reason-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-color);
}

.reason-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 6px 0;
}

.weather-note {
  font-size: 12px;
  color: var(--accent-color);
  margin: 4px 0 0 0;
}

.card-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.card-actions button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  border-radius: 14px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.card-actions button:active {
  transform: scale(0.95);
}

.btn-skip {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.btn-detail {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-like {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
  color: white;
}

.btn-like:active {
  background: linear-gradient(135deg, #ee5a5a 0%, #dd4a4a 100%);
}
</style>

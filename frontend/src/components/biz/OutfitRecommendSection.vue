<template>
  <div class="recommend-section">
    <div class="section-title">
      <span class="title-icon">✨</span>
      <span>{{ sceneName }} 推荐</span>
      <button class="refresh-btn" @click="$emit('refresh')" :class="{ spinning: isLoading }">
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
            <button class="action-detail" @click.stop="$emit('viewDetail', outfit)">📋</button>
            <button class="action-dislike" @click="$emit('dislike', index)">👎</button>
            <button class="action-like" @click="$emit('like', outfit)">❤️</button>
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
</template>

<script setup>
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
  }
})

const emit = defineEmits(['refresh', 'like', 'dislike', 'viewDetail'])

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
      emit('like', props.outfits[0])
    } else {
      emit('dislike', index)
    }
  }
  touchStartX = 0
  touchCurrentX = 0
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

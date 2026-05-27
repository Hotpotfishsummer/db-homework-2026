<template>
  <Transition name="overlay">
    <div v-if="visible" class="ai-thinking-overlay">
      <div class="thinking-content">
        <div class="pulse-ring">
          <div class="ring ring-1"></div>
          <div class="ring ring-2"></div>
          <div class="ring ring-3"></div>
          <div class="center-icon">🤖</div>
        </div>

        <div class="floating-icons">
          <span
            v-for="(item, i) in floatingItems"
            :key="i"
            class="float-item"
            :style="{
              left: item.x + '%',
              animationDelay: item.delay + 's',
              animationDuration: item.duration + 's'
            }"
          >{{ item.emoji }}</span>
        </div>

        <div class="text-stage">
          <Transition name="text-swap" mode="out-in">
            <p :key="currentTextIndex" class="stage-text">{{ texts[currentTextIndex] }}</p>
          </Transition>
        </div>

        <div class="progress-dots">
          <span
            v-for="(_, i) in texts"
            :key="i"
            class="dot"
            :class="{ active: i <= currentTextIndex, done: i < currentTextIndex }"
          ></span>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  visible: Boolean
})

const texts = [
  '正在分析您的衣橱...',
  '正在匹配当季流行趋势...',
  '正在计算最佳搭配方案...',
  '为您生成专属造型...'
]

const floatingItems = [
  { emoji: '👕', x: 15, delay: 0, duration: 2.8 },
  { emoji: '👖', x: 35, delay: 0.7, duration: 3.2 },
  { emoji: '👗', x: 55, delay: 1.4, duration: 2.6 },
  { emoji: '👟', x: 75, delay: 2.1, duration: 3.0 }
]

const currentTextIndex = ref(0)
let textTimer = null

const startTextCycle = () => {
  currentTextIndex.value = 0
  textTimer = setInterval(() => {
    if (currentTextIndex.value < texts.length - 1) {
      currentTextIndex.value++
    }
  }, 700)
}

const stopTextCycle = () => {
  if (textTimer) {
    clearInterval(textTimer)
    textTimer = null
  }
}

watch(() => props.visible, (val) => {
  if (val) {
    startTextCycle()
  } else {
    stopTextCycle()
  }
})

onUnmounted(() => {
  stopTextCycle()
})
</script>

<style scoped>
.ai-thinking-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 14, 30, 0.92);
  backdrop-filter: blur(16px);
  z-index: 300;
  display: flex;
  align-items: center;
  justify-content: center;
}

.thinking-content {
  text-align: center;
  padding: 40px;
}

.pulse-ring {
  position: relative;
  width: 140px;
  height: 140px;
  margin: 0 auto 48px;
}

.ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid rgba(0, 102, 204, 0.4);
  animation: pulseRing 2s ease-out infinite;
}

.ring-2 {
  animation-delay: 0.6s;
}

.ring-3 {
  animation-delay: 1.2s;
}

.center-icon {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  animation: iconPulse 2s ease-in-out infinite;
}

@keyframes pulseRing {
  0% {
    transform: scale(0.6);
    opacity: 1;
  }
  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}

@keyframes iconPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.15);
  }
}

.floating-icons {
  position: relative;
  height: 40px;
  margin-bottom: 32px;
}

.float-item {
  position: absolute;
  font-size: 24px;
  animation: floatUp 3s ease-in-out infinite;
  opacity: 0;
}

@keyframes floatUp {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 0;
  }
  20% {
    opacity: 0.9;
  }
  80% {
    opacity: 0.9;
  }
  100% {
    transform: translateY(-180px) rotate(15deg);
    opacity: 0;
  }
}

.text-stage {
  min-height: 30px;
  margin-bottom: 20px;
}

.stage-text {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
  letter-spacing: 1px;
}

.text-swap-enter-active,
.text-swap-leave-active {
  transition: all 0.35s ease;
}

.text-swap-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.text-swap-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

.progress-dots {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  transition: all 0.35s;
}

.dot.active {
  background: var(--accent-color);
  box-shadow: 0 0 8px rgba(0, 102, 204, 0.6);
  transform: scale(1.3);
}

.dot.done {
  background: rgba(0, 102, 204, 0.4);
}

.overlay-enter-active,
.overlay-leave-active {
  transition: all 0.4s ease;
}

.overlay-enter-from,
.overlay-leave-to {
  opacity: 0;
}
</style>

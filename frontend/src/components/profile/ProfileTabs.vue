<template>
  <div class="tabs-wrapper" ref="tabsRef" :class="{ sticky: isSticky }">
    <div class="tabs">
      <div
        class="tab"
        :class="{ active: modelValue === 'liked' }"
        @click="$emit('update:modelValue', 'liked')"
      >
        <span class="tab-icon">❤️</span>
        <span class="tab-text">收藏</span>
        <span class="tab-count" v-if="likedCount">{{ likedCount }}</span>
      </div>
      <div
        class="tab"
        :class="{ active: modelValue === 'history' }"
        @click="$emit('update:modelValue', 'history')"
      >
        <span class="tab-icon">🕐</span>
        <span class="tab-text">浏览</span>
        <span class="tab-count" v-if="historyCount">{{ historyCount }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  modelValue: { type: String, default: 'liked' },
  likedCount: { type: Number, default: 0 },
  historyCount: { type: Number, default: 0 },
  isSticky: { type: Boolean, default: false }
})

defineEmits(['update:modelValue'])

const tabsRef = ref(null)

defineExpose({ tabsRef })
</script>

<style scoped>
.tabs-wrapper {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--bg-secondary);
  padding: 20px 24px 0;
  transition: border-bottom 0.3s;
}

.tabs-wrapper.sticky {
  border-bottom: 1px solid var(--hairline);
  padding-bottom: 4px;
}

.tabs {
  display: flex;
  background: var(--bg-card);
  border-radius: 12px;
  padding: 4px;
  position: relative;
}

.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s;
  position: relative;
  z-index: 2;
}

.tab.active {
  background: var(--accent-color);
}

.tab-icon { font-size: 14px; }

.tab-text {
  font-size: 14px;
  font-weight: 400;
  color: var(--text-secondary);
}

.tab.active .tab-text { color: var(--on-primary); }

.tab-count {
  font-size: 10px;
  background: rgba(0,0,0,0.1);
  color: var(--text-tertiary);
  padding: 1px 6px;
  border-radius: 8px;
  min-width: 18px;
  text-align: center;
}

.tab.active .tab-count {
  background: rgba(255,255,255,0.3);
  color: var(--on-primary);
}
</style>

<template>
  <div class="bottom-nav">
    <div class="nav-item" @click="navigate('home')">
      <span class="nav-icon">🏠</span>
      <span class="nav-label">首页</span>
    </div>

    <div class="center-action" @click="openSheet">
      <div class="action-btn">
        <span class="action-icon">✨</span>
      </div>
    </div>

    <div class="nav-item" @click="navigate('wardrobe')">
      <span class="nav-icon">👗</span>
      <span class="nav-label">衣橱</span>
    </div>

    <div class="nav-item" @click="navigate('profile')">
      <span class="nav-icon">👤</span>
      <span class="nav-label">我的</span>
    </div>

    <BottomSheet v-model:show="showSheet" @action="handleSheetAction" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useHaptics } from '../composables/useHaptics'
import BottomSheet from './BottomSheet.vue'

const router = useRouter()
const { trigger } = useHaptics()
const showSheet = ref(false)

const navigate = (name) => {
  trigger('light')
  router.push({ name })
}

const openSheet = () => {
  trigger('medium')
  showSheet.value = true
}

const handleSheetAction = (type) => {
  if (type === 'add-cloth') {
    router.push('/add-cloth')
  } else if (type === 'ai-match') {
    router.push('/outfit-match')
  }
}
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: var(--bg-card);
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  padding-bottom: env(safe-area-inset-bottom, 10px);
  box-shadow: 0 -4px 20px var(--shadow-color);
  z-index: 100;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.nav-label {
  font-size: 11px;
  color: var(--text-tertiary);
  font-weight: 500;
}

.nav-item:active {
  transform: scale(0.95);
}

.center-action {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  padding-bottom: 8px;
}

.action-btn {
  width: 56px;
  height: 56px;
  background: var(--primary-gradient);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  transform: translateY(-20px);
  transition: all 0.3s;
}

.action-btn:active {
  transform: translateY(-16px) scale(0.95);
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.action-icon {
  font-size: 28px;
}
</style>
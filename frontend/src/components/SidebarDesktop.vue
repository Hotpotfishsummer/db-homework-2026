<template>
  <aside class="sidebar-desktop">
    <div class="sidebar-header">
      <span class="logo-icon">✨</span>
    </div>

    <nav class="sidebar-nav">
      <div
        class="nav-item"
        :class="{ active: currentRoute === 'home' }"
        @click="navigate('home')"
      >
        <span class="nav-icon">🏠</span>
        <span class="nav-label">首页</span>
      </div>

      <div
        class="nav-item"
        :class="{ active: currentRoute === 'wardrobe' }"
        @click="navigate('wardrobe')"
      >
        <span class="nav-icon">👗</span>
        <span class="nav-label">衣橱</span>
      </div>

      <div
        class="nav-item"
        :class="{ active: currentRoute === 'profile' }"
        @click="navigate('profile')"
      >
        <span class="nav-icon">👤</span>
        <span class="nav-label">我的</span>
      </div>
    </nav>

    <div class="sidebar-footer">
      <div class="action-btn" @click="openSheet">
        <span class="action-icon">✨</span>
      </div>
    </div>

    <BottomSheet v-model:show="showSheet" @action="handleSheetAction" />
  </aside>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useHaptics } from '../composables/useHaptics'
import BottomSheet from './BottomSheet.vue'

const router = useRouter()
const route = useRoute()
const { trigger } = useHaptics()
const showSheet = ref(false)

const currentRoute = computed(() => route.name)

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
.sidebar-desktop {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: var(--sidebar-width);
  background: var(--bg-card);
  border-right: 1px solid var(--border-color);
  display: none;
  flex-direction: column;
  align-items: center;
  padding: 16px 0;
  z-index: 100;
}

/* Show from tablet (768px) and up */
@media (min-width: 768px) {
  .sidebar-desktop {
    display: flex;
  }
}

.sidebar-header {
  padding: 8px;
  margin-bottom: 24px;
}

.logo-icon {
  font-size: 32px;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  padding: 0 8px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-item:active {
  transform: scale(0.95);
}

.nav-item.active {
  background: var(--accent-color);
}

.nav-item.active .nav-label {
  color: var(--on-primary);
}

.nav-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.nav-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 400;
}

.sidebar-footer {
  padding: 8px;
  margin-top: auto;
}

.action-btn {
  width: 48px;
  height: 48px;
  background: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-btn:active {
  transform: scale(0.95);
}

.action-icon {
  font-size: 24px;
}

/* Desktop */
@media (min-width: 1024px) {
  .sidebar-desktop {
    width: var(--sidebar-width);
  }
}
</style>
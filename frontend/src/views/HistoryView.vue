<template>
  <div class="history-container">
    <div class="page-nav">
      <button class="nav-back" @click="goBack">←</button>
      <h1>浏览历史</h1>
      <button class="clear-btn" @click="clearHistory" v-if="userStore.historyOutfits.length > 0">
        清空
      </button>
    </div>

    <div class="history-list" v-if="userStore.historyOutfits.length > 0">
      <div
        v-for="(outfit, index) in userStore.historyOutfits"
        :key="`${outfit.id}-${index}`"
        class="history-item"
        @click="viewDetail(outfit)"
      >
        <div class="item-image">
          <img :src="outfit.image" :alt="outfit.name" loading="lazy" />
        </div>
        <div class="item-info">
          <h3>{{ outfit.name }}</h3>
          <p class="view-time">{{ formatTime(outfit.viewedAt) }}</p>
        </div>
        <span class="arrow">›</span>
      </div>
    </div>

    <div v-else class="empty-state">
      <span class="empty-icon">🕐</span>
      <p>还没有浏览记录</p>
      <p class="empty-hint">去首页看看吧</p>
      <button class="go-discover" @click="goHome">去发现</button>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUserStore } from '../stores/user'
import { useHaptics } from '../composables/useHaptics'
import BottomNav from '../components/BottomNav.vue'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const { trigger } = useHaptics()

onMounted(() => {
  authStore.checkAuth()
  if (!authStore.isAuthenticated) {
    router.push('/login')
  }
})

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/home')
}

const viewDetail = (outfit) => {
  trigger('light')
  router.push(`/outfit/${outfit.id}`)
}

const formatTime = (dateStr) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`

  return `${date.getMonth() + 1}/${date.getDate()}`
}

const clearHistory = () => {
  trigger('medium')
  userStore.historyOutfits = []
}
</script>

<style scoped>
.history-container {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 100px;
}

.page-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 50px 24px 20px;
  background: var(--bg-card);
}

.nav-back {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-secondary);
  border: none;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
}

.page-nav h1 {
  font-size: 18px;
  color: var(--text-primary);
}

.clear-btn {
  padding: 6px 12px;
  background: var(--bg-secondary);
  border: none;
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-tertiary);
  cursor: pointer;
}

.history-list {
  padding: 20px 24px;
}

.history-item {
  display: flex;
  align-items: center;
  background: var(--bg-card);
  padding: 12px;
  border-radius: 18px;
  margin-bottom: 10px;
  border: 1px solid var(--hairline);
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:active {
  background: var(--bg-secondary);
}

.item-image {
  width: 56px;
  height: 56px;
  border-radius: 10px;
  overflow: hidden;
  margin-right: 12px;
  flex-shrink: 0;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-info h3 {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.374px;
  color: var(--text-primary);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.view-time {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0;
}

.arrow {
  font-size: 20px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: 80px 40px;
}

.empty-icon {
  font-size: 60px;
  display: block;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 16px;
  color: var(--text-secondary);
}

.empty-hint {
  font-size: 14px !important;
  color: var(--text-tertiary) !important;
  margin-top: 8px;
  margin-bottom: 24px;
}

.go-discover {
  padding: 11px 22px;
  background: var(--accent-color);
  color: var(--on-primary);
  border: none;
  border-radius: 9999px;
  font-size: 17px;
  font-weight: 400;
  cursor: pointer;
  transition: transform 0.2s;
}

.go-discover:active {
  transform: scale(0.95);
}
</style>
<template>
  <div class="liked-container">
    <div class="page-nav">
      <button class="nav-back" @click="goBack">←</button>
      <h1>我的收藏</h1>
      <span class="count">{{ userStore.likedOutfits.length }}</span>
    </div>

    <div class="liked-list" v-if="userStore.likedOutfits.length > 0">
      <div
        v-for="outfit in userStore.likedOutfits"
        :key="outfit.id"
        class="liked-item"
        @click="viewDetail(outfit)"
      >
        <div class="item-image">
          <img :src="outfit.image" :alt="outfit.name" loading="lazy" />
          <span class="scene-tag">{{ outfit.scene }}</span>
        </div>
        <div class="item-info">
          <h3>{{ outfit.name }}</h3>
          <p>{{ outfit.description }}</p>
          <span class="match-rate">💫 {{ outfit.matchRate }}% 搭配度</span>
        </div>
        <button class="unlike-btn" @click.stop="unlike(outfit.id)">
          ❤️
        </button>
      </div>
    </div>

    <div v-else class="empty-state">
      <span class="empty-icon">💝</span>
      <p>还没有收藏</p>
      <p class="empty-hint">去首页发现喜欢的穿搭吧</p>
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

const unlike = (id) => {
  trigger('light')
  userStore.unlikeOutfit(id)
}
</script>

<style scoped>
.liked-container {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 100px;
  overflow-x: hidden;
  width: 100%;
}

.page-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 50px 24px 20px;
  background: var(--bg-card);
}

@media (min-width: 768px) {
  .page-nav {
    position: sticky;
    top: 0;
    z-index: 50;
    padding: 20px 0 20px 30px;
  }
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

.count {
  font-size: 14px;
  color: var(--text-tertiary);
  min-width: 40px;
  text-align: right;
}

.liked-list {
  padding: 20px 24px;
}

.liked-item {
  display: flex;
  align-items: center;
  background: var(--bg-card);
  padding: 12px;
  border-radius: 18px;
  margin-bottom: 12px;
  border: 1px solid var(--hairline);
  cursor: pointer;
  transition: all 0.2s;
}

.liked-item:active {
  transform: scale(0.98);
}

.item-image {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 12px;
  overflow: hidden;
  margin-right: 12px;
  flex-shrink: 0;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.scene-tag {
  position: absolute;
  bottom: 4px;
  left: 4px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 9px;
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

.item-info p {
  font-size: 14px;
  font-weight: 400;
  letter-spacing: -0.224px;
  color: var(--text-secondary);
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.match-rate {
  font-size: 12px;
  color: var(--accent-color);
}

.unlike-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-secondary);
  border: none;
  font-size: 16px;
  cursor: pointer;
  flex-shrink: 0;
  margin-left: 8px;
  transition: all 0.2s;
}

.unlike-btn:active {
  transform: scale(0.9);
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
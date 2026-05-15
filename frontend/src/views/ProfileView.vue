<template>
  <div class="profile-container">
    <div class="profile-header">
      <div class="avatar-section">
        <div class="avatar">
          {{ authStore.user?.username?.charAt(0)?.toUpperCase() || 'U' }}
        </div>
        <div class="user-info">
          <h2>{{ authStore.user?.username || '用户' }}</h2>
          <p>AI 穿搭会员</p>
        </div>
      </div>
      <button class="btn-edit" @click="editMode = !editMode">
        {{ editMode ? '完成' : '编辑' }}
      </button>
    </div>

    <div class="stats-section">
      <div class="stat-item">
        <span class="stat-value">{{ userStore.likedOutfits.length }}</span>
        <span class="stat-label">收藏</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ wardrobeStore.clothes.length }}</span>
        <span class="stat-label">衣橱</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ userStore.historyOutfits.length }}</span>
        <span class="stat-label">浏览</span>
      </div>
    </div>

    <div class="style-profile-section">
      <h3>🎨 时尚档案</h3>

      <div class="profile-card">
        <div class="profile-item">
          <label>肤色</label>
          <div class="color-options">
            <div
              v-for="tone in skinTones"
              :key="tone.id"
              class="color-chip"
              :class="{ active: userStore.profile.skinTone === tone.id }"
              :style="{ background: tone.color }"
              @click="selectSkinTone(tone.id)"
            >
              <span v-if="userStore.profile.skinTone === tone.id">✓</span>
            </div>
          </div>
        </div>

        <div class="profile-item">
          <label>身型</label>
          <div class="body-options">
            <div
              v-for="body in bodyTypes"
              :key="body.id"
              class="body-option"
              :class="{ active: userStore.profile.bodyType === body.id }"
              @click="selectBodyType(body.id)"
            >
              <span class="body-icon">{{ body.icon }}</span>
              <span>{{ body.name }}</span>
            </div>
          </div>
        </div>

        <div class="profile-item">
          <label>风格偏好</label>
          <div class="style-tags">
            <div
              v-for="style in styleOptions"
              :key="style"
              class="style-tag"
              :class="{ active: userStore.profile.styles.includes(style) }"
              @click="toggleStyle(style)"
            >
              {{ style }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="menu-section">
      <div class="menu-item" @click="goToLiked">
        <span class="menu-icon">❤️</span>
        <span class="menu-text">我的收藏</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="goToHistory">
        <span class="menu-icon">🕐</span>
        <span class="menu-text">浏览历史</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="toggleTheme">
        <span class="menu-icon">{{ themeStore.isDark ? '☀️' : '🌙' }}</span>
        <span class="menu-text">{{ themeStore.isDark ? '浅色模式' : '深色模式' }}</span>
        <span class="menu-arrow">›</span>
      </div>
    </div>

    <button class="btn-logout" @click="handleLogout">
      退出登录
    </button>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUserStore } from '../stores/user'
import { useWardrobeStore } from '../stores/wardrobe'
import { useThemeStore } from '../stores/theme'
import { useHaptics } from '../composables/useHaptics'
import BottomNav from '../components/BottomNav.vue'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const wardrobeStore = useWardrobeStore()
const themeStore = useThemeStore()
const { trigger } = useHaptics()

const editMode = ref(false)

const skinTones = [
  { id: 'fair', color: '#ffe4c4' },
  { id: 'light', color: '#f5deb3' },
  { id: 'medium', color: '#deb887' },
  { id: 'tan', color: '#d2a679' },
  { id: 'dark', color: '#8b5a2b' }
]

const bodyTypes = [
  { id: 'apple', name: '苹果型', icon: '🍎' },
  { id: 'pear', name: '梨型', icon: '🍐' },
  { id: 'hourglass', name: '沙漏型', icon: '⏳' },
  { id: 'rectangle', name: '矩形', icon: '📏' }
]

const styleOptions = ['极简', '复古', '废土风', '高智感', '运动', '甜美', '酷帅', '文艺']

onMounted(() => {
  authStore.checkAuth()
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  wardrobeStore.initMockData()
})

const selectSkinTone = (id) => {
  trigger('light')
  userStore.updateProfile({ skinTone: id })
}

const selectBodyType = (id) => {
  trigger('light')
  userStore.updateProfile({ bodyType: id })
}

const toggleStyle = (style) => {
  trigger('light')
  const styles = [...userStore.profile.styles]
  const index = styles.indexOf(style)
  if (index > -1) {
    styles.splice(index, 1)
  } else {
    styles.push(style)
  }
  userStore.updateProfile({ styles })
}

const goToLiked = () => {
  trigger('light')
  router.push('/liked')
}

const goToHistory = () => {
  trigger('light')
  router.push('/history')
}

const toggleTheme = () => {
  trigger('light')
  themeStore.toggle()
}

const handleLogout = () => {
  trigger('medium')
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 100px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 50px 24px 24px;
  background: var(--primary-gradient);
  border-radius: 0 0 30px 30px;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar {
  width: 64px;
  height: 64px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
}

.user-info h2 {
  font-size: 20px;
  color: white;
  margin-bottom: 4px;
}

.user-info p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

.btn-edit {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 20px;
  color: white;
  font-size: 13px;
  cursor: pointer;
}

.stats-section {
  display: flex;
  justify-content: space-around;
  padding: 20px;
  margin: -20px 24px 0;
  background: var(--bg-card);
  border-radius: 16px;
  box-shadow: 0 4px 20px var(--shadow-color);
  position: relative;
  z-index: 10;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: var(--text-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.style-profile-section {
  padding: 24px;
}

.style-profile-section h3 {
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.profile-card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px var(--shadow-color);
}

.profile-item {
  margin-bottom: 20px;
}

.profile-item:last-child {
  margin-bottom: 0;
}

.profile-item label {
  display: block;
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 10px;
}

.color-options {
  display: flex;
  gap: 12px;
}

.color-chip {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--border-color);
  transition: all 0.2s;
}

.color-chip.active {
  border-color: var(--accent-color);
  transform: scale(1.1);
  color: var(--accent-color);
  font-size: 14px;
  font-weight: bold;
}

.body-options {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.body-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 8px;
  background: var(--bg-secondary);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.body-option:active {
  transform: scale(0.95);
}

.body-option.active {
  background: var(--primary-gradient);
}

.body-option.active span {
  color: white;
}

.body-icon {
  font-size: 24px;
}

.body-option span:last-child {
  font-size: 11px;
  color: var(--text-secondary);
}

.style-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.style-tag {
  padding: 8px 14px;
  background: var(--bg-secondary);
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.style-tag:active {
  transform: scale(0.95);
}

.style-tag.active {
  background: var(--primary-gradient);
  color: white;
}

.menu-section {
  padding: 0 24px;
}

.menu-item {
  display: flex;
  align-items: center;
  background: var(--bg-card);
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.menu-item:active {
  background: var(--bg-secondary);
}

.menu-icon {
  font-size: 20px;
  margin-right: 12px;
}

.menu-text {
  flex: 1;
  font-size: 15px;
  color: var(--text-primary);
}

.menu-arrow {
  font-size: 20px;
  color: var(--text-tertiary);
}

.btn-logout {
  display: block;
  width: calc(100% - 48px);
  margin: 24px auto 0;
  padding: 14px;
  background: var(--bg-card);
  border: 2px solid #ff4d4f;
  border-radius: 12px;
  color: #ff4d4f;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:active {
  background: #ff4d4f;
  color: white;
}
</style>
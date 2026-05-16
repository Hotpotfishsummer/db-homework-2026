<template>
  <div class="profile-container">
    <div class="profile-header">
      <div class="avatar-section">
        <div class="avatar" @click="triggerAvatarUpload">
          <img v-if="previewUrl || userStore.profile.avatar" :src="previewUrl || userStore.profile.avatar" alt="avatar" />
          <span v-else>{{ authStore.user?.username?.charAt(0)?.toUpperCase() || 'U' }}</span>
          <div v-if="uploading" class="avatar-overlay">
            <div class="spinner"></div>
          </div>
        </div>
        <input ref="fileInput" type="file" accept="image/jpeg,image/png" hidden @change="onFileChange" />
        <div class="user-info">
          <h2>{{ authStore.user?.username || '用户' }}</h2>
          <p>AI 穿搭会员</p>
          <p v-if="uploadError" class="upload-error">{{ uploadError }}</p>
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
      <div class="section-header">
        <h3>🎨 时尚档案</h3>
        <span v-if="!editMode && hasCompleteProfile" class="save-hint">已保存</span>
      </div>

      <div class="profile-card" :class="{ editing: editMode }">
        <!-- 编辑模式下显示提示 -->
        <div v-if="editMode" class="edit-tip">
          <span>✨ 点击选择，点击取消</span>
        </div>

        <div class="profile-item">
          <label>肤色</label>
          <div class="color-options">
            <div
              v-for="tone in skinTones"
              :key="tone.id"
              class="color-chip"
              :class="{ active: userStore.profile.skinTone === tone.id }"
              :style="{ background: tone.color }"
              @click="editMode && selectSkinTone(tone.id)"
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
              :class="{ active: userStore.profile.bodyType === body.id, disabled: !editMode }"
              @click="editMode && selectBodyType(body.id)"
            >
              <span class="body-icon">{{ body.icon }}</span>
              <span class="body-name">{{ body.name }}</span>
              <span class="body-desc">{{ body.desc }}</span>
            </div>
          </div>
        </div>

        <div class="profile-item">
          <label>风格偏好</label>
          <div class="style-tags">
            <div
              v-for="style in styleOptions"
              :key="style.id"
              class="style-tag"
              :class="{ active: userStore.profile.styles.includes(style.id), disabled: !editMode }"
              @click="editMode && toggleStyle(style.id)"
            >
              <span class="style-name">{{ style.label }}</span>
              <span class="style-desc">{{ style.desc }}</span>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUserStore } from '../stores/user'
import { useWardrobeStore } from '../stores/wardrobe'
import { useThemeStore } from '../stores/theme'
import { useHaptics } from '../composables/useHaptics'
import { validateImage } from '../services/user'
import BottomNav from '../components/BottomNav.vue'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const wardrobeStore = useWardrobeStore()
const themeStore = useThemeStore()
const { trigger } = useHaptics()

const editMode = ref(false)
const uploading = ref(false)
const uploadError = ref('')
const previewUrl = ref('')
const fileInput = ref(null)

const hasCompleteProfile = computed(() => {
  return userStore.profile.skinTone && userStore.profile.bodyType && userStore.profile.styles.length > 0
})

const skinTones = [
  { id: 'fair', color: '#ffe4c4' },
  { id: 'light', color: '#f5deb3' },
  { id: 'medium', color: '#deb887' },
  { id: 'tan', color: '#d2a679' },
  { id: 'dark', color: '#8b5a2b' }
]

const bodyTypes = [
  { id: 'slim', name: '纤细修长', icon: '🎋', desc: '高挑轻盈' },
  { id: 'athletic', name: '健康活力', icon: '💪', desc: '紧致有力' },
  { id: 'curvy', name: '玲珑曲线', icon: '🌙', desc: '柔美动人' },
  { id: 'balanced', name: '匀称自然', icon: '☯️', desc: '和谐舒展' }
]

const styleOptions = [
  { id: 'minimal', label: '静奢极简', desc: 'Less is more' },
  { id: 'vintage', label: '复古文艺', desc: '时光沉淀' },
  { id: 'urban', label: '都市通勤', desc: '利落干练' },
  { id: 'outdoor', label: '户外机能', desc: '自由探索' },
  { id: 'intellectual', label: '知识分子', desc: '书卷气息' },
  { id: 'french', label: '慵懒法式', desc: '松弛优雅' },
  { id: 'avantgarde', label: '前卫先锋', desc: '突破边界' },
  { id: 'zen', label: '东方禅意', desc: '内敛雅致' }
]

onMounted(() => {
  authStore.checkAuth()
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  wardrobeStore.initMockData()
  userStore.loadProfile()
})

const triggerAvatarUpload = () => {
  fileInput.value?.click()
}

const onFileChange = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  // 校验
  const validation = validateImage(file)
  if (!validation.valid) {
    uploadError.value = validation.error
    return
  }

  uploadError.value = ''
  uploading.value = true
  previewUrl.value = URL.createObjectURL(file)

  try {
    await userStore.updateAvatar(file)
    trigger('light')
  } catch (err) {
    uploadError.value = err.msg || '上传失败'
  } finally {
    uploading.value = false
  }
}

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
  overflow: hidden;
  cursor: pointer;
  position: relative;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #fff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.upload-error {
  color: #ff4d4f;
  font-size: 11px;
  margin-top: 2px;
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.save-hint {
  font-size: 12px;
  color: #52c41a;
  background: rgba(82, 196, 26, 0.1);
  padding: 4px 10px;
  border-radius: 10px;
}

.edit-tip {
  text-align: center;
  padding: 8px;
  margin-bottom: 12px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.profile-card.editing {
  border: 2px dashed var(--accent-color);
}

.color-chip.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.body-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.style-tag.disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.body-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 14px 10px;
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

.body-option.active .body-name,
.body-option.active .body-desc {
  color: white;
}

.body-icon {
  font-size: 22px;
  margin-bottom: 2px;
}

.body-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.body-desc {
  font-size: 10px;
  color: var(--text-tertiary);
}

.style-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.style-tag {
  display: flex;
  flex-direction: column;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: calc(50% - 4px);
}

.style-tag:active {
  transform: scale(0.98);
}

.style-tag.active {
  background: var(--primary-gradient);
}

.style-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.style-desc {
  font-size: 10px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.style-tag.active .style-name {
  color: white;
}

.style-tag.active .style-desc {
  color: rgba(255, 255, 255, 0.8);
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
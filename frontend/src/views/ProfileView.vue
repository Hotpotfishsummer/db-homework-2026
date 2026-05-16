<template>
  <div class="profile-container">
    <!-- 顶部进度条 -->
    <div v-if="userStore.profileCompleteness < 100" class="profile-progress-bar">
      <div class="progress-info">
        <span class="progress-label">时尚档案完善度</span>
        <span class="progress-value">{{ userStore.profileCompleteness }}%</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: userStore.profileCompleteness + '%' }"></div>
      </div>
    </div>

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
        <h3>数字人体卡片</h3>
        <span v-if="!editMode && hasCompleteProfile" class="save-hint">已保存</span>
      </div>

      <!-- ===== 1. 物理档案 ===== -->
      <div class="profile-card" :class="{ editing: editMode }">
        <div v-if="editMode" class="edit-tip">
          <span>✨ 点击选择，点击取消</span>
        </div>

        <!-- 基础维度 -->
        <div class="profile-item">
          <label>📏 基础维度</label>
          <div class="body-metrics">
            <div class="metric-input">
              <span class="metric-icon">📏</span>
              <input
                type="number"
                v-model="heightInput"
                placeholder="身高"
                :disabled="!editMode"
                @change="updateHeight"
              />
              <span class="metric-unit">cm</span>
            </div>
            <div class="metric-input">
              <span class="metric-icon">⚖️</span>
              <input
                type="number"
                v-model="weightInput"
                placeholder="体重"
                :disabled="!editMode"
                @change="updateWeight"
              />
              <span class="metric-unit">kg</span>
            </div>
            <div class="bmi-display" v-if="userStore.calculatedBMI">
              <span class="bmi-label">BMI</span>
              <span class="bmi-value" :class="bmiClass">{{ userStore.calculatedBMI }}</span>
            </div>
          </div>
        </div>

        <!-- 肤色定调 -->
        <div class="profile-item">
          <label>🎨 肤色定调</label>
          <div class="color-options">
            <div
              v-for="tone in skinTones"
              :key="tone.id"
              class="color-chip"
              :class="{ active: userStore.profile.skinTone === tone.id }"
              :style="{ background: tone.color }"
              @click="editMode && selectSkinTone(tone.id)"
            >
              <span v-if="userStore.profile.skinTone === tone.id" class="check-mark">✓</span>
              <span class="tone-label">{{ tone.name }}</span>
            </div>
          </div>
          <p class="profile-hint" v-if="userStore.profile.skinTone">
            💡 AI分析：你是「{{ getSeasonName(userStore.profile.skinTone) }}」，适合{{ getColorRecommendation(userStore.profile.skinTone) }}
          </p>
        </div>

        <!-- 体型选择 -->
        <div class="profile-item">
          <label>👤 体型</label>
          <div class="body-options">
            <div
              v-for="body in bodyShapes"
              :key="body.id"
              class="body-option"
              :class="{ active: userStore.profile.bodyShape === body.id }"
              @click="editMode && selectBodyShape(body.id)"
            >
              <div class="body-silhouette" v-html="body.svg"></div>
              <span class="body-name">{{ body.name }}</span>
            </div>
          </div>
        </div>

        <!-- 面部特征 -->
        <div class="profile-item">
          <label>✨ 面部特征（可选）</label>
          <div class="face-options">
            <div
              v-for="face in faceFeatures"
              :key="face.id"
              class="face-chip"
              :class="{ active: userStore.profile.faceFeature === face.id }"
              @click="editMode && selectFaceFeature(face.id)"
            >
              <span class="face-icon">{{ face.icon }}</span>
              <span class="face-name">{{ face.name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== 2. 风格标签 ===== -->
      <div class="section-header" style="margin-top: 24px;">
        <h3>时尚人格</h3>
      </div>

      <div class="profile-card" :class="{ editing: editMode }">
        <!-- 风格象限 -->
        <div class="profile-item">
          <label>📊 风格坐标</label>
          <div class="style-axes">
            <div class="axis-item" v-for="axis in styleAxes" :key="axis.id">
              <div class="axis-labels">
                <span>{{ axis.left }}</span>
                <span>{{ axis.right }}</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                v-model="userStore.profile.styleAxes[axis.id]"
                :disabled="!editMode"
                class="axis-slider"
                :style="getSliderStyle(axis.id)"
              />
              <div class="axis-value">{{ userStore.profile.styleAxes[axis.id] }}</div>
            </div>
          </div>
        </div>

        <!-- 风格标签 -->
        <div class="profile-item">
          <label>🏷️ 灵感标签</label>
          <div class="style-tags">
            <div
              v-for="style in styleTags"
              :key="style.id"
              class="style-tag"
              :class="{ active: userStore.profile.styleTags.includes(style.id) }"
              @click="editMode && toggleStyleTag(style.id)"
            >
              <span class="tag-name">{{ style.name }}</span>
              <span class="tag-desc">{{ style.desc }}</span>
            </div>
          </div>
        </div>

        <!-- 色彩偏好 -->
        <div class="profile-item">
          <label>❤️ 红榜（喜欢的颜色）</label>
          <div class="color-preference">
            <div
              v-for="color in availableColors"
              :key="color.id"
              class="pref-color"
              :class="{ active: userStore.profile.favoriteColors.includes(color.id), disabled: userStore.profile.avoidColors.includes(color.id) }"
              :style="{ background: color.color }"
              @click="editMode && toggleFavoriteColor(color.id)"
            >
              <span v-if="userStore.profile.favoriteColors.includes(color.id)">♥</span>
            </div>
          </div>
        </div>

        <div class="profile-item">
          <label>🚫 黑榜（绝不尝试的颜色）</label>
          <div class="color-preference">
            <div
              v-for="color in availableColors"
              :key="color.id"
              class="pref-color avoid"
              :class="{ active: userStore.profile.avoidColors.includes(color.id), disabled: userStore.profile.favoriteColors.includes(color.id) }"
              :style="{ background: color.color }"
              @click="editMode && toggleAvoidColor(color.id)"
            >
              <span v-if="userStore.profile.avoidColors.includes(color.id)">✕</span>
            </div>
          </div>
        </div>

        <!-- 版型偏好 -->
        <div class="profile-item">
          <label>📐 版型偏好</label>
          <div class="fit-options">
            <div
              v-for="fit in fitPreferences"
              :key="fit.id"
              class="fit-option"
              :class="{ active: userStore.profile.fitPreference === fit.id }"
              @click="editMode && selectFit(fit.id)"
            >
              <span class="fit-icon">{{ fit.icon }}</span>
              <span class="fit-name">{{ fit.name }}</span>
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

// 身高体重输入
const heightInput = ref(userStore.profile.height)
const weightInput = ref(userStore.profile.weight)

const hasCompleteProfile = computed(() => {
  return userStore.profile.skinTone && userStore.profile.bodyShape && userStore.profile.styleTags.length > 0
})

const bmiClass = computed(() => {
  const bmi = userStore.calculatedBMI
  if (!bmi) return ''
  if (bmi < 18.5) return 'bmi-low'
  if (bmi < 24) return 'bmi-normal'
  if (bmi < 28) return 'bmi-high'
  return 'bmi-obese'
})

// 肤色选项
const skinTones = [
  { id: 'fair_cool', name: '冷白', color: '#fce4d6', season: 'summer', recommendation: '柔和的冷色调，如雾霾蓝、薰衣草紫' },
  { id: 'fair_warm', name: '暖白', color: '#ffe4c4', season: 'spring', recommendation: '温暖的珊瑚色、米白色' },
  { id: 'medium', name: '自然', color: '#deb887', season: 'autumn', recommendation: '大地色系，如焦糖色、橄榄绿' },
  { id: 'tan', name: '小麦', color: '#d2a679', season: 'autumn', recommendation: '温暖的砖红色、芥末黄' },
  { id: 'dark', name: '深褐', color: '#8b5a2b', season: 'deep_winter', recommendation: '饱和度高的深色，如宝蓝、墨绿' }
]

// 体型选项（可视化SVG）
const bodyShapes = [
  {
    id: 'inverted_triangle',
    name: '倒三角',
    svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M20 5 L35 25 L30 55 L10 55 L5 25 Z"/></svg>`
  },
  {
    id: 'rectangle',
    name: '矩形',
    svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M10 5 L30 5 L30 55 L10 55 Z"/></svg>`
  },
  {
    id: 'pear',
    name: '梨型',
    svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M15 5 L25 5 L25 25 L35 35 L30 55 L10 55 L5 35 L15 25 Z"/></svg>`
  },
  {
    id: 'hourglass',
    name: '沙漏',
    svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M10 5 L30 5 L30 15 L32 25 L28 35 L32 45 L30 55 L10 55 L8 45 L12 35 L8 25 L10 15 Z"/></svg>`
  },
  {
    id: 'apple',
    name: '苹果',
    svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M12 5 L28 5 L28 15 Q35 20 30 30 L28 40 L30 55 L10 55 L12 40 L10 30 Q5 20 12 15 Z"/></svg>`
  }
]

// 面部特征
const faceFeatures = [
  { id: 'soft', name: '幼态柔和', icon: '🥚' },
  { id: 'sharp', name: '硬朗立体', icon: '⚔️' },
  { id: 'mature', name: '成熟优雅', icon: '👑' },
  { id: 'youthful', name: '元气活力', icon: '☀️' }
]

// 风格象限
const styleAxes = [
  { id: 'minimalComplex', left: '极简', right: '繁复' },
  { id: 'vintageModern', left: '复古', right: '科技' },
  { id: 'formalCasual', left: '正式', right: '休闲' }
]

// 风格标签
const styleTags = [
  { id: 'old_money', name: 'Old Money', desc: '低调奢华' },
  { id: 'intellectual', name: '高智感', desc: '书卷气质' },
  { id: 'dopamine', name: '多巴胺', desc: '色彩狂欢' },
  { id: 'american_vintage', name: '美式复古', desc: '街头经典' },
  { id: 'y2k', name: 'Y2K', desc: '千禧未来' },
  { id: 'clean_fit', name: 'Clean Fit', desc: '极简利落' },
  { id: 'athleisure', name: 'Athleisure', desc: '运动休闲' },
  { id: 'normcore', name: 'Normcore', desc: '平凡日常' },
  { id: 'gorpcore', name: 'Gorpcore', desc: '户外机能' },
  { id: 'japanese', name: '日系风格', desc: '文艺清新' },
  { id: 'streetwear', name: '街头潮流', desc: '个性张扬' },
  { id: 'korean', name: '韩系风格', desc: '精致通勤' }
]

// 可选颜色
const availableColors = [
  { id: 'red', color: '#e53935' },
  { id: 'orange', color: '#ff9800' },
  { id: 'yellow', color: '#fdd835' },
  { id: 'green', color: '#43a047' },
  { id: 'cyan', color: '#00acc1' },
  { id: 'blue', color: '#1e88e5' },
  { id: 'purple', color: '#8e24aa' },
  { id: 'pink', color: '#ec407a' },
  { id: 'white', color: '#fafafa', border: true },
  { id: 'black', color: '#212121' },
  { id: 'gray', color: '#757575' },
  { id: 'brown', color: '#795548' }
]

// 版型偏好
const fitPreferences = [
  { id: 'slim', name: '修身', icon: '👔' },
  { id: 'regular', name: '合身', icon: '👕' },
  { id: 'oversized', name: '廓形', icon: '🧥' }
]

onMounted(() => {
  authStore.checkAuth()
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  wardrobeStore.initMockData()
  userStore.loadProfile()
  // 同步输入框
  heightInput.value = userStore.profile.height
  weightInput.value = userStore.profile.weight
})

const triggerAvatarUpload = () => {
  fileInput.value?.click()
}

const onFileChange = async (e) => {
  const file = e.target.files[0]
  if (!file) return

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

// 基础维度
const updateHeight = () => {
  trigger('light')
  userStore.updateProfile({ height: Number(heightInput.value) || null })
}

const updateWeight = () => {
  trigger('light')
  userStore.updateProfile({ weight: Number(weightInput.value) || null })
}

// 肤色
const selectSkinTone = (id) => {
  trigger('light')
  userStore.updateProfile({ skinTone: id })
}

const getSeasonName = (skinToneId) => {
  const tones = {
    fair_cool: '夏季人',
    fair_warm: '春季人',
    medium: '秋季人',
    tan: '秋季人',
    dark: '深冬人'
  }
  return tones[skinToneId] || '未知'
}

const getColorRecommendation = (skinToneId) => {
  const tone = skinTones.find(t => t.id === skinToneId)
  return tone?.recommendation || '基础色'
}

// 体型
const selectBodyShape = (id) => {
  trigger('light')
  userStore.updateProfile({ bodyShape: id })
}

// 面部特征
const selectFaceFeature = (id) => {
  trigger('light')
  const current = userStore.profile.faceFeature
  userStore.updateProfile({ faceFeature: current === id ? null : id })
}

// 风格标签
const toggleStyleTag = (id) => {
  trigger('light')
  const tags = [...userStore.profile.styleTags]
  const index = tags.indexOf(id)
  if (index > -1) {
    tags.splice(index, 1)
  } else {
    tags.push(id)
  }
  userStore.updateProfile({ styleTags: tags })
}

// 颜色偏好
const toggleFavoriteColor = (id) => {
  trigger('light')
  const colors = [...userStore.profile.favoriteColors]
  const index = colors.indexOf(id)
  if (index > -1) {
    colors.splice(index, 1)
  } else {
    // 先从黑榜移除
    const avoid = userStore.profile.avoidColors.filter(c => c !== id)
    userStore.updateProfile({ avoidColors: avoid })
    colors.push(id)
  }
  userStore.updateProfile({ favoriteColors: colors })
}

const toggleAvoidColor = (id) => {
  trigger('light')
  const colors = [...userStore.profile.avoidColors]
  const index = colors.indexOf(id)
  if (index > -1) {
    colors.splice(index, 1)
  } else {
    // 先从红榜移除
    const fav = userStore.profile.favoriteColors.filter(c => c !== id)
    userStore.updateProfile({ favoriteColors: fav })
    colors.push(id)
  }
  userStore.updateProfile({ avoidColors: colors })
}

// 版型
const selectFit = (id) => {
  trigger('light')
  const current = userStore.profile.fitPreference
  userStore.updateProfile({ fitPreference: current === id ? null : id })
}

// 滑块样式
const getSliderStyle = (axisId) => {
  const value = userStore.profile.styleAxes[axisId]
  const hue = (value / 100) * 120 // 0-120: 红-绿
  return {
    background: `linear-gradient(to right, hsl(${hue}, 70%, 50%), hsl(${hue}, 70%, 70%))`
  }
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

/* 进度条 */
.profile-progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 8px 24px 12px;
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.95) 0%, rgba(102, 126, 234, 0.8) 100%);
  backdrop-filter: blur(10px);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.progress-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
}

.progress-value {
  font-size: 11px;
  color: white;
  font-weight: 600;
}

.progress-track {
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: white;
  border-radius: 2px;
  transition: width 0.3s ease;
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

/* 新增样式 - 基础维度 */
.body-metrics {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.metric-input {
  display: flex;
  align-items: center;
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 8px 14px;
  gap: 8px;
  flex: 1;
  min-width: 100px;
}

.metric-icon {
  font-size: 16px;
}

.metric-input input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  width: 60px;
}

.metric-input input::placeholder {
  color: var(--text-tertiary);
}

.metric-input input:disabled {
  color: var(--text-secondary);
}

.metric-unit {
  font-size: 12px;
  color: var(--text-tertiary);
}

.bmi-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: var(--bg-secondary);
  padding: 8px 14px;
  border-radius: 12px;
  min-width: 60px;
}

.bmi-label {
  font-size: 10px;
  color: var(--text-tertiary);
}

.bmi-value {
  font-size: 18px;
  font-weight: bold;
  color: var(--text-primary);
}

.bmi-value.bmi-normal {
  color: #52c41a;
}

.bmi-value.bmi-low {
  color: #faad14;
}

.bmi-value.bmi-high,
.bmi-value.bmi-obese {
  color: #ff4d4f;
}

/* 肤色选项增强 */
.color-options {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.color-chip {
  width: 48px;
  height: 56px;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  border: 2px solid var(--border-color);
  transition: all 0.25s;
}

.color-chip:active {
  transform: scale(0.95);
}

.color-chip.active {
  border-color: var(--accent-color);
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.check-mark {
  font-size: 14px;
  font-weight: bold;
}

.tone-label {
  font-size: 9px;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.8);
  padding: 1px 4px;
  border-radius: 4px;
}

.color-chip.active .tone-label {
  background: var(--accent-color);
  color: white;
}

.profile-hint {
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-secondary);
  padding: 10px 12px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08), rgba(118, 75, 162, 0.08));
  border-radius: 8px;
}

/* 体型选项 - 2行3列 */
.body-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.body-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
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
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.body-silhouette {
  width: 32px;
  height: 48px;
  color: var(--text-tertiary);
}

.body-option.active .body-silhouette {
  color: white;
}

.body-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
}

.body-option.active .body-name {
  color: white;
}

/* 面部特征 */
.face-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.face-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-secondary);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.face-chip:active {
  transform: scale(0.95);
}

.face-chip.active {
  background: var(--primary-gradient);
}

.face-icon {
  font-size: 16px;
}

.face-name {
  font-size: 13px;
  color: var(--text-primary);
}

.face-chip.active .face-name {
  color: white;
}

/* 风格象限 */
.style-axes {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.axis-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.axis-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-tertiary);
}

.axis-slider {
  -webkit-appearance: none;
  width: 100%;
  height: 8px;
  border-radius: 4px;
  outline: none;
}

.axis-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  cursor: pointer;
}

.axis-slider:disabled {
  opacity: 0.6;
}

.axis-slider:disabled::-webkit-slider-thumb {
  cursor: not-allowed;
}

.axis-value {
  text-align: center;
  font-size: 12px;
  color: var(--accent-color);
  font-weight: 600;
}

/* 颜色偏好 */
.color-preference {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pref-color {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--border-color);
  transition: all 0.2s;
}

.pref-color:active {
  transform: scale(0.9);
}

.pref-color.active {
  border-color: var(--accent-color);
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.pref-color.avoid {
  opacity: 0.7;
}

.pref-color.avoid.active {
  border-color: #ff4d4f;
  box-shadow: 0 2px 8px rgba(255, 77, 79, 0.3);
}

.pref-color.disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.pref-color span {
  font-size: 14px;
  font-weight: bold;
}

.pref-color:not(.avoid) span {
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.pref-color.avoid span {
  color: #ff4d4f;
}

/* 版型偏好 */
.fit-options {
  display: flex;
  gap: 10px;
}

.fit-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px;
  background: var(--bg-secondary);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.fit-option:active {
  transform: scale(0.95);
}

.fit-option.active {
  background: var(--primary-gradient);
}

.fit-icon {
  font-size: 24px;
}

.fit-name {
  font-size: 13px;
  color: var(--text-primary);
}

.fit-option.active .fit-name {
  color: white;
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
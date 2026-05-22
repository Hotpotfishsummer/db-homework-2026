<template>
  <div class="profile-container" ref="containerRef" @touchstart="onTouchStart" @touchend="onTouchEnd">
    <!-- ===== 1. 顶部视觉区 (Cover Section) ===== -->
    <div class="cover-section">
      <div class="cover-bg" :style="coverStyle" ref="coverBgRef">
        <!-- 上下模糊渐变层 -->
        <div class="cover-blur-top"></div>
        <div class="cover-blur-bottom"></div>

        <!-- 头像 - 左下角，2/3在背景图上 -->
        <div class="avatar-wrapper" @click="showAvatarModal = true">
          <div class="avatar-ring">
            <div class="avatar">
              <img v-if="previewUrl || userStore.profile.avatar" :src="previewUrl || userStore.profile.avatar" alt="avatar" />
              <span v-else class="avatar-placeholder">{{ authStore.user?.username?.charAt(0)?.toUpperCase() || 'U' }}</span>
              <div v-if="uploading" class="avatar-overlay">
                <div class="spinner"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 用户名 + 会员 - 紧贴在头像右边 -->
        <div class="cover-user-info">
          <h2 class="cover-username">{{ authStore.user?.username || '用户' }}</h2>
          <p class="cover-membership">AI 穿搭会员</p>
        </div>

        <!-- 设置齿轮 -->
        <button class="btn-settings" @click="goToSettings">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="gear-icon">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
        </button>
      </div>
      <input ref="coverInput" type="file" accept="image/jpeg,image/png" hidden @change="onCoverChange" />
      <input ref="fileInput" type="file" accept="image/jpeg,image/png" hidden @change="onFileChange" />

      <!-- ===== 2. 个性签名区 (紧贴背景图，无空隙) ===== -->
      <div class="bio-bar">
        <!-- 数据统计卡片 - 头像1/3右侧 -->
        <div class="stats-inline">
          <span class="stat-inline-item" @click="activeTab = 'liked'; scrollToTabs()">❤️ 收藏&nbsp;{{ userStore.likedOutfits.length }}</span>
          <span class="stat-inline-sep">·</span>
          <span class="stat-inline-item">👕 衣橱&nbsp;{{ wardrobeStore.clothes.length }}</span>
          <span class="stat-inline-sep">·</span>
          <span class="stat-inline-item" @click="activeTab = 'history'; scrollToTabs()">🕐 浏览&nbsp;{{ userStore.historyOutfits.length }}</span>
        </div>

        <!-- 个性签名 + 完善档案 (同一行) -->
        <div class="bio-row">
          <p class="bio-text" v-if="userStore.profile.bio">"{{ userStore.profile.bio }}"</p>
          <p v-else class="bio-text placeholder">写下一句话穿搭宣言...</p>
          <button class="btn-edit-profile" @click="goToProfileEdit">完善档案</button>
        </div>

        <p v-if="uploadError" class="upload-error">{{ uploadError }}</p>
      </div>
    </div>

    <!-- ===== 3. 数字人体卡片 ===== -->
    <div class="body-card-section">
      <div class="body-card">
        <div class="body-card-header">
          <h3>数字人体卡片</h3>
          <span v-if="hasCompleteProfile" class="save-badge">已完善</span>
        </div>

        <div class="body-summary">
          <div class="summary-row" v-if="userStore.profile.height || userStore.profile.weight">
            <span class="summary-icon">📏</span>
            <span v-if="userStore.profile.height">{{ userStore.profile.height }}cm</span>
            <span v-if="userStore.profile.height && userStore.profile.weight"> / </span>
            <span v-if="userStore.profile.weight">{{ userStore.profile.weight }}kg</span>
            <span v-if="userStore.calculatedBMI" class="bmi-tag" :class="bmiClass">BMI {{ userStore.calculatedBMI }}</span>
          </div>
          <div class="summary-row" v-if="userStore.profile.skinTone">
            <span class="summary-icon">🎨</span>
            <span>{{ getSeasonName(userStore.profile.skinTone) }}</span>
            <span class="skin-chip" :style="{ background: getSkinColor(userStore.profile.skinTone) }"></span>
          </div>
          <div class="summary-row" v-if="userStore.profile.bodyShape">
            <span class="summary-icon">👤</span>
            <span>{{ getBodyShapeName(userStore.profile.bodyShape) }}</span>
          </div>
          <div class="summary-row" v-if="userStore.profile.styleTags.length > 0">
            <span class="summary-icon">🏷️</span>
            <div class="summary-tags">
              <span v-for="tag in userStore.profile.styleTags.slice(0, 4)" :key="tag" class="mini-tag">{{ getStyleTagName(tag) }}</span>
              <span v-if="userStore.profile.styleTags.length > 4" class="mini-tag more">+{{ userStore.profile.styleTags.length - 4 }}</span>
            </div>
          </div>
          <p v-if="!hasCompleteProfile" class="body-hint">点击"完善档案"来建立你的数字人体模型</p>
        </div>
      </div>
    </div>

    <!-- ===== 4. 内容切换区 (Tabs) - 吸顶 ===== -->
    <div class="tabs-wrapper" ref="tabsRef" :class="{ sticky: isTabSticky }">
      <div class="tabs">
        <div
          class="tab"
          :class="{ active: activeTab === 'liked' }"
          @click="activeTab = 'liked'"
        >
          <span class="tab-icon">❤️</span>
          <span class="tab-text">收藏</span>
          <span class="tab-count" v-if="userStore.likedOutfits.length">{{ userStore.likedOutfits.length }}</span>
        </div>
        <div
          class="tab"
          :class="{ active: activeTab === 'history' }"
          @click="activeTab = 'history'"
        >
          <span class="tab-icon">🕐</span>
          <span class="tab-text">浏览</span>
          <span class="tab-count" v-if="userStore.historyOutfits.length">{{ userStore.historyOutfits.length }}</span>
        </div>
      </div>
    </div>

    <!-- Tab 内容区 -->
    <div class="tab-content">
      <!-- 收藏 -->
      <div v-if="activeTab === 'liked'" class="tab-panel">
        <div v-if="userStore.likedOutfits.length > 0" class="outfit-list">
          <div
            v-for="outfit in userStore.likedOutfits" :key="outfit.id"
            class="outfit-item"
            @click="goToDetail(outfit)"
          >
            <div class="outfit-image">
              <img :src="outfit.image" :alt="outfit.name" loading="lazy" />
              <span class="outfit-scene">{{ outfit.scene }}</span>
            </div>
            <div class="outfit-info">
              <h4>{{ outfit.name }}</h4>
              <p>{{ outfit.description }}</p>
              <span class="outfit-rate">💫 {{ outfit.matchRate }}%</span>
            </div>
            <button class="outfit-action liked" @click.stop="confirmUnlike(outfit)">❤️</button>
          </div>
        </div>
        <div v-else class="empty-state">
          <span class="empty-icon">💝</span>
          <p>还没有收藏</p>
          <p class="empty-hint">去首页发现喜欢的穿搭吧</p>
          <button class="go-discover" @click="goHome">去发现</button>
        </div>
      </div>

      <!-- 浏览历史 -->
      <div v-if="activeTab === 'history'" class="tab-panel">
        <div v-if="userStore.historyOutfits.length > 0" class="history-list">
          <div
            v-for="(outfit, index) in userStore.historyOutfits" :key="`${outfit.id}-${index}`"
            class="history-item"
            @click="goToDetail(outfit)"
          >
            <div class="history-image">
              <img :src="outfit.image" :alt="outfit.name" loading="lazy" />
            </div>
            <div class="history-info">
              <h4>{{ outfit.name }}</h4>
              <p>{{ formatTime(outfit.viewedAt) }}</p>
            </div>
            <span class="history-arrow">›</span>
          </div>
        </div>
        <div v-else class="empty-state">
          <span class="empty-icon">🕐</span>
          <p>还没有浏览记录</p>
          <p class="empty-hint">去首页看看吧</p>
          <button class="go-discover" @click="goHome">去发现</button>
        </div>
      </div>
    </div>

    <!-- 退出登录 -->
    <button class="btn-logout" @click="handleLogout">
      退出登录
    </button>

    <p class="bottom-hint">~ 探索更多穿搭灵感 ~</p>

    <BottomNav />

    <!-- ===== 头像大图预览 ===== -->
    <Teleport to="body">
      <div v-if="showAvatarModal" class="avatar-modal" @click="showAvatarModal = false">
        <div class="avatar-modal-mask"></div>
        <div class="avatar-modal-content">
          <img v-if="previewUrl || userStore.profile.avatar" :src="previewUrl || userStore.profile.avatar" alt="avatar" />
          <div v-else class="avatar-modal-placeholder">{{ authStore.user?.username?.charAt(0)?.toUpperCase() || 'U' }}</div>
          <button class="avatar-modal-close" @click="showAvatarModal = false">✕</button>
        </div>
      </div>

      <!-- ===== 取消收藏确认弹窗 ===== -->
      <div v-if="unlikeTarget" class="confirm-dialog" @click.self="unlikeTarget = null">
        <div class="confirm-mask"></div>
        <div class="confirm-card">
          <p class="confirm-title">移出珍藏</p>
          <p class="confirm-desc">这份穿搭灵感将从你的收藏夹中悄然离去</p>
          <div class="confirm-actions">
            <button class="confirm-btn cancel" @click="unlikeTarget = null">再想想</button>
            <button class="confirm-btn confirm" @click="doUnlike">移出收藏</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
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

const uploading = ref(false)
const uploadError = ref('')
const previewUrl = ref('')
const fileInput = ref(null)
const coverInput = ref(null)
const activeTab = ref('liked')
const showAvatarModal = ref(false)
const unlikeTarget = ref(null)
const isTabSticky = ref(false)
const tabsRef = ref(null)
const coverBgRef = ref(null)
const containerRef = ref(null)
const pullDistance = ref(0)

// 输入绑定
const heightInput = ref(userStore.profile.height)
const weightInput = ref(userStore.profile.weight)
const bioInput = ref(userStore.profile.bio || '')
const birthdayInput = ref(userStore.profile.birthday || '')

const genderOptions = [
  { value: 'male', label: '男' },
  { value: 'female', label: '女' },
  { value: 'other', label: '其他' }
]

// 封面背景样式（含下拉拉伸）
const baseCoverHeight = 240
const coverStyle = computed(() => {
  const h = baseCoverHeight + pullDistance.value
  const style = { height: h + 'px' }
  if (userStore.profile.coverImage) {
    style.backgroundImage = `url(${userStore.profile.coverImage})`
    style.backgroundSize = 'cover'
    style.backgroundPosition = 'center'
  } else {
    style.background = 'var(--primary-gradient)'
  }
  return style
})

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

const bodyShapes = [
  { id: 'inverted_triangle', name: '倒三角', svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M20 5 L35 25 L30 55 L10 55 L5 25 Z"/></svg>` },
  { id: 'rectangle', name: '矩形', svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M10 5 L30 5 L30 55 L10 55 Z"/></svg>` },
  { id: 'pear', name: '梨型', svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M15 5 L25 5 L25 25 L35 35 L30 55 L10 55 L5 35 L15 25 Z"/></svg>` },
  { id: 'hourglass', name: '沙漏', svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M10 5 L30 5 L30 15 L32 25 L28 35 L32 45 L30 55 L10 55 L8 45 L12 35 L8 25 L10 15 Z"/></svg>` },
  { id: 'apple', name: '苹果', svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M12 5 L28 5 L28 15 Q35 20 30 30 L28 40 L30 55 L10 55 L12 40 L10 30 Q5 20 12 15 Z"/></svg>` }
]

const faceFeatures = [
  { id: 'soft', name: '幼态柔和', icon: '🥚' },
  { id: 'sharp', name: '硬朗立体', icon: '⚔️' },
  { id: 'mature', name: '成熟优雅', icon: '👑' },
  { id: 'youthful', name: '元气活力', icon: '☀️' }
]

const styleAxes = [
  { id: 'minimalComplex', left: '极简', right: '繁复' },
  { id: 'vintageModern', left: '复古', right: '科技' },
  { id: 'formalCasual', left: '正式', right: '休闲' }
]

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

const availableColors = [
  { id: 'red', color: '#e53935' }, { id: 'orange', color: '#ff9800' },
  { id: 'yellow', color: '#fdd835' }, { id: 'green', color: '#43a047' },
  { id: 'cyan', color: '#00acc1' }, { id: 'blue', color: '#1e88e5' },
  { id: 'purple', color: '#8e24aa' }, { id: 'pink', color: '#ec407a' },
  { id: 'white', color: '#fafafa' }, { id: 'black', color: '#212121' },
  { id: 'gray', color: '#757575' }, { id: 'brown', color: '#795548' }
]

const fitPreferences = [
  { id: 'slim', name: '修身', icon: '👔' },
  { id: 'regular', name: '合身', icon: '👕' },
  { id: 'oversized', name: '廓形', icon: '🧥' }
]

// ===== 生命周期 =====
onMounted(() => {
  authStore.checkAuth()
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  wardrobeStore.initMockData()
  userStore.loadProfile()
  heightInput.value = userStore.profile.height
  weightInput.value = userStore.profile.weight
  bioInput.value = userStore.profile.bio || ''
  birthdayInput.value = userStore.profile.birthday || ''
  window.addEventListener('scroll', onScroll)
  containerRef.value?.addEventListener('touchmove', onTouchMove, { passive: false })
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  containerRef.value?.removeEventListener('touchmove', onTouchMove)
})

// ===== 滚动处理 =====
let pullTimer = null
const onScroll = () => {
  // 桌面端橡皮筋效果（macOS/iOS）
  const sy = window.scrollY
  if (sy < 0) {
    pullDistance.value = Math.min(Math.abs(sy) * 0.6, 100)
  } else if (pullDistance.value > 0 && sy >= 0 && !isPulling) {
    clearTimeout(pullTimer)
    pullTimer = setTimeout(() => { pullDistance.value = 0 }, 80)
  }

  // Tab 吸顶
  if (tabsRef.value) {
    const rect = tabsRef.value.getBoundingClientRect()
    isTabSticky.value = rect.top <= 0
  }
}

// ===== 触摸下拉 =====
let touchStartY = 0
let isPulling = false

const onTouchStart = (e) => {
  if (window.scrollY <= 0) {
    touchStartY = e.touches[0].clientY
    isPulling = false
  }
}

const onTouchMove = (e) => {
  if (window.scrollY > 0 || !touchStartY) return
  const delta = e.touches[0].clientY - touchStartY
  if (delta > 10) {
    // 阻止原生橡皮筋效果，避免露出深色背景
    if (delta > 0) e.preventDefault()
    isPulling = true
    pullDistance.value = Math.min(delta * 0.45, 100)
  }
}

const onTouchEnd = () => {
  if (isPulling) {
    // 下拉后缓慢回弹，避免突兀跳动
    setTimeout(() => {
      touchStartY = 0
      isPulling = false
      pullDistance.value = 0
    }, 50)
  } else {
    touchStartY = 0
    isPulling = false
    pullDistance.value = 0
  }
}

// ===== 辅助函数 =====
const getSkinColor = (id) => {
  const tone = skinTones.find(t => t.id === id)
  return tone?.color || '#deb887'
}

const getSeasonName = (skinToneId) => {
  const map = { fair_cool: '夏季人', fair_warm: '春季人', medium: '秋季人', tan: '秋季人', dark: '深冬人' }
  return map[skinToneId] || '未知'
}

const getColorRecommendation = (skinToneId) => {
  const tone = skinTones.find(t => t.id === skinToneId)
  return tone?.recommendation || '基础色'
}

const getBodyShapeName = (id) => {
  const shape = bodyShapes.find(b => b.id === id)
  return shape?.name || ''
}

const getStyleTagName = (id) => {
  const tag = styleTags.find(t => t.id === id)
  return tag?.name || id
}

// ===== 头像操作 =====
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

// ===== 封面图操作 =====
const triggerCoverUpload = () => {
  coverInput.value?.click()
}

const onCoverChange = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  const validation = validateImage(file)
  if (!validation.valid) {
    uploadError.value = validation.error
    return
  }
  uploadError.value = ''
  const reader = new FileReader()
  reader.onload = (ev) => {
    userStore.updateProfile({ coverImage: ev.target.result })
    trigger('light')
  }
  reader.readAsDataURL(file)
}

// ===== Bio =====
const updateBio = () => {
  userStore.updateProfile({ bio: bioInput.value })
}

// ===== 性别 =====
const selectGender = (val) => {
  trigger('light')
  const current = userStore.profile.gender
  userStore.updateProfile({ gender: current === val ? null : val })
}

// ===== 生日 =====
const updateBirthday = () => {
  userStore.updateProfile({ birthday: birthdayInput.value })
}

// ===== 基础维度 =====
const updateHeight = () => { trigger('light'); userStore.updateProfile({ height: Number(heightInput.value) || null }) }
const updateWeight = () => { trigger('light'); userStore.updateProfile({ weight: Number(weightInput.value) || null }) }

// ===== 肤色 =====
const selectSkinTone = (id) => { trigger('light'); userStore.updateProfile({ skinTone: id }) }

// ===== 体型 =====
const selectBodyShape = (id) => { trigger('light'); userStore.updateProfile({ bodyShape: id }) }

// ===== 面部 =====
const selectFaceFeature = (id) => {
  trigger('light')
  const current = userStore.profile.faceFeature
  userStore.updateProfile({ faceFeature: current === id ? null : id })
}

// ===== 风格标签 =====
const toggleStyleTag = (id) => {
  trigger('light')
  const tags = [...userStore.profile.styleTags]
  const index = tags.indexOf(id)
  index > -1 ? tags.splice(index, 1) : tags.push(id)
  userStore.updateProfile({ styleTags: tags })
}

// ===== 颜色偏好 =====
const toggleFavoriteColor = (id) => {
  trigger('light')
  const colors = [...userStore.profile.favoriteColors]
  const index = colors.indexOf(id)
  if (index > -1) { colors.splice(index, 1) } else {
    userStore.updateProfile({ avoidColors: userStore.profile.avoidColors.filter(c => c !== id) })
    colors.push(id)
  }
  userStore.updateProfile({ favoriteColors: colors })
}

const toggleAvoidColor = (id) => {
  trigger('light')
  const colors = [...userStore.profile.avoidColors]
  const index = colors.indexOf(id)
  if (index > -1) { colors.splice(index, 1) } else {
    userStore.updateProfile({ favoriteColors: userStore.profile.favoriteColors.filter(c => c !== id) })
    colors.push(id)
  }
  userStore.updateProfile({ avoidColors: colors })
}

// ===== 版型 =====
const selectFit = (id) => {
  trigger('light')
  const current = userStore.profile.fitPreference
  userStore.updateProfile({ fitPreference: current === id ? null : id })
}

// ===== 滑块样式 =====
const getSliderStyle = (axisId) => {
  const value = userStore.profile.styleAxes[axisId]
  const hue = (value / 100) * 120
  return { background: `linear-gradient(to right, hsl(${hue}, 70%, 50%), hsl(${hue}, 70%, 70%))` }
}

// ===== 导航 =====
const goToDetail = (outfit) => { trigger('light'); router.push(`/outfit/${outfit.id}`) }
const goHome = () => { trigger('light'); router.push('/home') }
const confirmUnlike = (outfit) => { trigger('light'); unlikeTarget.value = outfit }
const doUnlike = () => {
  trigger('medium')
  userStore.unlikeOutfit(unlikeTarget.value.id)
  unlikeTarget.value = null
}
const toggleTheme = () => { trigger('light'); themeStore.toggle() }
const handleLogout = () => { trigger('medium'); authStore.logout(); router.push('/login') }
const goToSettings = () => { trigger('light'); router.push('/profile/settings') }
const goToProfileEdit = () => { trigger('light'); router.push('/profile/edit') }

const scrollToTabs = () => {
  tabsRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
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
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 100px;
  overscroll-behavior: none;
}

/* ========== 1. 顶部视觉区 (Cover Section) ========== */
.cover-section {
  position: relative;
}

.cover-bg {
  height: 240px;
  position: relative;
  overflow: visible;
  transition: height 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  will-change: height;
}

/* 顶部模糊渐变 */
.cover-blur-top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: linear-gradient(180deg, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0.1) 60%, transparent 100%);
  z-index: 2;
  pointer-events: none;
}

/* 底部模糊渐变 - 填充与下方内容的间隙 */
.cover-blur-bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(0deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.15) 50%, transparent 100%);
  z-index: 2;
  pointer-events: none;
}

/* 用户信息 - 紧贴头像右边 */
.cover-user-info {
  position: absolute;
  bottom: 12px;
  left: 116px;
  z-index: 5;
  display: flex;
  flex-direction: column;
}

.cover-username {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 1px 6px rgba(0,0,0,0.4);
  line-height: 1.3;
}

.cover-membership {
  font-size: 11px;
  color: rgba(255,255,255,0.9);
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  padding: 2px 10px;
  border-radius: 8px;
  margin-top: 4px;
}

/* 头像 - 左下角，2/3在背景图上 */
.avatar-wrapper {
  position: absolute;
  bottom: -27px;
  left: 24px;
  z-index: 10;
  cursor: pointer;
  transition: transform 0.2s;
}

.avatar-wrapper:active {
  transform: scale(0.95);
}

.avatar-ring {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  padding: 3px;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.25);
  position: relative;
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 30px;
  font-weight: bold;
  color: var(--accent-color);
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.5);
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

/* 设置齿轮 - 头像同行右侧 */
.btn-settings {
  position: absolute;
  bottom: 12px;
  right: 16px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: all 0.2s;
}

.btn-settings:active {
  transform: scale(0.9);
  background: rgba(255,255,255,0.35);
}

.gear-icon {
  width: 20px;
  height: 20px;
}

.upload-error {
  color: #ff4d4f;
  font-size: 11px;
  margin-top: 4px;
  padding: 0 24px;
}

/* ========== 2. 个性签名区 (紧贴背景图) ========== */
.bio-bar {
  background: var(--bg-card);
  padding: 10px 24px 14px 118px;
  min-height: 50px;
}

/* 数据统计卡片 - 头像1/3右侧 */
.stats-inline {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.stat-inline-item {
  cursor: pointer;
  font-weight: 500;
  transition: color 0.2s;
}

.stat-inline-item:active {
  color: var(--accent-color);
}

.stat-inline-sep {
  color: var(--text-tertiary);
  font-size: 10px;
  cursor: default;
}

/* 个性签名行 + 完善档案 (同一行) */
.bio-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bio-text {
  flex: 1;
  font-family: 'KaiTi', 'STKaiti', 'Georgia', 'Times New Roman', serif;
  font-size: 14px;
  font-style: italic;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 0.5px;
}

.bio-text.placeholder {
  color: var(--text-tertiary);
}

.btn-edit-profile {
  flex-shrink: 0;
  padding: 4px 12px;
  border: 1px solid var(--accent-color);
  border-radius: 12px;
  background: transparent;
  color: var(--accent-color);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit-profile:active {
  background: var(--accent-color);
  color: white;
}

/* ========== 3. 数字人体卡片 ========== */
.body-card-section {
  padding: 12px 24px 0;
}

.body-card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px var(--shadow-color);
  transition: border 0.3s;
}

.body-card.editing {
  border: 2px dashed var(--accent-color);
}

.body-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.body-card-header h3 {
  font-size: 16px;
  color: var(--text-primary);
  margin: 0;
}

.save-badge {
  font-size: 11px;
  color: #52c41a;
  background: rgba(82,196,26,0.1);
  padding: 2px 10px;
  border-radius: 8px;
}

/* 紧凑摘要 */
.body-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.summary-icon {
  width: 22px;
  text-align: center;
}

.bmi-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 1px 8px;
  border-radius: 6px;
  margin-left: 4px;
}

.bmi-tag.bmi-normal { background: rgba(82,196,26,0.12); color: #52c41a; }
.bmi-tag.bmi-low { background: rgba(250,173,20,0.12); color: #faad14; }
.bmi-tag.bmi-high, .bmi-tag.bmi-obese { background: rgba(255,77,79,0.12); color: #ff4d4f; }

.skin-chip {
  display: inline-block;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid var(--border-color);
  margin-left: 4px;
}

.summary-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.mini-tag {
  font-size: 10px;
  padding: 2px 8px;
  background: rgba(91,154,139,0.1);
  color: var(--accent-color);
  border-radius: 6px;
}

.mini-tag.more {
  background: var(--bg-secondary);
  color: var(--text-tertiary);
}

.body-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 4px;
}

/* 编辑模式完整界面 */
.body-edit-full {
  margin-top: 0;
}

.edit-tip {
  text-align: center;
  padding: 8px;
  margin-bottom: 16px;
  background: rgba(91,154,139,0.08);
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-secondary);
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

/* 基础维度 */
.body-metrics {
  display: flex;
  gap: 10px;
  align-items: center;
}

.metric-input {
  display: flex;
  align-items: center;
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 8px 14px;
  gap: 6px;
  flex: 1;
  min-width: 80px;
}

.metric-input input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  width: 50px;
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
  min-width: 55px;
}

.bmi-label { font-size: 10px; color: var(--text-tertiary); }
.bmi-value { font-size: 18px; font-weight: bold; color: var(--text-primary); }
.bmi-value.bmi-normal { color: #52c41a; }
.bmi-value.bmi-low { color: #faad14; }
.bmi-value.bmi-high, .bmi-value.bmi-obese { color: #ff4d4f; }

/* 肤色选项 */
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

.color-chip:active { transform: scale(0.95); }

.color-chip.active {
  border-color: var(--accent-color);
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(91,154,139,0.3);
}

.check-mark { font-size: 14px; font-weight: bold; }

.tone-label {
  font-size: 9px;
  color: var(--text-secondary);
  background: rgba(255,255,255,0.85);
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
  background: rgba(91,154,139,0.08);
  border-radius: 8px;
}

/* 体型 */
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

.body-option:active { transform: scale(0.95); }

.body-option.active {
  background: var(--primary-gradient);
  box-shadow: 0 4px 12px rgba(91,154,139,0.3);
}

.body-silhouette { width: 32px; height: 48px; color: var(--text-tertiary); }
.body-option.active .body-silhouette { color: white; }
.body-name { font-size: 12px; font-weight: 500; color: var(--text-primary); }
.body-option.active .body-name { color: white; }

/* 面部特征 */
.face-options { display: flex; gap: 8px; flex-wrap: wrap; }

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

.face-chip:active { transform: scale(0.95); }
.face-chip.active { background: var(--primary-gradient); }
.face-icon { font-size: 16px; }
.face-name { font-size: 13px; color: var(--text-primary); }
.face-chip.active .face-name { color: white; }

/* 风格象限 */
.style-axes { display: flex; flex-direction: column; gap: 16px; }

.axis-item { display: flex; flex-direction: column; gap: 6px; }

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
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  cursor: pointer;
}

.axis-value { text-align: center; font-size: 12px; color: var(--accent-color); font-weight: 600; }

/* 风格标签 */
.style-tags { display: flex; flex-wrap: wrap; gap: 8px; }

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

.style-tag:active { transform: scale(0.98); }
.style-tag.active { background: var(--primary-gradient); }

.tag-name { font-size: 14px; font-weight: 500; color: var(--text-primary); }
.tag-desc { font-size: 10px; color: var(--text-tertiary); margin-top: 2px; }
.style-tag.active .tag-name { color: white; }
.style-tag.active .tag-desc { color: rgba(255,255,255,0.8); }

/* 颜色偏好 */
.color-preference { display: flex; gap: 8px; flex-wrap: wrap; }

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

.pref-color:active { transform: scale(0.9); }

.pref-color.active {
  border-color: var(--accent-color);
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(91,154,139,0.3);
}

.pref-color.avoid.active {
  border-color: #ff4d4f;
  box-shadow: 0 2px 8px rgba(255,77,79,0.3);
}

.pref-color.disabled { opacity: 0.3; cursor: not-allowed; }

.pref-color span {
  font-size: 14px;
  font-weight: bold;
  color: white;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

.pref-color.avoid span { color: #ff4d4f; }

/* 版型偏好 */
.fit-options { display: flex; gap: 10px; }

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

.fit-option:active { transform: scale(0.95); }
.fit-option.active { background: var(--primary-gradient); }
.fit-icon { font-size: 24px; }
.fit-name { font-size: 13px; color: var(--text-primary); }
.fit-option.active .fit-name { color: white; }

/* ========== 4. 内容切换区 (Tabs - 吸顶) ========== */
.tabs-wrapper {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--bg-secondary);
  padding: 20px 24px 0;
  transition: box-shadow 0.3s;
}

.tabs-wrapper.sticky {
  box-shadow: 0 2px 12px var(--shadow-color);
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
  background: var(--primary-gradient);
  box-shadow: 0 2px 8px rgba(91,154,139,0.3);
}

.tab-icon { font-size: 14px; }

.tab-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

.tab.active .tab-text { color: white; }

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
  color: white;
}

/* Tab 内容区 */
.tab-content {
  padding: 16px 24px 0;
}

.outfit-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.outfit-item {
  display: flex;
  align-items: center;
  background: var(--bg-card);
  padding: 12px;
  border-radius: 14px;
  box-shadow: 0 2px 8px var(--shadow-color);
  cursor: pointer;
  transition: all 0.2s;
}

.outfit-item:active { transform: scale(0.98); }

.outfit-image {
  position: relative;
  width: 72px;
  height: 72px;
  border-radius: 10px;
  overflow: hidden;
  margin-right: 12px;
  flex-shrink: 0;
}

.outfit-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.outfit-scene {
  position: absolute;
  bottom: 4px;
  left: 4px;
  background: rgba(0,0,0,0.6);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 9px;
}

.outfit-info {
  flex: 1;
  min-width: 0;
}

.outfit-info h4 {
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.outfit-info p {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.outfit-rate {
  font-size: 11px;
  color: var(--accent-color);
}

.outfit-action {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--bg-secondary);
  border: none;
  font-size: 14px;
  cursor: pointer;
  flex-shrink: 0;
  margin-left: 8px;
  transition: all 0.2s;
}

.outfit-action:active { transform: scale(0.9); }

/* 浏览历史 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  background: var(--bg-card);
  padding: 12px;
  border-radius: 12px;
  box-shadow: 0 2px 8px var(--shadow-color);
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:active { background: var(--bg-secondary); }

.history-image {
  width: 52px;
  height: 52px;
  border-radius: 10px;
  overflow: hidden;
  margin-right: 12px;
  flex-shrink: 0;
}

.history-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.history-info { flex: 1; min-width: 0; }

.history-info h4 {
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-info p {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0;
}

.history-arrow {
  font-size: 20px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 24px;
}

.empty-icon { font-size: 48px; display: block; margin-bottom: 12px; }

.empty-state p {
  font-size: 15px;
  color: var(--text-secondary);
}

.empty-hint {
  font-size: 13px !important;
  color: var(--text-tertiary) !important;
  margin-top: 6px;
  margin-bottom: 18px;
}

.go-discover {
  padding: 10px 28px;
  background: var(--primary-gradient);
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

/* ========== 5. 设置区 ========== */
.settings-section {
  padding: 28px 24px 0;
}

.settings-title {
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: 14px;
}

.settings-card {
  background: var(--bg-card);
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 14px;
  box-shadow: 0 1px 4px var(--shadow-color);
}

.settings-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  cursor: pointer;
  transition: background 0.15s;
}

.settings-item:active {
  background: var(--bg-secondary);
}

.settings-item-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.settings-icon {
  width: 28px;
  text-align: center;
  font-size: 18px;
}

.settings-label {
  font-size: 14px;
  color: var(--text-primary);
}

.settings-item-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.settings-arrow {
  font-size: 18px;
  color: var(--text-tertiary);
}

.mini-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: var(--accent-color);
}

.mini-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mini-cover {
  width: 48px;
  height: 32px;
  border-radius: 6px;
  overflow: hidden;
}

.mini-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.settings-divider {
  height: 1px;
  background: var(--border-color);
  margin: 0 16px;
}

.settings-input {
  border: none;
  background: transparent;
  font-size: 13px;
  color: var(--text-secondary);
  text-align: right;
  outline: none;
  min-width: 140px;
}

.settings-input::placeholder {
  color: var(--text-tertiary);
}

/* 性别选项 */
.gender-options {
  display: flex;
  gap: 4px;
}

.gender-btn {
  padding: 6px 14px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: transparent;
  font-size: 12px;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all 0.2s;
}

.gender-btn.active {
  border-color: var(--accent-color);
  background: rgba(91,154,139,0.1);
  color: var(--accent-color);
}

.settings-date {
  border: none;
  background: transparent;
  font-size: 13px;
  color: var(--text-secondary);
  outline: none;
}

/* 退出登录 */
.btn-logout {
  display: block;
  width: calc(100% - 48px);
  margin: 16px auto 0;
  padding: 14px;
  background: var(--bg-card);
  border: 1.5px solid #ff4d4f;
  border-radius: 14px;
  color: #ff4d4f;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:active {
  background: #ff4d4f;
  color: white;
}

/* 底部提示 */
.bottom-hint {
  text-align: center;
  padding: 24px 0 8px;
  font-size: 12px;
  color: var(--text-tertiary);
}

/* ========== 头像大图预览模态框 ========== */
.avatar-modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-modal-mask {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.85);
}

.avatar-modal-content {
  position: relative;
  width: 260px;
  height: 260px;
  border-radius: 50%;
  overflow: hidden;
  z-index: 1;
  box-shadow: 0 8px 40px rgba(0,0,0,0.5);
}

.avatar-modal-content img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-modal-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 80px;
  font-weight: bold;
  color: var(--accent-color);
  background: white;
}

.avatar-modal-close {
  position: fixed;
  top: 24px;
  right: 24px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

/* ========== 取消收藏确认弹窗 ========== */
.confirm-dialog {
  position: fixed;
  inset: 0;
  z-index: 1100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-mask {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.confirm-card {
  position: relative;
  z-index: 1;
  width: 300px;
  background: var(--bg-card);
  border-radius: 20px;
  padding: 28px 24px 20px;
  text-align: center;
  box-shadow: 0 12px 48px rgba(0,0,0,0.25);
  animation: confirmIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes confirmIn {
  from { opacity: 0; transform: scale(0.85) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.confirm-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.confirm-desc {
  font-size: 14px;
  color: var(--text-tertiary);
  line-height: 1.6;
  margin-bottom: 24px;
}

.confirm-actions {
  display: flex;
  gap: 12px;
}

.confirm-btn {
  flex: 1;
  padding: 12px 0;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.confirm-btn:active {
  transform: scale(0.96);
}

.confirm-btn.cancel {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.confirm-btn.confirm {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
}
</style>

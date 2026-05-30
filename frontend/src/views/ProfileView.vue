<template>
  <div class="profile-container" ref="containerRef" @touchstart="onTouchStart" @touchend="onTouchEnd">
    <!-- Cover Section -->
    <CoverSection
      :username="authStore.user?.username || '用户'"
      :avatar-url="userStore.profile.avatar"
      :preview-url="previewUrl"
      :bio="userStore.profile.bio"
      :liked-count="userStore.likedOutfits.length"
      :wardrobe-count="wardrobeStore.clothes.length"
      :history-count="userStore.historyOutfits.length"
      :pull-distance="pullDistance"
      :uploading="uploading"
      @open-avatar-modal="showAvatarModal = true"
      @go-to-settings="goToSettings"
      @go-to-profile-edit="goToProfileEdit"
      @switch-tab="onSwitchTab"
      @avatar-change="onAvatarChange"
    />

    <!-- Body Card Summary -->
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

    <!-- Tabs -->
    <ProfileTabs
      ref="tabsComponent"
      v-model="activeTab"
      :liked-count="userStore.likedOutfits.length"
      :history-count="userStore.historyOutfits.length"
      :is-sticky="isTabSticky"
    />

    <!-- Tab Content -->
    <div class="tab-content">
      <LikedOutfitsPanel
        v-if="activeTab === 'liked'"
        :outfits="userStore.likedOutfits"
        @go-to-detail="goToDetail"
        @confirm-unlike="confirmUnlike"
        @go-home="goHome"
      />
      <HistoryPanel
        v-if="activeTab === 'history'"
        :outfits="userStore.historyOutfits"
        @go-to-detail="goToDetail"
        @go-home="goHome"
      />
    </div>

    <!-- Logout -->
    <button class="btn-logout" @click="handleLogout">退出登录</button>
    <p class="bottom-hint">~ 探索更多穿搭灵感 ~</p>

    <BottomNav />

    <!-- Modals -->
    <AvatarModal
      :visible="showAvatarModal"
      :avatar-url="userStore.profile.avatar"
      :preview-url="previewUrl"
      :username="authStore.user?.username || 'U'"
      @close="showAvatarModal = false"
    />
    <ConfirmDialog
      :visible="!!unlikeTarget"
      @cancel="unlikeTarget = null"
      @confirm="doUnlike"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUserStore } from '../stores/user'
import { useWardrobeStore } from '../stores/wardrobe'
import { useHaptics } from '../composables/useHaptics'
import { validateImage } from '../services/user'
import BottomNav from '../components/BottomNav.vue'
import CoverSection from '../components/profile/CoverSection.vue'
import ProfileTabs from '../components/profile/ProfileTabs.vue'
import LikedOutfitsPanel from '../components/profile/LikedOutfitsPanel.vue'
import HistoryPanel from '../components/profile/HistoryPanel.vue'
import AvatarModal from '../components/profile/AvatarModal.vue'
import ConfirmDialog from '../components/profile/ConfirmDialog.vue'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const wardrobeStore = useWardrobeStore()
const { trigger } = useHaptics()

const uploading = ref(false)
const previewUrl = ref('')
const activeTab = ref('liked')
const showAvatarModal = ref(false)
const unlikeTarget = ref(null)
const isTabSticky = ref(false)
const tabsComponent = ref(null)
const containerRef = ref(null)
const pullDistance = ref(0)

// ---- Computed ----
const hasCompleteProfile = computed(() =>
  userStore.profile.skinTone && userStore.profile.bodyShape && userStore.profile.styleTags.length > 0
)

const bmiClass = computed(() => {
  const bmi = userStore.calculatedBMI
  if (!bmi) return ''
  if (bmi < 18.5) return 'bmi-low'
  if (bmi < 24) return 'bmi-normal'
  if (bmi < 28) return 'bmi-high'
  return 'bmi-obese'
})

// ---- Lookup helpers ----
const skinTones = [
  { id: 'fair_cool', color: '#fce4d6' }, { id: 'fair_warm', color: '#ffe4c4' },
  { id: 'medium', color: '#deb887' }, { id: 'tan', color: '#d2a679' }, { id: 'dark', color: '#8b5a2b' }
]
const bodyShapes = [
  { id: 'inverted_triangle', name: '倒三角' }, { id: 'rectangle', name: '矩形' },
  { id: 'pear', name: '梨型' }, { id: 'hourglass', name: '沙漏' }, { id: 'apple', name: '苹果' }
]
const styleTags = [
  { id: 'old_money', name: 'Old Money' }, { id: 'intellectual', name: '高智感' },
  { id: 'dopamine', name: '多巴胺' }, { id: 'american_vintage', name: '美式复古' },
  { id: 'y2k', name: 'Y2K' }, { id: 'clean_fit', name: 'Clean Fit' },
  { id: 'athleisure', name: 'Athleisure' }, { id: 'normcore', name: 'Normcore' },
  { id: 'gorpcore', name: 'Gorpcore' }, { id: 'japanese', name: '日系风格' },
  { id: 'streetwear', name: '街头潮流' }, { id: 'korean', name: '韩系风格' }
]

const getSkinColor = (id) => skinTones.find(t => t.id === id)?.color || '#deb887'
const getSeasonName = (id) => ({ fair_cool: '夏季人', fair_warm: '春季人', medium: '秋季人', tan: '秋季人', dark: '深冬人' }[id] || '未知')
const getBodyShapeName = (id) => bodyShapes.find(b => b.id === id)?.name || ''
const getStyleTagName = (id) => styleTags.find(t => t.id === id)?.name || id

// ---- Lifecycle ----
onMounted(async () => {
  authStore.checkAuth()
  if (!authStore.isAuthenticated) { router.push('/login'); return }
  await wardrobeStore.refreshWardrobe()
  userStore.loadProfile()
  window.addEventListener('scroll', onScroll)
  containerRef.value?.addEventListener('touchmove', onTouchMove, { passive: false })
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  containerRef.value?.removeEventListener('touchmove', onTouchMove)
})

// ---- Scroll / Pull ----
let pullTimer = null
const onScroll = () => {
  const sy = window.scrollY
  if (sy < 0) {
    pullDistance.value = Math.min(Math.abs(sy) * 0.6, 100)
  } else if (pullDistance.value > 0 && sy >= 0 && !isPulling) {
    clearTimeout(pullTimer)
    pullTimer = setTimeout(() => { pullDistance.value = 0 }, 80)
  }
  const tabsEl = tabsComponent.value?.tabsRef
  if (tabsEl) {
    const rect = tabsEl.getBoundingClientRect()
    isTabSticky.value = rect.top <= 0
  }
}

let touchStartY = 0
let isPulling = false
const onTouchStart = (e) => {
  if (window.scrollY <= 0) { touchStartY = e.touches[0].clientY; isPulling = false }
}
const onTouchMove = (e) => {
  if (window.scrollY > 0 || !touchStartY) return
  const delta = e.touches[0].clientY - touchStartY
  if (delta > 10) {
    if (delta > 0) e.preventDefault()
    isPulling = true
    pullDistance.value = Math.min(delta * 0.45, 100)
  }
}
const onTouchEnd = () => {
  if (isPulling) {
    setTimeout(() => { touchStartY = 0; isPulling = false; pullDistance.value = 0 }, 50)
  } else {
    touchStartY = 0; isPulling = false; pullDistance.value = 0
  }
}

// ---- Event handlers ----
const onSwitchTab = (tab) => {
  activeTab.value = tab
  tabsComponent.value?.tabsRef?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const onAvatarChange = async (file) => {
  uploading.value = true
  previewUrl.value = URL.createObjectURL(file)
  try {
    await userStore.updateAvatar(file)
    trigger('light')
  } catch { /* handled by store */ }
  finally { uploading.value = false }
}

const goToDetail = (outfit) => { trigger('light'); router.push(`/outfit/${outfit.id}`) }
const goHome = () => { trigger('light'); router.push('/home') }
const confirmUnlike = (outfit) => { trigger('light'); unlikeTarget.value = outfit }
const doUnlike = () => { trigger('medium'); userStore.unlikeOutfit(unlikeTarget.value.id); unlikeTarget.value = null }
const handleLogout = () => { trigger('medium'); authStore.logout(); router.push('/login') }
const goToSettings = () => { trigger('light'); router.push('/profile/settings') }
const goToProfileEdit = () => { trigger('light'); router.push('/profile/edit') }
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 100px;
  overscroll-behavior: none;
}

/* Body card summary (display only) */
.body-card-section { padding: 12px 24px 0; }

.body-card {
  background: var(--bg-card);
  border-radius: 18px;
  border: 1px solid var(--hairline);
  padding: 20px;
}

.body-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.body-card-header h3 {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.374px;
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

.body-summary { display: flex; flex-direction: column; gap: 8px; }

.summary-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.summary-icon { width: 22px; text-align: center; }

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
  border: 2px solid var(--hairline);
  margin-left: 4px;
}

.summary-tags { display: flex; flex-wrap: wrap; gap: 4px; }

.mini-tag {
  font-size: 10px;
  padding: 2px 8px;
  background: rgba(0,102,204,0.1);
  color: var(--accent-color);
  border-radius: 6px;
}

.mini-tag.more { background: var(--bg-secondary); color: var(--text-tertiary); }
.body-hint { font-size: 12px; color: var(--text-tertiary); margin-top: 4px; }

/* Tab content wrapper */
.tab-content { padding: 16px 24px 0; }

/* Logout */
.btn-logout {
  display: block;
  width: calc(100% - 48px);
  margin: 16px auto 0;
  padding: 14px;
  background: var(--bg-card);
  border: 1.5px solid #ff4d4f;
  border-radius: 18px;
  color: #ff4d4f;
  font-size: 14px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:active { background: #ff4d4f; color: var(--on-primary); }

.bottom-hint {
  text-align: center;
  padding: 24px 0 8px;
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>

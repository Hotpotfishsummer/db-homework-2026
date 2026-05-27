<template>
  <div class="cover-section">
    <div class="cover-bg" :style="coverStyle" ref="coverBgRef">
      <!-- Gradient overlays -->
      <div class="cover-blur-top"></div>
      <div class="cover-blur-bottom"></div>

      <!-- Avatar -->
      <div class="avatar-wrapper" @click="$emit('openAvatarModal')">
        <div class="avatar-ring">
          <div class="avatar">
            <img v-if="previewUrl || avatarUrl" :src="previewUrl || avatarUrl" alt="avatar" />
            <span v-else class="avatar-placeholder">{{ initial }}</span>
            <div v-if="uploading" class="avatar-overlay">
              <div class="spinner"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Username + membership -->
      <div class="cover-user-info">
        <h2 class="cover-username">{{ username }}</h2>
        <p class="cover-membership">AI 穿搭会员</p>
      </div>

      <!-- Settings button -->
      <button class="btn-settings" @click="$emit('goToSettings')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="gear-icon">
          <circle cx="12" cy="12" r="3"/>
          <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
        </svg>
      </button>
    </div>
    <input ref="coverInput" type="file" accept="image/jpeg,image/png" hidden @change="onCoverChange" />
    <input ref="fileInput" type="file" accept="image/jpeg,image/png" hidden @change="onFileChange" />

    <!-- Bio bar -->
    <div class="bio-bar">
      <div class="stats-inline">
        <span class="stat-inline-item" @click="$emit('switchTab', 'liked')">❤️ 收藏&nbsp;{{ likedCount }}</span>
        <span class="stat-inline-sep">·</span>
        <span class="stat-inline-item">👕 衣橱&nbsp;{{ wardrobeCount }}</span>
        <span class="stat-inline-sep">·</span>
        <span class="stat-inline-item" @click="$emit('switchTab', 'history')">🕐 浏览&nbsp;{{ historyCount }}</span>
      </div>

      <div class="bio-row">
        <p class="bio-text" v-if="bio">"{{ bio }}"</p>
        <p v-else class="bio-text placeholder">写下一句话穿搭宣言...</p>
        <button class="btn-edit-profile" @click="$emit('goToProfileEdit')">完善档案</button>
      </div>

      <p v-if="uploadError" class="upload-error">{{ uploadError }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import { useHaptics } from '../../composables/useHaptics'
import { validateImage } from '../../services/user'

const props = defineProps({
  username: { type: String, default: '用户' },
  avatarUrl: { type: String, default: '' },
  previewUrl: { type: String, default: '' },
  bio: { type: String, default: '' },
  likedCount: { type: Number, default: 0 },
  wardrobeCount: { type: Number, default: 0 },
  historyCount: { type: Number, default: 0 },
  pullDistance: { type: Number, default: 0 },
  uploading: { type: Boolean, default: false }
})

const emit = defineEmits(['openAvatarModal', 'goToSettings', 'goToProfileEdit', 'switchTab', 'avatarChange', 'coverChange', 'update:uploading', 'update:uploadError'])

const userStore = useUserStore()
const { trigger } = useHaptics()

const fileInput = ref(null)
const coverInput = ref(null)
const coverBgRef = ref(null)
const uploadError = ref('')

const initial = computed(() => props.username?.charAt(0)?.toUpperCase() || 'U')

const baseCoverHeight = 240
const coverStyle = computed(() => {
  const h = baseCoverHeight + props.pullDistance
  const style = { height: h + 'px' }
  if (userStore.profile.coverImage) {
    style.backgroundImage = `url(${userStore.profile.coverImage})`
    style.backgroundSize = 'cover'
    style.backgroundPosition = 'center'
  } else {
    style.background = 'var(--surface-black)'
  }
  return style
})

const onFileChange = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  const validation = validateImage(file)
  if (!validation.valid) {
    uploadError.value = validation.error
    return
  }
  uploadError.value = ''
  emit('avatarChange', file)
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

defineExpose({ coverBgRef })
</script>

<style scoped>
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
  font-weight: 600;
  letter-spacing: -0.374px;
  color: var(--on-primary);
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
  font-weight: 600;
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
  border: 2px solid var(--on-primary);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

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
  color: var(--on-primary);
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

.bio-bar {
  background: var(--bg-card);
  padding: 10px 24px 14px 118px;
  min-height: 50px;
}

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
  font-weight: 400;
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
  border-radius: 9999px;
  background: transparent;
  color: var(--accent-color);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit-profile:active {
  background: var(--accent-color);
  color: var(--on-primary);
}
</style>

<template>
  <div class="settings-container">
    <div class="page-nav">
      <button class="nav-back" @click="goBack">←</button>
      <h1>设置</h1>
      <span></span>
    </div>

    <div class="settings-content">
      <!-- 分区1: 头像 & 背景图 -->
      <div class="settings-card">
        <div class="settings-item" @click="triggerAvatarUpload">
          <div class="settings-item-left">
            <span class="settings-icon">👤</span>
            <span class="settings-label">切换头像</span>
          </div>
          <div class="settings-item-right">
            <div class="mini-avatar">
              <img v-if="previewUrl || userStore.profile.avatar" :src="previewUrl || userStore.profile.avatar" alt="" />
              <span v-else>{{ authStore.user?.username?.charAt(0)?.toUpperCase() || 'U' }}</span>
            </div>
            <span class="settings-arrow">›</span>
          </div>
        </div>
        <div class="settings-divider"></div>
        <div class="settings-item" @click="triggerCoverUpload">
          <div class="settings-item-left">
            <span class="settings-icon">🖼️</span>
            <span class="settings-label">设置背景图</span>
          </div>
          <div class="settings-item-right">
            <div class="mini-cover" v-if="userStore.profile.coverImage">
              <img :src="userStore.profile.coverImage" alt="" />
            </div>
            <span class="settings-arrow">›</span>
          </div>
        </div>
      </div>
      <input ref="fileInput" type="file" accept="image/jpeg,image/png" hidden @change="onFileChange" />
      <input ref="coverInput" type="file" accept="image/jpeg,image/png" hidden @change="onCoverChange" />

      <!-- 分区2: 个性签名 & 性别 & 生日 -->
      <div class="settings-card">
        <div class="settings-item">
          <div class="settings-item-left">
            <span class="settings-icon">✍️</span>
            <span class="settings-label">个性签名</span>
          </div>
          <div class="settings-item-right">
            <input
              type="text"
              v-model="bioInput"
              placeholder="写下你的穿搭宣言"
              class="settings-input"
              maxlength="50"
            />
          </div>
        </div>
        <div class="settings-divider"></div>
        <div class="settings-item">
          <div class="settings-item-left">
            <span class="settings-icon">⚧</span>
            <span class="settings-label">性别</span>
          </div>
          <div class="settings-item-right">
            <div class="gender-options">
              <button
                v-for="g in genderOptions" :key="g.value"
                class="gender-btn"
                :class="{ active: localGender === g.value }"
                @click="selectGender(g.value)"
              >{{ g.label }}</button>
            </div>
          </div>
        </div>
        <div class="settings-divider"></div>
        <div class="settings-item">
          <div class="settings-item-left">
            <span class="settings-icon">🎂</span>
            <span class="settings-label">生日</span>
          </div>
          <div class="settings-item-right">
            <input
              type="text"
              v-model="birthdayInput"
              placeholder="请输入生日，如 2000-01-01"
              class="settings-input"
            />
          </div>
        </div>
      </div>

      <!-- 主题切换 -->
      <div class="settings-card">
        <div class="settings-item" @click="toggleTheme">
          <div class="settings-item-left">
            <span class="settings-icon">{{ themeStore.isDark ? '☀️' : '🌙' }}</span>
            <span class="settings-label">{{ themeStore.isDark ? '浅色模式' : '深色模式' }}</span>
          </div>
          <div class="settings-item-right">
            <span class="settings-arrow">›</span>
          </div>
        </div>
      </div>

      <p v-if="uploadError" class="upload-error">{{ uploadError }}</p>

      <!-- 确认修改 -->
      <button class="btn-confirm" :class="{ saved: saved }" @click="confirmSave">
        {{ saved ? '✓ 已保存' : '确认修改' }}
      </button>

      <!-- 退出登录 -->
      <button class="btn-logout" @click="handleLogout">退出登录</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUserStore } from '../stores/user'
import { useThemeStore } from '../stores/theme'
import { useHaptics } from '../composables/useHaptics'
import { validateImage } from '../services/user'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const themeStore = useThemeStore()
const { trigger } = useHaptics()

const uploading = ref(false)
const uploadError = ref('')
const previewUrl = ref('')
const fileInput = ref(null)
const coverInput = ref(null)
const bioInput = ref('')
const birthdayInput = ref('')
const localGender = ref(null)
const saved = ref(false)

const genderOptions = [
  { value: 'male', label: '男' },
  { value: 'female', label: '女' },
  { value: 'other', label: '其他' }
]

onMounted(() => {
  authStore.checkAuth()
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  userStore.loadProfile()
  bioInput.value = userStore.profile.bio || ''
  birthdayInput.value = userStore.profile.birthday || ''
  localGender.value = userStore.profile.gender
})

const goBack = () => { trigger('light'); router.back() }

const triggerAvatarUpload = () => { fileInput.value?.click() }

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

const triggerCoverUpload = () => { coverInput.value?.click() }

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

const selectGender = (val) => { trigger('light'); localGender.value = localGender.value === val ? null : val }
const toggleTheme = () => { trigger('light'); themeStore.toggle() }
const handleLogout = () => { trigger('medium'); authStore.logout(); router.push('/login') }

const confirmSave = () => {
  trigger('medium')
  userStore.updateProfile({
    bio: bioInput.value,
    gender: localGender.value,
    birthday: birthdayInput.value
  })
  saved.value = true
  setTimeout(() => { saved.value = false; router.back() }, 600)
}
</script>

<style scoped>
.settings-container {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 40px;
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

.settings-content {
  padding: 20px 24px;
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
  font-family: 'KaiTi', 'STKaiti', 'Georgia', 'Times New Roman', serif;
  font-size: 13px;
  color: var(--text-secondary);
  text-align: right;
  outline: none;
  min-width: 140px;
}

.settings-input::placeholder {
  color: var(--text-tertiary);
}

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

.btn-confirm {
  display: block;
  width: 100%;
  margin-top: 16px;
  padding: 14px;
  background: var(--primary-gradient);
  border: none;
  border-radius: 14px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-confirm:active {
  opacity: 0.85;
  transform: scale(0.98);
}

.btn-confirm.saved {
  background: #52c41a;
}

.upload-error {
  text-align: center;
  color: #ff4d4f;
  font-size: 12px;
  margin-bottom: 12px;
}

.btn-logout {
  display: block;
  width: 100%;
  margin-top: 16px;
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
</style>

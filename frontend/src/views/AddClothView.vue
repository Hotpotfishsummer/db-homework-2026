<template>
  <div class="add-cloth-page">
    <div class="page-header">
      <button class="nav-back" @click="goBack">←</button>
      <h1>录入新单品</h1>
      <button class="save-btn" @click="saveCloth" :disabled="!canSave">保存</button>
    </div>

    <div class="form-content">
      <!-- 图片上传区域 -->
      <div class="image-upload" @click="triggerUpload">
        <img v-if="previewImage" :src="previewImage" class="preview-image" />
        <div v-else class="upload-placeholder">
          <div class="upload-options">
            <div class="upload-option" @click.stop="openCamera">
              <span class="option-icon">📷</span>
              <span>拍照</span>
            </div>
            <div class="upload-divider">或</div>
            <div class="upload-option">
              <span class="option-icon">🖼️</span>
              <span>从相册选择</span>
            </div>
          </div>
        </div>
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          capture="environment"
          @change="handleFileSelect"
          style="display: none"
        />
        <input
          ref="galleryInput"
          type="file"
          accept="image/*"
          @change="handleFileSelect"
          style="display: none"
        />
      </div>

      <!-- 衣服名称 -->
      <div class="form-group">
        <label>衣服名称</label>
        <input
          v-model="clothName"
          type="text"
          placeholder="例如：白色基础款T恤"
          class="form-input"
        />
      </div>

      <!-- 分类选择 -->
      <div class="form-group">
        <label>分类</label>
        <div class="category-grid">
          <div
            v-for="cat in categories"
            :key="cat.id"
            class="category-item"
            :class="{ active: selectedCategory === cat.id }"
            @click="selectedCategory = cat.id"
          >
            <span class="cat-icon">{{ cat.icon }}</span>
            <span class="cat-name">{{ cat.name }}</span>
          </div>
        </div>
      </div>

      <!-- 颜色选择 -->
      <div class="form-group">
        <label>主色调</label>
        <div class="color-grid">
          <div
            v-for="color in colors"
            :key="color.value"
            class="color-item"
            :class="{ active: selectedColor === color.value }"
            :style="{ background: color.value }"
            @click="selectedColor = color.value"
          >
            <span v-if="selectedColor === color.value" class="check-mark">✓</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useWardrobeStore } from '../stores/wardrobe'
import { useHaptics } from '../composables/useHaptics'

const router = useRouter()
const wardrobeStore = useWardrobeStore()
const { trigger } = useHaptics()

const fileInput = ref(null)
const galleryInput = ref(null)
const previewImage = ref('')
const clothName = ref('')
const selectedCategory = ref('top')
const selectedColor = ref('#ffffff')

const categories = [
  { id: 'top', name: '上装', icon: '👕' },
  { id: 'bottom', name: '下装', icon: '👖' },
  { id: 'shoes', name: '鞋靴', icon: '👟' },
  { id: 'accessory', name: '配饰', icon: '💍' },
  { id: 'bag', name: '包包', icon: '👜' }
]

const colors = [
  { name: '白色', value: '#ffffff' },
  { name: '黑色', value: '#1a1a1a' },
  { name: '灰色', value: '#9ca3af' },
  { name: '红色', value: '#ef4444' },
  { name: '粉色', value: '#ec4899' },
  { name: '橙色', value: '#f97316' },
  { name: '黄色', value: '#eab308' },
  { name: '绿色', value: '#22c55e' },
  { name: '蓝色', value: '#3b82f6' },
  { name: '紫色', value: '#8b5cf6' },
  { name: '棕色', value: '#92400e' },
  { name: '卡其', value: '#d4a574' }
]

const canSave = computed(() => {
  return clothName.value.trim() && (previewImage.value || selectedColor.value)
})

const goBack = () => {
  router.back()
}

const triggerUpload = () => {
  galleryInput.value?.click()
}

const openCamera = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    trigger('light')
    const reader = new FileReader()
    reader.onload = (e) => {
      previewImage.value = e.target?.result
    }
    reader.readAsDataURL(file)
  }
}

const saveCloth = () => {
  if (!canSave.value) return

  trigger('success')

  // 生成随机图片 URL（模拟真实场景）
  const randomImage = `https://picsum.photos/200?random=${Date.now()}`

  wardrobeStore.addCloth({
    name: clothName.value,
    category: selectedCategory.value,
    color: selectedColor.value,
    image: previewImage.value || randomImage,
    status: 'available'
  })

  router.push('/wardrobe')
}
</script>

<style scoped>
.add-cloth-page {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 40px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 50px 24px 16px;
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

.page-header h1 {
  font-size: 21px;
  color: var(--text-primary);
  font-weight: 600;
  letter-spacing: 0.231px;
}

.save-btn {
  padding: 8px 16px;
  background: var(--accent-color);
  color: var(--on-primary);
  border: none;
  border-radius: 9999px;
  font-size: 14px;
  cursor: pointer;
  transition: transform 0.2s;
}

.save-btn:active {
  transform: scale(0.95);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-content {
  padding: 20px 24px;
}

.image-upload {
  width: 100%;
  aspect-ratio: 1;
  max-height: 300px;
  background: var(--surface-pearl);
  border-radius: 18px;
  border: none;
  overflow: hidden;
  cursor: pointer;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.upload-placeholder {
  padding: 40px;
}

.upload-options {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.upload-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-option:active {
  transform: scale(0.95);
  background: var(--border-color);
}

.option-icon {
  font-size: 32px;
}

.upload-option span:last-child {
  font-size: 13px;
  color: var(--text-secondary);
}

.upload-divider {
  font-size: 14px;
  color: var(--text-tertiary);
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

.form-input {
  width: 100%;
  padding: 12px 20px;
  background: var(--bg-card);
  border: 1px solid var(--hairline);
  border-radius: 9999px;
  font-size: 17px;
  color: var(--text-primary);
  transition: border-color 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.form-input::placeholder {
  color: var(--text-tertiary);
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 8px;
  background: var(--bg-card);
  border-radius: 18px;
  cursor: pointer;
  transition: all 0.2s;
}

.category-item:active {
  transform: scale(0.95);
}

.category-item.active {
  background: var(--accent-color);
}

.cat-icon {
  font-size: 24px;
}

.cat-name {
  font-size: 11px;
  color: var(--text-secondary);
}

.category-item.active .cat-name {
  color: var(--on-primary);
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
}

.color-item {
  aspect-ratio: 1;
  border-radius: 50%;
  border: 2px solid var(--border-color);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.color-item:active {
  transform: scale(0.9);
}

.color-item.active {
  border-color: var(--accent-color);
  border-width: 3px;
  transform: scale(1.1);
}

.check-mark {
  color: var(--accent-color);
  font-size: 14px;
  font-weight: bold;
  text-shadow: 0 0 2px white;
}

.color-item[style*="background: rgb(255, 255, 255)"] .check-mark,
.color-item[style*="background: #ffffff"] .check-mark {
  color: #666;
  text-shadow: none;
}
</style>
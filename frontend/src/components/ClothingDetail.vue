<template>
  <div class="detail-overlay" @click="$emit('close')">
    <div class="detail-card" @click.stop>
      <button class="close-btn" @click="$emit('close')">✕</button>

      <div class="detail-image">
        <img :src="cloth.image" :alt="cloth.name" />
      </div>

      <div class="detail-info">
        <h2>{{ cloth.name }}</h2>
        <div class="detail-tags">
          <span class="tag">{{ getCategoryName(cloth.category) }}</span>
          <span class="tag" :class="cloth.status">{{ getStatusText(cloth.status) }}</span>
        </div>

        <div class="ai-suggestion">
          <div class="suggestion-header">
            <span class="ai-icon">🤖</span>
            <span>AI 搭配建议</span>
          </div>
          <p class="suggestion-text">
            这件{{ cloth.name }}可以搭配你的「黑色阔腿裤」和「小白鞋」，
            打造简约通勤风格。
          </p>
        </div>

        <div class="detail-actions">
          <button class="btn-secondary" @click="toggleStatus">
            {{ cloth.status === 'available' ? '标记清洗' : '取消标记' }}
          </button>
          <button class="btn-danger" @click="deleteCloth">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useWardrobeStore } from '../stores/wardrobe'
import { useHaptics } from '../composables/useHaptics'

const props = defineProps({
  cloth: Object
})

const emit = defineEmits(['close'])

const wardrobeStore = useWardrobeStore()
const { trigger } = useHaptics()

const getCategoryName = (category) => {
  const cat = wardrobeStore.categories.find(c => c.id === category)
  return cat ? cat.name : category
}

const getStatusText = (status) => {
  return status === 'available' ? '可用' : '清洗中'
}

const toggleStatus = () => {
  trigger('light')
  const newStatus = props.cloth.status === 'available' ? 'washing' : 'available'
  wardrobeStore.updateClothStatus(props.cloth.id, newStatus)
  emit('close')
}

const deleteCloth = () => {
  trigger('error')
  wardrobeStore.removeCloth(props.cloth.id)
  emit('close')
}
</script>

<style scoped>
.detail-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 300;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.detail-card {
  width: 100%;
  max-width: 500px;
  max-height: 85vh;
  background: var(--bg-card);
  border-radius: 24px 24px 0 0;
  overflow: hidden;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  font-size: 16px;
  cursor: pointer;
  z-index: 10;
}

.detail-image {
  width: 100%;
  height: 300px;
  background: var(--bg-secondary);
}

.detail-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.detail-info {
  padding: 24px;
}

.detail-info h2 {
  font-size: 20px;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.detail-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.tag {
  padding: 6px 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.tag.washing {
  background: #fff7e6;
  color: #fa8c16;
}

.ai-suggestion {
  background: var(--primary-gradient);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 24px;
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-weight: 600;
  margin-bottom: 8px;
}

.ai-icon {
  font-size: 18px;
}

.suggestion-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.detail-actions {
  display: flex;
  gap: 12px;
}

.detail-actions button {
  flex: 1;
  padding: 14px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: var(--bg-secondary);
  border: none;
  color: var(--text-secondary);
}

.btn-secondary:active {
  background: var(--border-color);
}

.btn-danger {
  background: var(--bg-card);
  border: 2px solid #ff4d4f;
  color: #ff4d4f;
}

.btn-danger:active {
  background: #ff4d4f;
  color: white;
}
</style>
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

        <section class="meta-section">
          <h3>基础信息</h3>
          <div class="meta-grid">
            <div class="meta-item">
              <span class="meta-label">原始文件名</span>
              <span class="meta-value">{{ cloth.sourceFilename || cloth.originalName || cloth.name }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">颜色</span>
              <span class="meta-value">{{ cloth.color || '未识别' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">图片格式</span>
              <span class="meta-value">{{ cloth.format || 'webp' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">图片地址</span>
              <span class="meta-value meta-path">{{ cloth.publicUrl || cloth.image }}</span>
            </div>
          </div>
        </section>

        <section class="meta-section" v-if="hasAnalysis">
          <h3>AI 识别结果</h3>
          <div class="tag-cloud">
            <span v-for="season in toArray(cloth.analysis?.season)" :key="`season-${season}`" class="chip">季节：{{ season }}</span>
            <span v-for="feature in toArray(cloth.analysis?.style_features)" :key="`feature-${feature}`" class="chip">风格：{{ feature }}</span>
            <span v-for="material in toArray(cloth.analysis?.materials)" :key="`material-${material}`" class="chip">材质：{{ material }}</span>
            <span v-if="cloth.analysis?.pattern" class="chip">图案：{{ cloth.analysis.pattern }}</span>
            <span v-if="cloth.analysis?.fit" class="chip">版型：{{ cloth.analysis.fit }}</span>
            <span v-if="cloth.analysis?.thickness" class="chip">厚度：{{ cloth.analysis.thickness }}</span>
            <span v-if="cloth.analysis?.warmth !== undefined && cloth.analysis?.warmth !== null" class="chip">保暖：{{ formatRatio(cloth.analysis.warmth) }}</span>
            <span v-if="cloth.analysis?.cooling !== undefined && cloth.analysis?.cooling !== null" class="chip">透气：{{ formatRatio(cloth.analysis.cooling) }}</span>
          </div>
          <p class="analysis-summary">{{ cloth.analysis?.summary || '暂无识别摘要' }}</p>
        </section>

        <section class="meta-section" v-if="hasDetection">
          <h3>检测信息</h3>
          <div class="meta-grid">
            <div class="meta-item">
              <span class="meta-label">是否检测到衣物</span>
              <span class="meta-value">{{ cloth.detection?.contains_garment ? '是' : '否' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">置信度</span>
              <span class="meta-value">{{ formatRatio(cloth.detection?.confidence) }}</span>
            </div>
          </div>
          <p class="analysis-summary">{{ cloth.detection?.description || '暂无检测描述' }}</p>
        </section>

        <section class="meta-section" v-if="cloth.tags && cloth.tags.length > 0">
          <h3>标签</h3>
          <div class="tag-cloud">
            <span v-for="tag in cloth.tags" :key="tag" class="chip">{{ tag }}</span>
          </div>
        </section>

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
import { watch, onBeforeUnmount } from 'vue'
import { useWardrobeStore } from '../stores/wardrobe'
import { useHaptics } from '../composables/useHaptics'

const props = defineProps({
  cloth: Object
})

const emit = defineEmits(['close'])

const wardrobeStore = useWardrobeStore()
const { trigger } = useHaptics()

const lockBodyScroll = () => {
  document.body.style.overflow = 'hidden'
}

const unlockBodyScroll = () => {
  document.body.style.overflow = ''
}

watch(
  () => !!props.cloth,
  (isOpen) => {
    if (isOpen) {
      lockBodyScroll()
    } else {
      unlockBodyScroll()
    }
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  unlockBodyScroll()
})

const hasAnalysis = Array.isArray(props.cloth?.analysis?.tags)
  || Array.isArray(props.cloth?.analysis?.materials)
  || Array.isArray(props.cloth?.analysis?.season)
  || Array.isArray(props.cloth?.analysis?.style_features)
  || !!props.cloth?.analysis?.summary

const hasDetection = !!props.cloth?.detection

const getCategoryName = (category) => {
  const cat = wardrobeStore.categories.find(c => c.id === category)
  return cat ? cat.name : category
}

const getStatusText = (status) => {
  return status === 'available' ? '可用' : '清洗中'
}

const toArray = (value) => {
  if (!value) return []
  return Array.isArray(value) ? value : [value]
}

const formatRatio = (value) => {
  if (value === undefined || value === null || Number.isNaN(Number(value))) {
    return '未提供'
  }
  const numberValue = Number(value)
  return numberValue > 1 ? `${numberValue}` : `${Math.round(numberValue * 100)}%`
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
  overscroll-behavior: contain;
}

.detail-card {
  width: 100%;
  max-width: 500px;
  max-height: 85vh;
  background: var(--bg-card);
  border-radius: 18px 18px 0 0;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
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
  font-size: 21px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  letter-spacing: 0.231px;
}

.detail-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.meta-section {
  margin-bottom: 20px;
}

.meta-section h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.meta-item {
  padding: 12px;
  border-radius: 12px;
  background: var(--bg-secondary);
}

.meta-label {
  display: block;
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: 6px;
}

.meta-value {
  display: block;
  font-size: 13px;
  color: var(--text-primary);
  word-break: break-word;
}

.meta-path {
  font-size: 12px;
  color: var(--text-secondary);
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  display: inline-flex;
  align-items: center;
  padding: 8px 10px;
  border-radius: 9999px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 12px;
}

.analysis-summary {
  margin-top: 10px;
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-secondary);
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
  background: var(--accent-color);
  border-radius: 18px;
  padding: 16px;
  margin-bottom: 24px;
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--on-primary);
  font-weight: 600;
  margin-bottom: 8px;
}

.ai-icon {
  font-size: 18px;
}

.suggestion-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  line-height: 1.43;
  margin: 0;
  letter-spacing: -0.224px;
}

.detail-actions {
  display: flex;
  gap: 12px;
}

.detail-actions button {
  flex: 1;
  padding: 11px 22px;
  border-radius: 9999px;
  font-size: 17px;
  font-weight: 400;
  cursor: pointer;
  transition: transform 0.2s;
}

.detail-actions button:active {
  transform: scale(0.95);
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
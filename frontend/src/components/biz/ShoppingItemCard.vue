<template>
  <div class="shopping-item-card" :class="{ 'is-dismissed': item.status === 'dismissed', 'is-bought': item.status === 'bought' }">
    <div class="card-image" :style="{ background: colorBlock }">
      <span class="category-emoji">{{ categoryEmoji }}</span>
      <div class="priority-badge" v-if="item.priority >= 80">⭐ 推荐</div>
    </div>
    <div class="card-body">
      <div class="card-header">
        <h4 class="item-name">{{ item.name }}</h4>
        <span class="category-tag" :data-cat="item.category">{{ categoryLabel }}</span>
      </div>
      <div class="meta-row">
        <span v-if="item.color" class="meta-chip">🎨 {{ item.color }}</span>
        <span v-if="item.price_range" class="meta-chip price">💰 {{ item.price_range }}</span>
      </div>
      <div v-if="item.style_tags && item.style_tags.length" class="tags-row">
        <span v-for="tag in item.style_tags.slice(0, 4)" :key="tag" class="style-tag">{{ tag }}</span>
      </div>
      <p class="reason-text">💡 {{ item.reason }}</p>
      <div class="card-actions">
        <button
          class="btn-action btn-dismiss"
          :disabled="item.status === 'dismissed'"
          @click="$emit('dismiss', item)"
        >
          <span>❌</span>
          <span>{{ item.status === 'dismissed' ? '已忽略' : '不需要' }}</span>
        </button>
        <button
          v-if="item.purchase_url"
          class="btn-action btn-link"
          @click="openLink"
        >
          <span>🔗</span>
          <span>购买</span>
        </button>
        <button
          class="btn-action btn-bought"
          :disabled="item.status === 'bought'"
          @click="$emit('bought', item)"
        >
          <span>✅</span>
          <span>{{ item.status === 'bought' ? '已买' : '已购买' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
})

defineEmits(['bought', 'dismiss'])

const CATEGORY_META = {
  top: { emoji: '👕', label: '上装', color: '#a8d8ea' },
  bottom: { emoji: '👖', label: '下装', color: '#aa96da' },
  outerwear: { emoji: '🧥', label: '外套', color: '#fcbad3' },
  shoes: { emoji: '👟', label: '鞋履', color: '#ffffd2' },
  accessory: { emoji: '🕶️', label: '配饰', color: '#ffd3b6' },
  bag: { emoji: '👜', label: '包包', color: '#d4a5a5' },
  other: { emoji: '👔', label: '其他', color: '#e0e0e0' },
}

const categoryEmoji = computed(() => CATEGORY_META[props.item.category]?.emoji || '👔')
const categoryLabel = computed(() => CATEGORY_META[props.item.category]?.label || '其他')

const colorBlock = computed(() => {
  // Use the item's declared color as a tint for the visual placeholder
  const base = CATEGORY_META[props.item.category]?.color || '#e0e0e0'
  return `linear-gradient(135deg, ${base} 0%, #ffffff 100%)`
})

function openLink() {
  if (props.item.purchase_url) {
    window.open(props.item.purchase_url, '_blank', 'noopener,noreferrer')
  }
}
</script>

<style scoped>
.shopping-item-card {
  background: var(--surface-card, #ffffff);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  transition: opacity 0.2s, transform 0.2s;
}

.shopping-item-card.is-dismissed {
  opacity: 0.5;
}

.shopping-item-card.is-bought {
  opacity: 0.7;
  border: 2px solid #4caf50;
}

.card-image {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.category-emoji {
  font-size: 56px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.priority-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #ff6b6b;
  color: white;
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 10px;
  font-weight: 600;
}

.card-body {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.item-name {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #1a1a1a);
  flex: 1;
  line-height: 1.3;
}

.category-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 8px;
  background: #f0f0f0;
  color: #555;
  white-space: nowrap;
}

.meta-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.meta-chip {
  font-size: 12px;
  color: var(--text-secondary, #666);
  background: #f8f8f8;
  padding: 2px 8px;
  border-radius: 8px;
}

.meta-chip.price {
  background: #fff3e0;
  color: #e65100;
}

.tags-row {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.style-tag {
  font-size: 11px;
  color: #5e35b1;
  background: #ede7f6;
  padding: 2px 8px;
  border-radius: 8px;
}

.reason-text {
  font-size: 12px;
  color: var(--text-secondary, #666);
  line-height: 1.5;
  margin: 4px 0 0;
  flex: 1;
}

.card-actions {
  display: flex;
  gap: 6px;
  margin-top: 8px;
}

.btn-action {
  flex: 1;
  background: #f5f5f5;
  border: none;
  border-radius: 8px;
  padding: 8px 4px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: background 0.15s;
}

.btn-action:hover:not(:disabled) {
  background: #e0e0e0;
}

.btn-action:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-bought {
  background: #e8f5e9;
  color: #2e7d32;
}

.btn-bought:hover:not(:disabled) {
  background: #c8e6c9;
}

.btn-dismiss {
  background: #ffebee;
  color: #c62828;
}

.btn-dismiss:hover:not(:disabled) {
  background: #ffcdd2;
}

.btn-link {
  background: #e3f2fd;
  color: #1565c0;
}
</style>

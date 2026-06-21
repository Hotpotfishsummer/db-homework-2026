<template>
  <div class="tab-panel">
    <div v-if="outfits.length > 0" class="history-list">
      <div
        v-for="(outfit, index) in outfits" :key="`${outfit.id}-${index}`"
        class="history-item"
        @click="$emit('goToDetail', outfit)"
      >
        <div class="history-image">
          <img :src="outfit.image" :alt="outfit.name" loading="lazy" />
        </div>
        <div class="history-info">
          <h4>{{ outfit.name }}</h4>
          <p>{{ formatTime(outfit.viewedAt) }}</p>
        </div>
        <button
          class="delete-btn"
          @click.stop="$emit('delete', outfit.outfitId || outfit.id)"
          title="删除记录"
        >✕</button>
        <span class="history-arrow">›</span>
      </div>
    </div>
    <div v-else class="empty-state">
      <span class="empty-icon">🕐</span>
      <p>还没有浏览记录</p>
      <p class="empty-hint">去首页看看吧</p>
      <button class="go-discover" @click="$emit('goHome')">去发现</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  outfits: { type: Array, default: () => [] }
})

defineEmits(['goToDetail', 'goHome', 'delete'])

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
  border-radius: 18px;
  border: 1px solid var(--hairline);
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

.delete-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: var(--bg-secondary);
  color: var(--text-tertiary);
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
  margin-right: 8px;
}

.delete-btn:hover {
  background: rgba(255, 77, 79, 0.1);
  color: #ff4d4f;
}

.history-arrow {
  font-size: 20px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

/* Empty state */
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
  background: var(--accent-color);
  color: var(--on-primary);
  border: none;
  border-radius: 9999px;
  font-size: 13px;
  font-weight: 400;
  cursor: pointer;
}
</style>

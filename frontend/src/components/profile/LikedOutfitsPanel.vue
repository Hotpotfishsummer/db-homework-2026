<template>
  <div class="tab-panel">
    <div v-if="outfits.length > 0" class="outfit-list">
      <div
        v-for="outfit in outfits" :key="outfit.id"
        class="outfit-item"
        @click="$emit('goToDetail', outfit)"
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
        <button class="outfit-action liked" @click.stop="$emit('confirmUnlike', outfit)">❤️</button>
      </div>
    </div>
    <div v-else class="empty-state">
      <span class="empty-icon">💝</span>
      <p>还没有收藏</p>
      <p class="empty-hint">去首页发现喜欢的穿搭吧</p>
      <button class="go-discover" @click="$emit('goHome')">去发现</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  outfits: { type: Array, default: () => [] }
})

defineEmits(['goToDetail', 'confirmUnlike', 'goHome'])
</script>

<style scoped>
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
  border-radius: 18px;
  border: 1px solid var(--hairline);
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
  border-radius: 9999px;
  background: var(--bg-secondary);
  border: none;
  font-size: 14px;
  cursor: pointer;
  flex-shrink: 0;
  margin-left: 8px;
  transition: all 0.2s;
}

.outfit-action:active { transform: scale(0.9); }

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

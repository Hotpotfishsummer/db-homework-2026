<template>
  <div class="wardrobe-gap-card">
    <div class="card-header">
      <span class="header-icon">📊</span>
      <h3>衣橱体检</h3>
    </div>
    <p class="summary">{{ report.summary }}</p>
    <div v-if="report.dominant_colors && report.dominant_colors.length" class="dominant-colors">
      <span class="label">主色调：</span>
      <span
        v-for="dc in report.dominant_colors"
        :key="dc.color"
        class="color-chip"
        :style="{ background: colorTint(dc.color) }"
      >
        {{ dc.color }} × {{ dc.count }}
      </span>
    </div>
    <div class="gaps-list">
      <div
        v-for="gap in report.gaps"
        :key="gap.category"
        class="gap-row"
        :class="{ 'is-short': gap.current < gap.suggested }"
      >
        <div class="gap-header">
          <span class="category-emoji">{{ categoryEmoji(gap.category) }}</span>
          <span class="category-name">{{ categoryLabel(gap.category) }}</span>
          <span class="count-bar">
            <span class="current">{{ gap.current }}</span>
            <span class="separator">/</span>
            <span class="suggested">{{ gap.suggested }}</span>
          </span>
        </div>
        <div class="progress-track">
          <div
            class="progress-fill"
            :style="{
              width: progressWidth(gap.current, gap.suggested) + '%',
              background: progressColor(gap.current, gap.suggested),
            }"
          />
        </div>
        <p class="gap-advice">{{ gap.advice }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  report: {
    type: Object,
    required: true,
  },
})

const CATEGORY_META = {
  top: '👕 上装',
  bottom: '👖 下装',
  outerwear: '🧥 外套',
  shoes: '👟 鞋履',
  accessory: '🕶️ 配饰',
  bag: '👜 包包',
  other: '👔 其他',
}

function categoryEmoji(cat) {
  const entry = CATEGORY_META[cat]
  return entry ? entry.split(' ')[0] : '👔'
}

function categoryLabel(cat) {
  const entry = CATEGORY_META[cat]
  return entry ? entry.split(' ')[1] : '其他'
}

function progressWidth(current, suggested) {
  if (suggested === 0) return 100
  return Math.min(100, (current / suggested) * 100)
}

function progressColor(current, suggested) {
  if (current >= suggested) return '#4caf50'
  if (current === 0) return '#ef5350'
  return '#ffa726'
}

function colorTint(color) {
  // Deterministic soft tint based on color name (for the chip background)
  if (!color) return '#f0f0f0'
  const map = {
    red: '#ffcdd2',
    blue: '#bbdefb',
    green: '#c8e6c9',
    black: '#cfd8dc',
    white: '#f5f5f5',
    yellow: '#fff9c4',
    pink: '#f8bbd0',
  }
  const lower = color.toLowerCase()
  for (const [key, val] of Object.entries(map)) {
    if (lower.includes(key)) return val
  }
  return '#f0f0f0'
}
</script>

<style scoped>
.wardrobe-gap-card {
  background: var(--surface-card, #ffffff);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.header-icon {
  font-size: 22px;
}

.card-header h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary, #1a1a1a);
}

.summary {
  font-size: 14px;
  color: var(--text-secondary, #555);
  line-height: 1.6;
  margin: 0 0 16px;
  padding: 10px 12px;
  background: #f5f5f5;
  border-radius: 10px;
  border-left: 3px solid #5e35b1;
}

.dominant-colors {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.dominant-colors .label {
  font-size: 12px;
  color: var(--text-secondary, #666);
}

.color-chip {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 8px;
  color: #333;
}

.gaps-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.gap-row {
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 12px;
}

.gap-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.gap-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.category-emoji {
  font-size: 16px;
}

.category-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary, #1a1a1a);
  flex: 1;
}

.count-bar {
  font-size: 12px;
  color: var(--text-secondary, #666);
  font-variant-numeric: tabular-nums;
}

.count-bar .current {
  font-weight: 600;
  color: var(--text-primary, #1a1a1a);
}

.count-bar .separator {
  margin: 0 2px;
  color: #ccc;
}

.progress-track {
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}

.gap-advice {
  font-size: 12px;
  color: var(--text-secondary, #666);
  margin: 0;
  line-height: 1.5;
}
</style>

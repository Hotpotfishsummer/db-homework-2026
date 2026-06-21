<template>
  <teleport to="body">
    <div v-if="visible" class="tip-overlay" @click.self="$emit('close')">
      <section class="tip-modal" role="dialog" aria-modal="true" aria-labelledby="daily-tip-title">
        <button class="tip-close" type="button" aria-label="关闭" @click="$emit('close')">×</button>

        <div class="tip-head">
          <span class="tip-mark">💡</span>
          <div>
            <p class="tip-kicker">每日穿搭小知识</p>
            <h2 id="daily-tip-title">{{ tip?.title || '今日穿搭小知识' }}</h2>
          </div>
        </div>

        <p class="tip-content">{{ tip?.content || fallbackText }}</p>

        <div v-if="tip?.example" class="tip-example">
          <span>例子</span>
          <p>{{ tip.example }}</p>
        </div>

        <div v-if="tipTags.length" class="tip-tags">
          <span v-for="tag in tipTags" :key="tag">{{ tag }}</span>
        </div>

        <div class="tip-actions">
          <button class="secondary-action" type="button" @click="$emit('close')">稍后再看</button>
          <button class="primary-action" type="button" @click="$emit('close')">知道了</button>
        </div>
      </section>
    </div>
  </teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  tip: {
    type: Object,
    default: null,
  },
})

defineEmits(['close'])

const fallbackText = '全身主色控制在三种以内，会让视觉更干净，也更容易穿出稳定的整体感。'
const tipTags = computed(() => Array.isArray(props.tip?.tags) ? props.tip.tags.slice(0, 5) : [])
</script>

<style scoped>
.tip-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(15, 18, 28, 0.42);
  backdrop-filter: blur(8px);
}

.tip-modal {
  position: relative;
  width: min(420px, 100%);
  max-height: min(82vh, 620px);
  overflow: auto;
  background: var(--surface-card, #ffffff);
  color: var(--text-primary, #1f1f1f);
  border-radius: 18px;
  padding: 24px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.22);
}

.tip-close {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: var(--bg-secondary, #f3f1f6);
  color: var(--text-secondary, #666);
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}

.tip-head {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding-right: 28px;
}

.tip-mark {
  display: grid;
  place-items: center;
  flex: 0 0 42px;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: #fff4c7;
  font-size: 22px;
}

.tip-kicker {
  margin: 0 0 5px;
  color: var(--accent-color, #5e35b1);
  font-size: 13px;
  font-weight: 700;
}

.tip-head h2 {
  margin: 0;
  color: var(--text-primary, #1f1f1f);
  font-size: 22px;
  line-height: 1.25;
  letter-spacing: 0;
}

.tip-content {
  margin: 20px 0 0;
  color: var(--text-primary, #1f1f1f);
  font-size: 16px;
  line-height: 1.7;
}

.tip-example {
  margin-top: 18px;
  padding: 14px 16px;
  border-radius: 12px;
  background: var(--bg-secondary, #f7f5fa);
}

.tip-example span {
  display: block;
  margin-bottom: 6px;
  color: var(--text-secondary, #666);
  font-size: 12px;
  font-weight: 700;
}

.tip-example p {
  margin: 0;
  color: var(--text-primary, #1f1f1f);
  font-size: 14px;
  line-height: 1.5;
}

.tip-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}

.tip-tags span {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(94, 53, 177, 0.08);
  color: var(--accent-color, #5e35b1);
  font-size: 12px;
  font-weight: 600;
}

.tip-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 24px;
}

.tip-actions button {
  min-height: 42px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}

.secondary-action {
  background: var(--bg-secondary, #f3f1f6);
  color: var(--text-secondary, #666);
}

.primary-action {
  background: var(--accent-color, #5e35b1);
  color: #ffffff;
}

@media (max-width: 420px) {
  .tip-overlay {
    align-items: flex-end;
    padding: 12px;
  }

  .tip-modal {
    border-radius: 18px 18px 16px 16px;
    padding: 22px 18px 18px;
  }

  .tip-head h2 {
    font-size: 20px;
  }
}
</style>

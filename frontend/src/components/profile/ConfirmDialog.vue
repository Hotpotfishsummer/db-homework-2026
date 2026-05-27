<template>
  <Teleport to="body">
    <div v-if="visible" class="confirm-dialog" @click.self="$emit('cancel')">
      <div class="confirm-mask"></div>
      <div class="confirm-card">
        <p class="confirm-title">移出珍藏</p>
        <p class="confirm-desc">这份穿搭灵感将从你的收藏夹中悄然离去</p>
        <div class="confirm-actions">
          <button class="confirm-btn cancel" @click="$emit('cancel')">再想想</button>
          <button class="confirm-btn confirm" @click="$emit('confirm')">移出收藏</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false }
})
defineEmits(['cancel', 'confirm'])
</script>

<style scoped>
.confirm-dialog {
  position: fixed;
  inset: 0;
  z-index: 1100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-mask {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.confirm-card {
  position: relative;
  z-index: 1;
  width: 300px;
  background: var(--bg-card);
  border-radius: 18px;
  border: 1px solid var(--hairline);
  padding: 28px 24px 20px;
  text-align: center;
  animation: confirmIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes confirmIn {
  from { opacity: 0; transform: scale(0.85) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.confirm-title {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.374px;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.confirm-desc {
  font-size: 14px;
  color: var(--text-tertiary);
  line-height: 1.6;
  margin-bottom: 24px;
}

.confirm-actions {
  display: flex;
  gap: 12px;
}

.confirm-btn {
  flex: 1;
  padding: 12px 0;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.confirm-btn:active {
  transform: scale(0.96);
}

.confirm-btn.cancel {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.confirm-btn.confirm {
  background: var(--accent-color);
  color: var(--on-primary);
}
</style>

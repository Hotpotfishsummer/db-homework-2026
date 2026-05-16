<template>
  <Teleport to="body">
    <Transition name="sheet">
      <div v-if="show" class="sheet-overlay" @click="close">
        <div class="sheet-content" @click.stop>
          <div class="sheet-handle"></div>
          <h3>✨ AI 灵感</h3>

          <div class="sheet-actions">
            <div class="action-item" @click="handleAction('add-cloth')">
              <div class="action-icon">👕</div>
              <span>录入新单品</span>
            </div>

            <div class="action-item" @click="handleAction('ai-match')">
              <div class="action-icon">🤖</div>
              <span>AI 搭配</span>
            </div>
          </div>

          <button class="cancel-btn" @click="close">取消</button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { watch } from 'vue'
import { useHaptics } from '../composables/useHaptics'

const props = defineProps({
  show: Boolean
})

const emit = defineEmits(['update:show', 'action'])

const { trigger } = useHaptics()

const close = () => {
  emit('update:show', false)
}

const handleAction = (type) => {
  trigger('success')
  emit('action', type)
  close()
}

watch(() => props.show, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.sheet-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 200;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.sheet-content {
  width: 100%;
  max-width: 500px;
  background: var(--bg-card);
  border-radius: 24px 24px 0 0;
  padding: 12px 24px 40px;
  padding-bottom: max(40px, env(safe-area-inset-bottom));
}

.sheet-handle {
  width: 40px;
  height: 4px;
  background: var(--border-color);
  border-radius: 2px;
  margin: 0 auto 20px;
}

.sheet-content h3 {
  text-align: center;
  font-size: 18px;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.sheet-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.action-item {
  flex: 1;
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-item:active {
  background: var(--border-color);
  transform: scale(0.98);
}

.action-icon {
  font-size: 40px;
}

.action-item span {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
  text-align: center;
}

.cancel-btn {
  width: 100%;
  padding: 14px;
  background: var(--bg-secondary);
  border: none;
  border-radius: 12px;
  font-size: 16px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:active {
  background: var(--border-color);
}

.sheet-enter-active,
.sheet-leave-active {
  transition: opacity 0.3s;
}

.sheet-enter-active .sheet-content,
.sheet-leave-active .sheet-content {
  transition: transform 0.3s;
}

.sheet-enter-from,
.sheet-leave-to {
  opacity: 0;
}

.sheet-enter-from .sheet-content,
.sheet-leave-to .sheet-content {
  transform: translateY(100%);
}
</style>
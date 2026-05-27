<template>
  <Teleport to="body">
    <div v-if="visible" class="avatar-modal" @click="$emit('close')">
      <div class="avatar-modal-mask"></div>
      <div class="avatar-modal-content">
        <img v-if="displayImage" :src="displayImage" alt="avatar" />
        <div v-else class="avatar-modal-placeholder">{{ initial }}</div>
        <button class="avatar-modal-close" @click="$emit('close')">✕</button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  avatarUrl: { type: String, default: '' },
  previewUrl: { type: String, default: '' },
  username: { type: String, default: 'U' }
})

defineEmits(['close'])

const displayImage = computed(() => props.previewUrl || props.avatarUrl || '')
const initial = computed(() => props.username?.charAt(0)?.toUpperCase() || 'U')
</script>

<style scoped>
.avatar-modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-modal-mask {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.85);
}

.avatar-modal-content {
  position: relative;
  width: 260px;
  height: 260px;
  border-radius: 50%;
  overflow: hidden;
  z-index: 1;
}

.avatar-modal-content img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-modal-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 80px;
  font-weight: 600;
  color: var(--accent-color);
  background: var(--surface-pearl);
}

.avatar-modal-close {
  position: fixed;
  top: 24px;
  right: 24px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}
</style>

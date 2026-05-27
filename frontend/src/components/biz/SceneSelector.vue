<template>
  <div class="scene-selector">
    <div class="scene-tabs">
      <div
        v-for="scene in scenes"
        :key="scene.id"
        class="scene-tab"
        :class="{ active: modelValue === scene.id }"
        @click="$emit('update:modelValue', scene.id)"
      >
        <span class="scene-icon">{{ scene.icon }}</span>
        <span>{{ scene.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  scenes: {
    type: Array,
    required: true
  },
  modelValue: {
    type: String,
    required: true
  }
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.scene-selector {
  padding: 0 24px;
  margin-top: -10px;
}

.scene-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 12px 0;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.scene-tabs::-webkit-scrollbar {
  display: none;
}

.scene-tab {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-card);
  border-radius: 9999px;
  border: 1px solid var(--hairline);
  font-size: 13px;
  font-weight: 400;
  letter-spacing: -0.224px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.scene-tab:active {
  transform: scale(0.95);
}

.scene-tab.active {
  background: var(--accent-color);
  color: var(--on-primary);
  border-color: transparent;
}

.scene-icon {
  font-size: 14px;
}
</style>

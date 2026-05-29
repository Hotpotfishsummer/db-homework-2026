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
        <span class="scene-name">{{ scene.name }}</span>
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

/* Desktop: vertical sidebar */
@media (min-width: 768px) {
  .scene-selector {
    width: 140px;
    flex-shrink: 0;
    padding: 20px 0;
    margin-top: 0;
  }

  .scene-tabs {
    display: flex;
    flex-direction: column;
    gap: 8px;
    overflow-x: visible;
    padding: 0;
  }
}

/* Large desktop: wider sidebar */
@media (min-width: 1280px) {
  .scene-selector {
    width: 180px;
  }
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

/* Desktop: full-width pills */
@media (min-width: 768px) {
  .scene-tab {
    flex-shrink: unset;
    width: 100%;
    padding: 12px 16px;
    border-radius: 12px;
    justify-content: flex-start;
  }
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

@media (min-width: 768px) {
  .scene-icon {
    font-size: 20px;
  }
}

@media (min-width: 1280px) {
  .scene-name {
    font-size: 15px;
  }
}
</style>
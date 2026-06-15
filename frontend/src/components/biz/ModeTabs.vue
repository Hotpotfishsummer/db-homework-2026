<template>
  <div class="mode-tabs">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      class="tab-button"
      :class="{ active: modelValue === tab.id }"
      @click="$emit('update:modelValue', tab.id)"
    >
      <span class="tab-icon">{{ tab.icon }}</span>
      <span class="tab-label">{{ tab.label }}</span>
    </button>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true,
  },
  tabs: {
    type: Array,
    required: true,
    // [{ id, label, icon }]
  },
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.mode-tabs {
  display: flex;
  background: var(--surface-card, #ffffff);
  border-radius: 12px;
  padding: 4px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  gap: 2px;
}

.tab-button {
  flex: 1;
  background: transparent;
  border: none;
  padding: 10px 8px;
  border-radius: 9px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary, #666);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: background 0.15s, color 0.15s;
}

.tab-button:hover {
  color: var(--text-primary, #1a1a1a);
}

.tab-button.active {
  background: linear-gradient(135deg, #5e35b1 0%, #7e57c2 100%);
  color: white;
  box-shadow: 0 2px 6px rgba(94, 53, 177, 0.25);
}

.tab-icon {
  font-size: 14px;
}

.tab-label {
  font-size: 13px;
}
</style>

<template>
  <div v-if="visible" class="llm-hint-card">
    <div class="hint-icon">💡</div>
    <div class="hint-content">
      <h4>想要更好的 AI 体验?</h4>
      <p>配置你自己的 OpenAI 兼容 LLM, 数据完全保留在你自己的设备上, 不上传服务器。</p>
    </div>
    <div class="hint-actions">
      <button class="btn btn-primary" @click="goToSettings">去设置</button>
      <button class="btn btn-ghost" @click="dismiss">稍后再说</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserLlmStore } from '../stores/user_llm'

const router = useRouter()
const store = useUserLlmStore()

const DISMISS_KEY = 'l-wardrobe.user_llm_hint_dismissed'

const dismissed = ref(false)

onMounted(() => {
  try {
    if (sessionStorage.getItem(DISMISS_KEY) === '1') {
      dismissed.value = true
    }
  } catch (e) { /* ignore */ }
})

const visible = computed(() => {
  return !dismissed.value && !store.isActive
})

function dismiss() {
  dismissed.value = true
  try {
    sessionStorage.setItem(DISMISS_KEY, '1')
  } catch (e) { /* ignore */ }
}

function goToSettings() {
  dismiss()
  router.push('/profile/settings')
}
</script>

<style scoped>
.llm-hint-card {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 12px 20px 4px;
  padding: 12px 14px;
  background: linear-gradient(135deg, #ede7f6 0%, #f3e5f5 100%);
  border-radius: 14px;
  border: 1px solid #d1c4e9;
}

.hint-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.hint-content {
  flex: 1;
  min-width: 0;
}

.hint-content h4 {
  margin: 0 0 2px;
  font-size: 13px;
  font-weight: 600;
  color: #4a2b91;
}

.hint-content p {
  margin: 0;
  font-size: 11px;
  color: #6c5b91;
  line-height: 1.4;
}

.hint-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.btn {
  border: none;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 12px;
  cursor: pointer;
  font-weight: 500;
  white-space: nowrap;
}

.btn-primary {
  background: #5e35b1;
  color: white;
}
.btn-primary:hover { background: #4a2b91; }

.btn-ghost {
  background: transparent;
  color: #6c5b91;
  text-decoration: underline;
}
.btn-ghost:hover { color: #4a2b91; }
</style>

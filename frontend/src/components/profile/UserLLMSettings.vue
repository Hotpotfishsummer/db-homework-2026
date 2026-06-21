<template>
  <div class="user-llm-settings" :class="{ expanded }">
    <!-- Header (always visible, click to toggle) -->
    <button class="settings-header" @click="toggle">
      <span class="header-left">
        <span class="header-icon">🔑</span>
        <span class="header-title">LLM 配置</span>
        <span class="status-badge" :class="statusClass">{{ statusText }}</span>
      </span>
      <span class="expand-icon" :class="{ flipped: expanded }">▾</span>
    </button>

    <!-- Expanded body -->
    <div v-if="expanded" class="settings-body">
      <p class="warning">
        ⚠️ 你的 API key 仅存储在本设备 (localStorage), 不会同步到服务器。
        后端在每次 LLM 请求时透传使用, 调用完即丢。
      </p>

      <!-- Enable switch -->
      <div class="form-row switch-row">
        <label class="switch-label">
          <input
            type="checkbox"
            :checked="enabled"
            @change="onEnabledChange($event.target.checked)"
          />
          <span class="switch-slider"></span>
          <span class="switch-text">使用我自己的 LLM</span>
        </label>
      </div>

      <!-- API Key -->
      <div class="form-row">
        <label class="form-label">API Key</label>
        <div class="input-with-icon">
          <input
            type="text"
            v-model="apiKey"
            class="form-input"
            :class="{ masked: !showKey }"
            placeholder="sk-..."
            autocomplete="off"
            autocapitalize="off"
            autocorrect="off"
            spellcheck="false"
          />
          <button
            class="icon-btn"
            type="button"
            @click="showKey = !showKey"
            :title="showKey ? '隐藏' : '显示'"
          >
            {{ showKey ? '🙈' : '👁' }}
          </button>
        </div>
      </div>

      <!-- Base URL -->
      <div class="form-row">
        <label class="form-label">Base URL</label>
        <input
          type="text"
          v-model="baseUrl"
          class="form-input"
          placeholder="https://api.openai.com/v1"
          autocomplete="off"
          spellcheck="false"
        />
        <p class="form-hint">OpenAI 兼容端点, 允许 https:// 或 http://localhost/IP</p>
      </div>

      <!-- Model -->
      <div class="form-row">
        <label class="form-label">Model</label>
        <div class="model-row">
          <select
            v-if="store.availableModels.length"
            v-model="model"
            class="form-input model-select"
          >
            <option v-for="m in store.availableModels" :key="m" :value="m">{{ m }}</option>
          </select>
          <input
            v-else
            type="text"
            v-model="model"
            class="form-input"
            placeholder="gpt-4o-mini"
          />
          <button
            class="icon-btn"
            type="button"
            :disabled="!apiKey || !baseUrl || store.isLoadingModels"
            @click="onRefreshModels"
            :title="store.isLoadingModels ? '加载中...' : '重新拉取模型列表'"
          >
            {{ store.isLoadingModels ? '⏳' : '🔄' }}
          </button>
        </div>
        <p class="form-hint" v-if="!store.availableModels.length">
          输入 key + base URL 后点击测试连接, 可拉取模型列表
        </p>
      </div>

      <!-- Action buttons -->
      <div class="action-row">
        <button
          class="btn btn-secondary"
          :disabled="!canTest || store.isTestingKey"
          @click="onTestKey"
        >
          <span v-if="store.isTestingKey">⏳</span>
          <span v-else>🔍</span>
          测试连接
        </button>
        <button
          class="btn btn-secondary"
          :disabled="!canTest || store.isTestingVision"
          @click="onTestVision"
        >
          <span v-if="store.isTestingVision">⏳</span>
          <span v-else>🖼️</span>
          测试多模态
        </button>
        <button
          class="btn btn-primary"
          :disabled="!canSave"
          @click="onSave"
        >
          💾 保存
        </button>
      </div>

      <!-- Status messages -->
      <div v-if="store.lastTestResult" class="status-msg" :class="store.lastTestResult.ok ? 'ok' : 'err'">
        {{ store.lastTestResult.ok ? '✅' : '❌' }}
        {{ store.lastTestResult.message }}
        <span v-if="store.lastTestResult.model_count" class="muted">
          ({{ store.lastTestResult.model_count }} 个模型)
        </span>
      </div>

      <div v-if="store.lastVisionResult" class="status-msg" :class="store.lastVisionResult.multimodal_ok ? 'ok' : 'err'">
        <template v-if="store.lastVisionResult.multimodal_ok">
          ✅ 多模态 OK — 模型支持图片理解
          <span v-if="store.lastVisionResult.response_text" class="muted">
            ("{{ store.lastVisionResult.response_text }}")
          </span>
        </template>
        <template v-else>
          ❌ 多模态失败: {{ store.lastVisionResult.error || '未知错误' }}
        </template>
      </div>

      <!-- Clear config -->
      <div v-if="hasConfig" class="clear-row">
        <button class="btn-link" @click="onClear">清除我的 LLM 配置</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserLlmStore } from '../../stores/user_llm'

const store = useUserLlmStore()

const expanded = ref(false)
const apiKey = ref('')
const baseUrl = ref('')
const model = ref('')
const enabled = ref(false)
const showKey = ref(false)

onMounted(() => {
  if (store.config) {
    apiKey.value = store.config.api_key || ''
    baseUrl.value = store.config.base_url || ''
    model.value = store.config.model || ''
    enabled.value = store.config.enabled !== false
  }
})

const hasConfig = computed(() => !!store.config)
const statusText = computed(() => {
  if (!store.config) return '未配置'
  if (store.config.enabled) return '已启用'
  return '已禁用'
})
const statusClass = computed(() => {
  if (!store.config) return 'idle'
  if (store.config.enabled) return 'active'
  return 'paused'
})

const canTest = computed(() => {
  return !!(apiKey.value.trim() && baseUrl.value.trim())
})

const canSave = computed(() => {
  return !!(apiKey.value.trim() && baseUrl.value.trim() && model.value.trim())
})

function toggle() {
  expanded.value = !expanded.value
}

function onEnabledChange(value) {
  enabled.value = value
  // If the user has a stored config, persist the new enable flag
  // immediately so they can see the effect without clicking Save.
  if (store.config && store.config.api_key === apiKey.value && store.config.base_url === baseUrl.value) {
    store.setEnabled(value)
  }
}

async function onTestKey() {
  await store.runTestKey({ api_key: apiKey.value, base_url: baseUrl.value })
}

async function onTestVision() {
  if (!model.value) return
  await store.runTestVision({
    api_key: apiKey.value,
    base_url: baseUrl.value,
    model: model.value,
  })
}

async function onRefreshModels() {
  if (!apiKey.value || !baseUrl.value) return
  // Reuse the existing connectivity test to fetch a model sample without
  // persisting credentials to localStorage.
  await store.runTestKey({ api_key: apiKey.value, base_url: baseUrl.value })
}

function onSave() {
  store.saveConfig({
    api_key: apiKey.value,
    base_url: baseUrl.value,
    model: model.value,
    enabled: enabled.value,
  })
  // Trigger haptic if available
  if (window?.navigator?.vibrate) window.navigator.vibrate(20)
}

function onClear() {
  if (!confirm('确定要清除你的 LLM 配置吗? 这将恢复使用服务器默认配置。')) return
  store.clearConfig()
  apiKey.value = ''
  baseUrl.value = ''
  model.value = ''
  enabled.value = false
  expanded.value = false
}
</script>

<style scoped>
.user-llm-settings {
  background: var(--bg-card);
  border-radius: 18px;
  margin-bottom: 14px;
  overflow: hidden;
  border: 1px solid var(--hairline);
}

.settings-header {
  width: 100%;
  background: none;
  border: none;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon { font-size: 18px; }
.header-title { font-weight: 600; }

.status-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}
.status-badge.active { background: rgba(82, 196, 26, 0.1); color: #52c41a; }
.status-badge.paused { background: rgba(255, 193, 7, 0.1); color: #faad14; }
.status-badge.idle { background: var(--bg-secondary); color: var(--text-tertiary); }

.expand-icon {
  transition: transform 0.2s;
  font-size: 14px;
  color: var(--text-tertiary);
}
.expand-icon.flipped { transform: rotate(180deg); }

.settings-body {
  padding: 0 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  border-top: 1px solid var(--border-color);
}

.warning {
  font-size: 12px;
  color: #856404;
  background: rgba(255, 193, 7, 0.1);
  padding: 10px 12px;
  border-radius: 10px;
  margin: 12px 0 4px;
  line-height: 1.5;
  border: 1px solid rgba(255, 193, 7, 0.2);
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.form-input {
  width: 100%;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 9px 12px;
  font-size: 13px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: ui-monospace, 'SF Mono', Menlo, monospace;
}

.form-input.masked {
  -webkit-text-security: disc;
  text-security: disc;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent-color);
  background: var(--bg-card);
}

.form-hint {
  font-size: 11px;
  color: var(--text-tertiary);
  margin: 0;
}

.input-with-icon, .model-row {
  position: relative;
  display: flex;
  gap: 6px;
}

.model-row .form-input, .model-row .model-select {
  flex: 1;
}

.model-select {
  appearance: none;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg width='10' height='6' viewBox='0 0 10 6' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23666' stroke-width='1.5' fill='none'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 30px;
}

.icon-btn {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  width: 38px;
  font-size: 14px;
  cursor: pointer;
  flex-shrink: 0;
  color: var(--text-primary);
}

.icon-btn:hover:not(:disabled) {
  background: var(--border-color);
}

.icon-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Switch */
.switch-row { padding-top: 4px; }
.switch-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}
.switch-label input { display: none; }
.switch-slider {
  position: relative;
  width: 40px;
  height: 22px;
  background: var(--border-color);
  border-radius: 11px;
  transition: background 0.2s;
}
.switch-slider::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 18px;
  height: 18px;
  background: white;
  border-radius: 50%;
  transition: transform 0.2s;
}
.switch-label input:checked + .switch-slider { background: var(--accent-color); }
.switch-label input:checked + .switch-slider::after { transform: translateX(18px); }
.switch-text { font-size: 14px; color: var(--text-primary); }

.action-row {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}
.btn {
  flex: 1;
  border: none;
  border-radius: 8px;
  padding: 9px 4px;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-weight: 500;
}
.btn:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-primary { background: var(--accent-color); color: var(--on-primary); }
.btn-primary:hover:not(:disabled) { background: var(--accent-hover); }
.btn-secondary { background: var(--bg-secondary); color: var(--text-primary); }
.btn-secondary:hover:not(:disabled) { background: var(--border-color); }

.status-msg {
  font-size: 12px;
  padding: 8px 10px;
  border-radius: 8px;
  line-height: 1.5;
}
.status-msg.ok { background: rgba(82, 196, 26, 0.1); color: #52c41a; }
.status-msg.err { background: rgba(255, 77, 79, 0.1); color: #ff4d4f; }
.status-msg .muted { color: inherit; opacity: 0.7; }

.clear-row {
  text-align: center;
  padding-top: 6px;
  border-top: 1px solid var(--border-color);
  margin-top: 6px;
}
.btn-link {
  background: none;
  border: none;
  color: #ff4d4f;
  font-size: 12px;
  cursor: pointer;
  text-decoration: underline;
  padding: 4px;
}
.btn-link:hover { color: #cf1322; }
</style>

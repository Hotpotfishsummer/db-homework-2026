<template>
  <div class="register-container">
    <div class="register-card">
      <div class="logo">👔</div>
      <h1>创建账号</h1>
      <p class="subtitle">加入 AI 穿搭，开启时尚之旅</p>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <input
            v-model="username"
            type="text"
            placeholder="请输入账号"
            :class="{ 'error-input': usernameError }"
          />
          <span v-if="usernameError" class="error-text">{{ usernameError }}</span>
        </div>

        <div class="form-group">
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码（至少3位）"
            :class="{ 'error-input': passwordError }"
          />
          <span v-if="passwordError" class="error-text">{{ passwordError }}</span>
        </div>

        <div class="form-group">
          <input
            v-model="confirmPassword"
            type="password"
            placeholder="请确认密码"
            :class="{ 'error-input': confirmPasswordError }"
          />
          <span v-if="confirmPasswordError" class="error-text">{{ confirmPasswordError }}</span>
        </div>

        <div v-if="successMsg" class="success-message">{{ successMsg }}</div>
        <div v-if="errorMsg" class="error-message">{{ errorMsg }}</div>

        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="loading" class="loading-text">注册中...</span>
          <span v-else>注 册</span>
        </button>
      </form>

      <p class="link-text">
        已有账号？<router-link to="/login">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const usernameError = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')

const validate = () => {
  usernameError.value = ''
  passwordError.value = ''
  confirmPasswordError.value = ''
  errorMsg.value = ''
  successMsg.value = ''
  let valid = true

  if (!username.value.trim()) {
    usernameError.value = '请输入账号'
    valid = false
  }

  if (!password.value) {
    passwordError.value = '请输入密码'
    valid = false
  } else if (password.value.length < 3) {
    // TODO: 上线前改为 6-8 位复杂密码校验
    passwordError.value = '密码长度至少为 3 位'
    valid = false
  }

  if (!confirmPassword.value) {
    confirmPasswordError.value = '请确认密码'
    valid = false
  } else if (password.value !== confirmPassword.value) {
    confirmPasswordError.value = '两次输入的密码不一致'
    valid = false
  }

  return valid
}

const handleRegister = async () => {
  if (!validate()) return

  loading.value = true
  errorMsg.value = ''

  try {
    await authStore.register(username.value, password.value)
    successMsg.value = '注册成功！正在跳转到登录页...'
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (error) {
    errorMsg.value = error.msg || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 20px;
}

.register-card {
  background: var(--bg-card);
  padding: 40px 35px;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 380px;
  text-align: center;
}

.logo {
  font-size: 60px;
  margin-bottom: 10px;
}

h1 {
  font-size: 24px;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  font-weight: 600;
}

.subtitle {
  color: var(--text-tertiary);
  font-size: 14px;
  margin: 0 0 30px 0;
}

.form-group {
  margin-bottom: 20px;
  text-align: left;
}

input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  font-size: 15px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #f5576c;
}

input.error-input {
  border-color: #ff4d4f;
}

.error-text {
  display: block;
  color: #ff4d4f;
  font-size: 12px;
  margin-top: 6px;
  text-align: left;
}

.success-message {
  color: #52c41a;
  font-size: 14px;
  margin-bottom: 15px;
  padding: 10px;
  background: #f6ffed;
  border-radius: 8px;
}

.error-message {
  color: #ff4d4f;
  font-size: 14px;
  margin-bottom: 15px;
  padding: 10px;
  background: #fff2f0;
  border-radius: 8px;
}

.btn-primary {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(245, 87, 108, 0.4);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.link-text {
  margin-top: 25px;
  color: var(--text-secondary);
  font-size: 14px;
}

.link-text a {
  color: #f5576c;
  text-decoration: none;
  font-weight: 600;
}

.link-text a:hover {
  text-decoration: underline;
}
</style>
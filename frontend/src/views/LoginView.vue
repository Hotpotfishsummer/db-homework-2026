<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo">👗</div>
      <h1>开启你的 AI 私人衣橱</h1>
      <p class="subtitle">智能穿搭推荐，遇见更美的自己</p>

      <form @submit.prevent="handleLogin">
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
            placeholder="请输入密码"
            :class="{ 'error-input': passwordError }"
          />
          <span v-if="passwordError" class="error-text">{{ passwordError }}</span>
        </div>

        <div v-if="errorMsg" class="error-message">{{ errorMsg }}</div>

        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="loading" class="loading-text">登录中...</span>
          <span v-else>登 录</span>
        </button>
      </form>

      <p class="link-text">
        还没有账号？<router-link to="/register">立即注册</router-link>
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
const loading = ref(false)
const errorMsg = ref('')
const usernameError = ref('')
const passwordError = ref('')

const validate = () => {
  usernameError.value = ''
  passwordError.value = ''
  errorMsg.value = ''
  let valid = true

  if (!username.value.trim()) {
    usernameError.value = '请输入账号'
    valid = false
  }

  if (!password.value) {
    passwordError.value = '请输入密码'
    valid = false
  } else if (password.value.length < 3) {
    passwordError.value = '密码长度至少为 3 位'
    valid = false
  }

  return valid
}

const handleLogin = async () => {
  if (!validate()) return

  loading.value = true
  errorMsg.value = ''

  try {
    await authStore.login(username.value, password.value)
    router.push('/home')
  } catch (error) {
    errorMsg.value = error.msg || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-gradient);
  padding: 20px;
}

.login-card {
  background: var(--bg-card);
  padding: 40px 35px;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
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
  border-color: var(--accent-color);
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
  background: var(--primary-gradient);
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
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-text {
  display: inline-block;
}

.link-text {
  margin-top: 25px;
  color: var(--text-secondary);
  font-size: 14px;
}

.link-text a {
  color: var(--accent-color);
  text-decoration: none;
  font-weight: 600;
}

.link-text a:hover {
  text-decoration: underline;
}
</style>
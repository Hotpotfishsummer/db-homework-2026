<template>
  <div class="app-root" :class="{ dark: themeStore.isDark }">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useThemeStore } from './stores/theme'

const themeStore = useThemeStore()

onMounted(() => {
  themeStore.init()
})
</script>

<style>
/* CSS 变量 - 亮色主题 */
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f8f8f8;
  --bg-card: #ffffff;
  --text-primary: #333333;
  --text-secondary: #666666;
  --text-tertiary: #999999;
  --border-color: #eeeeee;
  --shadow-color: rgba(0, 0, 0, 0.08);
  --primary-gradient: linear-gradient(135deg, #6BBA9E 0%, #4A8B7A 100%);
  --accent-color: #5B9A8B;
}

/* CSS 变量 - 深色主题 */
html.dark {
  --bg-primary: #1a1a1a;
  --bg-secondary: #121212;
  --bg-card: #2a2a2a;
  --text-primary: #ffffff;
  --text-secondary: #cccccc;
  --text-tertiary: #888888;
  --border-color: #333333;
  --shadow-color: rgba(0, 0, 0, 0.3);
}

/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body, html {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: background-color 0.3s, color 0.3s;
  overscroll-behavior: none;
}

input, textarea {
  background-color: var(--bg-card);
  color: var(--text-primary);
  border-color: var(--border-color);
}
</style>

<style scoped>
.app-root {
  min-height: 100vh;
  background-color: var(--bg-primary);
  transition: background-color 0.3s;
}
</style>
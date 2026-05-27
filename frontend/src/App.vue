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
/* Apple Design System - Light Theme */
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f7;
  --bg-card: #ffffff;
  --text-primary: #1d1d1f;
  --text-secondary: #7a7a7a;
  --text-tertiary: #7a7a7a;
  --border-color: #e0e0e0;
  --shadow-color: rgba(0, 0, 0, 0.04);
  --primary-gradient: #0066cc;
  --accent-color: #0066cc;
  --accent-hover: #0071e3;
  --accent-on-dark: #2997ff;
  --ink: #1d1d1f;
  --surface-pearl: #fafafc;
  --surface-tile-1: #272729;
  --surface-tile-2: #2a2a2c;
  --surface-tile-3: #252527;
  --surface-black: #000000;
  --chip-translucent: rgba(210, 210, 215, 0.64);
  --hairline: #e0e0e0;
  --divider-soft: #f0f0f0;
  --product-shadow: rgba(0, 0, 0, 0.22) 3px 5px 30px 0;
  --on-primary: #ffffff;
}

/* Apple Design System - Dark Theme */
html.dark {
  --bg-primary: #000000;
  --bg-secondary: #252527;
  --bg-card: #272729;
  --text-primary: #ffffff;
  --text-secondary: #cccccc;
  --text-tertiary: #7a7a7a;
  --border-color: #3a3a3c;
  --shadow-color: rgba(0, 0, 0, 0.22);
  --hairline: #3a3a3c;
  --divider-soft: #3a3a3c;
  --surface-pearl: #2a2a2c;
}

/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body, html {
  font-family: 'SF Pro Display', 'SF Pro Text', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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
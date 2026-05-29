<template>
  <div class="desktop-layout">
    <SidebarDesktop />
    <main class="desktop-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import SidebarDesktop from '../SidebarDesktop.vue'
</script>

<style scoped>
.desktop-layout {
  display: flex;
  min-height: 100vh;
}

.desktop-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  padding: 24px 48px;
  max-width: var(--content-max-width);
}

@media (min-width: 768px) {
  .desktop-content {
    padding: 24px 32px;
  }
}

@media (min-width: 1024px) {
  .desktop-content {
    padding: 32px 48px;
  }
}

@media (min-width: 1280px) {
  .desktop-content {
    padding: 40px 64px;
  }
}
</style>
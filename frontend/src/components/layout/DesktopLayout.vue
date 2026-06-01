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
  overflow-x: clip;
}

.desktop-content {
  flex: 1;
  margin-left: 0;
  padding: 0;
  max-width: var(--content-max-width);
  overflow-x: clip;
  min-width: 0;
}

@media (min-width: 768px) {
  .desktop-content {
    margin-left: var(--sidebar-width);
    padding: 0 32px 24px;
  }
}

@media (min-width: 1024px) {
  .desktop-content {
    padding: 0 48px 32px;
  }
}

@media (min-width: 1280px) {
  .desktop-content {
    padding: 0 64px 40px;
  }
}
</style>
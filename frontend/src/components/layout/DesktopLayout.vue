<template>
  <div class="desktop-layout">
    <SidebarDesktop />
    <main class="desktop-content">
      <div class="content-inner">
        <router-view />
      </div>
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
  min-width: 0;
  overflow-x: clip;
  width: 100%;
}

/*
 * Inner wrapper:
 * - A pass-through container that occupies the full horizontal space
 *   between the sidebar and the right edge of the viewport, so the
 *   page's background and edge-to-edge elements (sticky headers, hero
 *   cards, etc.) can stretch across the entire middle area without
 *   being clipped by a side gutter.
 * - Intentionally has zero padding/margin. Responsive inner spacing
 *   is the responsibility of each view's root container, which keeps
 *   desktop and mobile styling decisions in one place.
 */
.content-inner {
  width: 100%;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

@media (min-width: 768px) {
  .desktop-content {
    margin-left: var(--sidebar-width);
  }
}
</style>
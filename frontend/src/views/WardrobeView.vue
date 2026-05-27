<template>
  <div class="wardrobe-container">
    <div class="wardrobe-header">
      <h1>我的衣橱</h1>
      <span class="count">{{ wardrobeStore.filteredClothes.length }} 件单品</span>
    </div>

    <div class="category-tabs">
      <div
        v-for="cat in wardrobeStore.categories"
        :key="cat.id"
        class="tab-item"
        :class="{ active: wardrobeStore.filterCategory === cat.id }"
        @click="selectCategory(cat.id)"
      >
        <span class="tab-icon">{{ cat.icon }}</span>
        <span class="tab-name">{{ cat.name }}</span>
      </div>
    </div>

    <div class="clothing-grid" v-if="wardrobeStore.filteredClothes.length > 0">
      <TransitionGroup name="grid">
        <div
          v-for="cloth in wardrobeStore.filteredClothes"
          :key="cloth.id"
          class="clothing-item"
          @click="viewDetail(cloth)"
        >
          <div class="item-image">
            <img :src="cloth.image" :alt="cloth.name" loading="lazy" />
            <span v-if="cloth.status === 'washing'" class="status-badge">清洗中</span>
          </div>
          <div class="item-info">
            <p class="item-name">{{ cloth.name }}</p>
            <p class="item-color" :style="{ background: cloth.color }"></p>
            <button class="wash-btn" @click.stop="toggleStatus(cloth)">
              {{ cloth.status === 'available' ? '🧺 标记清洗' : '✓ 已清洗' }}
            </button>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <div v-else class="empty-wardrobe">
      <span class="empty-icon">👗</span>
      <p>衣橱空空如也</p>
      <p class="empty-hint">点击下方 ✨ 按钮添加衣服</p>
    </div>

    <BottomNav />

    <ClothingDetail
      v-if="selectedCloth"
      :cloth="selectedCloth"
      @close="selectedCloth = null"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useWardrobeStore } from '../stores/wardrobe'
import { useHaptics } from '../composables/useHaptics'
import BottomNav from '../components/BottomNav.vue'
import ClothingDetail from '../components/ClothingDetail.vue'

const router = useRouter()
const authStore = useAuthStore()
const wardrobeStore = useWardrobeStore()
const { trigger } = useHaptics()

const selectedCloth = ref(null)

onMounted(() => {
  authStore.checkAuth()
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  wardrobeStore.initMockData()
})

const selectCategory = (id) => {
  trigger('light')
  wardrobeStore.setFilter(id)
}

const viewDetail = (cloth) => {
  trigger('medium')
  selectedCloth.value = cloth
}

const toggleStatus = (cloth) => {
  trigger('light')
  const newStatus = cloth.status === 'available' ? 'washing' : 'available'
  wardrobeStore.updateClothStatus(cloth.id, newStatus)
}
</script>

<style scoped>
.wardrobe-container {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 100px;
}

.wardrobe-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 50px 24px 16px;
  background: var(--bg-card);
}

.wardrobe-header h1 {
  font-size: 28px;
  color: var(--text-primary);
  font-weight: 600;
  letter-spacing: -0.374px;
}

.count {
  font-size: 14px;
  color: var(--text-tertiary);
}

.category-tabs {
  display: flex;
  overflow-x: auto;
  gap: 8px;
  padding: 16px 24px;
  background: var(--bg-card);
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.category-tabs::-webkit-scrollbar {
  display: none;
}

.tab-item {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-item:active {
  transform: scale(0.95);
}

.tab-item.active {
  background: var(--accent-color);
}

.tab-item.active .tab-name {
  color: var(--on-primary);
}

.tab-icon {
  font-size: 20px;
}

.tab-name {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 400;
  letter-spacing: -0.12px;
}

.clothing-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 20px 24px;
}

.clothing-item {
  background: var(--bg-card);
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid var(--hairline);
  cursor: pointer;
  transition: all 0.2s;
}

.clothing-item:active {
  transform: scale(0.98);
}

.item-image {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  background: var(--bg-secondary);
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.item-image:hover img {
  transform: scale(1.05);
}

.status-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 152, 0, 0.9);
  color: white;
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 500;
}

.item-info {
  padding: 12px;
}

.item-name {
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  margin-bottom: 8px;
}

.wash-btn {
  width: 100%;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border: none;
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.wash-btn:active {
  transform: scale(0.98);
  background: var(--border-color);
}

.empty-wardrobe {
  text-align: center;
  padding: 80px 40px;
}

.empty-icon {
  font-size: 60px;
  display: block;
  margin-bottom: 16px;
}

.empty-wardrobe p {
  font-size: 16px;
  color: var(--text-secondary);
}

.empty-hint {
  font-size: 14px !important;
  color: var(--text-tertiary) !important;
  margin-top: 8px;
}

.grid-enter-active,
.grid-leave-active {
  transition: all 0.3s ease;
}

.grid-enter-from,
.grid-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.grid-move {
  transition: transform 0.3s ease;
}
</style>
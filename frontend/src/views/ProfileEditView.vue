<template>
  <div class="edit-container">
    <div class="page-nav">
      <button class="nav-back" @click="goBack">&#8592;</button>
      <h1>完善档案</h1>
      <span></span>
    </div>

    <div class="edit-content">
      <BodyCardSection
        :height="draft.height"
        :weight="draft.weight"
        :skinTone="draft.skinTone"
        :bodyShape="draft.bodyShape"
        :faceFeature="draft.faceFeature"
        @update:height="draft.height = $event"
        @update:weight="draft.weight = $event"
        @update:skinTone="selectSkinTone"
        @update:bodyShape="selectBodyShape"
        @update:faceFeature="selectFaceFeature"
      />

      <StylePersonalitySection
        :styleAxesValues="draft.styleAxes"
        :selectedStyleTags="draft.styleTags"
        :favoriteColors="draft.favoriteColors"
        :avoidColors="draft.avoidColors"
        :fitPreference="draft.fitPreference"
        @update:styleAxesValues="draft.styleAxes = $event"
        @toggleTag="toggleStyleTag"
        @toggleFavorite="toggleFavoriteColor"
        @toggleAvoid="toggleAvoidColor"
        @update:fitPreference="draft.fitPreference = $event"
      />

      <button class="btn-confirm" :class="{ saved: saved }" @click="confirmSave">
        {{ saved ? '✓ 已保存' : '确认修改' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUserStore } from '../stores/user'
import { useHaptics } from '../composables/useHaptics'
import BodyCardSection from '../components/profile/BodyCardSection.vue'
import StylePersonalitySection from '../components/profile/StylePersonalitySection.vue'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const { trigger } = useHaptics()

const saved = ref(false)

const draft = reactive({
  height: null,
  weight: null,
  skinTone: null,
  bodyShape: null,
  faceFeature: null,
  styleAxes: { minimalComplex: 50, vintageModern: 50, formalCasual: 50 },
  styleTags: [],
  favoriteColors: [],
  avoidColors: [],
  fitPreference: null
})

onMounted(() => {
  authStore.checkAuth()
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  userStore.loadProfile()
  const p = userStore.profile
  Object.assign(draft, {
    height: p.height, weight: p.weight, skinTone: p.skinTone,
    bodyShape: p.bodyShape, faceFeature: p.faceFeature,
    styleAxes: { ...p.styleAxes },
    styleTags: [...p.styleTags],
    favoriteColors: [...p.favoriteColors],
    avoidColors: [...p.avoidColors],
    fitPreference: p.fitPreference
  })
})

const goBack = () => { trigger('light'); router.back() }

const selectSkinTone = (id) => { trigger('light'); draft.skinTone = id }
const selectBodyShape = (id) => { trigger('light'); draft.bodyShape = id }
const selectFaceFeature = (id) => { trigger('light'); draft.faceFeature = id }

const toggleStyleTag = (id) => {
  trigger('light')
  const i = draft.styleTags.indexOf(id)
  i > -1 ? draft.styleTags.splice(i, 1) : draft.styleTags.push(id)
}

const toggleFavoriteColor = (id) => {
  trigger('light')
  const i = draft.favoriteColors.indexOf(id)
  if (i > -1) { draft.favoriteColors.splice(i, 1) }
  else {
    draft.avoidColors = draft.avoidColors.filter(c => c !== id)
    draft.favoriteColors.push(id)
  }
}

const toggleAvoidColor = (id) => {
  trigger('light')
  const i = draft.avoidColors.indexOf(id)
  if (i > -1) { draft.avoidColors.splice(i, 1) }
  else {
    draft.favoriteColors = draft.favoriteColors.filter(c => c !== id)
    draft.avoidColors.push(id)
  }
}

const confirmSave = () => {
  trigger('medium')
  userStore.updateProfile({
    height: draft.height, weight: draft.weight, skinTone: draft.skinTone,
    bodyShape: draft.bodyShape, faceFeature: draft.faceFeature,
    styleAxes: { ...draft.styleAxes },
    styleTags: [...draft.styleTags],
    favoriteColors: [...draft.favoriteColors],
    avoidColors: [...draft.avoidColors],
    fitPreference: draft.fitPreference
  })
  saved.value = true
  setTimeout(() => { saved.value = false; router.back() }, 600)
}
</script>

<style scoped>
.edit-container {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 40px;
}

.page-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 50px 24px 20px;
  background: var(--bg-card);
}

.nav-back {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-secondary);
  border: none;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
}

.page-nav h1 {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.374px;
  color: var(--text-primary);
}

.edit-content {
  padding: 20px 24px;
}

.btn-confirm {
  display: block;
  width: 100%;
  margin-top: 24px;
  padding: 14px;
  background: var(--accent-color);
  border: none;
  border-radius: 9999px;
  color: var(--on-primary);
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-confirm:active {
  opacity: 0.85;
  transform: scale(0.98);
}

.btn-confirm.saved {
  background: #52c41a;
}
</style>

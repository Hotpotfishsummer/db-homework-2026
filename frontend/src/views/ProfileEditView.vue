<template>
  <div class="edit-container">
    <div class="page-nav">
      <button class="nav-back" @click="goBack">←</button>
      <h1>完善档案</h1>
      <span></span>
    </div>

    <div class="edit-content">
      <!-- ===== 数字人体卡片 ===== -->
      <div class="section-header">
        <h3>数字人体卡片</h3>
      </div>

      <div class="profile-card">
        <div class="edit-tip">
          <span>✨ 点击选择，再次点击取消选择</span>
        </div>

        <!-- 基础维度 -->
        <div class="profile-item">
          <label>📏 基础维度</label>
          <div class="body-metrics">
            <div class="metric-input">
              <input type="number" v-model="heightInput" placeholder="身高" @change="updateHeight" />
              <span class="metric-unit">cm</span>
            </div>
            <div class="metric-input">
              <input type="number" v-model="weightInput" placeholder="体重" @change="updateWeight" />
              <span class="metric-unit">kg</span>
            </div>
            <div class="bmi-display" v-if="localBMI">
              <span class="bmi-label">BMI</span>
              <span class="bmi-value" :class="bmiClass">{{ localBMI }}</span>
            </div>
          </div>
        </div>

        <!-- 肤色定调 -->
        <div class="profile-item">
          <label>🎨 肤色定调</label>
          <div class="color-options">
            <div
              v-for="tone in skinTones" :key="tone.id"
              class="color-chip"
              :class="{ active: draft.skinTone === tone.id }"
              :style="{ background: tone.color }"
              @click="selectSkinTone(tone.id)"
            >
              <span v-if="draft.skinTone === tone.id" class="check-mark">✓</span>
              <span class="tone-label">{{ tone.name }}</span>
            </div>
          </div>
          <p class="profile-hint" v-if="draft.skinTone">
            💡 AI分析：你是「{{ getSeasonName(draft.skinTone) }}」，适合{{ getColorRecommendation(draft.skinTone) }}
          </p>
        </div>

        <!-- 体型选择 -->
        <div class="profile-item">
          <label>👤 体型</label>
          <div class="body-options">
            <div
              v-for="body in bodyShapes" :key="body.id"
              class="body-option"
              :class="{ active: draft.bodyShape === body.id }"
              @click="selectBodyShape(body.id)"
            >
              <div class="body-silhouette" v-html="body.svg"></div>
              <span class="body-name">{{ body.name }}</span>
            </div>
          </div>
        </div>

        <!-- 面部特征 -->
        <div class="profile-item">
          <label>✨ 面部特征（可选）</label>
          <div class="face-options">
            <div
              v-for="face in faceFeatures" :key="face.id"
              class="face-chip"
              :class="{ active: draft.faceFeature === face.id }"
              @click="selectFaceFeature(face.id)"
            >
              <span class="face-icon">{{ face.icon }}</span>
              <span class="face-name">{{ face.name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== 时尚人格 ===== -->
      <div class="section-header">
        <h3>时尚人格</h3>
      </div>

      <div class="profile-card">
        <!-- 风格象限 -->
        <div class="profile-item">
          <label>📊 风格坐标</label>
          <div class="style-axes">
            <div class="axis-item" v-for="axis in styleAxes" :key="axis.id">
              <div class="axis-labels">
                <span>{{ axis.left }}</span>
                <span>{{ axis.right }}</span>
              </div>
              <input
                type="range" min="0" max="100"
                v-model="draft.styleAxes[axis.id]"
                class="axis-slider"
                :style="getSliderStyle(axis.id)"
              />
              <div class="axis-value">{{ draft.styleAxes[axis.id] }}</div>
            </div>
          </div>
        </div>

        <!-- 风格标签 -->
        <div class="profile-item">
          <label>🏷️ 灵感标签</label>
          <div class="style-tags">
            <div
              v-for="style in styleTags" :key="style.id"
              class="style-tag"
              :class="{ active: draft.styleTags.includes(style.id) }"
              @click="toggleStyleTag(style.id)"
            >
              <span class="tag-name">{{ style.name }}</span>
              <span class="tag-desc">{{ style.desc }}</span>
            </div>
          </div>
        </div>

        <!-- 色彩偏好 -->
        <div class="profile-item">
          <label>❤️ 红榜（喜欢的颜色）</label>
          <div class="color-preference">
            <div
              v-for="color in availableColors" :key="color.id"
              class="pref-color"
              :class="{ active: draft.favoriteColors.includes(color.id), disabled: draft.avoidColors.includes(color.id) }"
              :style="{ background: color.color }"
              @click="toggleFavoriteColor(color.id)"
            >
              <span v-if="draft.favoriteColors.includes(color.id)">♥</span>
            </div>
          </div>
        </div>

        <div class="profile-item">
          <label>🚫 黑榜（绝不尝试的颜色）</label>
          <div class="color-preference">
            <div
              v-for="color in availableColors" :key="color.id"
              class="pref-color avoid"
              :class="{ active: draft.avoidColors.includes(color.id), disabled: draft.favoriteColors.includes(color.id) }"
              :style="{ background: color.color }"
              @click="toggleAvoidColor(color.id)"
            >
              <span v-if="draft.avoidColors.includes(color.id)">✕</span>
            </div>
          </div>
        </div>

        <!-- 版型偏好 -->
        <div class="profile-item">
          <label>📐 版型偏好</label>
          <div class="fit-options">
            <div
              v-for="fit in fitPreferences" :key="fit.id"
              class="fit-option"
              :class="{ active: draft.fitPreference === fit.id }"
              @click="selectFit(fit.id)"
            >
              <span class="fit-icon">{{ fit.icon }}</span>
              <span class="fit-name">{{ fit.name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 确认修改 -->
      <button class="btn-confirm" :class="{ saved: saved }" @click="confirmSave">
        {{ saved ? '✓ 已保存' : '确认修改' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUserStore } from '../stores/user'
import { useHaptics } from '../composables/useHaptics'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const { trigger } = useHaptics()

const saved = ref(false)
const heightInput = ref(null)
const weightInput = ref(null)

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

const localBMI = computed(() => {
  if (draft.height && draft.weight) {
    const h = draft.height / 100
    return (draft.weight / (h * h)).toFixed(1)
  }
  return null
})

const bmiClass = computed(() => {
  const bmi = localBMI.value
  if (!bmi) return ''
  if (bmi < 18.5) return 'bmi-low'
  if (bmi < 24) return 'bmi-normal'
  if (bmi < 28) return 'bmi-high'
  return 'bmi-obese'
})

const skinTones = [
  { id: 'fair_cool', name: '冷白', color: '#fce4d6', season: 'summer', recommendation: '柔和的冷色调，如雾霾蓝、薰衣草紫' },
  { id: 'fair_warm', name: '暖白', color: '#ffe4c4', season: 'spring', recommendation: '温暖的珊瑚色、米白色' },
  { id: 'medium', name: '自然', color: '#deb887', season: 'autumn', recommendation: '大地色系，如焦糖色、橄榄绿' },
  { id: 'tan', name: '小麦', color: '#d2a679', season: 'autumn', recommendation: '温暖的砖红色、芥末黄' },
  { id: 'dark', name: '深褐', color: '#8b5a2b', season: 'deep_winter', recommendation: '饱和度高的深色，如宝蓝、墨绿' }
]

const bodyShapes = [
  { id: 'inverted_triangle', name: '倒三角', svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M20 5 L35 25 L30 55 L10 55 L5 25 Z"/></svg>` },
  { id: 'rectangle', name: '矩形', svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M10 5 L30 5 L30 55 L10 55 Z"/></svg>` },
  { id: 'pear', name: '梨型', svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M15 5 L25 5 L25 25 L35 35 L30 55 L10 55 L5 35 L15 25 Z"/></svg>` },
  { id: 'hourglass', name: '沙漏', svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M10 5 L30 5 L30 15 L32 25 L28 35 L32 45 L30 55 L10 55 L8 45 L12 35 L8 25 L10 15 Z"/></svg>` },
  { id: 'apple', name: '苹果', svg: `<svg viewBox="0 0 40 60" fill="currentColor"><path d="M12 5 L28 5 L28 15 Q35 20 30 30 L28 40 L30 55 L10 55 L12 40 L10 30 Q5 20 12 15 Z"/></svg>` }
]

const faceFeatures = [
  { id: 'soft', name: '幼态柔和', icon: '🥚' },
  { id: 'sharp', name: '硬朗立体', icon: '⚔️' },
  { id: 'mature', name: '成熟优雅', icon: '👑' },
  { id: 'youthful', name: '元气活力', icon: '☀️' }
]

const styleAxes = [
  { id: 'minimalComplex', left: '极简', right: '繁复' },
  { id: 'vintageModern', left: '复古', right: '科技' },
  { id: 'formalCasual', left: '正式', right: '休闲' }
]

const styleTags = [
  { id: 'old_money', name: 'Old Money', desc: '低调奢华' },
  { id: 'intellectual', name: '高智感', desc: '书卷气质' },
  { id: 'dopamine', name: '多巴胺', desc: '色彩狂欢' },
  { id: 'american_vintage', name: '美式复古', desc: '街头经典' },
  { id: 'y2k', name: 'Y2K', desc: '千禧未来' },
  { id: 'clean_fit', name: 'Clean Fit', desc: '极简利落' },
  { id: 'athleisure', name: 'Athleisure', desc: '运动休闲' },
  { id: 'normcore', name: 'Normcore', desc: '平凡日常' },
  { id: 'gorpcore', name: 'Gorpcore', desc: '户外机能' },
  { id: 'japanese', name: '日系风格', desc: '文艺清新' },
  { id: 'streetwear', name: '街头潮流', desc: '个性张扬' },
  { id: 'korean', name: '韩系风格', desc: '精致通勤' }
]

const availableColors = [
  { id: 'red', color: '#e53935' }, { id: 'orange', color: '#ff9800' },
  { id: 'yellow', color: '#fdd835' }, { id: 'green', color: '#43a047' },
  { id: 'cyan', color: '#00acc1' }, { id: 'blue', color: '#1e88e5' },
  { id: 'purple', color: '#8e24aa' }, { id: 'pink', color: '#ec407a' },
  { id: 'white', color: '#fafafa' }, { id: 'black', color: '#212121' },
  { id: 'gray', color: '#757575' }, { id: 'brown', color: '#795548' }
]

const fitPreferences = [
  { id: 'slim', name: '修身', icon: '👔' },
  { id: 'regular', name: '合身', icon: '👕' },
  { id: 'oversized', name: '廓形', icon: '🧥' }
]

onMounted(() => {
  authStore.checkAuth()
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  userStore.loadProfile()
  // 从 store 复制到草稿
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
  heightInput.value = draft.height
  weightInput.value = draft.weight
})

const goBack = () => { trigger('light'); router.back() }

const getSeasonName = (skinToneId) => {
  const map = { fair_cool: '夏季人', fair_warm: '春季人', medium: '秋季人', tan: '秋季人', dark: '深冬人' }
  return map[skinToneId] || '未知'
}

const getColorRecommendation = (skinToneId) => {
  const tone = skinTones.find(t => t.id === skinToneId)
  return tone?.recommendation || '基础色'
}

const updateHeight = () => { trigger('light'); draft.height = Number(heightInput.value) || null }
const updateWeight = () => { trigger('light'); draft.weight = Number(weightInput.value) || null }
const selectSkinTone = (id) => { trigger('light'); draft.skinTone = id }
const selectBodyShape = (id) => { trigger('light'); draft.bodyShape = id }
const selectFaceFeature = (id) => { trigger('light'); draft.faceFeature = draft.faceFeature === id ? null : id }

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

const selectFit = (id) => { trigger('light'); draft.fitPreference = draft.fitPreference === id ? null : id }

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

const getSliderStyle = (axisId) => {
  const value = draft.styleAxes[axisId]
  const hue = (value / 100) * 120
  return { background: `linear-gradient(to right, hsl(${hue}, 70%, 50%), hsl(${hue}, 70%, 70%))` }
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
  font-size: 18px;
  color: var(--text-primary);
}

.edit-content {
  padding: 20px 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  margin-top: 8px;
}

.section-header h3 {
  font-size: 16px;
  color: var(--text-primary);
  margin: 0;
}

.profile-card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px var(--shadow-color);
  margin-bottom: 24px;
}

.edit-tip {
  text-align: center;
  padding: 8px;
  margin-bottom: 16px;
  background: rgba(91,154,139,0.08);
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.profile-item {
  margin-bottom: 20px;
}

.profile-item:last-child {
  margin-bottom: 0;
}

.profile-item label {
  display: block;
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 10px;
}

.body-metrics {
  display: flex;
  gap: 10px;
  align-items: center;
}

.metric-input {
  display: flex;
  align-items: center;
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 8px 14px;
  gap: 6px;
  flex: 1;
  min-width: 80px;
}

.metric-input input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  width: 50px;
}

.metric-unit { font-size: 12px; color: var(--text-tertiary); }

.bmi-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: var(--bg-secondary);
  padding: 8px 14px;
  border-radius: 12px;
  min-width: 55px;
}

.bmi-label { font-size: 10px; color: var(--text-tertiary); }
.bmi-value { font-size: 18px; font-weight: bold; color: var(--text-primary); }
.bmi-value.bmi-normal { color: #52c41a; }
.bmi-value.bmi-low { color: #faad14; }
.bmi-value.bmi-high, .bmi-value.bmi-obese { color: #ff4d4f; }

.color-options { display: flex; gap: 10px; flex-wrap: wrap; }

.color-chip {
  width: 48px;
  height: 56px;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  border: 2px solid var(--border-color);
  transition: all 0.25s;
}

.color-chip:active { transform: scale(0.95); }

.color-chip.active {
  border-color: var(--accent-color);
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(91,154,139,0.3);
}

.check-mark { font-size: 14px; font-weight: bold; }

.tone-label {
  font-size: 9px;
  color: var(--text-secondary);
  background: rgba(255,255,255,0.85);
  padding: 1px 4px;
  border-radius: 4px;
}

.color-chip.active .tone-label { background: var(--accent-color); color: white; }

.profile-hint {
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-secondary);
  padding: 10px 12px;
  background: rgba(91,154,139,0.08);
  border-radius: 8px;
}

.body-options { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }

.body-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 8px;
  background: var(--bg-secondary);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.body-option:active { transform: scale(0.95); }
.body-option.active { background: var(--primary-gradient); box-shadow: 0 4px 12px rgba(91,154,139,0.3); }
.body-silhouette { width: 32px; height: 48px; color: var(--text-tertiary); }
.body-option.active .body-silhouette { color: white; }
.body-name { font-size: 12px; font-weight: 500; color: var(--text-primary); }
.body-option.active .body-name { color: white; }

.face-options { display: flex; gap: 8px; flex-wrap: wrap; }

.face-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-secondary);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.face-chip:active { transform: scale(0.95); }
.face-chip.active { background: var(--primary-gradient); }
.face-icon { font-size: 16px; }
.face-name { font-size: 13px; color: var(--text-primary); }
.face-chip.active .face-name { color: white; }

.style-axes { display: flex; flex-direction: column; gap: 16px; }
.axis-item { display: flex; flex-direction: column; gap: 6px; }
.axis-labels { display: flex; justify-content: space-between; font-size: 11px; color: var(--text-tertiary); }

.axis-slider {
  -webkit-appearance: none;
  width: 100%;
  height: 8px;
  border-radius: 4px;
  outline: none;
}

.axis-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  cursor: pointer;
}

.axis-value { text-align: center; font-size: 12px; color: var(--accent-color); font-weight: 600; }

.style-tags { display: flex; flex-wrap: wrap; gap: 8px; }

.style-tag {
  display: flex;
  flex-direction: column;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: calc(50% - 4px);
}

.style-tag:active { transform: scale(0.98); }
.style-tag.active { background: var(--primary-gradient); }
.tag-name { font-size: 14px; font-weight: 500; color: var(--text-primary); }
.tag-desc { font-size: 10px; color: var(--text-tertiary); margin-top: 2px; }
.style-tag.active .tag-name { color: white; }
.style-tag.active .tag-desc { color: rgba(255,255,255,0.8); }

.color-preference { display: flex; gap: 8px; flex-wrap: wrap; }

.pref-color {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--border-color);
  transition: all 0.2s;
}

.pref-color:active { transform: scale(0.9); }
.pref-color.active { border-color: var(--accent-color); transform: scale(1.1); box-shadow: 0 2px 8px rgba(91,154,139,0.3); }
.pref-color.avoid.active { border-color: #ff4d4f; box-shadow: 0 2px 8px rgba(255,77,79,0.3); }
.pref-color.disabled { opacity: 0.3; cursor: not-allowed; }

.pref-color span {
  font-size: 14px;
  font-weight: bold;
  color: white;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

.pref-color.avoid span { color: #ff4d4f; }

.fit-options { display: flex; gap: 10px; }

.fit-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px;
  background: var(--bg-secondary);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.fit-option:active { transform: scale(0.95); }
.fit-option.active { background: var(--primary-gradient); }
.fit-icon { font-size: 24px; }
.fit-name { font-size: 13px; color: var(--text-primary); }
.fit-option.active .fit-name { color: white; }

.btn-confirm {
  display: block;
  width: 100%;
  margin-top: 24px;
  padding: 14px;
  background: var(--primary-gradient);
  border: none;
  border-radius: 14px;
  color: white;
  font-size: 16px;
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

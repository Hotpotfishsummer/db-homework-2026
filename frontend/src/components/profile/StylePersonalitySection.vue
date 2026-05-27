<template>
  <div>
    <div class="section-header">
      <h3>时尚人格</h3>
    </div>

    <div class="profile-card">
      <!-- 风格坐标 -->
      <div class="profile-item">
        <label>风格坐标</label>
        <div class="style-axes">
          <div class="axis-item" v-for="axis in styleAxes" :key="axis.id">
            <div class="axis-labels">
              <span>{{ axis.left }}</span>
              <span>{{ axis.right }}</span>
            </div>
            <input
              type="range" min="0" max="100"
              :value="styleAxesValues[axis.id]"
              @input="onAxisChange(axis.id, $event.target.value)"
              class="axis-slider"
              :style="getSliderStyle(axis.id)"
            />
            <div class="axis-value">{{ styleAxesValues[axis.id] }}</div>
          </div>
        </div>
      </div>

      <!-- 灵感标签 -->
      <div class="profile-item">
        <label>灵感标签</label>
        <div class="style-tags">
          <div
            v-for="style in styleTags" :key="style.id"
            class="style-tag"
            :class="{ active: selectedStyleTags.includes(style.id) }"
            @click="onToggleTag(style.id)"
          >
            <span class="tag-name">{{ style.name }}</span>
            <span class="tag-desc">{{ style.desc }}</span>
          </div>
        </div>
      </div>

      <!-- 红榜 -->
      <div class="profile-item">
        <label>红榜（喜欢的颜色）</label>
        <div class="color-preference">
          <div
            v-for="color in availableColors" :key="color.id"
            class="pref-color"
            :class="{ active: favoriteColors.includes(color.id), disabled: avoidColors.includes(color.id) }"
            :style="{ background: color.color }"
            @click="onToggleFavorite(color.id)"
          >
            <span v-if="favoriteColors.includes(color.id)">&#9829;</span>
          </div>
        </div>
      </div>

      <!-- 黑榜 -->
      <div class="profile-item">
        <label>黑榜（绝不尝试的颜色）</label>
        <div class="color-preference">
          <div
            v-for="color in availableColors" :key="color.id"
            class="pref-color avoid"
            :class="{ active: avoidColors.includes(color.id), disabled: favoriteColors.includes(color.id) }"
            :style="{ background: color.color }"
            @click="onToggleAvoid(color.id)"
          >
            <span v-if="avoidColors.includes(color.id)">&#10005;</span>
          </div>
        </div>
      </div>

      <!-- 版型偏好 -->
      <div class="profile-item">
        <label>版型偏好</label>
        <div class="fit-options">
          <div
            v-for="fit in fitPreferences" :key="fit.id"
            class="fit-option"
            :class="{ active: fitPreference === fit.id }"
            @click="onSelectFit(fit.id)"
          >
            <span class="fit-icon">{{ fit.icon }}</span>
            <span class="fit-name">{{ fit.name }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useHaptics } from '../../composables/useHaptics'

const props = defineProps({
  styleAxesValues: { type: Object, required: true },
  selectedStyleTags: { type: Array, required: true },
  favoriteColors: { type: Array, required: true },
  avoidColors: { type: Array, required: true },
  fitPreference: { type: String, default: null }
})

const emit = defineEmits([
  'update:styleAxesValues', 'toggleTag', 'toggleFavorite',
  'toggleAvoid', 'update:fitPreference'
])

const { trigger } = useHaptics()

const onAxisChange = (axisId, value) => {
  emit('update:styleAxesValues', { ...props.styleAxesValues, [axisId]: Number(value) })
}

const onToggleTag = (id) => { trigger('light'); emit('toggleTag', id) }
const onToggleFavorite = (id) => { trigger('light'); emit('toggleFavorite', id) }
const onToggleAvoid = (id) => { trigger('light'); emit('toggleAvoid', id) }
const onSelectFit = (id) => { trigger('light'); emit('update:fitPreference', props.fitPreference === id ? null : id) }

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

const getSliderStyle = (axisId) => {
  const value = props.styleAxesValues[axisId]
  const hue = (value / 100) * 120
  return { background: `linear-gradient(to right, hsl(${hue}, 70%, 50%), hsl(${hue}, 70%, 70%))` }
}
</script>

<style scoped>
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  margin-top: 8px;
}

.section-header h3 {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.374px;
  color: var(--text-primary);
  margin: 0;
}

.profile-card {
  background: var(--bg-card);
  border-radius: 18px;
  padding: 20px;
  border: 1px solid var(--hairline);
  margin-bottom: 24px;
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
.style-tag.active { background: var(--accent-color); }
.tag-name { font-size: 14px; font-weight: 400; color: var(--text-primary); }
.tag-desc { font-size: 10px; color: var(--text-tertiary); margin-top: 2px; }
.style-tag.active .tag-name { color: var(--on-primary); }
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
.pref-color.active { border-color: var(--accent-color); transform: scale(1.1); }
.pref-color.avoid.active { border-color: #ff4d4f; }
.pref-color.disabled { opacity: 0.3; cursor: not-allowed; }

.pref-color span {
  font-size: 14px;
  font-weight: 600;
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
.fit-option.active { background: var(--accent-color); }
.fit-icon { font-size: 24px; }
.fit-name { font-size: 13px; color: var(--text-primary); }
.fit-option.active .fit-name { color: var(--on-primary); }
</style>

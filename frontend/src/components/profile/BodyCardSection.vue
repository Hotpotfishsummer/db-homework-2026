<template>
  <div>
    <div class="section-header">
      <h3>数字人体卡片</h3>
    </div>

    <div class="profile-card">
      <div class="edit-tip">
        <span>点击选择，再次点击取消选择</span>
      </div>

      <!-- 基础维度 -->
      <div class="profile-item">
        <label>基础维度</label>
        <div class="body-metrics">
          <div class="metric-input">
            <input type="number" v-model="localHeight" placeholder="身高" @change="onHeightChange" />
            <span class="metric-unit">cm</span>
          </div>
          <div class="metric-input">
            <input type="number" v-model="localWeight" placeholder="体重" @change="onWeightChange" />
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
        <label>肤色定调</label>
        <div class="color-options">
          <div
            v-for="tone in skinTones" :key="tone.id"
            class="color-chip"
            :class="{ active: skinTone === tone.id }"
            :style="{ background: tone.color }"
            @click="$emit('update:skinTone', tone.id)"
          >
            <span v-if="skinTone === tone.id" class="check-mark">&#10003;</span>
            <span class="tone-label">{{ tone.name }}</span>
          </div>
        </div>
        <p class="profile-hint" v-if="skinTone">
          AI分析：你是「{{ getSeasonName(skinTone) }}」，适合{{ getColorRecommendation(skinTone) }}
        </p>
      </div>

      <!-- 体型选择 -->
      <div class="profile-item">
        <label>体型</label>
        <div class="body-options">
          <div
            v-for="body in bodyShapes" :key="body.id"
            class="body-option"
            :class="{ active: bodyShape === body.id }"
            @click="$emit('update:bodyShape', body.id)"
          >
            <div class="body-silhouette" v-html="body.svg"></div>
            <span class="body-name">{{ body.name }}</span>
          </div>
        </div>
      </div>

      <!-- 面部特征 -->
      <div class="profile-item">
        <label>面部特征（可选）</label>
        <div class="face-options">
          <div
            v-for="face in faceFeatures" :key="face.id"
            class="face-chip"
            :class="{ active: faceFeature === face.id }"
            @click="$emit('update:faceFeature', faceFeature === face.id ? null : face.id)"
          >
            <span class="face-icon">{{ face.icon }}</span>
            <span class="face-name">{{ face.name }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useHaptics } from '../../composables/useHaptics'

const props = defineProps({
  height: { type: Number, default: null },
  weight: { type: Number, default: null },
  skinTone: { type: String, default: null },
  bodyShape: { type: String, default: null },
  faceFeature: { type: String, default: null }
})

const emit = defineEmits([
  'update:height', 'update:weight', 'update:skinTone',
  'update:bodyShape', 'update:faceFeature'
])

const { trigger } = useHaptics()

const localHeight = defineModel('height')
const localWeight = defineModel('weight')

const onHeightChange = () => { trigger('light'); emit('update:height', Number(localHeight.value) || null) }
const onWeightChange = () => { trigger('light'); emit('update:weight', Number(localWeight.value) || null) }

const localBMI = computed(() => {
  if (props.height && props.weight) {
    const h = props.height / 100
    return (props.weight / (h * h)).toFixed(1)
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

const getSeasonName = (skinToneId) => {
  const map = { fair_cool: '夏季人', fair_warm: '春季人', medium: '秋季人', tan: '秋季人', dark: '深冬人' }
  return map[skinToneId] || '未知'
}

const getColorRecommendation = (skinToneId) => {
  const tone = skinTones.find(t => t.id === skinToneId)
  return tone?.recommendation || '基础色'
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

.edit-tip {
  text-align: center;
  padding: 8px;
  margin-bottom: 16px;
  background: rgba(0,102,204,0.08);
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
.bmi-value { font-size: 18px; font-weight: 600; color: var(--text-primary); }
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
}

.check-mark { font-size: 14px; font-weight: 600; }

.tone-label {
  font-size: 9px;
  color: var(--text-secondary);
  background: rgba(255,255,255,0.85);
  padding: 1px 4px;
  border-radius: 4px;
}

.color-chip.active .tone-label { background: var(--accent-color); color: var(--on-primary); }

.profile-hint {
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-secondary);
  padding: 10px 12px;
  background: rgba(0,102,204,0.08);
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
.body-option.active { background: var(--accent-color); }
.body-silhouette { width: 32px; height: 48px; color: var(--text-tertiary); }
.body-option.active .body-silhouette { color: var(--on-primary); }
.body-name { font-size: 12px; font-weight: 400; color: var(--text-primary); }
.body-option.active .body-name { color: var(--on-primary); }

.face-options { display: flex; gap: 8px; flex-wrap: wrap; }

.face-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-secondary);
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.2s;
}

.face-chip:active { transform: scale(0.95); }
.face-chip.active { background: var(--accent-color); }
.face-icon { font-size: 16px; }
.face-name { font-size: 13px; color: var(--text-primary); }
.face-chip.active .face-name { color: var(--on-primary); }
</style>

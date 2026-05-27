<template>
  <div class="match-filter">
    <div class="filter-section">
      <h3 class="section-label">🎯 选择场景</h3>
      <div class="scene-tabs">
        <div
          v-for="scene in scenes"
          :key="scene.id"
          class="scene-tab"
          :class="{ active: selectedScene === scene.id }"
          @click="onSelectScene(scene.id)"
        >
          <span class="scene-icon">{{ scene.icon }}</span>
          <span class="scene-name">{{ scene.name }}</span>
        </div>
      </div>
    </div>

    <div class="filter-section">
      <h3 class="section-label">🌤️ 今日天气</h3>
      <div class="weather-row" @click="toggleWeatherPicker">
        <div class="weather-info">
          <span class="weather-icon">{{ weather.icon }}</span>
          <span class="weather-text">{{ weather.desc }} {{ weather.temp }}°C</span>
        </div>
        <span class="weather-arrow">›</span>
      </div>
      <Transition name="fade">
        <div v-if="showWeatherPicker" class="weather-picker">
          <div
            v-for="w in weatherOptions"
            :key="w.temp"
            class="weather-option"
            :class="{ selected: weather.temp === w.temp }"
            @click="selectWeather(w)"
          >
            <span>{{ w.icon }}</span>
            <span>{{ w.desc }} {{ w.temp }}°C</span>
          </div>
        </div>
      </Transition>
    </div>

    <button class="generate-btn" @click="onGenerate">
      <span class="btn-icon">✨</span>
      <span>开始生成</span>
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useHaptics } from '../../composables/useHaptics'

const emit = defineEmits(['generate'])
const { trigger } = useHaptics()

const scenes = [
  { id: 'commute', name: '通勤', icon: '💼' },
  { id: 'date', name: '约会', icon: '💕' },
  { id: 'casual', name: '休闲', icon: '☕' },
  { id: 'sports', name: '运动', icon: '🏃' },
  { id: 'party', name: '派对', icon: '🎉' }
]

const weatherOptions = [
  { desc: '晴天', temp: 22, icon: '☀️' },
  { desc: '多云', temp: 18, icon: '⛅' },
  { desc: '阴天', temp: 12, icon: '☁️' },
  { desc: '小雨', temp: 10, icon: '🌧️' },
  { desc: '大风', temp: 8, icon: '💨' }
]

const selectedScene = ref('casual')
const weather = ref(weatherOptions[0])
const showWeatherPicker = ref(false)

const onSelectScene = (scene) => {
  trigger('light')
  selectedScene.value = scene
}

const toggleWeatherPicker = () => {
  trigger('light')
  showWeatherPicker.value = !showWeatherPicker.value
}

const selectWeather = (w) => {
  trigger('light')
  weather.value = w
  showWeatherPicker.value = false
}

const onGenerate = () => {
  trigger('success')
  emit('generate', {
    scene: selectedScene.value,
    weather: weather.value
  })
}
</script>

<style scoped>
.match-filter {
  padding: 20px;
}

.filter-section {
  margin-bottom: 24px;
}

.section-label {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  letter-spacing: -0.374px;
}

.scene-tabs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.scene-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: var(--bg-card);
  border-radius: 9999px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid var(--hairline);
  user-select: none;
}

.scene-tab:active {
  transform: scale(0.95);
}

.scene-tab.active {
  background: var(--accent-color);
  color: var(--on-primary);
  border-color: var(--accent-color);
}

.scene-icon {
  font-size: 16px;
}

.scene-name {
  font-weight: 400;
}

.weather-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: var(--bg-card);
  border-radius: 18px;
  border: 1px solid var(--hairline);
  cursor: pointer;
  transition: all 0.2s;
}

.weather-row:active {
  transform: scale(0.98);
}

.weather-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.weather-icon {
  font-size: 28px;
}

.weather-text {
  font-size: 17px;
  color: var(--text-primary);
  font-weight: 400;
}

.weather-arrow {
  font-size: 22px;
  color: var(--text-tertiary);
}

.weather-picker {
  margin-top: 8px;
  background: var(--bg-card);
  border-radius: 18px;
  padding: 8px;
  border: 1px solid var(--hairline);
}

.weather-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.weather-option:active {
  background: var(--bg-secondary);
}

.weather-option.selected {
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-weight: 500;
}

.generate-btn {
  width: 100%;
  padding: 11px 22px;
  background: var(--accent-color);
  border: none;
  border-radius: 9999px;
  color: var(--on-primary);
  font-size: 17px;
  font-weight: 400;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: transform 0.2s;
  margin-top: 8px;
}

.generate-btn:active {
  transform: scale(0.95);
}

.btn-icon {
  font-size: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>

import { API_BASE_URL } from './api'
import { useAuthStore } from '../stores/auth'

export async function fetchDailyTip() {
  const authStore = useAuthStore()
  const token = authStore.token || localStorage.getItem('token')

  const response = await fetch(`${API_BASE_URL}/daily-tips/`, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })

  const payload = await response.json().catch(() => ({}))
  if (!response.ok || payload.code !== 200) {
    const message = payload?.msg || `每日贴士加载失败 (HTTP ${response.status})`
    throw new Error(message)
  }
  return payload.data
}

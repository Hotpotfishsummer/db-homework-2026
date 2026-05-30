/**
 * 衣服相关 Service
 * 对接后端 POST /api/v1/garments/upload
 */

import { API_BASE_URL } from './api'
import { compressImage, validateImage } from './user'
import { useAuthStore } from '../stores/auth'

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/jpg']
const MAX_SIZE = 10 * 1024 * 1024 // 10MB

const getAuthToken = () => {
  const authStore = useAuthStore()
  return authStore.token || localStorage.getItem('token') || ''
}

const createAuthHeaders = () => ({
  ...(getAuthToken() ? { Authorization: `Bearer ${getAuthToken()}` } : {}),
})

/**
 * 上传衣服图片
 * @param {File} file - 图片文件
 * @returns {Promise<{code: number, data: GarmentUploadResponse, msg: string}>}
 */
export const uploadGarment = async (file) => {
  const validation = validateImage(file)
  if (!validation.valid) {
    return { code: 400, msg: validation.error }
  }

  if (file.size > MAX_SIZE) {
    return { code: 400, msg: '图片大小不能超过 10MB' }
  }

  const formData = new FormData()
  formData.append('image', file)

  try {
    const response = await fetch(`${API_BASE_URL}/garments/upload`, {
      method: 'POST',
      headers: createAuthHeaders(),
      body: formData
    })

    const data = await response.json()

    if (!response.ok) {
      return { code: response.status, msg: data.detail || '上传失败' }
    }

    return { code: 200, data, msg: '上传成功' }
  } catch (error) {
    console.error('上传衣服失败:', error)
    return { code: 500, msg: '网络错误，请重试' }
  }
}

/**
 * 压缩并上传衣服图片（推荐）
 * @param {File} file - 图片文件
 * @param {number} quality - 压缩质量 0-1
 * @returns {Promise<{code: number, data: GarmentUploadResponse, msg: string}>}
 */
export const compressAndUploadGarment = async (file, quality = 0.8) => {
  try {
    const base64 = await compressImage(file, quality)
    const response = await fetch(base64)
    const blob = await response.blob()
    const compressedFile = new File([blob], file.name, { type: 'image/jpeg' })
    return uploadGarment(compressedFile)
  } catch (error) {
    return uploadGarment(file)
  }
}

/**
 * 拉取当前用户的衣物列表
 * @returns {Promise<{code:number, data:Object, msg:string}>}
 */
export const listGarments = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/garments/`, {
      method: 'GET',
      headers: createAuthHeaders(),
    })

    const data = await response.json()
    if (!response.ok) {
      return { code: response.status, msg: data.detail || '获取衣物列表失败' }
    }

    return { code: 200, data, msg: 'ok' }
  } catch (error) {
    console.error('获取衣物列表失败:', error)
    return { code: 500, msg: '网络错误' }
  }
}
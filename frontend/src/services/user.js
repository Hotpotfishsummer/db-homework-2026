/**
 * 用户相关 Service
 * 模拟网络请求，支持随时切换真实后端
 */

// 允许的图片格式
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/jpg']
// 最大文件大小 2MB
const MAX_SIZE = 2 * 1024 * 1024

/**
 * 上传头像
 * @param {File} file - 图片文件
 * @returns {Promise<{code: number, data: {url: string}, msg: string}>}
 */
export const uploadAvatar = (file) => {
  return new Promise((resolve, reject) => {
    // 1. 前端校验
    if (!ALLOWED_TYPES.includes(file.type)) {
      reject({ code: 400, msg: '只支持 JPG/PNG 格式' })
      return
    }

    if (file.size > MAX_SIZE) {
      reject({ code: 400, msg: '图片大小不能超过 2MB' })
      return
    }

    // 2. 模拟网络延迟 1.5s
    setTimeout(() => {
      // 模拟 5% 概率上传失败
      if (Math.random() < 0.05) {
        reject({ code: 500, msg: '网络拥堵，请重试' })
        return
      }

      // 3. 读取文件为 Base64
      const reader = new FileReader()
      reader.onload = (e) => {
        resolve({
          code: 200,
          data: { url: e.target.result },
          msg: '上传成功'
        })
      }
      reader.onerror = () => {
        reject({ code: 500, msg: '文件读取失败' })
      }
      reader.readAsDataURL(file)
    }, 1500)
  })
}

/**
 * 压缩图片
 * @param {File} file - 原文件
 * @param {number} quality - 质量 0-1
 * @returns {Promise<string>} Base64
 */
export const compressImage = (file, quality = 0.8) => {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')

      // 限制最大尺寸 200x200
      const maxSize = 200
      let { width, height } = img
      if (width > maxSize || height > maxSize) {
        if (width > height) {
          height = (height / width) * maxSize
          width = maxSize
        } else {
          width = (width / height) * maxSize
          height = maxSize
        }
      }

      canvas.width = width
      canvas.height = height
      ctx.drawImage(img, 0, 0, width, height)

      resolve(canvas.toDataURL('image/jpeg', quality))
    }
    img.onerror = reject
    img.src = URL.createObjectURL(file)
  })
}

/**
 * 验证图片
 * @param {File} file
 * @returns {{valid: boolean, error?: string}}
 */
export const validateImage = (file) => {
  if (!file) {
    return { valid: false, error: '请选择图片' }
  }
  if (!ALLOWED_TYPES.includes(file.type)) {
    return { valid: false, error: '只支持 JPG/PNG 格式' }
  }
  if (file.size > MAX_SIZE) {
    return { valid: false, error: '图片大小不能超过 2MB' }
  }
  return { valid: true }
}
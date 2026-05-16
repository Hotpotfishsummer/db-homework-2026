/**
 * API 配置
 * 所有 API 地址集中管理
 */

// API 基础地址（开发环境）
// TODO: 上线前替换为正式地址
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'

// 超时时间（毫秒）
const API_TIMEOUT = 15000

export { API_BASE_URL, API_TIMEOUT }

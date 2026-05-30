import { API_BASE_URL } from './api'

const request = async (path, { method = 'POST', body, token } = {}) => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      ...(body ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: body ? JSON.stringify(body) : undefined
  })

  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw payload
  }
  return payload
}

export const loginRequest = (username, password) =>
  request('/auth/login', {
    body: { username, password }
  })

export const registerRequest = (username, password) =>
  request('/auth/register', {
    body: { username, password }
  })

export const fetchCurrentUser = (token) =>
  request('/user/me', {
    method: 'GET',
    token
  })
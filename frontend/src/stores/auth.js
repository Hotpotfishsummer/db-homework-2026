import { defineStore } from 'pinia'
import { fetchCurrentUser, loginRequest, registerRequest } from '../services/auth'

const STORAGE_TOKEN = 'token'
const STORAGE_USER = 'currentUser'

const persistSession = (token, user) => {
  localStorage.setItem(STORAGE_TOKEN, token)
  localStorage.setItem(STORAGE_USER, JSON.stringify(user))
}

const clearSession = () => {
  localStorage.removeItem(STORAGE_TOKEN)
  localStorage.removeItem(STORAGE_USER)
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    token: null
  }),

  actions: {
    async login(username, password) {
      const response = await loginRequest(username, password)
      this.token = response.access_token
      this.user = response.user
      this.isAuthenticated = true
      persistSession(this.token, this.user)
      return response
    },

    async register(username, password) {
      return registerRequest(username, password)
    },

    logout() {
      this.user = null
      this.isAuthenticated = false
      this.token = null
      clearSession()
    },

    checkAuth() {
      const token = localStorage.getItem(STORAGE_TOKEN)
      const user = localStorage.getItem(STORAGE_USER)
      if (token && user) {
        this.token = token
        this.user = JSON.parse(user)
        this.isAuthenticated = true
        return true
      }

      this.user = null
      this.token = null
      this.isAuthenticated = false
      return false
    },

    async validateSession() {
      if (!this.checkAuth()) {
        return false
      }

      try {
        const profile = await fetchCurrentUser(this.token)
        this.user = profile
        this.isAuthenticated = true
        persistSession(this.token, profile)
        return true
      } catch (error) {
        this.logout()
        throw error
      }
    }
  }
})
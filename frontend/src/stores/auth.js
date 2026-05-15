// Pinia 状态管理（异步 Mock）

import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    token: null
  }),

  actions: {
    async login(username, password) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const users = JSON.parse(localStorage.getItem('mock_users') || '[]')
          const user = users.find(u => u.username === username && u.password === password)

          if (user) {
            this.user = user
            this.isAuthenticated = true
            this.token = 'mock_token_' + Date.now()
            localStorage.setItem('token', this.token)
            localStorage.setItem('currentUser', JSON.stringify(user))
            resolve({ code: 200, msg: '登录成功' })
          } else {
            reject({ code: 400, msg: '账号或密码错误' })
          }
        }, 800)
      })
    },

    async register(username, password) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const users = JSON.parse(localStorage.getItem('mock_users') || '[]')
          const existingUser = users.find(u => u.username === username)

          if (existingUser) {
            reject({ code: 400, msg: '该账号已存在' })
          } else {
            const newUser = { username, password, createdAt: new Date().toISOString() }
            users.push(newUser)
            localStorage.setItem('mock_users', JSON.stringify(users))
            resolve({ code: 200, msg: '注册成功' })
          }
        }, 800)
      })
    },

    logout() {
      this.user = null
      this.isAuthenticated = false
      this.token = null
      localStorage.removeItem('token')
      localStorage.removeItem('currentUser')
    },

    checkAuth() {
      const token = localStorage.getItem('token')
      const user = localStorage.getItem('currentUser')
      if (token && user) {
        this.token = token
        this.user = JSON.parse(user)
        this.isAuthenticated = true
      }
    }
  }
})
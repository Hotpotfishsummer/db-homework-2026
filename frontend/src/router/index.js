// 路由 + 全局守卫

import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import HomeView from '../views/HomeView.vue'
import WardrobeView from '../views/WardrobeView.vue'
import ProfileView from '../views/ProfileView.vue'
import OutfitDetailView from '../views/OutfitDetailView.vue'
import LikedView from '../views/LikedView.vue'
import HistoryView from '../views/HistoryView.vue'
import OutfitMatchView from '../views/OutfitMatchView.vue'
import AddClothView from '../views/AddClothView.vue'
import ProfileEditView from '../views/ProfileEditView.vue'
import ProfileSettingsView from '../views/ProfileSettingsView.vue'
import DesktopLayout from '../components/layout/DesktopLayout.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/',
      component: DesktopLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: 'home',
          name: 'home',
          component: HomeView
        },
        {
          path: 'wardrobe',
          name: 'wardrobe',
          component: WardrobeView
        },
        {
          path: 'profile',
          name: 'profile',
          component: ProfileView
        },
        {
          path: 'outfit/:id',
          name: 'outfit-detail',
          component: OutfitDetailView
        },
        {
          path: 'liked',
          name: 'liked',
          component: LikedView
        },
        {
          path: 'history',
          name: 'history',
          component: HistoryView
        },
        {
          path: 'add-cloth',
          name: 'add-cloth',
          component: AddClothView
        },
        {
          path: 'outfit-match',
          name: 'outfit-match',
          component: OutfitMatchView
        },
        {
          path: 'profile/edit',
          name: 'profile-edit',
          component: ProfileEditView
        },
        {
          path: 'profile/settings',
          name: 'profile-settings',
          component: ProfileSettingsView
        }
      ]
    }
  ]
})

let devSkipLoginChecked = false

async function checkDevSkipLogin() {
  if (!import.meta.env.DEV || devSkipLoginChecked) return
  devSkipLoginChecked = true
  try {
    const res = await fetch('/.dev_skip_login')
    if (res.ok) {
      const mockToken = 'dev-token-' + Date.now()
      const mockUser = { id: 0, username: 'dev_user', nickname: '开发者' }
      localStorage.setItem('token', mockToken)
      localStorage.setItem('currentUser', JSON.stringify(mockUser))
    }
  } catch {}
}

router.beforeEach(async (to, from, next) => {
  await checkDevSkipLogin()

  const authStore = useAuthStore()
  const isAuthenticated = authStore.checkAuth()

  if (isAuthenticated) {
    const isDevToken = import.meta.env.DEV && authStore.token?.startsWith('dev-token-')
    if (!isDevToken) {
      try {
        await authStore.validateSession()
      } catch {
        next('/login')
        return
      }
    }
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    next('/home')
  } else {
    next()
  }
})

export default router
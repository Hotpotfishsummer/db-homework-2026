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
      path: '/home',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/wardrobe',
      name: 'wardrobe',
      component: WardrobeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true }
    },
    {
      path: '/outfit/:id',
      name: 'outfit-detail',
      component: OutfitDetailView,
      meta: { requiresAuth: true }
    },
    {
      path: '/liked',
      name: 'liked',
      component: LikedView,
      meta: { requiresAuth: true }
    },
    {
      path: '/history',
      name: 'history',
      component: HistoryView,
      meta: { requiresAuth: true }
    },
    {
      path: '/add-cloth',
      name: 'add-cloth',
      component: AddClothView,
      meta: { requiresAuth: true }
    },
    {
      path: '/outfit-match',
      name: 'outfit-match',
      component: OutfitMatchView,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token')
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    next('/home')
  } else {
    next()
  }
})

export default router
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/sy' },
  {
    path: '/sy',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/books',
    name: 'books',
    component: () => import('@/views/BookListView.vue'),
  },
  {
    path: '/book/:id',
    name: 'book-detail',
    component: () => import('@/views/BookDetailView.vue'),
  },
  {
    path: '/shjs',
    name: 'business',
    component: () => import('@/views/BusinessView.vue'),
  },
  {
    path: '/shhy',
    name: 'column',
    component: () => import('@/views/ColumnView.vue'),
  },
  {
    path: '/shhy/:id',
    name: 'column-detail',
    component: () => import('@/views/ArticleDetailView.vue'),
  },
  {
    path: '/shxw',
    name: 'order',
    component: () => import('@/views/OrderView.vue'),
  },
  {
    path: '/zpxx',
    name: 'company',
    component: () => import('@/views/CompanyView.vue'),
  },
  {
    path: '/contact',
    name: 'contact',
    component: () => import('@/views/ContactView.vue'),
  },
  {
    path: '/information',
    name: 'information',
    component: () => import('@/views/DownloadView.vue'),
  },
  {
    path: '/admin/login',
    name: 'admin-login',
    component: () => import('@/views/AdminLoginView.vue'),
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'admin', component: () => import('@/views/AdminView.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth) {
    const auth = useAuthStore()
    if (!auth.isLoggedIn) {
      return { name: 'admin-login' }
    }
  }
})

export default router

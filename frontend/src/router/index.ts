import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

/**
 * 路由配置
 * 包含公开路由和需要登录/管理员权限的受保护路由
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/entry',
  },
  {
    path: '/entry',
    name: 'Entry',
    component: () => import('@/views/visitor/EntryPage.vue'),
  },
  {
    path: '/exit',
    name: 'Exit',
    component: () => import('@/views/visitor/ExitPage.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginPage.vue'),
  },
  {
    path: '/staff/entry',
    name: 'StaffEntry',
    component: () => import('@/views/staff/StaffEntryPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/staff/exit',
    name: 'StaffExit',
    component: () => import('@/views/staff/StaffExitPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/dashboard/DashboardPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/screen',
    name: 'Screen',
    component: () => import('@/views/screen/ScreenPage.vue'),
  },
  {
    path: '/admin/config',
    name: 'AdminConfig',
    component: () => import('@/views/admin/ActivityConfigPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/logs',
    name: 'AdminLogs',
    component: () => import('@/views/admin/LogsPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/report',
    name: 'AdminReport',
    component: () => import('@/views/admin/ReportPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

/**
 * 路由守卫：检查登录状态和管理员权限
 *
 * - Token 不存在 & 访问需登录页面 → 重定向到 /login
 * - Token 存在 & 访问登录页 → 重定向到 /dashboard
 * - 管理员权限检查：从 localStorage 读取用户信息验证角色
 */
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')

  // 需要登录但无 token → 跳转登录页
  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 已登录但访问登录页 → 跳转控制台
  if (to.name === 'Login' && token) {
    next({ name: 'Dashboard' })
    return
  }

  // 需要管理员权限 → 从 localStorage 读取用户角色校验
  if (to.meta.requiresAdmin) {
    if (!token) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    try {
      const userStr = localStorage.getItem('user')
      const user = userStr ? JSON.parse(userStr) : null
      if (user?.role !== 'admin') {
        next({ name: 'Dashboard' })
        return
      }
    } catch {
      next({ name: 'Dashboard' })
      return
    }
  }

  next()
})

export default router

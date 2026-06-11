import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { post } from '@/utils/request'
import router from '@/router'

/**
 * 认证状态管理
 * 管理用户登录状态、token、用户信息
 */
export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const user = ref<{ id: number; username: string; role: string } | null>(null)

  /** 是否已登录 */
  const isLoggedIn = computed(() => !!token.value)

  /** 是否为管理员 */
  const isAdmin = computed(() => user.value?.role === 'admin')

  /** 登录 */
  async function login(username: string, password: string) {
    const res = await post('/auth/login', { username, password })
    token.value = res.access_token
    user.value = { id: res.user_id, username: res.username, role: res.role }
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  /** 登出 */
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  /** 尝试从 localStorage 恢复用户信息 */
  function restoreUser() {
    const saved = localStorage.getItem('user')
    if (saved) {
      try {
        user.value = JSON.parse(saved)
      } catch {
        user.value = null
      }
    }
  }

  return { token, user, isLoggedIn, isAdmin, login, logout, restoreUser }
})

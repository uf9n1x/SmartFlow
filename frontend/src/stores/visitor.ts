import { defineStore } from 'pinia'
import { ref } from 'vue'
import { post, get } from '@/utils/request'

/**
 * 游客状态管理
 * 管理游客进出场登记数据
 */
export const useVisitorStore = defineStore('visitor', () => {
  /** 加载状态 */
  const loading = ref(false)

  /** 最近一次操作结果 */
  const lastResult = ref<{
    success: boolean
    message: string
    currentPeople?: number
  } | null>(null)

  /** 是否达到人数上限 */
  const isFull = ref(false)

  /** 当前区域人数 */
  const currentPeople = ref(0)

  /** 人数上限 */
  const maxCapacity = ref(500)

  /**
   * 检查活动配置，判断是否达到人数上限
   */
  async function checkCapacity() {
    try {
      const res: any = await get('/dashboard')
      if (res) {
        currentPeople.value = res.current_people ?? 0
        maxCapacity.value = res.max_people ?? 500
        isFull.value = currentPeople.value >= maxCapacity.value
      }
    } catch {
      // 获取配置失败时允许继续操作
      isFull.value = false
    }
  }

  /**
   * 提交进场登记
   */
  async function submitEntry(count: number) {
    loading.value = true
    lastResult.value = null
    try {
      const res: any = await post('/visitor/entry', { count })
      currentPeople.value = res.current_people ?? currentPeople.value + count
      isFull.value = currentPeople.value >= maxCapacity.value
      lastResult.value = {
        success: true,
        message: res.message || '登记成功',
        currentPeople: currentPeople.value,
      }
    } catch (e: any) {
      const msg = e.response?.data?.detail || '登记失败，请稍后重试'
      lastResult.value = { success: false, message: msg }
    } finally {
      loading.value = false
    }
  }

  /**
   * 提交出场登记
   */
  async function submitExit(count: number) {
    loading.value = true
    lastResult.value = null
    try {
      const res: any = await post('/visitor/exit', { count })
      currentPeople.value = res.current_people ?? Math.max(0, currentPeople.value - count)
      isFull.value = currentPeople.value >= maxCapacity.value
      lastResult.value = {
        success: true,
        message: res.message || '登记成功',
        currentPeople: currentPeople.value,
      }
    } catch (e: any) {
      const msg = e.response?.data?.detail || '登记失败，请稍后重试'
      lastResult.value = { success: false, message: msg }
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    lastResult,
    isFull,
    currentPeople,
    maxCapacity,
    checkCapacity,
    submitEntry,
    submitExit,
  }
})

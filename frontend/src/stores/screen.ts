import { defineStore } from 'pinia'
import { ref } from 'vue'
import { get } from '@/utils/request'

/**
 * 大屏展示状态管理
 * 管理大屏实时数据（当前人数、进出统计、使用率）及操作日志
 */
export const useScreenStore = defineStore('screen', () => {
  /** 当前区域内人数 */
  const currentPeople = ref(0)
  /** 最大承载人数 */
  const maxPeople = ref(500)
  /** 今日进场总人次 */
  const todayEntry = ref(0)
  /** 今日离场总人次 */
  const todayExit = ref(0)
  /** 区域使用率（百分比） */
  const usageRate = ref(0)
  /** 最近操作记录列表 */
  const recentLogs = ref<any[]>([])
  /** 数据加载状态 */
  const loading = ref(false)

  /**
   * 获取大屏概览数据
   * 请求 /api/v1/dashboard 接口
   */
  async function fetchScreenData() {
    loading.value = true
    const res = await get('/dashboard')
    currentPeople.value = res.current_people || 0
    maxPeople.value = res.max_people || 500
    todayEntry.value = res.today_entry || 0
    todayExit.value = res.today_exit || 0
    usageRate.value = res.usage_rate || 0
    loading.value = false
  }

  /**
   * 获取最近操作日志
   * 请求 /api/v1/logs 接口，取前10条
   */
  async function fetchRecentLogs() {
    const res = await get('/logs', { page: 1, page_size: 10 })
    recentLogs.value = res.items || []
  }

  /**
   * 根据 WebSocket 推送数据更新状态
   * @param data - WebSocket 推送的实时数据
   */
  function updateFromWs(data: any) {
    if (data.current_people !== undefined) currentPeople.value = data.current_people
    if (data.max_people !== undefined) maxPeople.value = data.max_people
    if (data.today_entry !== undefined) todayEntry.value = data.today_entry
    if (data.today_exit !== undefined) todayExit.value = data.today_exit
    if (data.usage_rate !== undefined) usageRate.value = data.usage_rate
  }

  return {
    currentPeople,
    maxPeople,
    todayEntry,
    todayExit,
    usageRate,
    recentLogs,
    loading,
    fetchScreenData,
    fetchRecentLogs,
    updateFromWs,
  }
})

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { get, put } from '@/utils/request'

/**
 * 仪表盘状态管理
 * 管理区域人数统计的实时数据
 */
export const useDashboardStore = defineStore('dashboard', () => {
  /** 当前区域人数 */
  const currentPeople = ref(0)
  /** 最大人数上限 */
  const maxPeople = ref(500)
  /** 今日进场人数 */
  const todayEntry = ref(0)
  /** 今日出场人数 */
  const todayExit = ref(0)
  /** 总进场人数 */
  const totalEntry = ref(0)
  /** 总出场人数 */
  const totalExit = ref(0)
  /** 单次提交限制 */
  const singleSubmitLimit = ref(10)
  /** 数据加载状态 */
  const loading = ref(false)

  /** 剩余容量 */
  const remainingCapacity = computed(() => Math.max(0, maxPeople.value - currentPeople.value))
  /** 使用率（百分比） */
  const usageRate = computed(() => maxPeople.value > 0 ? Math.round((currentPeople.value / maxPeople.value) * 100) : 0)
  /** 是否已达上限 */
  const isFull = computed(() => currentPeople.value >= maxPeople.value)

  /**
   * 从后端获取 Dashboard 数据
   */
  async function fetchDashboard() {
    loading.value = true
    try {
      const res: any = await get('/dashboard')
      currentPeople.value = res.current_people || 0
      maxPeople.value = res.max_people || 500
      todayEntry.value = res.today_entry || 0
      todayExit.value = res.today_exit || 0
      totalEntry.value = res.total_entry || 0
      totalExit.value = res.total_exit || 0
      singleSubmitLimit.value = res.single_submit_limit || 10
    } finally {
      loading.value = false
    }

    // 同时获取配置信息
    try {
      const configRes: any = await get('/activity/config')
      singleSubmitLimit.value = configRes.single_submit_limit ?? 10
    } catch (_) {}
  }

  /**
   * WebSocket 推送更新
   * 根据推送数据增量更新各指标
   */
  function updateFromWs(data: any) {
    if (data.current_people !== undefined) currentPeople.value = data.current_people
    if (data.max_people !== undefined) maxPeople.value = data.max_people
    if (data.today_entry !== undefined) todayEntry.value = data.today_entry
    if (data.today_exit !== undefined) todayExit.value = data.today_exit
    if (data.total_entry !== undefined) totalEntry.value = data.total_entry
    if (data.total_exit !== undefined) totalExit.value = data.total_exit
    if (data.single_submit_limit !== undefined) singleSubmitLimit.value = data.single_submit_limit
  }

  /**
   * 更新活动配置（最大人数或单次限制）
   */
  async function updateActivityConfig(data: Record<string, any>) {
    await put('/activity/config', data)
    // 更新本地状态
    if (data.max_people !== undefined) maxPeople.value = data.max_people
    if (data.single_submit_limit !== undefined) singleSubmitLimit.value = data.single_submit_limit
  }

  return {
    currentPeople,
    maxPeople,
    todayEntry,
    todayExit,
    totalEntry,
    totalExit,
    loading,
    remainingCapacity,
    usageRate,
    isFull,
    singleSubmitLimit,
    updateActivityConfig,
    fetchDashboard,
    updateFromWs,
  }
})

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { get, put, downloadFile } from '@/utils/request'

/**
 * 管理后台状态管理
 * 管理活动配置、操作日志、报表导出等数据
 */
export const useAdminStore = defineStore('admin', () => {
  // ==================== 活动配置 ====================

  /** 活动配置信息 */
  const config = ref<{
    activity_name: string
    max_people: number
    current_people: number
    single_submit_limit: number
  } | null>(null)

  /** 获取活动配置 */
  async function fetchConfig() {
    const res = await get('/activity/config')
    config.value = res as any
  }

  /** 更新活动配置 */
  async function updateConfig(data: {
    max_people?: number
    single_submit_limit?: number
    activity_name?: string
  }) {
    await put('/activity/config', data)
    await fetchConfig()
  }

  // ==================== 操作日志 ====================

  /** 日志列表 */
  const logs = ref<any[]>([])
  /** 日志总数 */
  const logsTotal = ref(0)
  /** 日志加载状态 */
  const logsLoading = ref(false)

  /** 获取操作日志 */
  async function fetchLogs(params: {
    page?: number
    page_size?: number
    operation_type?: string
    source_type?: string
    start_date?: string
    end_date?: string
  }) {
    logsLoading.value = true
    try {
      const res = await get('/logs', params)
      logs.value = (res as any).items || []
      logsTotal.value = (res as any).total || 0
    } finally {
      logsLoading.value = false
    }
  }

  // ==================== 报表导出 ====================

  /** 导出状态 */
  const exporting = ref(false)

  /** 导出数据报表 */
  async function exportReport(params: {
    start_date?: string
    end_date?: string
    granularity: string
    format: string
  }) {
    exporting.value = true
    try {
      await downloadFile('/report/export', params)
    } finally {
      exporting.value = false
    }
  }

  return {
    config,
    fetchConfig,
    updateConfig,
    logs,
    logsTotal,
    logsLoading,
    fetchLogs,
    exporting,
    exportReport,
  }
})

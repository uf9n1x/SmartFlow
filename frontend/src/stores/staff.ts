import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { get, post } from '@/utils/request'
import { ElMessage } from 'element-plus'

/**
 * 工作人员状态管理
 * 管理工作人员进出场登记数据
 */
export const useStaffStore = defineStore('staff', () => {
  const loading = ref(false)

  // 容量信息
  const currentPeople = ref(0)
  const maxPeople = ref(500)
  const remainingCapacity = computed(() => Math.max(0, maxPeople.value - currentPeople.value))

  /** 快捷数量按钮 */
  const quickCounts = {
    entry: [1, 2, 3, 5, 10],
    exit: [1, 2, 3, 5, 10],
  }

  /** 获取当前容量信息 */
  async function fetchCapacity() {
    try {
      const res: any = await get('/dashboard')
      currentPeople.value = res.current_people ?? 0
      maxPeople.value = res.max_people ?? 500
    } catch { /* ignore */ }
  }

  /** 工作人员进场 */
  async function staffEntry(count: number) {
    loading.value = true
    try {
      const res: any = await post('/staff/entry', { count })
      ElMessage.success(`进场 ${count} 人成功，当前区域人数：${res.current_people}`)
      await fetchCapacity() // 刷新容量
    } catch (e: any) {
      ElMessage.error(e.response?.data?.detail || '操作失败')
    } finally {
      loading.value = false
    }
  }

  /** 工作人员出场 */
  async function staffExit(count: number) {
    loading.value = true
    try {
      const res: any = await post('/staff/exit', { count })
      ElMessage.success(`出场 ${count} 人成功，当前区域人数：${res.current_people}`)
      await fetchCapacity() // 刷新容量
    } catch (e: any) {
      ElMessage.error(e.response?.data?.detail || '操作失败')
    } finally {
      loading.value = false
    }
  }

  return { loading, currentPeople, maxPeople, remainingCapacity, fetchCapacity, quickCounts, staffEntry, staffExit }
})

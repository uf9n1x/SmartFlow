<template>
  <div class="admin-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/">
      <el-breadcrumb-item :to="{ path: '/dashboard' }">管理后台</el-breadcrumb-item>
      <el-breadcrumb-item>数据报表导出</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">数据报表导出</h1>
      <p class="page-desc">导出指定时间段内的进出场统计数据，支持多种粒度和格式</p>
    </div>

    <!-- 报表导出卡片 -->
    <el-card class="report-card" shadow="never">
      <template #header>
        <span class="card-header-title">导出参数设置</span>
      </template>

      <el-form label-position="top" class="report-form">
        <!-- 日期范围 -->
        <el-form-item label="统计日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%; max-width: 380px"
          />
          <div class="form-item-tip">留空则导出全部历史数据</div>
        </el-form-item>

        <!-- 统计粒度 -->
        <el-form-item label="统计粒度">
          <el-select
            v-model="granularity"
            placeholder="请选择统计粒度"
            style="width: 100%; max-width: 380px"
          >
            <el-option label="按天统计" value="day" />
            <el-option label="按周统计" value="week" />
            <el-option label="按月统计" value="month" />
          </el-select>
          <div class="form-item-tip">选择数据汇总的时间粒度</div>
        </el-form-item>

        <!-- 导出格式 -->
        <el-form-item label="导出格式">
          <el-radio-group v-model="format">
            <el-radio value="xlsx">Excel (.xlsx)</el-radio>
            <el-radio value="csv">CSV (.csv)</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 导出按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            class="btn-police"
            :loading="store.exporting"
            @click="handleExport"
          >
            {{ store.exporting ? '正在导出...' : '导出报表' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
/** 数据报表导出页面（需管理员权限） */
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAdminStore } from '@/stores/admin'

const store = useAdminStore()

/** 日期范围 */
const dateRange = ref<[string, string] | null>(null)

/** 统计粒度 */
const granularity = ref('day')

/** 导出格式 */
const format = ref('xlsx')

/** 导出报表 */
async function handleExport() {
  try {
    await ElMessageBox.confirm(
      `确认导出 ${granularityLabel.value} 的 ${format.value.toUpperCase()} 报表？\n日期范围：${dateRangeLabel.value}`,
      '确认导出',
      {
        confirmButtonText: '确认导出',
        cancelButtonText: '取消',
        type: 'info',
      }
    )
  } catch {
    return // 用户取消
  }

  try {
    const [start_date, end_date] = dateRange.value || ['', '']
    await store.exportReport({
      start_date: start_date || undefined,
      end_date: end_date || undefined,
      granularity: granularity.value,
      format: format.value,
    })
    ElMessage.success('报表导出成功')
  } catch {
    // 错误已在 request 拦截器中统一处理
  }
}

/** 粒度中文标签 */
const granularityLabel = computed(() => {
  const map: Record<string, string> = { day: '按天', week: '按周', month: '按月' }
  return map[granularity.value] || granularity.value
})

/** 日期范围中文标签 */
const dateRangeLabel = computed(() => {
  if (!dateRange.value) return '全部数据'
  return `${dateRange.value[0]} 至 ${dateRange.value[1]}`
})
</script>

<style scoped lang="scss">
@use '@/styles/police-blue.scss' as *;

.admin-page {
  max-width: 640px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin: 16px 0 24px;

  .page-title {
    font-size: 24px;
    font-weight: 700;
    color: $police-blue;
  }

  .page-desc {
    font-size: 14px;
    color: $text-secondary;
    margin-top: 4px;
  }
}

.report-card {
  border-radius: $radius-lg;
  border-left: 4px solid $police-blue;
  box-shadow: $shadow-md;

  :deep(.el-card__header) {
    border-bottom: 1px solid $border-color;
    padding: 16px 24px;
  }

  .card-header-title {
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
  }
}

.report-form {
  .form-item-tip {
    font-size: 12px;
    color: $text-secondary;
    margin-top: 4px;
  }
}

/** 公安蓝渐变导出按钮 */
.btn-police {
  background: linear-gradient(135deg, $police-blue, $police-accent);
  border: none;
  color: #fff;
  padding: 10px 32px;
  font-size: 15px;
  border-radius: $radius-md;

  &:hover {
    background: linear-gradient(135deg, #182e6e, #025c8e);
  }
}
</style>

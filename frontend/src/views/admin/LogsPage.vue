<template>
  <div class="admin-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/">
      <el-breadcrumb-item :to="{ path: '/dashboard' }">管理后台</el-breadcrumb-item>
      <el-breadcrumb-item>操作日志审计</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">操作日志审计</h1>
      <p class="page-desc">查看所有进出场操作记录，支持按类型与日期筛选</p>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-row">
        <!-- 操作类型筛选 -->
        <el-select
          v-model="filter.operation_type"
          placeholder="操作类型"
          clearable
          style="width: 140px"
        >
          <el-option label="全部" value="" />
          <el-option label="进场" value="entry" />
          <el-option label="出场" value="exit" />
        </el-select>

        <!-- 来源类型筛选 -->
        <el-select
          v-model="filter.source_type"
          placeholder="来源类型"
          clearable
          style="width: 140px"
        >
          <el-option label="全部" value="" />
          <el-option label="游客" value="visitor" />
          <el-option label="工作人员" value="staff" />
        </el-select>

        <!-- 日期范围 -->
        <el-date-picker
          v-model="filter.date_range"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 260px"
        />

        <!-- 搜索按钮 -->
        <el-button type="primary" class="btn-police" @click="handleSearch">
          搜索
        </el-button>
      </div>
    </el-card>

    <!-- 日志表格 -->
    <el-card class="table-card" shadow="never">
      <el-table
        :data="store.logs"
        v-loading="store.logsLoading"
        stripe
        style="width: 100%"
        empty-text="暂无操作日志"
      >
        <!-- 时间 -->
        <el-table-column label="时间" width="170" prop="created_at">
          <template #default="{ row }">
            <span class="time-text">{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>

        <!-- 操作类型 -->
        <el-table-column label="操作类型" width="100" prop="operation_type">
          <template #default="{ row }">
            <el-tag
              :type="getOperationTagType(row.operation_type)"
              effect="light"
              size="small"
            >
              {{ row.operation_type === 'entry' ? '进场' : '出场' }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 来源类型 -->
        <el-table-column label="来源" width="100" prop="source_type">
          <template #default="{ row }">
            <el-tag
              :type="getSourceTagType(row.source_type)"
              effect="light"
              size="small"
            >
              {{ row.source_type === 'visitor' ? '游客' : '工作人员' }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 人数 -->
        <el-table-column label="人数" width="80" prop="count" />

        <!-- IP 地址 -->
        <el-table-column label="IP" width="140" prop="ip_address" />

        <!-- User-Agent -->
        <el-table-column label="User-Agent" min-width="200" prop="user_agent">
          <template #default="{ row }">
            <el-tooltip
              :content="row.user_agent || '-'"
              placement="top"
              :show-after="300"
            >
              <span class="ua-text">{{ truncateText(row.user_agent, 40) }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="store.logsTotal"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="handleSearch"
          @current-change="handleSearch"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
/** 操作日志审计页面（需管理员权限） */
import { reactive, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'

const store = useAdminStore()

/** 筛选条件 */
const filter = reactive({
  operation_type: '',
  source_type: '',
  date_range: null as [string, string] | null,
})

/** 分页 */
const pagination = reactive({
  page: 1,
  page_size: 20,
})

/** 页面挂载时加载日志 */
onMounted(() => {
  handleSearch()
})

/** 搜索日志 */
function handleSearch() {
  const [start_date, end_date] = filter.date_range || ['', '']
  store.fetchLogs({
    page: pagination.page,
    page_size: pagination.page_size,
    operation_type: filter.operation_type || undefined,
    source_type: filter.source_type || undefined,
    start_date: start_date || undefined,
    end_date: end_date || undefined,
  })
}

/** 格式化时间 */
function formatTime(iso: string): string {
  if (!iso) return '-'
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

/** 截断文本 */
function truncateText(text: string, maxLen: number): string {
  if (!text) return '-'
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

/** 操作类型 Tag 颜色：entry=绿色, exit=红色 */
function getOperationTagType(type: string): 'success' | 'danger' | 'info' {
  return type === 'entry' ? 'success' : 'danger'
}

/** 来源类型 Tag 颜色：visitor=蓝色, staff=橙色 */
function getSourceTagType(type: string): 'primary' | 'warning' | 'info' {
  return type === 'visitor' ? 'primary' : 'warning'
}
</script>

<style scoped lang="scss">
@use '@/styles/police-blue.scss' as *;

.admin-page {
  max-width: 1200px;
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

.filter-card {
  margin-bottom: 16px;
  border-radius: $radius-lg;
  border-left: 4px solid $police-blue;
  box-shadow: $shadow-md;

  .filter-row {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }
}

.table-card {
  border-radius: $radius-lg;
  border-left: 4px solid $police-blue;
  box-shadow: $shadow-md;
}

.time-text {
  font-size: 13px;
  color: $text-secondary;
}

.ua-text {
  font-size: 12px;
  color: $text-secondary;
  cursor: default;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/** 公安蓝渐变按钮 */
.btn-police {
  background: linear-gradient(135deg, $police-blue, $police-accent);
  border: none;
  color: #fff;

  &:hover {
    background: linear-gradient(135deg, #182e6e, #025c8e);
  }
}
</style>

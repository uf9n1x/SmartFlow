<template>
  <div class="dashboard-page">
    <!-- ========== 顶部 Header ========== -->
    <header class="dashboard-header">
      <div class="header-left">
        <h1 class="header-title">
          <el-icon :size="28"><DataAnalysis /></el-icon>
          数据监控面板
        </h1>
      </div>
      <div class="header-right">
        <span class="header-time">{{ currentTime }}</span>
        <el-tag
          :type="wsConnected ? 'success' : 'danger'"
          size="small"
          effect="dark"
          class="ws-indicator"
        >
          {{ wsConnected ? '实时连接' : '连接断开' }}
        </el-tag>
        <router-link to="/screen" class="nav-btn">
          <el-icon><Monitor /></el-icon>
          <span>大屏展示</span>
        </router-link>
        <el-dropdown trigger="hover" class="nav-dropdown">
          <span class="nav-btn nav-btn-dropdown">
            <el-icon><User /></el-icon>
            <span>人员登记</span>
            <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item disabled class="dropdown-group-title">工作人员通道</el-dropdown-item>
              <el-dropdown-item>
                <router-link to="/staff/entry">进场登记</router-link>
              </el-dropdown-item>
              <el-dropdown-item>
                <router-link to="/staff/exit">离场登记</router-link>
              </el-dropdown-item>
              <el-dropdown-item divided disabled class="dropdown-group-title">游客通道</el-dropdown-item>
              <el-dropdown-item>
                <router-link to="/entry">进场登记</router-link>
              </el-dropdown-item>
              <el-dropdown-item>
                <router-link to="/exit">离场登记</router-link>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button class="logout-btn" @click="handleLogout" :icon="SwitchButton" text>
          退出
        </el-button>
      </div>
    </header>

    <!-- ========== 满员红色警示条 ========== -->
    <div v-if="store.isFull" class="full-alert-bar">
      <el-icon><WarningFilled /></el-icon>
      <span>区域人数已满！新进场登记已自动关闭</span>
    </div>

    <!-- ========== 主体内容 ========== -->
    <main class="dashboard-main" v-loading="store.loading">
      <div class="kpi-grid">
        <!-- Row 1: 当前区域人数 + 剩余容量 + 区域使用率(三卡等大) -->
        <!-- 当前区域人数 -->
        <div
          class="kpi-card"
          style="--card-index: 1;"
          @mouseenter="hoveredCard = 'currentPeople'"
          @mouseleave="hoveredCard = null"
        >
          <div class="kpi-card-header">
            <el-icon :size="22" color="#1E3A8A">
              <UserFilled />
            </el-icon>
            <span class="kpi-card-label">当前区域人数</span>
          </div>
          <div class="kpi-card-body">
            <transition name="number-fade" mode="out-in">
              <span class="kpi-card-value" :key="store.currentPeople">
                {{ formatNumber(store.currentPeople) }}
              </span>
            </transition>
            <span class="kpi-card-unit">人</span>
          </div>
        </div>

        <!-- 剩余容量 -->
        <div
          class="kpi-card"
          :class="store.isFull ? 'danger' : store.usageRate >= 80 ? 'warning' : 'success'"
          style="--card-index: 2;"
          @mouseenter="hoveredCard = 'remaining'"
          @mouseleave="hoveredCard = null"
        >
          <div class="kpi-card-header">
            <el-icon
              :size="22"
              :color="store.isFull ? '#EF4444' : store.usageRate >= 80 ? '#F59E0B' : '#22C55E'"
            >
              <CircleCheckFilled />
            </el-icon>
            <span class="kpi-card-label">剩余容量</span>
          </div>
          <div class="kpi-card-body">
            <transition name="number-fade" mode="out-in">
              <span class="kpi-card-value" :key="store.remainingCapacity">
                {{ formatNumber(store.remainingCapacity) }}
              </span>
            </transition>
            <span class="kpi-card-unit">人</span>
          </div>
        </div>

        <!-- 区域使用率 -->
        <div
          class="kpi-card usage-card"
          :class="{ 'is-full': store.isFull, 'is-high': store.usageRate >= 80 && !store.isFull }"
          style="--card-index: 3;"
          @mouseenter="hoveredCard = 'usage'"
          @mouseleave="hoveredCard = null"
        >
          <div class="kpi-card-header">
            <el-icon :size="22" :color="store.usageRate >= 80 ? '#EF4444' : '#3B82F6'">
              <PieChart />
            </el-icon>
            <span class="kpi-card-label">区域使用率</span>
          </div>
          <div class="kpi-card-body">
            <el-progress
              type="dashboard"
              :percentage="store.usageRate"
              :color="store.usageRate >= 90 ? '#EF4444' : store.usageRate >= 80 ? '#F59E0B' : '#1E3A8A'"
              :stroke-width="12"
              :width="100"
            >
              <template #default="{ percentage }">
                <span class="usage-percent">{{ percentage }}%</span>
              </template>
            </el-progress>
          </div>
        </div>

        <!-- Row 2: 今日进场 + 今日出场 -->
        <!-- 今日进场人数 (success) -->
        <div
          class="kpi-card success"
          style="--card-index: 3;"
          @mouseenter="hoveredCard = 'todayEntry'"
          @mouseleave="hoveredCard = null"
        >
          <div class="kpi-card-header">
            <el-icon :size="22" color="#22C55E">
              <Top />
            </el-icon>
            <span class="kpi-card-label">今日进场人数</span>
          </div>
          <div class="kpi-card-body">
            <transition name="number-fade" mode="out-in">
              <span class="kpi-card-value" :key="store.todayEntry">
                {{ formatNumber(store.todayEntry) }}
              </span>
            </transition>
            <span class="kpi-card-unit">人次</span>
          </div>
        </div>

        <!-- 今日出场人数 (warning) -->
        <div
          class="kpi-card warning"
          style="--card-index: 4;"
          @mouseenter="hoveredCard = 'todayExit'"
          @mouseleave="hoveredCard = null"
        >
          <div class="kpi-card-header">
            <el-icon :size="22" color="#F59E0B">
              <Bottom />
            </el-icon>
            <span class="kpi-card-label">今日出场人数</span>
          </div>
          <div class="kpi-card-body">
            <transition name="number-fade" mode="out-in">
              <span class="kpi-card-value" :key="store.todayExit">
                {{ formatNumber(store.todayExit) }}
              </span>
            </transition>
            <span class="kpi-card-unit">人次</span>
          </div>
        </div>

        <!-- Row 3: 总进场 + 总出场 -->
        <!-- 总进场人数 -->
        <div
          class="kpi-card"
          style="--card-index: 5;"
          @mouseenter="hoveredCard = 'totalEntry'"
          @mouseleave="hoveredCard = null"
        >
          <div class="kpi-card-header">
            <el-icon :size="22" color="#3B82F6">
              <UploadFilled />
            </el-icon>
            <span class="kpi-card-label">总进场人数</span>
          </div>
          <div class="kpi-card-body">
            <transition name="number-fade" mode="out-in">
              <span class="kpi-card-value" :key="store.totalEntry">
                {{ formatNumber(store.totalEntry) }}
              </span>
            </transition>
            <span class="kpi-card-unit">人次</span>
          </div>
        </div>

        <!-- 总出场人数 -->
        <div
          class="kpi-card"
          style="--card-index: 6;"
          @mouseenter="hoveredCard = 'totalExit'"
          @mouseleave="hoveredCard = null"
        >
          <div class="kpi-card-header">
            <el-icon :size="22" color="#475569">
              <Download />
            </el-icon>
            <span class="kpi-card-label">总出场人数</span>
          </div>
          <div class="kpi-card-body">
            <transition name="number-fade" mode="out-in">
              <span class="kpi-card-value" :key="store.totalExit">
                {{ formatNumber(store.totalExit) }}
              </span>
            </transition>
            <span class="kpi-card-unit">人次</span>
          </div>
        </div>

        <!-- Row 4: 最大人数上限 + 单次提交限制 -->
        <!-- 最大人数上限 (info) -->
        <div
          class="kpi-card info"
          style="--card-index: 7;"
          @mouseenter="hoveredCard = 'maxPeople'"
          @mouseleave="hoveredCard = null"
        >
          <div class="kpi-card-header">
            <el-icon :size="22" color="#64748B">
              <Odometer />
            </el-icon>
            <span class="kpi-card-label">最大人数上限</span>
          </div>
          <div class="kpi-card-body">
            <transition name="number-fade" mode="out-in">
              <span class="kpi-card-value" :key="store.maxPeople">
                {{ formatNumber(store.maxPeople) }}
              </span>
            </transition>
            <el-icon class="edit-icon" @click.stop="showEditDialog = true"><EditPen /></el-icon>
            <span class="kpi-card-unit">人</span>
          </div>
        </div>

        <!-- 单次提交限制（与最大人数上限相同结构） -->
        <div
          class="kpi-card info"
          style="--card-index: 8;"
          @mouseenter="hoveredCard = 'singleLimit'"
          @mouseleave="hoveredCard = null"
        >
          <div class="kpi-card-header">
            <el-icon :size="22" :color="'#64748B'"><Setting /></el-icon>
            <span class="kpi-card-label">单次提交限制</span>
          </div>
          <div class="kpi-card-body">
            <span class="kpi-card-value">{{ store.singleSubmitLimit }}</span>
            <el-icon class="edit-icon" @click.stop="openLimitDialog"><Edit /></el-icon>
            <span class="kpi-card-unit">人/次</span>
          </div>
        </div>

      </div>
    </main>

    <!-- ========== 编辑最大人数对话框 ========== -->
    <el-dialog v-model="showEditDialog" title="修改最大人数上限" width="420px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item label="最大人数上限">
          <el-input-number v-model="editMaxPeople" :min="1" :step="10" size="large" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveMaxPeople">保存</el-button>
      </template>
    </el-dialog>

    <!-- ========== 编辑单次提交限制对话框 ========== -->
    <el-dialog v-model="showLimitDialog" title="编辑单次提交限制" width="360px" :close-on-click-modal="false" destroy-on-close>
      <el-form label-position="top">
        <el-form-item label="单次提交人数上限">
          <el-input-number v-model="editLimit" :min="1" :max="100" :step="1" size="large" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLimitDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmLimitEdit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 数据监控面板页面
 * 实时展示区域人数统计 KPI 指标，支持 WebSocket 实时推送
 */
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { UserFilled, CircleCheckFilled, Top, Bottom, UploadFilled, Download, DataAnalysis, EditPen, WarningFilled, Monitor, User, ArrowDown, SwitchButton, Edit, Setting, PieChart } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { put } from '@/utils/request'
import { useWebSocket } from '@/composables/useWebSocket'
import { useDashboardStore } from '@/stores/dashboard'
import { useRouter } from 'vue-router'

const store = useDashboardStore()

/** 当前悬停的卡片 key（用于动画） */
const hoveredCard = ref<string | null>(null)

/** 编辑最大人数对话框可见性 */
const showEditDialog = ref(false)
/** 编辑对话框中的临时最大人数值 */
const editMaxPeople = ref(500)
/** 保存中状态 */
const saving = ref(false)

/** 路由实例 */
const router = useRouter()

/**
 * 退出登录：清除 token 并跳转到登录页
 */
const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

/** 打开对话框时用当前 store 值填充 */
watch(showEditDialog, (val) => {
  if (val) editMaxPeople.value = store.maxPeople
})

/**
 * 保存修改后的最大人数上限
 */
async function handleSaveMaxPeople() {
  saving.value = true
  try {
    await put('/activity/config', { max_people: editMaxPeople.value })
    ElMessage.success('最大人数已更新')
    showEditDialog.value = false
    await store.fetchDashboard()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '修改失败')
  } finally {
    saving.value = false
  }
}

/** 单次提交限制编辑对话框可见性 */
const showLimitDialog = ref(false)
/** 编辑中的临时单次提交限制值 */
const editLimit = ref(store.singleSubmitLimit)

/** 打开单次提交限制编辑对话框 */
const openLimitDialog = () => {
  editLimit.value = store.singleSubmitLimit
  showLimitDialog.value = true
}

/** 确认修改单次提交限制 */
const confirmLimitEdit = async () => {
  await store.updateActivityConfig({ single_submit_limit: editLimit.value })
  showLimitDialog.value = false
  ElMessage.success('单次提交限制已更新')
}

/** 当前时间（每秒更新） */
const currentTime = ref(formatTime(new Date()))
let timeTimer: number | null = null

/** WebSocket 连接 */
const { connected: wsConnected, data: wsData, connect: wsConnect, disconnect: wsDisconnect } =
  useWebSocket('/api/v1/ws/dashboard')

/**
 * 格式化数字（千分位）
 */
function formatNumber(num: number): string {
  return num.toLocaleString('zh-CN')
}

/**
 * 格式化时间为 HH:mm:ss
 */
function formatTime(date: Date): string {
  const h = String(date.getHours()).padStart(2, '0')
  const m = String(date.getMinutes()).padStart(2, '0')
  const s = String(date.getSeconds()).padStart(2, '0')
  return `${h}:${m}:${s}`
}

/**
 * 使用率进度条颜色
 * 低于 60% 绿色，60%-80% 橙色，80% 以上红色
 */
const usageProgressColor = computed(() => {
  const rate = store.usageRate
  if (rate >= 90) return '#EF4444'
  if (rate >= 80) return '#F59E0B'
  if (rate >= 60) return '#3B82F6'
  return '#22C55E'
})

// ========== 生命周期 ==========

onMounted(() => {
  // 初始化获取数据
  store.fetchDashboard()

  // 建立 WebSocket 实时连接
  wsConnect()

  // 启动时间计时器
  timeTimer = window.setInterval(() => {
    currentTime.value = formatTime(new Date())
  }, 1000)
})

onUnmounted(() => {
  // 清除计时器
  if (timeTimer) clearInterval(timeTimer)
  // 断开 WebSocket
  wsDisconnect()
})

// 监听 WebSocket 推送数据
watch(wsData, (newData) => {
  if (newData) {
    store.updateFromWs(newData)
  }
})
</script>

<style lang="scss" scoped>
// ========== 页面容器 ==========
.dashboard-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: $bg-primary;
  // 网格点阵纹理
  background-image:
    radial-gradient(circle, rgba(30, 58, 138, 0.04) 1px, transparent 1px);
  background-size: 24px 24px;
}

// ========== 顶部 Header ==========
.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 64px;
  background: linear-gradient(135deg, $police-dark 0%, $police-blue 50%, $police-accent 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  position: sticky;
  top: 0;
  z-index: 100;

  // 分割光效线
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  }

  .header-left {
    display: flex;
    align-items: center;
  }

  .header-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 20px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: 2px;
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .header-time {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.85);
    font-variant-numeric: tabular-nums;
    letter-spacing: 1px;
    min-width: 70px;
  }

  .ws-indicator {
    font-size: 12px;
    letter-spacing: 1px;
  }

  .nav-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 6px 14px;
    border-radius: 6px;
    color: rgba(255, 255, 255, 0.8);
    text-decoration: none;
    font-size: 13px;
    transition: all 0.2s;
    background: rgba(255, 255, 255, 0.08);

    &:hover {
      background: rgba(255, 255, 255, 0.2);
      color: #FFFFFF;
    }

    .el-icon { font-size: 16px; }
  }

  .logout-btn {
    color: rgba(255,255,255,0.7) !important;
    font-size: 13px;
    margin-left: 4px;
    &:hover { color: #F56C6C !important; }
  }
}

// ========== 主体内容 ==========
.dashboard-main {
  flex: 1;
  padding: 24px 32px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  align-items: stretch;

  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: auto auto auto;
    gap: 16px;
    width: 100%;
    align-content: start;
  }
}

// ========== KPI 卡片 ==========
.kpi-card {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 20px 24px;
  box-shadow: $shadow-md;
  border-left: 4px solid $police-blue;
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease;

  // 玻璃光效
  backdrop-filter: blur(4px);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(30, 58, 138, 0.08);

  // 入场动画
  opacity: 0;
  transform: translateY(20px);
  animation: cardIn 0.5s ease-out forwards;

  // 逐级延迟
  @for $i from 1 through 9 {
    &:nth-child(#{$i}) {
      animation-delay: #{$i * 0.06}s;
    }
  }

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
  }

  // 状态色变体
  &.success {
    border-left-color: $status-success;
  }
  &.warning {
    border-left-color: $status-warning;
  }
  &.danger {
    border-left-color: $status-danger;
  }
  &.info {
    border-left-color: $status-info;
  }

  // 卡片头部
  .kpi-card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }

  .kpi-card-label {
    font-size: 13px;
    color: $text-secondary;
    font-weight: 500;
    letter-spacing: 0.5px;
  }

  // 卡片数值区
  .kpi-card-body {
    display: flex;
    align-items: baseline;
    gap: 6px;
  }

  .kpi-card-value {
    font-size: 36px;
    font-weight: 700;
    color: $police-blue;
    line-height: 1.1;
    font-variant-numeric: tabular-nums;
  }

  .kpi-card-unit {
    font-size: 13px;
    color: $text-secondary;
    font-weight: 400;
  }

  // 编辑图标
  .edit-icon {
    font-size: 18px;
    color: #94A3B8;
    cursor: pointer;
    margin-left: 8px;
    vertical-align: middle;
    transition: color 0.2s;

    &:hover {
      color: #1E3A8A;
    }
  }

  // 卡片底部（描述 + 操作）
  .kpi-card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #E2E8F0;
  }

  .kpi-card-desc {
    font-size: 12px;
    color: $text-secondary;
  }

  .edit-btn {
    font-size: 13px;
  }
}

// ========== 满员警示条 ==========
.full-alert-bar {
  background: linear-gradient(90deg, #EF4444, #DC2626);
  color: #FFFFFF;
  text-align: center;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  animation: pulse 1.5s ease-in-out infinite;
}

// ========== 关键帧动画 ==========
@keyframes cardIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

@keyframes borderPulse {
  0%, 100% { border-left-color: #EF4444; }
  50% { border-left-color: #DC2626; }
}

// 使用率卡片特殊样式
.usage-card {
  border-left-color: $police-blue;

  &.is-high {
    border-left-color: $status-warning;
  }
  &.is-full {
    border-left-color: $status-danger;
    animation: borderPulse 1.5s ease-in-out infinite;
  }

  .usage-progress-wrap {
    display: flex;
    align-items: center;
    gap: 20px;
    justify-content: center;
    padding-top: 4px;

    :deep(.el-progress) {
      flex-shrink: 0;
    }
  }

  .usage-percent {
    font-size: 22px;
    font-weight: 700;
    color: $police-blue;
  }

  .usage-detail {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: $text-secondary;

    span:first-child {
      font-weight: 600;
      color: $text-primary;
      font-size: 15px;
    }
  }
}

// ========== 数字切换动画 ==========
.number-fade-enter-active,
.number-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.number-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.number-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

// ========== 响应式 ==========
@media (max-width: 768px) {
  .dashboard-header {
    padding: 0 16px;
    height: 56px;

    .header-title {
      font-size: 16px;
      gap: 6px;
    }
  }

  .dashboard-main {
    padding: 16px;

    .kpi-grid {
      grid-template-columns: 1fr;
    }
  }

  .kpi-card {
    padding: 16px 20px;

    .kpi-card-value {
      font-size: 28px;
    }
  }

  .usage-card .usage-progress-wrap {
    flex-direction: column;
    gap: 12px;
  }
}
</style>

<!-- 下拉菜单美化（非 scoped，因为 el-dropdown-menu 渲染到 body 层） -->
<style lang="scss">
// 下拉菜单美化
.el-dropdown-menu {
  background: rgba(15, 23, 42, 0.96) !important;
  backdrop-filter: blur(16px);
  border: 1px solid rgba(30, 58, 138, 0.3);
  border-radius: 10px;
  padding: 6px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);

  .el-dropdown-menu__item {
    color: #CBD5E1;
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 13px;
    transition: all 0.15s ease;

    &:hover {
      background: rgba(59, 130, 246, 0.2);
      color: #60A5FA;
    }

    a {
      color: inherit;
      text-decoration: none;
    }
  }

  .dropdown-group-title {
    font-size: 11px;
    color: #64748B;
    font-weight: 600;
    padding: 8px 14px 4px;
    cursor: default;
    pointer-events: none;
  }
}
</style>

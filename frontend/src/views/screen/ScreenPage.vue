<template>
  <div class="screen-page">
    <!-- ========== 顶部 Header ========== -->
    <header class="screen-header">
      <h1 class="title">区域人数管控统计系统</h1>
      <p class="time">{{ currentTime }}</p>
      <div class="header-actions">
        <span class="fullscreen-hint">按 F11 或点击按钮进入全屏模式</span>
        <el-button class="fullscreen-btn" type="primary" size="small" @click="toggleFullscreen">
          <el-icon><FullScreen /></el-icon>
          {{ isFullscreen ? '退出全屏' : '全屏展示' }}
        </el-button>
      </div>
    </header>

    <!-- ========== 主体区域 ========== -->
    <main class="screen-body">
      <!-- 左侧主区域（65%） -->
      <section class="left-panel">
        <!-- 1. KPI 卡片行 -->
        <div class="kpi-row">
          <div class="kpi-card current-people">
            <div class="kpi-icon">
              <el-icon :size="28"><UserFilled /></el-icon>
            </div>
            <div class="kpi-content">
              <div class="kpi-value">{{ store.currentPeople }}</div>
              <div class="kpi-label">当前区域人数</div>
            </div>
          </div>

          <div class="kpi-card remaining-capacity" :class="capacityStatus">
            <div class="kpi-icon">
              <el-icon :size="28"><Odometer /></el-icon>
            </div>
            <div class="kpi-content">
              <div class="kpi-value">{{ remainingCapacity }}</div>
              <div class="kpi-label">剩余容量</div>
            </div>
          </div>

          <div class="kpi-card usage-card">
            <div class="kpi-icon">
              <el-icon :size="28"><PieChart /></el-icon>
            </div>
            <div class="kpi-content">
              <div class="kpi-value usage-text" :style="{ color: usageColor }">
                {{ store.usageRate.toFixed(1) }}%
              </div>
              <div class="kpi-label">区域使用率</div>
            </div>
          </div>
        </div>

        <!-- 2. 进出场趋势图 -->
        <div class="chart-panel">
          <h3 class="panel-title">进出场趋势</h3>
          <v-chart class="chart" :option="lineChartOption" autoresize />
        </div>

        <!-- 3. 进场/出场占比饼图 -->
        <div class="chart-panel">
          <h3 class="panel-title">今日进出占比</h3>
          <v-chart class="chart chart-pie" :option="pieChartOption" autoresize />
        </div>
      </section>

      <!-- 右侧操作日志（35%） -->
      <section class="right-panel">
        <div class="log-panel">
          <h3 class="panel-title">最近操作记录</h3>
          <div class="log-list" ref="logListRef">
            <div
              v-for="(log, index) in displayLogs"
              :key="index"
              class="log-item"
            >
              <span class="log-time">{{ formatLogTime(log.created_at || log.time) }}</span>
              <el-tag
                :type="log.operation_type === 'entry' ? 'success' : 'danger'"
                size="small"
                class="log-tag"
              >
                {{ log.operation_type === 'entry' ? '进场' : '离场' }}
              </el-tag>
              <span class="log-people">{{ log.count || 1 }}人</span>
              <el-tag
                :type="log.source_type === 'staff' ? 'warning' : 'info'"
                size="small"
                class="log-tag"
              >
                {{ log.source_type === 'staff' ? '工作人员' : '游客' }}
              </el-tag>
            </div>
            <div v-if="displayLogs.length === 0" class="log-empty">暂无操作记录</div>
          </div>
        </div>
      </section>
    </main>

    <!-- ========== 底部状态栏 ========== -->
    <footer class="screen-footer">
      <div class="status-left">
        <span class="status-dot" :class="{ connected: wsConnected }"></span>
        <span>WebSocket {{ wsConnected ? '已连接' : '未连接' }}</span>
      </div>
      <div class="status-right">
        <span>下次刷新: {{ countdown }}s</span>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import { FullScreen, UserFilled, Odometer, PieChart } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart, PieChart as EChartsPieChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useScreenStore } from '@/stores/screen'
import { useWebSocket } from '@/composables/useWebSocket'

// 注册 ECharts 组件
use([
  LineChart,
  EChartsPieChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  CanvasRenderer,
])

const store = useScreenStore()

// ============ WebSocket 连接 ============
const { connected: wsConnected, data: wsData, connect: wsConnect } = useWebSocket('/api/v1/ws/dashboard')

/**
 * 监听 WebSocket 推送数据，实时更新 store
 */
watch(wsData, (newData) => {
  if (newData) {
    store.updateFromWs(newData)
  }
})

// ============ 当前时间 ============
const currentTime = ref('')

/**
 * 更新时间显示（每秒更新一次）
 */
function updateTime() {
  const now = new Date()
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  const hh = String(now.getHours()).padStart(2, '0')
  const mm = String(now.getMinutes()).padStart(2, '0')
  const ss = String(now.getSeconds()).padStart(2, '0')
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  currentTime.value = `${y}年${m}月${d}日 周${weekDays[now.getDay()]} ${hh}:${mm}:${ss}`
}

let timeTimer: number

// ============ 自动刷新 ============
const countdown = ref(30)
let countdownTimer: number

/**
 * 执行全量数据刷新
 */
async function refreshAll() {
  await Promise.all([store.fetchScreenData(), store.fetchRecentLogs(), fetchTrendData()])
}

/**
 * 重置倒计时
 */
function resetCountdown() {
  countdown.value = 30
}

/**
 * 启动 30 秒倒计时，到 0 后自动刷新数据
 */
function startCountdown() {
  countdownTimer = window.setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      refreshAll()
      resetCountdown()
    }
  }, 1000)
}

// ============ 全屏 ============
const isFullscreen = ref(false)

/**
 * 切换全屏 / 退出全屏
 */
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

/**
 * 监听全屏状态变化（用户按 F11 或 Esc 时同步状态）
 */
function onFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement
}

// ============ 剩余容量 ============
const remainingCapacity = computed(() => {
  return store.maxPeople - store.currentPeople
})

/** 根据使用率返回容量状态类名 */
const capacityStatus = computed(() => {
  if (store.usageRate >= 90) return 'danger'
  if (store.usageRate >= 70) return 'warning'
  return 'success'
})

/** 根据使用率返回对应颜色 */
const usageColor = computed(() => {
  if (store.usageRate >= 90) return '#EF4444'
  if (store.usageRate >= 70) return '#F59E0B'
  return '#22C55E'
})

// ============ 操作日志滚动 ============
const logListRef = ref<HTMLElement | null>(null)
let scrollTimer: number

/**
 * 模拟日志滚动效果：每隔 3 秒滚动一条
 */
function startLogScroll() {
  scrollTimer = window.setInterval(() => {
    if (!logListRef.value) return
    const el = logListRef.value
    // 滚动到最底部后回到顶部
    if (el.scrollTop + el.clientHeight >= el.scrollHeight - 5) {
      el.scrollTop = 0
    } else {
      el.scrollTop += 52 // 每条日志约 52px
    }
  }, 3000)
}

/**
 * 展示的日志列表（最多 20 条用于滚动展示，放冗余数据模拟真实场景）
 */
const displayLogs = computed(() => {
  const logs = store.recentLogs || []
  return logs.slice(0, 20)
})

/**
 * 格式化日志时间
 */
function formatLogTime(timeStr: string): string {
  if (!timeStr) return '--:--:--'
  const d = new Date(timeStr)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')
  return `${hh}:${mm}:${ss}`
}

// ============ 趋势数据 ============
interface TrendPoint {
  time: string
  currentPeople: number
  remainingCapacity: number
}

const trendData = ref<TrendPoint[]>([])

/** 获取趋势数据 */
const fetchTrendData = async () => {
  try {
    const res = await axios.get('/api/v1/report/trend')
    trendData.value = res.data.time_points || []
  } catch (err) {
    console.error('获取趋势数据失败', err)
  }
}

// ============ ECharts 折线图配置 —— 当前人数 + 剩余容量趋势 ============
/** 折线图配置 —— 当前人数 + 剩余容量趋势 */
const lineChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(15,23,42,0.9)',
    borderColor: 'rgba(30,58,138,0.3)',
    textStyle: { color: '#E2E8F0', fontSize: 12 },
    axisPointer: { type: 'cross', crossStyle: { color: '#94A3B8' } }
  },
  legend: {
    data: ['当前人数', '剩余容量'],
    top: 0,
    textStyle: { color: '#94A3B8', fontSize: 12 },
    itemWidth: 14,
    itemHeight: 8
  },
  grid: { left: '3%', right: '4%', bottom: '3%', top: '40px', containLabel: true },
  xAxis: {
    type: 'category',
    data: trendData.value.map((d: any) => d.time),
    axisLine: { lineStyle: { color: 'rgba(148,163,184,0.3)' } },
    axisLabel: { color: '#94A3B8', fontSize: 11, rotate: 30 }
  },
  yAxis: {
    type: 'value',
    name: '人数',
    nameTextStyle: { color: '#94A3B8', fontSize: 11 },
    axisLabel: { color: '#94A3B8' },
    splitLine: { lineStyle: { color: 'rgba(148,163,184,0.1)' } }
  },
  series: [
    {
      name: '当前人数',
      type: 'line',
      smooth: true,
      data: trendData.value.map((d: any) => d.currentPeople),
      lineStyle: { color: '#3B82F6', width: 2 },
      itemStyle: { color: '#3B82F6' },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [{ offset: 0, color: 'rgba(59,130,246,0.3)' }, { offset: 1, color: 'rgba(59,130,246,0.02)' }]
      }}
    },
    {
      name: '剩余容量',
      type: 'line',
      smooth: true,
      data: trendData.value.map((d: any) => d.remainingCapacity),
      lineStyle: { color: '#22C55E', width: 2, type: 'dashed' },
      itemStyle: { color: '#22C55E' },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [{ offset: 0, color: 'rgba(34,197,94,0.2)' }, { offset: 1, color: 'rgba(34,197,94,0.02)' }]
      }}
    }
  ]
}))

// ============ ECharts 饼图配置 ============
const pieChartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(15, 23, 42, 0.9)',
    borderColor: 'rgba(30, 58, 138, 0.5)',
    textStyle: { color: '#F8FAFC', fontSize: 13 },
    formatter: '{b}: {c} 人次 ({d}%)',
  },
  legend: {
    orient: 'horizontal',
    bottom: 5,
    textStyle: { color: '#94A3B8', fontSize: 13 },
  },
  series: [
    {
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderColor: '#0F172A',
        borderWidth: 3,
      },
      label: {
        show: false,
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 18,
          fontWeight: 'bold',
        },
      },
      data: [
        {
          value: store.todayEntry || 0,
          name: '进场',
          itemStyle: { color: '#3B82F6' },
        },
        {
          value: store.todayExit || 0,
          name: '出场',
          itemStyle: { color: '#F59E0B' },
        },
      ],
    },
  ],
}))

// ============ 生命周期 ============
onMounted(() => {
  // 初始数据加载
  refreshAll()

  // 建立 WebSocket 连接
  wsConnect()

  // 启动时间更新
  updateTime()
  timeTimer = window.setInterval(updateTime, 1000)

  // 启动 30 秒倒计时刷新
  startCountdown()

  // 启动日志滚动
  startLogScroll()

  // 监听全屏状态变化
  document.addEventListener('fullscreenchange', onFullscreenChange)
})

onUnmounted(() => {
  clearInterval(timeTimer)
  clearInterval(countdownTimer)
  clearInterval(scrollTimer)
  document.removeEventListener('fullscreenchange', onFullscreenChange)
})
</script>

<style lang="scss" scoped>
/* ========== 公安蓝大屏主题变量 ========== */
$bg-dark: #0F172A;
$card-bg: rgba(30, 41, 59, 0.8);
$border-color: rgba(30, 58, 138, 0.3);
$text-primary: #F8FAFC;
$text-secondary: #94A3B8;
$police-blue: #1E3A8A;
$blue-accent: #3B82F6;
$orange-accent: #F59E0B;
$green-accent: #22C55E;
$red-accent: #EF4444;

/* ========== 全屏根容器 ========== */
.screen-page {
  width: 100vw;
  height: 100vh;
  background: $bg-dark;
  background-image:
    linear-gradient(rgba(30, 58, 138, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(30, 58, 138, 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
  color: $text-primary;
  overflow: hidden;
  padding: 16px 24px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* ========== Header ========== */
.screen-header {
  text-align: center;
  padding: 6px 0 14px;
  border-bottom: 2px solid rgba(30, 58, 138, 0.5);
  margin-bottom: 14px;
  position: relative;
  flex-shrink: 0;

  .title {
    font-size: 30px;
    font-weight: 700;
    letter-spacing: 8px;
    background: linear-gradient(180deg, #F8FAFC 0%, #94A3B8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.3;
  }

  .time {
    color: $text-secondary;
    font-size: 14px;
    margin-top: 4px;
    letter-spacing: 2px;
  }

  .header-actions {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    align-items: center;
    gap: 12px;

    .fullscreen-hint {
      color: $text-secondary;
      font-size: 12px;
      opacity: 0.7;
    }

    .fullscreen-btn {
      background: rgba(30, 58, 138, 0.4);
      border: 1px solid rgba(30, 58, 138, 0.6);
      color: $text-primary;

      &:hover {
        background: rgba(30, 58, 138, 0.6);
      }
    }
  }
}

/* ========== 主体布局 ========== */
.screen-body {
  flex: 1;
  display: flex;
  gap: 16px;
  min-height: 0;
}

/* ========== 左侧面板（62%） ========== */
.left-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ========== KPI 卡片行 ========== */
.kpi-row {
  display: flex;
  gap: 14px;
  flex-shrink: 0;
}

.kpi-card {
  flex: 1;
  background: $card-bg;
  border: 1px solid $border-color;
  border-radius: 8px;
  padding: 16px 20px;
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  gap: 14px;
  transition: border-color 0.3s;

  .kpi-icon {
    width: 52px;
    height: 52px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    color: $text-primary;
  }

  .kpi-content {
    flex: 1;
    min-width: 0;
  }

  .kpi-value {
    font-size: 36px;
    font-weight: 700;
    color: $text-primary;
    line-height: 1.1;
  }

  .kpi-label {
    font-size: 13px;
    color: $text-secondary;
    margin-top: 4px;
    letter-spacing: 1px;
  }

  /* 当前人数卡片 */
  &.current-people {
    border-left: 3px solid $blue-accent;
    .kpi-icon {
      background: rgba(59, 130, 246, 0.15);
    }
  }

  /* 剩余容量 */
  &.remaining-capacity {
    &.success {
      border-left: 3px solid $green-accent;
      .kpi-icon { background: rgba(34, 197, 94, 0.15); }
    }
    &.warning {
      border-left: 3px solid $orange-accent;
      .kpi-icon { background: rgba(245, 158, 11, 0.15); }
    }
    &.danger {
      border-left: 3px solid $red-accent;
      .kpi-icon { background: rgba(239, 68, 68, 0.15); }
    }
  }

  /* 使用率卡片 */
  &.usage-card {
    border-left: 3px solid $blue-accent;
    .kpi-icon {
      background: rgba(30, 58, 138, 0.15);
    }
  }
}

/* ========== 图表面板 ========== */
.chart-panel {
  flex: 1;
  background: $card-bg;
  border: 1px solid $border-color;
  border-radius: 8px;
  padding: 14px 16px;
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-title {
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
  margin: 0 0 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(30, 58, 138, 0.3);
  position: relative;
  flex-shrink: 0;

  &::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: -1px;
    width: 40px;
    height: 2px;
    background: $blue-accent;
  }
}

.chart {
  flex: 1;
  min-height: 0;
}

.chart-pie {
  max-height: 220px;
}

/* ========== 右侧面板（38%） ========== */
.right-panel {
  flex: 0 0 22%;
  min-width: 220px;
  display: flex;
  flex-direction: column;
}

/* ========== 操作日志面板 ========== */
.log-panel {
  flex: 1;
  background: $card-bg;
  border: 1px solid $border-color;
  border-radius: 8px;
  padding: 14px 16px;
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.log-list {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;

  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(30, 58, 138, 0.5);
    border-radius: 2px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
}

.log-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  font-size: 13px;
  transition: background 0.2s;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background: rgba(30, 58, 138, 0.08);
  }

  .log-time {
    color: $text-secondary;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    flex-shrink: 0;
    min-width: 70px;
  }

  .log-tag {
    flex-shrink: 0;
  }

  .log-people {
    color: $text-primary;
    font-weight: 500;
    min-width: 30px;
  }
}

.log-empty {
  text-align: center;
  color: $text-secondary;
  padding: 60px 0;
  font-size: 14px;
}

/* ========== 底部状态栏 ========== */
.screen-footer {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0 0;
  margin-top: 12px;
  border-top: 1px solid rgba(30, 58, 138, 0.3);
  font-size: 13px;
  color: $text-secondary;

  .status-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: $red-accent;
    transition: background 0.3s;

    &.connected {
      background: $green-accent;
      box-shadow: 0 0 6px rgba(34, 197, 94, 0.5);
    }
  }
}
</style>

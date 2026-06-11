<template>
  <div class="staff-page">
    <!-- 公安蓝 Header -->
    <div class="staff-header">
      <el-icon :size="24"><Plus /></el-icon>
      <h1>进场登记 - 工作人员</h1>
      <div class="header-nav">
        <router-link to="/dashboard" class="nav-btn">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </router-link>
        <router-link to="/screen" class="nav-btn">
          <el-icon><Monitor /></el-icon>
          <span>大屏</span>
        </router-link>
        <el-button class="logout-btn" @click="handleLogout" circle>
          <el-icon><SwitchButton /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 容量信息卡片 -->
    <div class="capacity-cards">
      <div class="cap-card">
        <span class="cap-label">当前人数</span>
        <span class="cap-value primary">{{ staffStore.currentPeople }}</span>
      </div>
      <div class="cap-card">
        <span class="cap-label">最大上限</span>
        <span class="cap-value">{{ staffStore.maxPeople }}</span>
      </div>
      <div class="cap-card" :class="staffStore.remainingCapacity <= 0 ? 'danger' : 'success'">
        <span class="cap-label">剩余容量</span>
        <span class="cap-value">{{ staffStore.remainingCapacity }}</span>
      </div>
    </div>

    <div class="card-section first-section">
      <!-- 快捷按钮组 -->
      <div class="section-title">快捷数量</div>
      <div class="quick-btns">
        <el-button
          v-for="count in quickCounts.entry"
          :key="count"
          :type="activeQuickCount === count ? 'primary' : 'default'"
          size="large"
          class="quick-btn"
          :loading="loading && activeQuickCount === count"
          @click="handleQuickEntry(count)"
        >
          +{{ count }}
        </el-button>
      </div>
    </div>

    <div class="divider">
      <span>或</span>
    </div>

    <!-- 自定义数量 -->
    <div class="card-section">
      <div class="section-title">自定义进场人数</div>
      <div class="custom-row">
        <div class="number-input">
          <el-input-number
            v-model="customCount"
            :min="1"
            :max="50"
            :step="1"
            size="large"
            controls-position="right"
            placeholder="人数"
          />
        </div>
        <el-button
          type="primary"
          size="large"
          class="confirm-btn"
          :loading="loading"
          @click="handleCustomEntry"
        >
          确认进场
        </el-button>
      </div>
    </div>

    <div class="page-nav">
      <router-link to="/staff/exit" class="nav-link">去离场登记 →</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
/** 工作人员进场登记页面 - 公安蓝风格 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, DataAnalysis, Monitor, SwitchButton } from '@element-plus/icons-vue'
import { useStaffStore } from '@/stores/staff'

const router = useRouter()
const staffStore = useStaffStore()
const { loading, quickCounts } = staffStore

const customCount = ref(1)
const activeQuickCount = ref<number | null>(null)

onMounted(() => { staffStore.fetchCapacity() })

/** 退出登录 */
function handleLogout() {
  localStorage.removeItem('token')
  router.push('/login')
}

/** 快捷数量进场 */
async function handleQuickEntry(count: number) {
  activeQuickCount.value = count
  await staffStore.staffEntry(count)
  activeQuickCount.value = null
}

/** 自定义数量进场 */
async function handleCustomEntry() {
  await staffStore.staffEntry(customCount.value)
}
</script>

<style scoped lang="scss">
.staff-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  align-items: center;
  padding: 0 16px;
}

/* 公安蓝 Header */
.staff-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #1E3A8A, #0369A1);
  border-radius: 0 0 16px 16px;
  color: #FFFFFF;
  box-shadow: none;
  margin-bottom: 0;

  h1 {
    font-size: 22px;
    font-weight: 700;
  }
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;

  .nav-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 6px 14px;
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.85);
    text-decoration: none;
    font-size: 13px;
    font-weight: 500;
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.15);
    transition: all 0.2s ease;

    &:hover {
      background: rgba(255, 255, 255, 0.25);
      color: #FFFFFF;
      border-color: rgba(255, 255, 255, 0.3);
    }

    .el-icon { font-size: 16px; }
  }

  .logout-btn {
    background: rgba(255,255,255,0.1);
    border: none;
    color: rgba(255,255,255,0.7);
    &:hover { color: #F56C6C; background: rgba(255,255,255,0.2); }
  }
}

/* 容量信息卡片 */
.capacity-cards {
  display: flex;
  gap: 12px;
  margin-top: 28px;
  margin-bottom: 20px;

  .cap-card {
    flex: 1;
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(8px);
    border-radius: 12px;
    padding: 14px 12px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border-left: 3px solid #1E3A8A;
    transition: transform 0.2s;
    &:hover { transform: translateY(-2px); }

    &.success { border-left-color: #22C55E; }
    &.danger { border-left-color: #EF4444; }

    .cap-label {
      font-size: 12px;
      color: #94A3B8;
      display: block;
      margin-bottom: 4px;
    }

    .cap-value {
      font-size: 24px;
      font-weight: 700;
      color: #1E3A8A;

      &.primary { color: #1E3A8A; }
    }
  }
}

/* 卡片区域 */
.card-section {
  backdrop-filter: blur(8px);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.12);
  border-radius: 16px;
  padding: 24px;
  width: 100%;
}

/* capacity-cards 与第一个 card-section 的间距 */
.first-section {
  margin-top: 32px !important;
}

.section-title {
  font-size: 14px;
  color: #475569;
  margin-bottom: 16px;
  font-weight: 500;
}

/* 快捷按钮组 */
.quick-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.quick-btn {
  flex: 1;
  min-width: 0;
  height: 48px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 10px;
  transition: all 0.2s;

  &:not(.el-button--primary) {
    border-color: #E2E8F0;
    color: #1E3A8A;

    &:hover {
      border-color: #1E3A8A;
      color: #1E3A8A;
      background: #F0F4FF;
    }
  }

  &.el-button--primary {
    background: linear-gradient(135deg, #1E3A8A, #0369A1);
    border: none;
    box-shadow: 0 2px 8px rgba(30, 58, 138, 0.25);
  }
}

/* 分隔线 */
.divider {
  display: flex;
  align-items: center;
  margin: 24px 0;
  color: #94A3B8;
  font-size: 13px;

  &::before,
  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #E2E8F0;
  }

  span {
    padding: 0 16px;
  }
}

/* 自定义数量区域 */
.custom-row {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.number-input {
  flex: 1;

  :deep(.el-input-number) {
    width: 100%;
  }

  :deep(.el-input__wrapper) {
    border-radius: 8px;
  }
}

.confirm-btn {
  flex: 1;
  min-width: 0;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  background: linear-gradient(135deg, #1E3A8A, #0369A1) !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(30, 58, 138, 0.25);
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 4px 16px rgba(30, 58, 138, 0.4);
    transform: translateY(-1px);
  }
}

/* 底部互跳导航 */
.page-nav {
  max-width: 540px;
  width: 100%;
  text-align: center;
  margin: 20px auto 0;
  padding-top: 16px;
  border-top: 1px solid rgba(226, 232, 240, 0.4);

  .nav-link {
    color: #1E3A8A;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    padding: 8px 20px;
    border-radius: 8px;
    transition: all 0.2s;
    &:hover { background: rgba(30, 58, 138, 0.05); color: #0369A1; }
  }
}

/* PC 端适配 */
@media (min-width: 769px) {
  .staff-page {
    padding: 0;
  }

  .staff-header,
  .divider {
    max-width: 540px;
    width: 100%;
    margin-left: auto;
    margin-right: auto;
  }

  .capacity-cards, .card-section {
    max-width: 540px;
    width: 100%;
    margin-left: auto;
    margin-right: auto;
  }

  .card-section {
    margin-top: 24px;
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .staff-header {
    flex-wrap: wrap;
    gap: 8px;
    padding: 12px 12px;
  }

  .staff-header h1 {
    font-size: 15px;
  }

  .header-nav {
    width: 100%;
    justify-content: flex-end;
  }

  .capacity-cards {
    gap: 8px;
  }

  .cap-card {
    padding: 8px 6px;
  }

  .cap-value {
    font-size: 20px;
  }

  .cap-label {
    font-size: 11px;
  }

  .card-section {
    max-width: 480px;
    width: 100%;
    margin: 0 auto;
    backdrop-filter: none;
    background: #FFFFFF;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border-radius: 12px;
  }

  .quick-btns {
    gap: 8px;
  }

  .quick-btn {
    min-width: 60px;
    font-size: 16px;
  }

  .custom-row {
    flex-direction: column;
  }

  .confirm-btn {
    width: 100%;
  }
}
</style>

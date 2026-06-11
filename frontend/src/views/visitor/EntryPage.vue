<template>
  <div class="entry-page">
    <!-- 顶部公安蓝渐变 Header -->
    <header class="page-header">
      <div class="header-content">
        <el-icon :size="28" color="#FFFFFF"><UserFilled /></el-icon>
        <h1>进场登记</h1>
      </div>
      <p class="header-subtitle">大型活动区域人数管控系统</p>
    </header>

    <main class="page-main">
      <!-- 人数上限警告提示 -->
      <el-alert
        v-if="visitorStore.isFull"
        title="当前活动区域人数已达到最大上限，请您等待"
        type="warning"
        show-icon
        :closable="false"
        class="full-alert"
      />

      <!-- 容量信息卡片 -->
      <div class="capacity-cards">
        <div class="cap-card">
          <span class="cap-label">当前人数</span>
          <span class="cap-value primary">{{ visitorStore.currentPeople }}</span>
        </div>
        <div class="cap-card">
          <span class="cap-label">最大上限</span>
          <span class="cap-value">{{ visitorStore.maxCapacity }}</span>
        </div>
        <div class="cap-card" :class="{ success: !visitorStore.isFull, danger: visitorStore.isFull }">
          <span class="cap-label">剩余容量</span>
          <span class="cap-value">{{ visitorStore.maxCapacity - visitorStore.currentPeople }}</span>
        </div>
      </div>

      <!-- 登记表单卡片 -->
      <el-card v-if="!visitorStore.isFull" class="entry-card" shadow="hover">
        <div class="card-title">
          <el-icon :size="20"><EditPen /></el-icon>
          <span>请填写进场信息</span>
        </div>

        <el-form label-position="top" @submit.prevent="handleSubmit">
          <el-form-item label="本次进场人数">
            <el-input-number
              v-model="count"
              :min="1"
              :max="10"
              :controls="true"
              size="large"
              class="count-input"
            />
            <template #extra>
              <span class="form-tip">单次登记人数范围：1 ~ 10 人</span>
            </template>
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            class="submit-btn"
            :loading="visitorStore.loading"
            :disabled="count < 1"
            @click="handleSubmit"
          >
            确认进场
          </el-button>
        </el-form>
      </el-card>

      <!-- 结果反馈区域 -->
      <Transition name="fade">
        <div v-if="visitorStore.lastResult" class="result-section">
          <!-- 成功提示 -->
          <el-alert
            v-if="visitorStore.lastResult.success"
            :title="visitorStore.lastResult.message"
            type="success"
            show-icon
            :closable="false"
            class="result-alert"
          >
            <template #default>
              <p class="result-detail">
                当前区域人数：<strong>{{ visitorStore.lastResult.currentPeople }}</strong>
              </p>
            </template>
          </el-alert>

          <!-- 失败提示 -->
          <el-alert
            v-else
            :title="visitorStore.lastResult.message"
            type="error"
            show-icon
            :closable="false"
            class="result-alert"
          />
        </div>
      </Transition>


    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { UserFilled, EditPen } from '@element-plus/icons-vue'
import { useVisitorStore } from '@/stores/visitor'

const visitorStore = useVisitorStore()

/** 本次进场人数 */
const count = ref(1)

/**
 * 页面初始化：检查活动容量配置
 */
onMounted(() => {
  visitorStore.checkCapacity()
})

/**
 * 处理进场提交
 */
async function handleSubmit() {
  if (count.value < 1) return
  await visitorStore.submitEntry(count.value)
}
</script>

<style scoped lang="scss">
.entry-page {
  min-height: 100vh;
  background: var(--el-bg-color);
  display: flex;
  flex-direction: column;
  align-items: center;
}

// ========== 顶部 Header ==========
.page-header {
  background: linear-gradient(135deg, #1E3A8A, #0369A1);
  padding: 20px 24px;
  border-radius: 0 0 16px 16px;
  text-align: center;
  color: #FFFFFF;
  width: 100%;

  .header-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    max-width: 540px;
    margin: 0 auto;

    h1 {
      font-size: 22px;
      font-weight: 700;
      letter-spacing: 2px;
    }
  }

  .header-subtitle {
    margin-top: 8px;
    font-size: 14px;
    opacity: 0.85;
    letter-spacing: 1px;
  }

}

// ========== 主内容区 ==========
.page-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 8px 16px 24px;
  max-width: 480px;
  width: 100%;
  margin: 0 auto;
}

// 人数上限警告
.full-alert {
  border-radius: 12px;
  font-size: 15px;
}

// 容量信息卡片
.capacity-cards {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;

  .cap-card {
    flex: 1;
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(8px);
    padding: 14px 12px;
    border-radius: 12px;
    border-left: 3px solid #1E3A8A;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    transition: transform 0.2s;
    &:hover {
      transform: translateY(-2px);
    }

    .cap-label {
      display: block;
      font-size: 12px;
      color: #94A3B8;
      margin-bottom: 4px;
    }
    .cap-value {
      font-size: 24px;
      font-weight: 700;
      color: #1E3A8A;
      &.primary {
        color: #1E3A8A;
      }
      &.success {
        color: #22C55E;
      }
      &.danger {
        color: #EF4444;
      }
    }
  }
}

// 登记表单卡片
.entry-card {
  padding: 24px;
  backdrop-filter: blur(8px);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.12);
  border-radius: 16px;
  border: none;

  .card-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 600;
    color: #1E3A8A;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid #E2E8F0;
  }

  .count-input {
    width: 100%;
  }

  .form-tip {
    font-size: 12px;
    color: #94A3B8;
  }

  .submit-btn {
    width: 100%;
    margin-top: 8px;
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: 2px;
    background: linear-gradient(135deg, #1E3A8A, #0369A1);
    border: none;
    border-radius: 8px;

    &:hover {
      background: linear-gradient(135deg, #152C6B, #025A8C);
    }

    &:active {
      background: linear-gradient(135deg, #0F1F52, #014A73);
    }
  }
}

// ========== 结果反馈 ==========
.result-section {
  margin-top: 20px;

  .result-alert {
    border-radius: 12px;
    font-size: 15px;
  }

  .result-detail {
    margin-top: 4px;
    font-size: 14px;

    strong {
      color: #1E3A8A;
      font-size: 20px;
    }
  }
}

// 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// ========== PC 端适配 ==========
@media (min-width: 769px) {
  .page-header {
    max-width: 540px;
    margin: 0 auto;
      border-radius: 0 0 16px 16px;
    }

  .page-main {
    max-width: 540px;
    margin: 16px auto;
    padding: 16px 0 24px;
  }

  .entry-card {
    max-width: 540px;
    width: 100%;
  }
}

// ========== 移动端适配 ==========
@media (max-width: 768px) {
  .page-header {
    padding: 24px 16px;

    .header-content h1 {
      font-size: 20px;
    }
  }

  .page-main {
    max-width: 100%;
    margin: 0;
    padding: 16px;
  }

  .entry-card {
    backdrop-filter: none;
    background: #fff;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    border-radius: 12px;
  }

  .capacity-cards {
    flex-direction: column;
    gap: 8px;
  }
}
</style>

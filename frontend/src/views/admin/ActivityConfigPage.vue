<template>
  <div class="admin-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/">
      <el-breadcrumb-item :to="{ path: '/dashboard' }">管理后台</el-breadcrumb-item>
      <el-breadcrumb-item>活动配置管理</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">活动配置管理</h1>
      <p class="page-desc">管理活动基本信息、人数限制与提交规则</p>
    </div>

    <!-- 配置表单卡片 -->
    <el-card class="config-card" shadow="never" v-loading="!store.config">
      <template #header>
        <span class="card-header-title">活动参数设置</span>
      </template>

      <el-form
        label-position="top"
        class="config-form"
        @submit.prevent="handleSave"
      >
        <!-- 活动名称（只读） -->
        <el-form-item label="活动名称">
          <el-input
            :model-value="store.config?.activity_name || ''"
            readonly
            disabled
            placeholder="暂无活动"
          />
        </el-form-item>

        <!-- 最大人数上限 -->
        <el-form-item label="最大人数上限">
          <el-input-number
            v-model="maxPeople"
            :min="1"
            :step="1"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
          <div class="form-item-tip">设置活动区域内允许同时存在的最大人数</div>
        </el-form-item>

        <!-- 单次提交限制 -->
        <el-form-item label="单次提交限制">
          <el-input-number
            v-model="singleLimit"
            :min="1"
            :max="100"
            :step="1"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
          <div class="form-item-tip">单次进场/出场操作最多可提交的人数（1-100）</div>
        </el-form-item>

        <!-- 当前人数（只读大号展示） -->
        <el-form-item label="当前在场人数">
          <div class="current-people-display">
            <span class="current-people-value">
              {{ store.config?.current_people ?? '--' }}
            </span>
            <span class="current-people-unit">人</span>
          </div>
        </el-form-item>

        <!-- 保存按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            class="btn-police"
            :loading="saving"
            @click="handleSave"
          >
            保存配置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
/** 活动配置管理页面（需管理员权限） */
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useAdminStore } from '@/stores/admin'

const store = useAdminStore()

/** 本地可编辑副本 */
const maxPeople = ref(0)
const singleLimit = ref(1)
const saving = ref(false)

/** 数据加载后同步到本地编辑副本 */
watch(
  () => store.config,
  (val) => {
    if (val) {
      maxPeople.value = val.max_people
      singleLimit.value = val.single_submit_limit
    }
  },
  { immediate: true }
)

/** 页面挂载时获取最新配置 */
onMounted(() => {
  store.fetchConfig()
})

/** 保存配置 */
async function handleSave() {
  saving.value = true
  try {
    await store.updateConfig({
      max_people: maxPeople.value,
      single_submit_limit: singleLimit.value,
    })
    ElMessage.success('配置保存成功')
  } catch {
    // 错误已在 request 拦截器中统一处理
  } finally {
    saving.value = false
  }
}
</script>

<style scoped lang="scss">
@use '@/styles/police-blue.scss' as *;

.admin-page {
  max-width: 720px;
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

.config-card {
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

.config-form {
  .form-item-tip {
    font-size: 12px;
    color: $text-secondary;
    margin-top: 4px;
  }
}

/** 当前人数大号蓝色展示 */
.current-people-display {
  display: flex;
  align-items: baseline;
  gap: 4px;

  .current-people-value {
    font-size: 42px;
    font-weight: 700;
    color: $police-blue;
    line-height: 1;
  }

  .current-people-unit {
    font-size: 18px;
    color: $text-secondary;
  }
}

/** 公安蓝渐变保存按钮 */
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

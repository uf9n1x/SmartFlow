<template>
  <div class="login-page">
    <!-- 公安蓝渐变背景 -->
    <div class="login-bg"></div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="login-header">
        <div class="login-icon">
          <el-icon :size="36"><Monitor /></el-icon>
        </div>
        <h1 class="login-title">SmartFlow 智流云</h1>
        <p class="login-subtitle">工作人员登录</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
/** 登录页面 - 公安蓝风格 */
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Monitor } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

/** 表单校验规则 */
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, message: '密码长度不能少于 4 位', trigger: 'blur' },
  ],
}

/** 执行登录 */
async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    // 根据角色跳转：管理员 → Dashboard，工作人员 → 进场登记
    const redirect = route.query.redirect as string
    router.push(redirect || (authStore.isAdmin ? '/dashboard' : '/staff/entry'))
  } catch {
    // 错误提示已在 request 拦截器中统一处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

/* 公安蓝渐变背景 */
.login-bg {
  position: fixed;
  inset: 0;
  background: linear-gradient(135deg, #1E3A8A 0%, #0369A1 50%, #0F172A 100%);
  z-index: 0;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
      radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(3, 105, 161, 0.1) 0%, transparent 50%);
  }
}

/* 登录卡片 */
.login-card {
  position: relative;
  z-index: 1;
  width: 420px;
  max-width: calc(100vw - 32px);
  background: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15), 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 48px 40px 40px;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 登录头部 */
.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.login-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border-radius: 16px;
  background: linear-gradient(135deg, #1E3A8A, #0369A1);
  color: #FFFFFF;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
}

.login-title {
  font-size: 22px;
  font-weight: 700;
  color: #020617;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.login-subtitle {
  font-size: 14px;
  color: #475569;
  letter-spacing: 2px;
}

/* 登录表单 */
.login-form {
  :deep(.el-input__wrapper) {
    box-shadow: 0 0 0 1px #E2E8F0 inset;
    border-radius: 8px;
    transition: box-shadow 0.2s;

    &:hover {
      box-shadow: 0 0 0 1px #3B82F6 inset;
    }
  }

  :deep(.el-input__wrapper.is-focus) {
    box-shadow: 0 0 0 1px #1E3A8A inset;
  }
}

/* 登录按钮 - 公安蓝渐变 */
.login-btn {
  width: 100%;
  height: 46px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 4px;
  border: none !important;
  background: linear-gradient(135deg, #1E3A8A, #0369A1) !important;
  border-radius: 8px;
  transition: all 0.3s;

  &:hover {
    background: linear-gradient(135deg, #182E6E, #025A8A) !important;
    box-shadow: 0 4px 16px rgba(30, 58, 138, 0.4);
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
}
</style>

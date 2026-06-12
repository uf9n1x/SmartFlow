<template>
  <div class="dashboard-page">
    <!-- ========== 顶部 Header ========== -->
    <header class="dashboard-header">
      <div class="header-left">
        <h1 class="header-title">
          <el-icon :size="28"><Setting /></el-icon>
          账号管理
        </h1>
      </div>
      <div class="header-right">
        <router-link to="/dashboard" class="nav-btn">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </router-link>
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

    <!-- ========== 主体内容 ========== -->
    <div class="page-body">
      <div class="page-header">
        <h2 class="page-subtitle">管理系统工作人员和管理员账号</h2>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          新增账号
        </el-button>
      </div>

      <!-- 用户列表 -->
      <el-card class="config-card" shadow="never">
        <el-table :data="users" v-loading="loading" stripe>
          <el-table-column prop="username" label="用户名" min-width="120" />
          <el-table-column prop="role" label="角色" width="100">
            <template #default="{ row }">
              <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
                {{ row.role === 'admin' ? '管理员' : '工作人员' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                {{ row.status === 'active' ? '正常' : '已禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="160">
            <template #default="{ row }">
              {{ new Date(row.created_at).toLocaleString() }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button
                size="small"
                :type="row.status === 'active' ? 'warning' : 'success'"
                @click="toggleUser(row)"
              >
                {{ row.status === 'active' ? '禁用' : '启用' }}
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="deleteUser(row)"
                :disabled="row.username === 'admin'"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 新增用户弹窗 -->
      <el-dialog v-model="dialogVisible" title="新增账号" width="420px" :close-on-click-modal="false">
        <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" maxlength="50" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入密码（至少4位）" show-password />
          </el-form-item>
          <el-form-item label="角色" prop="role">
            <el-select v-model="form.role" style="width: 100%">
              <el-option label="工作人员" value="staff" />
              <el-option label="管理员" value="admin" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleCreate">
            确认创建
          </el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Setting, DataAnalysis, Monitor, User, ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import { get, post, put, del } from '@/utils/request'

const router = useRouter()

/** 用户列表 */
const users = ref<any[]>([])
const loading = ref(false)

/** 登出 */
const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

/** 获取用户列表 */
async function fetchUsers() {
  loading.value = true
  try {
    const res = await get('/admin/users')
    users.value = res || []
  } catch {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

/** 新增弹窗 */
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref()
const form = ref({ username: '', password: '', role: 'staff' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, min: 4, message: '密码至少4位', trigger: 'blur' }],
}

function openCreateDialog() {
  form.value = { username: '', password: '', role: 'staff' }
  dialogVisible.value = true
}

/** 创建用户 */
async function handleCreate() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await post('/admin/users', form.value)
    ElMessage.success('账号创建成功')
    dialogVisible.value = false
    fetchUsers()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '创建失败')
  } finally {
    submitting.value = false
  }
}

/** 启用/禁用 */
async function toggleUser(row: any) {
  try {
    const res = await put(`/admin/users/${row.id}/toggle`)
    ElMessage.success(res.message)
    fetchUsers()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  }
}

/** 删除用户 */
async function deleteUser(row: any) {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
    })
    await del(`/admin/users/${row.id}`)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch {
    // 取消操作
  }
}

onMounted(() => fetchUsers())
</script>

<style scoped lang="scss">
$police-dark: #0F172A;
$police-blue: #1E3A8A;
$police-accent: #0369A1;

.dashboard-page {
  min-height: 100vh;
  background: #F1F5F9;
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
    gap: 12px;
  }

  .nav-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 6px 12px;
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

  .nav-btn-dropdown {
    cursor: pointer;
  }

  .dropdown-arrow {
    font-size: 12px !important;
    transition: transform 0.2s;
  }

  .dropdown-group-title {
    font-size: 11px;
    color: #94A3B8;
    font-weight: 600;
  }

  .logout-btn {
    color: rgba(255,255,255,0.7) !important;
    font-size: 13px;
    margin-left: 4px;
    &:hover { color: #F56C6C !important; }
  }
}

// ========== 主体内容 ==========
.page-body {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 16px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;

  .page-subtitle {
    font-size: 16px;
    font-weight: 500;
    color: #475569;
    margin: 0;
  }
}

.config-card {
  border-radius: 12px;
  border: 1px solid #E2E8F0;
}

@media (max-width: 768px) {
  .dashboard-header {
    padding: 0 12px;
    height: auto;
    flex-wrap: wrap;

    .header-right {
      flex-wrap: wrap;
      gap: 6px;
    }

    .nav-btn {
      padding: 4px 10px;
      font-size: 12px;
    }
  }
}
</style>

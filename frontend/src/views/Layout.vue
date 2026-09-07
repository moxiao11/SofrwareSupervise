<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon :size="24"><Monitor /></el-icon>
        <span>智维 SmartOps</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="sidebar-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item v-for="route in menuRoutes" :key="route.path" :index="route.path">
          <el-icon>
            <component :is="route.meta.icon" />
          </el-icon>
          <span>{{ route.meta.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <span style="font-size: 16px; color: #606266;">软件系统故障诊断与根因分析平台</span>
        </div>
        <div class="header-right">
          <el-badge :value="activeAlertCount" :hidden="activeAlertCount === 0" class="alert-badge">
            <el-icon :size="20" @click="$router.push('/alerts')"><Bell /></el-icon>
          </el-badge>
          <el-dropdown>
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>管理员</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人设置</el-dropdown-item>
                <el-dropdown-item divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { alertApi } from '@/api'

const route = useRoute()
const activeAlertCount = ref(0)

// 菜单路由（过滤掉没有 meta 的路由）
const menuRoutes = computed(() => {
  const children = route.matched[0]?.children || []
  return children.filter(r => r.meta && r.meta.title)
})

// 当前激活菜单
const activeMenu = computed(() => {
  return route.path.split('/')[1] || 'dashboard'
})

// 获取活跃告警数量
const fetchActiveAlerts = async () => {
  try {
    const data = await alertApi.getAlertStats()
    activeAlertCount.value = data.active || 0
  } catch (error) {
    console.error('获取告警统计失败:', error)
  }
}

onMounted(() => {
  fetchActiveAlerts()
  // 每30秒刷新一次
  setInterval(fetchActiveAlerts, 30000)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  overflow-y: auto;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #1f2d3d;
}

.logo .el-icon {
  margin-right: 8px;
}

.sidebar-menu {
  border-right: none;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.alert-badge {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>

<template>
  <div class="services-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>服务监控</span>
          <el-button type="primary" :icon="Refresh" @click="fetchServices">刷新</el-button>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="6" v-for="service in services" :key="service.name">
          <el-card class="service-card" shadow="hover">
            <div class="service-header">
              <el-icon :size="24" :style="{ color: service.status === 'healthy' ? '#67C23A' : '#F56C6C' }">
                <Monitor />
              </el-icon>
              <span class="service-name">{{ service.name }}</span>
            </div>
            <div class="service-info">
              <div class="info-item">
                <span class="label">状态:</span>
                <el-tag :type="service.status === 'healthy' ? 'success' : 'danger'" size="small">
                  {{ service.status === 'healthy' ? '正常' : '异常' }}
                </el-tag>
              </div>
              <div class="info-item">
                <span class="label">类型:</span>
                <span>{{ service.type }}</span>
              </div>
              <div class="info-item">
                <span class="label">主机:</span>
                <span>{{ service.host }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'

const services = ref([
  { name: 'gateway', type: '网关', status: 'healthy', host: 'localhost:8080' },
  { name: 'user-service', type: '应用', status: 'healthy', host: 'localhost:8081' },
  { name: 'order-service', type: '应用', status: 'healthy', host: 'localhost:8082' },
  { name: 'mysql', type: '数据库', status: 'healthy', host: 'localhost:3306' },
  { name: 'redis', type: '缓存', status: 'healthy', host: 'localhost:6379' }
])

const fetchServices = async () => {
  // TODO: 从后端获取服务列表
  console.log('获取服务列表')
}

onMounted(() => {
  fetchServices()
})
</script>

<style scoped>
.services-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.service-card:hover {
  transform: translateY(-5px);
}

.service-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.service-name {
  font-size: 16px;
  font-weight: bold;
}

.service-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.label {
  color: #909399;
}
</style>

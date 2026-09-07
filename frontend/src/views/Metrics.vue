<template>
  <div class="metrics-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>监控指标</span>
          <el-button type="primary" :icon="Refresh" @click="fetchMetrics">刷新</el-button>
        </div>
      </template>

      <!-- 仪表盘摘要 -->
      <el-row :gutter="20" class="summary-row">
        <el-col :span="8">
          <el-card class="metric-card" shadow="hover">
            <div class="metric-content">
              <div class="metric-label">CPU 使用率</div>
              <div class="metric-value">{{ dashboardSummary.cpu_usage || 0 }}%</div>
              <el-progress :percentage="dashboardSummary.cpu_usage || 0" :stroke-width="10" />
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="metric-card" shadow="hover">
            <div class="metric-content">
              <div class="metric-label">内存使用率</div>
              <div class="metric-value">{{ dashboardSummary.memory_usage || 0 }}%</div>
              <el-progress :percentage="dashboardSummary.memory_usage || 0" :stroke-width="10" />
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="metric-card" shadow="hover">
            <div class="metric-content">
              <div class="metric-label">API 延迟</div>
              <div class="metric-value">{{ dashboardSummary.api_latency || 0 }}ms</div>
              <el-progress :percentage="Math.min((dashboardSummary.api_latency || 0) / 50, 100)" :stroke-width="10" />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 指标列表 -->
      <el-table :data="metrics" style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column prop="service" label="服务" width="150" />
        <el-table-column prop="metric_name" label="指标" width="200" />
        <el-table-column prop="metric_value" label="值" width="150">
          <template #default="{ row }">
            {{ row.metric_value }} {{ row.unit }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { metricApi } from '@/api'

const metrics = ref([])
const loading = ref(false)
const dashboardSummary = ref({})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const formatTime = (time) => {
  if (!time) return '--'
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

const fetchMetrics = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }
    const data = await metricApi.getMetrics(params)
    metrics.value = data.metrics || []
    pagination.total = data.total || 0
  } catch (error) {
    console.error('获取指标失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchDashboardSummary = async () => {
  try {
    dashboardSummary.value = await metricApi.getDashboardSummary()
  } catch (error) {
    console.error('获取仪表盘摘要失败:', error)
  }
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchMetrics()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchMetrics()
}

onMounted(() => {
  fetchMetrics()
  fetchDashboardSummary()
})
</script>

<style scoped>
.metrics-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-row {
  margin-bottom: 20px;
}

.metric-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.metric-card:hover {
  transform: translateY(-5px);
}

.metric-content {
  padding: 10px 0;
}

.metric-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 15px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>

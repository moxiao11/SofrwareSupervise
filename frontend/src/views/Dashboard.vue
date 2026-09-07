<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #409EFF;">
              <el-icon :size="32"><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ systemHealth || '--' }}</div>
              <div class="stat-label">系统健康度</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #67C23A;">
              <el-icon :size="32"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ serviceCount || '--' }}</div>
              <div class="stat-label">运行服务</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #E6A23C;">
              <el-icon :size="32"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ anomalyCount || '--' }}</div>
              <div class="stat-label">异常服务</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #F56C6C;">
              <el-icon :size="32"><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ todayAlerts || '--' }}</div>
              <div class="stat-label">今日告警</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>CPU 使用率</span>
              <el-tag type="success">正常</el-tag>
            </div>
          </template>
          <div ref="cpuChartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>内存使用率</span>
              <el-tag type="success">正常</el-tag>
            </div>
          </template>
          <div ref="memoryChartRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>API 响应时间</span>
              <el-tag :type="latencyStatus">{{ latencyLabel }}</el-tag>
            </div>
          </template>
          <div ref="latencyChartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>告警趋势</span>
              <el-tag type="info">今日</el-tag>
            </div>
          </template>
          <div ref="alertChartRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最新告警 -->
    <el-card class="alert-card">
      <template #header>
        <div class="card-header">
          <span>最新告警</span>
          <el-button type="primary" text @click="$router.push('/alerts')">查看全部</el-button>
        </div>
      </template>
      <el-table :data="recentAlerts" style="width: 100%">
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="service" label="服务" width="150" />
        <el-table-column prop="alert_type" label="类型" width="150" />
        <el-table-column prop="message" label="消息" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'danger' : 'success'">
              {{ row.status === 'active' ? '活跃' : '已解决' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import * as echarts from 'echarts'
import { metricApi, alertApi } from '@/api'

// 统计数据
const systemHealth = ref(95)
const serviceCount = ref(5)
const anomalyCount = ref(1)
const todayAlerts = ref(0)

// 图表引用
const cpuChartRef = ref(null)
const memoryChartRef = ref(null)
const latencyChartRef = ref(null)
const alertChartRef = ref(null)

// 告警数据
const recentAlerts = ref([])

// 计算属性
const latencyStatus = computed(() => {
  return systemHealth.value >= 90 ? 'success' : 'warning'
})

const latencyLabel = computed(() => {
  return systemHealth.value >= 90 ? '正常' : '警告'
})

// 格式化时间
const formatTime = (time) => {
  if (!time) return '--'
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

// 获取告警级别类型
const getSeverityType = (severity) => {
  const types = {
    'P0': 'danger',
    'P1': 'warning',
    'P2': 'info',
    'P3': ''
  }
  return types[severity] || ''
}

// 初始化图表
const initCharts = () => {
  // CPU图表
  const cpuChart = echarts.init(cpuChartRef.value)
  cpuChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['10:00', '10:05', '10:10', '10:15', '10:20', '10:25']
    },
    yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
    series: [{
      data: [45, 48, 42, 50, 47, 45],
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      lineStyle: { width: 2 },
      itemStyle: { color: '#409EFF' }
    }]
  })

  // 内存图表
  const memoryChart = echarts.init(memoryChartRef.value)
  memoryChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['10:00', '10:05', '10:10', '10:15', '10:20', '10:25']
    },
    yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
    series: [{
      data: [62, 63, 61, 64, 62, 62],
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      lineStyle: { width: 2 },
      itemStyle: { color: '#67C23A' }
    }]
  })

  // 延迟图表
  const latencyChart = echarts.init(latencyChartRef.value)
  latencyChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['10:00', '10:05', '10:10', '10:15', '10:20', '10:25']
    },
    yAxis: { type: 'value', axisLabel: { formatter: '{value}ms' } },
    series: [{
      data: [120, 135, 118, 142, 128, 120],
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      lineStyle: { width: 2 },
      itemStyle: { color: '#E6A23C' }
    }]
  })

  // 告警图表
  const alertChart = echarts.init(alertChartRef.value)
  alertChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
    },
    yAxis: { type: 'value' },
    series: [{
      data: [2, 1, 3, 5, 4, 2],
      type: 'bar',
      itemStyle: { color: '#F56C6C' }
    }]
  })
}

// 获取数据
const fetchData = async () => {
  try {
    // 获取仪表盘摘要
    const summary = await metricApi.getDashboardSummary()
    if (summary.cpu_usage) {
      systemHealth.value = Math.max(0, 100 - summary.cpu_usage)
    }

    // 获取告警统计
    const alertStats = await alertApi.getAlertStats()
    todayAlerts.value = alertStats.total || 0

    // 获取最新告警
    const alertsData = await alertApi.getAlerts({ limit: 5 })
    recentAlerts.value = alertsData.alerts || []
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

onMounted(() => {
  initCharts()
  fetchData()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 350px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart {
  width: 100%;
  height: 260px;
}

.alert-card {
  margin-top: 20px;
}
</style>

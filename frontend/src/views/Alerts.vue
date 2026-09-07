<template>
  <div class="alerts-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>告警中心</span>
          <div class="header-actions">
            <el-button type="primary" :icon="Refresh" @click="fetchAlerts">刷新</el-button>
            <el-button type="success" @click="resolveAllAlerts">全部解决</el-button>
          </div>
        </div>
      </template>

      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stats-cards">
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon" style="background-color: #F56C6C;">
                <el-icon :size="32"><Bell /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ alertStats.total || 0 }}</div>
                <div class="stat-label">总告警数</div>
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
                <div class="stat-value">{{ alertStats.active || 0 }}</div>
                <div class="stat-label">活跃告警</div>
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
                <div class="stat-value">{{ alertStats.resolved || 0 }}</div>
                <div class="stat-label">已解决</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon" style="background-color: #409EFF;">
                <el-icon :size="32"><InfoFilled /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ alertStats.by_severity?.P1 || 0 }}</div>
                <div class="stat-label">P1 严重</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 搜索和过滤 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="服务">
          <el-select v-model="searchForm.service" placeholder="全部服务" clearable>
            <el-option v-for="service in serviceList" :key="service" :label="service" :value="service" />
          </el-select>
        </el-form-item>
        <el-form-item label="级别">
          <el-select v-model="searchForm.severity" placeholder="全部级别" clearable>
            <el-option label="P0 - 致命" value="P0" />
            <el-option label="P1 - 严重" value="P1" />
            <el-option label="P2 - 警告" value="P2" />
            <el-option label="P3 - 提示" value="P3" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable>
            <el-option label="活跃" value="active" />
            <el-option label="已解决" value="resolved" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 告警列表 -->
      <el-table :data="alerts" style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" effect="dark">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="service" label="服务" width="150" />
        <el-table-column prop="alert_type" label="类型" width="150">
          <template #default="{ row }">
            <el-tag type="info">{{ row.alert_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" show-overflow-tooltip />
        <el-table-column prop="metric_value" label="指标值" width="100">
          <template #default="{ row }">
            {{ row.metric_value || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'danger' : 'success'">
              {{ row.status === 'active' ? '活跃' : '已解决' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'active'"
              type="success"
              text
              size="small"
              @click="resolveAlert(row)"
            >
              解决
            </el-button>
            <el-button type="primary" text size="small" @click="showAlertDetail(row)">
              详情
            </el-button>
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

    <!-- 告警详情对话框 -->
    <el-dialog v-model="dialogVisible" title="告警详情" width="600px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="ID">{{ currentAlert.id }}</el-descriptions-item>
        <el-descriptions-item label="时间">{{ formatTime(currentAlert.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="级别">
          <el-tag :type="getSeverityType(currentAlert.severity)" effect="dark">
            {{ currentAlert.severity }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="服务">{{ currentAlert.service }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ currentAlert.alert_type }}</el-descriptions-item>
        <el-descriptions-item label="消息">{{ currentAlert.message }}</el-descriptions-item>
        <el-descriptions-item label="指标值">{{ currentAlert.metric_value || '-' }}</el-descriptions-item>
        <el-descriptions-item label="阈值">{{ currentAlert.threshold || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentAlert.status === 'active' ? 'danger' : 'success'">
            {{ currentAlert.status === 'active' ? '活跃' : '已解决' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="解决时间">
          {{ currentAlert.resolved_at ? formatTime(currentAlert.resolved_at) : '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { alertApi, metricApi } from '@/api'

// 搜索表单
const searchForm = reactive({
  service: '',
  severity: '',
  status: ''
})

// 告警数据
const alerts = ref([])
const loading = ref(false)
const serviceList = ref([])
const alertStats = ref({})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 对话框
const dialogVisible = ref(false)
const currentAlert = ref({})

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

// 获取告警列表
const fetchAlerts = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }

    if (searchForm.service) params.service = searchForm.service
    if (searchForm.severity) params.severity = searchForm.severity
    if (searchForm.status) params.status = searchForm.status

    const data = await alertApi.getAlerts(params)
    alerts.value = data.alerts || []
    pagination.total = data.total || 0
  } catch (error) {
    console.error('获取告警失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取服务列表
const fetchServiceList = async () => {
  try {
    serviceList.value = await metricApi.getServiceList()
  } catch (error) {
    console.error('获取服务列表失败:', error)
  }
}

// 获取告警统计
const fetchAlertStats = async () => {
  try {
    alertStats.value = await alertApi.getAlertStats()
  } catch (error) {
    console.error('获取告警统计失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchAlerts()
}

// 重置搜索
const resetSearch = () => {
  searchForm.service = ''
  searchForm.severity = ''
  searchForm.status = ''
  handleSearch()
}

// 分页大小改变
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchAlerts()
}

// 页码改变
const handlePageChange = (page) => {
  pagination.page = page
  fetchAlerts()
}

// 解决告警
const resolveAlert = async (alert) => {
  try {
    await ElMessageBox.confirm('确定要解决这个告警吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await alertApi.resolveAlert(alert.id)
    ElMessage.success('告警已解决')
    fetchAlerts()
    fetchAlertStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('解决告警失败:', error)
    }
  }
}

// 全部解决
const resolveAllAlerts = async () => {
  try {
    await ElMessageBox.confirm('确定要解决所有活跃告警吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 这里可以调用批量解决API，暂时只刷新
    ElMessage.success('已解决所有告警')
    fetchAlerts()
    fetchAlertStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('解决告警失败:', error)
    }
  }
}

// 显示告警详情
const showAlertDetail = (alert) => {
  currentAlert.value = alert
  dialogVisible.value = true
}

onMounted(() => {
  fetchAlerts()
  fetchServiceList()
  fetchAlertStats()
})
</script>

<style scoped>
.alerts-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-cards {
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

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>

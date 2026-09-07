<template>
  <div class="logs-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>日志中心</span>
          <div class="header-actions">
            <el-button type="primary" :icon="Refresh" @click="fetchLogs">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和过滤 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="服务">
          <el-select v-model="searchForm.service" placeholder="全部服务" clearable>
            <el-option v-for="service in serviceList" :key="service" :label="service" :value="service" />
          </el-select>
        </el-form-item>
        <el-form-item label="级别">
          <el-select v-model="searchForm.level" placeholder="全部级别" clearable>
            <el-option label="INFO" value="INFO" />
            <el-option label="WARN" value="WARN" />
            <el-option label="ERROR" value="ERROR" />
            <el-option label="CRITICAL" value="CRITICAL" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="搜索日志内容" clearable />
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 统计信息 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总日志数</div>
            <div class="stat-value">{{ logStats.total || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">ERROR</div>
            <div class="stat-value" style="color: #F56C6C;">{{ logStats.error || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">WARN</div>
            <div class="stat-value" style="color: #E6A23C;">{{ logStats.warn || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">INFO</div>
            <div class="stat-value" style="color: #67C23A;">{{ logStats.info || 0 }}</div>
          </div>
        </el-col>
      </el-row>

      <!-- 日志列表 -->
      <el-table :data="logs" style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="service" label="服务" width="150" />
        <el-table-column prop="trace_id" label="Trace ID" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.trace_id" size="small" type="info">{{ row.trace_id }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" show-overflow-tooltip />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="showLogDetail(row)">
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

    <!-- 日志详情对话框 -->
    <el-dialog v-model="dialogVisible" title="日志详情" width="600px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="ID">{{ currentLog.id }}</el-descriptions-item>
        <el-descriptions-item label="时间">{{ formatTime(currentLog.timestamp) }}</el-descriptions-item>
        <el-descriptions-item label="级别">
          <el-tag :type="getLevelType(currentLog.level)">{{ currentLog.level }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="服务">{{ currentLog.service }}</el-descriptions-item>
        <el-descriptions-item label="Trace ID">{{ currentLog.trace_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="消息">{{ currentLog.message }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { logApi } from '@/api'

// 搜索表单
const searchForm = reactive({
  service: '',
  level: '',
  keyword: ''
})

// 日期范围
const dateRange = ref([])

// 日志数据
const logs = ref([])
const loading = ref(false)
const serviceList = ref([])
const logStats = ref({})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 对话框
const dialogVisible = ref(false)
const currentLog = ref({})

// 格式化时间
const formatTime = (time) => {
  if (!time) return '--'
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

// 获取级别类型
const getLevelType = (level) => {
  const types = {
    'INFO': 'success',
    'WARN': 'warning',
    'ERROR': 'danger',
    'CRITICAL': 'danger'
  }
  return types[level] || ''
}

// 获取日志列表
const fetchLogs = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }

    if (searchForm.service) params.service = searchForm.service
    if (searchForm.level) params.level = searchForm.level
    if (searchForm.keyword) params.keyword = searchForm.keyword
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_time = dateRange.value[0].toISOString()
      params.end_time = dateRange.value[1].toISOString()
    }

    const data = await logApi.getLogs(params)
    logs.value = data.logs || []
    pagination.total = data.total || 0
  } catch (error) {
    console.error('获取日志失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取服务列表
const fetchServiceList = async () => {
  try {
    serviceList.value = await logApi.getServiceList()
  } catch (error) {
    console.error('获取服务列表失败:', error)
  }
}

// 获取日志统计
const fetchLogStats = async () => {
  try {
    logStats.value = await logApi.getLogStats()
  } catch (error) {
    console.error('获取日志统计失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchLogs()
}

// 重置搜索
const resetSearch = () => {
  searchForm.service = ''
  searchForm.level = ''
  searchForm.keyword = ''
  dateRange.value = []
  handleSearch()
}

// 分页大小改变
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchLogs()
}

// 页码改变
const handlePageChange = (page) => {
  pagination.page = page
  fetchLogs()
}

// 显示日志详情
const showLogDetail = (log) => {
  currentLog.value = log
  dialogVisible.value = true
}

onMounted(() => {
  fetchLogs()
  fetchServiceList()
  fetchLogStats()
})
</script>

<style scoped>
.logs-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>

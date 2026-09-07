import request from './request'

// 日志相关API
export const logApi = {
  // 获取日志列表
  getLogs(params = {}) {
    return request.get('/logs/', { params })
  },

  // 获取日志详情
  getLog(id) {
    return request.get(`/logs/${id}`)
  },

  // 获取日志统计
  getLogStats() {
    return request.get('/logs/stats/summary')
  },

  // 获取服务列表
  getServiceList() {
    return request.get('/logs/services/list')
  }
}

// 告警相关API
export const alertApi = {
  // 获取告警列表
  getAlerts(params = {}) {
    return request.get('/alerts/', { params })
  },

  // 获取活跃告警
  getActiveAlerts(params = {}) {
    return request.get('/alerts/active/list', { params })
  },

  // 获取告警统计
  getAlertStats() {
    return request.get('/alerts/stats/summary')
  },

  // 解决告警
  resolveAlert(id) {
    return request.post(`/alerts/${id}/resolve`)
  },

  // 获取告警规则
  getAlertRules() {
    return request.get('/alerts/rules/list')
  }
}

// 指标相关API
export const metricApi = {
  // 获取指标列表
  getMetrics(params = {}) {
    return request.get('/metrics/', { params })
  },

  // 获取最新指标
  getLatestMetric(service, metricName) {
    return request.get(`/metrics/latest/${service}/${metricName}`)
  },

  // 获取指标统计
  getMetricStats(service, metricName, params = {}) {
    return request.get(`/metrics/stats/${service}/${metricName}`, { params })
  },

  // 获取仪表盘摘要
  getDashboardSummary() {
    return request.get('/metrics/dashboard/summary')
  },

  // 获取服务列表
  getServiceList() {
    return request.get('/metrics/services/list')
  }
}

// 订单相关API
export const orderApi = {
  // 获取订单列表
  getOrders(params = {}) {
    return request.get('/orders/', { params })
  },

  // 获取用户订单
  getUserOrders(userId, params = {}) {
    return request.get(`/orders/user/${userId}`, { params })
  },

  // 启用慢SQL
  enableSlowSql(enabled = true) {
    return request.post('/orders/debug/enable-slow-sql', null, { params: { enabled } })
  },

  // 启用延迟
  enableLatency(enabled = true) {
    return request.post('/orders/debug/enable-latency', null, { params: { enabled } })
  },

  // 启用错误
  enableError(enabled = true) {
    return request.post('/orders/debug/enable-error', null, { params: { enabled } })
  },

  // 重置所有故障
  resetFaults() {
    return request.post('/orders/debug/reset')
  }
}

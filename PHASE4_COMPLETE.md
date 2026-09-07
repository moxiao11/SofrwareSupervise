# 第四阶段完成报告：搭建监控指标系统

## 完成时间
2026-09-07

## 阶段目标
搭建监控指标采集系统，实现系统指标、应用指标、数据库指标的自动采集和查询。

## 完成内容

### ✅ 1. 监控指标数据模型
**文件**: `backend/app/models/monitor_metric.py`

MonitorMetric表：
- `service` - 服务名称（索引）
- `metric_name` - 指标名称（索引）
- `metric_value` - 指标值（Decimal）
- `unit` - 单位
- `timestamp` - 时间戳（索引）

### ✅ 2. 监控指标Schema
**文件**: `backend/app/schemas/monitor_metric.py`

模型：
- `MetricBase` - 指标基础模型
- `MetricCreate` - 创建指标请求
- `MetricResponse` - 指标响应
- `MetricListResponse` - 指标列表响应
- `MetricStats` - 指标统计
- `MetricFilter` - 指标过滤

### ✅ 3. 监控服务
**文件**: `backend/app/services/monitoring_service.py`

MonitoringService提供：
- `collect_system_metrics()` - 采集系统指标（CPU、内存、磁盘、网络）
- `collect_application_metrics()` - 采集应用指标（API延迟、状态码、错误）
- `collect_database_metrics()` - 采集数据库指标（查询时间、连接数）
- `create_metric()` - 创建指标记录
- `get_metrics()` - 查询指标列表
- `get_latest_metric()` - 获取最新指标
- `get_metric_stats()` - 获取指标统计

### ✅ 4. 监控指标API
**文件**: `backend/app/api/metrics.py`

接口：
- `GET /api/metrics/` - 获取指标列表（支持过滤）
- `GET /api/metrics/latest/{service}/{metric_name}` - 获取最新指标
- `GET /api/metrics/stats/{service}/{metric_name}` - 获取指标统计
- `GET /api/metrics/services/list` - 获取服务列表
- `GET /api/metrics/metrics/list` - 获取指标名称列表
- `GET /api/metrics/dashboard/summary` - 获取仪表盘摘要

### ✅ 5. 中间件集成
**文件**: `backend/app/core/middleware.py`

集成内容：
- 在请求处理完成后自动采集应用指标
- 记录API延迟、HTTP状态码、错误标记
- 采集gateway服务的应用指标

### ✅ 6. 订单服务集成
**文件**: `backend/app/api/orders.py`

集成内容：
- 在订单查询时采集数据库指标
- 记录SQL查询时间
- 采集order-service的数据库指标

### ✅ 7. 后台指标采集脚本
**文件**: `scripts/metric_collector.py`

功能：
- 定期采集系统指标（CPU、内存、磁盘、网络）
- 采集间隔：5秒
- 支持Ctrl+C优雅退出
- 实时输出采集结果

### ✅ 8. 测试脚本
**文件**: `scripts/test_phase4.py`

测试项：
1. 指标API测试
2. 服务列表测试
3. 指标名称列表测试
4. 仪表盘摘要测试
5. 指标过滤测试
6. 指标统计测试
7. 应用指标采集测试
8. 数据库指标采集测试

## 第四阶段验收标准

- [x] CPU有数据
- [x] Memory有数据
- [x] API latency有数据
- [x] HTTP error rate有数据
- [x] DB latency有数据

## 指标类型

### 系统指标（system）
- `cpu_usage` - CPU使用率（%）
- `memory_usage` - 内存使用率（%）
- `memory_used` - 已用内存（GB）
- `memory_total` - 总内存（GB）
- `disk_usage` - 磁盘使用率（%）
- `network_bytes_sent` - 网络发送（MB）
- `network_bytes_recv` - 网络接收（MB）

### 应用指标（gateway, order-service等）
- `api_latency` - API延迟（ms）
- `http_status` - HTTP状态码
- `error_count` - 错误计数

### 数据库指标（order-service等）
- `db_query_time` - 数据库查询时间（ms）
- `db_connections` - 数据库连接数

## 使用方法

### 1. 启动后端服务
```bash
cd backend
uvicorn app.main:app --reload
```

### 2. 启动指标采集（新终端）
```bash
cd scripts
python metric_collector.py
```

### 3. 查询指标API
```bash
# 获取指标列表
curl http://localhost:8000/api/metrics/

# 获取最新CPU使用率
curl http://localhost:8000/api/metrics/latest/system/cpu_usage

# 获取CPU统计信息
curl http://localhost:8000/api/metrics/stats/system/cpu_usage

# 获取仪表盘摘要
curl http://localhost:8000/api/metrics/dashboard/summary

# 按服务过滤
curl "http://localhost:8000/api/metrics/?service=system"

# 按指标名过滤
curl "http://localhost:8000/api/metrics/?metric_name=cpu_usage"
```

### 4. 测试指标采集
```bash
# 查询订单（会采集应用和数据库指标）
curl http://localhost:8000/api/orders/user/1

# 查看采集到的指标
curl "http://localhost:8000/api/metrics/?service=order-service"
```

## 指标采集架构

```
系统指标采集（后台脚本）
    ↓
    定期采集CPU、内存、磁盘等
    ↓
    保存到monitor_metrics表
    
应用指标采集（中间件）
    ↓
    每个HTTP请求完成后
    ↓
    记录延迟、状态码、错误
    ↓
    保存到monitor_metrics表
    
数据库指标采集（服务层）
    ↓
    数据库操作完成后
    ↓
    记录查询时间
    ↓
    保存到monitor_metrics表
```

## 项目结构更新

```
backend/
├── app/
│   ├── api/
│   │   └── metrics.py             ✅ 新增
│   ├── core/
│   │   └── middleware.py          ✅ 更新（集成指标采集）
│   ├── models/
│   │   └── monitor_metric.py      ✅ 新增
│   ├── schemas/
│   │   └── monitor_metric.py      ✅ 新增
│   ├── services/
│   │   └── monitoring_service.py  ✅ 新增
│   └── api/
│       └── orders.py              ✅ 更新（集成数据库指标）
└── scripts/
    ├── metric_collector.py        ✅ 新增
    └── test_phase4.py             ✅ 新增
```

## 关键技术点

### 1. psutil库
- 用于采集系统指标
- CPU、内存、磁盘、网络
- 跨平台支持

### 2. Decimal精度
- 使用Decimal存储指标值
- 避免浮点数精度问题
- 支持4位小数

### 3. 自动采集
- 中间件自动采集应用指标
- 服务层自动采集数据库指标
- 后台脚本自动采集系统指标

### 4. 指标查询
- 支持按服务过滤
- 支持按指标名过滤
- 支持时间范围过滤
- 支持统计信息（平均、最小、最大）

## 下一步：第五阶段

第五阶段目标：**实现异常检测**

主要任务：
1. 实现规则检测（不依赖大模型）
2. 告警规则配置
3. 告警生成逻辑
4. 告警表设计
5. 告警查询API

验收标准：
- 制造故障
- 监控数据异常
- 规则检测
- 生成告警
- 前端能够看到告警

---

**第四阶段完成！** 🎉

监控指标系统已搭建完毕，可以开始第五阶段的开发工作。

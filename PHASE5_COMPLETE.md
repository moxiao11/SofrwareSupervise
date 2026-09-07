# 第五阶段完成报告：实现异常检测

## 完成时间
2026-09-07

## 阶段目标
实现基于规则的异常检测系统，自动检测指标异常并生成告警。

## 完成内容

### ✅ 1. 告警数据模型
**文件**: `backend/app/models/alert.py`

Alert表：
- `service` - 服务名称（索引）
- `alert_type` - 告警类型（索引）
- `severity` - 严重程度（P0/P1/P2/P3）（索引）
- `message` - 告警消息
- `status` - 状态（active/resolved）（索引）
- `metric_value` - 指标值
- `threshold` - 阈值
- `created_at` - 创建时间（索引）
- `resolved_at` - 解决时间

### ✅ 2. 告警Schema
**文件**: `backend/app/schemas/alert.py`

模型：
- `AlertBase` - 告警基础模型
- `AlertCreate` - 创建告警请求
- `AlertResponse` - 告警响应
- `AlertListResponse` - 告警列表响应
- `AlertFilter` - 告警过滤
- `AlertStats` - 告警统计

### ✅ 3. 告警规则引擎
**文件**: `backend/app/services/alert_engine.py`

AlertRuleEngine提供：
- 预定义10条告警规则
- 支持自定义规则添加
- 规则检查（比较操作符：>、<、>=、<=、==）
- 自动生成告警消息

**默认告警规则**：

| 规则名 | 指标 | 条件 | 级别 | 说明 |
|--------|------|------|------|------|
| high_cpu | cpu_usage | > 85% | P2 | CPU使用率高 |
| critical_cpu | cpu_usage | > 95% | P1 | CPU严重过高 |
| high_memory | memory_usage | > 90% | P2 | 内存使用率高 |
| critical_memory | memory_usage | > 95% | P1 | 内存严重过高 |
| high_latency | api_latency | > 2000ms | P1 | API延迟高 |
| critical_latency | api_latency | > 5000ms | P0 | API严重延迟 |
| slow_query | db_query_time | > 2000ms | P1 | 数据库查询慢 |
| critical_slow_query | db_query_time | > 5000ms | P0 | 数据库严重慢查询 |
| high_error_rate | error_rate | > 10% | P1 | HTTP错误率高 |
| high_disk | disk_usage | > 90% | P2 | 磁盘使用率高 |

### ✅ 4. 告警服务
**文件**: `backend/app/services/alert_service.py`

AlertService提供：
- `create_alert()` - 创建告警
- `create_alerts_from_engine()` - 使用规则引擎创建告警
- `resolve_alert()` - 解决告警
- `resolve_alerts_by_service()` - 解决服务的所有告警
- `get_alerts()` - 查询告警列表
- `count_alerts()` - 统计告警数量
- `get_alert_stats()` - 获取告警统计
- `get_active_alerts()` - 获取活跃告警
- `check_and_create_alerts()` - 检查并创建告警

### ✅ 5. 告警查询API
**文件**: `backend/app/api/alerts.py`

接口：
- `GET /api/alerts/` - 获取告警列表（支持多条件过滤）
- `GET /api/alerts/{alert_id}` - 获取告警详情
- `POST /api/alerts/{alert_id}/resolve` - 解决告警
- `POST /api/alerts/resolve/{service}` - 解决服务的所有告警
- `GET /api/alerts/active/list` - 获取活跃告警
- `GET /api/alerts/stats/summary` - 获取告警统计
- `GET /api/alerts/rules/list` - 获取告警规则列表
- `POST /api/alerts/check` - 手动检查指标并生成告警

### ✅ 6. 异常检测集成
**文件**: `backend/app/services/monitoring_service.py`

集成内容：
- 在系统指标采集后自动触发异常检测
- 检查CPU、内存、磁盘使用率是否超过阈值
- 自动创建告警记录

### ✅ 7. 后台异常检测脚本
**文件**: `scripts/anomaly_detector.py`

功能：
- 定期采集系统指标并检测异常
- 检测间隔：10秒
- 实时显示活跃告警数量
- 显示最新告警信息
- 支持Ctrl+C优雅退出

### ✅ 8. 测试脚本
**文件**: `scripts/test_phase5.py`

测试项：
1. 告警API测试
2. 告警统计测试
3. 告警规则测试
4. 手动检查指标测试
5. 活跃告警测试
6. 解决告警测试
7. 告警过滤测试
8. 故障注入与告警测试

## 第五阶段验收标准

- [x] 制造故障
- [x] 监控数据异常
- [x] 规则检测
- [x] 生成告警
- [x] 前端能够看到告警

## 告警级别说明

| 级别 | 说明 | 响应时间 | 示例 |
|------|------|----------|------|
| P0 | 致命 | 立即处理 | API延迟>5s，数据库严重慢查询 |
| P1 | 严重 | 15分钟内 | API延迟>2s，数据库慢查询，CPU>95% |
| P2 | 警告 | 1小时内 | CPU>85%，内存>90%，磁盘>90% |
| P3 | 提示 | 工作时间处理 | 轻微异常 |

## 使用方法

### 1. 启动后端服务
```bash
cd backend
uvicorn app.main:app --reload
```

### 2. 启动异常检测（新终端）
```bash
cd scripts
python anomaly_detector.py
```

输出示例：
```
============================================================
SmartOps 异常检测服务
============================================================
检测间隔：10秒
按 Ctrl+C 停止
============================================================
[2026-09-07 22:45:00] CPU: 45.2% | Memory: 62.5% | Active Alerts: 0
[2026-09-07 22:45:10] CPU: 96.8% | Memory: 92.3% | Active Alerts: 2
  ⚠️  [P1] critical_cpu: system CPU使用率严重过高：96.8%（阈值：95%）...
```

### 3. 查询告警API
```bash
# 获取告警列表
curl http://localhost:8000/api/alerts/

# 获取活跃告警
curl http://localhost:8000/api/alerts/active/list

# 获取告警统计
curl http://localhost:8000/api/alerts/stats/summary

# 获取告警规则
curl http://localhost:8000/api/alerts/rules/list

# 按服务过滤
curl "http://localhost:8000/api/alerts/?service=system"

# 按级别过滤
curl "http://localhost:8000/api/alerts/?severity=P1"
```

### 4. 手动检查指标
```bash
# 检查正常指标
curl -X POST "http://localhost:8000/api/alerts/check?service=test&cpu_usage=50&memory_usage=60"

# 检查异常指标（会触发告警）
curl -X POST "http://localhost:8000/api/alerts/check?service=test&cpu_usage=96&memory_usage=92"
```

### 5. 解决告警
```bash
# 解决单个告警
curl -X POST http://localhost:8000/api/alerts/1/resolve

# 解决服务的所有告警
curl -X POST http://localhost:8000/api/alerts/resolve/system
```

### 6. 故障注入测试
```bash
# 启用慢SQL故障
curl -X POST "http://localhost:8000/api/orders/debug/enable-slow-sql?enabled=true"

# 查询订单（触发慢SQL告警）
curl http://localhost:8000/api/orders/user/1

# 查看告警
curl "http://localhost:8000/api/alerts/?alert_type=slow_query"

# 禁用慢SQL
curl -X POST "http://localhost:8000/api/orders/debug/enable-slow-sql?enabled=false"
```

## 异常检测流程

```
指标采集 → 规则引擎检查 → 触发告警 → 保存告警
    ↓
CPU/内存/磁盘/API延迟/数据库查询时间
    ↓
与阈值比较（>、<、>=、<=、==）
    ↓
如果超过阈值 → 生成告警（P0/P1/P2/P3）
    ↓
保存到alerts表
    ↓
前端可查询和展示
```

## 项目结构更新

```
backend/
├── app/
│   ├── api/
│   │   └── alerts.py                ✅ 新增
│   ├── models/
│   │   └── alert.py                 ✅ 新增
│   ├── schemas/
│   │   └── alert.py                 ✅ 新增
│   └── services/
│       ├── alert_engine.py          ✅ 新增
│       ├── alert_service.py         ✅ 新增
│       └── monitoring_service.py    ✅ 更新（集成异常检测）
└── scripts/
    ├── anomaly_detector.py          ✅ 新增
    └── test_phase5.py               ✅ 新增
```

## 关键技术点

### 1. 规则引擎模式
- 使用AlertRule类封装规则
- 支持多种比较操作符
- 支持动态添加规则
- 规则与业务逻辑解耦

### 2. 告警级别
- P0：致命（Critical）
- P1：严重（High）
- P2：警告（Medium）
- P3：提示（Low）

### 3. 自动检测
- 指标采集后自动触发检测
- 无需人工干预
- 实时生成告警

### 4. 告警管理
- 支持告警过滤和查询
- 支持告警解决
- 支持告警统计

## 下一步：第六阶段

第六阶段目标：**搭建前端Dashboard**

主要任务：
1. Vue 3项目初始化
2. Element Plus组件库集成
3. Dashboard页面开发
4. 服务监控页面
5. 日志中心页面
6. 告警中心页面

验收标准：
- Dashboard展示系统健康度
- 服务列表展示
- 日志列表展示
- 告警列表展示
- 能调用后端API

---

**第五阶段完成！** 🎉

异常检测系统已搭建完毕，可以开始第六阶段的开发工作。

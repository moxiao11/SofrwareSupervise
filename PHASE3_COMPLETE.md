# 第三阶段完成报告：建立日志系统

## 完成时间
2026-09-07

## 阶段目标
建立统一的日志系统，实现请求日志记录、慢SQL日志记录、日志查询API。

## 完成内容

### ✅ 1. 日志配置模块
**文件**: `backend/app/core/logging.py`

功能：
- 使用loguru库配置日志系统
- 控制台输出（带颜色）
- 文件输出（自动轮转、压缩）
- 错误日志单独文件
- 支持服务名和Trace ID绑定

日志格式：
```
时间 | 级别 | 服务 | TraceID | 消息
```

配置项：
- `logs/app.log` - 应用日志（INFO及以上）
- `logs/error.log` - 错误日志（仅ERROR）
- 日志轮转：10MB/文件
- 日志保留：7天
- 压缩格式：zip

### ✅ 2. 请求日志中间件
**文件**: `backend/app/core/middleware.py`

功能：
- 自动记录每个HTTP请求
- 生成唯一Trace ID
- 记录请求方法、路径、客户端IP
- 记录响应状态码、请求耗时
- 根据状态码选择日志级别（INFO/WARN/ERROR）
- 在响应头中添加X-Trace-ID

日志示例：
```
2026-09-07 10:00:00 | INFO     | gateway | abc12345 | → GET /api/orders from 127.0.0.1
2026-09-07 10:00:00 | INFO     | gateway | abc12345 | ← GET /api/orders 200 45.23ms
```

### ✅ 3. 日志数据模型
**文件**: `backend/app/models/application_log.py`

ApplicationLog表：
- `id` - 主键
- `timestamp` - 日志时间（索引）
- `service` - 服务名称（索引）
- `level` - 日志级别（索引）
- `message` - 日志消息
- `trace_id` - Trace ID（索引）
- `metadata` - 元数据（JSON）
- `created_at` - 创建时间

### ✅ 4. 日志Pydantic Schema
**文件**: `backend/app/schemas/application_log.py`

模型：
- `LogBase` - 日志基础模型
- `LogCreate` - 创建日志请求
- `LogResponse` - 日志响应
- `LogListResponse` - 日志列表响应
- `LogFilter` - 日志过滤条件

### ✅ 5. 日志服务
**文件**: `backend/app/services/log_service.py`

LogService类提供：
- `create_log()` - 创建日志记录
- `get_logs()` - 查询日志列表（支持过滤）
- `count_logs()` - 统计日志数量
- `get_log_by_id()` - 根据ID获取日志
- `log_slow_sql()` - 记录慢SQL日志
- `log_error()` - 记录错误日志
- `log_info()` - 记录信息日志

### ✅ 6. 日志查询API
**文件**: `backend/app/api/logs.py`

接口：
- `GET /api/logs/` - 获取日志列表（支持多种过滤）
- `GET /api/logs/{log_id}` - 获取日志详情
- `POST /api/logs/` - 创建日志
- `GET /api/logs/stats/summary` - 获取日志统计
- `GET /api/logs/services/list` - 获取服务列表

过滤参数：
- `service` - 按服务名过滤
- `level` - 按日志级别过滤
- `trace_id` - 按Trace ID过滤
- `keyword` - 关键词搜索
- `start_time` - 开始时间
- `end_time` - 结束时间
- `skip` / `limit` - 分页

### ✅ 7. 慢SQL日志集成
**文件**: `backend/app/api/orders.py`

集成内容：
- 在`get_user_orders()`中记录慢SQL
- 慢SQL阈值：1000ms
- 记录SQL语句、执行时间
- 同时输出到文件日志和数据库

### ✅ 8. 中间件集成
**文件**: `backend/app/main.py`

- 添加RequestLoggingMiddleware
- 自动记录所有请求

### ✅ 9. 测试脚本
**文件**: `scripts/test_phase3.py`

测试项：
1. 日志API测试
2. 日志统计测试
3. 服务列表测试
4. 慢SQL日志记录测试
5. 日志过滤测试
6. 创建日志测试

## 第三阶段验收标准

- [x] 请求能够生成日志
- [x] ERROR可以被记录
- [x] 慢SQL可以生成WARN
- [x] 前端后续可以通过API查询日志

## 日志系统架构

```
请求 → 中间件 → 记录请求日志
         ↓
    FastAPI处理
         ↓
    业务逻辑 → 记录业务日志
         ↓
    慢SQL检测 → 记录慢SQL日志
         ↓
    响应 → 记录响应日志
```

## 日志存储

### 文件日志
- `logs/app.log` - 应用日志
- `logs/error.log` - 错误日志
- 自动轮转、压缩、保留7天

### 数据库日志
- `application_logs` 表
- 支持查询、过滤、统计
- 前端可通过API访问

## 使用方法

### 1. 启动后端服务
```bash
cd backend
uvicorn app.main:app --reload
```

### 2. 查看实时日志
```bash
tail -f logs/app.log
```

### 3. 查询日志API
```bash
# 获取日志列表
curl http://localhost:8000/api/logs/

# 按服务过滤
curl "http://localhost:8000/api/logs/?service=order-service"

# 按级别过滤
curl "http://localhost:8000/api/logs/?level=ERROR"

# 关键词搜索
curl "http://localhost:8000/api/logs/?keyword=Slow"

# 获取日志统计
curl http://localhost:8000/api/logs/stats/summary

# 获取服务列表
curl http://localhost:8000/api/logs/services/list
```

### 4. 测试慢SQL日志
```bash
# 启用慢SQL
curl -X POST "http://localhost:8000/api/orders/debug/enable-slow-sql?enabled=true"

# 查询订单（产生慢SQL日志）
curl http://localhost:8000/api/orders/user/1

# 查看WARN日志
curl "http://localhost:8000/api/logs/?level=WARN"

# 禁用慢SQL
curl -X POST "http://localhost:8000/api/orders/debug/enable-slow-sql?enabled=false"
```

## 项目结构更新

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py      # 更新
│   │   ├── logs.py          # 新增
│   │   └── orders.py        # 更新（集成日志）
│   ├── core/
│   │   ├── logging.py       # 新增
│   │   └── middleware.py    # 新增
│   ├── models/
│   │   ├── __init__.py      # 更新
│   │   └── application_log.py  # 新增
│   ├── schemas/
│   │   ├── __init__.py      # 更新
│   │   └── application_log.py  # 新增
│   ├── services/
│   │   ├── __init__.py      # 新增
│   │   └── log_service.py   # 新增
│   └── main.py              # 更新
├── logs/                    # 日志目录
│   ├── app.log             # 应用日志
│   └── error.log           # 错误日志
└── scripts/
    └── test_phase3.py       # 新增
```

## 关键技术点

### 1. Loguru日志库
- 比Python标准logging更强大
- 支持彩色输出
- 支持文件轮转、压缩
- 支持绑定上下文（service, trace_id）

### 2. 中间件模式
- Starlette BaseHTTPMiddleware
- 自动记录所有请求
- 生成唯一Trace ID
- 计算请求耗时

### 3. 日志级别
- INFO - 正常请求
- WARNING - 慢SQL、异常
- ERROR - 5xx错误、异常
- CRITICAL - 严重错误

### 4. 日志过滤
- SQLAlchemy查询
- 支持多条件组合
- 支持关键词搜索
- 支持时间范围

## 下一步：第四阶段

第四阶段目标：**搭建监控指标系统**

主要任务：
1. 实现指标采集（CPU、内存、请求量、延迟等）
2. 指标数据结构设计
3. 监控指标数据库表
4. 指标采集频率控制
5. 指标查询API

验收标准：
- CPU有数据
- Memory有数据
- API latency有数据
- HTTP error rate有数据
- DB latency有数据

---

**第三阶段完成！** 🎉

日志系统已搭建完毕，可以开始第四阶段的开发工作。

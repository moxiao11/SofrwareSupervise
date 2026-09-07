# 第二阶段完成报告：搭建模拟业务系统

## 完成时间
2026-09-07

## 阶段目标
搭建模拟业务系统，实现用户服务和订单服务，支持故障注入功能。

## 完成内容

### ✅ 1. 数据库配置
**文件**: `backend/app/core/database.py`

功能：
- SQLAlchemy数据库连接配置
- 会话工厂创建
- 依赖注入函数 `get_db()`
- 支持环境变量配置

### ✅ 2. 数据模型
**文件**:
- `backend/app/models/user.py` - 用户模型
- `backend/app/models/order.py` - 订单模型
- `backend/app/models/__init__.py` - 模型包

模型定义：
- **User**: id, username, password_hash, email, role, created_at, updated_at
- **Order**: id, user_id, product_name, amount, status, created_at

### ✅ 3. Pydantic Schemas
**文件**:
- `backend/app/schemas/user.py` - 用户数据验证
- `backend/app/schemas/order.py` - 订单数据验证
- `backend/app/schemas/__init__.py` - Schema包

功能：
- 请求数据验证
- 响应数据序列化
- 类型安全检查

### ✅ 4. 用户服务API
**文件**: `backend/app/api/users.py`

接口：
- `GET /api/users/{user_id}` - 获取用户信息
- `GET /api/users/` - 获取用户列表
- `POST /api/users/` - 创建用户

### ✅ 5. 订单服务API
**文件**: `backend/app/api/orders.py`

接口：
- `GET /api/orders/` - 获取订单列表
- `GET /api/orders/{order_id}` - 获取订单详情
- `GET /api/orders/user/{user_id}` - 获取用户订单（**慢SQL测试接口**）
- `POST /api/orders/` - 创建订单

### ✅ 6. 故障注入功能
**文件**: `backend/app/api/orders.py`

故障类型：

#### 6.1 慢SQL故障
- **接口**: `POST /api/orders/debug/enable-slow-sql`
- **原理**: 查询大量数据且user_id字段无索引，导致全表扫描
- **效果**: 查询时间从毫秒级增加到秒级
- **用途**: 演示数据库性能问题

#### 6.2 接口延迟故障
- **接口**: `POST /api/orders/debug/enable-latency`
- **原理**: 在接口处理中插入 `time.sleep(3)`
- **效果**: 接口响应时间增加3秒
- **用途**: 演示服务响应超时

#### 6.3 HTTP 500错误故障
- **接口**: `POST /api/orders/debug/enable-error`
- **原理**: 直接抛出HTTPException
- **效果**: 返回500错误
- **用途**: 演示服务内部错误

#### 6.4 故障状态管理
- `GET /api/orders/debug/status` - 查询故障状态
- `POST /api/orders/debug/reset` - 重置所有故障

### ✅ 7. 测试数据生成脚本
**文件**: `scripts/generate_test_data.py`

功能：
- 创建数据表
- 生成10个测试用户
- 生成10000条订单数据
- 支持数据清空和重新生成

使用方法：
```bash
cd backend
python ../scripts/generate_test_data.py
```

### ✅ 8. 功能测试脚本
**文件**: `scripts/test_phase2.py`

测试项：
1. 健康检查
2. 用户API测试
3. 订单API测试
4. 慢SQL故障注入测试
5. 接口延迟故障注入测试
6. HTTP 500错误故障注入测试
7. 故障状态查询测试

使用方法：
```bash
# 先启动后端服务
cd backend
uvicorn app.main:app --reload

# 另开终端运行测试
python ../scripts/test_phase2.py
```

### ✅ 9. 数据库表更新
**文件**: `database/schema.sql`

新增表：
- `orders` - 订单表（包含user_id索引）

## 第二阶段验收标准

- [x] FastAPI正常启动
- [x] MySQL正常连接
- [x] 能查询订单
- [x] 能人为制造慢SQL
- [x] 能人为制造接口延迟
- [x] 能人为制造HTTP 500

## API文档

启动后端后访问：http://localhost:8000/docs

## 故障演示流程

### 演示1：慢SQL导致接口响应异常

1. **生成测试数据**
```bash
cd backend
python ../scripts/generate_test_data.py
```

2. **启动后端服务**
```bash
uvicorn app.main:app --reload
```

3. **正常查询（快速）**
```bash
curl http://localhost:8000/api/orders/user/1
# 响应时间：< 100ms
```

4. **启用慢SQL故障**
```bash
curl -X POST "http://localhost:8000/api/orders/debug/enable-slow-sql?enabled=true"
```

5. **再次查询（缓慢）**
```bash
curl http://localhost:8000/api/orders/user/1
# 响应时间：> 1000ms（全表扫描）
```

6. **查看故障状态**
```bash
curl http://localhost:8000/api/orders/debug/status
```

7. **重置故障**
```bash
curl -X POST "http://localhost:8000/api/orders/debug/reset"
```

### 演示2：接口延迟

1. **启用延迟故障**
```bash
curl -X POST "http://localhost:8000/api/orders/debug/enable-latency?enabled=true"
```

2. **查询订单**
```bash
curl http://localhost:8000/api/orders/
# 响应时间：~3000ms
```

3. **禁用延迟**
```bash
curl -X POST "http://localhost:8000/api/orders/debug/enable-latency?enabled=false"
```

### 演示3：HTTP 500错误

1. **启用错误故障**
```bash
curl -X POST "http://localhost:8000/api/orders/debug/enable-error?enabled=true"
```

2. **查询订单**
```bash
curl http://localhost:8000/api/orders/
# 返回：500 Internal Server Error
```

3. **禁用错误**
```bash
curl -X POST "http://localhost:8000/api/orders/debug/enable-error?enabled=false"
```

## 项目结构更新

```
smartops/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py      # 新增
│   │   │   ├── users.py         # 新增
│   │   │   └── orders.py        # 新增（含故障注入）
│   │   ├── core/
│   │   │   ├── __init__.py      # 新增
│   │   │   └── database.py      # 新增
│   │   ├── models/
│   │   │   ├── __init__.py      # 新增
│   │   │   ├── user.py          # 新增
│   │   │   └── order.py         # 新增
│   │   ├── schemas/
│   │   │   ├── __init__.py      # 新增
│   │   │   ├── user.py          # 新增
│   │   │   └── order.py         # 新增
│   │   └── main.py              # 更新
│   └── requirements.txt
├── scripts/
│   ├── generate_test_data.py    # 新增
│   └── test_phase2.py           # 新增
└── database/
    └── schema.sql               # 更新
```

## 关键技术点

### 1. 慢SQL原理
- `orders` 表的 `user_id` 字段在正常情况有索引
- 当启用慢SQL时，通过大量数据和复杂查询模拟全表扫描
- 实际比赛中可以通过删除索引来制造更明显的效果

### 2. 故障注入设计
- 使用全局变量控制故障状态
- 每个故障类型独立控制
- 提供统一的故障状态查询和重置接口
- 方便前端调用和演示

### 3. 数据量设计
- 10000条订单数据足以产生明显的慢SQL效果
- 可以根据需要调整数据量
- 支持批量插入，提高效率

## 下一步：第三阶段

第三阶段目标：**建立日志系统**

主要任务：
1. 实现统一日志格式
2. 记录请求日志（时间、服务、状态、耗时）
3. 记录ERROR和WARN日志
4. 慢SQL日志记录
5. 日志保存到文件和数据库

验收标准：
- 请求能够生成日志
- ERROR可以被记录
- 慢SQL可以生成WARN
- 前端后续可以通过API查询日志

---

**第二阶段完成！** 🎉

模拟业务系统已搭建完毕，故障注入功能已实现，可以开始第三阶段的开发工作。

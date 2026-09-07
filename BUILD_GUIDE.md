# SmartOps 构建指南

本文档详细说明智维项目的构建、部署和开发环境配置。

---

## 目录

1. [环境要求](#环境要求)
2. [安装步骤](#安装步骤)
3. [数据库配置](#数据库配置)
4. [后端配置](#后端配置)
5. [前端配置](#前端配置)
6. [启动服务](#启动服务)
7. [常见问题](#常见问题)
8. [开发建议](#开发建议)

---

## 环境要求

### 操作系统
- Windows 11（推荐）
- Ubuntu 22.04
- macOS 12+

### 软件依赖

| 软件 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.11+ | 后端运行环境 |
| Node.js | 20+ | 前端构建工具 |
| MySQL | 8.x | 关系数据库 |
| Git | 2.x | 版本控制 |
| pip | 最新版 | Python包管理 |
| npm | 最新版 | Node包管理 |

---

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd smartops
```

### 2. 安装 MySQL

**Windows:**
- 下载 MySQL Installer: https://dev.mysql.com/downloads/installer/
- 安装时设置 root 密码（请记住）
- 确保 MySQL 服务已启动

**Ubuntu:**
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

### 3. 安装 Python 依赖

```bash
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 安装 Node.js 依赖

```bash
cd frontend

# 安装依赖
npm install
```

---

## 数据库配置

### 1. 创建数据库

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE smartops CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建用户（可选，生产环境推荐）
CREATE USER 'smartops'@'localhost' IDENTIFIED BY 'smartops_password';
GRANT ALL PRIVILEGES ON smartops.* TO 'smartops'@'localhost';
FLUSH PRIVILEGES;

# 退出
EXIT;
```

### 2. 导入表结构

```bash
mysql -u root -p smartops < database/schema.sql
```

### 3. 导入测试数据（可选）

```bash
mysql -u root -p smartops < database/seed.sql
```

### 4. 验证数据库

```bash
mysql -u root -p smartops

# 查看表
SHOW TABLES;

# 应该看到以下表：
# users
# services
# application_logs
# monitor_metrics
# alerts
# fault_events
# diagnosis_results
# knowledge_metadata
# llm_call_logs
```

---

## 后端配置

### 1. 配置环境变量

```bash
cd backend

# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件
# Windows: notepad .env
# Linux/Mac: nano .env
```

### 2. 必填配置项

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_NAME=smartops

# LLM配置（必须配置至少一个）
LLM_PROVIDER=qwen
LLM_API_KEY=你的API密钥
LLM_MODEL=qwen-plus
```

### 3. LLM API Key 获取

**Qwen（通义千问）:**
- 访问: https://dashscope.console.aliyun.com/
- 注册账号并创建API Key

**DeepSeek:**
- 访问: https://platform.deepseek.com/
- 注册账号并创建API Key

**GLM（智谱）:**
- 访问: https://open.bigmodel.cn/
- 注册账号并创建API Key

---

## 前端配置

### 1. 配置API地址

编辑 `frontend/.env.development`（如果不存在则创建）:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 2. 验证配置

确保后端API地址正确，前端将调用此地址获取数据。

---

## 启动服务

### 1. 启动后端

```bash
cd backend

# 确保虚拟环境已激活
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# 启动FastAPI服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问API文档: http://localhost:8000/docs

### 2. 启动前端

打开新终端：

```bash
cd frontend

# 启动开发服务器
npm run dev
```

访问前端界面: http://localhost:5173

### 3. 验证服务

1. 打开浏览器访问: http://localhost:5173
2. 应该看到登录页面
3. 使用演示账号登录:
   - 管理员: admin / admin123
   - 运维: ops / ops123
   - 开发: dev / dev123

---

## 常见问题

### Q1: 后端启动失败，提示数据库连接错误

**解决方案:**
1. 检查MySQL服务是否已启动
2. 检查 `.env` 文件中的数据库配置是否正确
3. 验证数据库是否存在: `mysql -u root -p -e "SHOW DATABASES;"`

### Q2: 前端无法访问后端API

**解决方案:**
1. 确认后端已启动: http://localhost:8000/docs
2. 检查 `frontend/.env.development` 中的 `VITE_API_BASE_URL`
3. 检查浏览器控制台是否有CORS错误
4. 确保防火墙未阻止8000端口

### Q3: LLM调用失败

**解决方案:**
1. 检查 `.env` 中的 `LLM_API_KEY` 是否正确
2. 验证API Key是否有足够余额
3. 检查网络连接是否可以访问LLM API
4. 查看 `logs/app.log` 获取详细错误信息

### Q4: Python依赖安装失败

**解决方案:**
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q5: Node.js依赖安装失败

**解决方案:**
```bash
# 清除缓存
npm cache clean --force

# 使用国内镜像
npm install --registry=https://registry.npmmirror.com
```

---

## 开发建议

### 后端开发

1. **代码结构**
   - API路由放在 `app/api/`
   - 业务逻辑放在 `app/services/`
   - 数据模型放在 `app/models/`

2. **数据库操作**
   - 使用SQLAlchemy ORM
   - 避免直接写SQL语句
   - 使用Pydantic进行数据验证

3. **Agent开发**
   - Agent逻辑放在 `app/agents/`
   - Prompt模板放在 `app/prompts/`
   - 使用LangGraph构建工作流

### 前端开发

1. **组件开发**
   - 页面组件放在 `src/views/`
   - 通用组件放在 `src/components/`
   - 使用Element Plus组件库

2. **状态管理**
   - 使用Pinia管理全局状态
   - API调用封装在 `src/api/`

3. **路由配置**
   - 路由配置在 `src/router/`
   - 权限控制使用路由守卫

### 测试

1. **后端测试**
```bash
cd backend
pytest tests/
```

2. **前端测试**
```bash
cd frontend
npm run test
```

---

## 部署建议

### 开发环境
- 使用 `uvicorn --reload` 自动重载
- 前端使用 `npm run dev` 开发模式

### 生产环境

**后端:**
```bash
# 使用gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

**前端:**
```bash
# 构建生产版本
npm run build

# 部署dist目录到Nginx
```

---

## 支持

如遇问题，请：
1. 查看 `logs/app.log` 获取详细日志
2. 检查本文档的常见问题部分
3. 联系开发团队

---

## 更新日志

### 2026-09-07
- 初始版本
- 完成项目骨架搭建
- 建立构建文档

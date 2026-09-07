# 智维 —— 软件系统故障诊断与根因分析智能体

**SmartOps: Intelligent Agent for Software Fault Diagnosis and Root Cause Analysis**

2026 年华北五省（市、自治区）及港澳台大学生计算机应用大赛  
大模型与智能体应用赛道

---

## 项目简介

智维是一个基于大语言模型（LLM）、智能体（Agent）、检索增强生成（RAG）和故障知识图谱的智能软件运维系统。

系统能够自动完成：
- **故障发现** → 实时监控系统运行指标
- **信息收集** → 自动采集日志、数据库状态、调用链
- **异常分析** → 多Agent协同分析不同维度数据
- **根因定位** → 智能推理故障根本原因
- **证据链生成** → 提供可解释的故障推理过程
- **修复建议** → 自动生成解决方案和运维命令

---

## 核心功能

### 多智能体协同诊断
- **日志分析 Agent** - 分析应用日志，识别异常模式
- **监控分析 Agent** - 分析系统指标（CPU、内存、网络等）
- **数据库 Agent** - 检测慢SQL、分析执行计划、索引建议
- **知识库 Agent** - RAG检索历史故障案例和运维知识
- **根因分析 Agent** - 综合多源信息，推理故障根因
- **修复建议 Agent** - 生成可执行的修复方案

### 可视化平台
- 系统健康度仪表盘
- 服务拓扑图
- 实时日志中心
- 告警中心
- AI故障诊断界面
- 故障证据链展示

---

## 技术栈

### 前端
- Vue 3 + Vite
- Element Plus
- ECharts
- Axios
- Vue Router
- Pinia

### 后端
- Python 3.11
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

### 数据库
- MySQL 8.x（关系数据）
- Chroma（向量数据库）

### AI Agent
- LangGraph
- LangChain

### 大语言模型
- Qwen / DeepSeek / GLM（可配置）

---

## 运行环境要求

- **操作系统**：Windows 11 / Ubuntu 22.04
- **Python**：3.11+
- **Node.js**：20+
- **MySQL**：8.x
- **Git**：2.x

---

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd smartops
```

### 2. 数据库初始化

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE smartops CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 导入表结构
mysql -u root -p smartops < database/schema.sql

# 导入测试数据（可选）
mysql -u root -p smartops < database/seed.sql
```

### 3. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入数据库连接信息和LLM API Key

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问后端API文档：http://localhost:8000/docs

### 4. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问前端界面：http://localhost:5173

### 5. 演示账号

- 管理员：admin / admin123
- 运维人员：ops / ops123
- 开发人员：dev / dev123

---

## 项目结构

```
smartops/
├── frontend/                 # Vue前端
├── backend/                  # FastAPI后端
│   └── app/
│       ├── api/             # API路由
│       ├── core/            # 核心配置
│       ├── models/          # 数据模型
│       ├── schemas/         # Pydantic模型
│       ├── services/        # 业务逻辑
│       ├── agents/          # AI Agent
│       ├── rag/             # RAG知识库
│       ├── monitoring/      # 监控模块
│       └── prompts/         # Prompt模板
├── mock-system/             # 模拟故障业务系统
├── knowledge-base/          # RAG原始知识库
│   ├── mysql/
│   ├── linux/
│   ├── nginx/
│   ├── network/
│   └── cases/
├── database/                # 数据库脚本
│   ├── schema.sql
│   ├── seed.sql
│   └── backup/
├── scripts/                 # 初始化脚本
├── docs/                    # 文档
│   ├── architecture/        # 架构文档
│   ├── screenshots/         # 系统截图
│   ├── test/                # 测试文档
│   ├── demo/                # 演示案例
│   └── api/                 # API文档
├── logs/                    # 日志文件
├── docker/                  # Docker配置
├── README.md
├── BUILD_GUIDE.md
└── .gitignore
```

---

## 演示案例

系统预设三个典型故障案例：

### 案例一：慢SQL导致接口响应异常
- 订单查询页面响应缓慢
- 根因：orders表user_id字段缺少索引
- 修复：CREATE INDEX idx_orders_user_id ON orders(user_id)

### 案例二：HTTP 500错误
- 接口错误率上升
- 根因：应用代码异常
- 修复：代码修复

### 案例三：CPU高负载
- CPU使用率超过90%
- 根因：某服务计算任务异常
- 修复：优化算法或扩容

---

## 开发团队

2026年华北五省大学生计算机应用大赛参赛作品

---

## 许可证

本项目仅供比赛和学术研究使用

---

## 联系方式

如有问题，请联系开发团队

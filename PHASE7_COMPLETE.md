# Phase 7 完成报告：接入大语言模型

## 完成时间
2026-09-07

## 阶段目标
封装大语言模型调用，支持 Qwen/DeepSeek/GLM，为后续的 AI Agent 提供基础的 LLM 调用能力。

## 完成内容

### 1. LLMService 服务层
**文件**: `backend/app/services/llm_service.py`

创建了统一的 LLM 调用服务，包含：

#### 1.1 简单对话接口 `chat()`
- 支持系统提示词（system_prompt）
- 支持温度参数控制（temperature）
- 支持最大 token 数限制（max_tokens）
- 自动处理 API 调用异常

#### 1.2 结构化输出接口 `structured_output()`
- 强制模型返回 JSON 格式
- 支持 JSON Schema 定义期望结构
- 自动提取和解析 JSON（处理 markdown 代码块包裹）
- 返回解析后的字典对象

#### 1.3 配置管理
- 从 `.env` 文件读取配置
- 支持多提供商（Qwen/DeepSeek/GLM）
- API Key 脱敏显示
- 全局单例模式

### 2. LLM API 接口
**文件**: `backend/app/api/llm.py`

提供了 4 个测试接口：

| 接口 | 方法 | 功能 |
|------|------|------|
| `/api/llm/config` | GET | 获取 LLM 配置信息 |
| `/api/llm/chat` | POST | 简单对话 |
| `/api/llm/structured` | POST | 结构化输出 |
| `/api/llm/test` | GET | 连接测试 |

### 3. 配置文件
**文件**: `backend/.env`

```env
LLM_PROVIDER=qwen
LLM_API_KEY=sk-ws-H.EDYLEMI.PWOX.MEYCIQCfXfqHQds0G1_rqXy1TV_HIuZ5Pl5Fv_hWWpLXyopxsgIhAIEs3Mv8mkCB_nq8H1pNXPyN6e9jMEoD0IRRrL--uCvT
LLM_MODEL=qwen-plus
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 4. 测试脚本
**文件**: `scripts/test_llm.py`

自动化测试：
- ✓ 配置获取
- ✓ 简单对话
- ✓ 结构化输出

## 测试结果

```
============================================================
LLM 大语言模型测试
============================================================

[1] 获取 LLM 配置...
✓ 提供商: qwen
✓ 模型: qwen-plus
✓ API Key: sk-ws-H.ED***

[2] 测试简单对话...
✓ 模型回复: 你好！我是通义千问（Qwen），阿里巴巴集团旗下的超大规模语言模型...

[3] 测试结构化输出...
✓ 结构化输出成功:
  - 时间: 2026-09-07 10:05:25
  - 级别: ERROR
  - 服务: order-service
  - 错误: Database connection timeout
  - 严重程度: high

============================================================
✅ LLM 测试完成！
============================================================
```

## 使用方法

### 1. 测试连接
```bash
curl http://localhost:8000/api/llm/test
```

### 2. 简单对话
```bash
curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，请介绍一下自己"}'
```

### 3. 结构化输出（日志分析示例）
```bash
curl -X POST http://localhost:8000/api/llm/structured \
  -H "Content-Type: application/json" \
  -d '{
    "message": "分析这条日志：2026-09-07 10:05:25 ERROR order-service Database connection timeout",
    "schema": {
      "type": "object",
      "properties": {
        "timestamp": {"type": "string"},
        "level": {"type": "string"},
        "service": {"type": "string"},
        "error_type": {"type": "string"},
        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
      }
    }
  }'
```

### 4. 运行测试脚本
```bash
cd smartops
python scripts/test_llm.py
```

## 架构设计

```
┌─────────────────────────────────────┐
│      前端 / API 调用方              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      /api/llm/* 接口               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      LLMService (llm_service.py)   │
│  - chat()                           │
│  - structured_output()              │
│  - get_config()                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      OpenAI Compatible API         │
│  - Qwen (通义千问)                  │
│  - DeepSeek                         │
│  - GLM (智谱)                       │
└─────────────────────────────────────┘
```

## 关键设计

### 1. 提供商无关
使用 OpenAI 兼容接口，所有提供商（Qwen/DeepSeek/GLM）都支持 OpenAI API 格式，只需修改 `base_url` 即可切换。

### 2. 结构化输出
通过 prompt engineering 强制模型返回 JSON，自动处理 markdown 代码块，返回解析后的字典。

### 3. 错误处理
- API Key 未配置 → 返回错误提示
- API 调用失败 → 捕获异常并记录日志
- JSON 解析失败 → 返回原始文本供调试

### 4. 日志记录
每次 LLM 调用都会记录日志，便于追踪和调试。

## 下一步

Phase 7 为后续阶段奠定了基础：
- **Phase 8**: 日志分析 Agent - 使用 LLM 分析日志
- **Phase 9**: 数据库 Agent - 使用 LLM 分析数据库问题
- **Phase 12**: 根因分析 Agent - 使用 LLM 进行推理
- **Phase 13**: 修复建议 Agent - 使用 LLM 生成建议

## 文件清单

### 新增文件
- `backend/app/services/llm_service.py` - LLM 服务
- `backend/app/api/llm.py` - LLM API
- `scripts/test_llm.py` - 测试脚本

### 修改文件
- `backend/app/services/__init__.py` - 导出 LLMService
- `backend/app/api/__init__.py` - 注册 LLM 路由
- `backend/.env` - 添加 LLM 配置

## 验收标准

- [x] LLM 配置正确读取
- [x] 简单对话接口正常
- [x] 结构化输出接口正常
- [x] 错误处理完善
- [x] 日志记录完整
- [x] 测试脚本通过

---

**Phase 7 完成！** ✅

大语言模型已成功接入，下一步可以开始构建 AI Agent。

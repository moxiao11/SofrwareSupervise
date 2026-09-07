"""
LLM API
大语言模型测试 API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.services.llm_service import llm_service

router = APIRouter(prefix="/api/llm", tags=["大语言模型"])


class ChatRequest(BaseModel):
    """对话请求"""
    message: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7


class StructuredRequest(BaseModel):
    """结构化输出请求"""
    message: str
    schema: Dict[str, Any]
    system_prompt: Optional[str] = None


@router.get("/config")
async def get_llm_config():
    """获取 LLM 配置信息"""
    return llm_service.get_config()


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    简单对话接口

    示例：
    ```
    curl -X POST http://localhost:8000/api/llm/chat \
      -H "Content-Type: application/json" \
      -d '{"message": "你好，请介绍一下自己"}'
    ```
    """
    result = llm_service.chat(
        user_message=request.message,
        system_prompt=request.system_prompt,
        temperature=request.temperature
    )
    return {"response": result}


@router.post("/structured")
async def structured_output(request: StructuredRequest):
    """
    结构化输出接口 - 强制返回 JSON

    示例：
    ```
    curl -X POST http://localhost:8000/api/llm/structured \
      -H "Content-Type: application/json" \
      -d '{
        "message": "分析一下这条日志：2026-09-07 ERROR order-service Database connection timeout",
        "schema": {
          "type": "object",
          "properties": {
            "timestamp": {"type": "string"},
            "level": {"type": "string"},
            "service": {"type": "string"},
            "error_type": {"type": "string"},
            "severity": {"type": "string"}
          }
        }
      }'
    ```
    """
    result = llm_service.structured_output(
        user_message=request.message,
        expected_schema=request.schema,
        system_prompt=request.system_prompt
    )
    return result


@router.get("/test")
async def test_llm():
    """
    测试 LLM 连接

    返回示例响应，验证 API Key 是否有效
    """
    test_response = llm_service.chat(
        user_message="请用一句话介绍你自己",
        temperature=0.5
    )
    return {
        "status": "success" if "错误" not in test_response else "error",
        "config": llm_service.get_config(),
        "test_response": test_response
    }

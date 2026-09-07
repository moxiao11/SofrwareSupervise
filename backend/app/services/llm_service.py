"""
LLM Service
大语言模型服务 - 封装所有 LLM 调用
支持：Qwen（通义千问）/ DeepSeek / GLM（智谱）
"""
import os
import json
from typing import Optional, Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

from app.core.logging import get_logger

load_dotenv()

logger = get_logger(service="llm-service")


class LLMService:
    """大语言模型服务"""

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "qwen")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "qwen-plus")
        self.base_url = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

        if not self.api_key:
            logger.warning("LLM_API_KEY not configured")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logger.info(f"LLM Service initialized: provider={self.provider}, model={self.model}")

    def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        简单的对话接口

        Args:
            user_message: 用户消息
            system_prompt: 系统提示词（可选）
            temperature: 温度参数（0-1，越高越随机）
            max_tokens: 最大返回 token 数

        Returns:
            模型回复文本
        """
        if not self.client:
            return "错误：LLM_API_KEY 未配置"

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            result = response.choices[0].message.content
            logger.info(f"LLM chat success: {len(result)} chars")
            return result

        except Exception as e:
            logger.error(f"LLM chat failed: {str(e)}")
            return f"错误：{str(e)}"

    def structured_output(
        self,
        user_message: str,
        expected_schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        结构化输出接口 - 强制模型返回 JSON 格式

        Args:
            user_message: 用户消息
            expected_schema: 期望的 JSON Schema 描述
            system_prompt: 系统提示词（可选）
            temperature: 温度参数（较低以保证格式稳定）

        Returns:
            解析后的 JSON 字典
        """
        if not self.client:
            return {"error": "LLM_API_KEY 未配置"}

        try:
            # 构建提示词，要求返回 JSON
            json_instruction = f"""
请严格按照以下 JSON Schema 返回结果：
{json.dumps(expected_schema, ensure_ascii=False, indent=2)}

只返回 JSON，不要包含其他说明文字。
"""

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt + "\n" + json_instruction})
            else:
                messages.append({"role": "system", "content": json_instruction})
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )

            result_text = response.choices[0].message.content

            # 提取 JSON（可能被 markdown 代码块包裹）
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)
            logger.info(f"LLM structured output success: {list(result.keys())}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed: {str(e)}, raw: {result_text[:200]}")
            return {"error": "JSON 解析失败", "raw": result_text[:500]}
        except Exception as e:
            logger.error(f"LLM structured output failed: {str(e)}")
            return {"error": str(e)}

    def get_config(self) -> Dict[str, str]:
        """获取当前 LLM 配置信息"""
        return {
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "api_key_configured": bool(self.api_key),
            "api_key_masked": self.api_key[:10] + "***" if self.api_key else "未配置"
        }


# 全局单例
llm_service = LLMService()

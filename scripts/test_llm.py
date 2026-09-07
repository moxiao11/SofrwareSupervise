#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM 测试脚本
验证大语言模型连接是否正常
"""
import requests
import json
import sys

# 设置标准输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("LLM 大语言模型测试")
print("=" * 60)

# 测试 1：获取配置
print("\n[1] 获取 LLM 配置...")
try:
    response = requests.get(f"{BASE_URL}/api/llm/config")
    config = response.json()
    print(f"✓ 提供商: {config['provider']}")
    print(f"✓ 模型: {config['model']}")
    print(f"✓ API Key: {config['api_key_masked']}")
except Exception as e:
    print(f"✗ 获取配置失败: {e}")
    sys.exit(1)

# 测试 2：简单对话
print("\n[2] 测试简单对话...")
try:
    response = requests.post(
        f"{BASE_URL}/api/llm/chat",
        json={"message": "你好，请用一句话介绍你自己"},
        timeout=30
    )
    data = response.json()
    if 'response' in data:
        print(f"✓ 模型回复: {data['response'][:100]}...")
    else:
        print(f"✗ 回复错误: {data.get('error', 'Unknown')}")
except Exception as e:
    print(f"✗ 对话失败: {e}")

# 测试 3：结构化输出
print("\n[3] 测试结构化输出...")
try:
    response = requests.post(
        f"{BASE_URL}/api/llm/structured",
        json={
            "message": "分析这条日志：2026-09-07 10:05:25 ERROR order-service Database connection timeout",
            "schema": {
                "type": "object",
                "properties": {
                    "timestamp": {"type": "string", "description": "时间戳"},
                    "level": {"type": "string", "description": "日志级别"},
                    "service": {"type": "string", "description": "服务名称"},
                    "error_type": {"type": "string", "description": "错误类型"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
                },
                "required": ["timestamp", "level", "service", "error_type", "severity"]
            }
        },
        timeout=30
    )
    data = response.json()
    if 'error' not in data:
        print(f"✓ 结构化输出成功:")
        print(f"  - 时间: {data.get('timestamp')}")
        print(f"  - 级别: {data.get('level')}")
        print(f"  - 服务: {data.get('service')}")
        print(f"  - 错误: {data.get('error_type')}")
        print(f"  - 严重程度: {data.get('severity')}")
    else:
        print(f"✗ 结构化输出失败: {data.get('error')}")
except Exception as e:
    print(f"✗ 请求失败: {e}")

print("\n" + "=" * 60)
print("✅ LLM 测试完成！")
print("=" * 60)

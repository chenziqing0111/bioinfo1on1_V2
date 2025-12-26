import json
import re
import asyncio
from typing import Dict, Any, Optional

import httpx

from app.core.config import settings


class AIClient:
    """AI 客户端封装"""

    def __init__(self):
        self.deepseek_api_key = settings.DEEPSEEK_API_KEY
        self.deepseek_base_url = settings.DEEPSEEK_BASE_URL
        self.claude_api_key = settings.CLAUDE_API_KEY
        self.timeout = settings.AI_TIMEOUT_SECONDS

    async def chat(
        self,
        messages: list[Dict[str, str]],
        model: str = "deepseek-chat",
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        调用 AI 模型
        支持 DeepSeek 和 Claude
        """
        if timeout is None:
            timeout = self.timeout

        if model.startswith("deepseek"):
            return await self._deepseek_chat(messages, model, timeout)
        elif model.startswith("claude"):
            return await self._claude_chat(messages, model, timeout)
        else:
            raise ValueError(f"不支持的模型: {model}")

    async def _deepseek_chat(
        self,
        messages: list[Dict[str, str]],
        model: str,
        timeout: int
    ) -> Dict[str, Any]:
        """调用 DeepSeek API"""
        url = f"{self.deepseek_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4000
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return {
            "content": data["choices"][0]["message"]["content"],
            "model": data["model"],
            "usage": {
                "input_tokens": data["usage"]["prompt_tokens"],
                "output_tokens": data["usage"]["completion_tokens"]
            }
        }

    async def _claude_chat(
        self,
        messages: list[Dict[str, str]],
        model: str,
        timeout: int
    ) -> Dict[str, Any]:
        """调用 Claude API"""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.claude_api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        # Claude API 格式转换
        system_message = None
        claude_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append(msg)

        payload = {
            "model": model,
            "messages": claude_messages,
            "max_tokens": 4000,
            "temperature": 0.7
        }
        if system_message:
            payload["system"] = system_message

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return {
            "content": data["content"][0]["text"],
            "model": data["model"],
            "usage": {
                "input_tokens": data["usage"]["input_tokens"],
                "output_tokens": data["usage"]["output_tokens"]
            }
        }


def parse_ai_response(content: str) -> Dict[str, Any]:
    """
    解析 AI 返回的 JSON，带清洗逻辑
    """
    # 移除可能的 markdown 代码块标记
    content = re.sub(r'^```json\s*', '', content.strip())
    content = re.sub(r'\s*```$', '', content.strip())

    # 尝试直接解析
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # 尝试提取 JSON 部分
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        raise ValueError(f"无法解析 AI 响应: {content[:200]}")


# 全局 AI 客户端
ai_client = AIClient()

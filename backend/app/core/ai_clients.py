"""
AI Agent Floating Ball - AI Service Clients
AI服务客户端，集成Moonshot、DashScope、秘塔等服务
"""

import json
import time
from typing import Dict, List, Any, Optional
from openai import OpenAI
import requests

from .config import get_config


class MoonshotClient:
    """Moonshot Kimi API客户端"""

    def __init__(self):
        config = get_config()
        moonshot_config = config.ai.moonshot

        self.client = OpenAI(
            api_key=moonshot_config.api_key,
            base_url=moonshot_config.base_url
        )
        self.model = moonshot_config.model
        self.temperature = moonshot_config.temperature
        self.max_tokens = moonshot_config.max_tokens

    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """调用Moonshot聊天完成API"""
        try:
            # 设置参数
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            stream = kwargs.get('stream', False)

            # 调用API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )

            if stream:
                # 处理流式响应
                return {"content": "流式响应暂未实现", "model": self.model}
            else:
                # 处理普通响应
                content = response.choices[0].message.content
                usage = response.usage.model_dump() if response.usage else None

                return {
                    "content": content,
                    "model": self.model,
                    "usage": usage
                }

        except Exception as e:
            raise Exception(f"Moonshot API调用失败: {str(e)}")


class DashScopeClient:
    """DashScope API客户端"""

    def __init__(self):
        config = get_config()
        dashscope_config = config.ai.dashscope

        self.client = OpenAI(
            api_key=dashscope_config.api_key,
            base_url=dashscope_config.base_url
        )
        self.tts_model = dashscope_config.tts_model
        self.asr_model = dashscope_config.asr_model

    async def text_to_speech(self, text: str, voice: str = "zhichu") -> bytes:
        """文本转语音"""
        try:
            # 调用DashScope TTS API
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice,
                input=text
            )
            return response.content

        except Exception as e:
            raise Exception(f"DashScope TTS调用失败: {str(e)}")

    async def speech_to_text(self, audio_data: bytes, language: str = "zh-CN") -> str:
        """语音转文本"""
        try:
            # 这里应该调用DashScope ASR API
            # 暂时返回模拟数据
            return "这是模拟的语音识别结果"

        except Exception as e:
            raise Exception(f"DashScope ASR调用失败: {str(e)}")


class MetasoClient:
    """秘塔搜索API客户端"""

    def __init__(self):
        config = get_config()
        metaso_config = config.ai.metaso

        self.api_key = metaso_config.api_key
        self.base_url = metaso_config.base_url

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """执行搜索"""
        try:
            url = f"{self.base_url}/api/v1/search"

            payload = json.dumps({
                "q": query,
                "scope": kwargs.get("scope", "webpage"),
                "includeSummary": kwargs.get("include_summary", True),
                "size": kwargs.get("size", 20),
                "includeRawContent": kwargs.get("include_raw", False),
                "conciseSnippet": kwargs.get("concise", False)
            })

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            raise Exception(f"秘塔搜索API调用失败: {str(e)}")


class AIClientManager:
    """AI客户端管理器"""

    def __init__(self):
        self.moonshot = MoonshotClient()
        self.dashscope = DashScopeClient()
        self.metas = MetasoClient()

    async def chat_completion(self, messages: List[Dict], provider: str = "moonshot", **kwargs) -> Dict[str, Any]:
        """统一的聊天完成接口"""
        if provider == "moonshot":
            return await self.moonshot.chat_completion(messages, **kwargs)
        elif provider == "dashscope":
            # DashScope也可以做聊天，但这里主要用Moonshot
            return await self.moonshot.chat_completion(messages, **kwargs)
        else:
            raise ValueError(f"不支持的AI提供商: {provider}")

    async def text_to_speech(self, text: str, provider: str = "dashscope", **kwargs) -> bytes:
        """统一的文本转语音接口"""
        if provider == "dashscope":
            return await self.dashscope.text_to_speech(text, **kwargs)
        else:
            raise ValueError(f"不支持的TTS提供商: {provider}")

    async def speech_to_text(self, audio_data: bytes, provider: str = "dashscope", **kwargs) -> str:
        """统一的语音转文本接口"""
        if provider == "dashscope":
            return await self.dashscope.speech_to_text(audio_data, **kwargs)
        else:
            raise ValueError(f"不支持的ASR提供商: {provider}")

    async def search(self, query: str, provider: str = "metaso", **kwargs) -> Dict[str, Any]:
        """统一的搜索接口"""
        if provider == "metaso":
            return await self.metas.search(query, **kwargs)
        else:
            raise ValueError(f"不支持的搜索提供商: {provider}")


# 全局AI客户端实例
_ai_client: Optional[AIClientManager] = None


def get_ai_client() -> AIClientManager:
    """获取全局AI客户端实例"""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClientManager()
    return _ai_client


# 兼容性函数 - 用于兼容原有代码
async def chat_completion(messages: List[Dict], **kwargs) -> Dict[str, Any]:
    """兼容性函数：聊天完成"""
    client = get_ai_client()
    return await client.chat_completion(messages, **kwargs)


async def text_to_speech(text: str, **kwargs) -> bytes:
    """兼容性函数：文本转语音"""
    client = get_ai_client()
    return await client.text_to_speech(text, **kwargs)


async def speech_to_text(audio_data: bytes, **kwargs) -> str:
    """兼容性函数：语音转文本"""
    client = get_ai_client()
    return await client.speech_to_text(audio_data, **kwargs)


async def search(query: str, **kwargs) -> Dict[str, Any]:
    """兼容性函数：搜索"""
    client = get_ai_client()
    return await client.search(query, **kwargs)

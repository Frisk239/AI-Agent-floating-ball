"""
AI Agent Floating Ball - Chat API
聊天功能API路由
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import time
from pathlib import Path

from ..core.config import get_config
from ..core.ai_clients import get_ai_client


router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[float] = None


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    message: ChatMessage
    usage: Optional[Dict[str, Any]] = None
    model: str


@router.post("/send", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    发送聊天消息

    - **messages**: 消息列表
    - **model**: 使用的模型 (可选，默认使用Moonshot)
    - **temperature**: 温度参数 (可选)
    - **max_tokens**: 最大token数 (可选)
    - **stream**: 是否流式输出 (可选)
    """
    try:
        config = get_config()
        ai_client = get_ai_client()

        # 转换消息格式
        messages = []
        for msg in request.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # 设置参数
        model = request.model or config.ai.moonshot.model
        temperature = request.temperature or config.ai.moonshot.temperature
        max_tokens = request.max_tokens or config.ai.moonshot.max_tokens

        # 调用AI客户端
        response = await ai_client.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=request.stream
        )

        # 构造响应
        chat_response = ChatResponse(
            message=ChatMessage(
                role="assistant",
                content=response.get("content", ""),
                timestamp=time.time()
            ),
            usage=response.get("usage"),
            model=response.get("model", model)
        )

        # 后台保存聊天记录
        background_tasks.add_task(save_chat_history, request.messages, chat_response)

        return chat_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天请求失败: {str(e)}")


@router.get("/models")
async def get_available_models():
    """获取可用的AI模型列表"""
    config = get_config()

    models = {
        "moonshot": {
            "name": "Moonshot Kimi k2",
            "model": config.ai.moonshot.model,
            "description": "月之暗面Kimi大语言模型"
        },
        "dashscope": {
            "name": "DashScope",
            "model": "qwen-plus",
            "description": "阿里云DashScope模型"
        }
    }

    return {"models": models}


@router.get("/history")
async def get_chat_history(limit: int = 50, offset: int = 0):
    """获取聊天历史记录"""
    try:
        config = get_config()
        history_file = Path(config.data.output_file)

        if not history_file.exists():
            return {"history": [], "total": 0}

        with open(history_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {"history": [], "total": 0}

            data = json.loads(content)
            # 这里可以扩展为返回历史记录列表
            return {"history": [data], "total": 1}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


async def save_chat_history(request_messages: List[ChatMessage], response: ChatResponse):
    """保存聊天历史记录"""
    try:
        config = get_config()
        output_file = Path(config.data.output_file)

        # 确保目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 构造历史记录数据
        history_data = {
            "request_id": f"chat_{int(time.time())}",
            "timestamp": time.time(),
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in request_messages
            ] + [
                {"role": response.message.role, "content": response.message.content}
            ],
            "model": response.model,
            "usage": response.usage
        }

        # 保存到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"保存聊天历史失败: {e}")


@router.delete("/history")
async def clear_chat_history():
    """清空聊天历史记录"""
    try:
        config = get_config()
        output_file = Path(config.data.output_file)

        if output_file.exists():
            # 清空文件内容
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("")

        return {"message": "聊天历史已清空"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空历史记录失败: {str(e)}")

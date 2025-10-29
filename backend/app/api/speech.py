"""
AI Agent Floating Ball - Speech API
语音功能API路由
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import base64
import io

from ..core.config import get_config


router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "zhichu"  # zhichu, zhimiao, etc.
    speed: Optional[float] = 1.0
    volume: Optional[float] = 1.0


class TTSResponse(BaseModel):
    audio_base64: str
    format: str = "wav"
    duration: Optional[float] = None


class ASRRequest(BaseModel):
    audio_base64: str
    format: Optional[str] = "wav"
    language: Optional[str] = "zh-CN"


class ASRResponse(BaseModel):
    text: str
    confidence: Optional[float] = None
    language: Optional[str] = None


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    文本转语音

    - **text**: 要转换的文本
    - **voice**: 语音类型 (可选)
    - **speed**: 语速 (可选，0.5-2.0)
    - **volume**: 音量 (可选，0.0-1.0)
    """
    try:
        config = get_config()

        # 这里应该调用DashScope TTS服务
        # 暂时返回模拟响应
        audio_base64 = base64.b64encode(b"mock_audio_data").decode()

        return TTSResponse(
            audio_base64=audio_base64,
            format="wav",
            duration=len(request.text) * 0.1  # 估算时长
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS转换失败: {str(e)}")


@router.post("/asr", response_model=ASRResponse)
async def speech_to_text(request: ASRRequest):
    """
    语音转文本

    - **audio_base64**: base64编码的音频数据
    - **format**: 音频格式 (wav, mp3, etc.)
    - **language**: 语言代码 (zh-CN, en-US, etc.)
    """
    try:
        config = get_config()

        # 解码音频数据
        try:
            audio_data = base64.b64decode(request.audio_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"无效的base64音频数据: {str(e)}")

        # 这里应该调用DashScope ASR服务
        # 暂时返回模拟响应
        mock_text = "这是模拟的语音识别结果"

        return ASRResponse(
            text=mock_text,
            confidence=0.95,
            language=request.language or "zh-CN"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ASR转换失败: {str(e)}")


@router.post("/asr/upload", response_model=ASRResponse)
async def speech_to_text_upload(
    file: UploadFile = File(...),
    language: Optional[str] = "zh-CN"
):
    """
    上传音频文件进行语音识别

    - **file**: 音频文件 (wav, mp3, m4a等格式)
    - **language**: 语言代码 (可选)
    """
    try:
        # 验证文件类型
        allowed_formats = ["audio/wav", "audio/mpeg", "audio/mp4", "audio/x-m4a"]
        if file.content_type not in allowed_formats:
            raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file.content_type}")

        # 读取文件内容
        audio_data = await file.read()

        # 转换为base64
        audio_base64 = base64.b64encode(audio_data).decode()

        # 调用ASR服务
        asr_request = ASRRequest(
            audio_base64=audio_base64,
            format=file.content_type,
            language=language
        )

        return await speech_to_text(asr_request)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件ASR处理失败: {str(e)}")


@router.get("/voices")
async def get_available_voices():
    """获取可用的语音列表"""
    voices = {
        "zhichu": {
            "name": "智楚",
            "gender": "male",
            "language": "zh-CN",
            "description": "温暖男声"
        },
        "zhimiao": {
            "name": "智妙",
            "gender": "female",
            "language": "zh-CN",
            "description": "甜美女声"
        },
        "zhiyan": {
            "name": "智彦",
            "gender": "male",
            "language": "zh-CN",
            "description": "专业男声"
        }
    }

    return {"voices": voices}


@router.get("/status")
async def get_speech_status():
    """获取语音服务状态"""
    config = get_config()

    return {
        "tts_enabled": bool(config.ai.dashscope.api_key),
        "asr_enabled": bool(config.ai.dashscope.api_key),
        "wake_word": config.speech.wake_word,
        "sample_rate": config.speech.sample_rate
    }

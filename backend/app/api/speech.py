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


class WakeWordRequest(BaseModel):
    action: str  # "start", "stop", "status"


class WakeWordResponse(BaseModel):
    success: bool
    message: str
    status: Optional[dict] = None


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
        from ..services.speech.tts_service import realtime_tts_speak

        config = get_config()

        # 转换语音参数格式
        voice = "female" if request.voice == "zhimiao" else "male"

        # 调用实际的TTS服务
        # 注意：realtime_tts_speak是同步函数，需要在线程池中运行
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def tts_sync():
            realtime_tts_speak(request.text, voice=voice)

        # 在线程池中运行TTS
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, tts_sync)

        # 返回响应（实际音频已播放）
        return TTSResponse(
            audio_base64="",  # 实时播放，不返回文件
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
        from ..services.speech.asr_service import process_audio_file_asr
        import tempfile
        import os

        config = get_config()

        # 解码音频数据
        try:
            audio_data = base64.b64decode(request.audio_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"无效的base64音频数据: {str(e)}")

        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name

        try:
            # 调用ASR服务
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            def asr_sync():
                return process_audio_file_asr(temp_file_path)

            # 在线程池中运行ASR
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(executor, asr_sync)

            if result:
                return ASRResponse(
                    text=result,
                    confidence=0.95,
                    language=request.language or "zh-CN"
                )
            else:
                # 如果ASR失败，返回模拟响应
                return ASRResponse(
                    text="语音识别失败，请重试",
                    confidence=0.0,
                    language=request.language or "zh-CN"
                )

        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file_path)
            except:
                pass

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


@router.post("/wake-word", response_model=WakeWordResponse)
async def control_wake_word(request: WakeWordRequest):
    """
    控制语音唤醒功能

    - **action**: 操作类型 ("start", "stop", "status")
    """
    try:
        from ..services.speech.voice_wake_service import (
            start_voice_wake, stop_voice_wake, get_wake_status
        )

        config = get_config()

        if request.action == "start":
            # 启动语音唤醒
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            def start_sync():
                return start_voice_wake()

            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                success = await loop.run_in_executor(executor, start_sync)

            if success:
                return WakeWordResponse(
                    success=True,
                    message="语音唤醒已启动",
                    status=get_wake_status()
                )
            else:
                return WakeWordResponse(
                    success=False,
                    message="语音唤醒启动失败，请检查Vosk模型"
                )

        elif request.action == "stop":
            # 停止语音唤醒
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            def stop_sync():
                stop_voice_wake()

            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                await loop.run_in_executor(executor, stop_sync)

            return WakeWordResponse(
                success=True,
                message="语音唤醒已停止",
                status=get_wake_status()
            )

        elif request.action == "status":
            # 获取状态
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            def status_sync():
                return get_wake_status()

            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                status = await loop.run_in_executor(executor, status_sync)

            return WakeWordResponse(
                success=True,
                message="获取状态成功",
                status=status
            )

        else:
            raise HTTPException(status_code=400, detail=f"不支持的操作: {request.action}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音唤醒控制失败: {str(e)}")


@router.get("/wake-word/status")
async def get_wake_word_status():
    """获取语音唤醒状态"""
    try:
        from ..services.speech.voice_wake_service import get_wake_status
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def status_sync():
            return get_wake_status()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            status = await loop.run_in_executor(executor, status_sync)

        return status

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取唤醒状态失败: {str(e)}")


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

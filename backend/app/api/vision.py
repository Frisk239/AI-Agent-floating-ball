"""
AI Agent Floating Ball - Vision API
视觉功能API路由
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import base64
import os
from pathlib import Path

from ..core.config import get_config


router = APIRouter()


class VisionRequest(BaseModel):
    image_base64: str
    prompt: str
    model: Optional[str] = "qwen-vl-plus"
    temperature: Optional[float] = 0.1


class VisionResponse(BaseModel):
    description: str
    objects: Optional[List[str]] = None
    text_content: Optional[str] = None
    confidence: Optional[float] = None


class ScreenshotRequest(BaseModel):
    prompt: Optional[str] = "请描述这张屏幕截图的内容"
    region: Optional[dict] = None  # {"x": 0, "y": 0, "width": 1920, "height": 1080}


class OCRRequest(BaseModel):
    image_base64: str
    language: Optional[str] = "zh-CN"


class OCRResponse(BaseModel):
    text: str
    confidence: Optional[float] = None
    language: str
    bounding_boxes: Optional[List[dict]] = None


@router.post("/analyze", response_model=VisionResponse)
async def analyze_image(request: VisionRequest):
    """
    分析图像内容

    - **image_base64**: base64编码的图像数据
    - **prompt**: 分析提示词
    - **model**: 使用的模型 (可选)
    - **temperature**: 温度参数 (可选)
    """
    try:
        config = get_config()

        # 解码图像数据
        try:
            image_data = base64.b64decode(request.image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"无效的base64图像数据: {str(e)}")

        # 这里应该调用视觉AI服务（如DashScope视觉模型）
        # 暂时返回模拟响应
        mock_description = f"这是对图像的分析结果。用户提示：{request.prompt}"

        return VisionResponse(
            description=mock_description,
            objects=["object1", "object2"],
            text_content="提取的文本内容",
            confidence=0.95
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图像分析失败: {str(e)}")


@router.post("/screenshot", response_model=VisionResponse)
async def analyze_screenshot(request: ScreenshotRequest):
    """
    分析屏幕截图

    - **prompt**: 分析提示词 (可选)
    - **region**: 截图区域 (可选)
    """
    try:
        # 这里应该调用屏幕截图服务
        # 暂时返回模拟响应
        mock_description = "这是屏幕截图的分析结果"

        return VisionResponse(
            description=mock_description,
            objects=["窗口", "图标", "文本"],
            text_content="屏幕上的文本内容",
            confidence=0.90
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"屏幕截图分析失败: {str(e)}")


@router.post("/ocr", response_model=OCRResponse)
async def optical_character_recognition(request: OCRRequest):
    """
    OCR文字识别

    - **image_base64**: base64编码的图像数据
    - **language**: 语言代码 (zh-CN, en-US, etc.)
    """
    try:
        config = get_config()

        # 解码图像数据
        try:
            image_data = base64.b64decode(request.image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"无效的base64图像数据: {str(e)}")

        # 这里应该调用OCR服务（如Tesseract或云端OCR）
        # 暂时返回模拟响应
        mock_text = "这是OCR识别出的文字内容"

        return OCRResponse(
            text=mock_text,
            confidence=0.92,
            language=request.language,
            bounding_boxes=[
                {"x": 10, "y": 10, "width": 100, "height": 20, "text": "示例文字"}
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR识别失败: {str(e)}")


@router.post("/upload", response_model=VisionResponse)
async def upload_and_analyze_image(
    file: UploadFile = File(...),
    prompt: str = "请描述这张图片的内容"
):
    """
    上传并分析图像文件

    - **file**: 图像文件 (png, jpg, jpeg等格式)
    - **prompt**: 分析提示词 (可选)
    """
    try:
        # 验证文件类型
        allowed_formats = ["image/png", "image/jpeg", "image/jpg", "image/webp"]
        if file.content_type not in allowed_formats:
            raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file.content_type}")

        # 读取文件内容
        image_data = await file.read()

        # 转换为base64
        image_base64 = base64.b64encode(image_data).decode()

        # 调用图像分析服务
        vision_request = VisionRequest(
            image_base64=image_base64,
            prompt=prompt
        )

        return await analyze_image(vision_request)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图像上传分析失败: {str(e)}")


@router.get("/status")
async def get_vision_status():
    """获取视觉服务状态"""
    config = get_config()

    return {
        "vision_enabled": True,  # 假设视觉服务始终可用
        "ocr_enabled": True,
        "screenshot_enabled": True,
        "supported_formats": config.vision.supported_formats,
        "max_image_size": config.vision.max_image_size
    }


@router.get("/models")
async def get_vision_models():
    """获取可用的视觉模型"""
    models = {
        "qwen-vl-plus": {
            "name": "Qwen VL Plus",
            "description": "通义千问视觉大模型",
            "capabilities": ["image_analysis", "ocr", "object_detection"]
        },
        "qwen-vl-max": {
            "name": "Qwen VL Max",
            "description": "通义千问视觉大模型Max版",
            "capabilities": ["image_analysis", "ocr", "object_detection", "reasoning"]
        }
    }

    return {"models": models}

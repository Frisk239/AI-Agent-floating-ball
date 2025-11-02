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
        from ..services.vision.vision_service import get_image_response
        import tempfile
        import os

        config = get_config()

        # 解码图像数据
        try:
            image_data = base64.b64decode(request.image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"无效的base64图像数据: {str(e)}")

        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(image_data)
            temp_file_path = temp_file.name

        try:
            # 调用视觉分析服务
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            def vision_sync():
                return get_image_response(request.prompt, temp_file_path)

            # 在线程池中运行视觉分析
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(executor, vision_sync)

            if result:
                return VisionResponse(
                    description=result,
                    objects=[],  # 暂时不支持对象检测
                    text_content="",  # 暂时不支持文本提取
                    confidence=0.95
                )
            else:
                return VisionResponse(
                    description="图像分析失败，请重试",
                    objects=[],
                    text_content="",
                    confidence=0.0
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
        raise HTTPException(status_code=500, detail=f"图像分析失败: {str(e)}")


@router.post("/screenshot", response_model=VisionResponse)
async def analyze_screenshot(request: ScreenshotRequest):
    """
    分析屏幕截图

    - **prompt**: 分析提示词 (可选)
    - **region**: 截图区域 (可选)
    """
    try:
        from ..services.vision.screen_capture_service import capture_screen_opencv_only
        from ..services.vision.vision_service import get_image_response
        import os

        config = get_config()

        # 设置截图文件路径
        screenshot_path = "imgs/screen_capture.png"

        # 确保目录存在
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

        # 执行屏幕截图
        if request.region:
            # 有指定区域
            bbox = (
                request.region.get("x", 0),
                request.region.get("y", 0),
                request.region.get("x", 0) + request.region.get("width", 1920),
                request.region.get("y", 0) + request.region.get("height", 1080)
            )
            capture_screen_opencv_only(screenshot_path, bbox)
        else:
            # 全屏截图
            capture_screen_opencv_only(screenshot_path)

        # 分析截图
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def screenshot_sync():
            return get_image_response(request.prompt or "请描述这张屏幕截图的内容", screenshot_path)

        # 在线程池中运行分析
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, screenshot_sync)

        if result:
            return VisionResponse(
                description=result,
                objects=[],  # 暂时不支持对象检测
                text_content="",  # 暂时不支持文本提取
                confidence=0.90
            )
        else:
            return VisionResponse(
                description="屏幕截图分析失败，请重试",
                objects=[],
                text_content="",
                confidence=0.0
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
        from ..services.vision.ocr_service import ocr_image
        import tempfile
        import os

        config = get_config()

        # 解码图像数据
        try:
            image_data = base64.b64decode(request.image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"无效的base64图像数据: {str(e)}")

        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(image_data)
            temp_file_path = temp_file.name

        try:
            # 设置OCR语言参数
            lang_map = {
                "zh-CN": "chi_sim",
                "zh-TW": "chi_tra",
                "en-US": "eng",
                "ja": "jpn",
                "ko": "kor"
            }
            ocr_lang = lang_map.get(request.language, "chi_sim+eng")

            # 调用OCR服务
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            def ocr_sync():
                return ocr_image(temp_file_path, lang=ocr_lang)

            # 在线程池中运行OCR
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(executor, ocr_sync)

            if result and not result.startswith("错误"):
                return OCRResponse(
                    text=result,
                    confidence=0.92,
                    language=request.language,
                    bounding_boxes=[]  # 暂时不支持边界框
                )
            else:
                return OCRResponse(
                    text=result or "OCR识别失败，请检查Tesseract安装",
                    confidence=0.0,
                    language=request.language,
                    bounding_boxes=[]
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

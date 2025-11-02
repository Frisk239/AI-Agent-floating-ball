"""
AI Agent Floating Ball - System API
系统功能API路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import psutil
import platform
import os
from pathlib import Path

from ..core.config import get_config


router = APIRouter()


class SystemInfo(BaseModel):
    platform: str
    version: str
    architecture: str
    hostname: str
    cpu_count: int
    memory_total: int
    disk_total: int


class ProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str


class FileOperationRequest(BaseModel):
    operation: str  # "read", "write", "delete", "list"
    path: str
    content: Optional[str] = None
    encoding: Optional[str] = "utf-8"


class FileOperationResponse(BaseModel):
    success: bool
    message: str
    content: Optional[str] = None
    files: Optional[List[str]] = None


class SearchRequest(BaseModel):
    query: str
    search_type: Optional[str] = "web"  # "web", "chat"


class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_results: int
    search_time: float


class WeatherRequest(BaseModel):
    city: Optional[str] = None  # 如果不提供则自动获取当前城市


class WeatherResponse(BaseModel):
    city: str
    temperature: str
    feels_like: str
    humidity: str
    wind_direction: str
    wind_scale: str
    precipitation: str
    description: str


class WebReadRequest(BaseModel):
    url: Optional[str] = None  # 如果不提供则自动获取当前浏览器URL


class WebReadResponse(BaseModel):
    url: str
    title: str
    content: str
    summary: Optional[str] = None


class ContentAnalysisRequest(BaseModel):
    content: str
    analysis_type: str  # "summary", "write", "code", "explain"


class ContentAnalysisResponse(BaseModel):
    result: str
    analysis_type: str


class FileConversionRequest(BaseModel):
    input_content: str
    conversion_type: str  # "markdown_to_excel", "markdown_to_word"


class FileConversionResponse(BaseModel):
    success: bool
    message: str
    output_path: Optional[str] = None


@router.get("/info", response_model=SystemInfo)
async def get_system_info():
    """获取系统基本信息"""
    try:
        # 获取系统信息
        system_info = platform.uname()

        # 获取内存信息
        memory = psutil.virtual_memory()

        # 获取磁盘信息
        disk = psutil.disk_usage('/')

        return SystemInfo(
            platform=system_info.system,
            version=system_info.version,
            architecture=system_info.machine,
            hostname=system_info.node,
            cpu_count=psutil.cpu_count(),
            memory_total=memory.total,
            disk_total=disk.total
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统信息失败: {str(e)}")


@router.get("/performance")
async def get_system_performance():
    """获取系统性能指标"""
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)

        # 内存使用情况
        memory = psutil.virtual_memory()

        # 磁盘使用情况
        disk = psutil.disk_usage('/')

        # 网络IO
        network = psutil.net_io_counters()

        return {
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count(),
                "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk": {
                "total": disk.total,
                "free": disk.free,
                "percent": disk.percent,
                "used": disk.used
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取性能指标失败: {str(e)}")


@router.get("/processes", response_model=List[ProcessInfo])
async def get_process_list(limit: int = 20):
    """获取进程列表"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                info = proc.info
                processes.append(ProcessInfo(
                    pid=info['pid'],
                    name=info['name'],
                    cpu_percent=info['cpu_percent'] or 0.0,
                    memory_percent=info['memory_percent'] or 0.0,
                    status=info['status']
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # 按CPU使用率排序并限制数量
        processes.sort(key=lambda x: x.cpu_percent, reverse=True)
        return processes[:limit]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取进程列表失败: {str(e)}")


@router.post("/files", response_model=FileOperationResponse)
async def file_operation(request: FileOperationRequest):
    """
    文件操作

    - **operation**: 操作类型 ("read", "write", "delete", "list")
    - **path**: 文件/文件夹路径
    - **content**: 写入的内容 (write操作时需要)
    - **encoding**: 文件编码 (默认utf-8)
    """
    try:
        config = get_config()
        path = Path(request.path)

        # 安全检查：确保路径在允许的范围内
        if not str(path).startswith(str(Path.cwd())) and not path.is_absolute():
            # 如果是相对路径，转换为绝对路径
            path = Path.cwd() / path

        if request.operation == "read":
            # 读取文件
            if not path.exists():
                raise HTTPException(status_code=404, detail=f"文件不存在: {path}")

            if not path.is_file():
                raise HTTPException(status_code=400, detail=f"路径不是文件: {path}")

            with open(path, 'r', encoding=request.encoding) as f:
                content = f.read()

            return FileOperationResponse(
                success=True,
                message=f"文件读取成功: {path}",
                content=content
            )

        elif request.operation == "write":
            # 写入文件
            if request.content is None:
                raise HTTPException(status_code=400, detail="写入操作需要提供content")

            # 确保目录存在
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding=request.encoding) as f:
                f.write(request.content)

            return FileOperationResponse(
                success=True,
                message=f"文件写入成功: {path}"
            )

        elif request.operation == "delete":
            # 删除文件
            if not path.exists():
                raise HTTPException(status_code=404, detail=f"文件不存在: {path}")

            if path.is_file():
                path.unlink()
            elif path.is_dir():
                import shutil
                shutil.rmtree(path)

            return FileOperationResponse(
                success=True,
                message=f"删除成功: {path}"
            )

        elif request.operation == "list":
            # 列出目录内容
            if not path.exists():
                raise HTTPException(status_code=404, detail=f"路径不存在: {path}")

            if not path.is_dir():
                raise HTTPException(status_code=400, detail=f"路径不是目录: {path}")

            files = [str(f) for f in path.iterdir()]
            return FileOperationResponse(
                success=True,
                message=f"目录列出成功: {path}",
                files=files
            )

        else:
            raise HTTPException(status_code=400, detail=f"不支持的操作类型: {request.operation}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件操作失败: {str(e)}")


@router.get("/config")
async def get_current_config():
    """获取当前配置信息（脱敏）"""
    config = get_config()

    # 返回脱敏的配置信息
    return {
        "app": {
            "name": config.app.name,
            "version": config.app.version
        },
        "server": {
            "host": config.server.host,
            "port": config.server.port
        },
        "ai": {
            "moonshot": {
                "model": config.ai.moonshot.model,
                "configured": bool(config.ai.moonshot.api_key)
            },
            "dashscope": {
                "configured": bool(config.ai.dashscope.api_key)
            },
            "metaso": {
                "configured": bool(config.ai.metaso.api_key)
            }
        },
        "speech": {
            "wake_word": config.speech.wake_word,
            "tts_enabled": bool(config.ai.dashscope.api_key),
            "asr_enabled": bool(config.ai.dashscope.api_key)
        },
        "vision": {
            "enabled": True,
            "supported_formats": config.vision.supported_formats
        },
        "automation": {
            "gesture_enabled": config.automation.gesture_enabled,
            "hotkey_enabled": config.automation.hotkey_enabled,
            "system_control_enabled": config.automation.system_control_enabled
        },
        "ui": {
            "theme": config.ui.theme,
            "hotkey": config.ui.hotkey
        }
    }


@router.get("/logs")
async def get_system_logs(lines: int = 100):
    """获取系统日志"""
    try:
        config = get_config()
        log_file = Path(config.logging.file)

        if not log_file.exists():
            return {"logs": [], "message": "日志文件不存在"}

        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

        return {
            "logs": [line.strip() for line in recent_lines],
            "total_lines": len(all_lines),
            "returned_lines": len(recent_lines)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志失败: {str(e)}")


@router.post("/shutdown")
async def shutdown_system(delay: int = 0):
    """
    关闭系统

    - **delay**: 延迟关闭时间（秒），0表示立即关闭
    """
    try:
        import subprocess
        import time

        if delay > 0:
            time.sleep(delay)

        # Windows关机命令
        if platform.system() == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
        else:
            # Linux/Mac
            subprocess.run(["sudo", "shutdown", "now"], check=True)

        return {"message": f"系统将在{delay}秒后关闭"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"系统关闭失败: {str(e)}")


@router.post("/restart")
async def restart_system(delay: int = 0):
    """
    重启系统

    - **delay**: 延迟重启时间（秒），0表示立即重启
    """
    try:
        import subprocess
        import time

        if delay > 0:
            time.sleep(delay)

        # Windows重启命令
        if platform.system() == "Windows":
            subprocess.run(["shutdown", "/r", "/t", "0"], check=True)
        else:
            # Linux/Mac
            subprocess.run(["sudo", "reboot"], check=True)

        return {"message": f"系统将在{delay}秒后重启"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"系统重启失败: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_web(request: SearchRequest):
    """
    网页搜索

    - **query**: 搜索查询内容
    - **search_type**: 搜索类型 ("web", "chat")
    """
    try:
        import time
        from ..services.web.search import search_chat, search_chat2

        start_time = time.time()

        if request.search_type == "chat":
            # 聊天式搜索
            result = search_chat(request.query)
            results = [{"type": "chat", "content": result}]
        else:
            # 网页搜索
            result = search_chat2(request.query)
            # 解析JSON结果
            import json
            try:
                data = json.loads(result)
                results = []
                if "webpages" in data:
                    for webpage in data["webpages"][:5]:  # 限制前5个结果
                        results.append({
                            "title": webpage.get("title", ""),
                            "link": webpage.get("link", ""),
                            "snippet": webpage.get("snippet", "")
                        })
                else:
                    results = [{"type": "web", "content": result}]
            except:
                results = [{"type": "web", "content": result}]

        search_time = time.time() - start_time

        return SearchResponse(
            results=results,
            total_results=len(results),
            search_time=search_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"网页搜索失败: {str(e)}")


@router.post("/weather", response_model=WeatherResponse)
async def get_weather(request: WeatherRequest):
    """
    获取天气信息

    - **city**: 城市名称（可选，不提供则自动获取当前城市）
    """
    try:
        from ..services.web.Weather_data_get import get_weather as get_weather_service

        # 调用天气服务
        weather_info = get_weather_service(request.city)

        # 解析天气信息
        lines = weather_info.strip().split('\n')
        weather_data = {}

        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                weather_data[key] = value

        return WeatherResponse(
            city=request.city or "自动获取",
            temperature=weather_data.get('温度', '未知'),
            feels_like=weather_data.get('体感温度', '未知'),
            humidity=weather_data.get('湿度', '未知'),
            wind_direction=weather_data.get('风向', '未知'),
            wind_scale=weather_data.get('风力等级', '未知'),
            precipitation=weather_data.get('降水量', '未知'),
            description=weather_info
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取天气信息失败: {str(e)}")


@router.post("/web/read", response_model=WebReadResponse)
async def read_webpage(request: WebReadRequest):
    """
    读取网页内容

    - **url**: 网页URL（可选，不提供则自动获取当前浏览器URL）
    """
    try:
        from ..services.web.web_reader import read_webpage, extract_current_webpage_url

        if request.url:
            # 使用提供的URL
            url = request.url
        else:
            # 自动获取当前浏览器URL
            url = extract_current_webpage_url()
            if not url:
                raise HTTPException(status_code=400, detail="无法获取当前浏览器URL，请确保浏览器窗口处于活动状态")

        # 读取网页内容
        content = read_webpage()

        # 尝试提取标题
        title = "网页内容"
        try:
            import json
            data = json.loads(content)
            if "title" in data:
                title = data["title"]
        except:
            pass

        return WebReadResponse(
            url=url,
            title=title,
            content=content,
            summary=None  # 暂时不支持摘要
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取网页内容失败: {str(e)}")


@router.post("/content/analyze", response_model=ContentAnalysisResponse)
async def analyze_content(request: ContentAnalysisRequest):
    """
    AI内容分析

    - **content**: 要分析的内容
    - **analysis_type**: 分析类型 ("summary", "write", "code", "explain")
    """
    try:
        from ..services.file_processing.content_analyzer import (
            get_file_summary, write_ai_model, code_ai_model, code_ai_explain_model
        )

        if request.analysis_type == "summary":
            # 文件摘要
            result = get_file_summary(request.content)
        elif request.analysis_type == "write":
            # AI写作
            result = write_ai_model(request.content)
        elif request.analysis_type == "code":
            # 代码生成
            result = code_ai_model(request.content)
        elif request.analysis_type == "explain":
            # 代码解释
            result = code_ai_explain_model(request.content)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的分析类型: {request.analysis_type}")

        return ContentAnalysisResponse(
            result=result,
            analysis_type=request.analysis_type
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内容分析失败: {str(e)}")


@router.post("/files/convert", response_model=FileConversionResponse)
async def convert_file(request: FileConversionRequest):
    """
    文件格式转换

    - **input_content**: 输入内容（Markdown字符串或文件路径）
    - **conversion_type**: 转换类型 ("markdown_to_excel", "markdown_to_word")
    """
    try:
        if request.conversion_type == "markdown_to_excel":
            # Markdown转Excel
            from ..services.file_processing.markdown_to_excel import markdown_to_excel_main
            output_path = markdown_to_excel_main(request.input_content)
            if output_path:
                return FileConversionResponse(
                    success=True,
                    message="Markdown转Excel成功",
                    output_path=output_path
                )
            else:
                return FileConversionResponse(
                    success=False,
                    message="Markdown转Excel失败"
                )

        elif request.conversion_type == "markdown_to_word":
            # Markdown转Word
            from ..services.file_processing.markdown_to_mord_fun import md_to_word, create_file_path
            import tempfile
            import os

            # 创建临时Markdown文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(request.input_content)
                temp_md_path = temp_file.name

            try:
                # 生成Word文件路径
                word_path = create_file_path()

                # 转换Markdown到Word
                md_to_word(word_path)

                return FileConversionResponse(
                    success=True,
                    message="Markdown转Word成功",
                    output_path=word_path
                )

            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_md_path)
                except:
                    pass

        else:
            raise HTTPException(status_code=400, detail=f"不支持的转换类型: {request.conversion_type}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件转换失败: {str(e)}")

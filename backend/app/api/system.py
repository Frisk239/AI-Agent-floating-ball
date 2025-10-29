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
                "configured": bool(config.ai.metas.api_key)
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

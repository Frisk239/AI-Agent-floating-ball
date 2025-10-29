"""
AI Agent Floating Ball - Automation API
自动化功能API路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from ..core.config import get_config


router = APIRouter()


class WindowInfo(BaseModel):
    title: str
    pid: int
    executable: str
    is_active: bool = False


class AutomationRequest(BaseModel):
    action: str
    parameters: Optional[Dict[str, Any]] = None


class AutomationResponse(BaseModel):
    success: bool
    message: str
    result: Optional[Dict[str, Any]] = None


class GestureControlRequest(BaseModel):
    enabled: bool
    sensitivity: Optional[float] = 0.5


class KeyboardShortcutRequest(BaseModel):
    keys: List[str]  # ["ctrl", "c"] 或 ["win", "r"]


@router.get("/windows", response_model=List[WindowInfo])
async def get_window_list():
    """获取当前所有窗口列表"""
    try:
        # 这里应该调用窗口管理服务
        # 暂时返回模拟数据
        mock_windows = [
            WindowInfo(
                title="AI Agent Floating Ball",
                pid=1234,
                executable="python.exe",
                is_active=True
            ),
            WindowInfo(
                title="Visual Studio Code",
                pid=5678,
                executable="Code.exe",
                is_active=False
            )
        ]

        return mock_windows

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取窗口列表失败: {str(e)}")


@router.get("/active-window")
async def get_active_window():
    """获取当前活动窗口信息"""
    try:
        # 这里应该调用窗口服务
        mock_window = {
            "title": "AI Agent Floating Ball",
            "pid": 1234,
            "executable": "python.exe",
            "position": {"x": 100, "y": 100},
            "size": {"width": 400, "height": 600}
        }

        return mock_window

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取活动窗口失败: {str(e)}")


@router.post("/execute", response_model=AutomationResponse)
async def execute_automation(request: AutomationRequest):
    """
    执行自动化操作

    - **action**: 操作类型
    - **parameters**: 操作参数
    """
    try:
        config = get_config()

        # 根据action类型执行不同操作
        if request.action == "click":
            # 鼠标点击
            result = await perform_mouse_click(request.parameters)
        elif request.action == "type_text":
            # 输入文本
            result = await perform_text_input(request.parameters)
        elif request.action == "press_key":
            # 按键操作
            result = await perform_key_press(request.parameters)
        elif request.action == "take_screenshot":
            # 截图
            result = await perform_screenshot(request.parameters)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的操作类型: {request.action}")

        return AutomationResponse(
            success=True,
            message=f"操作 {request.action} 执行成功",
            result=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"自动化操作失败: {str(e)}")


@router.post("/gesture/control", response_model=AutomationResponse)
async def control_gesture_recognition(request: GestureControlRequest):
    """
    控制手势识别

    - **enabled**: 是否启用手势识别
    - **sensitivity**: 灵敏度 (0.0-1.0)
    """
    try:
        config = get_config()

        if not config.automation.gesture_enabled:
            raise HTTPException(status_code=400, detail="手势识别功能未启用")

        # 这里应该调用手势控制服务
        if request.enabled:
            # 启动手势识别
            result = {"status": "started", "sensitivity": request.sensitivity}
        else:
            # 停止手势识别
            result = {"status": "stopped"}

        return AutomationResponse(
            success=True,
            message=f"手势识别已{'启动' if request.enabled else '停止'}",
            result=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"手势控制失败: {str(e)}")


@router.post("/keyboard/shortcut", response_model=AutomationResponse)
async def execute_keyboard_shortcut(request: KeyboardShortcutRequest):
    """
    执行键盘快捷键

    - **keys**: 按键组合，如 ["ctrl", "c"] 或 ["win", "r"]
    """
    try:
        config = get_config()

        if not config.automation.hotkey_enabled:
            raise HTTPException(status_code=400, detail="快捷键功能未启用")

        # 这里应该调用键盘控制服务
        # 暂时返回模拟响应
        shortcut_name = "+".join(request.keys).upper()

        return AutomationResponse(
            success=True,
            message=f"快捷键 {shortcut_name} 执行成功",
            result={"shortcut": shortcut_name}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"快捷键执行失败: {str(e)}")


@router.get("/apps")
async def get_installed_apps():
    """获取已安装的应用程序列表"""
    try:
        # 这里应该扫描系统已安装的应用
        # 暂时返回常用应用列表
        common_apps = [
            {"name": "Chrome", "executable": "chrome.exe", "path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"},
            {"name": "VS Code", "executable": "code.exe", "path": "C:\\Users\\{username}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"},
            {"name": "Notepad++", "executable": "notepad++.exe", "path": "C:\\Program Files\\Notepad++\\notepad++.exe"},
            {"name": "Calculator", "executable": "calc.exe", "path": "C:\\Windows\\System32\\calc.exe"}
        ]

        return {"apps": common_apps}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取应用列表失败: {str(e)}")


@router.post("/apps/launch", response_model=AutomationResponse)
async def launch_application(app_name: str):
    """
    启动应用程序

    - **app_name**: 应用程序名称
    """
    try:
        # 这里应该调用应用启动服务
        # 暂时返回模拟响应
        return AutomationResponse(
            success=True,
            message=f"应用程序 {app_name} 启动成功",
            result={"app_name": app_name, "status": "running"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动应用程序失败: {str(e)}")


@router.get("/status")
async def get_automation_status():
    """获取自动化服务状态"""
    config = get_config()

    return {
        "gesture_enabled": config.automation.gesture_enabled,
        "hotkey_enabled": config.automation.hotkey_enabled,
        "system_control_enabled": config.automation.system_control_enabled,
        "active_window_tracking": True,
        "mouse_control": True,
        "keyboard_control": True
    }


# 辅助函数
async def perform_mouse_click(parameters: Dict[str, Any]):
    """执行鼠标点击操作"""
    x = parameters.get("x", 0)
    y = parameters.get("y", 0)
    button = parameters.get("button", "left")

    # 这里应该调用鼠标控制服务
    return {"action": "click", "position": {"x": x, "y": y}, "button": button}


async def perform_text_input(parameters: Dict[str, Any]):
    """执行文本输入操作"""
    text = parameters.get("text", "")

    # 这里应该调用键盘输入服务
    return {"action": "type_text", "text": text, "length": len(text)}


async def perform_key_press(parameters: Dict[str, Any]):
    """执行按键操作"""
    keys = parameters.get("keys", [])

    # 这里应该调用键盘控制服务
    return {"action": "press_key", "keys": keys}


async def perform_screenshot(parameters: Dict[str, Any]):
    """执行截图操作"""
    region = parameters.get("region")

    # 这里应该调用截图服务
    return {"action": "screenshot", "region": region, "saved": True}

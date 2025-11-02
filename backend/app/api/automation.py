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
        from ..services.automation.window_service import get_recent_windows_process_info
        import win32gui
        import win32process
        import psutil

        # 获取窗口进程信息
        process_info_list = get_recent_windows_process_info()

        windows = []
        for info in process_info_list:
            if info['process_name'] and info['pid']:
                try:
                    process = psutil.Process(info['pid'])
                    executable = process.exe()
                    windows.append(WindowInfo(
                        title=f"{info['process_name']} (PID: {info['pid']})",
                        pid=info['pid'],
                        executable=executable,
                        is_active=False  # 暂时不支持活动状态检测
                    ))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        return windows

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取窗口列表失败: {str(e)}")


@router.get("/active-window")
async def get_active_window():
    """获取当前活动窗口信息"""
    try:
        from ..services.automation.window_service import get_active_window_info
        import psutil

        # 获取活动窗口信息
        window_info = get_active_window_info()

        if window_info and window_info['pid']:
            try:
                process = psutil.Process(window_info['pid'])
                executable = process.exe()
                result = {
                    "title": window_info['window_title'] or "Unknown",
                    "pid": window_info['pid'],
                    "executable": executable,
                    "process_name": window_info['process_name'],
                    "timestamp": window_info.get('timestamp', 0)
                }
                return result
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return {
                    "title": window_info['window_title'] or "Unknown",
                    "pid": window_info['pid'],
                    "executable": "Unknown",
                    "process_name": window_info['process_name'],
                    "timestamp": window_info.get('timestamp', 0)
                }
        else:
            return {
                "title": "No active window",
                "pid": None,
                "executable": None,
                "process_name": None,
                "timestamp": 0
            }

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
        import pyautogui

        config = get_config()

        if not config.automation.hotkey_enabled:
            raise HTTPException(status_code=400, detail="快捷键功能未启用")

        # 转换按键名称
        key_map = {
            "ctrl": "ctrl",
            "control": "ctrl",
            "alt": "alt",
            "shift": "shift",
            "win": "win",
            "windows": "win",
            "cmd": "win",  # macOS兼容
            "command": "win",
            "space": "space",
            "enter": "enter",
            "return": "enter",
            "tab": "tab",
            "esc": "esc",
            "escape": "esc",
            "backspace": "backspace",
            "delete": "delete",
            "home": "home",
            "end": "end",
            "pageup": "pageup",
            "pagedown": "pagedown",
            "up": "up",
            "down": "down",
            "left": "left",
            "right": "right"
        }

        # 转换按键
        keys = []
        for key in request.keys:
            key_lower = key.lower()
            if key_lower in key_map:
                keys.append(key_map[key_lower])
            else:
                # 单个字符直接使用
                keys.append(key)

        # 执行快捷键
        if len(keys) == 1:
            pyautogui.press(keys[0])
        elif len(keys) == 2:
            pyautogui.hotkey(keys[0], keys[1])
        elif len(keys) == 3:
            pyautogui.hotkey(keys[0], keys[1], keys[2])
        elif len(keys) == 4:
            pyautogui.hotkey(keys[0], keys[1], keys[2], keys[3])
        else:
            raise HTTPException(status_code=400, detail="最多支持4个按键的组合")

        shortcut_name = "+".join(request.keys).upper()

        return AutomationResponse(
            success=True,
            message=f"快捷键 {shortcut_name} 执行成功",
            result={"shortcut": shortcut_name, "keys": keys}
        )

    except HTTPException:
        raise
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
        import subprocess
        import os

        # 预定义的应用映射
        app_commands = {
            "notepad": ["notepad.exe"],
            "calculator": ["calc.exe"],
            "explorer": ["explorer.exe"],
            "cmd": ["cmd.exe"],
            "powershell": ["powershell.exe"],
            "chrome": ["start", "chrome"],
            "edge": ["start", "msedge"],
            "vscode": ["code"],
            "word": ["start", "winword"],
            "excel": ["start", "excel"],
            "powerpoint": ["start", "powerpnt"],
            "netease": ["start", "cloudmusic"],  # 网易云音乐
            "wechat": ["start", "WeChat"],  # 微信
            "qq": ["start", "QQ"],  # QQ
            "dingtalk": ["start", "DingTalk"]  # 钉钉
        }

        # 检查是否是预定义应用
        if app_name.lower() in app_commands:
            cmd = app_commands[app_name.lower()]
            subprocess.Popen(cmd, shell=True)
            return AutomationResponse(
                success=True,
                message=f"应用程序 {app_name} 启动成功",
                result={"app_name": app_name, "status": "running", "command": cmd}
            )
        else:
            # 尝试直接启动
            try:
                subprocess.Popen([app_name], shell=True)
                return AutomationResponse(
                    success=True,
                    message=f"应用程序 {app_name} 启动成功",
                    result={"app_name": app_name, "status": "running"}
                )
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail=f"未找到应用程序: {app_name}")

    except HTTPException:
        raise
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
    import pyautogui

    x = parameters.get("x", 0)
    y = parameters.get("y", 0)
    button = parameters.get("button", "left")

    # 移动鼠标到指定位置
    pyautogui.moveTo(x, y)

    # 执行点击
    if button == "left":
        pyautogui.click(x, y)
    elif button == "right":
        pyautogui.rightClick(x, y)
    elif button == "middle":
        pyautogui.middleClick(x, y)

    return {"action": "click", "position": {"x": x, "y": y}, "button": button}


async def perform_text_input(parameters: Dict[str, Any]):
    """执行文本输入操作"""
    import pyautogui

    text = parameters.get("text", "")

    # 输入文本
    pyautogui.typewrite(text)

    return {"action": "type_text", "text": text, "length": len(text)}


async def perform_key_press(parameters: Dict[str, Any]):
    """执行按键操作"""
    import pyautogui

    keys = parameters.get("keys", [])

    # 执行按键组合
    if len(keys) == 1:
        pyautogui.press(keys[0])
    elif len(keys) == 2:
        pyautogui.hotkey(keys[0], keys[1])
    elif len(keys) == 3:
        pyautogui.hotkey(keys[0], keys[1], keys[2])
    elif len(keys) == 4:
        pyautogui.hotkey(keys[0], keys[1], keys[2], keys[3])

    return {"action": "press_key", "keys": keys}


async def perform_screenshot(parameters: Dict[str, Any]):
    """执行截图操作"""
    import pyautogui
    import os

    region = parameters.get("region")

    # 确保截图目录存在
    screenshot_dir = "imgs"
    os.makedirs(screenshot_dir, exist_ok=True)

    # 生成文件名
    import time
    filename = f"{screenshot_dir}/automation_screenshot_{int(time.time())}.png"

    # 执行截图
    if region:
        # 区域截图
        screenshot = pyautogui.screenshot(region=(
            region.get("x", 0),
            region.get("y", 0),
            region.get("width", 1920),
            region.get("height", 1080)
        ))
    else:
        # 全屏截图
        screenshot = pyautogui.screenshot()

    # 保存截图
    screenshot.save(filename)

    return {"action": "screenshot", "region": region, "saved": True, "filename": filename}

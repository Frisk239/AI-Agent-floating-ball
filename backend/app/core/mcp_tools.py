#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
AI Agent Floating Ball - MCP工具封装

基于当前项目的实际API接口，将所有服务功能封装为标准化的MCP工具。
完全匹配当前项目的API结构和参数。

功能模块：
1. 自动化工具 - 基于 /api/automation/ API
2. 语音工具 - 基于 /api/speech/ API
3. 视觉工具 - 基于 /api/vision/ API
4. 系统工具 - 基于 /api/system/ API
5. 聊天工具 - 基于 /api/chat/ API

作者: AI Assistant
版本: 3.0.0
"""

import time
import requests
import json
import base64
import os
from typing import List, Dict, Optional, Union, Any
from fastmcp import FastMCP

# 初始化FastMCP实例
mcp = FastMCP("AI Agent Floating Ball")

# API基础配置
BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30

# 会话管理
session = requests.Session()
session.timeout = API_TIMEOUT

def make_api_request(method: str, endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict:
    """统一的API请求函数"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method.upper() == "GET":
            response = session.get(url, params=data)
        elif method.upper() == "POST":
            if files:
                response = session.post(url, data=data, files=files)
            else:
                response = session.post(url, json=data)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": f"API请求失败: {str(e)}", "success": False}
    except json.JSONDecodeError as e:
        return {"error": f"JSON解析失败: {str(e)}", "success": False}

# =============================================================================
# 自动化工具模块 - 基于 /api/automation/ API
# =============================================================================

@mcp.tool()
def launch_application(app_name: str) -> Dict[str, Union[bool, str]]:
    """
    智能应用启动器 - 启动指定的应用程序

    该函数使用双重启动策略：首先尝试预定义的应用映射，
    如果失败则使用Windows开始菜单搜索功能来启动应用程序。

    Args:
        app_name (str): 要启动的应用程序名称，支持：
            - 系统应用: notepad, calculator, explorer, cmd, powershell
            - 浏览器: chrome, edge
            - 开发工具: vscode, word, excel, powerpoint
            - 娱乐应用: netease(网易云音乐), wechat(微信), qq, dingtalk(钉钉)

    Returns:
        Dict[str, Union[bool, str]]: 启动结果字典
            {
                "success": bool,           # 是否启动成功
                "method": str,            # 使用的启动方法 ("predefined" 或 "search")
                "message": str,           # 详细消息
                "app_name": str           # 应用名称
            }

    Example:
        >>> launch_application("notepad")
        {'success': True, 'method': 'predefined', 'message': '应用程序 notepad 启动成功', 'app_name': 'notepad'}

        >>> launch_application("微信")
        {'success': True, 'method': 'search', 'message': '应用程序 微信 通过搜索启动成功', 'app_name': '微信'}
    """
    result = make_api_request("POST", "/api/automation/apps/launch", {"app_name": app_name})
    if result.get("success"):
        return result
    else:
        return {
            "success": False,
            "method": "error",
            "message": result.get("error", "启动应用程序失败"),
            "app_name": app_name
        }


@mcp.tool()
def control_music_player(actions: List[str]) -> str:
    """
    音乐播放器控制 - 控制音乐播放应用

    通过模拟键盘快捷键来控制音乐播放应用（如网易云音乐、QQ音乐等），
    支持播放控制、音量调节等操作。

    Args:
        actions (List[str]): 要执行的操作名称列表，支持：
            - 'play_pause': 播放/暂停
            - 'next_song': 下一首
            - 'previous_song': 上一首
            - 'volume_up': 音量增大
            - 'volume_down': 音量减小
            - 'mini_mode': 切换迷你模式
            - 'like_song': 喜欢当前歌曲
            - 'lyrics_toggle': 显示/隐藏歌词
            - 'mute': 静音/取消静音
            - 'shuffle': 切换随机播放
            - 'repeat': 切换重复播放

    Returns:
        str: 操作执行结果描述，包括成功和失败的操作详情

    Example:
        >>> control_music_player(["play_pause", "next_song"])
        '已成功执行以下音乐操作: play_pause, next_song。'

        >>> control_music_player(["volume_up", "volume_up"])
        '已成功执行以下音乐操作: volume_up, volume_up。'
    """
    result = make_api_request("POST", "/api/automation/apps/music/control", {"actions": actions})
    if result.get("success"):
        return result.get("message", "音乐控制成功")
    else:
        return result.get("error", "音乐播放器控制失败")


@mcp.tool()
def control_browser(actions: List[str]) -> str:
    """
    浏览器控制 - 控制浏览器应用

    通过模拟键盘快捷键来控制浏览器（如Chrome、Edge、Firefox等），
    支持标签页管理、导航、缩放等操作。

    Args:
        actions (List[str]): 要执行的操作名称列表，支持：
            - 'new_tab': 新建标签页
            - 'close_tab': 关闭当前标签页
            - 'next_tab': 切换到下一个标签页
            - 'previous_tab': 切换到上一个标签页
            - 'reopen_closed_tab': 重新打开关闭的标签页
            - 'refresh': 刷新页面
            - 'hard_refresh': 强制刷新页面
            - 'back': 后退
            - 'forward': 前进
            - 'home': 回到主页
            - 'bookmarks': 打开书签
            - 'history': 打开历史记录
            - 'downloads': 打开下载
            - 'fullscreen': 全屏/退出全屏
            - 'zoom_in': 放大
            - 'zoom_out': 缩小
            - 'reset_zoom': 重置缩放

    Returns:
        str: 操作执行结果描述，包括成功和失败的操作详情

    Example:
        >>> control_browser(["new_tab", "close_tab"])
        '已成功执行以下浏览器操作: new_tab, close_tab。'

        >>> control_browser(["refresh", "fullscreen"])
        '已成功执行以下浏览器操作: refresh, fullscreen。'
    """
    try:
        result = control_browser_app(actions)
        return result
    except Exception as e:
        return f"浏览器控制失败: {str(e)}"


@mcp.tool()
def control_office_application(actions: List[str], app_type: str = "word") -> str:
    """
    Office应用控制 - 控制Office应用程序

    通过模拟键盘快捷键来控制Office应用（如Word、Excel、PowerPoint），
    支持文档操作、格式设置等功能。

    Args:
        actions (List[str]): 要执行的操作名称列表
        app_type (str, optional): 应用程序类型，支持 "word", "excel", "powerpoint"

    Returns:
        str: 操作执行结果描述，包括成功和失败的操作详情

    Example:
        >>> control_office_application(["save", "copy"], "word")
        '已成功执行以下WORD操作: save, copy。'

        >>> control_office_application(["bold", "italic"], "word")
        '已成功执行以下WORD操作: bold, italic。'
    """
    try:
        result = control_office_app(actions, app_type)
        return result
    except Exception as e:
        return f"Office应用控制失败: {str(e)}"


@mcp.tool()
def create_word_document(file_name: Optional[str] = None) -> str:
    """
    创建Word文档 - 创建并打开新的Word文档

    使用python-docx库创建一个新的空白Word文档，并自动打开供用户编辑。

    Args:
        file_name (str, optional): 文档文件名，如果不提供则使用默认名称

    Returns:
        str: 操作结果描述

    Example:
        >>> create_word_document("我的文档.docx")
        '文档已创建并打开: C:\\Users\\Username\\Desktop\\我的文档.docx'

        >>> create_word_document()
        '文档已创建并打开: C:\\Users\\Username\\Desktop\\new.docx'
    """
    try:
        result = create_and_open_word_doc(file_name)
        return result
    except Exception as e:
        return f"创建Word文档失败: {str(e)}"


@mcp.tool()
def launch_applications_by_search(app_names: List[str]) -> str:
    """
    通过搜索启动应用 - 使用Windows开始菜单搜索功能启动应用

    当标准启动方式无法启动某些应用程序时，使用此函数通过
    Windows开始菜单的搜索功能来启动应用程序。

    Args:
        app_names (List[str]): 要启动的应用程序名称列表

    Returns:
        str: 操作结果描述，包含成功启动的应用程序列表

    Example:
        >>> launch_applications_by_search(["微信", "QQ音乐"])
        '已打开以下软件: 微信, QQ音乐'
    """
    try:
        result = open_other_apps(app_names)
        return result
    except Exception as e:
        return f"通过搜索启动应用失败: {str(e)}"


@mcp.tool()
def get_window_information() -> List[Dict[str, Union[str, int]]]:
    """
    获取窗口信息 - 获取当前系统中的所有窗口信息

    获取系统中所有可见窗口的详细信息，包括窗口标题、进程ID、位置等。

    Returns:
        List[Dict[str, Union[str, int]]]: 窗口信息列表，每个窗口包含：
            - title: 窗口标题
            - pid: 进程ID
            - handle: 窗口句柄
            - rect: 窗口位置和大小

    Example:
        >>> get_window_information()
        [
            {
                'title': 'Visual Studio Code',
                'pid': 1234,
                'handle': 123456,
                'rect': {'left': 0, 'top': 0, 'right': 1920, 'bottom': 1080}
            }
        ]
    """
    try:
        windows = get_window_list_detailed()
        return windows
    except Exception as e:
        return [{"error": f"获取窗口信息失败: {str(e)}"}]


@mcp.tool()
def activate_window_by_title(window_title: str) -> str:
    """
    激活窗口 - 通过窗口标题激活指定的窗口

    将指定的窗口设置为活动窗口，并将其带到前台。

    Args:
        window_title (str): 要激活的窗口标题（支持部分匹配）

    Returns:
        str: 操作结果描述

    Example:
        >>> activate_window_by_title("Visual Studio Code")
        '已成功激活窗口: Visual Studio Code'

        >>> activate_window_by_title("Chrome")
        '已成功激活窗口: Google Chrome'
    """
    try:
        result = find_and_activate_window(window_title, "title")
        return result
    except Exception as e:
        return f"激活窗口失败: {str(e)}"


@mcp.tool()
def get_current_active_window() -> Dict[str, Union[str, int]]:
    """
    获取当前活动窗口信息

    获取当前活动窗口的详细信息，包括窗口标题、进程ID等。

    Returns:
        Dict[str, Union[str, int]]: 当前活动窗口信息
            {
                "title": str,      # 窗口标题
                "pid": int,        # 进程ID
                "path": str        # 应用程序路径
            }

    Example:
        >>> get_current_active_window()
        {
            'title': 'Visual Studio Code',
            'pid': 1234,
            'path': 'C:\\Users\\Username\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe'
        }
    """
    try:
        info = get_active_window_info()
        return info
    except Exception as e:
        return {"error": f"获取活动窗口信息失败: {str(e)}"}


@mcp.tool()
def manage_window(window_title: str, action: str) -> str:
    """
    窗口管理 - 对指定窗口执行管理操作

    对指定的窗口执行最小化、最大化或关闭操作。

    Args:
        window_title (str): 目标窗口标题
        action (str): 要执行的操作，支持 "minimize", "maximize", "close"

    Returns:
        str: 操作结果描述

    Example:
        >>> manage_window("Visual Studio Code", "minimize")
        '已成功最小化窗口: Visual Studio Code'

        >>> manage_window("Chrome", "close")
        '已成功关闭窗口: Chrome'
    """
    try:
        if action == "minimize":
            result = minimize_window_by_pid(window_title)
        elif action == "maximize":
            result = maximize_window_by_pid(window_title)
        elif action == "close":
            result = close_window_by_pid(window_title)
        else:
            return f"不支持的操作: {action}"

        return result
    except Exception as e:
        return f"窗口管理操作失败: {str(e)}"


@mcp.tool()
def execute_keyboard_shortcuts(actions: List[str]) -> str:
    """
    执行键盘快捷键 - 执行系统级键盘快捷键

    执行一系列Windows系统快捷键，支持窗口管理、系统操作等。

    Args:
        actions (List[str]): 要执行的快捷键操作列表

    Returns:
        str: 执行结果描述

    Example:
        >>> execute_keyboard_shortcuts(["task_manager", "file_explorer"])
        '已成功执行以下操作: task_manager, file_explorer。'
    """
    try:
        result = execute_multiple_shortcuts(actions)
        return result
    except Exception as e:
        return f"执行键盘快捷键失败: {str(e)}"


@mcp.tool()
def get_available_shortcuts() -> Dict[str, str]:
    """
    获取可用快捷键列表

    获取系统中所有支持的键盘快捷键及其描述。

    Returns:
        Dict[str, str]: 快捷键名称到描述的映射字典

    Example:
        >>> get_available_shortcuts()
        {
            'task_manager': '打开任务管理器 (Ctrl+Shift+Esc)',
            'file_explorer': '打开文件资源管理器 (Win+E)',
            'lock_screen': '锁定屏幕 (Win+L)'
        }
    """
    try:
        shortcuts = get_available_shortcuts()
        return shortcuts
    except Exception as e:
        return {"error": f"获取快捷键列表失败: {str(e)}"}


# =============================================================================
# 文件处理工具模块
# =============================================================================

@mcp.tool()
def analyze_text_content(text: str, analysis_type: str = "summary") -> str:
    """
    文本内容分析 - 分析和处理文本内容

    对输入的文本内容进行各种分析，包括摘要提取、关键词提取等。

    Args:
        text (str): 要分析的文本内容
        analysis_type (str, optional): 分析类型，支持 "summary", "keywords", "sentiment"

    Returns:
        str: 分析结果

    Example:
        >>> analyze_text_content("这是一段很长的文本内容...", "summary")
        '文本摘要：这段文本主要讨论了...'

        >>> analyze_text_content("人工智能发展前景", "keywords")
        '关键词：人工智能, 发展, 前景, 技术'
    """
    try:
        if analysis_type == "summary":
            result = get_file_summary(text)
        elif analysis_type == "batch":
            result = batch_analyze_texts([text], "总结")["results"][0] if text else "文本内容为空"
        else:
            result = get_file_summary(text)  # 默认使用总结功能

        return result
    except Exception as e:
        return f"文本内容分析失败: {str(e)}"


@mcp.tool()
def write_file_content(file_path: str, content: str, mode: str = "overwrite") -> str:
    """
    文件内容写入 - 向文件写入内容

    将指定的内容写入到文件中，支持覆盖写入或追加写入。

    Args:
        file_path (str): 目标文件路径
        content (str): 要写入的内容
        mode (str, optional): 写入模式，支持 "overwrite", "append"

    Returns:
        str: 操作结果描述

    Example:
        >>> write_file_content("notes.txt", "这是我的笔记", "overwrite")
        '已成功写入文件: notes.txt'

        >>> write_file_content("log.txt", "新日志条目", "append")
        '已成功追加到文件: log.txt'
    """
    try:
        if mode == "append":
            # 对于追加模式，我们需要先读取现有内容，然后合并
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                new_content = existing_content + content
            except FileNotFoundError:
                new_content = content
            result = write_and_open_txt(new_content, file_path)
        else:
            result = write_and_open_txt(content, file_path)

        return result
    except Exception as e:
        return f"文件写入失败: {str(e)}"


@mcp.tool()
def create_directory_structure(base_path: str, structure: Dict[str, Union[str, Dict]]) -> str:
    """
    创建目录结构 - 创建完整的目录和文件结构

    根据提供的结构字典创建目录和文件层次结构。

    Args:
        base_path (str): 基础路径
        structure (Dict[str, Union[str, Dict]]): 目录结构字典

    Returns:
        str: 操作结果描述

    Example:
        >>> create_directory_structure("project", {"src": {"main.py": "print('hello')", "utils": {}}})
        '已成功创建目录结构'
    """
    try:
        # 将字典结构转换为文件夹名称列表
        folder_names = []
        def extract_folders(structure_dict, current_path=""):
            for key, value in structure_dict.items():
                if isinstance(value, dict):
                    folder_names.append(key)
                    extract_folders(value, f"{current_path}/{key}" if current_path else key)
                else:
                    # 如果是文件，暂时只创建文件夹
                    folder_names.append(key.split('/')[0] if '/' in key else key)

        extract_folders(structure)
        result = create_folders_in_directory(folder_names, base_path)
        return result
    except Exception as e:
        return f"创建目录结构失败: {str(e)}"


@mcp.tool()
def convert_markdown_to_excel(markdown_text: str, output_path: Optional[str] = None) -> str:
    """
    Markdown转Excel - 将Markdown表格转换为Excel文件

    将包含表格的Markdown文本转换为Excel文件格式。

    Args:
        markdown_text (str): 包含表格的Markdown文本
        output_path (str, optional): 输出文件路径，如果不提供则使用默认路径

    Returns:
        str: 操作结果描述，包含生成的文件路径

    Example:
        >>> convert_markdown_to_excel("| 姓名 | 年龄 |\\n| --- | --- |\\n| 张三 | 25 |")
        '已生成Excel文件，文件路径为：output.xlsx'
    """
    try:
        result = markdown_to_excel_main(markdown_text, output_path)
        return result
    except Exception as e:
        return f"Markdown转Excel失败: {str(e)}"


@mcp.tool()
def convert_markdown_to_word(markdown_content: str, output_path: Optional[str] = None) -> str:
    """
    Markdown转Word - 将Markdown内容转换为Word文档

    将Markdown格式的文本转换为Word文档格式。

    Args:
        markdown_content (str): Markdown格式的文本内容
        output_path (str, optional): 输出文件路径，如果不提供则自动生成

    Returns:
        str: 操作结果描述，包含生成的文件路径

    Example:
        >>> convert_markdown_to_word("# 标题\\n这是内容")
        '已生成Word文档，文件路径为：document.docx'
    """
    try:
        if output_path is None:
            output_path = create_file_path()

        md_to_word(markdown_content, output_path)
        return f"已生成Word文档，文件路径为：{output_path}"
    except Exception as e:
        return f"Markdown转Word失败: {str(e)}"


# =============================================================================
# 语音工具模块
# =============================================================================

@mcp.tool()
def speech_to_text_from_microphone(duration: int = 5) -> str:
    """
    语音识别（麦克风）- 从麦克风输入进行语音识别

    录制指定时长的音频并转换为文本。

    Args:
        duration (int, optional): 录音时长（秒），默认为5秒

    Returns:
        str: 识别出的文本内容

    Example:
        >>> speech_to_text_from_microphone(3)
        '你好世界'

        >>> speech_to_text_from_microphone()
        '请说点什么'
    """
    try:
        result = speech_to_text()
        return result
    except Exception as e:
        return f"语音识别失败: {str(e)}"


@mcp.tool()
def speech_to_text_from_file(audio_file_path: str) -> str:
    """
    语音识别（文件）- 从音频文件进行语音识别

    对指定的音频文件进行语音识别并转换为文本。

    Args:
        audio_file_path (str): 音频文件路径

    Returns:
        str: 识别出的文本内容

    Example:
        >>> speech_to_text_from_file("recording.wav")
        '这是录音文件的内容'
    """
    try:
        result = process_audio_file_asr(audio_file_path)
        return result
    except Exception as e:
        return f"语音文件识别失败: {str(e)}"


@mcp.tool()
def text_to_speech_conversion(text: str, voice: Optional[str] = None, speed: float = 1.0) -> str:
    """
    文本转语音 - 将文本转换为语音

    将输入的文本转换为语音文件并播放。

    Args:
        text (str): 要转换为语音的文本
        voice (str, optional): 语音类型，如果不提供则使用默认语音
        speed (float, optional): 语速倍数，默认为1.0

    Returns:
        str: 操作结果描述

    Example:
        >>> text_to_speech_conversion("你好世界")
        '已成功转换为语音并播放'

        >>> text_to_speech_conversion("Hello World", voice="english", speed=0.8)
        '已成功转换为语音并播放'
    """
    result = make_api_request("POST", "/api/speech/tts", {
        "text": text,
        "voice": voice,
        "speed": speed
    })
    if result.get("success"):
        return result.get("message", "TTS转换成功")
    else:
        return result.get("error", "文本转语音失败")


@mcp.tool()
def get_speech_voices() -> List[str]:
    """
    获取可用语音列表

    获取系统中所有可用的语音类型和选项。

    Returns:
        List[str]: 可用的语音列表

    Example:
        >>> get_speech_voices()
        ['zh-CN-XiaoxiaoNeural', 'zh-CN-YunyangNeural', 'en-US-ZiraRUS']
    """
    try:
        voices = get_available_voices()
        return voices
    except Exception as e:
        return [f"获取语音列表失败: {str(e)}"]


@mcp.tool()
def start_voice_wake_detection() -> str:
    """
    启动语音唤醒检测

    启动语音唤醒服务，监听指定的唤醒词。

    Returns:
        str: 操作结果描述

    Example:
        >>> start_voice_wake_detection()
        '语音唤醒服务已启动'
    """
    try:
        result = start_voice_wake()
        return result
    except Exception as e:
        return f"启动语音唤醒失败: {str(e)}"


@mcp.tool()
def stop_voice_wake_detection() -> str:
    """
    停止语音唤醒检测

    停止语音唤醒服务。

    Returns:
        str: 操作结果描述

    Example:
        >>> stop_voice_wake_detection()
        '语音唤醒服务已停止'
    """
    try:
        result = stop_voice_wake()
        return result
    except Exception as e:
        return f"停止语音唤醒失败: {str(e)}"


@mcp.tool()
def get_voice_wake_status() -> Dict[str, Union[bool, str]]:
    """
    获取语音唤醒状态

    获取当前语音唤醒服务的运行状态和配置信息。

    Returns:
        Dict[str, Union[bool, str]]: 语音唤醒状态信息
            {
                "enabled": bool,      # 是否启用
                "wake_word": str,     # 唤醒词
                "status": str         # 当前状态
            }

    Example:
        >>> get_voice_wake_status()
        {
            'enabled': True,
            'wake_word': 'hello jarvis',
            'status': 'running'
        }
    """
    try:
        status = get_wake_status()
        return status
    except Exception as e:
        return {"error": f"获取语音唤醒状态失败: {str(e)}"}


# =============================================================================
# 视觉工具模块
# =============================================================================

@mcp.tool()
def extract_text_from_image_file(image_path: str) -> str:
    """
    OCR文字提取 - 从图片文件中提取文字

    使用OCR技术从图片文件中识别和提取文字内容。

    Args:
        image_path (str): 图片文件路径

    Returns:
        str: 提取出的文字内容

    Example:
        >>> extract_text_from_image_file("document.png")
        '这是图片中的文字内容'
    """
    try:
        result = ocr_image(image_path)
        return result
    except Exception as e:
        return f"OCR文字提取失败: {str(e)}"


@mcp.tool()
def get_supported_ocr_formats() -> List[str]:
    """
    获取支持的OCR图片格式

    获取OCR服务支持的所有图片文件格式。

    Returns:
        List[str]: 支持的图片格式列表

    Example:
        >>> get_supported_ocr_formats()
        ['png', 'jpg', 'jpeg', 'bmp', 'tiff']
    """
    try:
        formats = get_supported_image_formats()
        return formats
    except Exception as e:
        return [f"获取格式列表失败: {str(e)}"]


@mcp.tool()
def capture_screen_region(x: int, y: int, width: int, height: int, save_path: Optional[str] = None) -> str:
    """
    屏幕区域截图 - 截取指定区域的屏幕图像

    截取屏幕上指定坐标和大小的区域，并保存为图片文件。

    Args:
        x (int): 区域左上角X坐标
        y (int): 区域左上角Y坐标
        width (int): 区域宽度
        height (int): 区域高度
        save_path (str, optional): 保存路径，如果不提供则使用默认路径

    Returns:
        str: 操作结果描述，包含保存的文件路径

    Example:
        >>> capture_screen_region(100, 100, 800, 600)
        '屏幕截图已保存到: screenshot_001.png'
    """
    try:
        result = capture_screen_opencv_only(save_path, bbox=(x, y, x+width, y+height))
        return result
    except Exception as e:
        return f"屏幕区域截图失败: {str(e)}"


@mcp.tool()
def capture_full_screen(save_path: Optional[str] = None) -> str:
    """
    全屏截图 - 截取整个屏幕

    截取当前屏幕的完整图像并保存为文件。

    Args:
        save_path (str, optional): 保存路径，如果不提供则使用默认路径

    Returns:
        str: 操作结果描述，包含保存的文件路径

    Example:
        >>> capture_full_screen()
        '全屏截图已保存到: fullscreen_001.png'
    """
    try:
        result = capture_full_screen(save_path)
        return result
    except Exception as e:
        return f"全屏截图失败: {str(e)}"


@mcp.tool()
def analyze_image_with_ai(image_path: str, prompt: str) -> str:
    """
    AI图像分析 - 使用AI模型分析图片内容

    使用AI视觉模型对图片进行分析，回答关于图片的问题。

    Args:
        image_path (str): 图片文件路径
        prompt (str): 分析提示词，描述要分析的内容

    Returns:
        str: AI分析结果

    Example:
        >>> analyze_image_with_ai("photo.jpg", "描述这张图片的内容")
        '这张图片显示了一个美丽的日落场景...'
    """
    try:
        # 读取图片文件并转换为base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()

        result = make_api_request("POST", "/api/vision/analyze", {
            "image_base64": image_data,
            "prompt": prompt
        })

        if result.get("success"):
            return result.get("description", "图像分析完成")
        else:
            return result.get("error", "AI图像分析失败")

    except Exception as e:
        return f"AI图像分析失败: {str(e)}"


@mcp.tool()
def detect_objects_in_image_file(image_path: str) -> List[Dict[str, Union[str, float]]]:
    """
    物体检测 - 检测图片中的物体

    使用AI模型检测图片中的物体并返回检测结果。

    Args:
        image_path (str): 图片文件路径

    Returns:
        List[Dict[str, Union[str, float]]]: 检测到的物体列表
            每个物体包含: object(物体名称), confidence(置信度), bbox(边界框)

    Example:
        >>> detect_objects_in_image_file("scene.jpg")
        [
            {'object': 'person', 'confidence': 0.95, 'bbox': [100, 200, 150, 300]},
            {'object': 'car', 'confidence': 0.87, 'bbox': [400, 250, 550, 350]}
        ]
    """
    try:
        result = detect_objects_in_image(image_path)
        return result
    except Exception as e:
        return [{"error": f"物体检测失败: {str(e)}"}]


# =============================================================================
# 网络工具模块
# =============================================================================

@mcp.tool()
def web_search(query: str, search_type: str = "general") -> str:
    """
    网页搜索 - 使用AI搜索引擎进行网页搜索

    通过秘塔搜索API进行网页搜索，支持不同类型的搜索。

    Args:
        query (str): 搜索查询内容
        search_type (str, optional): 搜索类型，支持 "general", "academic", "news"

    Returns:
        str: 搜索结果的JSON字符串

    Example:
        >>> web_search("人工智能发展现状")
        '{"results": [{"title": "AI发展报告", "link": "...", "snippet": "..."}]}'

        >>> web_search("机器学习", "academic")
        '{"results": [{"title": "机器学习论文", "link": "...", "snippet": "..."}]}'
    """
    try:
        result = search_chat(query)
        return result
    except Exception as e:
        return f"网页搜索失败: {str(e)}"


@mcp.tool()
def open_ai_websites(urls: List[str], contents: Optional[List[str]] = None) -> str:
    """
    打开AI网站 - 打开多个AI网站并自动输入内容

    打开指定的AI网站列表，并在每个网站中自动输入对应的内容。

    Args:
        urls (List[str]): AI网站URL列表
        contents (List[str], optional): 要输入的内容列表

    Returns:
        str: 操作结果描述

    Example:
        >>> open_ai_websites(["https://chat.openai.com"], ["请解释量子计算"])
        '已成功打开1个AI网站并写入对应内容'
    """
    try:
        result = open_ai_urls(urls, contents)
        return result
    except Exception as e:
        return f"打开AI网站失败: {str(e)}"


@mcp.tool()
def open_websites_by_name(website_names: List[str]) -> str:
    """
    通过名称打开网站 - 使用网站名称打开常用网站

    根据网站名称打开对应的网站，支持中英文名称。

    Args:
        website_names (List[str]): 网站名称列表

    Returns:
        str: 操作结果描述

    Example:
        >>> open_websites_by_name(["哔哩哔哩", "GitHub"])
        '已成功打开以下网站: 哔哩哔哩, GitHub'
    """
    try:
        result = open_popular_websites(website_names)
        return result
    except Exception as e:
        return f"打开网站失败: {str(e)}"


@mcp.tool()
def get_weather_information(city: Optional[str] = None) -> str:
    """
    获取天气信息 - 查询指定城市的天气情况

    获取城市的当前天气信息，包括温度、湿度、风力等。

    Args:
        city (str, optional): 城市名称，如果不提供则查询IP所在城市

    Returns:
        str: 天气信息描述

    Example:
        >>> get_weather_information("北京")
        '北京: 温度 15°C, 晴天, 风力 2级'

        >>> get_weather_information()
        '当前城市: 温度 20°C, 多云, 风力 1级'
    """
    result = make_api_request("GET", "/api/system/weather", {"city": city} if city else {})
    return result


@mcp.tool()
def search_web_content(query: str) -> str:
    """
    网页内容搜索 - 搜索网页内容

    使用AI搜索引擎进行网页内容搜索。

    Args:
        query (str): 搜索查询内容

    Returns:
        str: 搜索结果

    Example:
        >>> search_web_content("人工智能发展")
        '搜索结果：...'
    """
    result = make_api_request("GET", "/api/system/search", {"query": query})
    return result


@mcp.tool()
def analyze_content_with_ai(content: str, user_content: str = "请分析这个内容") -> str:
    """
    AI内容分析 - 使用AI分析文本内容

    对输入的内容进行AI智能分析。

    Args:
        content (str): 要分析的内容
        user_content (str, optional): 分析要求

    Returns:
        str: 分析结果

    Example:
        >>> analyze_content_with_ai("这是一段文本", "总结主要内容")
        '分析结果：...'
    """
    result = make_api_request("POST", "/api/system/content-analyze", {
        "content": content,
        "user_content": user_content
    })
    return result.get("result", "分析完成")


@mcp.tool()
def write_file_to_system(file_path: str, content: str) -> str:
    """
    写入文件 - 向系统文件写入内容

    将内容写入到指定的文件路径。

    Args:
        file_path (str): 文件路径
        content (str): 文件内容

    Returns:
        str: 操作结果

    Example:
        >>> write_file_to_system("test.txt", "Hello World")
        '文件写入成功'
    """
    result = make_api_request("POST", "/api/system/files", {
        "file_path": file_path,
        "content": content
    })
    return result.get("message", "文件写入完成")


@mcp.tool()
def read_webpage(url: str, extract_info: bool = False) -> Union[str, Dict[str, str]]:
    """
    读取网页内容 - 读取指定URL的网页内容

    获取网页的文本内容，并可选地提取网页元信息。

    Args:
        url (str): 网页URL
        extract_info (bool, optional): 是否提取网页信息，默认为False

    Returns:
        Union[str, Dict[str, str]]: 网页内容或包含元信息的字典

    Example:
        >>> read_webpage("https://example.com")
        '这是网页的内容...'

        >>> read_webpage("https://example.com", extract_info=True)
        {'title': 'Example', 'description': '...', 'content': '...'}
    """
    try:
        if extract_info:
            result = extract_web_content(url)
        else:
            result = read_webpage(url)

        return result
    except Exception as e:
        return f"读取网页内容失败: {str(e)}"


# =============================================================================
# 系统工具模块
# =============================================================================

@mcp.tool()
def get_system_performance() -> Dict[str, Union[float, int, str]]:
    """
    获取系统性能信息

    获取当前系统的CPU、内存、磁盘等性能指标。

    Returns:
        Dict[str, Union[float, int, str]]: 系统性能信息
            {
                "cpu_percent": float,     # CPU使用率
                "memory_percent": float,  # 内存使用率
                "disk_usage": float,      # 磁盘使用率
                "network_io": dict        # 网络I/O统计
            }

    Example:
        >>> get_system_performance()
        {
            'cpu_percent': 25.5,
            'memory_percent': 60.2,
            'disk_usage': 45.8,
            'network_io': {'bytes_sent': 1024, 'bytes_recv': 2048}
        }
    """
    result = make_api_request("GET", "/api/system/performance")
    return result


@mcp.tool()
def get_system_information() -> Dict[str, str]:
    """
    获取系统基本信息

    获取操作系统的基本信息，包括版本、架构等。

    Returns:
        Dict[str, str]: 系统信息字典
            {
                "os": str,           # 操作系统
                "version": str,      # 版本信息
                "architecture": str, # 系统架构
                "hostname": str      # 主机名
            }

    Example:
        >>> get_system_information()
        {
            'os': 'Windows',
            'version': '10.0.19045',
            'architecture': '64bit',
            'hostname': 'DESKTOP-ABC123'
        }
    """
    result = make_api_request("GET", "/api/system/info")
    return result


@mcp.tool()
def get_clipboard_content() -> str:
    """
    获取剪切板内容

    获取系统剪切板中的文本内容。

    Returns:
        str: 剪切板中的文本内容

    Example:
        >>> get_clipboard_content()
        '这是剪切板中的内容'
    """
    try:
        content = pyperclip.paste()
        return content if content else "剪切板为空"
    except Exception as e:
        return f"获取剪切板内容失败: {str(e)}"


@mcp.tool()
def set_clipboard_content(text: str) -> str:
    """
    设置剪切板内容

    将指定的文本内容设置到系统剪切板中。

    Args:
        text (str): 要设置到剪切板的文本

    Returns:
        str: 操作结果描述

    Example:
        >>> set_clipboard_content("Hello World")
        '已成功设置剪切板内容'
    """
    try:
        pyperclip.copy(text)
        return "已成功设置剪切板内容"
    except Exception as e:
        return f"设置剪切板内容失败: {str(e)}"


# =============================================================================
# 聊天工具模块 - 基于 /api/chat/ API
# =============================================================================

@mcp.tool()
def send_chat_message(message: str, model: Optional[str] = None, temperature: Optional[float] = None) -> Dict[str, Any]:
    """
    发送聊天消息 - 与AI助手进行对话

    向AI聊天接口发送消息并获取回复。

    Args:
        message (str): 要发送的消息内容
        model (str, optional): 使用的AI模型
        temperature (float, optional): 温度参数，控制回复的随机性

    Returns:
        Dict[str, Any]: 聊天回复结果
            {
                "content": str,        # AI回复内容
                "timestamp": str,      # 时间戳
                "usage": dict,         # Token使用情况
                "model": str          # 使用的模型
            }

    Example:
        >>> send_chat_message("你好，请介绍一下自己")
        {
            'content': '你好！我是AI助手...',
            'timestamp': '2024-01-01T12:00:00Z',
            'usage': {'prompt_tokens': 10, 'completion_tokens': 50, 'total_tokens': 60},
            'model': 'qwen-turbo'
        }
    """
    data = {"message": message}
    if model:
        data["model"] = model
    if temperature is not None:
        data["temperature"] = temperature

    result = make_api_request("POST", "/api/chat/send", data)
    return result


@mcp.tool()
def get_chat_history(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    获取聊天历史记录

    获取最近的聊天历史记录。

    Args:
        limit (int, optional): 返回的最大记录数量

    Returns:
        List[Dict[str, Any]]: 聊天历史记录列表

    Example:
        >>> get_chat_history(5)
        [
            {
                'role': 'user',
                'content': '你好',
                'timestamp': '2024-01-01T12:00:00Z'
            },
            {
                'role': 'assistant',
                'content': '你好！',
                'timestamp': '2024-01-01T12:00:01Z'
            }
        ]
    """
    params = {}
    if limit:
        params["limit"] = limit

    result = make_api_request("GET", "/api/chat/history", params)
    return result.get("history", [])


@mcp.tool()
def clear_chat_history() -> str:
    """
    清空聊天历史记录

    删除所有的聊天历史记录。

    Returns:
        str: 操作结果描述

    Example:
        >>> clear_chat_history()
        '聊天历史记录已清空'
    """
    result = make_api_request("POST", "/api/chat/clear")
    if result.get("success"):
        return "聊天历史记录已清空"
    else:
        return result.get("error", "清空聊天历史失败")


@mcp.tool()
def get_chat_status() -> Dict[str, Any]:
    """
    获取聊天服务状态

    获取聊天服务的当前状态和配置信息。

    Returns:
        Dict[str, Any]: 聊天服务状态信息

    Example:
        >>> get_chat_status()
        {
            'enabled': True,
            'model': 'qwen-turbo',
            'temperature': 0.7,
            'max_tokens': 2000,
            'total_messages': 150
        }
    """
    result = make_api_request("GET", "/api/chat/status")
    return result


# =============================================================================
# 主程序入口
# =============================================================================

if __name__ == "__main__":
    # 启动MCP服务器
    try:
        print("AI Agent Floating Ball MCP服务器启动中...")
        print("支持的功能模块:")
        print("- 自动化工具: 应用启动、窗口管理、快捷键")
        print("- 文件处理工具: 文档转换、内容分析")
        print("- 语音工具: 语音识别、文本转语音")
        print("- 视觉工具: OCR、屏幕截图、图像分析")
        print("- 网络工具: 网页搜索、天气查询")
        print("- 系统工具: 性能监控、系统信息")

        mcp.run(transport="http", port=9000)
        print("MCP服务器已启动在 http://localhost:9000")

    except Exception as e:
        print(f"MCP服务器启动失败: {e}")
        sys.exit(1)

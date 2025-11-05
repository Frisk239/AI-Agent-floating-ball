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
    keys: Optional[List[str]] = None  # ["ctrl", "c"] 或 ["win", "r"] (可选)
    actions: Optional[List[str]] = None  # ["copy", "paste"] 等操作名称 (可选)


class FolderCreateRequest(BaseModel):
    folder_names: List[str]
    base_path: Optional[str] = None


class ClipboardContent(BaseModel):
    content: str


class AppLaunchRequest(BaseModel):
    app_name: str


class BatchTextAnalysisRequest(BaseModel):
    texts: List[str]
    analysis_type: str = "总结"


class BatchAppLaunchRequest(BaseModel):
    app_names: List[str]


class DocumentAnalyzeRequest(BaseModel):
    user_content: str = "请总结这个文档的主要内容"
    file_path: Optional[str] = None


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


@router.post("/windows/activate/{pid}")
async def activate_window(pid: int):
    """
    激活指定进程ID的窗口 - 简化接口（兼容老项目）

    - **pid**: 进程ID
    """
    try:
        from ..services.automation.window_service import activate_window_simple

        result = activate_window_simple(pid)
        return AutomationResponse(
            success="成功" in result,
            message=result,
            result={"pid": pid}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"激活窗口失败: {str(e)}")


@router.post("/windows/switch/{index}")
async def switch_to_window(index: int):
    """
    切换到指定索引的窗口（基于历史记录）

    - **index**: 窗口索引，0表示当前窗口，1表示上一个窗口，以此类推
    """
    try:
        from ..services.automation.window_service import switch_to_window_by_index

        result = switch_to_window_by_index(index)
        return AutomationResponse(
            success="成功" in result,
            message=result,
            result={"index": index}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切换窗口失败: {str(e)}")


@router.post("/windows/find")
async def find_and_activate_window_endpoint(
    search_term: str,
    search_type: str = "title"
):
    """
    根据搜索条件查找并激活窗口

    - **search_term**: 搜索关键词
    - **search_type**: 搜索类型，"title"表示按标题搜索，"process"表示按进程名搜索
    """
    try:
        from ..services.automation.window_service import find_and_activate_window

        result = find_and_activate_window(search_term, search_type)
        return AutomationResponse(
            success="成功" in result,
            message=result,
            result={"search_term": search_term, "search_type": search_type}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查找并激活窗口失败: {str(e)}")


@router.get("/windows/all")
async def get_all_windows():
    """获取系统中所有可见窗口的详细信息列表"""
    try:
        from ..services.automation.window_service import get_window_list_detailed

        windows = get_window_list_detailed()
        return {"windows": windows, "count": len(windows)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取窗口列表失败: {str(e)}")


@router.post("/windows/{pid}/minimize")
async def minimize_window(pid: int):
    """
    最小化指定PID的窗口

    - **pid**: 进程ID
    """
    try:
        from ..services.automation.window_service import minimize_window_by_pid

        success = minimize_window_by_pid(pid)
        return AutomationResponse(
            success=success,
            message=f"窗口最小化{'成功' if success else '失败'}",
            result={"pid": pid, "action": "minimize"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"最小化窗口失败: {str(e)}")


@router.post("/windows/{pid}/maximize")
async def maximize_window(pid: int):
    """
    最大化指定PID的窗口

    - **pid**: 进程ID
    """
    try:
        from ..services.automation.window_service import maximize_window_by_pid

        success = maximize_window_by_pid(pid)
        return AutomationResponse(
            success=success,
            message=f"窗口最大化{'成功' if success else '失败'}",
            result={"pid": pid, "action": "maximize"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"最大化窗口失败: {str(e)}")


@router.post("/windows/{pid}/close")
async def close_window(pid: int):
    """
    关闭指定PID的窗口

    - **pid**: 进程ID
    """
    try:
        from ..services.automation.window_service import close_window_by_pid

        success = close_window_by_pid(pid)
        return AutomationResponse(
            success=success,
            message=f"窗口关闭{'成功' if success else '失败'}",
            result={"pid": pid, "action": "close"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"关闭窗口失败: {str(e)}")


@router.post("/web/open-ai-sites")
async def open_ai_sites(
    urls: list,
    user_contents: list = None
):
    """
    打开指定的AI网站列表，并将对应的用户内容粘贴到各个网站中

    - **urls**: 要打开的AI网站URL地址列表
    - **user_contents**: 需要粘贴到网站中的文本内容列表（可选）
    """
    try:
        from ..services.web.search import open_ai_urls

        result = open_ai_urls(urls, user_contents)
        return AutomationResponse(
            success="成功" in result,
            message=result,
            result={"urls": urls, "contents_provided": user_contents is not None}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"打开AI网站失败: {str(e)}")


@router.post("/web/open-popular-sites")
async def open_popular_sites(website_names: list):
    """
    打开常用网站网页，支持同时打开多个流行网站

    - **website_names**: 网站名称列表
    """
    try:
        from ..services.web.search import open_popular_websites

        result = open_popular_websites(website_names)
        return AutomationResponse(
            success="成功" in result,
            message=result,
            result={"websites": website_names}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"打开常用网站失败: {str(e)}")


@router.post("/office/word/edit")
async def edit_word_document(user_content: str):
    """
    对当前活动窗口的Word文档进行AI处理

    - **user_content**: 用户对Word文档的具体操作要求
    """
    try:
        from ..services.file_processing.file_writer import change_word_file

        result = change_word_file(user_content)
        return AutomationResponse(
            success="完成" in result,
            message=result,
            result={"action": "word_edit", "content": user_content}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word文档编辑失败: {str(e)}")


@router.post("/office/excel/edit")
async def edit_excel_document(user_content: str):
    """
    对当前活动窗口的Excel文件进行AI处理

    - **user_content**: 用户对Excel文档的具体操作要求
    """
    try:
        from ..services.file_processing.file_writer import change_excel_file

        result = change_excel_file(user_content)
        return AutomationResponse(
            success="完成" in result,
            message=result,
            result={"action": "excel_edit", "content": user_content}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel文档编辑失败: {str(e)}")


@router.post("/office/analyze")
async def analyze_office_file(request: DocumentAnalyzeRequest):
    """
    读取和分析Office文件内容

    - **user_content**: 用户对文件内容的具体要求
    - **file_path**: Office文件路径（可选，默认使用当前活动窗口的文件）
    """
    try:
        from ..services.file_processing.file_writer import read_office_file

        print(f"🔍 Office分析请求: user_content='{request.user_content}', file_path='{request.file_path}'")

        result = read_office_file(request.file_path, request.user_content)
        return AutomationResponse(
            success="完成" in result or "分析" in result,
            message=result,
            result={"action": "office_analysis", "file_path": request.file_path, "content": request.user_content}
        )

    except Exception as e:
        print(f"❌ Office分析异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Office文件分析失败: {str(e)}")


@router.post("/documents/ppt/analyze")
async def analyze_ppt_file(request: DocumentAnalyzeRequest):
    """
    读取和分析PPT文件内容

    - **user_content**: 用户对PPT内容的具体要求（如总结、提取要点等）
    - **file_path**: PPT文件路径（可选，默认使用当前活动窗口的文件）
    """
    try:
        from ..services.file_processing.file_writer import read_ppt

        print(f"🔍 PPT分析请求: user_content='{request.user_content}', file_path='{request.file_path}'")

        if request.file_path:
            # 如果提供了文件路径，直接使用
            print(f"📁 使用指定文件路径: {request.file_path}")
            result = read_ppt(request.user_content, request.file_path)
        else:
            # 尝试从活动窗口获取文件路径
            print("🔍 尝试从活动窗口获取PPT文件路径")
            result = read_ppt(request.user_content)

        print(f"📄 PPT分析结果: {result[:200]}...")

        return AutomationResponse(
            success="已生成" in result or "完成" in result,
            message=result,
            result={"action": "ppt_analysis", "content": request.user_content, "file_path": request.file_path}
        )

    except Exception as e:
        print(f"❌ PPT分析异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PPT文件分析失败: {str(e)}")


@router.post("/documents/pdf/analyze")
async def analyze_pdf_file(request: DocumentAnalyzeRequest):
    """
    读取和分析PDF文件内容

    - **user_content**: 用户对PDF内容的具体要求（如总结、提取要点等）
    - **file_path**: PDF文件路径（可选，默认使用当前活动窗口的文件）
    """
    try:
        from ..services.file_processing.file_writer import read_pdf

        print(f"🔍 PDF分析请求: user_content='{request.user_content}', file_path='{request.file_path}'")

        if request.file_path:
            # 如果提供了文件路径，直接使用
            print(f"📁 使用指定文件路径: {request.file_path}")
            result = read_pdf(request.user_content, request.file_path)
        else:
            # 尝试从活动窗口获取文件路径
            print("🔍 尝试从活动窗口获取PDF文件路径")
            result = read_pdf(request.user_content)

        print(f"📄 PDF分析结果: {result[:200]}...")

        return AutomationResponse(
            success="已生成" in result or "完成" in result,
            message=result,
            result={"action": "pdf_analysis", "content": request.user_content, "file_path": request.file_path}
        )

    except Exception as e:
        print(f"❌ PDF分析异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF文件分析失败: {str(e)}")


@router.post("/folders/create")
async def create_folders(request: FolderCreateRequest):
    """
    在指定路径或当前活动文件夹路径下创建多个新文件夹

    - **folder_names**: 要创建的文件夹名称列表
    - **base_path**: 基础路径（可选），如果不提供则使用活动窗口路径
    """
    try:
        from ..services.file_processing.file_writer import create_folders_in_directory

        # 如果提供了base_path，使用指定路径；否则使用活动路径
        if request.base_path:
            result = create_folders_in_directory(request.folder_names, request.base_path)
        else:
            # 回退到原有逻辑：使用活动路径
            result = create_folders_in_directory(request.folder_names, None)

        return AutomationResponse(
            success="已成功创建" in result,
            message=result,
            result={
                "action": "create_folders",
                "folder_names": request.folder_names,
                "base_path": request.base_path
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建文件夹失败: {str(e)}")


@router.get("/clipboard")
async def get_clipboard():
    """获取剪切板内容"""
    try:
        from ..services.file_processing.content_analyzer import get_clipboard_content

        content = get_clipboard_content()
        return AutomationResponse(
            success="剪切板中没有文本内容" not in content,
            message="获取剪切板内容成功" if "没有文本内容" not in content else content,
            result={"action": "get_clipboard", "content": content if "没有文本内容" not in content else ""}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取剪切板内容失败: {str(e)}")


@router.post("/clipboard/set")
async def set_clipboard(request: ClipboardContent):
    """
    设置剪切板内容

    - **content**: 要设置到剪切板的内容
    """
    try:
        from ..services.file_processing.content_analyzer import set_clipboard_content

        result = set_clipboard_content(request.content)
        return AutomationResponse(
            success="成功" in result,
            message=result,
            result={"action": "set_clipboard", "length": len(request.content)}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置剪切板内容失败: {str(e)}")


@router.post("/clipboard/analyze")
async def analyze_clipboard(user_content: str = "请分析这个剪切板内容"):
    """
    AI智能分析剪切板内容

    - **user_content**: 对剪切板内容的分析要求
    """
    try:
        from ..services.file_processing.content_analyzer import analyze_clipboard_content

        result = analyze_clipboard_content(user_content)
        return AutomationResponse(
            success="分析完成" in result,
            message=result,
            result={"action": "analyze_clipboard", "analysis_type": user_content}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"剪切板内容分析失败: {str(e)}")


@router.get("/context/info")
async def get_context_info():
    """获取智能上下文感知信息"""
    try:
        from ..services.automation.window_service import get_context_aware_info

        context_info = get_context_aware_info()
        return {
            "context_info": context_info,
            "timestamp": context_info.get('timestamp', 0)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取上下文信息失败: {str(e)}")


@router.get("/context/suggestions")
async def get_context_suggestions():
    """获取基于当前上下文的智能建议"""
    try:
        from ..services.automation.window_service import generate_smart_suggestions, get_context_aware_info

        context_info = get_context_aware_info()
        suggestions = generate_smart_suggestions(context_info)
        return {
            "suggestions": suggestions,
            "context_summary": {
                "active_app": context_info.get('active_window', {}).get('process_name', ''),
                "system_load": context_info.get('system_state', {}),
                "activity_pattern": context_info.get('user_activity', {}).get('activity_time_distribution', '')
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取智能建议失败: {str(e)}")


@router.get("/context/actions")
async def get_adaptive_actions():
    """获取自适应行动建议"""
    try:
        from ..services.automation.window_service import get_adaptive_action_suggestions

        suggestions = get_adaptive_action_suggestions()
        return {
            "adaptive_actions": suggestions,
            "count": len(suggestions)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取自适应行动建议失败: {str(e)}")


@router.get("/context/predict")
async def predict_user_intent_endpoint():
    """预测用户意图"""
    try:
        from ..services.automation.window_service import predict_user_intent

        prediction = predict_user_intent()
        return {
            "prediction": prediction,
            "confidence_level": "high" if prediction.get('confidence', 0) > 0.7 else "medium" if prediction.get('confidence', 0) > 0.5 else "low"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"用户意图预测失败: {str(e)}")


@router.post("/batch/analyze-texts")
async def batch_analyze_texts_endpoint(request: BatchTextAnalysisRequest):
    """
    批量分析多个文本内容

    - **texts**: 要分析的文本内容列表
    - **analysis_type**: 分析类型 (总结/关键词/情感/分类/翻译)
    """
    try:
        from ..services.file_processing.content_analyzer import batch_analyze_texts

        result = batch_analyze_texts(request.texts, request.analysis_type)
        return {
            "batch_analysis_result": result,
            "status": "completed" if result.get('failed_count', 0) == 0 else "partial_success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量文本分析失败: {str(e)}")


@router.post("/batch/generate-content")
async def batch_generate_content_endpoint(
    prompts: list,
    content_type: str = "文章"
):
    """
    批量生成AI内容

    - **prompts**: 内容生成提示列表
    - **content_type**: 内容类型 (文章/代码/邮件/报告/摘要)
    """
    try:
        from ..services.file_processing.content_analyzer import batch_generate_content

        result = batch_generate_content(prompts, content_type)
        return {
            "batch_generation_result": result,
            "status": "completed" if result.get('failed_count', 0) == 0 else "partial_success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量内容生成失败: {str(e)}")


@router.post("/batch/open-urls")
async def batch_open_urls(urls: list):
    """
    批量打开多个URL

    - **urls**: 要打开的URL列表
    """
    try:
        from ..services.web.search import open_urls

        result = open_urls(urls)
        return AutomationResponse(
            success="失败" not in result,
            message=result,
            result={"action": "batch_open_urls", "url_count": len(urls)}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量打开URL失败: {str(e)}")


@router.post("/batch/open-websites")
async def batch_open_websites(website_names: list):
    """
    批量打开常用网站

    - **website_names**: 网站名称列表
    """
    try:
        from ..services.web.search import open_popular_websites

        result = open_popular_websites(website_names)
        return AutomationResponse(
            success="未找到" not in result,
            message=result,
            result={"action": "batch_open_websites", "website_count": len(website_names)}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量打开网站失败: {str(e)}")


@router.post("/batch/launch-apps")
async def batch_launch_apps(request: BatchAppLaunchRequest):
    """
    批量启动应用程序

    - **app_names**: 应用程序名称列表
    """
    try:
        from ..services.automation.app_launcher import open_other_apps

        result = open_other_apps(request.app_names)
        return AutomationResponse(
            success="失败" not in result,
            message=result,
            result={"action": "batch_launch_apps", "app_count": len(request.app_names)}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量启动应用失败: {str(e)}")


@router.post("/batch/execute-shortcuts")
async def batch_execute_shortcuts(actions: list):
    """
    批量执行快捷键操作

    - **actions**: 要执行的快捷键操作名称列表
    """
    try:
        from ..services.automation.keyboard_shortcut_service import windows_shortcut

        result = windows_shortcut(actions)
        return AutomationResponse(
            success="失败" not in result,
            message=result,
            result={"action": "batch_execute_shortcuts", "action_count": len(actions)}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量执行快捷键失败: {str(e)}")


@router.post("/batch/search-websites")
async def batch_search_websites(
    website_names: list,
    search_contents: list
):
    """
    在多个网站中批量搜索内容

    - **website_names**: 网站名称列表
    - **search_contents**: 搜索内容列表
    """
    try:
        from ..services.web.search import search_in_websites

        result = search_in_websites(website_names, search_contents)
        return AutomationResponse(
            success="失败" not in result,
            message=result,
            result={
                "action": "batch_search_websites",
                "website_count": len(website_names),
                "search_count": len(search_contents)
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量网站搜索失败: {str(e)}")


@router.post("/web/control")
async def control_webpage(user_content: str):
    """
    智能网页控制和操作

    - **user_content**: 用户对网页的具体操作要求
    """
    try:
        from ..services.web.web_reader import control_webpage

        result = control_webpage(user_content)
        return AutomationResponse(
            success="完成" in result,
            message=result,
            result={"action": "web_control", "content": user_content}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"网页控制失败: {str(e)}")


@router.post("/web/extract")
async def extract_web_content(
    content_type: str = "text",
    url: str = None
):
    """
    从网页提取指定类型的内容

    - **content_type**: 内容类型 (text/links/images/tables/headers)
    - **url**: 网页URL（可选，默认使用当前活动网页）
    """
    try:
        from ..services.web.web_reader import extract_web_content

        result = extract_web_content(url, content_type)
        return AutomationResponse(
            success="失败" not in result,
            message=result,
            result={"action": "web_extract", "content_type": content_type, "url": url}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"网页内容提取失败: {str(e)}")


@router.post("/web/to-markdown")
async def convert_webpage_to_markdown(url: str = None):
    """
    将网页内容转换为Markdown格式

    - **url**: 网页URL（可选，默认使用当前活动网页）
    """
    try:
        from ..services.web.web_reader import webpage_to_markdown

        result = webpage_to_markdown(url)
        return AutomationResponse(
            success="保存为" in result,
            message=result,
            result={"action": "web_to_markdown", "url": url}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"网页转Markdown失败: {str(e)}")


@router.post("/apps/music/control")
async def control_music_application(actions: list):
    """
    控制音乐播放应用

    - **actions**: 要执行的操作列表
    """
    try:
        from ..services.automation.app_launcher import control_music_app

        result = control_music_app(actions)
        return AutomationResponse(
            success="已成功执行" in result,
            message=result,
            result={"action": "music_control", "operations": actions}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音乐应用控制失败: {str(e)}")


@router.post("/apps/browser/control")
async def control_browser_application(actions: list):
    """
    控制浏览器应用

    - **actions**: 要执行的操作列表
    """
    try:
        from ..services.automation.app_launcher import control_browser_app

        result = control_browser_app(actions)
        return AutomationResponse(
            success="已成功执行" in result,
            message=result,
            result={"action": "browser_control", "operations": actions}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"浏览器控制失败: {str(e)}")


@router.post("/apps/office/control")
async def control_office_application(
    actions: list,
    app_type: str = "word"
):
    """
    控制Office应用

    - **actions**: 要执行的操作列表
    - **app_type**: 应用程序类型 (word/excel/powerpoint)
    """
    try:
        from ..services.automation.app_launcher import control_office_app

        result = control_office_app(actions, app_type)
        return AutomationResponse(
            success="已成功执行" in result,
            message=result,
            result={"action": "office_control", "app_type": app_type, "operations": actions}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Office应用控制失败: {str(e)}")


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
    执行键盘快捷键 - 支持操作名称和按键组合两种方式

    支持两种调用方式：
    1. 操作名称: {"actions": ["copy", "paste"]}
    2. 按键组合: {"keys": ["ctrl", "c"]}

    - **actions**: 快捷键操作名称列表 (可选)
    - **keys**: 按键组合，如 ["ctrl", "c"] 或 ["win", "r"] (可选)

    注意：actions 和 keys 参数不能同时为空
    """
    try:
        from ..services.automation.keyboard_shortcut_service import (
            execute_multiple_shortcuts,
            execute_shortcut_by_keys
        )

        config = get_config()

        if not config.automation.hotkey_enabled:
            raise HTTPException(status_code=400, detail="快捷键功能未启用")

        # 检查是否有额外的actions参数
        actions = getattr(request, 'actions', None)
        keys = request.keys

        # 优先处理actions参数（新功能）
        if actions:
            if not isinstance(actions, list):
                raise HTTPException(status_code=400, detail="actions 必须是字符串列表")

            result = execute_multiple_shortcuts(actions)

            return AutomationResponse(
                success=result["success"],
                message=result["message"],
                result={
                    "method": "actions",
                    "requested_actions": actions,
                    "successful_actions": result.get("successful_actions", []),
                    "failed_actions": result.get("failed_actions", []),
                    "total_requested": result.get("total_requested", 0),
                    "total_successful": result.get("total_successful", 0),
                    "total_failed": result.get("total_failed", 0)
                }
            )

        # 处理keys参数（原有功能）
        elif keys:
            if not isinstance(keys, list):
                raise HTTPException(status_code=400, detail="keys 必须是字符串列表")

            result = execute_shortcut_by_keys(keys)

            return AutomationResponse(
                success=result["success"],
                message=result["message"],
                result={
                    "method": "keys",
                    "keys": keys,
                    "converted_keys": result.get("converted_keys", [])
                }
            )

        else:
            raise HTTPException(status_code=400, detail="必须提供 actions 或 keys 参数中的至少一个")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"快捷键执行失败: {str(e)}")


@router.get("/keyboard/shortcuts", response_model=Dict[str, List[str]])
async def get_available_shortcuts():
    """
    获取所有可用的快捷键操作

    返回按类别分组的所有可用快捷键操作名称
    """
    try:
        from ..services.automation.keyboard_shortcut_service import get_available_shortcuts

        shortcuts = get_available_shortcuts()

        return shortcuts

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取快捷键列表失败: {str(e)}")


@router.get("/keyboard/shortcut/{action}")
async def get_shortcut_info(action: str):
    """
    获取指定快捷键的详细信息

    - **action**: 快捷键操作名称
    """
    try:
        from ..services.automation.keyboard_shortcut_service import get_shortcut_info

        info = get_shortcut_info(action)

        if info is None:
            raise HTTPException(status_code=404, detail=f"未找到快捷键操作: {action}")

        return info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取快捷键信息失败: {str(e)}")


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
async def launch_application(request: AppLaunchRequest):
    """
    启动应用程序 - 智能双重启动策略

    该接口首先尝试使用预定义的应用映射启动应用程序，
    如果失败则使用Windows搜索启动方式来启动应用程序。

    - **app_name**: 应用程序名称，支持：
      - 系统应用: notepad, calculator, explorer, cmd, powershell
      - 浏览器: chrome, edge
      - 开发工具: vscode, word, excel, powerpoint
      - 社交软件: wechat, qq, dingtalk
      - 媒体软件: netease
      - 其他任意已安装应用（通过搜索启动）
    """
    try:
        from ..services.automation.app_launcher import launch_application_smart

        # 使用智能启动器
        result = launch_application_smart(request.app_name)

        if result["success"]:
            return AutomationResponse(
                success=True,
                message=result["message"],
                result={
                    "app_name": request.app_name,
                    "status": "running",
                    "method": result["method"],
                    "command": result.get("command")
                }
            )
        else:
            raise HTTPException(status_code=404, detail=result["message"])

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

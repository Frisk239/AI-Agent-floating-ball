import win32com.client
import time
import win32gui
import win32process
import win32con
import platform
import psutil
import re
import pyperclip
import os
import subprocess
import pyautogui
import uiautomation as auto

# 全局变量：存储最近激活的窗口历史记录（最多保存5个）
window_history = []
MAX_HISTORY_SIZE = 6
# 标记是否已经初始化窗口历史
window_history_initialized = False

def write_and_open_txt(ai_content, file_path="file_summary\\summary.txt"):
    # 将内容写入文件并打开记事本
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(ai_content)
    print(f"内容已写入 {file_path}")

    # 根据不同操作系统打开文件
    system = platform.system()

    if system == "Windows":
        # Windows系统重启记事本并打开文件
        try:
            # 强制终止现有的记事本进程及子进程
            subprocess.run(["taskkill", "/f", "/t", "/im", "notepad.exe"],
                         stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            print("已强制终止现有的记事本进程。")
        except Exception as e:
            print("无法强制终止现有的记事本进程。")

        # 等待一段时间确保进程已结束
        time.sleep(0.5)

        # 启动记事本并打开文件
        subprocess.Popen(["notepad.exe", file_path])
    else:
        print(f"无法自动打开文件，请手动打开: {file_path}")


def get_active_window_title():
    """
    获取当前活动窗口的标题（仅支持Windows）

    Returns:
        str: 活动窗口标题，如果无法获取则返回空字符串
    """
    system = platform.system()
    if system == "Windows":
        try:
            # 获取当前活动窗口句柄
            hwnd = win32gui.GetForegroundWindow()
            # 获取窗口标题
            window_title = win32gui.GetWindowText(hwnd)
            # 获取窗口所属进程ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            return window_title, pid
        except ImportError:
            print("需要安装pywin32库: pip install pywin32")
            return "", None
        except Exception as e:
            print(f"获取活动窗口信息时出错: {e}")
            return "", None
    else:
        print("此功能主要支持Windows系统")
        return "", None

def get_active_window_info():
    """
    获取当前活动窗口的详细信息

    Returns:
        dict: 包含活动窗口信息的字典
    """
    info = {
        'window_title': '',
        'process_name': '',
        'pid': None,
        'timestamp': time.time()  # 添加时间戳用于排序
    }
    window_title, pid = get_active_window_title()
    info['window_title'] = window_title
    info['pid'] = pid

    if pid:
        try:
            process = psutil.Process(pid)
            process_name = process.name().lower()
            info['process_name'] = process_name
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # 如果历史记录已经初始化，则更新历史记录
    global window_history_initialized
    if window_history_initialized:
        update_window_history(info)
    
    return info

def update_window_history(window_info):
    """
    更新窗口激活历史记录
    
    Args:
        window_info: 窗口信息字典
    """
    global window_history
    
    # 创建窗口唯一标识符（标题+进程名+PID）
    window_id = f"{window_info['window_title']}_{window_info['process_name']}_{window_info['pid']}"
    
    # 如果当前窗口已在历史记录中，先移除它
    window_history = [win for win in window_history if 
                     f"{win['window_title']}_{win['process_name']}_{win['pid']}" != window_id]
    
    # 将当前窗口添加到历史记录的最前面（最新）
    window_history.insert(0, window_info.copy())
    
    # 限制历史记录大小
    if len(window_history) > MAX_HISTORY_SIZE:
        window_history = window_history[:MAX_HISTORY_SIZE]

def initialize_window_history():
    """
    初始化窗口历史记录，捕获系统中最近的窗口活动
    尝试通过多种方法获取已存在的窗口历史
    """
    global window_history, window_history_initialized
    window_history = []  # 确保window_history被初始化
    
    try:
        # 方法1：使用EnumWindows枚举所有顶级窗口并按Z-order排序
        windows = []
        
        def callback(hwnd, windows_list):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    try:
                        process = psutil.Process(pid)
                        process_name = process.name().lower()
                        windows_list.append({
                            'hwnd': hwnd,
                            'window_title': title,
                            'process_name': process_name,
                            'pid': pid,
                            'timestamp': time.time()  # 使用当前时间作为时间戳
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        
        # 枚举所有窗口
        win32gui.EnumWindows(callback, windows)
        
        # 按Z-order排序，通常最上面的窗口是最近活动的
        # 这里我们使用一个简单的启发式方法，尝试获取几个最可能最近活动的窗口
        if windows:
            # 首先添加当前活动窗口
            current_window = get_active_window_info()
            if current_window['pid']:
                update_window_history(current_window)
            
            # 添加其他可见窗口，避免重复
            for window in windows:
                window_id = f"{window['window_title']}_{window['process_name']}_{window['pid']}"
                if not any(f"{win['window_title']}_{win['process_name']}_{win['pid']}" == window_id for win in window_history):
                    update_window_history(window)
                if len(window_history) >= MAX_HISTORY_SIZE:
                    break
        
        # 方法2：尝试使用PowerShell获取最近活动的应用程序
        if len(window_history) < MAX_HISTORY_SIZE:
            try:
                # 使用PowerShell命令获取运行中的进程，并按CPU使用率排序（作为活动程度的近似）
                cmd = [
                    "powershell",
                    "-Command",
                    "Get-Process | Where-Object { $_.MainWindowTitle -ne '' } | Sort-Object -Property CPU -Descending | Select-Object -First 10 Name, Id, MainWindowTitle"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=5)
                
                if result.returncode == 0:
                    # 解析PowerShell输出并添加到历史记录
                    lines = result.stdout.strip().split('\n')[3:]  # 跳过标题行
                    for line in lines:
                        if line.strip():
                            parts = re.split(r'\s{2,}', line.strip())
                            if len(parts) >= 3:
                                process_name = parts[0].lower()
                                try:
                                    pid = int(parts[1])
                                    window_title = ' '.join(parts[2:])
                                    
                                    # 检查是否已在历史记录中
                                    window_id = f"{window_title}_{process_name}_{pid}"
                                    if not any(f"{win['window_title']}_{win['process_name']}_{win['pid']}" == window_id for win in window_history):
                                        window_info = {
                                            'window_title': window_title,
                                            'process_name': process_name,
                                            'pid': pid,
                                            'timestamp': time.time()
                                        }
                                        update_window_history(window_info)
                                    if len(window_history) >= MAX_HISTORY_SIZE:
                                        break
                                except ValueError:
                                    continue
            except Exception:
                # 如果PowerShell命令失败，继续尝试其他方法
                pass
        
        # 方法3：尝试使用uiautomation获取顶层窗口
        if len(window_history) < MAX_HISTORY_SIZE:
            try:
                # 获取所有顶级窗口
                root = auto.GetRootControl()
                children = root.GetChildren()
                
                for child in children:
                    try:
                        # 获取窗口信息
                        window_title = child.Name
                        if window_title and len(window_title) > 1:  # 过滤掉空标题和系统窗口
                            # 通过窗口标题查找进程信息
                            hwnd = child.NativeWindowHandle
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            try:
                                process = psutil.Process(pid)
                                process_name = process.name().lower()
                                
                                # 检查是否已在历史记录中
                                window_id = f"{window_title}_{process_name}_{pid}"
                                if not any(f"{win['window_title']}_{win['process_name']}_{win['pid']}" == window_id for win in window_history):
                                    window_info = {
                                        'window_title': window_title,
                                        'process_name': process_name,
                                        'pid': pid,
                                        'timestamp': time.time()
                                    }
                                    update_window_history(window_info)
                                if len(window_history) >= MAX_HISTORY_SIZE:
                                    break
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                    except Exception:
                        continue
            except Exception:
                # 如果uiautomation方法失败，忽略错误
                pass
    
    finally:
        # 确保窗口历史记录已初始化标志设置为True
        window_history_initialized = True

def get_recent_windows_process_info():
    """
    获取最近激活的窗口的进程信息，按时间顺序排列
    1是最后激活的（当前激活窗口），2是之前激活的，以此类推
    
    Returns:
        list: 包含最多MAX_HISTORY_SIZE个窗口进程信息的列表，每个元素是包含'process_name'和'pid'的字典，
              按激活时间从新到旧排序
    """
    global window_history_initialized, window_history
    
    # 如果窗口历史未初始化，先进行初始化
    if not window_history_initialized:
        initialize_window_history()
    
    # 获取当前活动窗口，确保历史记录更新
    current_window = get_active_window_info()
    
    # 确保当前窗口在历史记录的最前面
    current_id = f"{current_window['window_title']}_{current_window['process_name']}_{current_window['pid']}"
    if window_history:
        first_id = f"{window_history[0]['window_title']}_{window_history[0]['process_name']}_{window_history[0]['pid']}"
        
        # 如果当前窗口不是历史记录的第一个，则更新
        if current_id != first_id:
            # 从历史记录中移除当前窗口（如果存在）
            window_history = [win for win in window_history if 
                             f"{win['window_title']}_{win['process_name']}_{win['pid']}" != current_id]
            # 将当前窗口添加到历史记录的最前面
            window_history.insert(0, current_window.copy())
    else:
        # 如果历史记录为空，添加当前窗口
        window_history = [current_window.copy()]
    
    # 提取进程信息列表（包含进程名和PID）
    process_info_list = []
    for window in window_history[:MAX_HISTORY_SIZE]:
        if window and window['process_name']:
            process_info_list.append({
                'process_name': window['process_name'],
                'pid': window['pid']
            })
        else:
            process_info_list.append({'process_name': None, 'pid': None})
    
    # 如果进程信息列表不足MAX_HISTORY_SIZE个，用None填充
    while len(process_info_list) < MAX_HISTORY_SIZE:
        process_info_list.append({'process_name': None, 'pid': None})
    
    return process_info_list[:MAX_HISTORY_SIZE]  # 只返回最多MAX_HISTORY_SIZE个

# 保留原函数名作为兼容性封装
def get_recent_five_windows_process_names():
    """
    获取最近激活的五个窗口的进程名，按时间顺序排列（兼容性函数）
    1是最后激活的（当前激活窗口），2是之前激活的，以此类推
    
    Returns:
        list: 包含最多5个窗口进程名的列表，按激活时间从新到旧排序
    """
    process_info_list = get_recent_windows_process_info()
    # 只提取进程名
    return [info['process_name'] for info in process_info_list[:5]]  # 保持原函数只返回前5个

# 移除依赖不存在模块的函数

def get_activate_path():
    """
    获取当前活动窗口的文件路径和内容信息
    Returns:
        dict: 包含文件信息和内容的字典
    """
    # 获取当前活动窗口句柄
    window_title, pid = get_active_window_title()
    info = get_active_window_info()
    print("info", info)

    # 初始化结果字典
    result_file_content = {
        'file_name': '',
        'file_path': '',
        'file_type': '',
        'content': ''
    }

    # 如果当前活动窗口是Word
    if info['process_name']=="winword.exe":
        try:
            # 连接到正在运行的Word实例
            word_app = win32com.client.GetActiveObject("Word.Application")
            # 获取当前活动文档
            if word_app.Documents.Count > 0:
                active_doc = word_app.ActiveDocument
                result_file_content['file_name'] = active_doc.Name
                result_file_content['file_path'] = active_doc.FullName
                result_file_content['file_type'] = "word"
                return result_file_content['file_path']
        except Exception as e:
            print(e)

    # 如果当前活动窗口是Excel
    if info['process_name']=="excel.exe":
        try:
            excel_app = win32com.client.GetActiveObject("Excel.Application")
            if excel_app.Workbooks.Count > 0:
                active_workbook = excel_app.ActiveWorkbook
                result_file_content['file_name'] = active_workbook.Name
                result_file_content['file_path'] = active_workbook.FullName
                result_file_content['file_type'] = "excel"
                result_file_content['content'] = ""
                return result_file_content['file_path']
        except Exception as e:
            print(e)

    # 如果当前活动窗口是PowerPoint
    if info['process_name']=="powerpnt.exe":
        try:
            powerpoint_app = win32com.client.GetActiveObject("PowerPoint.Application")
            if powerpoint_app.Presentations.Count > 0:
                active_presentation = powerpoint_app.ActivePresentation
                result_file_content['file_name'] = active_presentation.Name
                result_file_content['file_path'] = active_presentation.FullName
                result_file_content['file_type'] = "ppt"
                result_file_content['content'] = ""
                return result_file_content['file_path']
        except Exception as e:
            print(e)

    # 如果当前活动窗口是pycharm
    if info['process_name']=="pycharm64.exe":
        pass

    # 如果当前活动窗口是explorer.exe
    if info['process_name']=="explorer.exe":
        hwnd = win32gui.GetForegroundWindow()
        print(f"[DEBUG] Explorer窗口检测 - 窗口句柄: {hwnd}, 进程名: {info['process_name']}, PID: {info['pid']}")

        # 返回当前活动的文件夹路径
        # 使用PowerShell获取Explorer窗口的当前路径
        cmd = [
            "powershell",
            "-Command",
            "(New-Object -ComObject Shell.Application).Windows() | "
            "Where-Object { $_.HWND -eq " + str(hwnd) + " } | "
            "Select-Object -ExpandProperty LocationUrl"
        ]

        print(f"[DEBUG] 执行PowerShell命令1: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        print(f"[DEBUG] PowerShell命令1结果 - 返回码: {result.returncode}")
        print(f"[DEBUG] PowerShell命令1输出: '{result.stdout.strip()}'")
        print(f"[DEBUG] PowerShell命令1错误: '{result.stderr.strip()}'")

        if result.returncode == 0 and result.stdout.strip():
            # 处理file://协议路径
            path = result.stdout.strip()
            print(f"[DEBUG] 获取到路径: '{path}'")
            if path.startswith("file:///"):
                # 转换为本地路径格式
                local_path = path[8:].replace("/", "\\")
                print(f"[DEBUG] 转换后路径: '{local_path}'")
                return local_path
            return path

        # 如果上面的方法失败，尝试另一种方法
        cmd2 = [
            "powershell",
            "-Command",
            "(New-Object -ComObject Shell.Application).Windows() | "
            "Where-Object { $_.HWND -eq " + str(hwnd) + " } | "
            "Select-Object -ExpandProperty Document | "
            "Select-Object -ExpandProperty Folder | "
            "Select-Object -ExpandProperty Self | "
            "Select-Object -ExpandProperty Path"
        ]

        print(f"[DEBUG] 执行PowerShell命令2: {' '.join(cmd2)}")
        result2 = subprocess.run(cmd2, capture_output=True, text=True, shell=True)
        print(f"[DEBUG] PowerShell命令2结果 - 返回码: {result2.returncode}")
        print(f"[DEBUG] PowerShell命令2输出: '{result2.stdout.strip()}'")
        print(f"[DEBUG] PowerShell命令2错误: '{result2.stderr.strip()}'")

        if result2.returncode == 0 and result2.stdout.strip():
            path = result2.stdout.strip()
            print(f"[DEBUG] 获取到路径: '{path}'")
            return path
        else:
            print("[DEBUG] 所有PowerShell方法都失败了")

    return ""


def get_activate_path2():
    """
    获取当前活动窗口名
    """
    # 获取当前活动窗口句柄
    window_title, pid = get_active_window_title()
    info = get_active_window_info()
    #print("info", info)
    return info['process_name']

def activate_window_by_pid(pid, max_retries=3):
    """
    根据进程PID激活对应的窗口（增强版，采用多种方法绕过Windows安全限制）
    
    Args:
        pid (int): 进程ID
        max_retries (int): 最大重试次数
        
    Returns:
        bool: 是否成功激活窗口
    """
    import win32api
    import ctypes
    
    # 存储找到的窗口句柄列表（可能有多个窗口）
    target_hwnds = []
    
    # 回调函数：查找指定PID的所有可见窗口
    def enum_windows_callback(hwnd, l_param):
        if win32gui.IsWindowVisible(hwnd):
            # 获取窗口对应的进程ID
            _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
            # 如果进程ID匹配且窗口可见
            if window_pid == l_param:
                # 获取窗口标题，确保不是空窗口
                title = win32gui.GetWindowText(hwnd)
                if title:
                    target_hwnds.append((hwnd, title))
        return True
    
    # 枚举所有窗口查找匹配的PID
    win32gui.EnumWindows(enum_windows_callback, pid)
    
    # 如果找到了窗口
    if target_hwnds:
        # 优先选择主窗口（通常是第一个有标题的窗口）
        target_hwnd, window_title = target_hwnds[0]
        print(f"找到PID为{pid}的窗口，标题: {window_title}")
        
        # 尝试多次激活窗口
        for attempt in range(max_retries):
            try:
                print(f"尝试激活窗口 (第{attempt + 1}/{max_retries}次)")
                
                # 方法1: 使用AttachThreadInput和常规API
                success = _activate_with_attach_thread(target_hwnd)
                if success:
                    print(f"窗口激活成功 (方法1)")
                    return True
                
                # 方法2: 模拟Alt-Tab组合键
                print("尝试方法2: 模拟Alt-Tab组合键")
                success = _activate_with_alt_tab(target_hwnd)
                if success:
                    print(f"窗口激活成功 (方法2)")
                    return True
                
                # 方法3: 使用Windows API直接修改前台窗口
                print("尝试方法3: 使用Windows API直接修改前台窗口")
                success = _activate_with_system_api(target_hwnd)
                if success:
                    print(f"窗口激活成功 (方法3)")
                    return True
                
                # 方法4: 模拟鼠标点击窗口
                print("尝试方法4: 模拟鼠标点击窗口")
                success = _activate_with_mouse_click(target_hwnd)
                if success:
                    print(f"窗口激活成功 (方法4)")
                    return True
                
                # 如果不是最后一次尝试，等待一段时间后重试
                if attempt < max_retries - 1:
                    print("激活失败，等待1秒后重试...")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"激活尝试中出错: {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)
        
        print(f"所有{max_retries}次激活尝试均失败")
        return False
    else:
        print(f"未找到PID为{pid}的可见窗口")
        return False


def _activate_with_attach_thread(hwnd):
    """使用AttachThreadInput方法激活窗口"""
    try:
        import win32api
        
        # 获取当前活动窗口和线程信息
        current_thread_id = win32api.GetCurrentThreadId()
        target_thread_id, _ = win32process.GetWindowThreadProcessId(hwnd)
        
        # 将当前线程附加到目标窗口的线程
        win32process.AttachThreadInput(current_thread_id, target_thread_id, True)
        
        try:
            # 确保窗口可见
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # 设置窗口为最顶层
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0,
                                 win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            
            # 尝试激活窗口
            result = win32gui.SetForegroundWindow(hwnd)
            if result:
                return True
                
            # 如果失败，尝试模拟Alt键
            win32api.keybd_event(0x12, 0, 0, 0)  # Alt键按下
            win32api.keybd_event(0x12, 0, win32con.KEYEVENTF_KEYUP, 0)  # Alt键释放
            time.sleep(0.1)
            
            return win32gui.SetForegroundWindow(hwnd)
            
        finally:
            # 无论成功与否，都要分离线程输入
            win32process.AttachThreadInput(current_thread_id, target_thread_id, False)
            
    except Exception:
        return False


def _activate_with_alt_tab(hwnd):
    """通过模拟Alt-Tab组合键激活窗口"""
    try:
        import win32api
        
        # 模拟Alt键按下
        win32api.keybd_event(0x12, 0, 0, 0)  # Alt键按下
        time.sleep(0.1)
        
        # 尝试激活窗口
        result = win32gui.SetForegroundWindow(hwnd)
        
        # 释放Alt键
        win32api.keybd_event(0x12, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        return result
        
    except Exception:
        return False


def _activate_with_system_api(hwnd):
    """使用系统API直接修改前台窗口"""
    try:
        # 加载user32.dll
        user32 = ctypes.windll.user32
        
        # 获取当前线程ID
        current_thread_id = win32api.GetCurrentThreadId()
        
        # 设置前台窗口
        return user32.SetForegroundWindow(hwnd) != 0
        
    except Exception:
        return False


def _activate_with_mouse_click(hwnd):
    """通过模拟鼠标点击窗口来激活它"""
    try:
        import win32api
        
        # 获取窗口的位置和大小
        rect = win32gui.GetWindowRect(hwnd)
        center_x = (rect[0] + rect[2]) // 2
        center_y = (rect[1] + rect[3]) // 2
        
        # 确保窗口可见
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        # 保存当前鼠标位置
        old_pos = win32api.GetCursorPos()
        
        try:
            # 移动鼠标到窗口中心
            win32api.SetCursorPos((center_x, center_y))
            time.sleep(0.1)
            
            # 模拟鼠标左键按下和释放
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.1)
            
            # 检查窗口是否被激活
            return win32gui.GetForegroundWindow() == hwnd
            
        finally:
            # 恢复鼠标位置
            win32api.SetCursorPos(old_pos)
            
    except Exception:
        return False

def activate_next_window():
    """获取之前一个激活窗口的信息"""
    result = get_recent_windows_process_info()
    #print("当前的窗口信息为：", result[0])
    current_pid = result[0]['pid']
    current_process_name = result[0]['process_name']
    # 将result倒序输出
    #print("之前的窗口信息为：", result[::-1][:-1])
    #print(len(result[::-1][:-1]))
    #if current_process_name == "mcp_agent.exe":
    for info in result[::-1][:-1]:
        if info['pid'] != current_pid and info["process_name"] != "mcp_agent.exe":
            print(info)
            return f"之前窗口软件为：{info['process_name']}，之前窗口的pid为：{info['pid']}。"
            break
    return f"未找到之前激活的窗口。"


def activate_window_simple(pid: int) -> str:
    """
    激活指定进程ID的窗口 - 简化版接口（兼容老项目）

    该函数会将当前活动窗口切换到指定进程ID对应的窗口。如果指定的进程ID
    不存在或无效，则会返回错误信息。

    Args:
        pid (int): 要激活的窗口的进程ID

    Returns:
        str: 操作结果描述，包含激活的窗口的软件名称和进程ID

    Example:
        >>> activate_window_simple(1234)
        '激活窗口软件为：notepad.exe，进程ID为：1234'
    """
    try:
        success = activate_window_by_pid(pid)
        if success:
            current_file_path = get_activate_path()
            file_path_info = f"当前文件路径为：{current_file_path}" if current_file_path else ""
            window_info = get_active_window_info()
            return f"激活窗口软件为：{window_info['process_name']}，进程ID为：{pid}，{file_path_info}。"
        else:
            return f"激活窗口失败：未找到PID为{pid}的窗口或激活失败。"
    except Exception as e:
        return f"激活窗口时出错: {str(e)}"


def switch_to_window_by_index(index: int) -> str:
    """
    切换到指定索引的窗口（基于历史记录）

    Args:
        index (int): 窗口索引，0表示当前窗口，1表示上一个窗口，以此类推

    Returns:
        str: 操作结果描述
    """
    try:
        recent_windows = get_recent_windows_process_info()

        if index < 0 or index >= len(recent_windows):
            return f"无效的窗口索引: {index}，可用索引范围: 0-{len(recent_windows)-1}"

        target_info = recent_windows[index]
        if not target_info['pid']:
            return f"索引{index}处的窗口信息无效"

        success = activate_window_by_pid(target_info['pid'])
        if success:
            return f"成功切换到索引{index}的窗口：{target_info['process_name']} (PID: {target_info['pid']})"
        else:
            return f"切换到索引{index}的窗口失败：{target_info['process_name']} (PID: {target_info['pid']})"

    except Exception as e:
        return f"切换窗口时出错: {str(e)}"


def find_and_activate_window(search_term: str, search_type: str = "title") -> str:
    """
    根据搜索条件查找并激活窗口

    Args:
        search_term (str): 搜索关键词
        search_type (str): 搜索类型，"title"表示按标题搜索，"process"表示按进程名搜索

    Returns:
        str: 操作结果描述
    """
    try:
        import win32gui

        found_windows = []

        def enum_callback(hwnd, l_param):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    try:
                        process = psutil.Process(pid)
                        process_name = process.name().lower()

                        # 根据搜索类型进行匹配
                        if search_type == "title" and search_term.lower() in title.lower():
                            found_windows.append({
                                'hwnd': hwnd,
                                'title': title,
                                'pid': pid,
                                'process_name': process_name
                            })
                        elif search_type == "process" and search_term.lower() in process_name:
                            found_windows.append({
                                'hwnd': hwnd,
                                'title': title,
                                'pid': pid,
                                'process_name': process_name
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            return True

        # 枚举所有窗口
        win32gui.EnumWindows(enum_callback, None)

        if not found_windows:
            return f"未找到包含'{search_term}'的窗口"

        # 激活第一个匹配的窗口
        target_window = found_windows[0]
        success = activate_window_by_pid(target_window['pid'])

        if success:
            return f"成功激活窗口：{target_window['title']} ({target_window['process_name']}, PID: {target_window['pid']})"
        else:
            return f"激活窗口失败：{target_window['title']} ({target_window['process_name']}, PID: {target_window['pid']})"

    except Exception as e:
        return f"查找并激活窗口时出错: {str(e)}"


def get_window_list_detailed() -> list:
    """
    获取系统中所有可见窗口的详细信息列表

    Returns:
        list: 窗口详细信息列表
    """
    try:
        import win32gui

        windows = []

        def enum_callback(hwnd, l_param):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:  # 只包含有标题的窗口
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    try:
                        process = psutil.Process(pid)
                        process_name = process.name().lower()
                        executable = process.exe()

                        # 获取窗口位置和大小
                        rect = win32gui.GetWindowRect(hwnd)

                        windows.append({
                            'hwnd': hwnd,
                            'title': title,
                            'pid': pid,
                            'process_name': process_name,
                            'executable': executable,
                            'rect': {
                                'left': rect[0],
                                'top': rect[1],
                                'right': rect[2],
                                'bottom': rect[3],
                                'width': rect[2] - rect[0],
                                'height': rect[3] - rect[1]
                            }
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        # 对于无法访问的进程，仍添加基本信息
                        rect = win32gui.GetWindowRect(hwnd)
                        windows.append({
                            'hwnd': hwnd,
                            'title': title,
                            'pid': pid,
                            'process_name': 'unknown',
                            'executable': 'unknown',
                            'rect': {
                                'left': rect[0],
                                'top': rect[1],
                                'right': rect[2],
                                'bottom': rect[3],
                                'width': rect[2] - rect[0],
                                'height': rect[3] - rect[1]
                            }
                        })
            return True

        win32gui.EnumWindows(enum_callback, None)

        # 按窗口标题排序
        windows.sort(key=lambda x: x['title'].lower())

        return windows

    except Exception as e:
        print(f"获取窗口列表时出错: {e}")
        return []


def minimize_window_by_pid(pid: int) -> bool:
    """
    最小化指定PID的窗口

    Args:
        pid (int): 进程ID

    Returns:
        bool: 是否成功最小化
    """
    try:
        import win32gui

        def enum_callback(hwnd, target_pid):
            if win32gui.IsWindowVisible(hwnd):
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid == target_pid:
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                    return False  # 找到后停止枚举
            return True

        win32gui.EnumWindows(enum_callback, pid)
        return True

    except Exception as e:
        print(f"最小化窗口时出错: {e}")
        return False


def maximize_window_by_pid(pid: int) -> bool:
    """
    最大化指定PID的窗口

    Args:
        pid (int): 进程ID

    Returns:
        bool: 是否成功最大化
    """
    try:
        import win32gui

        def enum_callback(hwnd, target_pid):
            if win32gui.IsWindowVisible(hwnd):
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid == target_pid:
                    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                    return False  # 找到后停止枚举
            return True

        win32gui.EnumWindows(enum_callback, pid)
        return True

    except Exception as e:
        print(f"最大化窗口时出错: {e}")
        return False


def close_window_by_pid(pid: int) -> bool:
    """
    关闭指定PID的窗口

    Args:
        pid (int): 进程ID

    Returns:
        bool: 是否成功关闭
    """
    try:
        import win32gui

        def enum_callback(hwnd, target_pid):
            if win32gui.IsWindowVisible(hwnd):
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid == target_pid:
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    return False  # 找到后停止枚举
            return True

        win32gui.EnumWindows(enum_callback, pid)
        return True

    except Exception as e:
        print(f"关闭窗口时出错: {e}")
        return False


def get_context_aware_info() -> dict:
    """
    获取智能上下文感知信息

    该函数会自动分析当前系统状态，提供智能的上下文信息，
    包括活动窗口、最近操作、系统状态等，用于智能适配用户操作。

    Returns:
        dict: 包含各种上下文信息的字典
    """
    try:
        context_info = {
            'timestamp': time.time(),
            'active_window': {},
            'recent_windows': [],
            'system_state': {},
            'user_activity': {},
            'smart_suggestions': []
        }

        # 获取活动窗口信息
        active_info = get_active_window_info()
        context_info['active_window'] = {
            'title': active_info['window_title'],
            'process_name': active_info['process_name'],
            'pid': active_info['pid'],
            'file_path': get_activate_path()
        }

        # 获取最近窗口历史
        recent_windows = get_recent_windows_process_info()
        context_info['recent_windows'] = [
            {
                'process_name': win['process_name'],
                'pid': win['pid']
            } for win in recent_windows if win['process_name']
        ]

        # 获取系统状态信息
        context_info['system_state'] = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent
        }

        # 分析用户活动模式
        context_info['user_activity'] = analyze_user_activity_pattern()

        # 生成智能建议
        context_info['smart_suggestions'] = generate_smart_suggestions(context_info)

        return context_info

    except Exception as e:
        print(f"获取上下文信息时出错: {e}")
        return {
            'timestamp': time.time(),
            'error': str(e),
            'active_window': {},
            'recent_windows': [],
            'system_state': {},
            'user_activity': {},
            'smart_suggestions': []
        }


def analyze_user_activity_pattern() -> dict:
    """
    分析用户活动模式

    通过分析窗口切换历史、操作频率等，识别用户的活动模式和偏好。

    Returns:
        dict: 用户活动模式分析结果
    """
    try:
        pattern_info = {
            'most_used_apps': [],
            'activity_time_distribution': {},
            'switching_frequency': 0,
            'preferred_workflows': []
        }

        # 分析最常用的应用程序
        recent_windows = get_recent_windows_process_info()
        app_count = {}

        for win in recent_windows:
            if win['process_name']:
                app_count[win['process_name']] = app_count.get(win['process_name'], 0) + 1

        # 按使用频率排序
        sorted_apps = sorted(app_count.items(), key=lambda x: x[1], reverse=True)
        pattern_info['most_used_apps'] = [app[0] for app in sorted_apps[:5]]

        # 分析活动时间分布（简化版）
        current_hour = time.localtime().tm_hour
        if 9 <= current_hour <= 12:
            pattern_info['activity_time_distribution'] = 'morning_work'
        elif 13 <= current_hour <= 17:
            pattern_info['activity_time_distribution'] = 'afternoon_work'
        elif 18 <= current_hour <= 22:
            pattern_info['activity_time_distribution'] = 'evening_leisure'
        else:
            pattern_info['activity_time_distribution'] = 'night_rest'

        # 计算窗口切换频率（简化版）
        if len(recent_windows) > 1:
            pattern_info['switching_frequency'] = len(recent_windows)

        # 识别偏好的工作流程
        pattern_info['preferred_workflows'] = identify_preferred_workflows(sorted_apps)

        return pattern_info

    except Exception as e:
        print(f"分析用户活动模式时出错: {e}")
        return {}


def identify_preferred_workflows(sorted_apps: list) -> list:
    """
    识别用户偏好的工作流程

    Args:
        sorted_apps: 按使用频率排序的应用程序列表

    Returns:
        list: 识别出的工作流程建议
    """
    workflows = []

    # 基于常用应用组合识别工作流程
    app_names = [app[0] for app in sorted_apps]

    # 开发工作流程
    dev_apps = ['pycharm64.exe', 'code.exe', 'chrome.exe', 'firefox.exe']
    if any(app in app_names for app in dev_apps):
        workflows.append('development')

    # 办公工作流程
    office_apps = ['winword.exe', 'excel.exe', 'powerpnt.exe', 'outlook.exe']
    if any(app in app_names for app in office_apps):
        workflows.append('office_work')

    # 多媒体工作流程
    media_apps = ['vlc.exe', 'mpc-hc64.exe', 'spotify.exe', 'cloudmusic.exe']
    if any(app in app_names for app in media_apps):
        workflows.append('multimedia')

    # 浏览器工作流程
    browser_apps = ['chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe']
    if any(app in app_names for app in browser_apps):
        workflows.append('web_browsing')

    return workflows


def generate_smart_suggestions(context_info: dict) -> list:
    """
    基于上下文信息生成智能建议

    Args:
        context_info: 上下文信息字典

    Returns:
        list: 智能建议列表
    """
    suggestions = []

    try:
        active_window = context_info.get('active_window', {})
        system_state = context_info.get('system_state', {})
        user_activity = context_info.get('user_activity', {})

        # 基于活动窗口的建议
        process_name = active_window.get('process_name', '')
        if process_name:
            if 'winword.exe' in process_name:
                suggestions.append("检测到正在使用Word，可以为您提供文档编辑、格式调整、内容分析等服务")
            elif 'excel.exe' in process_name:
                suggestions.append("检测到正在使用Excel，可以为您提供数据处理、图表生成、公式计算等服务")
            elif 'chrome.exe' in process_name or 'firefox.exe' in process_name:
                suggestions.append("检测到正在使用浏览器，可以为您提供网页内容提取、翻译、总结等服务")
            elif 'code.exe' in process_name or 'pycharm64.exe' in process_name:
                suggestions.append("检测到正在使用代码编辑器，可以为您提供代码解释、优化、重构等服务")

        # 基于系统状态的建议
        memory_percent = system_state.get('memory_percent', 0)
        if memory_percent > 80:
            suggestions.append("系统内存使用率较高，建议关闭不必要的应用程序")

        cpu_percent = system_state.get('cpu_percent', 0)
        if cpu_percent > 80:
            suggestions.append("系统CPU使用率较高，可能影响操作流畅度")

        # 基于用户活动模式的建议
        activity_time = user_activity.get('activity_time_distribution', '')
        if activity_time == 'morning_work':
            suggestions.append("早上好！根据您的使用习惯，现在是高效工作时间")
        elif activity_time == 'evening_leisure':
            suggestions.append("晚上好！您可能正在进行休闲娱乐活动")

        preferred_workflows = user_activity.get('preferred_workflows', [])
        if preferred_workflows:
            workflow_text = "、".join(preferred_workflows)
            suggestions.append(f"检测到您常用的工作流程包括：{workflow_text}")

    except Exception as e:
        print(f"生成智能建议时出错: {e}")

    return suggestions


def get_adaptive_action_suggestions() -> list:
    """
    获取自适应行动建议

    基于当前上下文智能推荐下一步可能的操作。

    Returns:
        list: 行动建议列表
    """
    try:
        context = get_context_aware_info()
        suggestions = []

        active_process = context['active_window'].get('process_name', '')

        # 基于当前活动窗口推荐操作
        if active_process:
            if 'winword.exe' in active_process:
                suggestions.extend([
                    "总结当前Word文档内容",
                    "将文档转换为PDF格式",
                    "检查文档拼写和语法",
                    "提取文档中的关键要点"
                ])
            elif 'excel.exe' in active_process:
                suggestions.extend([
                    "分析当前Excel表格数据",
                    "生成数据可视化图表",
                    "执行数据计算和统计",
                    "导出数据到其他格式"
                ])
            elif 'chrome.exe' in active_process:
                suggestions.extend([
                    "总结当前网页内容",
                    "翻译网页内容",
                    "提取网页中的重要信息",
                    "将网页保存为Markdown"
                ])
            elif 'explorer.exe' in active_process:
                suggestions.extend([
                    "分析当前文件夹结构",
                    "整理文件夹中的文件",
                    "批量重命名文件",
                    "创建新的文件夹组织结构"
                ])

        # 基于系统状态的建议
        system_state = context.get('system_state', {})
        if system_state.get('memory_percent', 0) > 80:
            suggestions.append("清理系统内存，关闭不必要的程序")

        # 基于用户习惯的建议
        user_patterns = context.get('user_activity', {}).get('preferred_workflows', [])
        if 'development' in user_patterns:
            suggestions.append("启动开发环境相关工具")
        elif 'office_work' in user_patterns:
            suggestions.append("准备办公文档处理工具")

        return suggestions[:5]  # 最多返回5个建议

    except Exception as e:
        print(f"获取自适应行动建议时出错: {e}")
        return []


def predict_user_intent() -> dict:
    """
    预测用户意图

    基于历史行为和当前上下文预测用户可能想要执行的操作。

    Returns:
        dict: 预测结果字典
    """
    try:
        context = get_context_aware_info()

        prediction = {
            'predicted_actions': [],
            'confidence': 0.0,
            'reasoning': '',
            'context_factors': []
        }

        active_process = context['active_window'].get('process_name', '')
        recent_apps = [win['process_name'] for win in context['recent_windows'][:3]]

        # 基于当前活动应用预测意图
        if active_process:
            prediction['context_factors'].append(f"当前活动应用: {active_process}")

            if 'winword.exe' in active_process:
                prediction['predicted_actions'] = ['edit_document', 'format_text', 'save_file']
                prediction['confidence'] = 0.8
                prediction['reasoning'] = "用户正在使用Word文档编辑器，可能需要文档编辑相关功能"

            elif 'chrome.exe' in active_process:
                prediction['predicted_actions'] = ['web_search', 'read_content', 'translate_page']
                prediction['confidence'] = 0.7
                prediction['reasoning'] = "用户正在使用浏览器，可能需要网页内容处理功能"

            elif 'explorer.exe' in active_process:
                prediction['predicted_actions'] = ['organize_files', 'create_folder', 'search_files']
                prediction['confidence'] = 0.6
                prediction['reasoning'] = "用户正在使用文件管理器，可能需要文件组织功能"

        # 基于应用切换模式预测
        if len(recent_apps) >= 2:
            prediction['context_factors'].append(f"最近使用的应用: {', '.join(recent_apps[:3])}")

            # 如果频繁在特定应用间切换，可能表示多任务工作
            if len(set(recent_apps)) > 2:
                prediction['predicted_actions'].append('multitask_support')
                prediction['reasoning'] += "；检测到多应用切换模式"

        # 基于时间因素预测
        current_hour = time.localtime().tm_hour
        if 9 <= current_hour <= 12:
            prediction['context_factors'].append("工作时间: 上午")
            prediction['reasoning'] += "；上午工作时间段，适合处理重要任务"
        elif 18 <= current_hour <= 22:
            prediction['context_factors'].append("休闲时间: 晚上")
            prediction['reasoning'] += "；晚上休闲时间段，可能需要娱乐相关功能"

        return prediction

    except Exception as e:
        print(f"预测用户意图时出错: {e}")
        return {
            'predicted_actions': [],
            'confidence': 0.0,
            'reasoning': f'预测失败: {str(e)}',
            'context_factors': []
        }

if __name__ == "__main__":
    print("当前活动窗口名：")
    time.sleep(5)
    # 测试获取最近五个激活窗口的进程名功能
    print("\n测试获取最近五个激活窗口的进程名功能：")
    print("正在获取系统中的最近窗口活动历史...")
    
    # 测试激活窗口功能
    print("\n\n测试根据PID激活窗口功能：")
    # 获取最近的窗口进程信息
    recent_process_info = get_recent_windows_process_info()
    
    if len(recent_process_info) > 1 and recent_process_info[1]['pid']:
        # 获取第二个窗口的PID（即之前激活的窗口）
        previous_pid = recent_process_info[1]['pid']
        previous_name = recent_process_info[1]['process_name']
        print(f"\n准备激活PID为 {previous_pid} 的窗口（进程名：{previous_name}）")
        print("5秒后开始激活操作，请确保有足够权限...")
        time.sleep(5)
        
        success = activate_window_by_pid(previous_pid)
        if success:
            print(f"成功激活PID为 {previous_pid} 的窗口")
        else:
            print(f"激活PID为 {previous_pid} 的窗口失败")
    else:
        print("没有足够的历史窗口信息来测试激活功能")
    
    print("\n测试完成")
    
    # 获取并显示最近的五个激活窗口进程名（兼容旧功能）
    recent_process_names = get_recent_five_windows_process_names()
    
    print("\n最近激活的五个窗口进程名（按时间倒序）：")
    for i, process_name in enumerate(recent_process_names, 1):
        if process_name:
            print(f"{i}. {process_name}")
        else:
            print(f"{i}. 无历史记录")
    
    # 测试新功能：获取包含PID信息的最近窗口进程详情
    print("\n测试获取最近窗口的进程信息（含PID）功能：")
    recent_process_info = get_recent_windows_process_info()
    
    print("\n最近激活的窗口进程信息（按时间倒序）：")
    for i, info in enumerate(recent_process_info, 1):
        if info['process_name']:
            print(f"{i}. 进程名: {info['process_name']}, PID: {info['pid']}")
        else:
            print(f"{i}. 无历史记录")
    
    # 原有的测试代码
    print("\n\n当前活动窗口的文件路径和内容信息：")
    result_file_content = get_activate_path()
    print(result_file_content)

    print("\n当前活动窗口名：")
    time1 = time.time()
    result_file_content = get_activate_path2()
    print(result_file_content)
    print("耗时：", time.time()-time1)

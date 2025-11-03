"""
AI Agent Floating Ball - Keyboard Shortcut Service
键盘快捷键服务 - 支持58+ Windows快捷键操作
"""

import time
import pyautogui
from typing import List, Dict, Any, Tuple, Optional


class KeyboardShortcutService:
    """
    键盘快捷键服务类

    支持Windows系统的常用快捷键操作，包括：
    - 系统相关快捷键
    - 窗口和任务管理
    - 通用编辑和导航
    - 截图和录屏
    - 浏览器/应用常用
    - 辅助功能
    """

    def __init__(self):
        """初始化快捷键服务"""
        self.shortcuts = self._load_shortcuts()
        self.key_map = self._load_key_map()

    def _load_key_map(self) -> Dict[str, str]:
        """加载按键映射"""
        return {
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

    def _load_shortcuts(self) -> Dict[str, Tuple]:
        """加载所有预定义快捷键"""
        return {
            # 系统相关
            'lock_screen': ('win', 'l'),
            'task_manager': ('ctrl', 'shift', 'esc'),
            'switch_user': ('ctrl', 'alt', 'del'),  # 通常会打开安全选项菜单
            'log_off': ('win', 'x'),
            'search_apps': ('win', 'q'),
            'run_dialog': ('win', 'r'),
            'file_explorer': ('win', 'e'),
            'settings': ('win', 'i'),
            'notifications': ('win', 'a'),
            'quick_link_menu': ('win', 'x'),  # Win+X 菜单
            'delete': ('delete',),
            'enter': ('enter',),

            # 窗口和任务管理
            'task_view': ('win', 'tab'),
            'timeline': ('win', 'tab'),  # 在某些版本中与任务视图相同
            'new_virtual_desktop': ('win', 'ctrl', 'd'),
            'close_virtual_desktop': ('win', 'ctrl', 'f4'),
            'switch_desktop_left': ('win', 'ctrl', 'left'),
            'switch_desktop_right': ('win', 'ctrl', 'right'),
            'minimize_all': ('win', 'm'),
            'show_desktop': ('win', 'd'),
            'maximize_window': ('win', 'up'),
            'minimize_window': ('win', 'down'),
            'dock_left': ('win', 'left'),
            'dock_right': ('win', 'right'),

            # 通用编辑和导航
            'copy': ('ctrl', 'c'),
            'cut': ('ctrl', 'x'),
            'paste': ('ctrl', 'v'),
            'paste_special': ('ctrl', 'shift', 'v'),  # 某些应用支持
            'undo': ('ctrl', 'z'),
            'redo': ('ctrl', 'y'),
            'select_all': ('ctrl', 'a'),
            'find': ('ctrl', 'f'),
            'find_next': ('f3',),
            'find_previous': ('shift', 'f3'),
            'replace': ('ctrl', 'h'),
            'refresh': ('f5',),
            'hard_refresh': ('ctrl', 'f5'),

            # 截图和录屏 (部分功能可能需要配合 Snipping Tool/截图工具)
            'screenshot': ('printscreen',),
            'screenshot_active_window': ('alt', 'printscreen'),
            'screenshot_rectangular': ('win', 'shift', 's'),  # Windows 10/11 录屏快捷
            'screen_recording': ('win', 'alt', 'r'),  # Windows 10/11 录屏快捷
            'game_bar': ('win', 'g'),  # Xbox Game Bar

            # 浏览器/应用常用 (通常在应用内有效)
            'new_window': ('ctrl', 'n'),
            'new_tab': ('ctrl', 't'),
            'close_tab': ('ctrl', 'w'),
            'reopen_closed_tab': ('ctrl', 'shift', 't'),
            'next_tab': ('ctrl', 'tab'),
            'previous_tab': ('ctrl', 'shift', 'tab'),
            'open_address_bar': ('ctrl', 'l'),
            'fullscreen': ('f11',),
            'zoom_in': ('ctrl', '+'),
            'zoom_out': ('ctrl', '-'),
            'reset_zoom': ('ctrl', '0'),
            'save': ('ctrl', 's'),

            # 辅助功能
            'narrator': ('win', 'ctrl', 'enter'),
            'magnifier': ('win', '+'),  # 启动并放大
            'magnifier_zoom_in': ('win', '+'),
            'magnifier_zoom_out': ('win', '-'),
            'high_contrast': ('left alt', 'left shift', 'printscreen'),  # 或 Alt+Shift+PrtScn

            # 其他
            'rename': ('f2',),  # 在文件资源管理器中重命名
            'properties': ('alt', 'enter'),  # 或 Ctrl+Shift+Esc 打开任务管理器后选中进程按此
        }

    def execute_shortcut_by_name(self, action: str) -> Dict[str, Any]:
        """
        通过操作名称执行快捷键

        Args:
            action (str): 快捷键操作名称

        Returns:
            Dict[str, Any]: 执行结果
        """
        if action not in self.shortcuts:
            return {
                "success": False,
                "message": f"不支持的操作: '{action}'",
                "action": action
            }

        try:
            keys = self.shortcuts[action]
            pyautogui.hotkey(*keys)
            return {
                "success": True,
                "message": f"快捷键 {action} 执行成功",
                "action": action,
                "keys": list(keys)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"执行快捷键 {action} 时出错: {str(e)}",
                "action": action
            }

    def execute_shortcut_by_keys(self, keys: List[str]) -> Dict[str, Any]:
        """
        通过按键组合执行快捷键

        Args:
            keys (List[str]): 按键列表

        Returns:
            Dict[str, Any]: 执行结果
        """
        try:
            # 转换按键名称
            converted_keys = []
            for key in keys:
                key_lower = key.lower()
                if key_lower in self.key_map:
                    converted_keys.append(self.key_map[key_lower])
                else:
                    # 单个字符直接使用
                    converted_keys.append(key)

            # 执行快捷键
            if len(converted_keys) == 1:
                pyautogui.press(converted_keys[0])
            elif len(converted_keys) == 2:
                pyautogui.hotkey(converted_keys[0], converted_keys[1])
            elif len(converted_keys) == 3:
                pyautogui.hotkey(converted_keys[0], converted_keys[1], converted_keys[2])
            elif len(converted_keys) == 4:
                pyautogui.hotkey(converted_keys[0], converted_keys[1], converted_keys[2], converted_keys[3])
            else:
                return {
                    "success": False,
                    "message": "最多支持4个按键的组合",
                    "keys": keys
                }

            shortcut_name = "+".join(keys).upper()
            return {
                "success": True,
                "message": f"快捷键 {shortcut_name} 执行成功",
                "keys": keys,
                "converted_keys": converted_keys
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"执行快捷键时出错: {str(e)}",
                "keys": keys
            }

    def execute_multiple_shortcuts(self, actions: List[str]) -> Dict[str, Any]:
        """
        批量执行多个快捷键操作

        Args:
            actions (List[str]): 快捷键操作名称列表

        Returns:
            Dict[str, Any]: 批量执行结果
        """
        if not isinstance(actions, list):
            return {
                "success": False,
                "message": "参数错误：actions 必须是一个操作名称列表"
            }

        successful_actions = []
        failed_actions = []

        # 处理需要连续按键的特殊情况
        def handle_special_action(action):
            try:
                if action == 'log_off':
                    pyautogui.hotkey('win', 'x')
                    time.sleep(0.2)
                    pyautogui.press('u')
                    time.sleep(0.2)
                    pyautogui.press('o')
                    return True, f"已执行: {action} (通过 Win+X -> U -> O)"
                elif action == 'shutdown':
                    pyautogui.hotkey('win', 'x')
                    time.sleep(0.2)
                    pyautogui.press('u')
                    time.sleep(0.2)
                    pyautogui.press('u')
                    return True, f"已执行: {action} (通过 Win+X -> U -> U)"
                return False, ""
            except Exception as e:
                return False, f"执行 '{action}' 时出错: {e}"

        # 遍历所有请求的操作
        for action in actions:
            # 处理特殊操作
            is_special, special_result = handle_special_action(action)
            if is_special:
                if "出错" not in special_result:
                    successful_actions.append(action)
                else:
                    failed_actions.append(f"{action}({special_result})")
                continue

            # 检查请求的操作是否受支持
            if action not in self.shortcuts:
                failed_actions.append(f"{action}(不支持的操作: '{action}')")
                continue

            # 执行标准快捷键
            try:
                keys = self.shortcuts[action]
                pyautogui.hotkey(*keys)
                successful_actions.append(action)
            except Exception as e:
                failed_actions.append(f"{action}(执行 '{action}' 时出错: {e})")

        # 等待所有操作执行完成
        if successful_actions:
            time.sleep(len(successful_actions) * 0.1)  # 根据执行操作数量调整等待时间

        # 构造返回信息
        result_message = ""
        if successful_actions:
            result_message += f"已成功执行以下操作: {', '.join(successful_actions)}。"
        if failed_actions:
            if successful_actions:
                result_message += f" 部分操作执行失败: {', '.join(failed_actions)}。"
            else:
                result_message += f"操作执行失败: {', '.join(failed_actions)}。"

        if not successful_actions and not failed_actions:
            result_message = "没有指定要执行的操作。"

        return {
            "success": len(successful_actions) > 0,
            "message": result_message,
            "successful_actions": successful_actions,
            "failed_actions": failed_actions,
            "total_requested": len(actions),
            "total_successful": len(successful_actions),
            "total_failed": len(failed_actions)
        }

    def get_available_shortcuts(self) -> Dict[str, List[str]]:
        """
        获取所有可用的快捷键操作

        Returns:
            Dict[str, List[str]]: 按类别分组的快捷键列表
        """
        categories = {
            "系统相关": [
                'lock_screen', 'task_manager', 'switch_user', 'log_off',
                'search_apps', 'run_dialog', 'file_explorer', 'settings',
                'notifications', 'quick_link_menu', 'delete', 'enter'
            ],
            "窗口和任务管理": [
                'task_view', 'timeline', 'new_virtual_desktop', 'close_virtual_desktop',
                'switch_desktop_left', 'switch_desktop_right', 'minimize_all',
                'show_desktop', 'maximize_window', 'minimize_window', 'dock_left', 'dock_right'
            ],
            "通用编辑和导航": [
                'copy', 'cut', 'paste', 'paste_special', 'undo', 'redo',
                'select_all', 'find', 'find_next', 'find_previous', 'replace',
                'refresh', 'hard_refresh'
            ],
            "截图和录屏": [
                'screenshot', 'screenshot_active_window', 'screenshot_rectangular',
                'screen_recording', 'game_bar'
            ],
            "浏览器/应用常用": [
                'new_window', 'new_tab', 'close_tab', 'reopen_closed_tab',
                'next_tab', 'previous_tab', 'open_address_bar', 'fullscreen',
                'zoom_in', 'zoom_out', 'reset_zoom', 'save'
            ],
            "辅助功能": [
                'narrator', 'magnifier', 'magnifier_zoom_in', 'magnifier_zoom_out',
                'high_contrast'
            ],
            "其他": [
                'rename', 'properties'
            ]
        }

        return categories

    def get_shortcut_info(self, action: str) -> Optional[Dict[str, Any]]:
        """
        获取指定快捷键的详细信息

        Args:
            action (str): 快捷键操作名称

        Returns:
            Optional[Dict[str, Any]]: 快捷键信息，包含按键组合和描述
        """
        if action not in self.shortcuts:
            return None

        keys = self.shortcuts[action]
        key_names = [key.upper() for key in keys]

        # 快捷键描述映射
        descriptions = {
            'lock_screen': '锁定屏幕 (Win+L)',
            'task_manager': '打开任务管理器 (Ctrl+Shift+Esc)',
            'copy': '复制 (Ctrl+C)',
            'paste': '粘贴 (Ctrl+V)',
            'cut': '剪切 (Ctrl+X)',
            'select_all': '全选 (Ctrl+A)',
            'undo': '撤销 (Ctrl+Z)',
            'redo': '重做 (Ctrl+Y)',
            'find': '查找 (Ctrl+F)',
            'save': '保存 (Ctrl+S)',
            'new_tab': '新建标签页 (Ctrl+T)',
            'close_tab': '关闭标签页 (Ctrl+W)',
            'screenshot': '全屏截图 (PrintScreen)',
            'screenshot_rectangular': '矩形截图 (Win+Shift+S)',
            'show_desktop': '显示桌面 (Win+D)',
            'task_view': '任务视图 (Win+Tab)',
            'file_explorer': '文件资源管理器 (Win+E)',
            'settings': '设置 (Win+I)',
            'search_apps': '搜索应用 (Win+Q)',
            'run_dialog': '运行对话框 (Win+R)',
            # 可以继续添加更多描述...
        }

        return {
            "action": action,
            "keys": list(keys),
            "key_names": key_names,
            "shortcut": "+".join(key_names),
            "description": descriptions.get(action, f"{action} 快捷键")
        }


# 创建全局服务实例
keyboard_shortcut_service = KeyboardShortcutService()


def execute_shortcut_by_name(action: str) -> Dict[str, Any]:
    """
    通过操作名称执行快捷键 (便捷函数)

    Args:
        action (str): 快捷键操作名称

    Returns:
        Dict[str, Any]: 执行结果
    """
    return keyboard_shortcut_service.execute_shortcut_by_name(action)


def execute_shortcut_by_keys(keys: List[str]) -> Dict[str, Any]:
    """
    通过按键组合执行快捷键 (便捷函数)

    Args:
        keys (List[str]): 按键列表

    Returns:
        Dict[str, Any]: 执行结果
    """
    return keyboard_shortcut_service.execute_shortcut_by_keys(keys)


def execute_multiple_shortcuts(actions: List[str]) -> Dict[str, Any]:
    """
    批量执行多个快捷键操作 (便捷函数)

    Args:
        actions (List[str]): 快捷键操作名称列表

    Returns:
        Dict[str, Any]: 批量执行结果
    """
    return keyboard_shortcut_service.execute_multiple_shortcuts(actions)


def get_available_shortcuts() -> Dict[str, List[str]]:
    """
    获取所有可用的快捷键操作 (便捷函数)

    Returns:
        Dict[str, List[str]]: 按类别分组的快捷键列表
    """
    return keyboard_shortcut_service.get_available_shortcuts()


def get_shortcut_info(action: str) -> Optional[Dict[str, Any]]:
    """
    获取指定快捷键的详细信息 (便捷函数)

    Args:
        action (str): 快捷键操作名称

    Returns:
        Optional[Dict[str, Any]]: 快捷键信息
    """
    return keyboard_shortcut_service.get_shortcut_info(action)

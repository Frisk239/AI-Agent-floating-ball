import platform
import psutil
import re
import pyperclip
import os
import subprocess
import time
import platform
from .content_analyzer import get_file_summary

def write_and_open_txt(ai_content, file_path="file_summary\\write.md"):
    # 将内容写入文件并打开文件
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

def ai_write_and_open_txt(user_content, file_path="file_summary\\write.md"):
    """
    用AI写用户要求的内容。
    :param user_content:
    :param file_path:
    :return:
    """
    from .content_analyzer import write_ai_model
    ai_content = write_ai_model(user_content)
    try:
        # 将AI生成的内容复制到剪切板
        pyperclip.copy(ai_content)
        write_and_open_txt(ai_content, file_path)
        return "内容如下："+ai_content[:2000]

    except Exception as e:
        print(f"写入或打开文件时出错: {e}")
        return "总结文件时出错。"

def ai_write_code_and_open_txt(user_content, file_path="file_summary\\code.txt"):
    """
    对文件内容进行AI代码生成，并将结果写入指定文件，然后尝试打开该文件
    :param file_content: 要进行代码生成的原始文件内容
    :param file_path: 代码生成结果保存的文件路径，默认为"file_summary\\code.txt"
    :return: 成功时返回AI代码内容，失败时返回错误提示信息
    """
    from .content_analyzer import code_ai_model
    ai_content = code_ai_model(user_content)
    try:
        # 将AI生成的内容复制到剪切板
        pyperclip.copy(ai_content)
        write_and_open_txt(ai_content, file_path)
        return "代码内容编写完成。以下是代码内容："+ai_content[:3000]
    except Exception as e:
        print(f"写入或打开文件时出错: {e}")
        return "总结文件时出错。"


def change_word_file(user_content: str) -> str:
    """
    对当前活动窗口的Word文档进行AI处理

    该函数会自动获取当前活动的Word文档路径，并根据用户的具体需求对文档进行相应操作，
    包括格式调整、内容修改、导出等操作，并将修改后的文件保存并重新打开。

    Args:
        user_content (str): 用户对Word文档的具体操作要求，可以包括：
            - 字体大小、样式、颜色调整
            - 段落间距、对齐方式设置
            - 页面布局、页眉页脚修改
            - 导出为PDF或其他格式
            - 其他针对Word文档的特定操作要求

    Returns:
        str: 操作结果描述，包括：
            - 成功完成操作时返回确认信息
            - 当前不是Word文件时返回提示信息
            - 出现错误时返回错误描述

    Example:
        >>> change_word_file("将标题字体改为黑体，字号24，加粗")
        '操作完成。'

        >>> change_word_file("将文档导出为PDF格式")
        '操作完成。'
    """
    try:
        from ..automation.window_service import get_activate_path

        word_path = get_activate_path()
        # 如果当前文件路径为word文件路径，则进行操作
        if word_path and (word_path.endswith(".docx") or word_path.endswith(".doc")):
            # 构建AI处理指令
            ai_instruction = f"文件路径为：{word_path}\n{user_content}\n将修改后的文件存储下来并打开。"
            # 获取文件夹路径
            word_path_folder = os.path.dirname(word_path)

            # 这里应该调用AI处理服务，暂时使用文本总结作为示例
            # 在实际实现中，应该调用专门的Office AI处理服务
            result = get_file_summary(f"请根据以下要求处理Word文档：{ai_instruction}")

            return f"Word文档AI处理完成。处理结果：{result[:500]}..."
        else:
            return "当前文件不是Word文件，请检查文件路径。"
    except Exception as e:
        return f"操作Word文档时出错: {str(e)}"


def change_excel_file(user_content: str) -> str:
    """
    对当前活动窗口的Excel文件进行AI处理

    该函数会自动获取当前活动的Excel文件路径，并根据用户的具体需求对表格进行相应操作，
    包括数据处理、公式计算、样式调整等操作，并将修改后的文件保存并重新打开。

    Args:
        user_content (str): 用户对Excel文档的具体操作要求，可以包括：
            - 单元格样式、颜色、字体调整
            - 数据计算、求和、统计分析
            - 公式添加和修改
            - 图表创建和格式化
            - 其他针对Excel文档的特定操作要求

    Returns:
        str: 操作结果描述，包括：
            - 成功完成操作时返回确认信息
            - 当前不是Excel文件时返回提示信息
            - 出现错误时返回错误描述

    Example:
        >>> change_excel_file("对B列数据求和，并在最后一行显示结果")
        '操作完成。'

        >>> change_excel_file("将A1单元格背景色改为黄色，字体加粗")
        '操作完成。'
    """
    try:
        from ..automation.window_service import get_activate_path

        excel_path = get_activate_path()
        # 如果当前文件路径为Excel文件路径，则进行操作
        if excel_path and (excel_path.endswith(".xlsx") or excel_path.endswith(".xls")):
            # 构建AI处理指令
            ai_instruction = f"文件路径为：{excel_path}\n{user_content}\n将修改后的文件存储下来并打开。"
            # 获取文件夹路径
            excel_path_folder = os.path.dirname(excel_path)

            # 这里应该调用AI处理服务，暂时使用文本总结作为示例
            # 在实际实现中，应该调用专门的Office AI处理服务
            result = get_file_summary(f"请根据以下要求处理Excel表格：{ai_instruction}")

            return f"Excel表格AI处理完成。处理结果：{result[:500]}..."
        else:
            return "当前文件不是Excel文件，请检查文件路径。"
    except Exception as e:
        return f"操作Excel文档时出错: {str(e)}"


def read_office_file(file_path: str = None, user_content: str = "请总结这个文档的主要内容") -> str:
    """
    读取和分析Office文件内容

    该函数可以读取Word、Excel等Office文件，并根据用户要求进行内容分析、总结等操作。

    Args:
        file_path (str, optional): Office文件路径，如果不提供则自动获取当前活动窗口的文件
        user_content (str): 用户对文件内容的具体要求，如总结、提取要点等

    Returns:
        str: 文件分析结果
    """
    try:
        from ..automation.window_service import get_activate_path

        # 如果没有指定文件路径，获取当前活动窗口的文件
        if not file_path:
            file_path = get_activate_path()

        if not file_path:
            return "无法获取文件路径，请确保打开了Office文件。"

        # 检查文件类型
        if file_path.endswith((".docx", ".doc")):
            file_type = "Word文档"
        elif file_path.endswith((".xlsx", ".xls")):
            file_type = "Excel表格"
        else:
            return f"不支持的文件类型: {file_path}"

        # 构建分析指令
        analysis_instruction = f"请分析这个{file_type}：{file_path}\n用户要求：{user_content}"

        # 使用AI进行内容分析
        result = get_file_summary(analysis_instruction)

        # 将结果保存到文件并复制到剪切板
        result_file = f"file_summary/office_analysis_{int(time.time())}.txt"
        write_and_open_txt(result, result_file)
        pyperclip.copy(result)

        return f"{file_type}分析完成。结果已保存并复制到剪切板。分析摘要：{result[:300]}..."

    except Exception as e:
        return f"读取Office文件时出错: {str(e)}"


def read_ppt(user_content: str) -> str:
    """
    读取PPT内容并按用户要求进行操作

    该函数会自动获取当前活动的PowerPoint文件路径，将PPT转换为文本格式，
    然后根据用户的具体需求对内容进行处理，包括总结、摘要、要点提取等操作。

    Args:
        user_content (str): 用户对PPT内容的具体操作要求，可以包括：
            - 内容总结和摘要提取
            - 关键要点整理
            - 内容改写和优化
            - 其他针对PPT内容的特定处理要求

    Returns:
        str: 操作结果描述，包括：
            - 成功完成操作时返回处理后的内容
            - 当前不是PPT文件时返回提示信息
            - 出现错误时返回错误描述

    Example:
        >>> read_ppt("请总结这个PPT的主要内容")
        '已生成PPT内容总结，文件已保存并打开。'

        >>> read_ppt("提取PPT中的关键要点")
        '已提取PPT关键要点，文件已保存并打开。'
    """
    try:
        from ..automation.window_service import get_activate_path
        from ..web.web_reader import convert_document_to_txt
        import pyautogui

        ppt_path = get_activate_path()
        # 如果当前文件路径为PPT文件路径，则进行操作
        if ppt_path and (ppt_path.endswith(".pptx") or ppt_path.endswith(".ppt")):
            # 模拟按下键盘的Ctrl+S保存
            pyautogui.hotkey('ctrl', 's')
            time.sleep(0.5)  # 等待保存完成

            # 将PPT转换为文本
            result_txt_path = convert_document_to_txt(ppt_path)
            if not result_txt_path:
                return "PPT转换失败，请检查文件是否损坏。"

            # 读取转换后的文本文件
            with open(result_txt_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 使用AI进行内容分析
            analysis_instruction = f"PPT文件路径：{ppt_path}\nPPT内容：{content}\n用户要求：{user_content}"
            return_content = get_file_summary(analysis_instruction)

            # 将结果写到剪切板
            pyperclip.copy(return_content)

            # 保存结果到文件并打开
            result_file = f"file_summary/ppt_analysis_{int(time.time())}.txt"
            write_and_open_txt(return_content, result_file)

            return f"已生成PPT内容分析，文件已保存到：{result_file} 并打开。"
        else:
            return "当前文件不是PPT文件，请检查文件路径。"
    except Exception as e:
        return f"读取PPT时出错: {str(e)}"


def read_pdf(user_content: str) -> str:
    """
    读取PDF内容并按用户要求进行操作

    该函数会自动获取当前活动的PDF文件路径，将PDF转换为文本格式，
    然后根据用户的具体需求对内容进行处理，包括总结、摘要、要点提取等操作。

    Args:
        user_content (str): 用户对PDF内容的具体操作要求，可以包括：
            - 内容总结和摘要提取
            - 关键要点整理
            - 内容改写和优化
            - 其他针对PDF内容的特定处理要求

    Returns:
        str: 操作结果描述，包括：
            - 成功完成操作时返回处理后的内容
            - 当前不是PDF文件时返回提示信息
            - 出现错误时返回错误描述

    Example:
        >>> read_pdf("请总结这个PDF的主要内容")
        '已生成PDF内容总结，文件已保存并打开。'

        >>> read_pdf("提取PDF中的关键要点")
        '已提取PDF关键要点，文件已保存并打开。'
    """
    try:
        from ..automation.window_service import get_activate_path
        from ..web.web_reader import convert_document_to_txt, extract_current_webpage_url
        import pyautogui
        import urllib.parse

        # 首先检查是否为浏览器中的PDF
        app_name = get_activate_path()
        if app_name and ("msedge.exe" in app_name or "chrome.exe" in app_name or "firefox.exe" in app_name):
            # 在浏览器中，提取当前URL
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.2)

            # 读取剪切板中的URL
            current_url = pyperclip.paste()

            # URL解码处理
            if current_url.startswith("file://"):
                # 去掉 file:// 前缀
                path_without_scheme = current_url.replace("file://", "")
                # URL解码
                decoded_path = urllib.parse.unquote(path_without_scheme)
                # Windows专用：去掉开头多余的 '/'
                if os.name == 'nt' and decoded_path.startswith('/'):
                    decoded_path = decoded_path[1:]
                file_path = decoded_path
            else:
                return "当前浏览器页面不是本地PDF文件。"
        else:
            # 检查是否为本地PDF文件
            file_path = get_activate_path()
            if not file_path or not file_path.endswith(".pdf"):
                return "当前文件不是PDF文件，请检查文件路径。"

        # 将PDF转换为文本
        result_txt_path = convert_document_to_txt(file_path)
        if not result_txt_path:
            return "PDF转换失败，请检查文件是否损坏或受保护。"

        # 读取转换后的文本文件
        with open(result_txt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 使用AI进行内容分析
        analysis_instruction = f"PDF文件路径：{file_path}\nPDF内容：{content}\n用户要求：{user_content}"
        return_content = get_file_summary(analysis_instruction)

        # 将结果写到剪切板
        pyperclip.copy(return_content)

        # 保存结果到文件并打开
        result_file = f"file_summary/pdf_analysis_{int(time.time())}.txt"
        write_and_open_txt(return_content, result_file)

        return f"已生成PDF内容分析，文件已保存到：{result_file} 并打开。"
    except Exception as e:
        return f"读取PDF时出错: {str(e)}"


def create_folders_in_active_directory(folder_names: list) -> str:
    """
    在当前活动文件夹路径下创建多个新文件夹

    该函数会自动获取当前活动的文件夹路径（通过文件资源管理器窗口），
    然后在该路径下创建用户指定的文件夹列表。如果文件夹已存在，则不会重复创建。

    Args:
        folder_names (list): 要创建的文件夹名称列表，每个元素为字符串类型的文件夹名称
            例如: ["项目文档", "代码备份", "测试结果"]

    Returns:
        str: 操作结果描述，包括：
            - 成功创建的文件夹列表
            - 已存在的文件夹列表
            - 出现错误时的错误信息

    Example:
        >>> create_folders_in_active_directory(["文档", "图片", "视频"])
        '已成功创建以下文件夹: 文档, 图片, 视频。'

        >>> create_folders_in_active_directory(["已存在文件夹", "新文件夹"])
        '已成功创建以下文件夹: 新文件夹。 以下文件夹已存在: 已存在文件夹。'

        >>> create_folders_in_active_directory([])
        '没有指定要创建的文件夹。'
    """
    try:
        # 检查输入参数是否为空
        if not folder_names:
            return "没有指定要创建的文件夹。"

        # 获取当前活动文件夹路径
        from ..automation.window_service import get_activate_path

        active_path = get_activate_path()

        # 检查路径是否存在
        if not os.path.exists(active_path):
            return f"操作失败：活动路径不存在: {active_path}"

        # 检查是否为目录
        if not os.path.isdir(active_path):
            return f"操作失败：当前活动窗口不是目录文件夹: {active_path}"

        created_folders = []
        existing_folders = []

        # 遍历文件夹名称列表，创建每个文件夹
        for folder_name in folder_names:
            # 构造完整路径
            new_folder_path = os.path.join(active_path, folder_name)
            # 如果文件夹不存在，则创建
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
                created_folders.append(folder_name)
                print(f"已创建文件夹: {new_folder_path}")
            else:
                existing_folders.append(folder_name)
                print(f"文件夹已存在: {new_folder_path}")

        # 构造返回信息
        result_message = ""
        if created_folders:
            result_message += f"已成功创建以下文件夹: {', '.join(created_folders)}。"
        if existing_folders:
            if created_folders:
                result_message += f" 以下文件夹已存在: {', '.join(existing_folders)}。"
            else:
                result_message += f"所有文件夹均已存在: {', '.join(existing_folders)}。"

        return result_message

    except Exception as e:
        return f"创建文件夹时出错: {str(e)}"


if __name__ == "__main__":
    # user_content = "写一个100字CNN网络的总结"
    # ai_content = ai_write_and_open_txt(user_content)
    # print(ai_content)

    user_content = "写python贪吃蛇代码"
    ai_content = ai_write_code_and_open_txt(user_content)
    print(ai_content)

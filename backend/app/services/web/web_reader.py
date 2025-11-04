import pygetwindow as gw
import pyautogui
import pyperclip
import time
import http.client
import json
import os
from dotenv import load_dotenv

load_dotenv()  # 默认会加载根目录下的.env文件

def extract_current_webpage_url():
    """
    提取当前显示网页的URL

    Returns:
        str: 当前网页的URL，如果失败则返回None
    """
    try:
        # 查找活动的浏览器窗口
        active_window = gw.getActiveWindow()
        print(f"活动窗口: {active_window}")

        if not active_window:
            print("没有找到活动窗口")
            return None

        window_title = active_window.title
        print(f"窗口标题: {window_title}")

        # 检查是否为浏览器窗口
        browser_indicators = ['Chrome', 'Firefox', 'Edge', 'Safari', 'Browser']
        is_browser = any(indicator in window_title for indicator in browser_indicators)
        print(f"是否为浏览器: {is_browser}")

        if not is_browser:
            print("当前窗口不是浏览器")
            return None

        # 激活窗口
        active_window.activate()
        time.sleep(0.3)

        # 复制URL (Ctrl+L 选中地址栏，然后 Ctrl+C 复制)
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.2)

        # 获取剪贴板内容
        url = pyperclip.paste()
        print(f"复制的URL: {url}")

        # 验证是否为有效的URL
        if url and (url.startswith('http://') or url.startswith('https://')):
            return url
        else:
            print("URL格式无效")
            return None

    except Exception as e:
        print(f"提取URL时出错: {e}")
        return None

def read_webpage():
    url = extract_current_webpage_url()
    print(f"提取到的URL: {url}")

    if url is None:
        return "无法获取当前浏览器URL，请确保浏览器窗口处于活动状态"

    try:
        conn = http.client.HTTPSConnection("metaso.cn")
        payload = json.dumps({"url": url})
        headers = {
            'Authorization': 'Bearer '+os.getenv("METASO_API_KEY"),
            'Accept': 'text/plain',
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/api/v1/reader", payload, headers)
        res = conn.getresponse()
        data = res.read()
        return data.decode("utf-8")
    except Exception as e:
        return f"网页读取失败: {str(e)}"


import os
import comtypes.client
from PyPDF2 import PdfReader
import pythoncom
import re


def ppt_to_pdf(ppt_path, pdf_path=None):
    """
    将PPT文件转换为PDF文件
    参数:
    ppt_path: PPT文件路径
    pdf_path: PDF文件保存路径（可选，默认与PPT同名）
    返回:
    转换后的PDF文件路径
    """
    # 如果没有指定PDF路径，则使用PPT文件名替换扩展名为.pdf
    if pdf_path is None:
        pdf_path = os.path.splitext(ppt_path)[0] + '.pdf'
    # 初始化COM组件
    pythoncom.CoInitialize()
    try:
        # 创建PowerPoint应用程序对象
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        powerpoint.Visible = 1
        # 打开PPT文件
        presentation = powerpoint.Presentations.Open(ppt_path)
        # 保存为PDF格式
        presentation.SaveAs(pdf_path, 32)  # 32表示PDF格式
        # 关闭演示文稿和PowerPoint应用
        presentation.Close()
        powerpoint.Quit()
        print(f"PPT已成功转换为PDF: {pdf_path}")
        return pdf_path

    except Exception as e:
        print(f"转换过程中出现错误: {e}")
        return None
    finally:
        # 清理COM组件
        pythoncom.CoUninitialize()


def pdf_to_txt(pdf_path, txt_path=None):
    """
    从PDF文件中提取文本并保存为TXT文件
    参数:
    pdf_path: PDF文件路径
    txt_path: TXT文件保存路径（可选，默认与PDF同名）
    返回:
    生成的TXT文件路径
    """
    # 如果没有指定TXT路径，则使用PDF文件名替换扩展名为.txt
    if txt_path is None:
        txt_path = os.path.splitext(pdf_path)[0] + '.txt'
    try:
        # 创建PDF阅读器对象
        reader = PdfReader(pdf_path)
        # 提取所有页面的文本
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text() + "\n"
        # 将文本写入TXT文件
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        print(f"PDF文本已成功提取到TXT文件: {txt_path}")
        return txt_path
    except Exception as e:
        print(f"提取文本时出现错误: {e}")
        return None


def get_unique_filename(base_path):
    """
    获取唯一的文件名，如果文件已存在则在文件名后添加数字
    参数:
    base_path: 基础文件路径
    返回:
    唯一的文件路径
    """
    if not os.path.exists(base_path):
        return base_path
    directory = os.path.dirname(base_path)
    filename = os.path.basename(base_path)
    name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_filename = f"{name}{counter}{ext}"
        new_path = os.path.join(directory, new_filename)
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def convert_document_to_txt(file_path):
    """
    将文档文件转换为TXT文件
    参数:
    file_path: PPT或PDF文件路径
    返回:
    生成的TXT文件路径
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误：找不到文件 {file_path}")
        return None
    # 获取文件扩展名
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    # 获取文件所在目录
    directory = os.path.dirname(file_path) or '.'
    base_name = os.path.splitext(os.path.basename(file_path))[0]

    if ext == '.ppt' or ext == '.pptx':
        # 处理PPT文件
        # 生成PDF文件路径
        pdf_path = os.path.join(directory, base_name + '.pdf')
        pdf_path = get_unique_filename(pdf_path)
        # 将PPT转换为PDF
        pdf_result = ppt_to_pdf(file_path, pdf_path)
        if not pdf_result:
            return None
        # 生成TXT文件路径
        txt_path = os.path.join(directory, base_name + '.txt')
        txt_path = get_unique_filename(txt_path)
        # 将PDF转换为TXT
        txt_result = pdf_to_txt(pdf_result, txt_path)
        return txt_result

    elif ext == '.pdf':
        # 处理PDF文件
        # 生成TXT文件路径
        txt_path = os.path.join(directory, base_name + '.txt')
        txt_path = get_unique_filename(txt_path)
        # 将PDF转换为TXT
        txt_result = pdf_to_txt(file_path, txt_path)
        return txt_result

    else:
        print(f"不支持的文件格式: {ext}")
        return None


def control_webpage(user_content: str) -> str:
    """
    智能网页控制和操作

    该函数可以对当前活动的网页进行各种操作，如内容提取、格式转换、信息整理、文本爬取、图片爬取、视频爬取等功能。
    函数会自动获取当前网页的URL，并结合用户的具体需求进行相应处理。

    Args:
        user_content (str): 用户对网页的具体操作要求，可以包括：
            - 网页内容提取和整理
            - 网页信息分析和总结
            - 网页数据导出和格式转换
            - 网页元素操作和交互
            - 其他针对网页的特定操作要求

    Returns:
        str: 操作结果描述，包括：
            - 成功完成操作时返回确认信息
            - 出现错误时返回错误描述

    Example:
        >>> control_webpage("提取网页中的关键信息并整理成报告")
        '网页操作完成，已生成内容报告。'

        >>> control_webpage("将网页内容转换为Markdown格式")
        '网页操作完成，已转换为Markdown格式。'

        >>> control_webpage("下载网页中的所有图片")
        '网页操作完成，已下载图片到指定文件夹。'
    """
    try:
        # 获取当前网页URL
        web_url = extract_current_webpage_url()
        if not web_url:
            return "无法获取当前网页URL，请确保浏览器窗口处于活动状态。"

        # 构建AI处理指令
        ai_instruction = f"当前网页URL：{web_url}\n用户要求：{user_content}\n请根据用户要求对该网页进行相应操作。可以选择用python脚本实现，将生成的文件存储到桌面上的一个文件夹中并打开该文件夹。"

        # 使用AI进行网页操作分析
        from ..file_processing.content_analyzer import get_file_summary
        result = get_file_summary(ai_instruction)

        # 将结果保存到文件并复制到剪切板
        import pyperclip
        pyperclip.copy(result)

        # 保存结果到文件
        result_file = f"web_control_result_{int(time.time())}.txt"
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"网页URL: {web_url}\n操作要求: {user_content}\n\n处理结果:\n{result}")

        return f"网页操作完成。结果已保存到文件：{result_file} 并复制到剪切板。"

    except Exception as e:
        return f"网页控制操作失败: {str(e)}"


def extract_web_content(url: str = None, content_type: str = "text") -> str:
    """
    从网页提取指定类型的内容

    Args:
        url (str, optional): 网页URL，如果不提供则获取当前活动网页
        content_type (str): 内容类型，可选值：
            - "text": 提取文本内容
            - "links": 提取所有链接
            - "images": 提取图片链接
            - "tables": 提取表格数据
            - "headers": 提取标题结构

    Returns:
        str: 提取的内容结果
    """
    try:
        if not url:
            url = extract_current_webpage_url()
            if not url:
                return "无法获取网页URL"

        # 使用read_webpage获取网页内容
        webpage_content = read_webpage()
        if not webpage_content:
            return "无法读取网页内容"

        # 根据内容类型进行处理
        if content_type == "text":
            # 提取纯文本内容
            result = get_file_summary(f"请从以下网页内容中提取纯文本，不包含HTML标签和脚本：{webpage_content}")
        elif content_type == "links":
            # 提取链接
            result = get_file_summary(f"请从以下网页内容中提取所有链接（URLs），列出链接文本和URL：{webpage_content}")
        elif content_type == "images":
            # 提取图片链接
            result = get_file_summary(f"请从以下网页内容中提取所有图片链接：{webpage_content}")
        elif content_type == "tables":
            # 提取表格数据
            result = get_file_summary(f"请从以下网页内容中提取表格数据，整理成结构化的格式：{webpage_content}")
        elif content_type == "headers":
            # 提取标题结构
            result = get_file_summary(f"请从以下网页内容中提取标题结构（H1-H6标签），整理成层级结构：{webpage_content}")
        else:
            result = f"不支持的内容类型: {content_type}"

        return result

    except Exception as e:
        return f"内容提取失败: {str(e)}"


def webpage_to_markdown(url: str = None) -> str:
    """
    将网页内容转换为Markdown格式

    Args:
        url (str, optional): 网页URL，如果不提供则获取当前活动网页

    Returns:
        str: Markdown格式的内容
    """
    try:
        if not url:
            url = extract_current_webpage_url()
            if not url:
                return "无法获取网页URL"

        webpage_content = read_webpage()
        if not webpage_content:
            return "无法读取网页内容"

        # 转换为Markdown
        markdown_content = get_file_summary(f"请将以下HTML网页内容转换为Markdown格式，保持结构和链接：{webpage_content}")

        # 保存为文件
        filename = f"webpage_{int(time.time())}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {url}\n\n{markdown_content}")

        return f"网页已转换为Markdown格式，保存为：{filename}"

    except Exception as e:
        return f"转换失败: {str(e)}"


# 使用示例
if __name__ == "__main__":
    print("5秒后")
    time.sleep(5)
    print(read_webpage())

import http.client
import json
import webbrowser
import os
import time
import pyperclip
import pyautogui
from dotenv import load_dotenv

load_dotenv()  # 默认会加载根目录下的.env文件

def search_chat2(content: str):
    """

    :param content:
    :return:
    """
    conn = http.client.HTTPSConnection("metaso.cn")
    payload = json.dumps(
        {"q": content, "scope": "webpage", "includeSummary": False, "size": "10", "includeRawContent": True,
         "conciseSnippet": False})
    headers = {
        'Authorization': 'Bearer '+os.getenv("METASO_API_KEY"),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/api/v1/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    #print(data.decode("utf-8"))
    return data.decode("utf-8")

def search_chat(content: str) -> str:
    """
    搜索内容并返回答案，用来搜索

    :param content: 搜索的查询内容
    :return: 搜索结果的答案内容，已清理引用标记
    """
    # 移除TTS调用，在API服务中不需要
    conn = http.client.HTTPSConnection("metaso.cn")
    payload = json.dumps({"q": content, "model": "fast", "format": "simple"})
    headers = {
      'Authorization': 'Bearer '+os.getenv("METASO_API_KEY"),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
    conn.request("POST", "/api/v1/chat/completions", payload, headers)
    res = conn.getresponse()
    data = res.read()

    # 解析JSON响应
    json_data = json.loads(data.decode("utf-8"))

    # 提取answer内容
    if 'answer' in json_data:
        answer_content = json_data['answer']
        # 删除所有类似[[1]]的引用标记
        import re
        cleaned_answer = re.sub(r'\[\[\d+\]\]', '', answer_content)
        # 去除所有换行符
        cleaned_answer = cleaned_answer.replace('\n', '').replace('\r', '')
        # 清理多余的空格
        cleaned_answer = re.sub(r'\s+', ' ', cleaned_answer).strip()
        return cleaned_answer

    else:
        return "没有搜索到相关内容"

def open_webpage(content: str) -> (list, str):
    """
    打开相关网页，用来打开网页

    :param content: 搜索的查询内容
    :return: 包含网页标题和链接的列表
    """
    #realtime_tts_speak("好的，马上打开", rate=25000)
    conn = http.client.HTTPSConnection("metaso.cn")
    payload = json.dumps({"q": content, "scope": "webpage", "includeSummary": True, "size": "5", "includeRawContent": False, "conciseSnippet": False})
    headers = {
      'Authorization': 'Bearer '+os.getenv("METASO_API_KEY"),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
    conn.request("POST", "/api/v1/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    # 解析JSON响应
    json_data = json.loads(data.decode("utf-8"))
    # 提取webpages中的title和link
    titles_and_links = []
    if 'webpages' in json_data and isinstance(json_data['webpages'], list):
        for webpage in json_data['webpages']:
            if 'title' in webpage and 'link' in webpage:
                titles_and_links.append({
                    'title': webpage['title'],
                    'link': webpage['link']
                })
    # 打开网页链接
    for i, item in enumerate(titles_and_links):
        if i < 5:  # 限制打开前5个链接，避免打开过多网页
            webbrowser.open_new(item['link'])
    return titles_and_links, "已打开相关网页"


def open_ai_urls(urls: list, user_contents: list = None) -> str:
    """
    打开指定的AI网站列表，并将对应的用户内容粘贴到各个网站中

    该函数可以同时打开多个AI网站（如豆包、通义千问、DeepSeek、KIMI等），并将对应的文本内容
    自动复制到剪切板并粘贴到每个打开的网页中，方便快速与多个AI进行交互。

    Args:
        urls (list): 要打开的AI网站URL地址列表
        user_contents (list, optional): 需要粘贴到网站中的文本内容列表。
            - 如果提供一个内容列表，将按顺序将不同内容粘贴到对应网站
            - 如果提供单个字符串，将在所有网站中粘贴相同内容
            - 如果不提供或为空，则仅打开网站不粘贴内容
            默认值为None。

    Returns:
        str: 操作结果描述，包括：
            - 成功打开网站并粘贴内容时返回确认信息
            - 出现错误时返回错误描述

    Example:
        >>> open_ai_urls(["https://www.doubao.com/chat/", "https://www.tongyi.com/qianwen"],
                         ["请帮我写一篇关于人工智能的报告", "解释一下量子计算的基本原理"])
        '已成功打开2个AI网站并写入对应内容'

        >>> open_ai_urls(["https://chat.deepseek.com/", "https://www.kimi.com/zh/"],
                         "请分析当前市场趋势")
        '已成功打开2个AI网站并写入相同内容'

        >>> open_ai_urls(["https://www.doubao.com/chat/", "https://www.tongyi.com/qianwen"])
        '已成功打开2个AI网站'

    Supported AI Websites:
        - 豆包AI: https://www.doubao.com/chat/
        - 豆包AI写作: https://www.doubao.com/chat/write
        - 豆包AI生成图像: https://www.doubao.com/chat/create-image
        - 豆包AI编程写代码: https://www.doubao.com/code/chat
        - 豆包AI翻译: https://www.doubao.com/chat/translate
        - 豆包AI智能体: https://www.doubao.com/chat/bot/discover
        - 通义千问AI: https://www.tongyi.com/qianwen
        - 通义千问AIPPT: https://www.tongyi.com/aippt
        - 通义千问AI实时记录，会议记录，语音记录，AI翻译: https://www.tongyi.com/live/
        - 通义千问音频视频速读: https://www.tongyi.com/discover/audioread
        - 通义千问阅读文档，阅读助手: https://www.tongyi.com/read
        - DeepSeek: https://chat.deepseek.com/
        - KIMI: https://www.kimi.com/zh/
        - KIMI生成PPT: https://www.kimi.com/kimiplus/slides
        - KIMI医疗搜索: https://www.kimi.com/kimiplus/cu52bqh7l5gqdkncdg01
    """
    try:
        # 检查输入参数
        if not isinstance(urls, list):
            return "参数错误：urls 必须是一个网址列表"

        if not urls:
            return "错误：urls 列表不能为空"

        # 处理用户内容参数
        contents = []
        content_mode = "none"  # none, single, multiple

        if user_contents is None:
            content_mode = "none"
        elif isinstance(user_contents, str):
            # 单个内容，应用到所有网站
            content_mode = "single"
            contents = [user_contents] * len(urls)
        elif isinstance(user_contents, list):
            if not user_contents:
                content_mode = "none"
            else:
                content_mode = "multiple"
                # 如果内容列表长度小于URL列表，用最后一个内容填充
                contents = user_contents[:]
                if len(contents) < len(urls):
                    contents.extend([contents[-1]] * (len(urls) - len(contents)))
                # 如果内容列表长度大于URL列表，截取前面的部分
                contents = contents[:len(urls)]
        else:
            content_mode = "none"

        # 打开所有网站
        opened_count = 0
        pasted_count = 0

        for i, url in enumerate(urls):
            # 打开网站
            webbrowser.open_new(url)
            opened_count += 1

            # 如果有内容需要粘贴
            if content_mode in ["single", "multiple"] and i < len(contents) and contents[i]:
                # 等待页面加载
                time.sleep(1.5)
                # 复制内容到剪切板
                pyperclip.copy(contents[i])
                # 模拟粘贴操作
                pyautogui.hotkey('ctrl', 'v')
                pasted_count += 1
                # 等待粘贴完成
                time.sleep(0.5)

        # 构造返回信息
        result_msg = f"已成功打开{opened_count}个AI网站"
        if pasted_count > 0:
            if content_mode == "single":
                result_msg += "并写入相同内容"
            else:
                result_msg += "并写入对应内容"
            result_msg += "。若发现未生效，请手动粘贴一下。请手动按回车键确认。"
        else:
            result_msg += "。"

        return result_msg

    except Exception as e:
        return f"打开AI网站时出错: {str(e)}"


def open_popular_websites(website_names: list) -> str:
    """
    打开常用网站网页，支持同时打开多个流行网站

    该函数可以打开用户指定的常用网站列表，包括社交媒体、购物、视频、新闻、开发等各类网站。
    如果未找到对应网站，会尝试通过搜索引擎查找相关内容。

    Args:
        website_names (list): 网站名称或关键词列表，支持以下常用网站：
            社交媒体类: 微博、微信、QQ、Facebook、Twitter、Instagram、LinkedIn
            视频娱乐类: 哔哩哔哩、抖音、快手、YouTube、爱奇艺、腾讯视频、优酷
            购物类: 淘宝、天猫、京东、拼多多、亚马逊、 eBay
            新闻资讯类: 新浪新闻、腾讯新闻、网易新闻、今日头条、知乎、澎湃新闻
            搜索引擎类: 必应、百度、搜狗
            开发技术类: GitHub、CSDN、博客园、StackOverflow、掘金
            学习教育类: 学习通、智慧树、中国大学MOOC、网易云课堂
            办公工具类: 腾讯文档、石墨文档、阿里云盘、百度网盘
            邮箱类: QQ邮箱、网易邮箱、Gmail、Outlook
            其他: 小红书、美团、携程、58同城
            还可以有一些官网，比如北京大学官网

    Returns:
        str: 操作结果描述，包括：
            - 成功打开网站时返回确认信息
            - 未找到对应网站时返回提示信息
            - 出现错误时返回错误描述

    Example:
        >>> open_popular_websites(["哔哩哔哩", "GitHub"])
        '已成功打开以下网站: 哔哩哔哩, GitHub'

        >>> open_popular_websites(["未知网站", "知乎"])
        '已成功打开以下网站: 知乎。未找到以下网站，已通过搜索引擎查找: 未知网站'
    """
    # 常用网站URL映射字典
    websites = {
        # 社交媒体类
        '微博': 'https://weibo.com',
        '微信': 'https://wx.qq.com',
        'qq': 'https://qzone.qq.com',
        'facebook': 'https://www.facebook.com',
        'twitter': 'https://twitter.com',
        'instagram': 'https://www.instagram.com',
        'linkedin': 'https://www.linkedin.com',

        # 视频娱乐类
        '哔哩哔哩': 'https://www.bilibili.com',
        '抖音': 'https://www.douyin.com',
        '快手': 'https://www.kuaishou.com',
        'youtube': 'https://www.youtube.com',
        '爱奇艺': 'https://www.iqiyi.com',
        '腾讯视频': 'https://v.qq.com',
        '优酷': 'https://www.youku.com',

        # 购物类
        '淘宝': 'https://www.taobao.com',
        '天猫': 'https://www.tmall.com',
        '京东': 'https://www.jd.com',
        '拼多多': 'https://www.pinduoduo.com',
        '亚马逊': 'https://www.amazon.com',
        'eBay': 'https://www.ebay.com',

        # 新闻资讯类
        '新浪新闻': 'https://news.sina.com.cn',
        '腾讯新闻': 'https://news.qq.com',
        '网易新闻': 'https://news.163.com',
        '今日头条': 'https://www.toutiao.com',
        '知乎': 'https://www.zhihu.com',
        '澎湃新闻': 'https://www.thepaper.cn',

        # 搜索引擎类
        '百度': 'https://www.baidu.com',
        '谷歌': 'https://www.google.com',
        '必应': 'https://www.bing.com',
        '搜狗': 'https://www.sogou.com',

        # 开发技术类
        'github': 'https://github.com',
        'csdn': 'https://www.csdn.net',
        '博客园': 'https://www.cnblogs.com',
        'stackoverflow': 'https://stackoverflow.com',
        '掘金': 'https://juejin.cn',

        # 学习教育类
        '学习通': 'https://i.chaoxing.com',
        '智慧树': 'https://www.zhihuishu.com',
        '中国大学mooc': 'https://www.icourse163.org',
        '网易云课堂': 'https://study.163.com',

        # 办公工具类
        '腾讯文档': 'https://docs.qq.com',
        '石墨文档': 'https://shimo.im',
        '阿里云盘': 'https://www.aliyundrive.com',
        '百度网盘': 'https://pan.baidu.com',

        # 邮箱类
        'qq邮箱': 'https://mail.qq.com',
        '网易邮箱': 'https://mail.163.com',
        'gmail': 'https://mail.google.com',
        'outlook': 'https://outlook.live.com',

        # 其他
        '小红书': 'https://www.xiaohongshu.com',
        '美团': 'https://www.meituan.com',
        '携程': 'https://www.ctrip.com',
        '58同城': 'https://www.58.com'
    }

    # 确保输入是列表格式
    if not isinstance(website_names, list):
        return "参数错误：website_names 必须是一个网站名称列表"

    # 分别存储成功和失败的网站
    successful_sites = []
    failed_sites = []

    try:
        # 遍历所有请求的网站
        for website_name in website_names:
            # 尝试直接匹配网站
            if website_name in websites:
                url = websites[website_name]
                webbrowser.open_new(url)
                successful_sites.append(website_name)
            else:
                # 尝试模糊匹配（不区分大小写）
                matched_sites = [name for name in websites.keys()
                               if website_name.lower() in name.lower() or
                               name.lower() in website_name.lower()]

                if matched_sites:
                    site_name = matched_sites[0]
                    url = websites[site_name]
                    webbrowser.open_new(url)
                    successful_sites.append(site_name)
                else:
                    # 未找到对应网站，通过搜索引擎搜索
                    search_url = f"https://www.bing.com/search?q={website_name}"
                    webbrowser.open_new(search_url)
                    failed_sites.append(website_name)

        # 构造返回信息
        result_message = ""
        if successful_sites:
            result_message += f"已成功打开以下网站: {', '.join(successful_sites)}。"
        if failed_sites:
            if successful_sites:
                result_message += f" 未找到以下网站，已通过搜索引擎查找: {', '.join(failed_sites)}并已经打开。"
            else:
                result_message += f"未找到以下网站，已通过搜索引擎查找: {', '.join(failed_sites)}并已经打开。"

        if not successful_sites and not failed_sites:
            result_message = "没有指定要打开的网站。"

        return result_message

    except Exception as e:
        return f"打开网站时出错: {str(e)}"


if __name__ == "__main__":
    # results = open_webpage("如何使用python")
    # for item in results:
    #     print(item)
    #     print("-" * 50)
    print(search_chat2("超兽武装"))
    #print(search_chat("如何使用python"))

import os
from openai import OpenAI
import re
from dotenv import load_dotenv

load_dotenv()  # 默认会加载根目录下的.env文件

def get_file_summary(file_content):
    #realtime_tts_speak("正在总结内容", rate=29000)
    if len(file_content) > 80000:
        return "文档长度过长。模型无法总结。"
    elif len(file_content)<6000:
        model='qwen-flash'
    else:
        model='qwen-long'
    try:
        client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        completion = client.chat.completions.create(
            # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            model=model,
            messages=[
                {"role": "system", "content": "你是一个处理长文本的模型，你会将接收的文本进行要点与重点的总结整理与分析，并满足用户的要求。内容总结清晰完整。"},
                {"role": "user", "content": file_content},
            ],
            # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
            # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
            # extra_body={"enable_thinking": False},
        )
        content = completion.choices[0].message.content
        return content
    except Exception as e:
        print(e)
        return "Sorry, I can't summarize this file."


def write_ai_model(user_content):
    try:
        client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        completion = client.chat.completions.create(
            # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            model="qwen-long",
            messages=[
                {"role": "system", "content": "你是一个写作模型，为用户生成文稿，要满足用户要求，文稿长度和结构要结合用户的要求和上下文。"},
                {"role": "user", "content": user_content},
            ],
            # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
            # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
            # extra_body={"enable_thinking": False},
        )
        content = completion.choices[0].message.content
        return content
    except Exception as e:
        print(e)
        return "Sorry, I can't write this file."

def extract_code_blocks(text):
    """
    从文本中提取Markdown格式的代码块
    参数:
        text (str): 包含代码块的文本
    返回:
        list: 包含所有提取的代码块的列表
    """
    # 匹配Markdown代码块的正则表达式模式
    pattern = r'```(?:\w+)?\s*([\s\S]*?)```'
    # 查找所有匹配的代码块
    code_blocks = re.findall(pattern, text, re.MULTILINE)
    # 清理每个代码块（去除首尾空白）
    cleaned_blocks = [block.strip() for block in code_blocks]
    return cleaned_blocks

def code_ai_model(user_content):
    try:
        client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        completion = client.chat.completions.create(
            # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            model="qwen3-coder-flash",
            messages=[
                {"role": "system", "content": "你是代码生成模型，只生成代码，不写除代码外的任何东西，对代码的所有解释都写在代码注释中。"},
                {"role": "user", "content": user_content},
            ],
            # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
            # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
            # extra_body={"enable_thinking": False},
        )
        content = completion.choices[0].message.content
        content = extract_code_blocks(content)
        return content[0]
    except Exception as e:
        print(e)
        return "Sorry, I can't write this file."

def code_ai_explain_model(user_content):
    try:
        client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        completion = client.chat.completions.create(
            # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            model="qwen3-coder-flash",
            messages=[
                {"role": "system", "content": "你是一个讲解代码的模型，对接收到的代码内容进行讲解，讲解细致清晰，清晰条理。用户要求简短时，你的回答要简洁简短，500字左右。用户要求详细时，详细讲解代码。"},
                {"role": "user", "content": user_content},
            ],
            # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
            # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
            # extra_body={"enable_thinking": False},
        )
        content = completion.choices[0].message.content
        # content = extract_code_blocks(content)
        return content
    except Exception as e:
        print(e)
        return "Sorry, I can't write this file."


def analyze_clipboard_content(user_content: str = "请分析这个剪切板内容") -> str:
    """
    智能分析剪切板内容

    该函数获取系统剪切板中的文本内容，并根据用户的要求进行智能分析和处理。
    支持内容分析、格式转换、内容优化等多种AI处理功能。

    Args:
        user_content (str): 用户对剪切板内容的具体处理要求，可以包括：
            - 内容分析和总结
            - 格式转换（如Markdown、HTML等）
            - 内容优化和改写
            - 语言翻译
            - 内容分类和标签
            - 其他AI处理需求

    Returns:
        str: 智能分析结果，包括：
            - 剪切板内容分析结果
            - 处理后的内容
            - 相关建议或优化方案

    Example:
        >>> analyze_clipboard_content("请总结这个文本的主要内容")
        '文本总结：这是一篇关于人工智能发展的文章，主要讨论了...'

        >>> analyze_clipboard_content("将这个文本转换为Markdown格式")
        '# 标题\\n\\n这是转换后的Markdown内容...'

        >>> analyze_clipboard_content("分析这个代码的复杂度")
        '代码复杂度分析：时间复杂度O(n)，空间复杂度O(1)...'
    """
    try:
        import pyperclip

        # 获取剪切板内容
        clipboard_content = pyperclip.paste()

        # 检查剪切板是否为空
        if not clipboard_content or not clipboard_content.strip():
            return "剪切板为空，请先复制一些内容到剪切板中。"

        # 构建AI分析指令
        analysis_instruction = f"""请根据以下用户要求分析剪切板内容：

剪切板内容：
{clipboard_content}

用户要求：
{user_content}

请提供详细的分析结果。"""

        # 使用AI进行内容分析
        result = get_file_summary(analysis_instruction)

        # 将结果复制回剪切板（可选，用户可选择是否替换）
        # pyperclip.copy(result)

        return f"剪切板内容AI分析完成：\\n\\n{result}"

    except ImportError:
        return "剪切板功能需要安装pyperclip库，请运行: pip install pyperclip"
    except Exception as e:
        return f"剪切板内容分析失败: {str(e)}"


def get_clipboard_content() -> str:
    """
    获取剪切板中的内容并返回

    该函数可以读取系统剪切板中的文本内容，并将其返回给用户。
    支持获取用户复制或剪切的文本内容，方便后续处理或查看。

    Returns:
        str: 剪切板中的文本内容，如果剪切板为空或出现错误则返回相应提示信息

    Example:
        >>> get_clipboard_content()
        '这是剪切板中的文本内容'

        >>> get_clipboard_content()
        '剪切板中没有文本内容'
    """
    try:
        import pyperclip

        # 从剪切板获取内容
        clipboard_content = pyperclip.paste()

        # 检查剪切板是否为空
        if clipboard_content:
            return clipboard_content
        else:
            return "剪切板中没有文本内容"
    except ImportError:
        return "剪切板功能需要安装pyperclip库，请运行: pip install pyperclip"
    except Exception as e:
        return f"获取剪切板内容时出错: {str(e)}"


def set_clipboard_content(content: str) -> str:
    """
    设置剪切板内容

    该函数将指定的文本内容设置到系统剪切板中，方便后续粘贴操作。

    Args:
        content (str): 要设置到剪切板的文本内容

    Returns:
        str: 操作结果描述

    Example:
        >>> set_clipboard_content("这是要复制到剪切板的内容")
        '内容已成功复制到剪切板'

        >>> set_clipboard_content("")
        '剪切板内容已清空'
    """
    try:
        import pyperclip

        # 设置剪切板内容
        pyperclip.copy(content)

        if content:
            return f"内容已成功复制到剪切板（{len(content)}个字符）"
        else:
            return "剪切板内容已清空"

    except ImportError:
        return "剪切板功能需要安装pyperclip库，请运行: pip install pyperclip"
    except Exception as e:
        return f"设置剪切板内容时出错: {str(e)}"


def batch_analyze_texts(texts: list, analysis_type: str = "总结") -> dict:
    """
    批量分析多个文本内容

    该函数支持并发处理多个文本的AI分析，提高处理效率。
    支持文本总结、关键词提取、情感分析等多种分析类型。

    Args:
        texts (list): 要分析的文本内容列表
        analysis_type (str): 分析类型，可选值：
            - "总结": 文本内容总结
            - "关键词": 提取关键词
            - "情感": 情感分析
            - "分类": 文本分类
            - "翻译": 翻译为中文

    Returns:
        dict: 批量分析结果，包含：
            - results: 各文本的分析结果列表
            - total_processed: 处理的总文本数量
            - success_count: 成功处理的文本数量
            - failed_count: 处理失败的文本数量
            - processing_time: 总处理时间

    Example:
        >>> batch_analyze_texts(["第一段文本", "第二段文本"], "总结")
        {
            'results': ['文本1的总结', '文本2的总结'],
            'total_processed': 2,
            'success_count': 2,
            'failed_count': 0,
            'processing_time': 1.5
        }
    """
    import time
    import concurrent.futures
    from typing import Dict, List, Any

    start_time = time.time()

    if not texts or not isinstance(texts, list):
        return {
            'results': [],
            'total_processed': 0,
            'success_count': 0,
            'failed_count': 0,
            'processing_time': 0,
            'error': '输入参数无效：texts必须是非空列表'
        }

    # 定义分析函数
    def analyze_single_text(text: str, index: int) -> Dict[str, Any]:
        try:
            if not text or not isinstance(text, str):
                return {'index': index, 'success': False, 'error': '文本内容无效'}

            # 根据分析类型构建提示
            prompts = {
                "总结": f"请总结以下文本的主要内容，控制在200字以内：\n\n{text}",
                "关键词": f"请从以下文本中提取关键词（5-10个），用逗号分隔：\n\n{text}",
                "情感": f"请分析以下文本的情感倾向（积极/消极/中性），并简要说明理由：\n\n{text}",
                "分类": f"请为以下文本分类（新闻/科技/娱乐/其他），并简要说明分类理由：\n\n{text}",
                "翻译": f"请将以下文本翻译成中文：\n\n{text}"
            }

            prompt = prompts.get(analysis_type, prompts["总结"])

            # 调用AI分析
            result = get_file_summary(prompt)

            return {
                'index': index,
                'success': True,
                'result': result,
                'text_length': len(text),
                'analysis_type': analysis_type
            }

        except Exception as e:
            return {
                'index': index,
                'success': False,
                'error': str(e),
                'text_length': len(text) if isinstance(text, str) else 0
            }

    # 使用线程池并发处理
    results = []
    success_count = 0
    failed_count = 0

    # 限制并发数量，避免API调用过于频繁
    max_workers = min(5, len(texts))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_index = {
            executor.submit(analyze_single_text, text, i): i
            for i, text in enumerate(texts)
        }

        # 收集结果
        for future in concurrent.futures.as_completed(future_to_index):
            result = future.result()
            results.append(result)

            if result['success']:
                success_count += 1
            else:
                failed_count += 1

    # 按原始顺序排序结果
    results.sort(key=lambda x: x['index'])

    processing_time = time.time() - start_time

    return {
        'results': [r.get('result', r.get('error', '未知错误')) for r in results],
        'detailed_results': results,
        'total_processed': len(texts),
        'success_count': success_count,
        'failed_count': failed_count,
        'processing_time': round(processing_time, 2),
        'analysis_type': analysis_type
    }


def batch_generate_content(prompts: list, content_type: str = "文章") -> dict:
    """
    批量生成内容

    该函数支持并发生成多个AI内容，提高创作效率。
    支持文章写作、代码生成、邮件撰写等多种内容类型。

    Args:
        prompts (list): 内容生成提示列表
        content_type (str): 内容类型，可选值：
            - "文章": 文章写作
            - "代码": 代码生成
            - "邮件": 邮件撰写
            - "报告": 报告生成
            - "摘要": 内容摘要

    Returns:
        dict: 批量生成结果，包含：
            - results: 生成的内容列表
            - total_generated: 生成的总内容数量
            - success_count: 成功生成的内容数量
            - failed_count: 生成失败的内容数量
            - processing_time: 总处理时间

    Example:
        >>> batch_generate_content(["写一篇关于AI的文章", "写一篇关于机器学习的文章"], "文章")
        {
            'results': ['AI文章内容...', '机器学习文章内容...'],
            'total_generated': 2,
            'success_count': 2,
            'failed_count': 0,
            'processing_time': 3.2
        }
    """
    import time
    import concurrent.futures
    from typing import Dict, List, Any

    start_time = time.time()

    if not prompts or not isinstance(prompts, list):
        return {
            'results': [],
            'total_generated': 0,
            'success_count': 0,
            'failed_count': 0,
            'processing_time': 0,
            'error': '输入参数无效：prompts必须是非空列表'
        }

    # 定义生成函数
    def generate_single_content(prompt: str, index: int) -> Dict[str, Any]:
        try:
            if not prompt or not isinstance(prompt, str):
                return {'index': index, 'success': False, 'error': '提示内容无效'}

            # 根据内容类型调用相应的生成函数
            if content_type == "代码":
                result = code_ai_model(prompt)
            elif content_type in ["文章", "邮件", "报告", "摘要"]:
                result = write_ai_model(prompt)
            else:
                result = write_ai_model(prompt)  # 默认使用文章生成

            return {
                'index': index,
                'success': True,
                'result': result,
                'content_type': content_type,
                'prompt_length': len(prompt)
            }

        except Exception as e:
            return {
                'index': index,
                'success': False,
                'error': str(e),
                'content_type': content_type
            }

    # 使用线程池并发处理
    results = []
    success_count = 0
    failed_count = 0

    # 限制并发数量，避免API调用过于频繁
    max_workers = min(3, len(prompts))  # 内容生成更耗时，减少并发数

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_index = {
            executor.submit(generate_single_content, prompt, i): i
            for i, prompt in enumerate(prompts)
        }

        # 收集结果
        for future in concurrent.futures.as_completed(future_to_index):
            result = future.result()
            results.append(result)

            if result['success']:
                success_count += 1
            else:
                failed_count += 1

    # 按原始顺序排序结果
    results.sort(key=lambda x: x['index'])

    processing_time = time.time() - start_time

    return {
        'results': [r.get('result', r.get('error', '生成失败')) for r in results],
        'detailed_results': results,
        'total_generated': len(prompts),
        'success_count': success_count,
        'failed_count': failed_count,
        'processing_time': round(processing_time, 2),
        'content_type': content_type
    }


if __name__ == '__main__':
    file_content = input("请输入要总结的文件内容：")
    output_content = code_ai_explain_model(file_content)
    print(output_content)

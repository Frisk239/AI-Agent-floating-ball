#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Agent Floating Ball - 智能MCP客户端

基于Moonshot API的智能MCP客户端，支持自然语言指令理解和自动工具调用
"""

import sys
import os
import json
import time
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

try:
    from openai import OpenAI
    from fastmcp import Client
except ImportError as e:
    print(f"❌ 缺少必要的依赖包: {e}")
    print("请安装: pip install openai fastmcp")
    sys.exit(1)


def load_config(config_path: str = "backend/config.json") -> dict:
    """从配置文件加载配置"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ 配置文件不存在: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        return {}
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return {}


class SmartMCPClient:
    """基于Moonshot API的智能MCP客户端"""

    def __init__(self, mcp_server_url: str = "http://localhost:9000", config_path: str = "backend/config.json"):
        # 从配置文件加载Moonshot配置
        config = load_config(config_path)
        moonshot_config = config.get("ai", {}).get("moonshot", {})

        # 获取API密钥（优先从配置文件，环境变量作为后备）
        moonshot_api_key = moonshot_config.get("api_key") or os.getenv("MOONSHOT_API_KEY")
        if not moonshot_api_key:
            raise ValueError("请在配置文件中设置 Moonshot API key，或设置环境变量 MOONSHOT_API_KEY")

        # 获取其他配置参数
        base_url = moonshot_config.get("base_url", "https://api.moonshot.cn/v1")
        model = moonshot_config.get("model", "moonshot-v1-8k")

        print(f"🔑 使用Moonshot配置: 模型={model}, API密钥={'*' * 10}...")

        # 初始化Moonshot客户端
        self.openai_client = OpenAI(
            api_key=moonshot_api_key,
            base_url=base_url
        )

        # 初始化MCP客户端 - 尝试添加/mcp路径前缀
        mcp_url = f"{mcp_server_url}/mcp" if not mcp_server_url.endswith("/mcp") else mcp_server_url
        print(f"🔗 连接到MCP服务器: {mcp_url}")
        self.mcp_client = Client(mcp_url)
        self.tools = []
        self.model = model  # 使用配置文件中的模型

    async def initialize(self):
        """初始化MCP客户端，获取可用工具列表"""
        try:
            print("🔗 连接到MCP服务器...")
            async with self.mcp_client:
                tools = await self.mcp_client.list_tools()
                self.tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema
                        }
                    }
                    for tool in tools
                ]
            print(f"✅ 成功连接，获取到 {len(self.tools)} 个工具")
            return True
        except Exception as e:
            print(f"❌ MCP服务器连接失败: {e}")
            return False

    def build_context(self) -> str:
        """构建上下文信息"""
        context_parts = []

        # 当前时间
        current_time = datetime.now().strftime('%Y年%m月%d日 %H时%M分%S秒')
        context_parts.append(f"当前时间: {current_time}")

        # 系统信息（如果可用）
        try:
            import platform
            context_parts.append(f"操作系统: {platform.system()} {platform.release()}")
        except:
            pass

        return "\n".join(context_parts)

    async def process_instruction(self, user_input: str) -> str:
        """处理用户指令"""
        try:
            print("🔍 正在理解您的指令...")

            # 构建上下文
            context = self.build_context()

            # 构建系统提示
            system_prompt = f"""你是智能助手，可以使用各种工具来帮助用户解决问题。

上下文信息:
{context}

你需要理解用户的指令，决定是否需要调用工具来完成任务。
如果需要调用工具，请使用工具调用功能；如果不需要，直接回答用户。

支持的工具类型:
- 系统工具: 获取系统信息、性能监控、天气查询等
- 聊天工具: 与AI对话
- 自动化工具: 应用启动、窗口管理等
- 语音工具: 文本转语音
- 视觉工具: 图像分析
- 网络工具: 网页搜索、内容读取

请用简洁的语言回答用户的问题。"""

            # 构建消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]

            # 调用Moonshot API进行意图识别
            print("🤖 正在分析指令意图...")
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                max_tokens=2048,
                temperature=0.1  # 降低随机性，提高准确性
            )

            # 检查是否需要工具调用
            if response.choices[0].finish_reason == 'tool_calls':
                print("⚙️ 检测到工具调用需求，正在执行...")
                result = await self.execute_tool_calls(response.choices[0].message.tool_calls)
                return result
            else:
                # 直接回答
                answer = response.choices[0].message.content
                print("💬 直接回答用户问题")
                return answer

        except Exception as e:
            error_msg = f"❌ 处理指令时出错: {str(e)}"
            print(error_msg)
            return error_msg

    async def execute_tool_calls(self, tool_calls) -> str:
        """执行工具调用"""
        results = []

        async with self.mcp_client:
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                print(f"🔧 执行工具: {tool_name}")
                print(f"📝 参数: {tool_args}")

                try:
                    start_time = time.time()

                    # 调用工具
                    result = await self.mcp_client.call_tool(tool_name, tool_args)

                    end_time = time.time()
                    duration = end_time - start_time

                    print(f"⏱️ 工具执行耗时: {duration:.2f}秒")

                    # 提取工具结果
                    if result.content and len(result.content) > 0:
                        tool_result = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                    else:
                        tool_result = "工具执行完成"

                    results.append(f"工具 {tool_name} 执行结果:\n{tool_result}")

                except Exception as e:
                    error_msg = f"工具 {tool_name} 执行失败: {str(e)}"
                    print(f"❌ {error_msg}")
                    results.append(error_msg)

        return "\n\n".join(results)

    def show_help(self):
        """显示帮助信息"""
        print("\n" + "="*70)
        print("🤖 AI Agent Floating Ball - 智能MCP客户端")
        print("="*70)
        print("\n🎯 支持的指令类型:")
        print("• 系统相关: '查看系统信息'、'系统性能'、'北京天气'")
        print("• 聊天相关: '和AI聊天'、'你好'")
        print("• 自动化相关: '启动计算器'、'查看窗口'")
        print("• 语音相关: '文本转语音'")
        print("• 视觉相关: '分析图片'")
        print("• 网络相关: '搜索人工智能'、'读取网页'")
        print()
        print("💡 使用提示:")
        print("• 输入自然语言指令，系统会自动理解并调用相应工具")
        print("• 支持中文和英文指令")
        print("• 输入 'help' 显示此帮助")
        print("• 输入 'exit' 退出程序")
        print("="*70)

    async def run_interactive(self):
        """运行交互式客户端"""
        print("🚀 启动智能MCP客户端...")

        # 初始化连接
        if not await self.initialize():
            print("❌ 初始化失败，请检查MCP服务器是否运行")
            return

        self.show_help()

        while True:
            try:
                # 获取用户输入
                user_input = input("\n🎯 请输入指令 > ").strip()

                if not user_input:
                    continue

                # 处理控制指令
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👋 感谢使用，再见！")
                    break
                elif user_input.lower() in ['help', 'h', '?']:
                    self.show_help()
                    continue

                # 处理用户指令
                start_time = time.time()
                result = await self.process_instruction(user_input)
                end_time = time.time()

                print(f"⏱️ 总耗时: {end_time - start_time:.2f}秒")
                print(f"📄 结果:\n{result}")
                print("\n✅ 指令处理完成")

            except KeyboardInterrupt:
                print("\n👋 用户中断，退出程序")
                break
            except Exception as e:
                print(f"❌ 发生错误: {str(e)}")
                print("💡 请检查网络连接和API密钥配置")


async def main():
    """主函数"""
    try:
        # 创建客户端（会自动从配置文件读取API密钥）
        client = SmartMCPClient()

        # 运行交互式客户端
        await client.run_interactive()

    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("💡 请检查 backend/config.json 中的 Moonshot 配置")
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())

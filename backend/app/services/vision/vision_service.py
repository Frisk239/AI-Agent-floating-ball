from openai import OpenAI
import os
import base64
import random

#  base 64 编码格式
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_response(user_content, path="imgs/test.png"):
    try:
        print("🔍 [DEBUG] 开始视觉分析处理...")
        print(f"🔍 [DEBUG] 用户提示: {user_content}")
        print(f"🔍 [DEBUG] 图片路径: {path}")

        # 检查图片文件
        import os
        if not os.path.exists(path):
            print(f"❌ [DEBUG] 图片文件不存在: {path}")
            return f"图片文件不存在: {path}"

        file_size = os.path.getsize(path)
        print(f"🔍 [DEBUG] 图片文件大小: {file_size} bytes ({file_size/1024:.1f} KB)")

        print("🔍 [DEBUG] 正在获取配置...")
        try:
            from ..core.config import get_config
            config = get_config()
            print("✅ [DEBUG] 配置获取成功")
        except ImportError as import_error:
            print(f"❌ [DEBUG] 相对导入失败: {import_error}")
            print("🔍 [DEBUG] 尝试绝对导入...")
            try:
                import sys
                import os
                # 添加项目根目录到Python路径
                current_file = os.path.abspath(__file__)
                backend_dir = os.path.dirname(current_file)  # services/vision
                app_dir = os.path.dirname(backend_dir)       # services
                project_root = os.path.dirname(app_dir)      # app
                backend_root = os.path.dirname(project_root) # backend

                if backend_root not in sys.path:
                    sys.path.insert(0, backend_root)
                    print(f"🔍 [DEBUG] 已添加backend根目录到Python路径: {backend_root}")

                # 尝试直接导入配置模块
                from app.core.config import get_config
                config = get_config()
                print("✅ [DEBUG] 绝对导入配置成功")
            except ImportError as abs_import_error:
                print(f"❌ [DEBUG] 绝对导入也失败: {abs_import_error}")
                # 最后的fallback：直接读取配置文件
                print("🔍 [DEBUG] 使用fallback方式读取配置...")
                import json

                # 从当前文件位置计算config.json的路径
                current_file = os.path.abspath(__file__)
                backend_dir = os.path.dirname(current_file)  # .../services/vision
                services_dir = os.path.dirname(backend_dir)  # .../services
                app_dir = os.path.dirname(services_dir)      # .../app
                backend_root = os.path.dirname(app_dir)      # .../backend
                config_path = os.path.join(backend_root, 'config.json')

                print(f"🔍 [DEBUG] 配置文件路径: {config_path}")

                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)

                    # 创建一个简化的配置对象
                    class SimpleConfig:
                        def __init__(self, data):
                            self.ai = type('AI', (), {
                                'dashscope': type('DashScope', (), {
                                    'api_key': data.get('ai', {}).get('dashscope', {}).get('api_key', ''),
                                    'base_url': data.get('ai', {}).get('dashscope', {}).get('base_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
                                })()
                            })()

                    config = SimpleConfig(config_data)
                    print("✅ [DEBUG] Fallback配置读取成功")
                else:
                    raise Exception(f"配置文件不存在: {config_path}")

        # 检查API配置
        api_key = config.ai.dashscope.api_key
        base_url = config.ai.dashscope.base_url
        print(f"🔍 [DEBUG] API Key配置: {'是' if api_key else '否'}")
        print(f"🔍 [DEBUG] Base URL: {base_url}")

        if not api_key:
            print("❌ [DEBUG] DashScope API密钥未配置")
            return "DashScope API密钥未配置"

        print("🔍 [DEBUG] 正在编码图片...")
        base64_image = encode_image(path)
        if not base64_image:
            print("❌ [DEBUG] 图片编码失败")
            return "图片编码失败"

        print(f"✅ [DEBUG] 图片编码成功，长度: {len(base64_image)} 字符")

        print("🔍 [DEBUG] 正在初始化OpenAI客户端...")
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        print("✅ [DEBUG] OpenAI客户端初始化成功")

        print("🔍 [DEBUG] 正在调用DashScope API...")
        completion = client.chat.completions.create(
            model="qwen-vl-plus",
            messages=[
                {
                  "role": "user",
                  "content": [
                    {
                      "type": "text",
                      "text": user_content
                    },
                    {
                      "type": "image_url",
                      "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                      }
                    }
                  ]
                }
              ],
              # stream=True,
              # stream_options={"include_usage":True}
            )

        print("✅ [DEBUG] API调用成功")
        print(f"🔍 [DEBUG] API响应类型: {type(completion)}")

        # 提取content内容
        if hasattr(completion, 'choices') and completion.choices:
            choice = completion.choices[0]
            print(f"🔍 [DEBUG] Choice类型: {type(choice)}")

            if hasattr(choice, 'message'):
                message = choice.message
                print(f"🔍 [DEBUG] Message类型: {type(message)}")

                if hasattr(message, 'content'):
                    content = message.content
                    print(f"✅ [DEBUG] 成功获取响应内容，长度: {len(str(content))}")
                    print(f"📝 [DEBUG] 响应内容: {content}")
                    return content
                else:
                    print("❌ [DEBUG] Message对象没有content属性")
                    print(f"🔍 [DEBUG] Message属性: {dir(message)}")
            else:
                print("❌ [DEBUG] Choice对象没有message属性")
                print(f"🔍 [DEBUG] Choice属性: {dir(choice)}")
        else:
            print("❌ [DEBUG] Completion对象没有choices属性或choices为空")
            print(f"🔍 [DEBUG] Completion属性: {dir(completion)}")

        print("❌ [DEBUG] 无法从API响应中提取内容")
        return "无法从API响应中提取内容"

    except ImportError as e:
        print(f"❌ [DEBUG] 导入错误: {e}")
        return f"导入错误: {e}"
    except ConnectionError as e:
        print(f"❌ [DEBUG] 网络连接错误: {e}")
        return f"网络连接错误: {e}"
    except Exception as e:
        print(f"❌ [DEBUG] 未知错误: {type(e).__name__}: {e}")
        import traceback
        print(f"🔍 [DEBUG] 完整错误堆栈:")
        traceback.print_exc()
        return f"视觉分析错误: {e}"

if __name__=='__main__':
    get_image_response(input("请输入内容："))

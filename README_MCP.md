# AI Agent Floating Ball - MCP工具框架

## 📋 项目概述

本项目实现了一个完整的AI Agent系统，包含后端API服务、MCP工具框架和智能客户端。支持自然语言指令理解和自动工具调用。

## 🏗️ 架构组成

### 1. 后端API服务 (`backend/`)
- **FastAPI框架**: 提供RESTful API接口
- **模块化设计**: 系统、聊天、自动化、语音、视觉、网络等功能模块
- **统一接口**: 所有功能通过标准API调用

### 2. MCP工具框架 (`backend/app/core/mcp_tools.py`)
- **FastMCP集成**: 基于Model Context Protocol标准
- **工具注册**: 自动注册所有可用工具
- **标准化接口**: 统一的工具描述和调用格式

### 3. 测试工具
- **API测试脚本** (`test_document_apis.py`): 测试文档处理功能
- **MCP测试脚本** (`test_mcp_tools.py`): 自动化测试MCP工具
- **交互式测试** (`interactive_mcp_test.py`): 手动测试工具功能

### 4. 智能客户端 (`smart_mcp_client.py`)
- **Moonshot AI集成**: 基于Moonshot API进行意图识别
- **自然语言处理**: 支持中文自然语言指令
- **自动工具调用**: 智能匹配和执行工具

## 🚀 快速开始

### 环境准备

1. **安装依赖**:
```bash
cd AI-Agent-floating-ball/backend
pip install -r requirements.txt
```

2. **配置API密钥**:
API密钥已配置在 `backend/config.json` 文件中，无需额外设置环境变量。

如果需要修改API密钥，请编辑 `backend/config.json` 文件：
```json
{
  "ai": {
    "moonshot": {
      "api_key": "your_moonshot_api_key_here",
      "base_url": "https://api.moonshot.cn/v1",
      "model": "moonshot-v1-8k"
    }
  }
}
```

环境变量作为后备选项（如果配置文件中没有找到API密钥）:
```bash
export MOONSHOT_API_KEY="your_api_key_here"  # 仅在配置文件无效时使用
```

### 启动服务

1. **启动后端API服务**:
```bash
cd AI-Agent-floating-ball/backend
python main.py
```

2. **启动MCP服务器** (可选):
```bash
cd AI-Agent-floating-ball/backend
python -c "from app.core.mcp_tools import mcp; mcp.run(transport='http', port=9000)"
```

### 测试功能

#### 方法1: 使用智能客户端 (推荐)
```bash
cd AI-Agent-floating-ball
python smart_mcp_client.py
```

支持的指令示例:
- "帮我查看系统信息"
- "北京今天天气怎么样"
- "搜索人工智能发展"
- "启动计算器"
- "分析这张图片"

#### 方法2: 使用交互式测试脚本
```bash
cd AI-Agent-floating-ball
python interactive_mcp_test.py
```

#### 方法3: 使用自动化测试脚本
```bash
cd AI-Agent-floating-ball
python test_mcp_tools.py
```

## 📚 API接口文档

### 系统工具
- `GET /api/system/info` - 获取系统基本信息
- `GET /api/system/performance` - 获取系统性能监控
- `GET /api/system/weather?city=北京` - 获取天气信息

### 聊天工具
- `POST /api/chat/send` - 发送聊天消息
- `GET /api/chat/status` - 获取聊天状态

### 自动化工具
- `POST /api/automation/apps/launch` - 启动应用程序
- `GET /api/automation/windows` - 获取窗口信息

### 语音工具
- `POST /api/speech/tts` - 文本转语音

### 视觉工具
- `POST /api/vision/analyze` - AI图像分析

### 网络工具
- `GET /api/system/search?query=关键词` - 网页搜索

## 🔧 MCP工具列表

### 系统工具
- `get_system_information()` - 获取系统基本信息
- `get_system_performance()` - 获取系统性能监控
- `get_weather_information(city)` - 获取天气信息

### 聊天工具
- `send_chat_message(message)` - 发送聊天消息
- `get_chat_status()` - 获取聊天状态

### 自动化工具
- `launch_application(app_name)` - 启动应用程序
- `get_window_information()` - 获取窗口信息

### 语音工具
- `text_to_speech_conversion(text)` - 文本转语音

### 视觉工具
- `analyze_image_with_ai(image_path, prompt)` - AI图像分析

### 网络工具
- `search_web_content(query)` - 网页搜索
- `read_webpage(url)` - 读取网页内容

## 🎯 使用示例

### 智能客户端使用

```bash
$ python smart_mcp_client.py

🚀 启动智能MCP客户端...
🔗 连接到MCP服务器...
✅ 成功连接，获取到 12 个工具

🎯 请输入指令 > 帮我查看北京的天气

🔍 正在理解您的指令...
🤖 正在分析指令意图...
⚙️ 检测到工具调用需求，正在执行...
🔧 执行工具: get_weather_information
📝 参数: {'city': '北京'}
⏱️ 工具执行耗时: 0.45秒

⏱️ 总耗时: 1.23秒
📄 结果:
工具 get_weather_information 执行结果:
{"city": "北京", "temperature": "18°C", "weather": "晴天", "wind": "2级"}

✅ 指令处理完成
```

### API直接调用

```python
import requests

# 获取系统信息
response = requests.get("http://localhost:8000/api/system/info")
print(response.json())

# 发送聊天消息
response = requests.post("http://localhost:8000/api/chat/send",
                        json={"message": "你好"})
print(response.json())
```

## 🔍 故障排除

### 常见问题

1. **后端服务无法启动**
   - 检查端口8000是否被占用
   - 确认所有依赖都已安装

2. **MCP客户端连接失败**
   - 确认后端服务正在运行
   - 检查网络连接

3. **Moonshot API调用失败**
   - 检查MOONSHOT_API_KEY环境变量
   - 确认API密钥有效

4. **工具调用失败**
   - 检查工具参数格式
   - 查看后端日志

### 调试模式

启用详细日志:
```bash
export PYTHONPATH=/path/to/AI-Agent-floating-ball/backend
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

## 📈 性能优化

- **连接池**: 使用requests.Session复用连接
- **异步处理**: MCP客户端支持异步调用
- **缓存机制**: 对频繁查询的结果进行缓存
- **错误重试**: 网络请求失败时自动重试

## 🔒 安全考虑

- API密钥通过环境变量配置
- 输入验证和参数检查
- 错误信息过滤，避免泄露敏感信息
- 网络请求超时控制

## 📝 开发指南

### 添加新工具

1. 在相应服务模块中实现功能
2. 在 `mcp_tools.py` 中添加 `@mcp.tool()` 装饰器
3. 更新API路由
4. 添加测试用例

### 扩展智能客户端

1. 修改系统提示词以支持新工具
2. 更新指令解析逻辑
3. 添加新的参数提取规则

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交变更
4. 发起Pull Request

## 📄 许可证

本项目采用MIT许可证。

## 📞 联系方式

如有问题或建议，请提交Issue或Pull Request。

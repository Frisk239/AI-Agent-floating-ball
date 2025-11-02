# AI Agent Floating Ball v2.0

现代化AI助手悬浮球应用，基于 Tauri + React + FastAPI 构建。

## 🚀 功能特性

- **桌面悬浮球**: 启动后直接在桌面上显示可拖拽的悬浮球
- **拖动选择识图**: 拖拽悬浮球选择屏幕区域，自动进行AI图像分析
- **AI对话**: 支持与Moonshot Kimi等大语言模型对话
- **语音交互**: 集成语音识别和语音合成
- **系统控制**: 窗口管理、应用启动等自动化功能
- **边缘隐藏**: 智能边缘隐藏和恢复功能

## 🏗️ 技术架构

### 前端 (Tauri + React + TypeScript)
- **Tauri**: 原生桌面应用框架
- **React**: 用户界面框架
- **TypeScript**: 类型安全的JavaScript
- **拖拽选择**: 基于轨迹检测的封闭图形识别
- **屏幕截图**: 原生系统API进行高效截图

### 后端 (FastAPI + Python)
- **FastAPI**: 异步高性能Web框架
- **AI集成**: Moonshot Kimi、DashScope、秘塔搜索
- **RESTful API**: 完整的API接口设计
- **配置管理**: Pydantic配置验证

## 📦 安装运行

### 环境要求
- **Node.js** >= 18.0.0
- **Rust** >= 1.70.0
- **Python** >= 3.8.0

### 后端安装
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 前端安装
```bash
cd frontend
npm install
npm run tauri dev
```

## 🎯 使用方法

1. **启动应用**: 运行后悬浮球会出现在桌面右下角
2. **拖拽选择**: 长按悬浮球拖拽，选择屏幕区域
3. **自动分析**: 松开鼠标后自动截图并发送给AI分析
4. **对话交互**: 双击悬浮球打开聊天界面
5. **边缘隐藏**: 将悬浮球拖到屏幕边缘会自动隐藏

## 🔧 核心功能实现

### 拖动选择识图算法
```typescript
// 轨迹检测和封闭图形识别
const detectEnclosedArea = (points: TrajectoryPoint[]): SelectionRegion | null => {
  // 计算起点终点距离
  const distance = calculateDistance(firstPoint, lastPoint);

  // 查找最远两点
  let maxDistance = 0;
  // ...

  // 判断是否形成有效封闭图形
  if (distance < 50 && maxDistance > 80) {
    // 计算最小外接矩形
    return selection;
  }
  return null;
};
```

### 屏幕截图 (Rust实现)
```rust
#[tauri::command]
async fn capture_screen_region(x: f64, y: f64, width: f64, height: f64) -> Result<String, String> {
    // 获取屏幕信息
    let screens = screen::Screen::from_primary()?;

    // 创建截图
    let screenshot = screens.capture()?;

    // 坐标转换和裁剪
    let scale_factor = screens.scale_factor();
    let physical_x = (x * scale_factor) as u32;
    // ...

    // 返回base64编码的图像
    Ok(base64_string)
}
```

## 📁 项目结构

```
AI-Agent-floating-ball/
├── backend/                    # FastAPI后端
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── core/              # 核心服务
│   │   └── services/          # 业务服务
│   └── requirements.txt
├── frontend/                   # Tauri + React前端
│   ├── src/
│   │   ├── components/        # React组件
│   │   ├── services/          # API服务
│   │   ├── types/             # TypeScript类型
│   │   └── utils/             # 工具函数
│   └── src-tauri/             # Tauri Rust代码
└── docs/                      # 文档
```

## 🔐 配置说明

### 后端配置 (backend/config.json)
```json
{
  "ai": {
    "moonshot": {
      "api_key": "your-moonshot-api-key",
      "model": "kimi-k2-0905-preview"
    },
    "dashscope": {
      "api_key": "your-dashscope-api-key"
    }
  }
}
```

### 前端配置 (frontend/src-tauri/tauri.conf.json)
```json
{
  "windows": [{
    "label": "floating-ball",
    "width": 60,
    "height": 60,
    "decorations": false,
    "transparent": true,
    "alwaysOnTop": true
  }]
}
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Tauri](https://tauri.app/) - 现代化桌面应用框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Moonshot AI](https://moonshot.cn/) - AI大语言模型服务
- [DashScope](https://dashscope.aliyun.com/) - 阿里云AI服务

---

**AI Agent Floating Ball** - 让AI助手随时陪伴在您身边！ 🤖✨

# AI Agent Backend API 测试指令集

本文档包含了AI Agent Backend API的所有测试指令，使用Windows CMD环境进行测试。

## 🚀 环境准备

确保后端服务已启动：
```cmd
cd backend
python main.py
```

## 🧪 API测试指令

### 1. 文件夹管理 - 批量创建文件夹
```cmd
curl -X POST "http://localhost:8000/api/automation/folders/create" -H "Content-Type: application/json" -d "{\"folder_names\":[\"测试项目A\",\"测试项目B\",\"测试项目C\"],\"base_path\":\".\"}"
```

### 2. 剪切板管理 - 获取剪切板内容
```cmd
curl "http://localhost:8000/api/automation/clipboard"
```

### 3. 剪切板管理 - 设置剪切板内容
```cmd
curl -X POST "http://localhost:8000/api/automation/clipboard/set" -H "Content-Type: application/json" -d "{\"content\":\"这是测试内容 Hello World!\"}"
```

### 4. 应用启动 - 启动单个应用
```cmd
curl -X POST "http://localhost:8000/api/automation/apps/launch" -H "Content-Type: application/json" -d "{\"app_name\":\"notepad\"}"
```

### 5. 应用启动 - 批量启动应用
```cmd
curl -X POST "http://localhost:8000/api/automation/batch/launch-apps" -H "Content-Type: application/json" -d "{\"app_names\":[\"notepad\",\"calc\"]}"
```

### 6. 快捷键操作 - 执行快捷键
```cmd
curl -X POST "http://localhost:8000/api/automation/keyboard/shortcut" -H "Content-Type: application/json" -d "{\"actions\":[\"copy\",\"paste\"]}"
```

### 7. 窗口管理 - 获取窗口列表
```cmd
curl "http://localhost:8000/api/automation/windows"
```

### 8. 窗口管理 - 激活窗口
```cmd
curl -X POST "http://localhost:8000/api/automation/windows/activate/1234"
```

### 9. 上下文感知 - 获取上下文信息
```cmd
curl "http://localhost:8000/api/automation/context/info"
```

### 10. 上下文感知 - 获取智能建议
```cmd
curl "http://localhost:8000/api/automation/context/suggestions"
```

### 11. 批量文本分析 - AI智能分析
```cmd
curl -X POST "http://localhost:8000/api/automation/batch/analyze-texts" -H "Content-Type: application/json" -d "{\"texts\":[\"AI技术\",\"机器学习\"],\"analysis_type\":\"总结\"}"
```

### 12. 系统信息 - 获取系统状态
```cmd
curl "http://localhost:8000/api/system/info"
```

### 13. 系统信息 - 获取性能监控
```cmd
curl "http://localhost:8000/api/system/performance"
```

### 14. 健康检查
```cmd
curl "http://localhost:8000/api/health"
```

## 📊 测试覆盖说明

### ✅ 已验证功能 (8/10)
- **文件夹管理**: 批量创建文件夹，支持相对路径
- **剪切板管理**: 获取和设置剪切板内容，AI智能分析
- **应用启动**: 智能启动策略，批量启动应用
- **快捷键操作**: 系统快捷键执行（复制、粘贴等）
- **窗口管理**: 窗口列表获取，窗口激活控制
- **上下文感知**: 系统状态监控，用户行为分析
- **批量文本分析**: AI并发分析，多种分析类型
- **批量应用启动**: 批量启动多个应用程序

### 🔄 待验证功能
- **语音交互**: 语音识别和语音合成
- **图像分析**: OCR文字识别和图像理解

## 🎯 使用说明

1. **顺序执行**: 建议按照文档顺序执行测试
2. **依赖关系**: 某些测试可能依赖前面的操作结果
3. **并发安全**: API支持并发请求，但建议单线程测试
4. **错误处理**: 所有API都包含完善的错误处理机制

## 📝 注意事项

- 确保后端服务正在运行在 `localhost:8000`
- 某些自动化功能需要在Windows环境下才能正常工作
- 批量操作会同时执行多个任务，请注意系统资源使用
- 所有测试都是非破坏性的，不会影响现有文件或应用

---

**测试环境**: Windows 11 + Python 3.8+ + FastAPI
**测试时间**: 2025/11/3
**测试状态**: ✅ 8/10 功能验证通过

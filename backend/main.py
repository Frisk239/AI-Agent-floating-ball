#!/usr/bin/env python3
"""
AI Agent Floating Ball - FastAPI Backend
现代化AI助手后端服务
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.main import create_application

# 创建FastAPI应用
app = create_application()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    )

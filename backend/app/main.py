"""
AI Agent Floating Ball - FastAPI Application
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .core.config import get_config
from .api.chat import router as chat_router
from .api.speech import router as speech_router
from .api.vision import router as vision_router
from .api.automation import router as automation_router
from .api.system import router as system_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    config = get_config()
    print(f"🚀 Starting {config.app.name} v{config.app.version}")

    yield

    # 关闭时
    print("👋 Shutting down AI Agent")


def create_application() -> FastAPI:
    """创建FastAPI应用实例"""

    # 获取配置
    config = get_config()

    # 创建FastAPI应用
    app = FastAPI(
        title=config.app.name,
        description=config.app.description,
        version=config.app.version,
        lifespan=lifespan
    )

    # 注册路由
    app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
    app.include_router(speech_router, prefix="/api/speech", tags=["speech"])
    app.include_router(vision_router, prefix="/api/vision", tags=["vision"])
    app.include_router(automation_router, prefix="/api/automation", tags=["automation"])
    app.include_router(system_router, prefix="/api/system", tags=["system"])

    # 健康检查端点
    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "healthy", "version": config.app.version}

    # 根路径
    @app.get("/", tags=["root"])
    async def root():
        return {
            "name": config.app.name,
            "version": config.app.version,
            "description": config.app.description,
            "docs": "/docs",
            "health": "/health"
        }

    return app

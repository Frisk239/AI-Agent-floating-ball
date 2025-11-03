"""
AI Agent Floating Ball - Configuration Management
配置管理系统，统一读取config.json配置
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MoonshotConfig:
    """Moonshot Kimi配置"""
    api_key: str
    base_url: str
    model: str
    temperature: float
    max_tokens: int


@dataclass
class DashScopeConfig:
    """DashScope配置"""
    api_key: str
    base_url: str
    tts_model: str
    asr_model: str


@dataclass
class MetasoConfig:
    """秘塔搜索配置"""
    api_key: str
    base_url: str


@dataclass
class AIConfig:
    """AI服务配置"""
    moonshot: MoonshotConfig
    dashscope: DashScopeConfig
    metaso: MetasoConfig


@dataclass
class SpeechConfig:
    """语音配置"""
    wake_word: str
    tts_engine: str
    stt_engine: str
    sample_rate: int
    channels: int


@dataclass
class VisionConfig:
    """视觉配置"""
    screenshot_quality: int
    max_image_size: int
    supported_formats: list


@dataclass
class AutomationConfig:
    """自动化配置"""
    gesture_enabled: bool
    hotkey_enabled: bool
    system_control_enabled: bool


@dataclass
class UIConfig:
    """UI配置"""
    theme: str
    position: Dict[str, int]
    size: Dict[str, int]
    hotkey: str
    transparency: float


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str
    file: str
    max_size: str
    backup_count: int


@dataclass
class DataConfig:
    """数据配置"""
    input_file: str
    output_file: str
    temp_dir: str
    models_dir: str


@dataclass
class AppConfig:
    """应用配置"""
    name: str
    version: str
    description: str


@dataclass
class ServerConfig:
    """服务器配置"""
    host: str
    port: int
    debug: bool


class Config:
    """主配置类"""

    def __init__(self, config_file: str = "config.json"):
        self._config_file = config_file
        self._config_data: Dict[str, Any] = {}
        self._load_config()

        # 初始化配置对象
        self.app = AppConfig(**self._config_data.get("app", {}))
        self.server = ServerConfig(**self._config_data.get("server", {}))

        # AI配置
        ai_data = self._config_data.get("ai", {})
        self.ai = AIConfig(
            moonshot=MoonshotConfig(**ai_data.get("moonshot", {})),
            dashscope=DashScopeConfig(**ai_data.get("dashscope", {})),
            metaso=MetasoConfig(**ai_data.get("metaso", {}))
        )

        # 其他配置
        self.speech = SpeechConfig(**self._config_data.get("speech", {}))
        self.vision = VisionConfig(**self._config_data.get("vision", {}))
        self.automation = AutomationConfig(**self._config_data.get("automation", {}))
        self.ui = UIConfig(**self._config_data.get("ui", {}))
        self.logging = LoggingConfig(**self._config_data.get("logging", {}))
        self.data = DataConfig(**self._config_data.get("data", {}))

    def _load_config(self):
        """加载配置文件"""
        # 配置文件路径：backend/config.json
        config_path = Path(__file__).parent.parent.parent / self._config_file

        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise Exception(f"加载配置文件失败: {e}")

    def reload(self):
        """重新加载配置"""
        self._load_config()
        # 重新初始化所有配置对象
        self.__init__(self._config_file)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config_data.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置值（仅内存中，不保存到文件）"""
        self._config_data[key] = value


# 全局配置实例
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config():
    """重新加载全局配置"""
    global _config
    if _config is not None:
        _config.reload()


# 便捷函数
def get_ai_config() -> AIConfig:
    """获取AI配置"""
    return get_config().ai


def get_speech_config() -> SpeechConfig:
    """获取语音配置"""
    return get_config().speech


def get_vision_config() -> VisionConfig:
    """获取视觉配置"""
    return get_config().vision


def get_server_config() -> ServerConfig:
    """获取服务器配置"""
    return get_config().server

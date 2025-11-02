"""
AI Agent Floating Ball - Configuration Management
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class AppConfig(BaseModel):
    name: str = "AI Agent Floating Ball"
    version: str = "2.0.0"
    description: str = "现代化AI助手悬浮球应用"


class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True


class MoonshotConfig(BaseModel):
    api_key: str = Field(default_factory=lambda: os.getenv("MOONSHOT_API_KEY", ""))
    base_url: str = "https://api.moonshot.cn/v1"
    model: str = "kimi-k2-0905-preview"
    temperature: float = 0.6
    max_tokens: int = 1024


class DashScopeConfig(BaseModel):
    api_key: str = Field(default_factory=lambda: os.getenv("DASHSCOPE_API_KEY", ""))
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    tts_model: str = "sambert-zhichu-v1"
    asr_model: str = "paraformer-realtime-8k-v1"


class MetasoConfig(BaseModel):
    api_key: str = Field(default_factory=lambda: os.getenv("METASO_API_KEY", ""))
    base_url: str = "https://metaso.cn/api/v1"


class AIConfig(BaseModel):
    moonshot: MoonshotConfig = MoonshotConfig()
    dashscope: DashScopeConfig = DashScopeConfig()
    metaso: MetasoConfig = MetasoConfig()


class SpeechConfig(BaseModel):
    wake_word: str = "hello jarvis"
    tts_engine: str = "dashscope"
    stt_engine: str = "dashscope"
    sample_rate: int = 16000
    channels: int = 1


class VisionConfig(BaseModel):
    screenshot_quality: int = 80
    max_image_size: int = 2048
    supported_formats: list = ["png", "jpg", "jpeg"]


class AutomationConfig(BaseModel):
    gesture_enabled: bool = True
    hotkey_enabled: bool = True
    system_control_enabled: bool = True


class UIConfig(BaseModel):
    theme: str = "dark"
    position: Dict[str, int] = {"x": 100, "y": 100}
    size: Dict[str, int] = {"width": 400, "height": 600}
    hotkey: str = "Ctrl+Alt+A"
    transparency: float = 0.9


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "logs/ai_agent.log"
    max_size: str = "10 MB"
    backup_count: int = 5


class DataConfig(BaseModel):
    input_file: str = "data/input_message.json"
    output_file: str = "data/output_message.json"
    temp_dir: str = "data/temp"
    models_dir: str = "models"


class Config(BaseModel):
    app: AppConfig = AppConfig()
    server: ServerConfig = ServerConfig()
    ai: AIConfig = AIConfig()
    speech: SpeechConfig = SpeechConfig()
    vision: VisionConfig = VisionConfig()
    automation: AutomationConfig = AutomationConfig()
    ui: UIConfig = UIConfig()
    logging: LoggingConfig = LoggingConfig()
    data: DataConfig = DataConfig()


# 全局配置实例
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def load_config(config_path: Optional[str] = None) -> Config:
    """加载配置文件"""
    if config_path is None:
        # 默认配置文件路径
        config_path = Path(__file__).parent.parent.parent / "config.json"

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 创建配置实例
        config = Config(**config_data)
        return config

    except FileNotFoundError:
        print(f"⚠️  配置文件不存在: {config_path}")
        print("📝 使用默认配置")
        return Config()
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        print("📝 使用默认配置")
        return Config()
    except Exception as e:
        print(f"❌ 加载配置失败: {e}")
        print("📝 使用默认配置")
        return Config()


def save_config(config: Config, config_path: Optional[str] = None) -> bool:
    """保存配置文件"""
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config.json"

    try:
        # 确保目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # 转换为字典并保存
        config_data = config.model_dump()
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

        print(f"✅ 配置已保存到: {config_path}")
        return True

    except Exception as e:
        print(f"❌ 保存配置失败: {e}")
        return False


def update_config(updates: Dict[str, Any]) -> Config:
    """更新配置"""
    config = get_config()

    # 递归更新配置
    def update_nested_dict(d: Dict[str, Any], keys: list, value: Any):
        if len(keys) == 1:
            d[keys[0]] = value
        else:
            if keys[0] not in d:
                d[keys[0]] = {}
            update_nested_dict(d[keys[0]], keys[1:], value)

    for key_path, value in updates.items():
        keys = key_path.split('.')
        config_dict = config.model_dump()
        update_nested_dict(config_dict, keys, value)

        # 重新创建配置实例
        config = Config(**config_dict)

    # 更新全局配置
    global _config
    _config = config

    return config

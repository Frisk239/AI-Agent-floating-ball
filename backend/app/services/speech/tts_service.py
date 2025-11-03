import os
import dashscope
import pyaudio
import time
import base64
import numpy as np
import json
from typing import Optional, Dict, Any

# 用于控制悬浮球输入框禁用状态的标志文件路径
INPUT_DISABLE_FLAG = "data/input_disabled.flag"
OUTPUT_FILE = "data/output_message.json"

def get_voice_from_config() -> str:
    """
    从配置中获取语音设置
    """
    try:
        from ..core.config import get_config
        config = get_config()
        voice_setting = config.speech.tts_engine  # 从配置中读取
        if voice_setting == "female":
            return "Cherry"
        else:
            return "Ethan"
    except Exception as e:
        print(f"获取语音配置失败: {e}")
        return "Ethan"  # 默认使用Ethan

def generate_tts_audio(text: str, voice: Optional[str] = None, api_key: Optional[str] = None) -> tuple[str, float]:
    """
    生成TTS音频数据（用于API返回）

    参数:
    text (str): 要转换的文本内容
    voice (str): 语音角色，默认为"Ethan"
    api_key (str): DashScope API密钥

    返回:
    tuple: (base64音频数据, 时长)
    """
    # 如果没有提供voice，使用配置中的设置
    if voice is None:
        voice = get_voice_from_config()
    elif voice == "female":
        voice = "Cherry"
    else:
        voice = "Ethan"

    # 如果没有提供api_key，使用配置中的设置
    if api_key is None:
        try:
            from ..core.config import get_config
            config = get_config()
            api_key = config.ai.dashscope.api_key
        except Exception as e:
            print(f"获取API密钥失败: {e}")
            raise Exception(f"API密钥配置错误: {e}")

    try:
        # 调用语音合成API
        responses = dashscope.audio.qwen_tts.SpeechSynthesizer.call(
            model="qwen-tts",
            api_key=api_key,
            text=text,
            voice=voice,
            stream=False  # 非流式，返回完整音频
        )

        # 收集所有音频数据
        audio_chunks = []
        for chunk in responses:
            if "output" in chunk and "audio" in chunk["output"] and "data" in chunk["output"]["audio"]:
                audio_string = chunk["output"]["audio"]["data"]
                audio_chunks.append(audio_string)

        if audio_chunks:
            # 合并所有音频块
            combined_audio = "".join(audio_chunks)
            # 估算时长（每字符约0.1秒）
            duration = len(text) * 0.1
            return combined_audio, duration
        else:
            raise Exception("未收到音频数据")

    except Exception as e:
        raise Exception(f"TTS生成失败: {str(e)}")

def realtime_tts_speak(text: str, voice: Optional[str] = None, api_key: Optional[str] = None, rate: int = 27000) -> int:
    """
    实时语音播报功能函数

    参数:
    text (str): 要播报的文本内容
    voice (str): 语音角色，默认为"Ethan"
    api_key (str): DashScope API密钥
    """
    # 如果没有提供voice，使用配置中的设置
    if voice is None:
        voice = get_voice_from_config()
    elif voice == "female":
        voice = "Cherry"
    else:
        voice = "Ethan"

    # 如果没有提供api_key，使用配置中的设置
    if api_key is None:
        try:
            from ..core.config import get_config
            config = get_config()
            api_key = config.ai.dashscope.api_key
        except Exception as e:
            print(f"获取API密钥失败: {e}")
            return -1

    if os.path.exists(INPUT_DISABLE_FLAG):
        # 初始化PyAudio
        p = pyaudio.PyAudio()

        # 创建音频流
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=rate,
                        output=True)

        try:
            # 调用语音合成API
            responses = dashscope.audio.qwen_tts.SpeechSynthesizer.call(
                model="qwen-tts",
                api_key=api_key,
                text=text,
                voice=voice,
                stream=True
            )

            # 实时播放音频数据
            for chunk in responses:
                if "output" in chunk and "audio" in chunk["output"] and "data" in chunk["output"]["audio"]:
                    audio_string = chunk["output"]["audio"]["data"]
                    wav_bytes = base64.b64decode(audio_string)
                    audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
                    # 直接播放音频数据
                    stream.write(audio_np.tobytes())

            # 等待播放完成
            time.sleep(0.8)

        except Exception as e:
            print(f"语音播报出错: {e}")
        finally:
            # 清理资源
            stream.stop_stream()
            stream.close()
            p.terminate()
    
    else:
        response_data = {
            'request_id': str(time.time()),
            'content': text+"...\n\n"+"当前请不要在输入框输入任何内容。",
            'timestamp': time.time()
        }
    
        # 写入输出文件
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, ensure_ascii=False)
        #return 0


# 使用示例
if __name__ == "__main__":
    # 调用函数进行实时语音播报
    realtime_tts_speak("随时为您效劳，先生")

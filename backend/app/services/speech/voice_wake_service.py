import pyaudio
from vosk import Model, KaldiRecognizer
import json
import re
import threading
import time
import os

# 全局变量
wake_word_detected = False
listening_active = False
audio_interface = None
audio_stream = None
recognizer = None
wake_thread = None

def init_voice_wake(model_path='vosk-model-small-en-us-0.15'):
    """
    初始化语音唤醒服务
    :param model_path: Vosk模型路径
    :return: 是否初始化成功
    """
    global audio_interface, audio_stream, recognizer

    try:
        # 检查模型路径
        if not os.path.exists(model_path):
            print(f"模型路径不存在: {model_path}")
            return False

        # 初始化语音识别模型
        model = Model(model_path)
        audio_interface = pyaudio.PyAudio()
        audio_stream = audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4000,
        )
        recognizer = KaldiRecognizer(model, 16000)
        print("语音唤醒服务初始化成功")
        return True
    except Exception as e:
        print(f"语音唤醒服务初始化失败: {e}")
        return False

def voice_wake_listen():
    """
    语音唤醒监听循环
    """
    global wake_word_detected, listening_active, audio_stream, recognizer

    print("开始语音唤醒监听...")

    while listening_active:
        try:
            data = audio_stream.read(4000, exception_on_overflow=False)
            if len(data) == 0:
                break

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result["text"]
                print(f"识别结果: {text}")

                # 使用正则表达式识别唤醒词
                if re.search(r'\bhello\s[tcdjh]', text, re.IGNORECASE):
                    print("✅ 唤醒词识别成功!")
                    wake_word_detected = True
                    break

        except Exception as e:
            print(f"语音识别错误: {e}")
            time.sleep(0.1)

    print("语音唤醒监听结束")

def start_voice_wake():
    """
    启动语音唤醒监听
    :return: 是否启动成功
    """
    global listening_active, wake_word_detected, wake_thread

    if listening_active:
        print("语音唤醒已在运行中")
        return True

    # 初始化服务
    if not init_voice_wake():
        return False

    wake_word_detected = False
    listening_active = True

    # 启动监听线程
    wake_thread = threading.Thread(target=voice_wake_listen, daemon=True)
    wake_thread.start()

    print("语音唤醒服务已启动")
    return True

def stop_voice_wake():
    """
    停止语音唤醒监听
    """
    global listening_active, audio_stream, audio_interface

    listening_active = False

    # 等待线程结束
    if wake_thread and wake_thread.is_alive():
        wake_thread.join(timeout=1.0)

    # 清理资源
    if audio_stream:
        try:
            audio_stream.stop_stream()
            audio_stream.close()
        except:
            pass
        audio_stream = None

    if audio_interface:
        try:
            audio_interface.terminate()
        except:
            pass
        audio_interface = None

    print("语音唤醒服务已停止")

def is_wake_word_detected():
    """
    检查是否检测到唤醒词
    :return: 是否检测到唤醒词
    """
    global wake_word_detected
    if wake_word_detected:
        wake_word_detected = False  # 重置标志
        return True
    return False

def get_wake_status():
    """
    获取语音唤醒状态
    :return: 状态信息
    """
    return {
        "active": listening_active,
        "wake_word_detected": wake_word_detected,
        "model_loaded": recognizer is not None
    }

# 清理函数
def cleanup():
    """清理资源"""
    stop_voice_wake()

if __name__ == "__main__":
    # 测试代码
    try:
        if start_voice_wake():
            print("语音唤醒测试开始，请说 'hello t' 或 'hello c' 等唤醒词")
            while True:
                if is_wake_word_detected():
                    print("🎉 唤醒成功！")
                    break
                time.sleep(0.1)
        else:
            print("语音唤醒启动失败")
    except KeyboardInterrupt:
        print("测试结束")
    finally:
        cleanup()

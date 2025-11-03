import pyaudio
import dashscope
import time
from dashscope.audio.asr import *
import math
import random
import os

# 初始化DashScope API Key
try:
    from ..core.config import get_config
    config = get_config()
    dashscope.api_key = config.ai.dashscope.api_key
except Exception as e:
    print(f"加载配置失败: {e}")
    dashscope.api_key = None

mic = None
stream = None
last_transcription_time = 0
transcription_timeout = 1  # 2秒超时
sentences = {}  # 存储不同sentence id的句子
start_time = 0  # 记录函数开始执行的时间
# stop_mark = 0
translator_started = False  # 跟踪语音识别器的状态

class Callback(TranslationRecognizerCallback):
    def on_open(self) -> None:
        global mic, stream, start_time
        print("TranslationRecognizerCallback open.")
        mic = pyaudio.PyAudio()
        stream = mic.open(
            format=pyaudio.paInt16, channels=1, rate=16000, input=True
        )
        # 记录开始时间
        start_time = time.time()

    def on_close(self) -> None:
        global mic, stream
        print("TranslationRecognizerCallback close.")
        if stream:
            stream.stop_stream()
            stream.close()
        if mic:
            mic.terminate()
        stream = None
        mic = None

    def on_event(
        self,
        request_id,
        transcription_result: TranscriptionResult,
        translation_result: TranslationResult,
        usage,
    ) -> None:
        global last_transcription_time, sentences
        print("request id: ", request_id)
        print("usage: ", usage)

        if translation_result is not None:
            print(
                "translation_languages: ",
                translation_result.get_language_list(),
            )
            english_translation = translation_result.get_translation("en")
            print("sentence id: ", english_translation.sentence_id)
            print("translate to english: ", english_translation.text)

        if transcription_result is not None:
            print("sentence id: ", transcription_result.sentence_id)
            print("transcription: ", transcription_result.text)

            # 保存不同sentence id的句子
            sentence_id = transcription_result.sentence_id
            sentences[sentence_id] = transcription_result.text.strip()

            # 更新最后的转录时间
            if transcription_result.text.strip():
                last_transcription_time = time.time()

callback = Callback()

translator = TranslationRecognizerRealtime(
    model="gummy-realtime-v1",
    format="pcm",
    sample_rate=16000,
    transcription_enabled=True,
    translation_enabled=True,
    translation_target_languages=["en"],
    callback=callback,
)

def get_final_transcription():
    """将所有句子按sentence id顺序拼接"""
    global sentences
    # 按sentence id排序并拼接
    sorted_sentences = sorted(sentences.items())
    final_text = "".join([text for _, text in sorted_sentences])
    sentences = {}
    return final_text

def speech_to_text():
    global translator_started, stream, mic
    try:
        if not translator_started:
            translator.start()
            translator_started = True

        print("请您通过麦克风讲话体验实时语音识别和翻译功能")

        while True:
            global sentences
            # 检查是否超过10秒还未收到任何语音
            if time.time() - start_time > 30 and sentences == {}:
                print("30秒内未接收到任何语音输入，返回None")
                # 清空句子缓存
                sentences = {}
                return None


            if stream:
                data = stream.read(3200, exception_on_overflow=False)
                translator.send_audio_frame(data)

                # 检查是否超时
                if sentences and (time.time() - last_transcription_time > transcription_timeout):
                    # 获取第一个键并检查是否为0
                    first_key = list(sentences.keys())[0] if sentences.keys() else None
                    if first_key == 0 :
                        if translator_started:
                            translator.stop()
                            translator_started = False
                        print("第一个键是0")
                        print("检测到2秒内无新语音输入，停止录音")
                        print(sentences)
                        final_result = get_final_transcription()
                        print("最终转录结果:", final_result)
                        return final_result
                    else:
                        sentences = {}
                        continue
            else:
                break

    except KeyboardInterrupt:
        print("用户中断录音")
        final_result = get_final_transcription()
        if translator_started:
            translator.stop()
            translator_started = False
        if final_result:
            print("最终转录结果:", final_result)
            return final_result
        else:
            return None
    finally:
        # 确保语音识别器被正确停止
        if translator_started:
            try:
                translator.stop()
                translator_started = False
            except Exception as e:
                print(f"停止translator时出错: {e}")
        # 确保资源被正确释放
        if stream:
            stream.stop_stream()
            stream.close()
            stream = None
        if mic:
            mic.terminate()
            mic = None

def process_audio_file_asr(audio_file_path):
    """
    处理音频文件进行语音识别（使用Whisper模型）
    :param audio_file_path: 音频文件路径
    :return: 识别结果文本
    """
    try:
        import os
        print(f"[DEBUG] 开始处理音频文件: {audio_file_path}")
        print(f"[DEBUG] 文件是否存在: {os.path.exists(audio_file_path)}")
        print(f"[DEBUG] 文件大小: {os.path.getsize(audio_file_path) if os.path.exists(audio_file_path) else 'N/A'} bytes")

        # 使用Whisper进行语音识别
        import whisper
        print("[DEBUG] 正在加载Whisper模型...")

        # 使用在线large-v3模型（会自动下载）
        model_name = "large-v3"
        print(f"[DEBUG] 使用模型: {model_name}")

        # 加载Whisper模型
        model = whisper.load_model(model_name)
        print("[DEBUG] Whisper模型加载完成")

        # 进行语音识别
        print("[DEBUG] 正在进行语音识别...")
        result = model.transcribe(audio_file_path, language="zh")
        print(f"[DEBUG] 识别完成，结果类型: {type(result)}")

        # 提取识别结果
        if result and 'text' in result:
            text_result = result['text'].strip()
            print(f"[DEBUG] 识别结果: {text_result}")
            return text_result
        else:
            print("[DEBUG] 识别结果为空")
            return None

    except Exception as e:
        print(f"[DEBUG] ASR处理异常: {type(e).__name__}: {e}")
        import traceback
        print(f"[DEBUG] 完整异常信息:\n{traceback.format_exc()}")
        return None


if __name__ == "__main__":
    print("--------------------------------------------------------------")
    print(speech_to_text())
    time.sleep(2)
    print("--------------------------------------------------------------")
    print(speech_to_text())
    time.sleep(2)
    print("--------------------------------------------------------------")
    print(speech_to_text())
    time.sleep(2)

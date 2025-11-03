from openai import OpenAI
import os
import base64
import random

#  base 64 编码格式
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_response(user_content, path="imgs/test.png"):
    try:
        from ..core.config import get_config
        config = get_config()

        base64_image = encode_image(path)
        client = OpenAI(
            api_key=config.ai.dashscope.api_key,
            base_url=config.ai.dashscope.base_url,
        )
        completion = client.chat.completions.create(
            model="qwen-vl-plus",
            messages=[
                {
                  "role": "user",
                  "content": [
                    {
                      "type": "text",
                      "text": user_content
                    },
                    {
                      "type": "image_url",
                      "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                      }
                    }
                  ]
                }
              ],
              # stream=True,
              # stream_options={"include_usage":True}
            )
        # 提取content内容
        content = completion.choices[0].message.content
        print(content)
        # 不在API服务中保存文件，直接返回结果
        return content
    except Exception as e:
        print(e)
        return "Sorry, I can't understand your image."

if __name__=='__main__':
    get_image_response(input("请输入内容："))

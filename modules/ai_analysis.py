import streamlit as st
from PIL import Image
import base64
import io
import requests

def image_to_base64(image_file):
    img = Image.open(image_file).convert("RGB")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def analyze_crown(image_file, api_key, shade=None):
    img_base64 = image_to_base64(image_file)

    shade_text = f"Target Vita shade: {shade}." if shade else ""

    prompt = f"""You are a professional dental ceramist assistant.
Analyze this dental crown photo and provide recommendations in Russian.

{shade_text}

1. ТЕКУЩИЙ ОТТЕНОК по Vita шкале
2. Цервикальная зона, средняя треть, режущий край
3. ОТКЛОНЕНИЯ от заказанного оттенка
4. КОНКРЕТНЫЙ ПЛАН ДОРАБОТКИ:
   - материал и куда наносить
   - толщина слоя
   - температура обжига

Отвечай на русском. Конкретно и профессионально."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }

    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"DeepSeek ошибка {response.status_code}: {response.text}")

import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import io

def image_to_base64(image_file):
    img = Image.open(image_file).convert("RGB")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def analyze_crown(image_file, api_key, shade=None):
    client = OpenAI(api_key=api_key)
    
    img_base64 = image_to_base64(image_file)
    
    shade_text = f"Заказанный оттенок: {shade}." if shade else ""
    
    prompt = f"""Ты эксперт-зубной техник с 20-летним опытом работы с керамикой Noritake CZR.

Проанализируй фото зубной коронки и дай профессиональное заключение:

{shade_text}

1. ТЕКУЩЕЕ СОСТОЯНИЕ:
   - Определи визуальный оттенок по шкале Vita (A1-D4)
   - Оцени цервикальную зону (насыщенность, хрома)
   - Оцени среднюю треть (мамелоны, опал-эффект)
   - Оцени режущий край (прозрачность)

2. ОТКЛОНЕНИЯ ОТ ИДЕАЛА:
   - Что именно не так
   - Насколько критично

3. КОНКРЕТНЫЕ ДЕЙСТВИЯ:
   - Пошагово что нужно сделать технику
   - Какие материалы использовать
   - Какой обжиг рекомендуется

Отвечай на русском языке. Будь конкретным и практичным."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
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
        max_tokens=1000
    )
    
    return response.choices[0].message.content

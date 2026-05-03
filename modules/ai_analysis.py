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
    
    prompt = f"""You are a professional dental ceramist assistant helping analyze crown photos.

Please analyze this dental crown photo and provide recommendations in Russian language.

{f"Target Vita shade: {shade}" if shade else ""}

Provide analysis in this exact format:

1. ТЕКУЩИЙ ОТТЕНОК:
   - Оттенок по Vita шкале
   - Цервикальная зона (насыщенность)
   - Средняя треть (мамелоны, опал-эффект)
   - Режущий край (прозрачность)

2. ОТКЛОНЕНИЯ:
   - Что именно отличается от заказанного оттенка
   - Насколько критично

3. ПЛАН ДОРАБОТКИ (конкретные шаги):
   - Какой материал нанести и куда
   - Толщина слоя
   - Температура обжига
   - Контроль результата

Answer only in Russian. Be specific and professional."""

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

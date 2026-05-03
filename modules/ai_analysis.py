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
    
    prompt = f"""Ты опытный зубной техник-керамист с 20-летним стажем. 
Специализация: керамика Noritake CZR, эстетическая стоматология.

Перед тобой фото зубной коронки ПОСЛЕ калибровки White Balance.
{f"Заказанный оттенок по Vita: {shade}" if shade else "Оттенок не указан."}

Дай КОНКРЕТНОЕ профессиональное заключение:

1. ТЕКУЩИЙ ОТТЕНОК:
   - Точное значение по Vita (например A2, B1 и т.д.)
   - Цервикальная зона: оттенок, насыщенность хромы (1-4)
   - Средняя треть: мамелоны (выраженные/слабые/отсутствуют), опал-эффект
   - Режущий край: % прозрачности (0-40%), опал-эффект

2. ОТКЛОНЕНИЯ от заказанного оттенка {shade if shade else ""}:
   - Конкретно что не совпадает (например: "цервикальная зона светлее на 1 тон")
   - Критичность: высокая/средняя/низкая

3. ПОШАГОВЫЙ ПЛАН ДОРАБОТКИ:
   Напиши конкретные действия например:
   - "Нанести слой Noritake CZR Cervical Modifier CM3 толщиной 0.3мм в цервикальной зоне"
   - "Добавить опаловую массу OPA в режущей трети"
   - "Обжиг при 920°C, скорость подъёма 55°C/мин"
   - "После обжига проверить оттенок при дневном освещении"

Отвечай ТОЛЬКО на русском. Без воды — только конкретные профессиональные рекомендации."""

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

import streamlit as st
import numpy as np
from PIL import Image
import base64
import requests
import io
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VITA_SHADES = {
    "A1": "Светлый, минимальная хрома, тёплый",
    "A2": "Светло-средний, тёплый",
    "A3": "Средний, выраженная хрома",
    "A3.5": "Средне-тёмный, тёплый",
    "A4": "Тёмный, высокая хрома",
    "B1": "Самый светлый, холодный",
    "B2": "Светлый, нейтральный",
    "B3": "Средний, нейтральный",
    "B4": "Средне-тёмный, нейтральный",
    "C1": "Светлый, сероватый",
    "C2": "Средний, сероватый",
    "C3": "Средне-тёмный, серый",
    "C4": "Тёмный, серый",
    "D2": "Светлый, розоватый",
    "D3": "Средний, розоватый",
    "D4": "Тёмно-розоватый",
}

def image_to_base64(img_array):
    img_pil = Image.fromarray(img_array)
    buffer = io.BytesIO()
    img_pil.save(buffer, format="JPEG", quality=90)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def analyze_with_claude(img_array, target_shade, notes, api_key):
    img_base64 = image_to_base64(img_array)
    shade_text = f"Заказанный оттенок: {target_shade}." if target_shade != "Не указан" else ""
    notes_text = f"Комментарий техника: {notes}" if notes else ""

    prompt = f"""Ты опытный зубной техник-керамист.
Перед тобой фото зубной работы.
На фото могут быть десна, фон, модель — игнорируй их.
Анализируй ТОЛЬКО керамику коронки/коронок.

{shade_text}
{notes_text}

Дай профессиональный анализ:

**ОТТЕНОК ПО VITA:**
- Цервикальная зона: [оттенок + насыщенность]
- Средняя зона: [оттенок + мамелоны]
- Режущая зона: [оттенок + прозрачность %]
- Общий оттенок: [итог]

**ГРАДИЕНТ ЗОН:**
[правильный/нарушен + объяснение]

**ПРОБЛЕМЫ:**
[конкретно что не так или "не выявлено"]

**ПЛАН ДОРАБОТКИ:**
[пошагово что делать технику]

Отвечай на русском. Коротко и профессионально."""

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-opus-4-5",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": img_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    }
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=payload
    )
    if response.status_code == 200:
        return response.json()["content"][0]["text"]
    else:
        raise Exception(f"Ошибка {response.status_code}: {response.text}")

def show_page():
    st.title("Колористика")
    st.info("Загрузи фото коронки — Claude проанализирует оттенок по зонам как опытный техник.")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Фото коронки")
        img_file = st.camera_input("Сфотографировать", key="cam_color")
        if not img_file:
            img_file = st.file_uploader(
                "Или загрузить из галереи",
                type=["jpg","jpeg","png"],
                key="color_upload"
            )
        if img_file:
            st.session_state["color_img"] = img_file
        if st.session_state.get("color_img"):
            st.image(st.session_state["color_img"],
                     use_container_width=True)

    with col2:
        st.subheader("Параметры")
        target_shade = st.selectbox(
            "Заказанный оттенок",
            ["Не указан"] + list(VITA_SHADES.keys()),
            key="target_shade_main"
        )
        notes = st.text_area(
            "Комментарий (необязательно)",
            placeholder="Например: коронка после 3-го обжига, нужно светлее в режущей зоне...",
            height=120
        )
        st.markdown("""
        **Советы для точного анализа:**
        - Чёрный фон — лучший результат
        - Равномерное освещение
        - Коронка в фокусе
        """)

    if st.session_state.get("color_img"):
        st.divider()

        api_key = st.session_state.get("claude_api_key", "")

        if api_key:
            if st.button("Анализировать оттенок", type="primary"):
                with st.spinner("Claude анализирует коронку..."):
                    try:
                        img_array = np.array(
                            Image.open(
                                st.session_state["color_img"]
                            ).convert("RGB")
                        )
                        result = analyze_with_claude(
                            img_array, target_shade, notes, api_key
                        )
                        st.session_state["color_result"] = result
                    except Exception as e:
                        st.error(f"Ошибка: {str(e)}")
        else:
            st.warning("Перейди в Настройки и введи Claude API ключ")

        if st.session_state.get("color_result"):
            st.divider()
            st.subheader("Результат анализа")
            st.markdown(st.session_state["color_result"])

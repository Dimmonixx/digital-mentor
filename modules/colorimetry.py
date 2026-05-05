import streamlit as st
import numpy as np
from PIL import Image
import cv2
import base64
import requests
import io
import os
from streamlit_drawable_canvas import st_canvas

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

def apply_tooth_mask(img_array):
    img_hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(img_hsv,
        np.array([0, 0, 140]),
        np.array([40, 100, 255])
    )
    kernel = np.ones((10,10), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask

def image_to_base64(img_array):
    img_pil = Image.fromarray(img_array)
    buffer = io.BytesIO()
    img_pil.save(buffer, format="JPEG", quality=90)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def analyze_with_claude(img_array, target_shade, api_key):
    img_base64 = image_to_base64(img_array)
    shade_text = f"Заказанный оттенок: {target_shade}." if target_shade != "Не указан" else ""
    prompt = f"""Ты эксперт зубной техник-керамист с 20-летним опытом.
Перед тобой фото зубной коронки — уже обрезанное и очищенное от фона.
Анализируй ТОЛЬКО то что видишь на фото.

{shade_text}

Дай профессиональный анализ:

**ОТТЕНОК ПО VITA:**
- Цервикальная зона: [оттенок + хрома]
- Средняя зона: [оттенок + мамелоны]
- Режущая зона: [оттенок + прозрачность %]
- Общий оттенок: [итог]

**ГРАДИЕНТ ЗОН:**
[правильный/нарушен + почему]

**ПРОБЛЕМЫ:**
[конкретно что не так или не выявлено]

**ПЛАН ДОРАБОТКИ:**
[пошагово что делать технику]

Отвечай на русском. Коротко и по делу."""

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
    st.info("Выдели зону зуба слайдерами — система очистит фон — Claude проанализирует оттенок.")
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
            st.image(st.session_state["color_img"], use_container_width=True)

    with col2:
        st.subheader("Инструкция")
        st.markdown("""
        1. Загрузи фото коронки
        2. Слайдерами выдели только зуб
        3. Система уберёт фон автоматически
        4. Claude определит оттенок по зонам

        Лучший результат на чёрном фоне
        """)
        target_shade = st.selectbox(
            "Заказанный оттенок",
            ["Не указан"] + list(VITA_SHADES.keys()),
            key="target_shade_main"
        )

    if st.session_state.get("color_img"):
        st.divider()
        st.subheader("Выдели зубы")
        st.caption("Нарисуй прямоугольник вокруг зубов мышкой")

        img_temp = Image.open(
            st.session_state["color_img"]
        ).convert("RGB")
        
        canvas_result = st_canvas(
            fill_color="rgba(0, 150, 255, 0.1)",
            stroke_width=2,
            stroke_color="#0096FF",
            background_image=img_temp,
            update_streamlit=True,
            height=400,
            drawing_mode="rect",
            key="canvas_tooth",
        )

        if (canvas_result.json_data is not None and 
            len(canvas_result.json_data["objects"]) > 0):
            obj = canvas_result.json_data["objects"][-1]
            
            img_array = np.array(img_temp)
            h_img, w_img = img_array.shape[:2]
            
            scale_x = w_img / canvas_result.json_data.get("width", w_img)
            scale_y = h_img / 400
            
            x1 = max(0, int(obj["left"] * scale_x))
            y1 = max(0, int(obj["top"] * scale_y))
            x2 = min(w_img, int((obj["left"] + obj["width"]) * scale_x))
            y2 = min(h_img, int((obj["top"] + obj["height"]) * scale_y))
            
            cropped = img_array[y1:y2, x1:x2]
            
            if cropped.size > 0:
                st.image(cropped, 
                         caption="Выделенная зона",
                         use_container_width=True)
                st.session_state["color_cropped"] = cropped

        st.divider()
        api_key = st.session_state.get("claude_api_key", "")

        if api_key:
            if st.button("Анализировать оттенок", type="primary"):
                with st.spinner("Claude анализирует коронку..."):
                    try:
                        img_to_analyze = st.session_state.get(
                            "color_cropped", 
                            np.array(Image.open(
                                st.session_state["color_img"]
                            ).convert("RGB"))
                        )
                        result = analyze_with_claude(
                            img_to_analyze, target_shade, api_key
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

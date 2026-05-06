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

def analyze_with_claude(img_array, target_shade, notes, work_stage, api_key):
    img_base64 = image_to_base64(img_array)
    shade_text = f"Заказанный оттенок: {target_shade}." if target_shade != "Не указан" else ""
    notes_text = f"Комментарий техника: {notes}" if notes else ""
    stage_text = f"Этап работы: {work_stage}." if work_stage != "Не указан" else ""

    prompt = f"""Ты опытный зубной техник-керамист с 20-летним стажем.
У тебя дружелюбный и немного ироничный стиль — как у старшего коллеги который видел всякое.
Например начни с чего-то типа "Ну давай посмотрим что тут получилось..." или 
"Хм, интересное решение..." или "Окей бро, разберём..."

На фото зубная работа. Игнорируй дёсны, фон, модель — анализируй только керамику.

{shade_text}
{stage_text}
{notes_text}

Дай профессиональный анализ по такой структуре:

**ОТТЕНОК ПО VITA:**
- Цервикальная зона: [оттенок + насыщенность хромы]
- Средняя зона: [оттенок + мамелоны есть/нет]
- Режущая зона: [оттенок + прозрачность %]
- Общий оттенок: [итог]

**ГРАДИЕНТ И ГАРМОНИЯ:**
- Градиент зон: [правильный/нарушен + почему]
- Симметрия: [оцени если видно несколько зубов]
- Гармония с соседними зубами: [если видны]
- Размер и пропорции: [оцени]
- Краевое прилегание: [оцени если видно]

**ПРОБЛЕМЫ:**
[конкретно что не так или "Всё чисто, бро"]

**ПЛАН КОРРЕКЦИИ:**

🔴 РАДИКАЛЬНОЕ (спиливание/добавление керамики, перепечь):
[только если без этого не обойтись — конкретные действия]
[если не нужно — напиши "Не требуется"]

🟡 ПОВЕРХНОСТНОЕ (красители, глазурь, минимальная коррекция):
[что можно исправить без переделки]
[если не нужно — напиши "Не требуется"]

Отвечай на русском. Будь конкретным, дружелюбным и ироничным."""

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
    st.title("🎨 Анализ работы")
    st.info("Загрузи фото работы — разберём форму, оттенок, градиент зон и что с этим делать.")

    # Кнопка сброса
    if st.button("🗑️ Очистить и начать заново"):
        for key in ["color_img", "color_result", "color_chat"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.divider()

    st.markdown("""
    <style>
    /* Убираем красный hover на кнопках загрузки */
    .stFileUploader button:hover {
        border-color: #1a3a5c !important;
        color: #1a3a5c !important;
    }
    .stFileUploader button {
        border-color: #888 !important;
    }
    /* Убираем красную обводку с полей */
    .stTextArea textarea:focus {
        border-color: #1a3a5c !important;
        box-shadow: 0 0 0 1px #1a3a5c !important;
    }
    .stTextArea textarea {
        border: 1px solid #ddd !important;
    }
    /* Камера кнопка */
    .stCameraInput button:hover {
        border-color: #1a3a5c !important;
        color: #1a3a5c !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📷 Фото работы")
        img_file = st.camera_input("Сфотографировать", key="cam_color")
        if not img_file:
            img_file = st.file_uploader(
                "Или загрузить из галереи",
                type=["jpg","jpeg","png"],
                key="color_upload"
            )
        if img_file:
            st.session_state["color_img"] = img_file

    with col2:
        if st.session_state.get("color_img"):
            st.subheader("Превью")
            img_temp = Image.open(
                st.session_state["color_img"]
            ).convert("RGB")
            w, h = img_temp.size
            max_w = 400
            if w > max_w:
                ratio = max_w / w
                img_temp = img_temp.resize(
                    (max_w, int(h * ratio))
                )
            st.image(img_temp, use_container_width=True)
        else:
            st.subheader("Превью")
            st.markdown("""
            <div style="height:200px; background:#f0f2f6; 
                border-radius:10px; display:flex; 
                align-items:center; justify-content:center;
                color:#888; font-size:14px;">
                Фото появится здесь
            </div>
            """, unsafe_allow_html=True)

    if st.session_state.get("color_img"):
        st.divider()

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            target_shade = st.selectbox(
                "Заказанный оттенок",
                ["Не указан"] + list(VITA_SHADES.keys()),
                key="target_shade_main"
            )
        with col_p2:
            work_stage = st.selectbox(
                "Этап работы",
                ["Не указан", "Бисквит после 1-го обжига",
                 "После 2-го обжига", "Финальный обжиг",
                 "Готовая работа (глазурь)"],
                key="work_stage"
            )

        notes = st.text_area(
            "Комментарий к работе (необязательно)",
            placeholder="Например: 2 центральных резца, пациент 35 лет, просит натуральный вид...",
            height=80
        )

        api_key = st.session_state.get("claude_api_key", "")

        if api_key:
            if st.button("🔍 Анализ работы", type="primary"):
                with st.spinner("Смотрим что тут получилось..."):
                    try:
                        img_array = np.array(
                            Image.open(
                                st.session_state["color_img"]
                            ).convert("RGB")
                        )
                        result = analyze_with_claude(
                            img_array, target_shade,
                            notes, work_stage, api_key
                        )
                        st.session_state["color_result"] = result
                        st.session_state["color_chat"] = []
                    except Exception as e:
                        st.error(f"Ошибка: {str(e)}")
        else:
            st.warning("Перейди в ⚙️ Настройки и введи Claude API ключ")

    if st.session_state.get("color_result"):
        st.divider()
        st.subheader("📋 Результат анализа")
        st.markdown(st.session_state["color_result"])

        st.divider()
        st.subheader("💬 Вопросы по работе")
        st.caption("Есть вопросы по анализу? Спроси — отвечу.")

        if "color_chat" not in st.session_state:
            st.session_state["color_chat"] = []

        for msg in st.session_state["color_chat"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if question := st.chat_input("Спроси что-то по работе..."):
            st.session_state["color_chat"].append(
                {"role": "user", "content": question}
            )
            api_key = st.session_state.get("claude_api_key", "")
            if api_key:
                with st.spinner("Думаю..."):
                    try:
                        context = st.session_state["color_result"]
                        headers = {
                            "x-api-key": api_key,
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json"
                        }
                        payload = {
                            "model": "claude-opus-4-5",
                            "max_tokens": 512,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": f"""Ты опытный зубной техник-керамист с дружелюбным и немного ироничным стилем общения.
Ранее ты дал такой анализ работы:

{context}

Теперь техник задаёт уточняющий вопрос: {question}

Отвечай на русском, дружелюбно и по делу."""
                                }
                            ]
                        }
                        response = requests.post(
                            "https://api.anthropic.com/v1/messages",
                            headers=headers,
                            json=payload
                        )
                        if response.status_code == 200:
                            answer = response.json()[
                                "content"
                            ][0]["text"]
                            st.session_state["color_chat"].append(
                                {"role": "assistant", "content": answer}
                            )
                            st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка: {str(e)}")

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

def analyze_with_claude(img_array, target_shade, notes, work_stage, analysis_type, api_key):
    img_base64 = image_to_base64(img_array)
    shade_text = f"Заказанный оттенок: {target_shade}." if target_shade != "Не указан" else ""
    notes_text = f"Комментарий техника: {notes}" if notes else ""
    stage_text = f"Этап работы: {work_stage}." if work_stage != "Не указан" else ""
    type_text = f"Тип анализа: {analysis_type}."

    prompt = f"""Ты опытный зубной техник-керамист с 20-летним стажем.
Стиль: честный, профессиональный, без лести. Цель — рост техника.

{shade_text}
{stage_text}
{type_text}
{notes_text}

СТРОГИЕ ПРАВИЛА АНАЛИЗА:

1. СИММЕТРИЯ — никогда не пиши "симметричная работа" если есть 
   заметные отличия. Используй градацию:
   - "практически идентичные" — отличия минимальны
   - "близкие по форме" — есть небольшие отличия
   - "заметные различия" — отличия очевидны
   - "значительная асимметрия" — грубые отличия
   Порог: от 25% различий — уже не "симметричная"

2. СЕПАРАЦИЯ — всегда оценивай детально:
   - "Аккуратная" — тонкий диск, касание экватора, характеризация красками
   - "Топорная" — прорезана сверху вниз, без касания экватора
   - "Минимальная" — есть но сливается с зубами, эффект забора
   - "Отсутствует" — зубы слиплись полностью
   НИКОГДА не пиши просто "нет сепарации" если промежутки есть

3. ПРОЗРАЧНОСТЬ И МАМЕЛОНЫ — если их нет, добавляй контекст:
   - "Прозрачность отсутствует — если это не было оговорено изначально, 
     режущий край выглядит глухо"
   - "Мамелоны не выражены — для данного типа работы это [норма/недостаток]"

4. ПРОПОРЦИИ — измеряй ТОЧНО:
   - Норма ширина/высота центрального резца: 75-80%
   - Если единицы шире двоек — это грубая ошибка, называй прямо
   - "на грани нормы" пиши только если реально на грани

5. ДЕСНА — если не видна полностью: "не видна на фото"
   Не придумывай контур, зениты, сосочки если их нет в кадре

6. НЕ ПИШИ "заказчик" — техник проверяет свою работу

Структура анализа:

**ПЕРВОЕ ВПЕЧАТЛЕНИЕ:**
[честно — не льсти]

**ОТТЕНОК ПО VITA:**
- Цервикальная зона: [оттенок + хрома]
- Средняя зона: [оттенок + что видно внутри]
- Режущая зона: [оттенок + прозрачность % + опал — с контекстом если нет]
- Общий оттенок: [итог]

**МОРФОЛОГИЯ И ФОРМА:**
- Поверхностная текстура: [перикиматы есть/нет]
- Медиальные/дистальные валики: [выражены/сглажены]
- Мамелоны: [есть/не выражены — с контекстом]
- Пропорции: [ТОЧНО — соотношение ширины/высоты, сравни единицы и двойки]
- Форма: [тип + соответствие возрасту]

**СЕПАРАЦИЯ:**
- Тип: [аккуратная/топорная/минимальная/отсутствует]
- Межзубные промежутки: [описание]
- Характеризация контактных точек: [есть/нет]
- Вывод: [что улучшить]

**СИММЕТРИЯ И ГАРМОНИЯ:**
- 11 vs 21: [конкретные отличия с градацией из правила 1]
- 12 vs 22: [конкретные отличия]
- Осевые наклоны: [правильные/нарушены]
- Режущие края: [уровень]
- Общая гармония: [честная оценка с градацией]

**СОСТОЯНИЕ ДЕСНЫ:**
[если не видна — "Десна не видна на фото, оценить невозможно"]
[если видна — контур, зенит, сосочки, треугольники]

**ПРОБЛЕМЫ:**
[нумерованный список — от критичных к мелким]
[для каждой проблемы — степень: критично/важно/желательно исправить]

**ПЛАН КОРРЕКЦИИ:**

🔴 РАДИКАЛЬНОЕ (переделка/спиливание/перепечь):
[если нужно — конкретно что и где]
[если не нужно — "Не требуется"]

🟡 ПОВЕРХНОСТНОЕ (красители/глазурь/сепарация):
[конкретные действия]
[если не нужно — "Не требуется"]

Отвечай на русском. Профессионально и честно.
Помни: задача не похвалить а улучшить работу."""

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-opus-4-5",
        "max_tokens": 1500,
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

        analysis_type = st.selectbox(
            "Тип анализа",
            [
                "Общий анализ работы",
                "Проверить цвет и оттенок",
                "Проверить форму и морфологию",
                "Оценить симметрию",
                "Просто похвастаться 😎",
                "Найти косяки",
                "Финальная проверка перед сдачей"
            ],
            key="analysis_type"
        )
        notes = st.text_area(
            "Комментарий к работе (необязательно)",
            placeholder="Например: 2 центральных резца, пациент 35 лет, блич BL1...",
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
                            notes, work_stage, 
                            analysis_type, api_key
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

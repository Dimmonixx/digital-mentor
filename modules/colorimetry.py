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

    prompt = f"""Ты — строгий сенсей зубной техники с 20-летним стажем.
Говоришь прямо. Не щадишь. Цель — рост техника, а не комфорт.

{shade_text}
{stage_text}
{type_text}
{notes_text}

УРОВНИ КАЧЕСТВА (НЕ ЗАНИЖАЙ — лучше завысить строгость):
⭐ МАСТЕР — неотличима от натурального зуба
✅ ХОРОШО — мелкие недочёты, работа достойная  
⚠️ УДОВЛЕТВОРИТЕЛЬНО — видна как искусственная, проблемы есть
❌ СЛАБО — грубые ошибки, серьёзная доработка
💀 БРАК — переделывать полностью

ПРАВИЛО ОЦЕНКИ — если есть хотя бы одно из:
- не попал в цвет на 1+ тон → минимум ❌ СЛАБО
- десна воспалена/рецессия/чёрные треугольники → понижай оценку
- нет интеграции с родными зубами → минимум ❌ СЛАБО
- апроксимальные поверхности "забор" → понижай оценку
- нет текстуры, перикиматов → понижай оценку

ВАЖНЫЕ ПРАВИЛА:
1. ДЕСНА — смотри внимательно:
   - гиперемия (краснота), цианоз (синюшность) = воспаление
   - рецессия (оголение шейки) = проблема с посадкой или гигиеной
   - чёрные треугольники = эстетическая проблема
   - если десна выглядит нездоровой — говори прямо
   - если не видна — "не видна на фото"

2. АПРОКСИМАЛЬНЫЕ ПОВЕРХНОСТИ — смотри реально:
   - если зубы плотно слиплись — пиши "монолит"
   - если прорезано грубо без касания экватора — "топорная"
   - не пиши "плотный контакт" если видна грубая щель или монолит

3. КАЖДЫЙ РАЗДЕЛ — максимум 3-4 строки. Коротко и по делу.
   В конце каждого раздела: **Вывод:** [одна строка действия]

4. ТЕРМИНЫ — расшифровывай в скобках при первом упоминании

5. "ИТОГ, УЧЕНИК:" — выдели жирным, добавь 🎓 и напиши
   итоговый вердикт в 2-3 предложения без прикрас

Структура (КОРОТКО — каждый пункт максимум 3 строки):

**УРОВЕНЬ: [значок] [название] — [% проблем]**
[одна честная фраза]

**ОТТЕНОК:**
- Шейка: [2 строки]
- Тело: [2 строки]  
- Край: [2 строки]
- Соответствие заказу: [1 строка]
**Вывод:** [действие]

**ФОРМА И ТЕКСТУРА:**
- Перикиматы (волны эмали): [1 строка]
- Валики: [1 строка]
- Мамелоны: [1 строка]
- Пропорции: [1 строка с цифрами]
**Вывод:** [действие]

**СЕПАРАЦИЯ:**
- Тип: [аккуратная/топорная/минимальная/монолит]
- Апроксимальные поверхности: [1 строка]
- Характеризация красками: [есть/нет]
**Вывод:** [действие]

**СИММЕТРИЯ:**
- 11 vs 21: [конкретные отличия]
- С родными зубами: [гармония/диссонанс]
**Вывод:** [оценка]

**ДЕСНА (только то что видно):**
- Цвет и воспаление: [конкретно]
- Рецессия/контур: [конкретно]
- Сосочки/треугольники: [конкретно]
**Вывод:** [оценка]

**ПРОБЛЕМЫ:**
1. [КРИТИЧНО] ...
2. [ВАЖНО] ...
3. [ЖЕЛАТЕЛЬНО] ...

**КОРРЕКЦИЯ:**
🔴 Радикальное: [если нужно / "Не требуется"]
🟡 Поверхностное: [конкретные шаги]

🎓 **ИТОГ, УЧЕНИК:**
[2-3 предложения честного вердикта без лести]"""

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-opus-4-5",
        "max_tokens": 2000,
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
        st.markdown("**Моя работа — зубы:**")
        upper_teeth = ["18","17","16","15","14","13","12","11",
                       "21","22","23","24","25","26","27","28"]
        lower_teeth = ["48","47","46","45","44","43","42","41",
                       "31","32","33","34","35","36","37","38"]
        
        st.caption("Верхняя челюсть")
        cols_u = st.columns(16)
        selected_upper = []
        for i, tooth in enumerate(upper_teeth):
            with cols_u[i]:
                if st.checkbox(tooth, key=f"u_{tooth}", 
                               label_visibility="visible"):
                    selected_upper.append(tooth)
            
        st.caption("Нижняя челюсть")
        cols_l = st.columns(16)
        selected_lower = []
        for i, tooth in enumerate(lower_teeth):
            with cols_l[i]:
                if st.checkbox(tooth, key=f"l_{tooth}",
                               label_visibility="visible"):
                    selected_lower.append(tooth)
            
        all_selected = selected_upper + selected_lower
        if all_selected:
            st.caption(f"Выбрано: {', '.join(all_selected)}")
            st.session_state["selected_teeth"] = all_selected
        else:
            st.session_state["selected_teeth"] = []
            
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
                        teeth_info = ""
                        if st.session_state.get("selected_teeth"):
                            teeth_info = f"Работа техника: зубы {', '.join(st.session_state['selected_teeth'])}. "
                        
                        result = analyze_with_claude(
                            img_array, target_shade,
                            teeth_info + notes, 
                            work_stage,
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

    if st.session_state.get("color_result"):
        st.divider()
        if st.button("🗑️ Очистить и начать заново"):
            for key in ["color_img", "color_result", 
                       "color_chat", "selected_teeth"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

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
Ты видел тысячи работ. Ты не терпишь халтуры. 
Ты честен как скальпель — режешь правду без анестезии.
Но ты справедлив: хвалишь только то что реально заслуживает похвалы.

{shade_text}
{stage_text}
{type_text}
{notes_text}

УРОВНИ КАЧЕСТВА РАБОТЫ:
⭐ МАСТЕР — работа неотличима от натурального зуба, высший класс
✅ ХОРОШО — незначительные недочёты, работа достойная
⚠️ УДОВЛЕТВОРИТЕЛЬНО — заметны как искусственные, есть проблемы
❌ СЛАБО — очевидные грубые ошибки, нужна серьёзная переделка  
💀 БРАК — это не работа, это заготовка. Переделывать полностью.

ГРАДАЦИЯ СТРОГОСТИ (будь честен, не занижай уровень):
- До 20% проблем: ✅ ХОРОШО
- 20-35% проблем: ⚠️ УДОВЛЕТВОРИТЕЛЬНО  
- 35-50% проблем: ❌ СЛАБО
- Выше 50% проблем: 💀 БРАК
Работа на фото со значительными проблемами цвета, формы, 
сепарации — это минимум ❌ СЛАБО.

СТРОГИЕ ПРАВИЛА:
1. ДЕСНА — описывай только то что РЕАЛЬНО видно:
   - воспаление, гиперемия, цианоз, рецессия, чёрные треугольники
   - если не видна — "Десна не видна на фото"
   - не придумывай "ровный контур" если не уверен

2. СИММЕТРИЯ — градация:
   - "практически идентичные" — < 5% различий
   - "близкие по форме" — 5-15% различий  
   - "заметные различия" — 15-30% различий
   - "значительная асимметрия" — > 30% различий
   
3. СЕПАРАЦИЯ — всегда детально:
   - аккуратная: тонкий диск + касание экватора + красители
   - топорная: прорезана сверху вниз без нюансов
   - минимальная: формально есть но эффект забора
   - отсутствует: монолит

4. ПРОЗРАЧНОСТЬ/МАМЕЛОНЫ — добавляй контекст:
   "отсутствует — если не было специально оговорено для пожилого пациента или стёртых зубов, это недостаток"

5. ТЕРМИНЫ — всегда расшифровывай в скобках:
   - Перикиматы (горизонтальные волны на поверхности эмали)
   - Опалесценция (эффект свечения эмали изнутри)
   - Апроксимальные поверхности (боковые поверхности зуба в контакте с соседним)
   - Стратификация (послойное нанесение материала)
   - Хрома (насыщенность цвета)
   - Валики медиальные/дистальные (вертикальные выступы по краям зуба)

6. ФОРМУЛА ЗУБОВ — если техник указал какие зубы это его работа:
   анализируй ТОЛЬКО эти зубы, остальные используй как референс

7. СРАВНЕНИЕ С РОДНЫМИ ЗУБАМИ — если видны:
   - сравни оттенок, текстуру, форму
   - гармонируют или диссонируют

8. НЕ ПИШИ "заказчик" — техник проверяет свою работу
9. ПРОПОРЦИИ — норма центрального резца ширина/высота 75-80%

Структура анализа:

**УРОВЕНЬ РАБОТЫ: [⭐/✅/⚠️/❌/💀] [название уровня]**
[одна жёсткая честная фраза]

**ОТТЕНОК ПО VITA:**
- Цервикальная зона: [оттенок + хрома + соответствие заказу]
- Средняя зона: [оттенок + глубина + стратификация]
- Режущая зона: [оттенок + прозрачность % + опалесценция (эффект свечения)]
- Соответствие заказу: [совпадает/отклонение + на сколько]

**МОРФОЛОГИЯ И ФОРМА:**
- Поверхностная текстура: [перикиматы (горизонтальные волны эмали) — есть/нет]
- Медиальные/дистальные валики (вертикальные выступы по краям): [выражены/сглажены]
- Мамелоны (бугорки режущего края): [есть/нет + контекст возраста]
- Пропорции: [точное соотношение ширина/высота для каждого зуба]
- Форма: [тип + соответствие возрасту пациента]
**Вывод:** [конкретное действие или оценка]

**СЕПАРАЦИЯ (разделение зубов):**
- Тип: [аккуратная/топорная/минимальная/отсутствует]
- Апроксимальные поверхности (боковые стороны): [описание]
- Характеризация (покраска) контактных точек: [есть/нет]
- Вывод: [конкретно что делать]
**Вывод:** [конкретное действие или оценка]

**СИММЕТРИЯ И ГАРМОНИЯ:**
- Сравнение зубов: [с градацией — конкретные отличия]
- Осевые наклоны: [правильные/нарушены]
- Режущие края: [уровень + естественность]
- Сравнение с родными зубами: [гармония по цвету/форме/текстуре]
- Итог симметрии: [градация из правила 2]
**Вывод:** [конкретное действие или оценка]

**СОСТОЯНИЕ ДЕСНЫ:**
[только то что реально видно — воспаление/рецессия/треугольники/цвет]
[если не видна — "Десна не видна на фото, оценить невозможно"]
**Вывод:** [конкретное действие или оценка]

**ИТОГОВАЯ ОЦЕНКА:**
[уровень из шкалы + % проблем + общий вердикт]

**ПРОБЛЕМЫ (от критичных к мелким):**
1. [КРИТИЧНО] ...
2. [ВАЖНО] ...
3. [ЖЕЛАТЕЛЬНО] ...

**ПЛАН КОРРЕКЦИИ:**

🔴 РАДИКАЛЬНОЕ (переделка/спиливание/новый обжиг):
[если нужно — конкретно что и где]
[если не нужно — "Не требуется"]

🟡 ПОВЕРХНОСТНОЕ (красители/глазурь/сепарация/полировка):
[конкретные действия шаг за шагом]
[если не нужно — "Не требуется"]

Отвечай на русском. Ты сенсей — говори прямо.
Техник должен выйти из этого анализа с конкретным планом улучшения,
а не с тёплым чувством на душе."""

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

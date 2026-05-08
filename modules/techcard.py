import streamlit as st
import requests
import base64
import io
from PIL import Image
import numpy as np

def image_to_base64(img):
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=90)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def generate_techcard(data, api_key, ref_image=None):
    
    content = []
    
    if ref_image is not None:
        img_base64 = image_to_base64(ref_image)
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": img_base64
            }
        })
    
    prompt = f"""Ты опытный зубной техник-керамист с 20-летним стажем.
Составь профессиональную тех-карту нанесения керамики на основе данных.

ДАННЫЕ РАБОТЫ:
- Зубы: {data['teeth']}
- Заказанный оттенок: {data['shade']}
- Тип работы: {data['work_type']}
- Возраст пациента: {data['age']}
- Тип каркаса: {data['framework']}

НАБЛЮДЕНИЯ ПО РЕФЕРЕНСНОМУ ЗУБУ:
Цервикальная зона: {data['cervical']}
Средняя зона: {data['middle']}
Режущий край: {data['incisal']}
Текстура поверхности: {data['texture']}
Особенности: {data['features']}

{"На фото — референсный зуб для точного повторения. Анализируй его тщательно." if ref_image is not None else ""}

Составь тех-карту строго по этой структуре:

## ТЕХ-КАРТА НАНЕСЕНИЯ

**Работа:** {data['teeth']} | **Оттенок:** {data['shade']} | **Тип:** {data['work_type']}

---

### 1. ПОДГОТОВКА КАРКАСА
[что нужно сделать с каркасом перед нанесением]

---

### 2. НАНЕСЕНИЕ ПО ЗОНАМ

**Цервикальная зона (шейка):**
- Масса: [тип + рекомендуемый оттенок]
- Объём: [толщина слоя]
- Техника: [способ нанесения]
- Цель: [чего добиваемся]

**Средняя зона (тело):**
- Дентиновое ядро: [масса + оттенок]
- Эмалевое перекрытие: [масса + оттенок]
- Техника: [способ]
- Цель: [результат]

**Режущая зона:**
- Масса: [тип]
- Прозрачность: [%]
- Опал: [нужен/нет + где]
- Техника: [способ]

---

### 3. ХАРАКТЕРИЗАЦИЯ
- Вертикальные элементы: [трещины/желобки — где и как]
- Горизонтальные элементы: [перикиматы — нужны/нет]
- Цветовые акценты: [красители — где и какие]
- Белые пятна/эффекты: [нужны/нет]

---

### 4. СЕПАРАЦИЯ
- Медиальная: [техника + красители]
- Дистальная: [техника + красители]
- Апроксимальные поверхности: [как обработать]

---

### 5. ФИНАЛЬНАЯ ОБРАБОТКА
- Глазурь: [нужна/нет + тип]
- Полировка: [где и чем]
- Матирование: [где нужно]
- Финальный контроль: [на что смотреть]

---

### 6. КОНТРОЛЬНЫЕ ТОЧКИ
До финального обжига проверить:
- [ ] Оттенок в шейке соответствует референсу
- [ ] Градиент плавный без резких переходов
- [ ] Режущий край правильная прозрачность
- [ ] Сепарация читается но не режет глаз
- [ ] Текстура соответствует возрасту

---

### ⚠️ ВАЖНО ДЛЯ ЭТОЙ РАБОТЫ:
[3-5 специфических предупреждений для данного кейса]

Отвечай на русском. Конкретно и профессионально.
Термины расшифровывай в скобках."""

    content.append({"type": "text", "text": prompt})
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-opus-4-5",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": content}]
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
    st.title("📋 Тех-карта")
    st.info("Опиши работу и референсный зуб — получи пошаговую карту нанесения керамики.")

    if st.button("🗑️ Новая карта"):
        for key in ["techcard_result"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📷 Фото референсного зуба")
        st.caption("Загрузи фото соседнего зуба — Claude проанализирует его")
        ref_file = st.camera_input("Сфотографировать", key="cam_ref")
        if not ref_file:
            ref_file = st.file_uploader(
                "Или загрузить из галереи",
                type=["jpg","jpeg","png"],
                key="ref_upload"
            )
        if ref_file:
            st.session_state["ref_img"] = ref_file
            st.image(ref_file, use_container_width=True)

    with col2:
        st.subheader("⚙️ Параметры работы")

        teeth_input = st.text_input(
            "Зубы (формула)",
            placeholder="Например: 11, 21 или 14-16",
            key="teeth_input"
        )

        shade = st.selectbox(
            "Заказанный оттенок",
            ["A1","A2","A3","A3.5","A4",
             "B1","B2","B3","B4",
             "C1","C2","C3","C4",
             "D2","D3","D4",
             "BL1","BL2","BL3","BL4"],
            key="tc_shade"
        )

        work_type = st.selectbox(
            "Тип работы",
            ["Коронка МК (металлокерамика)",
             "Коронка безметалловая (циркон)",
             "Коронка e.max",
             "Винир керамический",
             "Винир e.max",
             "Мостовидный протез МК",
             "Мостовидный протез безметалловый"],
            key="tc_work_type"
        )

        age_group = st.selectbox(
            "Возраст пациента",
            ["Молодой (18-30 лет) — выраженные мамелоны, яркий опал",
             "Средний (30-50 лет) — умеренная морфология",
             "Зрелый (50+ лет) — сглаженная морфология, стёртость"],
            key="tc_age"
        )

        framework = st.selectbox(
            "Тип каркаса",
            ["Металл (МК)",
             "Диоксид циркония белый",
             "Диоксид циркония анатомический",
             "Прессованная керамика e.max"],
            key="tc_framework"
        )

    st.divider()
    st.subheader("🔬 Наблюдения по референсному зубу")
    st.caption("Опиши что видишь — чем точнее, тем лучше тех-карта")

    col3, col4 = st.columns(2)

    with col3:
        cervical = st.text_area(
            "Цервикальная зона (шейка)",
            placeholder="Например: тёплое дентиновое ядро A3, насыщенность средняя, переход плавный...",
            height=100,
            key="tc_cervical"
        )
        middle = st.text_area(
            "Средняя зона (тело)",
            placeholder="Например: дентин сужается к центру, лёгкая прозрачность по краям валиков...",
            height=100,
            key="tc_middle"
        )

    with col4:
        incisal = st.text_area(
            "Режущий край",
            placeholder="Например: умеренная прозрачность 15-20%, без голубого опала, волнистый контур...",
            height=100,
            key="tc_incisal"
        )
        texture = st.text_area(
            "Текстура поверхности",
            placeholder="Например: перикиматы сглажены, лёгкий микрорельеф, вертикальный желобок...",
            height=100,
            key="tc_texture"
        )

    features = st.text_area(
        "Особенности и дополнения",
        placeholder="Трещины, белые пятна, характеризация, асимметрия, пожелания врача...",
        height=80,
        key="tc_features"
    )

    st.divider()

    api_key = st.session_state.get("claude_api_key", "")

    if api_key:
        if st.button("📋 Сгенерировать тех-карту", type="primary"):
            if not teeth_input:
                st.warning("Укажи формулу зубов")
            else:
                with st.spinner("Составляю тех-карту..."):
                    try:
                        ref_image = None
                        if st.session_state.get("ref_img"):
                            ref_image = Image.open(
                                st.session_state["ref_img"]
                            ).convert("RGB")

                        data = {
                            "teeth": teeth_input,
                            "shade": shade,
                            "work_type": work_type,
                            "age": age_group,
                            "framework": framework,
                            "cervical": cervical or "не указано",
                            "middle": middle or "не указано",
                            "incisal": incisal or "не указано",
                            "texture": texture or "не указано",
                            "features": features or "не указано"
                        }

                        result = generate_techcard(data, api_key, ref_image)
                        st.session_state["techcard_result"] = result
                    except Exception as e:
                        st.error(f"Ошибка: {str(e)}")
    else:
        st.warning("Перейди в ⚙️ Настройки и введи Claude API ключ")

    if st.session_state.get("techcard_result"):
        st.divider()
        st.subheader("📋 Тех-карта")
        st.markdown(st.session_state["techcard_result"])

        if st.button("⬇️ Скачать тех-карту"):
            result_text = st.session_state["techcard_result"]
            st.download_button(
                label="Скачать как текст",
                data=result_text,
                file_name=f"techcard_{teeth_input}_{shade}.txt",
                mime="text/plain"
            )

        st.divider()
        if st.button("🗑️ Новая карта", key="clear_bottom"):
            for key in ["techcard_result", "ref_img"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

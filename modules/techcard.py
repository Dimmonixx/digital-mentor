import streamlit as st
import requests
import base64
import io
from PIL import Image


def image_to_base64(img):
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=90)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def analyze_reference(img, api_key, tooth_ref=""):
    img_base64 = image_to_base64(img)
    tooth_text = f"Анализируй зуб {tooth_ref}." if tooth_ref else ""

    prompt = f"""Ты опытный зубной техник. {tooth_text}
Анализируй ТОЛЬКО указанный зуб как референс.

ВАЖНО ПРО ОРИЕНТАЦИЮ:
- Зуб стоит ВЕРТИКАЛЬНО
- ШЕЙКА (цервикальная зона) — это часть где зуб выходит из десны
- РЕЖУЩИЙ КРАЙ — это противоположный конец зуба (острый край)
- Средняя треть — между шейкой и режущим краем

Заполни каждое поле КОРОТКО (2-3 предложения):

ЦЕРВИКАЛЬНАЯ_ЗОНА: [оттенок, насыщенность хромы, характер дентинного ядра у шейки]
СРЕДНЯЯ_ЗОНА: [переход дентина, валики, глубина цвета]
РЕЖУЩИЙ_КРАЙ: [прозрачность %, опал, форма края, мамелоны]
ТЕКСТУРА: [перикиматы есть/нет, микрорельеф, вертикальные элементы]
ОСОБЕННОСТИ: [трещины, белые пятна, характеризация, возрастные особенности]

Отвечай СТРОГО в этом формате. Каждый пункт на отдельной строке."""

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-opus-4-5",
        "max_tokens": 800,
        "messages": [{
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
                {"type": "text", "text": prompt}
            ]
        }]
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


def parse_reference_analysis(text):
    result = {
        "cervical": "",
        "middle": "",
        "incisal": "",
        "texture": "",
        "features": ""
    }

    key_map = {
        "ЦЕРВИКАЛЬНАЯ_ЗОНА": "cervical",
        "СРЕДНЯЯ_ЗОНА": "middle",
        "РЕЖУЩИЙ_КРАЙ": "incisal",
        "ТЕКСТУРА": "texture",
        "ОСОБЕННОСТИ": "features"
    }

    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        for kw, field in key_map.items():
            if kw in line and ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    result[field] = parts[1].strip()
                break

    if not any(result.values()):
        result["features"] = text

    return result


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
Составь профессиональную тех-карту нанесения керамики.

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

{"На фото — референсный зуб. Анализируй его тщательно." if ref_image else ""}

Составь тех-карту по структуре:

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
- [ ] Оттенок в шейке соответствует референсу
- [ ] Градиент плавный без резких переходов
- [ ] Режущий край правильная прозрачность
- [ ] Сепарация читается но не режет глаз
- [ ] Текстура соответствует возрасту

---

### ВАЖНО ДЛЯ ЭТОЙ РАБОТЫ:
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
    st.info("Раздел в разработке — скоро здесь появится функционал")

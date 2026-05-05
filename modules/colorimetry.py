import streamlit as st
import numpy as np
from PIL import Image
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VITA_SHADES = {
    "A1": {"L": 78, "a": 1.5, "b": 18, "description": "Светлый, минимальная хрома"},
    "A2": {"L": 74, "a": 2.0, "b": 22, "description": "Светло-средний, тёплый"},
    "A3": {"L": 70, "a": 2.5, "b": 26, "description": "Средний, выраженная хрома"},
    "A3.5": {"L": 67, "a": 3.0, "b": 28, "description": "Средне-тёмный"},
    "A4": {"L": 63, "a": 3.5, "b": 30, "description": "Тёмный, высокая хрома"},
    "B1": {"L": 80, "a": 0.5, "b": 16, "description": "Самый светлый, холодный"},
    "B2": {"L": 75, "a": 1.0, "b": 18, "description": "Светлый, нейтральный"},
    "B3": {"L": 70, "a": 1.5, "b": 22, "description": "Средний, нейтральный"},
    "B4": {"L": 65, "a": 2.0, "b": 24, "description": "Средне-тёмный, нейтральный"},
    "C1": {"L": 75, "a": 1.0, "b": 14, "description": "Светлый, сероватый"},
    "C2": {"L": 70, "a": 1.5, "b": 16, "description": "Средний, сероватый"},
    "C3": {"L": 65, "a": 2.0, "b": 18, "description": "Средне-тёмный, серый"},
    "C4": {"L": 60, "a": 2.5, "b": 20, "description": "Тёмный, серый"},
    "D2": {"L": 74, "a": 1.5, "b": 20, "description": "Светлый, розоватый"},
    "D3": {"L": 69, "a": 2.0, "b": 22, "description": "Средний, розоватый"},
    "D4": {"L": 64, "a": 2.5, "b": 24, "description": "Тёмно-розоватый"},
}

def rgb_to_lab(rgb):
    r, g, b = rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0
    
    def linearize(c):
        return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
    
    r, g, b = linearize(r), linearize(g), linearize(b)
    
    X = r*0.4124 + g*0.3576 + b*0.1805
    Y = r*0.2126 + g*0.7152 + b*0.0722
    Z = r*0.0193 + g*0.1192 + b*0.9505
    
    X, Y, Z = X/0.95047, Y/1.00000, Z/1.08883
    
    def f(t):
        return t**(1/3) if t > 0.008856 else 7.787*t + 16/116
    
    L = 116*f(Y) - 16
    a = 500*(f(X) - f(Y))
    b_val = 200*(f(Y) - f(Z))
    
    return L, a, b_val

def find_closest_shade(L, a, b):
    min_dist = float('inf')
    closest = "A2"
    distances = {}
    
    for shade, values in VITA_SHADES.items():
        dist = ((L - values["L"])**2 + 
                (a - values["a"])**2 + 
                (b - values["b"])**2)**0.5
        distances[shade] = dist
        if dist < min_dist:
            min_dist = dist
            closest = shade
    
    sorted_shades = sorted(distances.items(), key=lambda x: x[1])
    return closest, sorted_shades[:3]

def analyze_zones(img_array):
    h, w = img_array.shape[:2]
    
    cervical = img_array[int(h*0.6):int(h*0.85), int(w*0.2):int(w*0.8)]
    middle = img_array[int(h*0.3):int(h*0.6), int(w*0.2):int(w*0.8)]
    incisal = img_array[int(h*0.05):int(h*0.3), int(w*0.2):int(w*0.8)]
    
    results = {}
    for name, zone in [("Цервикальная", cervical), 
                        ("Средняя", middle), 
                        ("Режущая", incisal)]:
        mean_rgb = np.mean(zone.reshape(-1, 3), axis=0)
        L, a, b = rgb_to_lab(mean_rgb)
        shade, top3 = find_closest_shade(L, a, b)
        results[name] = {
            "rgb": mean_rgb,
            "L": round(L, 1),
            "a": round(a, 2),
            "b": round(b, 2),
            "shade": shade,
            "top3": top3
        }
    
    return results

def show_page():
    st.title("🎨 Колористика")
    st.info("Анализ оттенка коронки по шкале Vita. Загрузи фото коронки — система определит оттенок по зонам.")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Фото коронки")
        img_file = st.camera_input("Сфотографировать", key="cam_color")
        if not img_file:
            img_file = st.file_uploader("Или загрузить из галереи",
                                         type=["jpg","jpeg","png"],
                                         key="color_upload")
        if img_file:
            st.session_state["color_img"] = img_file
        if st.session_state.get("color_img"):
            st.image(st.session_state["color_img"], 
                     use_container_width=True)

    with col2:
        st.subheader("Параметры анализа")
        st.markdown("""
        **Для точного результата:**
        1. Откалиброй фото через Фото-инженер
        2. Равномерное освещение
        3. Коронка занимает 60%+ кадра
        4. Нейтральный фон
        """)
        
        use_wb = st.checkbox(
            "Использовать WB-коррекцию из Фото-инженера",
            value=True
        )
        
        target_shade = st.selectbox(
            "Заказанный оттенок (для сравнения)",
            ["Не указан"] + list(VITA_SHADES.keys()), key="target_shade_main"
        )

    if st.session_state.get("color_img"):
        st.divider()
        st.subheader("Выдели зону зуба для анализа")
        st.caption("Обрежь кадр чтобы в анализ попал только зуб без дёсен и фона")
        
        img_temp = Image.open(st.session_state["color_img"]).convert("RGB")
        w_img, h_img = img_temp.size
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            x_start = st.slider("Левая граница %", 0, 40, 10)
            y_start = st.slider("Верхняя граница %", 0, 40, 5)
        with col_s2:
            x_end = st.slider("Правая граница %", 60, 100, 90)
            y_end = st.slider("Нижняя граница %", 60, 100, 85)
        
        x1 = int(w_img * x_start / 100)
        y1 = int(h_img * y_start / 100)
        x2 = int(w_img * x_end / 100)
        y2 = int(h_img * y_end / 100)
        
        cropped = img_temp.crop((x1, y1, x2, y2))
        st.image(cropped, caption="Выделенная зона для анализа", 
                 use_container_width=True)
        st.session_state["color_crop"] = (x1, y1, x2, y2)

    st.divider()
    
    api_key = st.session_state.get("deepseek_api_key", "")
    
    col_analyze, col_reset = st.columns([2, 1])
    
    with col_analyze:
        target_shade = st.session_state.get("target_shade_main", "Не указан")
        
        if api_key:
            if st.button("Определить оттенок", type="primary"):
                with st.spinner("AI анализирует только зубы..."):
                    try:
                        import base64
                        import requests
                        import io

                        img = Image.open(
                            st.session_state["color_img"]
                        ).convert("RGB")
                        buffer = io.BytesIO()
                        img.save(buffer, format="JPEG")
                        img_base64 = base64.b64encode(
                            buffer.getvalue()
                        ).decode("utf-8")

                        shade_text = f"Заказанный оттенок: {target_shade}." if target_shade != "Не указан" else ""

                        prompt = f"""You are a dental colorimetry expert.
Analyze ONLY the ceramic crown or tooth in this photo.
Ignore gums, background, shadows, and anything that is not the tooth.

{shade_text}

Respond in Russian with this exact format:

**ОТТЕНОК ПО VITA:**
- Цервикальная зона: [оттенок]
- Средняя зона: [оттенок]  
- Режущая зона: [оттенок]
- Общий оттенок: [оттенок]

**СРАВНЕНИЕ С ЗАКАЗОМ:**
[совпадает или отличается и как именно]

**ХАРАКТЕРИСТИКА:**
- Value (яркость): [высокий/средний/низкий]
- Chroma (насыщенность): [высокая/средняя/низкая]
- Hue (тон): [тёплый A/нейтральный B/серый C/розовый D]

**РЕКОМЕНДАЦИИ ТЕХНИКУ:**
[конкретные действия для доработки]"""

                        headers = {
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        }
                        payload = {
                            "model": "deepseek-vision",
                            "messages": [
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
                            "max_tokens": 800
                        }
                        response = requests.post(
                            "https://api.deepseek.com/chat/completions",
                            headers=headers,
                            json=payload
                        )
                        if response.status_code == 200:
                            result = response.json()[
                                "choices"
                            ][0]["message"]["content"]
                            st.session_state["color_result"] = result
                        else:
                            st.error(f"Ошибка API: {response.status_code}")
                    except Exception as e:
                        st.error(f"Ошибка: {str(e)}")
        else:
            st.warning("Перейди в ⚙️ Настройки и введи DeepSeek API ключ")
    
    with col_reset:
        if st.button("🔄 Очистить экран"):
            # Очищаем все сессионные данные колористики
            keys_to_clear = ["color_img", "color_result", "color_ai_result", "color_crop"]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

if st.session_state.get("color_result"):
    st.divider()
    st.subheader("Результат анализа")
    st.markdown(st.session_state["color_result"])

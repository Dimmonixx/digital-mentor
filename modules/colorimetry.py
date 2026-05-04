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
            ["Не указан"] + list(VITA_SHADES.keys())
        )

    if st.session_state.get("color_img"):
        if st.button("Определить оттенок", type="primary"):
            img_file = st.session_state["color_img"]
            img_array = np.array(Image.open(img_file).convert("RGB"))
            
            if use_wb and st.session_state.get("wb_result"):
                wb = st.session_state["wb_result"]
                corrected = img_array.astype(np.float32)
                corrected[:,:,0] = np.clip(corrected[:,:,0] * wb["gain_r"], 0, 255)
                corrected[:,:,1] = np.clip(corrected[:,:,1] * wb["gain_g"], 0, 255)
                corrected[:,:,2] = np.clip(corrected[:,:,2] * wb["gain_b"], 0, 255)
                img_array = corrected.astype(np.uint8)
                st.success("WB-коррекция применена")
            
            with st.spinner("Анализирую оттенок..."):
                zones = analyze_zones(img_array)
                st.session_state["color_result"] = zones

    if st.session_state.get("color_result"):
        zones = st.session_state["color_result"]
        
        st.divider()
        st.subheader("Результат анализа по зонам")

        cols = st.columns(3)
        zone_colors = {
            "Цервикальная": "#E8943A",
            "Средняя": "#7B68EE", 
            "Режущая": "#4A90D9"
        }

        for i, (zone_name, data) in enumerate(zones.items()):
            with cols[i]:
                rgb = data["rgb"]
                hex_color = "#{:02x}{:02x}{:02x}".format(
                    int(rgb[0]), int(rgb[1]), int(rgb[2])
                )
                st.markdown(
                    f'<div style="background:{hex_color};height:60px;'
                    f'border-radius:8px;margin-bottom:8px;"></div>',
                    unsafe_allow_html=True
                )
                st.markdown(f"**{zone_name} зона**")
                st.markdown(f"Оттенок: **{data['shade']}**")
                st.markdown(f"L: {data['L']} | a: {data['a']} | b: {data['b']}")
                st.caption(VITA_SHADES[data['shade']]['description'])

        st.divider()
        
        shades = [zones[z]["shade"] for z in zones]
        most_common = max(set(shades), key=shades.count)
        
        st.subheader("Общий оттенок")
        col_result, col_compare = st.columns(2)
        
        with col_result:
            st.metric("Определённый оттенок", most_common)
            st.markdown(VITA_SHADES[most_common]["description"])
        
        with col_compare:
            if target_shade != "Не указан":
                if most_common == target_shade:
                    st.success(f"✅ Совпадает с заказом ({target_shade})")
                else:
                    target_L = VITA_SHADES[target_shade]["L"]
                    current_L = VITA_SHADES[most_common]["L"]
                    diff = current_L - target_L
                    if diff > 0:
                        st.warning(f"⚠️ Светлее заказанного на {abs(diff):.0f} ед.")
                    else:
                        st.warning(f"⚠️ Темнее заказанного на {abs(diff):.0f} ед.")

        api_key = st.session_state.get("deepseek_api_key", "")
        if api_key:
            st.divider()
            if st.button("Получить рекомендации по доработке"):
                shade_info = ", ".join([f"{z}: {d['shade']}" for z, d in zones.items()])
                question = f"""Анализ коронки показал оттенки по зонам: {shade_info}.
                Заказанный оттенок: {target_shade if target_shade != 'Не указан' else 'не указан'}.
                Дай конкретные рекомендации что нужно сделать технику 
                чтобы привести коронку к нужному оттенку."""
                
                with st.spinner("AI формирует рекомендации..."):
                    from modules import ai_analysis
                    try:
                        headers = {"Authorization": f"Bearer {api_key}",
                                   "Content-Type": "application/json"}
                        payload = {
                            "model": "deepseek-chat",
                            "messages": [{"role": "user", "content": question}],
                            "max_tokens": 600
                        }
                        import requests
                        response = requests.post(
                            "https://api.deepseek.com/chat/completions",
                            headers=headers, json=payload
                        )
                        if response.status_code == 200:
                            result = response.json()["choices"][0]["message"]["content"]
                            st.session_state["color_ai_result"] = result
                    except Exception as e:
                        st.error(f"Ошибка: {str(e)}")

        if st.session_state.get("color_ai_result"):
            st.markdown(st.session_state["color_ai_result"])

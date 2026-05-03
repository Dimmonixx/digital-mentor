import streamlit as st
import numpy as np
from PIL import Image

def show_page():
    st.title("📷 Фото-инженер")
    
    st.info("Модуль анализирует фото и корректирует цвет для точного подбора оттенка. Поддерживает два режима: калибровка по серой карте (профессиональный) и по расцветке Vita (быстрый).")
    
    режим = st.radio(
        "Выбери режим калибровки",
        ["⬜ Серая карта (Grey Card)", "🦷 Расцветка Vita"],
        horizontal=True
    )
    
    st.divider()
    
    if режим == "⬜ Серая карта (Grey Card)":
        st.subheader("Инструкция")
        st.markdown("""
        1. Сфотографируй коронку вместе с серой картой в одном кадре
        2. Одинаковое освещение для карты и коронки  
        3. Загрузи фото ниже — система найдёт карту автоматически
        """)
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Шаг 1 — Серая карта")
            grey = st.camera_input("Сфотографировать", key="cam_grey")
            if not grey:
                grey = st.file_uploader("Или загрузить из галереи",
                                        type=["jpg","jpeg","png"],
                                        key="grey_card")
            if grey:
                st.image(grey, use_container_width=True)
        with col2:
            st.subheader("Шаг 2 — Коронка")
            crown = st.camera_input("Сфотографировать", key="cam_crown")
            if not crown:
                crown = st.file_uploader("Или загрузить из галереи",
                                         type=["jpg","jpeg","png"],
                                         key="crown_grey")
            if crown:
                st.image(crown, use_container_width=True)
        
        if grey and crown:
            if st.button("🔍 Анализировать баланс белого"):
                
                # Загружаем оба фото
                img_grey = np.array(Image.open(grey).convert("RGB"))
                img_crown = np.array(Image.open(crown).convert("RGB"))
                
                # Берём центральный патч серой карты (20% центр изображения)
                h, w = img_grey.shape[:2]
                y1, y2 = int(h*0.4), int(h*0.6)
                x1, x2 = int(w*0.4), int(w*0.6)
                patch = img_grey[y1:y2, x1:x2]
                
                # Считаем средние значения каналов
                mean_r = np.mean(patch[:,:,0])
                mean_g = np.mean(patch[:,:,1])
                mean_b = np.mean(patch[:,:,2])
                
                # Вычисляем коэффициенты WB
                target = (mean_r + mean_g + mean_b) / 3.0
                gain_r = target / mean_r
                gain_g = target / mean_g
                gain_b = target / mean_b
                
                # Применяем коррекцию к коронке
                corrected = img_crown.astype(np.float32)
                corrected[:,:,0] = np.clip(corrected[:,:,0] * gain_r, 0, 255)
                corrected[:,:,1] = np.clip(corrected[:,:,1] * gain_g, 0, 255)
                corrected[:,:,2] = np.clip(corrected[:,:,2] * gain_b, 0, 255)
                corrected = corrected.astype(np.uint8)
                
                # Показываем результат
                st.divider()
                st.subheader("📊 Результат калибровки")
                
                col_r, col_g, col_b = st.columns(3)
                col_r.metric("R gain", f"{gain_r:.3f}")
                col_g.metric("G gain", f"{gain_g:.3f}")
                col_b.metric("B gain", f"{gain_b:.3f}")
                
                st.divider()
                col_before, col_after = st.columns(2)
                with col_before:
                    st.caption("До коррекции")
                    st.image(img_crown, use_container_width=True)
                with col_after:
                    st.caption("После коррекции")
                    st.image(corrected, use_container_width=True)
                
                # Оценка качества
                deviation = np.std([mean_r, mean_g, mean_b])
                if deviation < 5:
                    st.success("✅ Отличная калибровка — серая карта нейтральна")
                elif deviation < 15:
                    st.warning("⚠️ Допустимое отклонение — результат приемлем")
                else:
                    st.error("❌ Сильный цветовой сдвиг — проверь освещение")
        
        elif grey and not crown:
            st.info("👆 Загрузи фото коронки для применения коррекции")
        elif crown and not grey:
            st.info("👆 Загрузи фото с серой картой для калибровки")
    
    else:
        st.subheader("Инструкция")
        st.markdown("""
        1. Сфотографируй коронку рядом с расцветкой Vita в одном кадре
        2. Расцветка должна занимать минимум 20% кадра
        3. Избегай теней и бликов на расцветке
        """)
        st.divider()
        vita = st.file_uploader("📸 Фото коронки с расцветкой Vita", 
                                 type=["jpg","jpeg","png"], 
                                 key="vita")
        оттенок = st.selectbox(
            "Предполагаемый оттенок (для сравнения)",
            ["A1","A2","A3","A3.5","A4",
             "B1","B2","B3","B4",
             "C1","C2","C3","C4",
             "D2","D3","D4"]
        )
        if vita:
            st.image(vita, use_container_width=True)
        
        if st.button("🔍 Сравнить с расцветкой"):
            st.info("Алгоритм сравнения подключим на следующем шаге")

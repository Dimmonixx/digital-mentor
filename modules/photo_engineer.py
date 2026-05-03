import streamlit as st

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
            grey = st.file_uploader("📸 Фото с серой картой",
                                    type=["jpg","jpeg","png"],
                                    key="grey_card")
            if grey:
                st.image(grey, use_container_width=True)
        with col2:
            st.subheader("Шаг 2 — Коронка")
            crown = st.file_uploader("🦷 Фото коронки",
                                     type=["jpg","jpeg","png"],
                                     key="crown_grey")
            if crown:
                st.image(crown, use_container_width=True)

        if st.button("🔍 Анализировать баланс белого"):
            st.info("Алгоритм WB подключим на следующем шаге")

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
        st.selectbox(
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

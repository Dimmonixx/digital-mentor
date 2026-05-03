# -*- coding: utf-8 -*-
import streamlit as st
from modules import photo_engineer

st.set_page_config(
    page_title="Цифровой Наставник",
    page_icon="🦷",
    layout="wide"
)

with st.sidebar:
    st.title("🦷 Цифровой Наставник")
    st.divider()
    st.caption("Навигация")
    page = st.radio("", [
        "🏠 Главная",
        "📷 Фото-инженер",
        "🔍 Детекция дефектов",
        "🎨 Колористика",
        "📋 Тех-карта",
        "🔬 Морфология",
        "📁 Кейсы",
        "🦴 Анатомия зубов",
        "💬 Чат техников",
        "⚙️ Настройки"
    ])

if page == "🏠 Главная":
    st.title("🦷 Добро пожаловать!")
    st.subheader("Твой AI-помощник в зуботехнической лаборатории")
    st.divider()
    st.subheader("Анализ и инструменты")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("📷 Фото-инженер", use_container_width=True)
    with col2:
        st.button("🔍 Дефекты", use_container_width=True)
    with col3:
        st.button("🎨 Колористика", use_container_width=True)
    col4, col5, col6 = st.columns(3)
    with col4:
        st.button("📋 Тех-карта", use_container_width=True)
    with col5:
        st.button("🔬 Морфология", use_container_width=True)
    with col6:
        st.button("📁 Кейсы", use_container_width=True)
    st.divider()
    st.subheader("Обучение и сообщество")
    col7, col8 = st.columns(2)
    with col7:
        st.button("🦴 Анатомия зубов", use_container_width=True)
    with col8:
        st.button("💬 Чат техников", use_container_width=True)

elif page == "📷 Фото-инженер":
    photo_engineer.show_page()

else:
    st.title(page)
    st.info("Раздел в разработке — скоро здесь появится функционал")

import streamlit as st
from modules import photo_engineer, anatomy, settings

st.set_page_config(page_title="Цифровой Наставник", layout="wide")

# Initialize session state for page navigation
if "page" not in st.session_state:
    st.session_state["page"] = "🏠 Главная"

# Sidebar navigation
st.sidebar.title("🦷 Цифровой Наставник")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Навигация",
    [
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
    ],
    index=[
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
    ].index(st.session_state["page"])
)

st.session_state["page"] = page

# Main content
if st.session_state["page"] == "🏠 Главная":
    st.title("🦷 Добро пожаловать!")
    st.subheader("Твой AI-помощник в зуботехнической лаборатории")
    st.divider()

    st.subheader("Анализ и инструменты")

    # Row 1
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📷 Фото-инженер", use_container_width=True):
            st.session_state["page"] = "📷 Фото-инженер"
            st.rerun()
    with col2:
        if st.button("🔍 Дефекты", use_container_width=True):
            st.session_state["page"] = "🔍 Детекция дефектов"
            st.rerun()
    with col3:
        if st.button("🎨 Колористика", use_container_width=True):
            st.session_state["page"] = "🎨 Колористика"
            st.rerun()

    # Row 2
    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button("📋 Тех-карта", use_container_width=True):
            st.session_state["page"] = "📋 Тех-карта"
            st.rerun()
    with col5:
        if st.button("� Морфология", use_container_width=True):
            st.session_state["page"] = "🔬 Морфология"
            st.rerun()
    with col6:
        if st.button("📁 Кейсы", use_container_width=True):
            st.session_state["page"] = "📁 Кейсы"
            st.rerun()

    st.divider()
    st.subheader("Обучение и сообщество")

    # Row 3
    col7, col8 = st.columns(2)
    with col7:
        if st.button("🦴 Анатомия зубов", use_container_width=True):
            st.session_state["page"] = "🦴 Анатомия зубов"
            st.rerun()
    with col8:
        if st.button("� Чат техников", use_container_width=True):
            st.session_state["page"] = "💬 Чат техников"
            st.rerun()

elif page == "📷 Фото-инженер":
    photo_engineer.show_page()

elif st.session_state["page"] == "🔍 Детекция дефектов":
    st.title("🔍 Детекция дефектов")
    st.info("Раздел в разработке — скоро здесь появится функционал")

elif st.session_state["page"] == "🎨 Колористика":
    st.title("🎨 Колористика")
    st.info("Раздел в разработке — скоро здесь появится функционал")

elif st.session_state["page"] == "📋 Тех-карта":
    st.title("📋 Тех-карта")
    st.info("Раздел в разработке — скоро здесь появится функционал")

elif st.session_state["page"] == "🔬 Морфология":
    st.title("🔬 Морфология")
    st.info("Раздел в разработке — скоро здесь появится функционал")

elif st.session_state["page"] == "📁 Кейсы":
    st.title("📁 Кейсы")
    st.info("Раздел в разработке — скоро здесь появится функционал")

elif st.session_state["page"] == "🦴 Анатомия зубов":
    anatomy.show_page()

elif st.session_state["page"] == "💬 Чат техников":
    st.title("💬 Чат техников")
    st.info("Раздел в разработке — скоро здесь появится функционал")

elif st.session_state["page"] == "⚙️ Настройки":
    settings.show_page()

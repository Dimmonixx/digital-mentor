import streamlit as st

def show_page():
    st.title("⚙️ Настройки")
    st.info("Введи API ключи один раз — они будут доступны во всех модулях приложения.")

    st.subheader("OpenAI API")
    openai_key = st.text_input(
        "OpenAI API ключ",
        type="password",
        placeholder="sk-...",
        value=st.session_state.get("openai_api_key", "")
    )
    if st.button("Сохранить OpenAI ключ"):
        st.session_state["openai_api_key"] = openai_key
        st.success("Ключ сохранён!")

    st.divider()

    st.subheader("DeepSeek API")
    deepseek_key = st.text_input(
        "DeepSeek API ключ",
        type="password",
        placeholder="sk-...",
        value=st.session_state.get("deepseek_api_key", "")
    )
    if st.button("Сохранить DeepSeek ключ"):
        st.session_state["deepseek_api_key"] = deepseek_key
        st.success("Ключ сохранён!")

    st.divider()
    st.caption("Ключи хранятся только в текущей сессии и не передаются третьим лицам.")

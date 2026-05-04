import streamlit as st
import requests
import json
from datetime import datetime
from modules import ai_analysis

FIREBASE_URL = "https://digital-mentor-98da3-default-rtdb.europe-west1.firebasedatabase.app"

def get_messages():
    try:
        response = requests.get(f"{FIREBASE_URL}/chat.json")
        data = response.json()
        if not data:
            return []
        messages = []
        for key, value in data.items():
            value["id"] = key
            messages.append(value)
        messages.sort(key=lambda x: x.get("timestamp", ""))
        return messages[-50:]
    except:
        return []

def send_message(username, text):
    message = {
        "username": username,
        "text": text,
        "timestamp": datetime.now().isoformat()
    }
    requests.post(f"{FIREBASE_URL}/chat.json", 
                  data=json.dumps(message))

def get_ai_response(question, api_key):
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": """Ты AI-помощник для зубных техников. 
                    Отвечай коротко и по делу на русском языке.
                    Фокус на практических советах по керамике, 
                    цветоведению, технике нанесения масс."""
                },
                {
                    "role": "user", 
                    "content": question
                }
            ],
            "max_tokens": 500
        }
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return None
    except:
        return None

def show_page():
    st.title("💬 Чат техников")
    st.info("Общайся с коллегами и получай AI-помощь. AI можно включить/выключить.")

    col_name, col_ai = st.columns([3, 1])
    
    with col_name:
        username = st.text_input("Твоё имя", 
                                  value=st.session_state.get("chat_username", ""),
                                  placeholder="Введи имя...")
        if username:
            st.session_state["chat_username"] = username

    with col_ai:
        ai_enabled = st.toggle("AI помощник", 
                                value=st.session_state.get("ai_enabled", True))
        st.session_state["ai_enabled"] = ai_enabled

    st.divider()

    messages = get_messages()
    
    chat_container = st.container()
    with chat_container:
        if not messages:
            st.info("Пока нет сообщений. Начни первым!")
        for msg in messages:
            is_ai = msg.get("username") == "AI Наставник"
            if is_ai:
                with st.chat_message("assistant"):
                    st.markdown(f"**AI Наставник** 🤖")
                    st.markdown(msg["text"])
            else:
                with st.chat_message("user"):
                    st.markdown(f"**{msg.get('username', 'Аноним')}**")
                    st.markdown(msg["text"])

    st.divider()

    with st.form("chat_form", clear_on_submit=True):
        message_text = st.text_area("Сообщение", 
                                     placeholder="Напиши вопрос или совет...",
                                     height=80)
        submitted = st.form_submit_button("Отправить")
        
        if submitted and message_text and username:
            send_message(username, message_text)
            
            if ai_enabled:
                api_key = st.session_state.get("deepseek_api_key", "")
                if api_key:
                    with st.spinner("AI думает..."):
                        ai_response = get_ai_response(message_text, api_key)
                        if ai_response:
                            send_message("AI Наставник", ai_response)
            
            st.rerun()
        
        elif submitted and not username:
            st.warning("Введи своё имя выше")

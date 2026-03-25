import streamlit as st
import requests
import json
import time

# ---------------- CONFIG ----------------
MAX_HISTORY = 50
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

st.set_page_config(page_title="AI Assistant", layout="wide")

# ---------------- STATE ----------------
for k, v in {
    "messages": [],
    "history": [],
    "summary": "",
    "chat_ended": False,
    "loaded_from_history": False,
    "is_typing": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- FLOATING BUTTON STYLE ----------------
st.markdown("""
<style>
.floating-controls {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  gap: 10px;
}
.fade-in { animation: fadeIn 0.3s ease-in; }
@keyframes fadeIn { from {opacity:0;} to {opacity:1;} }
.content { margin-top: 80px; }
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Settings")
assistant_name = st.sidebar.text_input("Assistant Name", "Demo Assistant")
#api_key = st.sidebar.text_input("OpenRouter API Key", type="password")
api_key = st.secrets["OPENROUTER_API_KEY"]
model = st.sidebar.selectbox("Model", [
    "openai/gpt-4o-mini",
    "anthropic/claude-3-haiku",
    "meta-llama/llama-3-8b-instruct"
])

st.sidebar.markdown("---")

# ---------------- HISTORY ----------------
st.sidebar.subheader("📜 History")
for i, chat in enumerate(st.session_state.history):
    with st.sidebar.expander(chat.get("title", f"Chat {i+1}")):
        if st.button("Load", key=f"load_{i}"):
            st.session_state.messages = chat["messages"].copy()
            st.session_state.summary = chat.get("summary", "")
            st.session_state.chat_ended = True
            st.session_state.loaded_from_history = True
            st.rerun()

# ---------------- FLOATING BUTTONS ----------------
st.markdown("<div class='floating-controls'>", unsafe_allow_html=True)

# No chat
if not st.session_state.messages:
    if st.button("🆕 New Chat"):
        st.session_state.messages = []
        st.session_state.chat_ended = False
        st.session_state.loaded_from_history = False
        st.rerun()

# Active chat
elif st.session_state.messages and not st.session_state.chat_ended and not st.session_state.loaded_from_history:
    if st.button("🛑 End Chat"):
        st.session_state.chat_ended = True
        st.session_state.history.insert(0, {"messages": st.session_state.messages.copy(), "summary": "", "title": "Conversation"})
        st.session_state.history = st.session_state.history[:MAX_HISTORY]
        st.rerun()

# Loaded from history
elif st.session_state.loaded_from_history:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 New Chat"):
            st.session_state.messages = []
            st.session_state.chat_ended = False
            st.session_state.loaded_from_history = False
            st.rerun()
    with col2:
        if st.button("🛑 End Chat"):
            st.session_state.chat_ended = True
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title(f"🚀 {assistant_name}")

# ---------------- CHAT DISPLAY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f"<div class='fade-in'>{msg['content']}</div>", unsafe_allow_html=True)

# ---------------- INPUT ----------------
if not st.session_state.chat_ended:
    user_input = st.chat_input("Type message...", disabled=st.session_state.is_typing)

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_typing = True
        st.rerun()

# ---------------- STREAMING RESPONSE ----------------
if st.session_state.is_typing:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": st.session_state.messages}

    placeholder = st.empty()
    full_reply = ""

    try:
        res = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        data = res.json()
        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "No response")

        # Simulated token streaming
        for token in reply.split():
            full_reply += token + " "
            with placeholder.container():
                with st.chat_message("assistant"):
                    st.markdown(full_reply)
            time.sleep(0.03)

    except Exception as e:
        full_reply = f"Error: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": full_reply})
    st.session_state.is_typing = False
    st.rerun()

# ---------------- SUMMARY ----------------
if st.session_state.chat_ended and st.session_state.messages:
    st.markdown("---")
    if st.button("Generate Summary"):
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Summarize this chat"},
                {"role": "user", "content": json.dumps(st.session_state.messages)}
            ]
        }
        res = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        data = res.json()
        st.session_state.summary = data.get("choices", [{}])[0].get("message", {}).get("content", "")

    st.download_button("Export Chat", json.dumps(st.session_state.messages, indent=2))

if st.session_state.summary:
    st.info(st.session_state.summary)

# ---------------- FOOTER ----------------
st.caption("🚀 Token streaming + Floating buttons + Multi-turn chat")
import streamlit as st
from components.sidebar import render_sidebar
from services.backend_api import ask_question

st.set_page_config(page_title="Chat with Tiny", page_icon="💬", layout="wide")

render_sidebar()
st.title("💬 Tiny Chatbot")
st.caption("AI assistant for your internal documents")

# Lịch sử chat giờ chỉ được lưu trong session_state
if "messages" not in st.session_state:
	st.session_state.messages = [{"role": "assistant", "content": "Hi! How can I help you today?"}]

# Hiển thị các tin nhắn đã có trong lịch sử
for message in st.session_state.messages:
	with st.chat_message(message["role"]):
		st.markdown(message["content"])

# Vòng lặp Hỏi-Đáp
if prompt := st.chat_input("Ask your question..."):
	st.session_state.messages.append({"role": "user", "content": prompt})
	with st.chat_message("user"):
		st.markdown(prompt)

	with st.chat_message("assistant"):
		response_placeholder = st.empty()
		with st.spinner("Tiny is thinking..."):
			ai_answer = ask_question(prompt)
			response_placeholder.markdown(ai_answer)
	st.session_state.messages.append({"role": "assistant", "content": ai_answer})

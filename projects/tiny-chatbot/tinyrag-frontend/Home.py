import streamlit as st
from components.sidebar import render_sidebar
import os

st.set_page_config(page_title="Tiny - Home", page_icon="🏠", layout="wide")

render_sidebar()

st.title("Welcome from Tiny 👋")
st.header("AI Assistant to discover internal documents")

st.markdown("---")

st.markdown(
	"""
	This is an intelligent question-answering (RAG) system built 
	to help you quickly find information from your documents.

	### Functions:
	- **💬 Chatbot:** Chat and ask questions with Tiny.
	- **📚 Knowledge:** To manage knowledge base of Tiny as uploading, viewing, 
	and deleting knowledge base files.

	👈 **Please select a page from the sidebar to get started!**
	"""
)

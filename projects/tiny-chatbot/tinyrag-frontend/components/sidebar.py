import streamlit as st
from core.config import settings


def render_sidebar():
	with st.sidebar:
		st.header("About")
		st.markdown(
			f"**Tiny** is an AI assistant based on `{settings.MODEL_NAME}` and RAG mechanism,"
			" to be built to help with lookup and Q&A based on internal documents."
		)
		st.markdown("---")
		st.markdown("### Architecture:")
		st.markdown(
			f"""
			- **UI:** Streamlit
			- **Backend:** FastAPI, LangChain
			- **Database:** ChromaDB
			- **LLM Server:** LM Studio
			- **Model:** `{settings.MODEL_NAME}`
			"""
		)
		st.markdown("---")
		st.markdown("""<style>div[data-testid="stAlert"] div[data-testid="stMarkdownContainer"] {text-align: center;}</style>""", unsafe_allow_html=True)
		st.info("Made by **Pham Minh Tuan**")

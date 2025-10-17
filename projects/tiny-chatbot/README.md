# 🤖 TinyChatbot — Modular RAG Chatbot Framework

**TinyChatbot** is a lightweight, modular project demonstrating how to build a **Retrieval-Augmented Generation (RAG)** chatbot using **Python**, **FastAPI**, and **Streamlit**.  
It’s designed for self-learning, rapid experimentation, and flexible integration with multiple model backends such as **Ollama**, **LM Studio**, or **OpenAI GPT**.

> “Flexible. Portable. Understandable.” — TinyChatbot helps you learn how modern AI chat systems are built.

---

## 🧠 Core Idea

The project demonstrates the logic behind a modern **RAG pipeline**:
1. 🧩 *Retrieve* relevant context from your knowledge base  
2. 💬 *Augment* user queries with that context  
3. 🧠 *Generate* responses using your chosen LLM backend  

---

## ⚙️ Tech Stack

| Layer | Technology | Description |
|-------|-------------|-------------|
| 🧠 **Backend** | **Python**, **FastAPI** | Core RAG API — retrieval, context management, and generation |
| 💬 **Frontend** | **Streamlit** | Interactive chat interface built in Python |
| 🧩 **Models** | **Ollama**, **LM Studio**, **OpenAI GPT** | Switch between LLM providers easily |
| 🔍 **Retrieval** | Embedding-based RAG pipeline | Contextual grounding for answers |
| 🐳 **Deployment** | **Docker**, **docker-compose** | One-command containerized setup |

---

## 🧭 Project Structure

```
tiny-chatbot/
├── tinyrag-backend/       # FastAPI backend (RAG logic, model integration)
├── tinyrag-frontend/      # Streamlit UI for chatting and visualization
├── docker-compose.yml     # Orchestrates backend + frontend
└── README.md              # This file
```

---

## 🚀 Quick Start

### 🐳 Option 1 — Run with Docker (recommended)

Make sure you have **Docker** and **docker-compose** installed.

```bash
docker-compose up --build
```

Then open:
- Frontend → http://localhost:8501  
- Backend API → http://localhost:6138/docs  

---

### 🐍 Option 2 — Run manually (for development)

#### Backend
```bash
cd tinyrag-backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Access API at: [http://localhost:6138/docs](http://localhost:6138/docs)

#### Frontend
```bash
cd tinyrag-frontend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open: [http://localhost:8501](http://localhost:8501)

---

## 🧩 Features

| Feature | Description |
|----------|--------------|
| **RAG Pipeline** | Retrieve → Augment → Generate structure |
| **Dual Python Stack** | Backend (FastAPI) + Frontend (Streamlit) — no Node required |
| **Multi-Model Support** | Switch between Ollama, LM Studio, and OpenAI APIs |
| **Dockerized Setup** | Portable, reproducible environment |
| **Simple UI** | Chat interface in Streamlit with context visualization |
| **Extensible Design** | Add your own retrievers, embeddings, or UI logic |

---

## 🔧 Configuration

| File | Purpose |
|------|----------|
| `.env` | API keys, model backend, and config |
| `docker-compose.yml` | Defines backend + frontend containers |
| `requirements.txt` | Python dependencies |
| `app.py` | Streamlit frontend entry point |

Example `.env`:
```
LLM_API_URL: http://host.docker.internal:11434/v1
MODEL_NAME: gpt-oss:20b (or llama3:8b)
API_KEY: ollama

volumes:
   - ./tinyrag-backend:/app
   - chroma_data:/app/db
```

---

## 🧠 Learning Focus

This project is ideal for:
- Practicing **FastAPI** + **Streamlit** integration  
- Understanding **Retrieval-Augmented Generation (RAG)**  
- Experimenting with **embeddings, vector stores**, and **model orchestration**  
- Learning how to **Dockerize AI applications**

---

## 🧰 Tech Summary

| Category | Tool |
|-----------|------|
| Language | Python 3.10+ |
| Backend | FastAPI |
| Frontend | Streamlit |
| LLM Backends | Ollama / LM Studio / OpenAI |
| Vector Store | FAISS / Chroma |
| Deployment | Docker / docker-compose |
| Platform | macOS / Linux / Windows |

---

## 🧭 Future Enhancements
- Persistent vector store (Chroma / FAISS / PostgreSQL)  
- Streaming responses from models  
- Multi-document context retrieval  
- Advanced UI with conversation history and analytics  

---

## 📜 License
MIT License — for learning, research, and experimentation.

---

**Author:** *Pham Minh Tuan*  
© 2025 — *TinyChatBot: Build, Learn, Share.*

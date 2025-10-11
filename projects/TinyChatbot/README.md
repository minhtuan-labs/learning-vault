# 🤖 TinyChatBot — Modular RAG Chatbot Framework

**TinyChatBot** is a lightweight, modular project that demonstrates how to build a **Retrieval-Augmented Generation (RAG)**–based chatbot using modern open-source tools.  
It is designed for self-learning, experimentation, and fast prototyping with multiple model backends.

> “Flexible. Portable. Understandable.” — TinyChatBot helps you learn how modern AI chat systems are built.

---

## 🧠 Core Idea

The goal of **TinyChatBot** is to explore **how RAG pipelines work**:
1. 🧩 *Retrieve* relevant context from your local knowledge base  
2. 💬 *Augment* user queries with the retrieved context  
3. 🧠 *Generate* a contextualized answer via your chosen LLM backend  

---

## ⚙️ Tech Stack

| Layer | Technology | Description |
|-------|-------------|-------------|
| 🧠 **Backend** | **Python**, **FastAPI** | RESTful API layer for query handling, retrieval, and response generation |
| 💬 **Models** | **Ollama**, **LM Studio**, or **OpenAI GPT** | Switch between model providers easily |
| 🔍 **Retrieval** | RAG pipeline with embeddings & vector database | Provides contextual grounding for chatbot answers |
| 🐳 **Deployment** | **Docker**, **docker-compose** | Simple and reproducible deployment across environments |
| 🧩 **Architecture** | Modular design (backend + frontend) | Easy to extend and customize |

---

## 🧭 Project Structure

```
TinyChatBot/
├── tinyrag-backend/       # FastAPI backend service (RAG logic, model integration)
├── tinyrag-frontend/      # Frontend UI (React/Vite chat interface)
├── docker-compose.yml     # Orchestrates backend + frontend services
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
- Frontend → http://localhost:3000  
- Backend API → http://localhost:8000/docs

---

### 🐍 Option 2 — Run manually (for development)

#### Backend
```bash
cd tinyrag-backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
API available at http://localhost:8000/docs

#### Frontend
```bash
cd tinyrag-frontend
npm install
npm run dev
```
Frontend available at http://localhost:3000

---

## 🧩 Features

| Feature | Description |
|----------|--------------|
| **RAG Architecture** | Retrieve → Augment → Generate pipeline |
| **Pluggable Models** | Easily switch between Ollama, LM Studio, or GPT-based APIs |
| **FastAPI Backend** | Async API endpoints for chat and retrieval |
| **Dockerized Setup** | 1-command environment replication |
| **Custom Data Sources** | Extend retrieval logic to local files, docs, or databases |
| **Frontend Chat UI** | Simple web interface for chatting and visualizing context |

---

## 🔧 Configuration

| File | Purpose |
|------|----------|
| `.env` | Define API keys, model settings, and backend ports |
| `docker-compose.yml` | Container orchestration |
| `requirements.txt` | Python dependencies |
| `vite.config.js` | Frontend build configuration |

Example `.env`:
```
MODEL_BACKEND=ollama
MODEL_NAME=llama3
VECTOR_DB_PATH=./data/vectorstore
OPENAI_API_KEY=your-key-here
```

---

## 🧠 Learning Focus

This project is ideal for:
- Practicing **FastAPI** + **LLM integration**
- Understanding **RAG (retrieval-augmented generation)** concepts
- Experimenting with **embeddings, vector stores**, and **contextual prompts**
- Learning how to **containerize AI microservices**

---

## 🧰 Tech Summary

| Category | Tool |
|-----------|------|
| Language | Python 3.10+ |
| API Framework | FastAPI |
| LLM Integration | Ollama / LM Studio / OpenAI |
| Vector Store | FAISS / Chroma (optional) |
| Containerization | Docker / docker-compose |
| Frontend | React + Vite |
| Platform | Cross-platform (macOS / Linux / Windows) |

---

## 🧭 Future Enhancements
- Add **vector database persistence** (Chroma / FAISS / PostgreSQL)  
- Support for **RAG streaming responses**  
- Add **multi-model orchestration layer**  
- Integrate **embedding pipeline for PDF / text ingestion**

---

## 📜 License

MIT License — for learning, research, and experimentation.

---

**Author:** *Pham Minh Tuan*  
© 2025 — *TinyChatBot: Build, Learn, Share.*

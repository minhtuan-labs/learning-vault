# TinyRAG — Lightweight RAG System

TinyRAG is a small-scale **Retrieval-Augmented Generation** (RAG) project combining:
- 🧠 **Backend** (Python/FastAPI) for embedding, retrieval, and model interaction
- 💻 **Frontend** (React/Vite) for chat UI and user experience
- 🐳 **Docker Compose** to orchestrate both services easily

---

## 📂 Structure

| Folder | Description |
|---------|--------------|
| `tinyrag-backend/` | Core backend service (API, vector DB, embedding, etc.) |
| `tinyrag-frontend/` | Chat UI built with React/Vite |
| `fine-tuning/` | Scripts and checkpoints for LLM fine-tuning |
| `prepare-data/` | Preprocessing and dataset preparation utilities |

---

## 🚀 Quick Start

### Run with Docker
```bash
docker-compose up --build

Then open the frontend at:
👉 http://localhost:3000

API docs (FastAPI Swagger):
👉 http://localhost:8000/docs

⸻

🧩 Tech Stack

Backend: Python, FastAPI, LangChain, FAISS / Chroma
Frontend: React, Vite, Tailwind
Infra: Docker, docker-compose

⸻

🧠 Purpose

TinyRAG is built for learning and experimentation — a sandbox for understanding how RAG systems integrate embedding, retrieval, and generation.

“Build small, learn fast.”

---

## ✅ 5️⃣ Commit & Push lên repo learning-vault/projects
```bash
git add .
git commit -m "Clean TinyRAG project structure and add README"
git push origin main






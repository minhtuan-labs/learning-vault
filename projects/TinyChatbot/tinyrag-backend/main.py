from fastapi import FastAPI
from api.routers import rag, data_sources

app = FastAPI(title="TinyRAG Backend API")

@app.get("/health", status_code=200, tags=["Health Check"])
def health_check():
    return {"status": "ok"}

app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])
app.include_router(data_sources.router, prefix="/api/v1/data-sources", tags=["Data Sources"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the stable TinyRAG API"}


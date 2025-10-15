from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from core.schemas import Query
from services import rag_service
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/ask")
async def ask(query: Query):
	try:
		answer = await run_in_threadpool(rag_service.ask_question, query.question)
		return {"answer": answer}
	except Exception as e:
		logger.error(f"Error in /ask endpoint: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail=str(e))

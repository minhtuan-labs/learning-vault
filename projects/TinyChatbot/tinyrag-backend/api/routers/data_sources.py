from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from services import data_manager
from dependencies import services as app_services
from core.schemas import UpdateSource
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.get("")
def get_sources_paginated(page: int = 1, page_size: int = settings.PAGE_SIZE):
	return data_manager.get_all_sources(page, page_size)

@router.post("")
async def add_source(title: str = Form(...), description: str = Form(""), url: Optional[str] = Form(None),
					 file: Optional[UploadFile] = File(None)):
	if not url and not file:
		raise HTTPException(status_code=400, detail="Either a file or a URL must be provided.")

	new_source = data_manager.add_new_source(title, description, url, file)
	if not new_source:
		raise HTTPException(status_code=500, detail="Failed to add new knowledge source.")
	return new_source

@router.delete("/{source_id}")
def delete_source(source_id: str):
	success = data_manager.remove_source(source_id)
	if not success:
		raise HTTPException(status_code=404, detail="Source not found or could not be deleted.")
	return {"message": "Source deleted successfully."}

@router.put("/{source_id}")
def update_source_info(source_id: str, source_data: UpdateSource):
	updated_source = data_manager.update_source(source_id, source_data)
	if not updated_source:
		raise HTTPException(status_code=404, detail="Source not found or could not be updated.")
	return updated_source

@router.post("/re-index")
def reindex_data():
	result = data_manager.trigger_reindex()
	if not result.get("success"):
		raise HTTPException(status_code=500, detail=result.get("message"))

	# Tải lại RAG service sau khi re-index thành công
	rag_service = app_services.get("rag_service")
	rag_service = app_services.get("rag_service")
	if rag_service:
		try:
			rag_service.reload()
			logger.info("RAG service reloaded successfully.")
		except Exception as e:
			logger.error(f"Failed to reload RAG service: {e}")
			raise HTTPException(status_code=500, detail="Re-indexing succeeded, but failed to reload the RAG service.")
	return {"message": result.get("message")}

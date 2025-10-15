import os
import json
import uuid
import subprocess
import math
from fastapi import UploadFile
from typing import Optional

# LangChain imports for vector deletion
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Core imports
from core.config import settings
from core.schemas import UpdateSource
from core.logger import get_logger

# Khởi tạo logger cho file này
logger = get_logger(__name__)

def read_metadata():
	try:
		if not os.path.exists(settings.METADATA_FILE):
			logger.info("metadata.json not found, returning empty list.")
			return []
		with open(settings.METADATA_FILE, "r", encoding="utf-8") as f:
			return json.load(f)
	except (json.JSONDecodeError, FileNotFoundError) as e:
		logger.error(f"Error reading or parsing metadata file: {e}", exc_info=True)
		return []

def write_metadata(data) -> bool:
	try:
		with open(settings.METADATA_FILE, "w", encoding="utf-8") as f:
			json.dump(data, f, indent=4, ensure_ascii=False)
		return True
	except IOError as e:
		logger.error(f"Failed to write metadata file: {e}", exc_info=True)
		return False

def get_all_sources(page: int, page_size: int):
	"""Lấy danh sách các nguồn tri thức có phân trang."""
	metadata = read_metadata()
	metadata.sort(key=lambda x: x.get("status", "indexed"), reverse=True)

	start = (page - 1) * page_size
	end = start + page_size
	total_items = len(metadata)

	total_pages = math.ceil(total_items / page_size) if page_size > 0 else 0

	return {
		"total_items": total_items, "items": metadata[start:end],
		"page": page, "page_size": page_size, "total_pages": total_pages
	}

def add_new_source(title: str, description: str, url: Optional[str], file: Optional[UploadFile]):
	try:
		metadata = read_metadata()
		new_source = {
			"id": str(uuid.uuid4()), "title": title, "description": description, "status": "pending"
		}
		if file:
			os.makedirs(settings.DATA_PATH, exist_ok=True)
			file_path = os.path.join(settings.DATA_PATH, file.filename)
			with open(file_path, "wb+") as f:
				f.write(file.file.read())
			new_source["source_type"] = "file"
			new_source["source_name"] = file.filename
		elif url:
			new_source["source_type"] = "url"
			new_source["source_name"] = url
		else:
			logger.info(f"No URL or File uploaded: {title}")
			return None

		metadata.append(new_source)
		if write_metadata(metadata):
			logger.info(f"Successfully added new source: {title}")
			return new_source
		else:
			return None
	except Exception as e:
		logger.error(f"Failed to add new source: {e}", exc_info=True)
		return None

def remove_source(source_id: str) -> bool:
	try:
		metadata = read_metadata()
		source_to_delete = next((item for item in metadata if item["id"] == source_id), None)
		if not source_to_delete:
			logger.warning(f"Attempted to delete non-existent source with id: {source_id}")
			return False

		# Xóa các vector liên quan trong ChromaDB
		try:
			logger.info(f"Deleting vectors for source_id: {source_id} from ChromaDB.")
			embedding_function = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
			db = Chroma(persist_directory=settings.DB_PATH, embedding_function=embedding_function)

			# Xóa các vector có metadata khớp với source_id
			db.delete(where={"source_id": source_id})
			logger.info(f"Successfully deleted vectors for source_id: {source_id}.")
		except Exception as e:
			# Lỗi xóa vector không nên ngăn việc xóa file và metadata, chỉ ghi log
			logger.error(f"Could not delete vectors for source_id {source_id}: {e}", exc_info=True)

		# Xóa file vật lý nếu có
		if source_to_delete["source_type"] == "file":
			file_path = os.path.join(settings.DATA_PATH, source_to_delete["source_name"])
			if os.path.exists(file_path):
				os.remove(file_path)

		# Xóa metadata
		updated_metadata = [item for item in metadata if item["id"] != source_id]
		if write_metadata(updated_metadata):
			logger.info(f"Successfully removed source metadata with id: {source_id}")
			return True
		else:
			return False
	except Exception as e:
		logger.error(f"Failed to remove source with id {source_id}: {e}", exc_info=True)
		return False

def update_source(source_id: str, source_data: UpdateSource):
	try:
		metadata = read_metadata()
		source_to_update = next((item for item in metadata if item["id"] == source_id), None)
		if not source_to_update:
			logger.warning(f"Attempted to update non-existent source with id: {source_id}")
			return None

		source_to_update["title"] = source_data.title
		source_to_update["description"] = source_data.description
		if write_metadata(metadata):
			logger.info(f"Successfully updated source with id: {source_id}")
			return source_to_update
		else:
			return None
	except Exception as e:
		logger.error(f"Failed to update source with id {source_id}: {e}", exc_info=True)
		return None

def trigger_reindex() -> dict:
	try:
		# Chạy ingest.py như một tiến trình con
		process = subprocess.Popen(["python", "scripts/ingest.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
								   text=True)
		stdout, stderr = process.communicate()
		if process.returncode != 0:
			logger.error(f"Re-indexing process failed with stderr: {stderr}")
			return {"success": False, "message": f"Re-indexing process failed: {stderr}"}

		logger.info(f"Successfully triggered re-indexing. Output: {stdout}")
		return {"success": True, "message": "Knowledge base update has been requested!"}
	except Exception as e:
		logger.error(f"Failed to trigger re-index process: {e}", exc_info=True)
		return {"success": False, "message": f"Server error while triggering re-index: {e}"}

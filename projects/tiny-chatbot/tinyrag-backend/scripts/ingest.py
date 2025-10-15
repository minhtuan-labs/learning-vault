import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import PyPDFLoader, TextLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)

def create_vector_db():
	try:
		with open(settings.METADATA_FILE, "r", encoding="utf-8") as f:
			metadata_list = json.load(f)
	except (FileNotFoundError, json.JSONDecodeError):
		logger.warning("metadata.json not found or is invalid. Stopping ingestion.")
		return

	items_to_process = [item for item in metadata_list if item.get("status") == "pending"]

	if not items_to_process:
		logger.info("No new documents to process.")
		return

	logger.info(f"Found {len(items_to_process)} new documents to process...")

	all_new_chunks = []  # Tạo một list mới để chứa tất cả các chunk

	for item in items_to_process:
		source_id = item.get("id")
		source_type = item.get("source_type")
		source_name = item.get("source_name")

		try:
			loader = None
			if source_type == "file":
				file_path = os.path.join(settings.DATA_PATH, source_name)
				if file_path.endswith(".pdf"):
					loader = PyPDFLoader(file_path)
				elif file_path.endswith(".txt"):
					loader = TextLoader(file_path)
				else:
					logger.warning(f"Unsupported file type for {source_name}. Skipping.")
					continue
			elif source_type == "url":
				loader = WebBaseLoader(source_name)

			if not loader:
				continue

			# Tải và cắt văn bản
			documents = loader.load()
			text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
			chunks = text_splitter.split_documents(documents)

			# Gán source_id vào metadata của mỗi chunk
			for chunk in chunks:
				if chunk.metadata is None:
					chunk.metadata = {}
				chunk.metadata["source_id"] = source_id

			all_new_chunks.extend(chunks)
			logger.info(f"Processed {source_type}: {source_name}, generated {len(chunks)} chunks.")

		except Exception as e:
			logger.error(f"Error processing source '{source_name}': {e}", exc_info=True)
			item['status'] = 'failed'
			continue

	if not all_new_chunks:
		logger.warning("Could not load any new documents from pending sources. Stopping.")
		write_metadata(metadata_list)
		return

	logger.info(f"Total new chunks to add: {len(all_new_chunks)}.")
	logger.info("Vectorizing and adding to the database...")
	embedding_function = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)

	try:
		db = Chroma(persist_directory=settings.DB_PATH, embedding_function=embedding_function)
		db.add_documents(all_new_chunks)
		logger.info("Successfully added new vectors to the database.")

		for item in items_to_process:
			if item.get('status') != 'failed':
				item['status'] = 'indexed'

		write_metadata(metadata_list)
		logger.info("Updated metadata.json file.")
	except Exception as e:
		logger.error(f"Failed to add documents to ChromaDB: {e}", exc_info=True)

def write_metadata(data):
	try:
		with open(settings.METADATA_FILE, "w", encoding="utf-8") as f:
			json.dump(data, f, indent=4, ensure_ascii=False)
	except IOError as e:
		logger.error(f"Failed to write metadata to file: {e}", exc_info=True)

if __name__ == "__main__":
	create_vector_db()

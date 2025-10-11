import requests
from core.config import settings

def ask_question(question: str):
	"""Gửi một câu hỏi đơn giản đến RAG service."""
	url = f"{settings.BACKEND_URL_BASE}/rag/ask"
	try:
		response = requests.post(url, json={"question": question}, timeout=120)
		response.raise_for_status()
		return response.json().get("answer", "Error: Invalid response.")
	except requests.exceptions.HTTPError as http_err:
		try:
			detail = http_err.response.json().get("detail", str(http_err))
			return f"**Backend Error:**\n\n```\n{detail}\n```"
		except:
			return f"**Backend HTTP Error:** {http_err}"
	except requests.exceptions.RequestException as e:
		return f"**Connection Error:** {e}"

def get_data_sources(page: int = 1):
	"""Lấy danh sách các nguồn tri thức có phân trang."""
	url = f"{settings.BACKEND_URL_BASE}/data-sources?page={page}&page_size={settings.PAGE_SIZE}"
	try:
		response = requests.get(url)
		response.raise_for_status()
		return response.json()
	except requests.exceptions.RequestException:
		return {"items": [], "total_pages": 1}

def add_data_source(title: str, description: str, url: str or None, file_data: tuple or None):
	"""Thêm một nguồn tri thức mới."""
	url_endpoint = f"{settings.BACKEND_URL_BASE}/data-sources"
	files = {'file': file_data} if file_data else None
	data = {'title': title, 'description': description, 'url': url or ''}
	try:
		response = requests.post(url_endpoint, files=files, data=data)
		response.raise_for_status()
		return True, "Successfully added!"
	except requests.exceptions.RequestException as e:
		return False, f"Error: {e}"

def delete_data_source(source_id: str):
	"""Xóa một nguồn tri thức."""
	url = f"{settings.BACKEND_URL_BASE}/data-sources/{source_id}"
	try:
		requests.delete(url).raise_for_status()
		return True
	except:
		return False

def update_data_source(source_id: str, source_data: dict):
	"""Cập nhật title và description cho một nguồn dữ liệu."""
	url = f"{settings.BACKEND_URL_BASE}/data-sources/{source_id}"
	try:
		requests.put(url, json=source_data).raise_for_status()
		return True
	except:
		return False

def reindex_knowledge_base():
	"""Kích hoạt quá trình cập nhật CSDL Vector."""
	url = f"{settings.BACKEND_URL_BASE}/data-sources/re-index"
	try:
		response = requests.post(url)
		response.raise_for_status()
		return True, response.json().get('message')
	except:
		return False, "Connection Error"

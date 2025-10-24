import streamlit as st
import requests
from core.config import settings
from datetime import datetime, timedelta
import json


def _is_token_valid(token: str) -> bool:
	"""Kiểm tra token có còn hợp lệ không"""
	try:
		# Decode JWT token để kiểm tra expiration
		import base64
		parts = token.split('.')
		if len(parts) != 3:
			return False
		
		# Decode payload
		payload = parts[1]
		# Add padding if needed
		payload += '=' * (4 - len(payload) % 4)
		decoded = base64.urlsafe_b64decode(payload)
		payload_data = json.loads(decoded)
		
		# Kiểm tra expiration
		exp = payload_data.get('exp')
		if exp:
			exp_time = datetime.fromtimestamp(exp)
			return datetime.now() < exp_time
		return True
	except Exception:
		return False


def _clear_auth_session():
	"""Xóa session và cookie khi token hết hạn"""
	if 'auth_token' in st.session_state:
		del st.session_state['auth_token']
	# Clear cookie nếu có
	try:
		from utils import auth
		auth.logout()
	except:
		pass


def login(username, password):
	try:
		response = requests.post(
			f"{settings.PAM_BACKEND_API_URL}/api/v1/users/token",
			data={"username": username, "password": password}
		)
		response.raise_for_status() # Ném lỗi nếu status code là 4xx hoặc 5xx
		return response.json()
	except requests.exceptions.RequestException as e:
		if e.response is not None:
			try:
				error_details = e.response.json().get('detail', 'An unknown error occurred.')
				st.warning(f"{error_details}")
			except requests.exceptions.JSONDecodeError:
				st.error(f"Login failed: Server returned an unexpected response. Please check backend logs.")
				st.error(f"Raw error: {e.response.text[:500]}")
		else:
			st.error(f"Login failed: Could not connect to the backend server. {e}")
		return None


def get_data(endpoint: str):
	token = st.session_state.get('auth_token')
	if not token:
		st.error("Authentication token not found. Please login again.")
		return None
	
	# Kiểm tra token expiration
	if not _is_token_valid(token):
		st.error("Your session has expired. Please login again.")
		_clear_auth_session()
		return None
	
	headers = {"Authorization": f"Bearer {token}"}
	try:
		response = requests.get(f"{settings.PAM_BACKEND_API_URL}{endpoint}", headers=headers, timeout=10)
		response.raise_for_status()
		return response.json()
	except requests.exceptions.Timeout:
		st.error("Request timeout. Please check your connection and try again.")
		return None
	except requests.exceptions.ConnectionError:
		st.error("Could not connect to the server. Please check if the backend is running.")
		return None
	except requests.exceptions.RequestException as e:
		if e.response is not None:
			if e.response.status_code == 401:
				st.error("Authentication failed. Please login again.")
				_clear_auth_session()
				return None
			try:
				error_details = e.response.json().get('detail', 'No JSON detail found.')
			except requests.exceptions.JSONDecodeError:
				error_details = e.response.text
			st.error(f"Error details: {error_details}")
		else:
			st.error(f"Failed to fetch data from {endpoint}: {e}")
		return None


def post_data(endpoint: str, data: dict, params: dict | None = None):
	"""Hàm chung để gửi dữ liệu (tạo mới) đến các endpoint được bảo vệ."""
	token = st.session_state.get('auth_token')
	if not token:
		st.error("Authentication token not found. Please login again.")
		return None
	
	# Kiểm tra token expiration
	if not _is_token_valid(token):
		st.error("Your session has expired. Please login again.")
		_clear_auth_session()
		return None
	
	headers = {"Authorization": f"Bearer {token}"}
	try:
		response = requests.post(f"{settings.PAM_BACKEND_API_URL}{endpoint}", headers=headers, json=data, params=params, timeout=10)
		response.raise_for_status()
		return response.json()
	except requests.exceptions.Timeout:
		st.error("Request timeout. Please check your connection and try again.")
		return None
	except requests.exceptions.ConnectionError:
		st.error("Could not connect to the server. Please check if the backend is running.")
		return None
	except requests.exceptions.RequestException as e:
		if e.response is not None:
			if e.response.status_code == 401:
				st.error("Authentication failed. Please login again.")
				_clear_auth_session()
				return None
			try:
				error_details = e.response.json().get('detail', 'No JSON detail found.')
			except requests.exceptions.JSONDecodeError:
				error_details = e.response.text
			st.error(f"Error details: {error_details}")
		else:
			st.error(f"Failed to create resource at {endpoint}: {e}")
		return None


def patch_data(endpoint: str, data: dict):
	"""Hàm chung để gửi yêu cầu cập nhật (PATCH) đến các endpoint được bảo vệ."""
	token = st.session_state.get('auth_token')
	if not token:
		st.error("Authentication token not found. Please login again.")
		return None
	
	# Kiểm tra token expiration
	if not _is_token_valid(token):
		st.error("Your session has expired. Please login again.")
		_clear_auth_session()
		return None

	headers = {"Authorization": f"Bearer {token}"}
	try:
		response = requests.patch(f"{settings.PAM_BACKEND_API_URL}{endpoint}", headers=headers, json=data, timeout=10)
		response.raise_for_status()
		return response.json()
	except requests.exceptions.Timeout:
		st.error("Request timeout. Please check your connection and try again.")
		return None
	except requests.exceptions.ConnectionError:
		st.error("Could not connect to the server. Please check if the backend is running.")
		return None
	except requests.exceptions.RequestException as e:
		if e.response is not None:
			if e.response.status_code == 401:
				st.error("Authentication failed. Please login again.")
				_clear_auth_session()
				return None
			try:
				error_details = e.response.json().get('detail', 'No JSON detail found.')
			except requests.exceptions.JSONDecodeError:
				error_details = e.response.text
			st.error(f"Error details: {error_details}")
		else:
			st.error(f"Failed to update resource at {endpoint}: {e}")
		return None


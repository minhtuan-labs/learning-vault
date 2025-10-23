import streamlit as st
import requests
from core.config import settings


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
	headers = {"Authorization": f"Bearer {token}"}
	try:
		response = requests.get(f"{settings.PAM_BACKEND_API_URL}{endpoint}", headers=headers)
		response.raise_for_status()
		return response.json()
	except requests.exceptions.RequestException as e:
		st.error(f"Failed to fetch data from {endpoint}: {e}")
		if e.response is not None:
			try:
				error_details = e.response.json().get('detail', 'No JSON detail found.')
			except requests.exceptions.JSONDecodeError:
				error_details = e.response.text
			st.error(f"Error details: {error_details}")
		return None


def post_data(endpoint: str, data: dict, params: dict | None = None):
	token = st.session_state.get('auth_token')
	if not token:
		"""Hàm chung để gửi dữ liệu (tạo mới) đến các endpoint được bảo vệ."""
		token = st.session_state.get('auth_token')
	if not token:
		st.error("Authentication token not found. Please login again.")
		return None
	headers = {"Authorization": f"Bearer {token}"}
	try:
		response = requests.post(f"{settings.PAM_BACKEND_API_URL}{endpoint}", headers=headers, json=data, params=params)
		response.raise_for_status()
		return response.json()
	except requests.exceptions.RequestException as e:
		st.error(f"Failed to create resource at {endpoint}: {e}")
		if e.response is not None:
			try:
				error_details = e.response.json().get('detail', 'No JSON detail found.')
			except requests.exceptions.JSONDecodeError:
				error_details = e.response.text
			st.error(f"Error details: {error_details}")
	return None


def patch_data(endpoint: str, data: dict):
	"""Hàm chung để gửi yêu cầu cập nhật (PATCH) đến các endpoint được bảo vệ."""
	token = st.session_state.get('auth_token')
	if not token:
		st.error("Authentication token not found. Please login again.")
		return None

	headers = {"Authorization": f"Bearer {token}"}
	try:
		response = requests.patch(f"{settings.PAM_BACKEND_API_URL}{endpoint}", headers=headers, json=data)
		response.raise_for_status()
		return response.json()
	except requests.exceptions.RequestException as e:
		st.error(f"Failed to update resource at {endpoint}: {e}")
		if e.response is not None:
			try:
				error_details = e.response.json().get('detail', 'No JSON detail found.')
			except requests.exceptions.JSONDecodeError:
				error_details = e.response.text
			st.error(f"Error details: {error_details}")
		return None


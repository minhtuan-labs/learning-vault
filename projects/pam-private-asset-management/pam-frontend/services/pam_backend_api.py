import streamlit as st
import requests
from core.config import settings


def login(username, password):
	try:
		response = requests.post(
			f"{settings.PAM_BACKEND_API_URL}/api/v1/users/token",
			data={"username": username, "password": password}
		)
		response.raise_for_status()
		return response.json()
	except requests.exceptions.RequestException as e:
		st.error(f"Login failed: {e}")
		if e.response is not None:
			st.error(f"Error details: {e.response.json().get('detail', 'No details')}")
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
			st.error(f"Error details: {e.response.json().get('detail', 'No details')}")
		return None


def post_data(endpoint: str, data: dict):
	"""Hàm chung để gửi dữ liệu (tạo mới) đến các endpoint được bảo vệ."""
	token = st.session_state.get('auth_token')
	if not token:
		st.error("Authentication token not found. Please login again.")
		return None
	headers = {"Authorization": f"Bearer {token}"}
	try:
		response = requests.post(f"{settings.PAM_BACKEND_API_URL}{endpoint}", headers=headers, json=data)
		response.raise_for_status()
		return response.json()
	except requests.exceptions.RequestException as e:
		st.error(f"Failed to create resource at {endpoint}: {e}")
		if e.response is not None:
			st.error(f"Error details: {e.response.json().get('detail', 'No details')}")
		return None


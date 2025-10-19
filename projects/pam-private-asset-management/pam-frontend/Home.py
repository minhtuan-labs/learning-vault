import streamlit as st
# Import các hàm đã được tách ra từ module service
from services import pam_backend_api as api

# --- Cấu hình trang ---
st.set_page_config(
	page_title="My PAM | Login",
	page_icon="🔐",
	layout="centered"
)

# --- Giao diện ---
st.title("🔐 My Private Asset Management")

# Khởi tạo session state để lưu trạng thái đăng nhập nếu chưa có
if 'auth_token' not in st.session_state:
	st.session_state['auth_token'] = None

# --- Logic hiển thị ---

# Nếu người dùng đã đăng nhập
if st.session_state['auth_token']:
	st.success("You are logged in successfully!")
	st.info("Select a page from the sidebar to start managing your assets.")

	if st.button("Logout"):
		st.session_state['auth_token'] = None
		st.success("You have been logged out.")
		st.rerun()  # Chạy lại script để hiển thị lại form đăng nhập

# Nếu người dùng chưa đăng nhập
else:
	# Hiển thị form đăng nhập
	with st.form("login_form"):
		st.header("Login")
		username = st.text_input("Username")
		password = st.text_input("Password", type="password")
		submitted = st.form_submit_button("Login")

		if submitted:
			if not username or not password:
				st.warning("Please enter both username and password.")
			else:
				with st.spinner("Logging in..."):
					# Gọi hàm login từ module API
					token_data = api.login(username, password)
					if token_data:
						# Lưu token vào session state để duy trì đăng nhập
						st.session_state['auth_token'] = token_data['access_token']
						st.success("Login successful!")
						st.rerun()  # Chạy lại script để hiển thị thông báo đã đăng nhập


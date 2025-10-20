import streamlit as st
from services import pam_backend_api as api
from utils import auth

# --- Cấu hình trang ---
st.set_page_config(
	page_title="My PAM | Login",
	page_icon="🔐",
	layout="centered"
)

# Khởi tạo session, khôi phục từ cookie nếu có
auth.initialize_session()

# --- Giao diện ---
st.title("🔐 My Private Asset Management")

# --- Logic hiển thị ---

# Sử dụng hàm is_authenticated() để kiểm tra trạng thái đăng nhập
if auth.is_authenticated():
	st.success("You are logged in successfully!")
	st.info("Select a page from the sidebar to start managing your assets.")

	# Sử dụng hàm logout() để xử lý đăng xuất
	if st.button("Logout"):
		auth.logout()
		st.success("You have been logged out.")
		st.rerun()
else:
	# Hiển thị form đăng nhập nếu chưa xác thực
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
					token_data = api.login(username, password)
					if token_data:
						# Sử dụng hàm login() để lưu token
						auth.login(token_data['access_token'])
						st.success("Login successful!")
						st.rerun()


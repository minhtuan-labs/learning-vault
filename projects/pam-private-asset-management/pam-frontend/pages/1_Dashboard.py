import streamlit as st
from utils import auth

# --- Cấu hình trang ---
st.set_page_config(
    page_title="My PAM | Dashboard",
    page_icon="📊",
    layout="wide"
)

# SỬA LỖI: Thêm dòng khởi tạo session ở đầu
auth.initialize_session()

st.title("📊 Dashboard")

# --- Kiểm tra xác thực (sử dụng hàm is_authenticated() cho nhất quán) ---
if not auth.is_authenticated():
    st.warning("Please login to access this page.")
    st.stop() # Dừng thực thi script nếu chưa đăng nhập

# --- Nội dung trang ---
st.success(f"Welcome to your dashboard!")
st.write("This page will show an overview of your assets.")


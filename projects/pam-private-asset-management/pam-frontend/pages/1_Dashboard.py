import streamlit as st

# --- Cấu hình trang ---
st.set_page_config(
    page_title="My PAM | Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard")

# --- Kiểm tra xác thực ---
# Đây là bước cực kỳ quan trọng cho mọi trang con
if 'auth_token' not in st.session_state or st.session_state['auth_token'] is None:
    st.warning("Please login to access this page.")
    st.stop() # Dừng thực thi script nếu chưa đăng nhập

# --- Nội dung trang ---
st.write("Welcome to your dashboard!")
st.write("This page will show an overview of your assets.")

# (Chúng ta sẽ thêm logic gọi API và vẽ biểu đồ ở đây sau)


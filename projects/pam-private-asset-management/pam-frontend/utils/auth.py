import streamlit as st
# SỬA LỖI: Thêm dòng import còn thiếu
from streamlit_cookies_manager import EncryptedCookieManager

# Khởi tạo cookie manager. `key` là một chuỗi bí mật để mã hóa cookie.
# Nó nên được đặt trong biến môi trường trong thực tế, nhưng tạm thời để đây.
# SỬA LỖI: Đổi tên tham số từ `key` thành `password`
cookies = EncryptedCookieManager(
    password="my_super_secret_pam_cookie_key"
)

def initialize_session():
    """
    Hàm này sẽ được gọi ở đầu mỗi trang.
    Nó kiểm tra session state và cookie để khôi phục trạng thái đăng nhập.
    """
    if 'auth_token' not in st.session_state:
        # Thử đọc token từ cookie nếu có
        st.session_state['auth_token'] = cookies.get('auth_token')

def is_authenticated():
    """Kiểm tra xem người dùng đã đăng nhập hay chưa."""
    return st.session_state.get('auth_token') is not None

def login(token: str):
    """Lưu token vào session state và set cookie."""
    st.session_state['auth_token'] = token
    cookies['auth_token'] = token
    cookies.save()

def logout():
    """Xóa token khỏi session state và xóa cookie."""
    st.session_state['auth_token'] = None
    if 'auth_token' in cookies:
        del cookies['auth_token']
        cookies.save()


import streamlit as st
import pandas as pd
from services import pam_backend_api as api

# --- Cấu hình trang ---
st.set_page_config(
	page_title="My PAM | Manage Assets",
	page_icon="💼",
	layout="wide"
)

st.title("💼 Manage Your Assets")

# --- Kiểm tra xác thực ---
# Đảm bảo người dùng đã đăng nhập trước khi hiển thị nội dung
if 'auth_token' not in st.session_state or st.session_state['auth_token'] is None:
	st.warning("Please login to access this page.")
	st.stop()

# --- Chức năng chính ---

# Hiển thị danh sách các tài sản hiện có
st.header("Your Current Assets")

with st.spinner("Fetching assets..."):
	assets_data = api.get_data("/api/v1/assets/")

if assets_data is not None:
	if assets_data:
		# Chuyển dữ liệu sang DataFrame của Pandas để hiển thị bảng đẹp hơn
		df = pd.DataFrame(assets_data)
		# Sắp xếp và chọn các cột cần hiển thị
		df_display = df[['id', 'name', 'asset_type', 'cost_basis', 'created_at']]
		st.dataframe(df_display, use_container_width=True)
	else:
		st.info("You don't have any assets yet. Add one below!")
else:
	st.error("Could not load asset data.")

st.divider()

# Form để tạo tài sản mới
st.header("Create a New Asset")
with st.form("new_asset_form", clear_on_submit=True):
	name = st.text_input("Asset Name", placeholder="E.g., VPS Securities Account, Techcombank Savings")
	# Lấy danh sách các loại asset từ Enum đã định nghĩa ở backend
	# Đây là một ví dụ, trong thực tế có thể gọi một API để lấy danh sách này
	asset_type = st.selectbox(
		"Asset Type",
		("CASH", "STOCKS", "FUNDS", "SAVINGS")
	)

	submitted = st.form_submit_button("Create Asset")

	if submitted:
		if not name:
			st.warning("Please enter an asset name.")
		else:
			new_asset_data = {"name": name, "asset_type": asset_type}
			with st.spinner("Creating asset..."):
				result = api.post_data("/api/v1/assets/", data=new_asset_data)
				if result:
					st.success(f"Asset '{result['name']}' created successfully!")
				# Gợi ý: Có thể dùng st.rerun() để tự động làm mới danh sách tài sản
				# Tuy nhiên, để tránh refresh liên tục, chúng ta sẽ để người dùng tự refresh
				# Hoặc có thể quản lý state phức tạp hơn sau này.
			# Nếu có lỗi, thông báo đã được hiển thị bên trong hàm post_data

import streamlit as st
import pandas as pd
from services import pam_backend_api as api
from datetime import datetime, date
from utils import auth
from enum import Enum
import math  # Import math for rounding


# Tạm định nghĩa Enum và Mapping cho hiển thị ngắn gọn
class SavingTypeEnumFE(Enum):
	TERM_DEPOSIT = "term_deposit"
	CERTIFICATE_OF_DEPOSIT = "certificate_of_deposit"


SAVING_TYPE_DISPLAY_MAP = {
	"term_deposit": "Term",
	"certificate_of_deposit": "Cert"
}

# --- Cấu hình trang ---
st.set_page_config(
	page_title="My PAM | Savings",
	page_icon="🏦",
	layout="wide"
)

# Khởi tạo và kiểm tra xác thực
auth.initialize_session()
st.title("🏦 Savings & Deposits")

if not auth.is_authenticated():
	st.warning("Please login to access this page.")
	st.stop()


# --- Chức năng chính ---

@st.cache_data(ttl=60)
def load_savings():
	"""Tải danh sách các Asset loại SAVINGS và chi tiết của chúng."""
	all_assets = api.get_data("/api/v1/assets/")
	savings_list = []
	if all_assets:
		savings_assets = [a for a in all_assets if a['asset_type'] == 'savings']
		for asset in savings_assets:
			# Sửa lỗi tiềm ẩn: Kiểm tra detail_res trước khi truy cập
			detail_res = api.get_data(f"/api/v1/assets/{asset['id']}/savings/")
			if detail_res and isinstance(detail_res, dict):  # Đảm bảo detail_res là dict hợp lệ
				savings_list.append({
					"asset_id": asset['id'],
					"name": asset['name'],
					"saving_id": detail_res.get('id'),  # Dùng .get() để an toàn
					**detail_res
				})
			elif detail_res is None:
				st.error(f"Could not load details for asset ID {asset['id']}. Skipping.")
		# else: # Xử lý trường hợp detail_res không phải dict nếu cần
		#      st.error(f"Unexpected data format for asset ID {asset['id']}: {detail_res}")

	return savings_list


# 1. FORM NHẬP LIỆU KHOẢN TIẾT KIỆM MỚI
with st.expander("Record a New Saving/Deposit", expanded=False):
	with st.form("new_saving_form", clear_on_submit=True):
		st.subheader("Asset Information")
		asset_name = st.text_input("Saving Account Name", placeholder="E.g., Techcombank 6-month Deposit")

		st.subheader("Saving Details")
		col1, col2, col3 = st.columns(3)
		with col1:
			saving_type = st.selectbox("Saving Type", options=[e.value for e in SavingTypeEnumFE])
			initial_amount = st.number_input("Initial Amount (VND)", min_value=1, step=1000, format="%d")
		with col2:
			interest_rate_pa = st.number_input("Interest Rate (% p.a.)", min_value=0.0, step=0.1, format="%.1f")
			term_months = st.number_input("Term (Months)", min_value=1, step=1, value=6)
		with col3:
			start_date = st.date_input("Start Date", value=date.today())
			bank_code = st.text_input("Bank Code (Optional)", max_chars=10)

		submitted = st.form_submit_button("Record Saving")

		if submitted:
			if not all([asset_name, saving_type, initial_amount, interest_rate_pa, term_months, start_date]):
				st.warning("Please fill in all required fields.")
			else:
				asset_data = {"name": asset_name, "asset_type": "savings"}
				with st.spinner("Creating asset..."):
					asset_result = api.post_data("/api/v1/assets/", data=asset_data)

				if asset_result:
					new_asset_id = asset_result['id']
					saving_data = {
						"saving_type": saving_type, "initial_amount": float(initial_amount),
						"interest_rate_pa": interest_rate_pa, "term_months": term_months,
						"start_date": start_date.isoformat(), "bank_code": bank_code,
					}
					with st.spinner("Recording saving details..."):
						saving_result = api.post_data(f"/api/v1/assets/{new_asset_id}/savings/", data=saving_data)
						if saving_result:
							st.success(f"Successfully recorded saving '{asset_name}'!")
							load_savings.clear()
							st.rerun()
						else:
							st.error("Failed to record saving details.")
				else:
					st.error("Failed to create the asset.")

# 2. BẢNG HIỂN THỊ VÀ TƯƠNG TÁC (Sử dụng st.columns)
st.divider()
st.header("Current Savings & Deposits")

col_left_filter, col_right_filter = st.columns([3, 1])
with col_right_filter:
	show_matured = st.toggle("Show matured savings", value=False, key="show_matured_toggle")

savings_data = load_savings()

# Khởi tạo cờ kiểm soát vòng lặp
if 'saving_update_processed' not in st.session_state:
	st.session_state.saving_update_processed = False

if savings_data:
	df_savings = pd.DataFrame(savings_data)

	# Lọc dựa trên toggle
	if not show_matured:
		df_display = df_savings[df_savings['is_matured'] == False].copy()
	else:
		df_display = df_savings.copy()

	if not df_display.empty:
		st.subheader("Savings List")

		# --- SỬA ĐỔI: Tạo bảng thủ công bằng st.columns ---

		# Tạo header
		cols_header = st.columns([2.5, 0.8, 1.2, 0.8, 0.8, 1, 1.2, 1])  # Điều chỉnh tỉ lệ cột
		headers = ["Account Name", "Type", "Initial (VND)", "Rate (%)", "Term", "Start Date", "Est. Maturity (VND)",
				   "Action"]
		for col, header in zip(cols_header, headers):
			col.markdown(f"**{header}**")
		st.markdown("""<hr style="height:2px;border:none;color:#333;background-color:#eee;" /> """,
					unsafe_allow_html=True)  # Dòng kẻ đậm hơn

		# Lặp qua từng dòng dữ liệu để hiển thị
		for index, row in df_display.iterrows():
			# Tính toán EMA
			ema = math.ceil(
				row['initial_amount'] * (1 + (row['interest_rate_pa'] / 100) * (row['term_months'] / 12))) if row.get(
				'term_months') else row['initial_amount']

			cols_data = st.columns([2.5, 0.8, 1.2, 0.8, 0.8, 1, 1.2, 1])
			cols_data[0].write(row['name'])
			cols_data[1].write(SAVING_TYPE_DISPLAY_MAP.get(row['saving_type'], row['saving_type']))  # Dùng map
			cols_data[2].write(f"{int(round(row['initial_amount'], 0)):,}")  # Làm tròn, bỏ thập phân
			cols_data[3].write(f"{row['interest_rate_pa']:.1f}%")
			cols_data[4].write(row.get('term_months', '-'))  # Dùng get phòng trường hợp thiếu
			cols_data[5].write(pd.to_datetime(row['start_date']).strftime('%Y-%m-%d'))
			cols_data[6].write(f"{int(round(ema, 0)):,}")

			# Nút hành động tích hợp vào dòng
			action_button_placeholder = cols_data[7].empty()
			unique_key_mature = f"mature_{row['saving_id']}_{index}"
			unique_key_undo = f"undo_{row['saving_id']}_{index}"

			if not row['is_matured']:
				if action_button_placeholder.button("Mark Matured", key=unique_key_mature, type="primary",
													use_container_width=True):
					st.session_state.saving_to_mature = row['saving_id']
					st.rerun()
			else:
				if action_button_placeholder.button("Undo", key=unique_key_undo, type="secondary",
													use_container_width=True):  # Nút ngắn gọn hơn
					with st.spinner("Undoing maturity..."):
						update_data = {"is_matured": False, "actual_settlement_date": None, "matured_amount": None}
						result = api.patch_data(f"/api/v1/savings/{row['saving_id']}", data=update_data)
						if result:
							st.toast("Maturity undone successfully!")
							load_savings.clear()
							st.session_state.saving_update_processed = True
							st.rerun()
			st.markdown("""<hr style="height:1px;border:none;color:#eee;background-color:#eee;" /> """,
						unsafe_allow_html=True)  # Dòng kẻ mỏng

		# --- FORM XÁC NHẬN TẤT TOÁN (Popup) ---
		if 'saving_to_mature' in st.session_state and st.session_state.saving_to_mature is not None:
			saving_id_to_mature = st.session_state.saving_to_mature
			# Sửa lỗi tiềm ẩn: Đảm bảo saving_id_to_mature có trong df_savings trước khi truy cập
			saving_to_edit_list = df_savings[df_savings['saving_id'] == saving_id_to_mature]
			if not saving_to_edit_list.empty:
				saving_to_edit_series = saving_to_edit_list.iloc[0]

				with st.dialog("Confirm Maturity"):
					st.subheader(f"Confirm Maturity for: {saving_to_edit_series['name']}")

					estimated_matured = saving_to_edit_series['initial_amount'] * (
								1 + (saving_to_edit_series['interest_rate_pa'] / 100) * (
									saving_to_edit_series['term_months'] / 12)) if saving_to_edit_series.get(
						'term_months') else saving_to_edit_series['initial_amount']

					actual_date = st.date_input("Actual Settlement Date", value=date.today())
					matured_amount = st.number_input(
						"Matured Amount Received (VND)", min_value=0, step=1000, format="%d",
						value=math.ceil(estimated_matured)
					)

					col_btn1, col_btn2 = st.columns(2)
					with col_btn1:
						if st.button("Confirm Maturity", use_container_width=True, type="primary"):
							update_data = {
								"is_matured": True,
								"actual_settlement_date": actual_date.isoformat(),
								"matured_amount": float(matured_amount)
							}
							with st.spinner("Confirming maturity..."):
								result = api.patch_data(f"/api/v1/savings/{saving_id_to_mature}", data=update_data)
								if result:
									st.toast("Saving marked as matured!")
									load_savings.clear()
									st.session_state.saving_update_processed = True
									del st.session_state.saving_to_mature
									st.rerun()
								else:
									st.error("Failed to update saving status.")
					with col_btn2:
						if st.button("Cancel", use_container_width=True, type="secondary"):
							del st.session_state.saving_to_mature
							st.rerun()
			else:
				st.error("Could not find the saving record to mark as matured. Please refresh.")
				# Tự động xóa state nếu không tìm thấy record
				if 'saving_to_mature' in st.session_state:
					del st.session_state.saving_to_mature


	else:
		st.info("No savings to display based on current filter.")

elif savings_data is None:
	st.error("Could not load savings data.")
else:
	st.info("You have no savings recorded yet. Add one in the form above.")

# Nút Refresh vẫn giữ lại
if st.button("Refresh Savings Data"):
	load_savings.clear()
	st.rerun()


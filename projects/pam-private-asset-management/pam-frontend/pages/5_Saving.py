import streamlit as st
import pandas as pd
from services import pam_backend_api as api
from datetime import datetime, date
from utils import auth
from enum import Enum


# Tạm định nghĩa Enum ở đây
class SavingTypeEnumFE(Enum):
	TERM_DEPOSIT = "term_deposit"
	CERTIFICATE_OF_DEPOSIT = "certificate_of_deposit"


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

# 1. FORM NHẬP LIỆU KHOẢN TIẾT KIỆM MỚI
with st.expander("Record a New Saving/Deposit", expanded=False):  # Mặc định thu gọn
	with st.form("new_saving_form", clear_on_submit=True):
		st.subheader("Asset Information")
		asset_name = st.text_input("Saving Account Name", placeholder="E.g., Techcombank 6-month Deposit")

		st.subheader("Saving Details")
		col1, col2, col3 = st.columns(3)
		with col1:
			saving_type = st.selectbox("Saving Type", options=[e.value for e in SavingTypeEnumFE])
			initial_amount = st.number_input("Initial Amount", min_value=0.01, format="%.2f")
		with col2:
			interest_rate_pa = st.number_input("Interest Rate (% p.a.)", min_value=0.0, format="%.2f")
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
						"saving_type": saving_type, "initial_amount": initial_amount,
						"interest_rate_pa": interest_rate_pa, "term_months": term_months,
						"start_date": start_date.isoformat(), "bank_code": bank_code,
					}
					with st.spinner("Recording saving details..."):
						saving_result = api.post_data(f"/api/v1/assets/{new_asset_id}/savings/", data=saving_data)
						if saving_result:
							st.success(f"Successfully recorded saving '{asset_name}'!")
							st.cache_data.clear()
							load_savings.clear()
							st.rerun()
						else:
							st.error("Failed to record saving details.")
				else:
					st.error("Failed to create the asset.")

# 2. BẢNG HIỂN THỊ VÀ TƯƠNG TÁC
st.divider()
st.header("Current Savings & Deposits")

col_left_filter, col_right_filter = st.columns([3, 1])
with col_right_filter:
	show_matured = st.toggle("Show matured savings", value=False, key="show_matured_toggle")


@st.cache_data(ttl=60)
def load_savings():
	"""Tải danh sách các Asset loại SAVINGS và chi tiết của chúng."""
	all_assets = api.get_data("/api/v1/assets/")
	savings_list = []
	if all_assets:
		savings_assets = [a for a in all_assets if a['asset_type'] == 'savings']
		for asset in savings_assets:
			# Gọi API mới để lấy SavingDetail
			detail_res = api.get_data(f"/api/v1/assets/{asset['id']}/savings/")
			if detail_res:
				# Gộp thông tin Asset và SavingDetail
				savings_list.append({
					"asset_id": asset['id'],
					"name": asset['name'],
					"saving_id": detail_res['id'],
					**detail_res  # Gộp tất cả các trường từ SavingDetail
				})
	return savings_list


savings_data = load_savings()

if savings_data:
	df_savings = pd.DataFrame(savings_data)

	# Lọc dựa trên toggle
	if not show_matured:
		df_display = df_savings[df_savings['is_matured'] == False].copy()
	else:
		df_display = df_savings.copy()

	if not df_display.empty:
		st.subheader("Savings List")
		# Sử dụng cột để hiển thị nút bên cạnh bảng (hoặc lặp và tạo layout)

		# Tạo header cho bảng hiển thị (dùng st.columns cho đẹp)
		cols_header = st.columns([2, 1, 1, 1, 1, 1, 1, 1, 1])
		headers = ["Account Name", "Type", "Initial Amount", "Rate (%)", "Term", "Start Date", "Matured?",
				   "Maturity Amount", "Actions"]
		for col, header in zip(cols_header, headers):
			col.markdown(f"**{header}**")

		# Lặp qua từng khoản tiết kiệm để hiển thị và tạo nút
		for index, row in df_display.iterrows():
			cols = st.columns([2, 1, 1, 1, 1, 1, 1, 1, 1])
			cols[0].write(row['name'])
			cols[1].write(row['saving_type'])
			cols[2].write(f"{row['initial_amount']:,.2f}")
			cols[3].write(f"{row['interest_rate_pa']:.2f}%")
			cols[4].write(row['term_months'])
			cols[5].write(pd.to_datetime(row['start_date']).strftime('%Y-%m-%d'))
			cols[6].write("Yes" if row['is_matured'] else "No")
			cols[7].write(f"{row['matured_amount']:,.2f}" if row['matured_amount'] is not None else "N/A")

			# Nút hành động
			action_button_placeholder = cols[8].empty()
			if not row['is_matured']:
				if action_button_placeholder.button("Mark Matured", key=f"mature_{row['saving_id']}"):
					# Lưu ID vào session state để hiển thị form xác nhận
					st.session_state.saving_to_mature = row['saving_id']
					st.rerun()  # Chạy lại để hiển thị form xác nhận
			else:
				if action_button_placeholder.button("Undo Maturity", key=f"undo_{row['saving_id']}"):
					with st.spinner("Undoing maturity..."):
						update_data = {
							"is_matured": False,
							"actual_settlement_date": None,  # Xóa ngày và số tiền thực tế
							"matured_amount": None
						}
						result = api.patch_data(f"/api/v1/savings/{row['saving_id']}", data=update_data)
						if result:
							st.toast("Maturity undone successfully!")
							st.cache_data.clear()
							load_savings.clear()
							st.rerun()

		# --- FORM XÁC NHẬN TẤT TOÁN (hiển thị khi cần) ---
		if 'saving_to_mature' in st.session_state and st.session_state.saving_to_mature is not None:
			saving_id_to_mature = st.session_state.saving_to_mature
			saving_to_edit = df_savings[df_savings['saving_id'] == saving_id_to_mature].iloc[0]

			st.divider()
			st.subheader(f"Confirm Maturity for: {saving_to_edit['name']}")
			with st.form(f"confirm_maturity_{saving_id_to_mature}", clear_on_submit=True):
				actual_date = st.date_input("Actual Settlement Date", value=date.today())
				matured_amount = st.number_input("Matured Amount Received", min_value=0.0, format="%.2f",
												 value=saving_to_edit['initial_amount'])

				confirm_submitted = st.form_submit_button("Confirm Maturity")
				cancel_submitted = st.form_submit_button("Cancel")
				if confirm_submitted:
					update_data = {
						"is_matured": True,
						"actual_settlement_date": actual_date.isoformat(),
						"matured_amount": matured_amount
					}
					with st.spinner("Confirming maturity..."):
						result = api.patch_data(f"/api/v1/savings/{saving_id_to_mature}", data=update_data)
						if result:
							st.toast("Saving marked as matured!")
							st.cache_data.clear()
							load_savings.clear()
							# Xóa state để ẩn form
							del st.session_state.saving_to_mature
							st.rerun()
				if cancel_submitted:
					# Xóa state để ẩn form
					del st.session_state.saving_to_mature
					st.rerun()
	else:
		st.info("No savings to display based on current filter.")
else:
	st.info("You have no savings recorded yet. Add one above!")

if st.button("Refresh Savings Data"):
	st.cache_data.clear()
	load_savings.clear()
	st.rerun()


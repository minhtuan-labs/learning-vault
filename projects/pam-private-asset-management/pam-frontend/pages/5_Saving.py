import streamlit as st
import pandas as pd
from services import pam_backend_api as api
from datetime import datetime, date
from utils import auth
from enum import Enum
import math  # Import math
import time  # Import time for a small delay


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
	if all_assets is None:
		return None
	if all_assets:
		savings_assets = [a for a in all_assets if a.get('asset_type') == 'savings']
		for asset in savings_assets:
			asset_id = asset.get('id')
			if asset_id is None:
				continue

			detail_res = api.get_data(f"/api/v1/assets/{asset_id}/savings/")
			if detail_res and isinstance(detail_res, dict):
				savings_list.append({
					"asset_id": asset_id,
					"name": asset.get('name', 'Unnamed Asset'),
					"saving_id": detail_res.get('id'),
					**detail_res
				})
	return savings_list


# 1. FORM NHẬP LIỆU
# ... (code form không đổi) ...
with st.expander("Record a New Saving/Deposit", expanded=False):
	with st.form("new_saving_form", clear_on_submit=True):
		st.subheader("Asset Information")
		asset_name = st.text_input("Saving Account Name", placeholder="E.g., Techcombank 6-month Deposit")

		st.subheader("Saving Details")
		col1, col2, col3 = st.columns(3)
		with col1:
			saving_type = st.selectbox("Saving Type", options=[e.value for e in SavingTypeEnumFE])
			initial_amount = st.number_input("Initial Amount (VND)", min_value=1, step=1000, format="%d",
											 key="initial_amount_input")
		with col2:
			interest_rate_pa = st.number_input("Interest Rate (% p.a.)", min_value=0.0, step=0.1, format="%.1f",
											   key="interest_rate_input")
			term_months = st.number_input("Term (Months)", min_value=1, step=1, value=6, key="term_months_input")
		with col3:
			start_date = st.date_input("Start Date", value=date.today(), key="start_date_input")
			bank_code = st.text_input("Bank Code (Optional)", max_chars=10, key="bank_code_input")

		submitted = st.form_submit_button("Record Saving")

		if submitted:
			# --- Validation input ---
			if not asset_name:
				st.warning("Please enter an asset name.")
			elif not saving_type:
				st.warning("Please select a saving type.")
			elif initial_amount <= 0:
				st.warning("Initial amount must be greater than 0.")
			elif interest_rate_pa < 0:
				st.warning("Interest rate cannot be negative.")
			elif term_months <= 0:
				st.warning("Term must be greater than 0.")
			elif not start_date:
				st.warning("Please select a start date.")
			else:
				# --- Process valid data ---
				asset_data = {"name": asset_name, "asset_type": "savings"}
				asset_created = False
				saving_recorded = False
				with st.spinner("Processing..."):
					asset_result = api.post_data("/api/v1/assets/", data=asset_data)
					if asset_result:
						new_asset_id = asset_result.get('id')
						if new_asset_id:
							asset_created = True
							saving_data = {
								"saving_type": saving_type, "initial_amount": float(initial_amount),
								"interest_rate_pa": interest_rate_pa, "term_months": term_months,
								"start_date": start_date.isoformat(), "bank_code": bank_code,
							}
							saving_result = api.post_data(f"/api/v1/assets/{new_asset_id}/savings/", data=saving_data)
							if saving_result:
								saving_recorded = True

				if asset_created and saving_recorded:
					st.success(f"Successfully recorded saving '{asset_name}'!")
					st.cache_data.clear()
					time.sleep(0.1)
					st.rerun()
				elif asset_created and not saving_recorded:
					st.error("Failed to record saving details after creating asset. Please check backend logs.")
				else:
					st.error("Failed to create the asset for this saving.")

# 2. BẢNG HIỂN THỊ VÀ TƯƠNG TÁC (Dùng st.columns, cải thiện UI)
st.divider()
st.header("Current Savings & Deposits")

col_left_filter, col_right_filter = st.columns([3, 1])
with col_right_filter:
	show_matured = st.toggle("Show matured savings", value=False, key="show_matured_toggle")

savings_data = load_savings()

# Khởi tạo state cho dialog
if 'saving_to_mature' not in st.session_state:
	st.session_state.saving_to_mature = None

if savings_data is None:
	if not auth.is_authenticated():
		st.warning("Session expired or invalid. Please login again.")
		if st.button("Go to Login Page"):
			st.switch_page("Home.py")
	else:
		st.error("Could not load savings data. Please check backend connection or refresh.")
elif not savings_data:
	st.info("You have no savings recorded yet. Add one in the form above.")
else:
	df_savings = pd.DataFrame(savings_data)

	# Lọc dựa trên toggle
	if not show_matured:
		df_display = df_savings[df_savings['is_matured'] == False].copy()
	else:
		df_display = df_savings.copy()

	if not df_display.empty:
		st.subheader("Savings List")

		# --- Tạo bảng thủ công bằng st.columns ---
		column_ratios = [3, 0.8, 1.5, 0.8, 0.8, 1.2, 1.5, 1.2]
		headers = ["Account Name", "Type", "Initial (VND)", "Rate (%)", "Term", "Start Date", "Est. Maturity (VND)",
				   "Action"]

		# --- CSS Tùy chỉnh ---
		st.markdown("""
		<style>
		    /* Căn giữa header và làm đậm */
		    .stMarkdown > div[data-testid="stMarkdownContainer"] > p > strong {
		        display: block; text-align: center; font-weight: bold;
		    }

		    /* SỬA LỖI: Căn giữa dọc (vertical-align) cho TẤT CẢ các cell */
		    div[data-testid="stHorizontalBlock"] > div > div[data-testid^="stVerticalBlock"] { 
		          display: flex; 
		          flex-direction: column; /* Xếp nội dung theo chiều dọc */
		          justify-content: top; /* Căn giữa theo chiều dọc */
		          height: 48px; /* Đặt chiều cao CỐ ĐỊNH cho hàng */
		     }

		    /* Căn phải cho cột số (cho phép markdown <p align='right'> hoạt động) */
		    .stMarkdown[data-testid="stMarkdownContainer"] p[align="right"] { 
		        text-align: right; 
		    }

		    /* Bỏ margin mặc định của <p> để căn chỉnh đẹp hơn */
		    div[data-testid="stHorizontalBlock"] .stMarkdown p {
		         margin-bottom: 0px !important;
		    }

		    /* Giảm padding nút */
		     div[data-testid="stHorizontalBlock"] button {
		          padding-top: 0.1rem !important; padding-bottom: 0.1rem !important;
		          padding-left: 0.5rem !important; padding-right: 0.5rem !important;
		          line-height: 1.2 !important; min-height: auto !important;
		     }

		     /* Căn giữa cụ thể cho cột 2 (Type) và 6 (Start Date) */
		     div[data-testid="stHorizontalBlock"] > div:nth-child(2) p,
		     div[data-testid="stHorizontalBlock"] > div:nth-child(6) p {
		          text-align: center; 
		     }

		     /* Căn trái cột đầu */
		     div[data-testid="stHorizontalBlock"] > div:first-child p {
		          text-align: left !important; 
		     }
		</style>
		""", unsafe_allow_html=True)

		# Tạo header
		cols_header = st.columns(column_ratios)
		for col, header in zip(cols_header, headers):
			col.markdown(f"**{header}**")
		st.markdown("""<hr style="height:2px;border:none;color:#333;background-color:#eee;" /> """,
					unsafe_allow_html=True)

		# Biến để lưu ID cần mở dialog
		saving_id_to_trigger_dialog = None

		# Lặp qua từng dòng dữ liệu để hiển thị
		for index, row in df_display.iterrows():
			initial_amount = row.get('initial_amount', 0)
			interest_rate = row.get('interest_rate_pa', 0)
			term = row.get('term_months')
			ema = math.ceil(initial_amount * (1 + (interest_rate / 100) * (term / 12))) if term else initial_amount

			cols_data = st.columns(column_ratios)
			cols_data[0].markdown(f"<p style='text-align: left;'>{row.get('name', 'N/A')}</p>", unsafe_allow_html=True)
			saving_type_val = row.get('saving_type', '')
			cols_data[1].markdown(f"<p>{SAVING_TYPE_DISPLAY_MAP.get(saving_type_val, saving_type_val)}</p>",
								  unsafe_allow_html=True)
			cols_data[2].markdown(f"<p align='right'>{int(round(initial_amount, 0)):,}</p>", unsafe_allow_html=True)
			cols_data[3].markdown(f"<p align='right'>{interest_rate:.1f}%</p>", unsafe_allow_html=True)
			cols_data[4].markdown(f"<p align='right'>{term if term else '-'}</p>", unsafe_allow_html=True)
			start_date_val = row.get('start_date')
			try:
				cols_data[5].markdown(
					f"<p>{pd.to_datetime(start_date_val).strftime('%Y-%m-%d') if start_date_val else '-'}</p>",
					unsafe_allow_html=True)
			except:
				cols_data[5].markdown("<p style='color: red;'>Invalid Date</p>", unsafe_allow_html=True)
			cols_data[6].markdown(f"<p align='right'>{int(round(ema, 0)):,}</p>", unsafe_allow_html=True)

			action_button_placeholder = cols_data[7]
			saving_id = row.get('saving_id')
			is_matured = row.get('is_matured', False)
			unique_key_mature = f"mature_{saving_id}_{index}"
			unique_key_undo = f"undo_{saving_id}_{index}"

			if saving_id is not None:
				if not is_matured:
					if action_button_placeholder.button("Mature", key=unique_key_mature, type="primary"):
						saving_id_to_trigger_dialog = saving_id
				else:
					if action_button_placeholder.button("Undo", key=unique_key_undo, type="secondary"):
						with st.spinner("Undoing maturity..."):
							update_data = {"is_matured": False, "actual_settlement_date": None, "matured_amount": None}
							result = api.patch_data(f"/api/v1/savings/{saving_id}", data=update_data)
							if result:
								st.toast("Maturity undone successfully!")
								st.cache_data.clear()
								st.rerun()
			else:
				action_button_placeholder.warning("Missing ID")

		# --- FORM XÁC NHẬN TẤT TOÁN (Popup dùng st.dialog) ---
		# SỬA LỖI: Chỉ mở dialog nếu saving_id_to_trigger_dialog được set ở vòng lặp trên
		if saving_id_to_trigger_dialog is not None:
			# Tìm trong df_savings gốc
			saving_to_edit_list = df_savings[df_savings['saving_id'] == saving_id_to_trigger_dialog]

			if not saving_to_edit_list.empty:
				saving_to_edit_series = saving_to_edit_list.iloc[0]


				# Sử dụng st.dialog đúng cách
				@st.dialog("Confirm Maturity")
				def confirm_maturity_dialog(saving_info):
					st.subheader(f"Confirm Maturity for: {saving_info.get('name', 'N/A')}")

					est_initial = saving_info.get('initial_amount', 0)
					est_rate = saving_info.get('interest_rate_pa', 0)
					est_term = saving_info.get('term_months')
					estimated_matured = est_initial * (
								1 + (est_rate / 100) * (est_term / 12)) if est_term else est_initial

					actual_date = st.date_input("Actual Settlement Date", value=date.today(),
												key=f"actual_date_{saving_id_to_trigger_dialog}")
					matured_amount = st.number_input(
						"Matured Amount Received (VND)", min_value=0, step=1000, format="%d",
						value=math.ceil(estimated_matured), key=f"matured_amount_{saving_id_to_trigger_dialog}"
					)

					col_btn1, col_btn2 = st.columns(2)
					with col_btn1:
						if st.button("Confirm", key=f"confirm_mat_{saving_id_to_trigger_dialog}", type="primary"):
							update_data = {
								"is_matured": True,
								"actual_settlement_date": actual_date.isoformat(),
								"matured_amount": float(matured_amount)
							}
							result = api.patch_data(f"/api/v1/savings/{saving_id_to_trigger_dialog}", data=update_data)
							if result:
								st.toast("Saving marked as matured!")
								# SỬA LỖI: Xóa cache TRƯỚC khi rerun
								st.cache_data.clear()
								st.rerun()  # Rerun để đóng dialog và cập nhật bảng
							else:
								st.error("Failed to update saving status.")

					with col_btn2:
						if st.button("Cancel", key=f"cancel_mat_{saving_id_to_trigger_dialog}", type="secondary"):
							# Chỉ cần rerun để đóng dialog
							st.rerun()

						# Gọi hàm dialog


				confirm_maturity_dialog(saving_to_edit_series)

			else:  # Không tìm thấy saving record
				st.error("Could not find the saving record to mark as matured. Please refresh.")


	else:  # df_display rỗng
		st.info("No savings to display based on current filter.")

if st.button("Refresh Savings Data"):
	st.cache_data.clear()
	st.rerun()


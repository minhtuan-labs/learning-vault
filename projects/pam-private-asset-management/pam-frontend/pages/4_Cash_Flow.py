import streamlit as st
import pandas as pd
from services import pam_backend_api as api
from datetime import datetime, date  # Ensure date is imported
from utils import auth
import math  # Import math
import time  # Import time for a small delay

# --- Cấu hình trang ---
st.set_page_config(
	page_title="My PAM | Cash Flow",
	page_icon="💰",
	layout="wide"
)

# Khởi tạo và kiểm tra xác thực
auth.initialize_session()
st.title("💰 Investment Cash Flow")

if not auth.is_authenticated():
	st.warning("Please login to access this page.")
	st.stop()


# --- Chức năng chính ---

@st.cache_data(ttl=30)  # Giảm TTL để cập nhật thường xuyên hơn
def load_transactions(asset_id):
	"""Tải lịch sử giao dịch của tài sản CASH."""
	if not asset_id: return None
	# Trả về list rỗng nếu API trả về None (lỗi) hoặc list rỗng
	result = api.get_data(f"/api/v1/assets/{asset_id}/transactions/")
	return result if result is not None else []


@st.cache_data(ttl=60)
def get_cash_asset_id():
	"""Tìm ID của tài sản CASH. Tự động tạo nếu chưa có."""
	all_assets = api.get_data("/api/v1/assets/")
	if all_assets is None:
		return None
	if all_assets:
		for asset in all_assets:
			if asset.get('asset_type') == 'cash':
				return asset.get('id')
	new_cash_asset = api.post_data("/api/v1/assets/", data={"name": "Investment Cash", "asset_type": "cash"})
	if new_cash_asset:
		st.toast("Auto-created 'Investment Cash' asset for you.")
		get_cash_asset_id.clear()
		return new_cash_asset.get('id')
	return None


cash_asset_id = get_cash_asset_id()

if not cash_asset_id:
	st.error("Could not find or create a CASH asset. Please check backend connection or refresh.")
	if not auth.is_authenticated():
		st.warning("Session might have expired. Please login again.")
	if st.button("Retry"):
		get_cash_asset_id.clear()
		st.rerun()
	st.stop()

# Tải dữ liệu giao dịch
transactions_data = load_transactions(cash_asset_id)

# --- HIỂN THỊ TÓM TẮT LÊN ĐẦU ---
st.header("Balance Summary")

current_balance = 0.0
# SỬA LỖI: Khởi tạo là DataFrame rỗng
balance_sheet_data = pd.DataFrame(columns=['transaction_type', 'Total Amount'])

# Chỉ xử lý nếu transactions_data không phải None VÀ không rỗng (là list có phần tử)
if transactions_data:  # Kiểm tra list không rỗng
	df_trans = pd.DataFrame(transactions_data)
	if not df_trans.empty:
		df_trans['transaction_date'] = pd.to_datetime(df_trans['transaction_date'], errors='coerce')
		df_trans['amount'] = pd.to_numeric(df_trans['amount'], errors='coerce').fillna(0)

		df_trans = df_trans.sort_values(by='transaction_date', ascending=False).reset_index(drop=True)

		if not df_trans.empty:
			df_trans['balance'] = df_trans['amount'].iloc[::-1].cumsum()[::-1]
			if not df_trans['balance'].empty and pd.notna(df_trans['balance'].iloc[0]):
				current_balance = df_trans['balance'].iloc[0]
			else:
				current_balance = df_trans['amount'].sum()

		balance_sheet = df_trans.groupby('transaction_type')['amount'].sum().reset_index()
		balance_sheet.rename(columns={'amount': 'Total Amount'}, inplace=True)
		balance_sheet_data = balance_sheet
elif transactions_data is None:  # Xử lý trường hợp API lỗi rõ ràng hơn
	st.warning("Could not load transaction data for summary.")

st.metric("Current Cash Balance", f"{current_balance:,.0f} VND")

# Hiển thị bảng tóm tắt (kiểm tra .empty đã đúng)
if not balance_sheet_data.empty:
	st.dataframe(
		balance_sheet_data,
		column_config={
			"transaction_type": st.column_config.TextColumn("Transaction Type"),
			"Total Amount": st.column_config.NumberColumn("Total Amount (VND)", format="%d")
		},
		hide_index=True,
		# SỬA WARNING: Xóa use_container_width
	)
# Không cần else ở đây nữa

st.divider()

# 1. FORM NHẬP LIỆU GIAO DỊCH TIỀN MẶT
with st.expander("Record a New Cash Transaction", expanded=False):
	with st.form("new_cash_transaction_form", clear_on_submit=True):
		col1, col2, col3 = st.columns(3)
		with col1:
			transaction_type = st.selectbox("Transaction Type", ("DEPOSIT", "WITHDRAWAL", "DIVIDEND_INCOME", "FEE"))
		with col2:
			amount = st.number_input("Amount (VND)", min_value=1, step=1000, format="%d")
		with col3:
			transaction_date = st.date_input("Transaction Date")

		description = st.text_input("Description (Optional)")
		submitted = st.form_submit_button("Record Transaction")

		if submitted:
			if not transaction_type:
				st.warning("Please select transaction type.")
			elif amount <= 0:
				st.warning("Amount must be greater than 0.")
			elif not transaction_date:
				st.warning("Please select transaction date.")
			else:
				final_amount = amount if transaction_type in ["DEPOSIT", "DIVIDEND_INCOME"] else -amount
				transaction_data = {
					"transaction_type": transaction_type.lower(),
					"transaction_date": transaction_date.isoformat(),
					"amount": float(final_amount),
					"description": description
				}
				with st.spinner("Recording transaction..."):
					result = api.post_data(f"/api/v1/assets/{cash_asset_id}/transactions/", data=transaction_data)
					if result:
						st.success(f"Successfully recorded transaction!")
						load_transactions.clear()
						st.rerun()

# 2. BẢNG HIỂN THỊ LỊCH SỬ GIAO DỊCH TIỀN MẶT
st.header("Detailed Transaction History")

# Xử lý trường hợp transactions_data là None hoặc rỗng
if transactions_data is None:
	if not auth.is_authenticated():
		st.warning("Session expired or invalid. Please login again.")
		if st.button("Go to Login Page"):
			st.switch_page("Home.py")
	else:
		st.error("Could not load transaction data.")
elif not transactions_data:
	st.info("You have no cash transactions yet. Record one in the form above.")
else:
	# Chỉ xử lý nếu có dữ liệu và df_trans tồn tại
	if 'df_trans' in locals() and not df_trans.empty:
		df_trans['transaction_date'] = pd.to_datetime(df_trans['transaction_date'], errors='coerce').dt.strftime(
			'%Y-%m-%d %H:%M:%S')

		st.dataframe(
			df_trans[['transaction_date', 'transaction_type', 'amount', 'balance', 'description']],
			column_config={
				"amount": st.column_config.NumberColumn("Amount (VND)", format="localized"),
				"balance": st.column_config.NumberColumn("Balance (VND)", format="localized"),
			},
			hide_index=True,
		)
	else:
		st.info("No transactions to display.")

if st.button("Refresh Cash Data"):
	load_transactions.clear()
	st.rerun()


import streamlit as st
import pandas as pd
from services import pam_backend_api as api
from datetime import datetime
from utils import auth

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
	return api.get_data(f"/api/v1/assets/{asset_id}/transactions/")


@st.cache_data(ttl=60)
def get_cash_asset_id():
	"""Tìm ID của tài sản CASH. Tự động tạo nếu chưa có."""
	all_assets = api.get_data("/api/v1/assets/")
	if all_assets:
		for asset in all_assets:
			if asset['asset_type'] == 'cash':
				return asset['id']
	new_cash_asset = api.post_data("/api/v1/assets/", data={"name": "Investment Cash", "asset_type": "cash"})
	if new_cash_asset:
		st.toast("Auto-created 'Investment Cash' asset for you.")
		get_cash_asset_id.clear()
		return new_cash_asset['id']
	return None


cash_asset_id = get_cash_asset_id()

if not cash_asset_id:
	st.error("Could not find or create a CASH asset. Please try refreshing the page.")
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

if transactions_data is not None and transactions_data:  # Kiểm tra transactions_data không rỗng
	df_trans = pd.DataFrame(transactions_data)
	if not df_trans.empty:  # Chỉ xử lý nếu DataFrame không rỗng
		df_trans['transaction_date'] = pd.to_datetime(df_trans['transaction_date'])
		df_trans = df_trans.sort_values(by='transaction_date', ascending=False).reset_index(drop=True)
		df_trans['balance'] = df_trans['amount'].iloc[::-1].cumsum()[::-1]
		current_balance = df_trans['balance'].iloc[0]

		# Tính toán bảng tóm tắt
		balance_sheet = df_trans.groupby('transaction_type')['amount'].sum().reset_index()
		balance_sheet.rename(columns={'amount': 'Total Amount'}, inplace=True)
		balance_sheet_data = balance_sheet

# Hiển thị số dư hiện tại
st.metric("Current Cash Balance", f"{current_balance:,.2f}")

# Hiển thị bảng tóm tắt (kiểm tra .empty đã đúng)
if not balance_sheet_data.empty:
	st.dataframe(
		balance_sheet_data,
		column_config={
			"transaction_type": st.column_config.TextColumn("Transaction Type"),
			"Total Amount": st.column_config.NumberColumn("Total Amount", format="%.2f")
		},
		hide_index=True,
		use_container_width=True
	)
else:
	# Chỉ thông báo nếu balance_sheet rỗng VÀ có giao dịch (trường hợp lạ)
	if transactions_data:
		st.info("No transaction types found for summary.")

st.divider()

# 1. FORM NHẬP LIỆU GIAO DỊCH TIỀN MẶT
with st.expander("Record a New Cash Transaction", expanded=False):
	with st.form("new_cash_transaction_form", clear_on_submit=True):
		col1, col2, col3 = st.columns(3)
		with col1:
			transaction_type = st.selectbox("Transaction Type", ("DEPOSIT", "WITHDRAWAL", "DIVIDEND_INCOME", "FEE"))
		with col2:
			amount = st.number_input("Amount", min_value=0.01, format="%.2f")
		with col3:
			transaction_date = st.date_input("Transaction Date")

		description = st.text_input("Description (Optional)")

		submitted = st.form_submit_button("Record Transaction")

		if submitted:
			if not all([transaction_type, amount]):
				st.warning("Please fill in all required fields.")
			else:
				final_amount = amount if transaction_type in ["DEPOSIT", "DIVIDEND_INCOME"] else -amount
				transaction_data = {
					"transaction_type": transaction_type.lower(),
					"transaction_date": transaction_date.isoformat(),
					"amount": final_amount,
					"description": description
				}
				with st.spinner("Recording transaction..."):
					result = api.post_data(f"/api/v1/assets/{cash_asset_id}/transactions/", data=transaction_data)
					if result:
						st.success(f"Successfully recorded transaction!")
						load_transactions.clear()
						get_cash_asset_id.clear()
						st.rerun()

# 2. BẢNG HIỂN THỊ LỊCH SỬ GIAO DỊCH TIỀN MẶT
st.header("Detailed Transaction History")

# Kiểm tra transactions_data một cách an toàn
if transactions_data is None:
	if cash_asset_id:  # Chỉ báo lỗi nếu đã có asset ID
		st.error("Could not load transaction data.")
elif not transactions_data:  # List rỗng
	st.info("You have no cash transactions yet. Record one in the form above.")
else:  # Có dữ liệu
	# Tái sử dụng df_trans đã tính toán ở trên (nếu có)
	if 'df_trans' in locals() and not df_trans.empty:
		df_trans['transaction_date'] = pd.to_datetime(df_trans['transaction_date']).dt.strftime('%Y-%m-%d %H:%M:%S')
		st.dataframe(
			df_trans[['transaction_date', 'transaction_type', 'amount', 'balance', 'description']],
			hide_index=True,
			use_container_width=True
		)
	else:  # Xử lý trường hợp transactions_data không rỗng nhưng df_trans lại rỗng (ít xảy ra)
		st.warning("No transactions to display after processing.")

if st.button("Refresh Cash Data"):
	load_transactions.clear()
	get_cash_asset_id.clear()
	st.rerun()


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

# Hàm để tìm ID của tài sản CASH, tự động tạo nếu chưa có
@st.cache_data(ttl=60)
def get_cash_asset_id():
	"""
	Tìm ID của tài sản CASH.
	Backend sẽ tự động tạo nếu nó không tồn tại khi có giao dịch đầu tiên,
	nhưng chúng ta cần ID của nó để ghi nhận giao dịch nạp/rút.
	"""
	all_assets = api.get_data("/api/v1/assets/")
	if all_assets:
		for asset in all_assets:
			if asset['asset_type'] == 'CASH':
				return asset['id']
	# Nếu không tìm thấy, tạo mới
	new_cash_asset = api.post_data("/api/v1/assets/", data={"name": "Investment Cash", "asset_type": "CASH"})
	if new_cash_asset:
		st.toast("Auto-created 'Investment Cash' asset for you.")
		return new_cash_asset['id']
	return None


cash_asset_id = get_cash_asset_id()

if not cash_asset_id:
	st.error("Could not find or create a CASH asset. Please try refreshing the page.")
	st.stop()

# 1. FORM NHẬP LIỆU GIAO DỊCH TIỀN MẶT
with st.expander("Record a New Cash Transaction", expanded=True):
	with st.form("new_cash_transaction_form", clear_on_submit=True):
		col1, col2, col3 = st.columns(3)
		with col1:
			# Chỉ cho phép người dùng nhập các loại giao dịch thủ công
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
				# Điều chỉnh giá trị amount dựa trên loại giao dịch
				final_amount = amount if transaction_type in ["DEPOSIT", "DIVIDEND_INCOME"] else -amount

				transaction_data = {
					"transaction_type": transaction_type,
					"transaction_date": transaction_date.isoformat(),
					"amount": final_amount,
					"description": description
				}

				with st.spinner("Recording transaction..."):
					result = api.post_data(f"/api/v1/assets/{cash_asset_id}/transactions/", data=transaction_data)
					if result:
						st.success(f"Successfully recorded transaction!")
						st.cache_data.clear()
						st.rerun()

# 2. BẢNG HIỂN THỊ LỊCH SỬ GIAO DỊCH TIỀN MẶT
st.divider()
st.header("Cash Transaction History")


@st.cache_data(ttl=30)
def load_transactions(asset_id):
	"""Tải lịch sử giao dịch của tài sản CASH."""
	return api.get_data(f"/api/v1/assets/{asset_id}/transactions/")


transactions_data = load_transactions(cash_asset_id)

if transactions_data is not None:
	if transactions_data:
		df = pd.DataFrame(transactions_data)

		# Sắp xếp theo ngày mới nhất lên đầu
		df['transaction_date'] = pd.to_datetime(df['transaction_date'])
		df = df.sort_values(by='transaction_date', ascending=False).reset_index(drop=True)

		# Tính toán số dư
		df['balance'] = df['amount'].iloc[::-1].cumsum()[::-1]

		df['transaction_date'] = df['transaction_date'].dt.strftime('%Y-%m-%d %H:%M:%S')

		# Hiển thị bảng
		st.dataframe(df[['transaction_date', 'transaction_type', 'amount', 'balance', 'description']],
					 use_container_width=True)

		# Hiển thị số dư cuối cùng
		st.metric("Current Cash Balance", f"{df['balance'].iloc[0]:,.2f}")

	else:
		st.info("You have no cash transactions yet. Record one above!")
else:
	st.error("Could not load transaction data.")

if st.button("Refresh Data"):
	st.cache_data.clear()
	st.rerun()


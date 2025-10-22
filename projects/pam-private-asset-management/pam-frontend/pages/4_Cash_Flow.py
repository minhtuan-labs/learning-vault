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

@st.cache_data(ttl=30)
def load_transactions(asset_id):
	if not asset_id: return None
	return api.get_data(f"/api/v1/assets/{asset_id}/transactions/")


@st.cache_data(ttl=60)
def get_cash_asset_id():
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
balance_sheet_data = []

if transactions_data is not None and transactions_data:
	df_trans = pd.DataFrame(transactions_data)
	df_trans['transaction_date'] = pd.to_datetime(df_trans['transaction_date'])
	df_trans = df_trans.sort_values(by='transaction_date', ascending=False).reset_index(drop=True)
	df_trans['balance'] = df_trans['amount'].iloc[::-1].cumsum()[::-1]
	current_balance = df_trans['balance'].iloc[0]

	# Tính toán bảng tóm tắt
	balance_sheet = df_trans.groupby('transaction_type')['amount'].sum().reset_index()
	balance_sheet.rename(columns={'amount': 'Total Amount'}, inplace=True)
	balance_sheet_data = balance_sheet

# Thêm dòng tổng cộng (có thể không cần thiết nếu đã có Current Balance)
# total_row = pd.DataFrame([{'transaction_type': 'NET CHANGE', 'Total Amount': balance_sheet['Total Amount'].sum()}])
# balance_sheet = pd.concat([balance_sheet, total_row], ignore_index=True)

# Hiển thị số dư hiện tại
st.metric("Current Cash Balance", f"{current_balance:,.2f}")

# Hiển thị bảng tóm tắt
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
	st.info("No transactions recorded yet to generate a summary.")

st.divider()

# 1. FORM NHẬP LIỆU GIAO DỊCH TIỀN MẶT
with st.expander("Record a New Cash Transaction", expanded=False):  # Mặc định thu gọn
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

if transactions_data is not None:
	if transactions_data:
		df_trans['transaction_date'] = df_trans['transaction_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
		st.dataframe(
			df_trans[['transaction_date', 'transaction_type', 'amount', 'balance', 'description']],
			hide_index=True,
			use_container_width=True
		)
	else:
		st.info("You have no cash transactions yet. Record one in the form above.")
else:
	if cash_asset_id:
		st.error("Could not load transaction data.")

if st.button("Refresh Cash Data"):
	load_transactions.clear()
	get_cash_asset_id.clear()
	st.rerun()


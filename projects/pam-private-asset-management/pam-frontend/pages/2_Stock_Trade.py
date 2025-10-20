import streamlit as st
import pandas as pd
from services import pam_backend_api as api
from datetime import datetime
from utils import auth

# --- Cấu hình trang ---
st.set_page_config(
	page_title="My PAM | Stock Trade",
	page_icon="📈",
	layout="centered"
)

# Khởi tạo session, khôi phục từ cookie nếu có
auth.initialize_session()

st.title("📈 Record a Stock Trade")

# --- Kiểm tra xác thực ---
if not auth.is_authenticated():
	st.warning("Please login to access this page.")
	st.stop()

# --- Form nhập liệu ---
with st.form("new_stock_trade_form", clear_on_submit=True):
	st.header("New Trade Details")

	col1, col2 = st.columns(2)
	with col1:
		ticker = st.text_input("Ticker Symbol", placeholder="E.g., HPG, FPT").upper()
		trade_type = st.selectbox("Trade Type", ("BUY", "SELL"))

	with col2:
		quantity = st.number_input("Quantity", min_value=0.01, step=0.01)
		price = st.number_input("Price per Share", min_value=0.0, step=100.0)
		fee = st.number_input("Fee", min_value=0.0, step=1000.0)

	trade_date = st.date_input("Trade Date")
	trade_time = st.time_input("Trade Time")
	notes = st.text_area("Notes (Optional)")

	submitted = st.form_submit_button("Record Trade")

	if submitted:
		if not all([ticker, trade_type, quantity, price]):
			st.warning("Please fill in all required fields.")
		else:
			# Kết hợp ngày và giờ
			trade_datetime = datetime.combine(trade_date, trade_time)

			# Chuẩn bị dữ liệu cho API
			trade_data = {
				"trade_type": trade_type.lower(),
				"trade_date": trade_datetime.isoformat(),
				"quantity": quantity,
				"price": price,
				"fee": fee,
				"notes": notes
			}

			# Tham số truy vấn bây giờ chỉ cần ticker
			params = {"ticker": ticker}

			with st.spinner("Recording trade..."):
				# Gọi đến API nghiệp vụ, backend sẽ tự lo phần còn lại
				result = api.post_data("/api/v1/trades/stock", data=trade_data, params=params)
				if result:
					st.success(f"Successfully recorded '{trade_type}' trade for {ticker}!")


import streamlit as st
import pandas as pd
from services import pam_backend_api as api
from datetime import datetime
from utils import auth

# --- Cấu hình trang ---
st.set_page_config(
	page_title="My PAM | Stock Trades",
	page_icon="📈",
	layout="wide"
)

# Khởi tạo và kiểm tra xác thực
auth.initialize_session()
st.title("📈 Stock Trading Log")

if not auth.is_authenticated():
	st.warning("Please login to access this page.")
	st.stop()

# --- Chức năng chính ---

# 1. FORM NHẬP LIỆU
with st.expander("Record a New Stock Trade", expanded=True):
	with st.form("new_stock_trade_form", clear_on_submit=True):
		col1, col2, col3 = st.columns(3)
		with col1:
			ticker = st.text_input("Ticker Symbol", placeholder="E.g., HPG, FPT").upper()
			trade_type = st.selectbox("Trade Type", ("BUY", "SELL"))
		with col2:
			quantity = st.number_input("Quantity", min_value=100, format="%d")
			price = st.number_input("Price per Share", min_value=0.0, format="%.2f")
		with col3:
			trade_date = st.date_input("Trade Date")
			fee = st.number_input("Fee", min_value=0.0, format="%.2f")

		notes = st.text_area("Notes (Optional)")

		submitted = st.form_submit_button("Record Trade")

		if submitted:
			if not all([ticker, trade_type, quantity, price]):
				st.warning("Please fill in all required fields.")
			else:
				trade_data = {
					"trade_type": trade_type.lower(),
					"trade_date": trade_date.isoformat(),
					"quantity": quantity,
					"price": price,
					"fee": fee,
					"notes": notes
				}
				params = {"ticker": ticker}

				with st.spinner("Recording trade..."):
					result = api.post_data("/api/v1/trades/stock", data=trade_data, params=params)
					if result:
						st.success(f"Successfully recorded '{trade_type}' trade for {ticker}!")
						st.cache_data.clear()
						st.rerun()

# 2. BẢNG HIỂN THỊ LỊCH SỬ GIAO DỊCH
st.divider()
st.header("Trade History")

col_left, col_right = st.columns([3, 1])
with col_right:
	show_hidden = st.toggle("Show hidden trades", value=False, key="show_hidden_toggle")


@st.cache_data(ttl=30)
def load_trades():
	# API này bây giờ đã trả về dữ liệu được sắp xếp sẵn
	return api.get_data("/api/v1/trades/stock")


trades_data = load_trades()

if trades_data is not None:
	if trades_data:
		df = pd.DataFrame(trades_data)
		df['trade_date'] = pd.to_datetime(df['trade_date']).dt.date
		df['total_value'] = df['quantity'] * df['price']

		# SỬA ĐỔI: Không cần sắp xếp ở frontend nữa, vì backend đã làm

		# Lọc dữ liệu dựa trên toggle
		if not show_hidden:
			df_display = df[df['is_hidden'] == False].copy()
		else:
			df_display = df.copy()

		st.session_state['df_to_display'] = df_display.copy()

		column_order = [
			"ticker", "trade_date", "trade_type", "quantity", "price",
			"total_value", "fee", "notes", "is_hidden"
		]

		df_display_processed = df_display.reindex(columns=column_order + ['id', 'portfolio_id', 'created_at'])

		edited_df = st.data_editor(
			df_display_processed,
			column_config={
				"ticker": st.column_config.TextColumn("Ticker", width="small"),
				"trade_date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
				"trade_type": st.column_config.TextColumn("Type", width="small"),
				"quantity": st.column_config.NumberColumn(format="%.2f"),
				"price": st.column_config.NumberColumn("Price", format="%.2f"),
				"total_value": st.column_config.NumberColumn("Total Value", format="%.2f"),
				"is_hidden": st.column_config.CheckboxColumn("Hide", default=False),
				"id": None,
				"portfolio_id": None,
				"created_at": None,  # Ẩn cột created_at khỏi giao diện
			},
			disabled=df_display_processed.columns.drop("is_hidden"),
			hide_index=True,
			use_container_width=True,
			key="trades_editor"
		)

		df_before_edit = st.session_state.get('df_to_display')
		if df_before_edit is not None and not df_before_edit.equals(edited_df):
			changed_mask = (df_before_edit['is_hidden'] != edited_df['is_hidden'])
			changed_rows = edited_df[changed_mask]

			with st.spinner("Updating visibility..."):
				for _, row in changed_rows.iterrows():
					trade_id = row['id']
					update_data = {"is_hidden": bool(row["is_hidden"])}
					api.patch_data(f"/api/v1/stock-trades/{trade_id}", data=update_data)

			st.toast("Visibility updated!")
			st.cache_data.clear()

	else:
		st.info("You have no stock trades yet. Record one above!")
else:
	st.error("Could not load trade data.")

if st.button("Refresh Data"):
	st.cache_data.clear()
	st.rerun()


import streamlit as st
import pandas as pd
from services import pam_backend_api as api
from datetime import datetime
from utils import auth
import math

# --- Cấu hình trang ---
st.set_page_config(
	page_title="My PAM | Stock Trades",
	page_icon="📈",
	layout="wide"
)


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
			quantity = st.number_input("Quantity", min_value=1, step=10, format="%d", value=100)
			price_input = st.number_input(
				"Price per Share ('000 VND)", min_value=0.0, format="%.2f", step=0.05,
				help="Enter price in thousands (e.g., 30.15 for 30,150 VND)"
			)
		with col3:
			trade_date = st.date_input("Trade Date")
			fee_input = st.number_input("Fee (VND)", min_value=0, step=100, format="%d")

		notes = st.text_area("Notes (Optional)")
		submitted = st.form_submit_button("Record Trade")

		if submitted:
			if not all([ticker, trade_type, quantity, price_input]):
				st.warning("Please fill in all required fields.")
			else:
				actual_price = price_input * 1000
				trade_data = {
					"trade_type": trade_type.lower(), "trade_date": trade_date.isoformat(),
					"quantity": float(quantity),
					"price": actual_price,
					"fee": float(fee_input), "notes": notes
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
	def clear_cache_on_toggle():
		if 'show_hidden_toggle_prev' not in st.session_state or st.session_state.show_hidden_toggle != st.session_state.show_hidden_toggle_prev:
			st.cache_data.clear()
		st.session_state.show_hidden_toggle_prev = st.session_state.show_hidden_toggle
	show_hidden = st.toggle(
		"Show hidden trades", value=st.session_state.get('show_hidden_toggle_prev', False),
		key="show_hidden_toggle", on_change=clear_cache_on_toggle
	)

@st.cache_data(ttl=30)
def load_trades():
	return api.get_data("/api/v1/trades/stock")


trades_data = load_trades()

if 'update_processed' not in st.session_state:
	st.session_state.update_processed = False

if trades_data is not None:
	if trades_data:
		df_all = pd.DataFrame(trades_data)
		# --- SỬA ĐỔI: Chỉ chuyển đổi kiểu dữ liệu, không chia 1000 ---
		numeric_cols = ['quantity', 'price', 'fee']
		for col in numeric_cols:
			df_all[col] = pd.to_numeric(df_all[col], errors='coerce').fillna(0)

		df_all['trade_date'] = pd.to_datetime(df_all['trade_date'], errors='coerce')

		# Tính toán tổng giá trị thực tế (kiểu số)
		df_all['total_value_vnd'] = (df_all['quantity'] * df_all['price']) + df_all['fee']
		# Không cần 'price_display_000' nữa

		df_all = df_all.sort_values(by='created_at', ascending=False).reset_index(drop=True)

		df_to_display = df_all[df_all['is_hidden'] == False].copy() if not show_hidden else df_all.copy()

		if 'df_stock_before_edit' not in st.session_state or st.session_state.update_processed:
			st.session_state['df_stock_before_edit'] = df_to_display.copy()
			st.session_state.update_processed = False

		# SỬA ĐỔI: Thứ tự cột hiển thị
		column_order = [
			"ticker", "trade_date", "trade_type", "quantity", "price",  # Hiển thị 'price' gốc
			"total_value_vnd", "fee", "notes", "is_hidden"
		]
		# Các cột ẩn cần thiết để xử lý logic
		hidden_cols = ['id', 'portfolio_id', 'created_at']

		# Đảm bảo các cột tồn tại trước khi reindex
		for col in column_order + hidden_cols:
			if col not in df_to_display.columns:
				df_to_display[col] = None

		df_display_processed = df_to_display.reindex(columns=column_order + hidden_cols)

		edited_df = st.data_editor(
			df_display_processed,
			column_config={
				"ticker": st.column_config.TextColumn("Ticker", width="small"),
				"trade_date": st.column_config.DateColumn("Date", format="YYYY-MM-DD", width="small"),
				"trade_type": st.column_config.TextColumn("Type", width="small"),
				"quantity": st.column_config.NumberColumn("Quantity", format="localized"),
				"price": st.column_config.NumberColumn("Price (VND)", format="localized"),
				"total_value_vnd": st.column_config.NumberColumn("Total (VND)", format="localized"),
				"fee": st.column_config.NumberColumn("Fee (VND)", format="localized"),
				"notes": st.column_config.TextColumn("Notes"),
				"is_hidden": st.column_config.CheckboxColumn("Hide", default=False),
				"id": None, "portfolio_id": None, "created_at": None,
			},
			column_order=column_order,
			disabled=df_display_processed.columns.drop("is_hidden"),
			hide_index=True,
			key="trades_editor"
		)

		df_before_edit = st.session_state.get('df_stock_before_edit')

		# --- Logic xử lý ẩn/hiện không đổi ---
		if df_before_edit is not None and not st.session_state.update_processed:
			try:
				if len(df_before_edit) == len(edited_df):
					edited_df_reindexed = edited_df.set_index(df_before_edit.index)
					changed_mask = df_before_edit['is_hidden'] != edited_df_reindexed['is_hidden']

					if changed_mask.any():
						rows_to_update = df_before_edit[changed_mask]

						if not rows_to_update.empty:
							with st.spinner("Updating visibility..."):
								for index, row in rows_to_update.iterrows():
									try:
										new_hidden_status = edited_df_reindexed.loc[index, 'is_hidden']
										trade_id = row['id']
										update_data = {"is_hidden": bool(new_hidden_status)}
										api.patch_data(f"/api/v1/stock-trades/{trade_id}", data=update_data)
									except KeyError:
										st.warning(
											f"Could not find row with index {index} after edit. Skipping update.")
									except Exception as e:
										st.error(f"Error updating visibility for trade ID {row.get('id', 'N/A')}: {e}")

							st.toast("Visibility updated!")
							st.cache_data.clear()
							st.session_state.update_processed = True
							st.rerun()
				else:
					st.warning("Dataframe length mismatch after edit. Cannot compare changes. Please refresh the trade history.")
			except Exception as e:
				st.error(f"Error comparing dataframes: {e}")
	else: # Not trades_data
		st.info("You have no stock trades yet. Record one above!")
else: # trades_data is None
	if not auth.is_authenticated():
		st.warning("Session expired or invalid. Please login again.")
		if st.button("Go to Login Page"):
			st.switch_page("Home.py")
	else:
		st.error("Could not load trade data. An error occurred.")

if st.button("Refresh Data"):
	st.cache_data.clear()
	st.rerun()


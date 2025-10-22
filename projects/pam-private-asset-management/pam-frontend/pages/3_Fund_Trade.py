import streamlit as st
import pandas as pd
from services import pam_backend_api as api
from datetime import datetime
from utils import auth

# --- Cấu hình trang ---
st.set_page_config(
	page_title="My PAM | Fund Trades",
	page_icon="💸",
	layout="wide"
)

# Khởi tạo và kiểm tra xác thực
auth.initialize_session()
st.title("💸 Fund Trading Log")

if not auth.is_authenticated():
	st.warning("Please login to access this page.")
	st.stop()

# --- Chức năng chính ---

# 1. FORM NHẬP LIỆU
with st.expander("Record a New Fund Trade", expanded=True):
	with st.form("new_fund_trade_form", clear_on_submit=True):
		col1, col2, col3 = st.columns(3)
		with col1:
			ticker = st.text_input("Fund Ticker Symbol", placeholder="E.g., E1VFVN30").upper()
			trade_type = st.selectbox("Trade Type", ("BUY", "SELL"))
		with col2:
			quantity = st.number_input("Quantity", min_value=0.0, format="%.2f")
			price = st.number_input("Price per Unit", min_value=0.0, format="%.2f")
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
					# Gọi đến API nghiệp vụ của Fund
					result = api.post_data("/api/v1/trades/fund", data=trade_data, params=params)
					if result:
						st.success(f"Successfully recorded '{trade_type}' trade for {ticker}!")
						st.cache_data.clear()
						st.rerun()

# 2. BẢNG HIỂN THỊ LỊCH SỬ GIAO DỊCH
st.divider()
st.header("Trade History")

col_left, col_right = st.columns([3, 1])
with col_right:
	show_hidden = st.toggle("Show hidden trades", value=False, key="show_hidden_fund_toggle")


@st.cache_data(ttl=30)
def load_trades():
	return api.get_data("/api/v1/trades/fund")

trades_data = load_trades()

if 'fund_update_processed' not in st.session_state:
    st.session_state.fund_update_processed = False

if trades_data is not None:
	if trades_data:
		df = pd.DataFrame(trades_data)
		df['trade_date'] = pd.to_datetime(df['trade_date']).dt.date
		df['total_value'] = df['quantity'] * df['price']

		df = df.sort_values(by='created_at', ascending=False).reset_index(drop=True)

		df_to_display = df[df['is_hidden'] == False].copy() if not show_hidden else df.copy()

		st.session_state['df_fund_before_edit'] = df_to_display.copy()

		column_order = [
			"ticker", "trade_date", "trade_type", "quantity", "price",
			"total_value", "fee", "notes", "is_hidden"
		]

		df_display_processed = df_to_display.reindex(columns=column_order + ['id', 'portfolio_id', 'created_at'])

		edited_df = st.data_editor(
			df_display_processed,
			column_config={
				"ticker": st.column_config.TextColumn("Ticker", width="small"),
				"trade_date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
				"trade_type": st.column_config.TextColumn("Type", width="small"),
				"quantity": st.column_config.NumberColumn(format="%.4f"),
				"price": st.column_config.NumberColumn("Price", format="%.2f"),
				"total_value": st.column_config.NumberColumn("Total Value", format="%.2f"),
				"is_hidden": st.column_config.CheckboxColumn("Hide", default=False),
				"id": None, "portfolio_id": None, "created_at": None
			},
			disabled=df_display_processed.columns.drop("is_hidden"),
			hide_index=True,
			use_container_width=True,
			key="fund_trades_editor"
		)

		df_before_edit = st.session_state.get('df_fund_before_edit')
		if df_before_edit is not None and not df_before_edit.reset_index(drop=True).equals(
				edited_df.reset_index(drop=True)) and not st.session_state.fund_update_processed:
			changed_mask = (df_before_edit['is_hidden'].values != edited_df['is_hidden'].values)
			rows_to_update = df_before_edit[changed_mask]
			if not rows_to_update.empty:
				with st.spinner("Updating visibility..."):
					for index, row in rows_to_update.iterrows():
						try:
							original_index = edited_df[edited_df['id'] == row['id']].index[0]
							trade_id = row['id']
							new_hidden_status = edited_df.loc[original_index, "is_hidden"]
							update_data = {"is_hidden": bool(new_hidden_status)}
							api.patch_data(f"/api/v1/fund-trades/{trade_id}", data=update_data)
						except IndexError:
							st.warning(f"Could not find matching row for ID {row['id']} after edit. Skipping update.")
				st.toast("Visibility updated!")
				st.cache_data.clear()
				st.session_state.fund_update_processed = True
				st.rerun()
	else:
		st.info("You have no fund trades yet. Record one above!")
else:
	st.error("Could not load fund trade data.")

if st.button("Refresh Data"):
	st.cache_data.clear()
	st.rerun()


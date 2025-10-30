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

# --- Helper functions ---
@st.cache_data(ttl=30)
def load_stock_trades():
	"""Load stock trades from API"""
	return api.get_data("/api/v1/trades/stock")

@st.cache_data(ttl=30)
def load_stock_portfolios():
	"""Load stock portfolios to get current holdings"""
	try:
		# Lấy tất cả assets
		assets = api.get_data("/api/v1/assets/")
		if not assets:
			return []
		
		# Tìm stock asset
		stock_asset = None
		for asset in assets:
			if asset.get('asset_type') == 'stocks':
				stock_asset = asset
				break
		
		if not stock_asset:
			return []
		
		# Lấy stock portfolios
		portfolios = api.get_data(f"/api/v1/assets/{stock_asset['id']}/stock-portfolios/")
		return portfolios if portfolios else []
	except Exception:
		return []

def calculate_stock_holdings():
	"""Calculate current stock holdings from trades"""
	trades = load_stock_trades()
	if not trades:
		return {}
	
	holdings = {}
	for trade in trades:
		ticker = trade.get('ticker', '')
		quantity = float(trade.get('quantity', 0))
		trade_type = trade.get('trade_type', '')
		
		if ticker not in holdings:
			holdings[ticker] = {'quantity': 0, 'total_cost': 0}
		
		if trade_type == 'buy':
			holdings[ticker]['quantity'] += quantity
			holdings[ticker]['total_cost'] += quantity * float(trade.get('price', 0))
		elif trade_type == 'sell':
			holdings[ticker]['quantity'] -= quantity
			holdings[ticker]['total_cost'] -= quantity * float(trade.get('price', 0))
	
	# Filter out zero or negative holdings
	return {k: v for k, v in holdings.items() if v['quantity'] > 0}

# --- 1. STOCK LIST (Current Holdings) ---
st.header("📊 Current Stock Holdings")

# Reset any stuck session states on page load
# Always reset sell dialog states when page loads
for key in list(st.session_state.keys()):
	if key.startswith('show_sell_'):
		del st.session_state[key]

holdings = calculate_stock_holdings()

if holdings:
	# Tạo DataFrame cho holdings
	holdings_data = []
	for ticker, data in holdings.items():
		holdings_data.append({
			'Ticker': ticker,
			'Quantity': f"{data['quantity']:,.0f}",
			'Total Cost': f"{data['total_cost']:,.0f} VND",
			'Avg Price': f"{data['total_cost']/data['quantity']:,.0f} VND" if data['quantity'] > 0 else "0 VND"
		})
	
	holdings_df = pd.DataFrame(holdings_data)
	
	# Hiển thị bảng với nút Sell
	for idx, row in holdings_df.iterrows():
		col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 3, 2])
		
		with col1:
			st.write(f"**{row['Ticker']}**")
		with col2:
			st.write(row['Quantity'])
		with col3:
			st.write(row['Total Cost'])
		with col4:
			st.write(row['Avg Price'])
		with col5:
			if st.button(f"Sell", key=f"sell_{row['Ticker']}", type="secondary"):
				st.session_state[f"show_sell_{row['Ticker']}"] = True
	
	# Sell dialog forms using st.dialog
	for ticker in holdings.keys():
		if st.session_state.get(f"show_sell_{ticker}", False):
			@st.dialog(f"Sell {ticker}")
			def sell_stock_dialog(ticker_symbol=ticker):
				# Current holding info
				current_qty = holdings[ticker_symbol]['quantity']
				avg_price = holdings[ticker_symbol]['total_cost'] / current_qty if current_qty > 0 else 0
				st.info(f"**Current Holdings:** {current_qty:,.0f} shares | **Avg Price:** {avg_price:,.0f} VND")
				
				with st.form(f"sell_form_{ticker_symbol}", clear_on_submit=True, border=False):
					col1, col2 = st.columns(2)
					with col1:
						sell_quantity = st.number_input(
							"Quantity to Sell", 
							min_value=1, 
							max_value=int(current_qty),
							step=1,
							key=f"qty_{ticker_symbol}"
						)
					with col2:
						sell_price = st.number_input(
							"Price per Share ('000 VND)", 
							min_value=0.0, 
							step=0.01,
							format="%.2f",
							help="E.g., 123.24 = 123,240 VND",
							key=f"price_{ticker_symbol}"
						)
					
					sell_fee = st.number_input("Fee (VND)", min_value=0, step=100, format="%d", key=f"fee_{ticker_symbol}")
					sell_notes = st.text_area("Notes (Optional)", key=f"notes_{ticker_symbol}")
					
					# Calculate and show estimated proceeds
					if sell_quantity > 0 and sell_price > 0:
						total_value = sell_quantity * sell_price * 1000  # Convert to actual VND
						net_proceeds = total_value - sell_fee
						st.write(f"**Estimated Proceeds:** {net_proceeds:,.0f} VND")
					
					col_submit, col_cancel = st.columns(2)
					with col_submit:
						if st.form_submit_button("✅ Confirm Sell", type="primary"):
							if sell_quantity > 0 and sell_price > 0:
								actual_price = sell_price * 1000  # Convert to actual VND
								trade_data = {
									"trade_type": "sell",
									"trade_date": datetime.now().date().isoformat(),
									"quantity": float(sell_quantity),
									"price": actual_price,
									"fee": float(sell_fee),
									"notes": sell_notes
								}
								params = {"ticker": ticker_symbol}
								
								with st.spinner("Recording sell trade..."):
									result = api.post_data("/api/v1/trades/stock", data=trade_data, params=params)
									if result:
										st.success(f"✅ Successfully sold {sell_quantity} shares of {ticker_symbol}!")
										st.cache_data.clear()
										# Reset session state
										st.session_state[f"show_sell_{ticker_symbol}"] = False
										st.rerun()
							else:
								st.warning("Please enter valid quantity and price.")
					
					with col_cancel:
						if st.form_submit_button("❌ Cancel"):
							st.session_state[f"show_sell_{ticker_symbol}"] = False
							st.rerun()
			
			sell_stock_dialog(ticker)
else:
	st.info("No stock holdings found. Start by buying some stocks!")

# --- 2. NEW TRADE FORM ---
st.divider()
st.header("➕ Record New Stock Trade")

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

# --- 3. TRADE HISTORY ---
st.divider()
st.header("📋 Trade History")

# Pagination controls
if 'stock_page' not in st.session_state:
	st.session_state.stock_page = 1

trades_data = load_stock_trades()

if trades_data is not None:
	if trades_data:
		df_all = pd.DataFrame(trades_data)
		# Convert data types
		numeric_cols = ['quantity', 'price', 'fee']
		for col in numeric_cols:
			df_all[col] = pd.to_numeric(df_all[col], errors='coerce').fillna(0)

		df_all['trade_date'] = pd.to_datetime(df_all['trade_date'], errors='coerce')

		# Calculate total value
		df_all['total_value'] = df_all['quantity'] * df_all['price']
		df_all['net_amount'] = df_all['total_value'] + df_all['fee']
		
		# Sort by trade ID descending (newest first)
		df_all = df_all.sort_values('id', ascending=False)
		
		# Pagination
		items_per_page = 20
		total_items = len(df_all)
		total_pages = math.ceil(total_items / items_per_page)
		
		col_left, col_right = st.columns([3, 1])
		with col_right:
			show_hidden = st.toggle("Show hidden trades", value=False)
		
		# Filter hidden trades
		if not show_hidden:
			df_all = df_all[df_all.get('is_hidden', False) == False]
		
		# Apply pagination
		start_idx = (st.session_state.stock_page - 1) * items_per_page
		end_idx = start_idx + items_per_page
		df_page = df_all.iloc[start_idx:end_idx]
		
		# Display current page info
		st.write(f"Showing {start_idx + 1}-{min(end_idx, len(df_all))} of {len(df_all)} trades")
		
		# Pagination controls
		col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
		with col1:
			if st.button("⏮️ First", disabled=st.session_state.stock_page == 1):
				st.session_state.stock_page = 1
				st.rerun()
		with col2:
			if st.button("⬅️ Prev", disabled=st.session_state.stock_page == 1):
				st.session_state.stock_page -= 1
				st.rerun()
		with col3:
			st.write(f"Page {st.session_state.stock_page} of {total_pages}")
		with col4:
			if st.button("Next ➡️", disabled=st.session_state.stock_page == total_pages):
				st.session_state.stock_page += 1
				st.rerun()
		with col5:
			if st.button("Last ⏭️", disabled=st.session_state.stock_page == total_pages):
				st.session_state.stock_page = total_pages
				st.rerun()
		
		# Display table
		if not df_page.empty:
			# Format for display
			display_df = df_page.copy()
			display_df['price'] = display_df['price'] / 1000  # Convert back to thousands
			#display_df['total_value'] = display_df['total_value'] / 1000
			#display_df['net_amount'] = display_df['net_amount'] / 1000
			
			# Format columns
			display_df['price'] = display_df['price'].apply(lambda x: f"{x:.2f}")
			display_df['total_value'] = display_df['total_value'].apply(lambda x: f"{x:,.0f}")
			display_df['net_amount'] = display_df['net_amount'].apply(lambda x: f"{x:,.0f}")
			display_df['fee'] = display_df['fee'].apply(lambda x: f"{x:,.0f}")
			display_df['quantity'] = display_df['quantity'].apply(lambda x: f"{x:,.0f}")
			
			# Select columns to display (exclude ID column)
			columns_to_show = ['ticker', 'trade_type', 'trade_date', 'quantity', 'price', 'fee', 'total_value', 'net_amount', 'notes']
			display_df = display_df[columns_to_show]
			
			# Rename columns
			display_df.columns = ['Ticker', 'Type', 'Date', 'Quantity', 'Price (K)', 'Fee', 'Total Value', 'Net Amount', 'Notes']
			
			st.dataframe(
				display_df, 
				use_container_width=True,
				column_config={
					"Quantity": st.column_config.NumberColumn("Quantity", format="localized"),
					"Price (K)": st.column_config.NumberColumn("Price (K)", format="%.2f"),
					"Fee": st.column_config.NumberColumn("Fee", format="localized"),
					"Total Value": st.column_config.NumberColumn("Total Value", format="localized"),
					"Net Amount": st.column_config.NumberColumn("Net Amount", format="localized")
				}
			)
		else:
			st.info("No trades found for this page.")
	else:
		st.info("No stock trades recorded yet.")
else:
	st.error("Failed to load trade data. Please try again.")

# --- Footer ---
st.markdown("---")
st.markdown("*Stock Trading Log - Last updated: " + datetime.now().strftime("%d/%m/%Y %H:%M") + "*")
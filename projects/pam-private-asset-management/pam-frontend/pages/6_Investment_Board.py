import streamlit as st
import pandas as pd
import requests
from utils import auth
from services import pam_backend_api as api
from datetime import datetime

# --- Page config ---
st.set_page_config(
	page_title="My PAM | Investment Board",
	page_icon="📋",
	layout="wide"
)

# --- Session / Auth ---
auth.initialize_session()

if not auth.is_authenticated():
	st.warning("Please login to access this page.")
	st.stop()

st.title("📋 Investment Board")

# --- Helpers ---
@st.cache_data(ttl=60)
def get_realtime_price(ticker: str) -> float | None:
	"""Fetch realtime price via Yahoo Finance. Assumes VN tickers; tries .VN suffix."""
	if not ticker:
		return None
	candidates = [f"{ticker}.VN", f"{ticker}.HM", f"{ticker}.HN", ticker]
	for symbol in candidates:
		try:
			url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
			r = requests.get(url, timeout=6)
			r.raise_for_status()
			data = r.json()
			result = data.get("quoteResponse", {}).get("result", [])
			if result and "regularMarketPrice" in result[0] and result[0]["regularMarketPrice"] is not None:
				return float(result[0]["regularMarketPrice"]) * 1000.0  # về VND (nghìn -> VND)
		except Exception:
			continue
	return None

@st.cache_data(ttl=120)
def load_stock_trades() -> list[dict]:
	trades = api.get_data("/api/v1/trades/stock")
	return trades if trades else []


def aggregate_holdings(trades: list[dict]) -> pd.DataFrame:
	"""Aggregate trades into current holdings per ticker."""
	holdings: dict[str, dict] = {}
	for tr in trades:
		ticker = tr.get("ticker")
		qty = float(tr.get("quantity", 0) or 0)
		price = float(tr.get("price", 0) or 0)
		fee = float(tr.get("fee", 0) or 0)
		if not ticker:
			continue
		pos = holdings.setdefault(ticker, {"ticker": ticker, "quantity": 0.0, "total_cost": 0.0})
		if tr.get("trade_type") == "buy":
			pos["quantity"] += qty
			pos["total_cost"] += qty * price + fee
		elif tr.get("trade_type") == "sell":
			pos["quantity"] -= qty
			# giảm cost tỉ lệ theo giá vốn (giữ simple)
			if pos["quantity"] > 0:
				avg_cost = pos["total_cost"] / (pos["quantity"] + qty)
				pos["total_cost"] -= avg_cost * qty
			else:
				pos["total_cost"] = 0.0
	# build df
	rows = []
	for p in holdings.values():
		if p["quantity"] <= 0:
			continue
		avg_cost = p["total_cost"] / p["quantity"] if p["quantity"] else 0.0
		rows.append({
			"Ticker": p["ticker"],
			"Quantity": round(p["quantity"], 0),
			"Avg Cost": avg_cost,
		})
	return pd.DataFrame(rows)

# --- Helper functions for API ---
@st.cache_data(ttl=300)
def get_portfolio_by_ticker(ticker: str):
	"""Get stock portfolio by ticker from API"""
	try:
		result = api.get_data(f"/api/v1/stock-portfolios/by-ticker/{ticker}")
		return result
	except:
		return None


@st.cache_data(ttl=60)
def load_watchlist():
	"""Load watchlist from API"""
	result = api.get_data("/api/v1/watchlists/")
	return result if result else []

# --- Holdings table ---
st.subheader("Holdings Overview")
trades = load_stock_trades()
holdings_df = aggregate_holdings(trades)

if holdings_df.empty:
	st.info("No stock holdings found.")
else:
	# enrich with current price, SL/TP, và các chỉ số
	cur_prices = []
	sl_vals = []
	tp_vals = []
	current_values = []
	pnl_vals = []
	pnl_pcts = []
	trends = []
	notify_vals = []
	portfolio_ids = []  # Lưu portfolio_id để update sau
	
	for _, row in holdings_df.iterrows():
		ticker = row["Ticker"]
		qty = row["Quantity"]
		avg_cost = row["Avg Cost"]  # Giá trị thực tế trong VND
		price = get_realtime_price(ticker) or 0.0  # Giá trị thực tế trong VND
		
		# Hiển thị giá per share chia 1000 (với 2 số thập phân)
		cur_prices.append(price / 1000.0 if price > 0 else 0.0)
		
		# Tính các chỉ số
		current_value = qty * price if price > 0 else 0.0
		total_cost = qty * avg_cost
		pnl = current_value - total_cost
		pnl_pct = ((price - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0.0
		
		current_values.append(round(current_value, 0))  # Làm tròn thành integer
		pnl_vals.append(round(pnl, 0))  # Làm tròn thành integer
		pnl_pcts.append(pnl_pct)
		
		# Trend với mũi tên và % (1 chữ số thập phân)
		if pnl_pct > 0:
			trends.append(f"🔼 +{pnl_pct:.1f}%")
		elif pnl_pct < 0:
			trends.append(f"🔽 {pnl_pct:.1f}%")
		else:
			trends.append("➡️ 0.0%")
		
		# Lấy Stop Loss / Target Price từ API
		portfolio = get_portfolio_by_ticker(ticker)
		portfolio_id = portfolio.get("id") if portfolio else None
		portfolio_ids.append(portfolio_id)
		
		stop_loss = portfolio.get("stop_loss_price") if portfolio else None
		target_price = portfolio.get("target_price") if portfolio else None
		
		# Hiển thị chia 1000
		sl_vals.append((stop_loss / 1000.0) if stop_loss and stop_loss > 0 else 0.0)
		tp_vals.append((target_price / 1000.0) if target_price and target_price > 0 else 0.0)
		
		# Notification (tạm thời lấy từ portfolio notes hoặc có thể thêm field riêng sau)
		notify_vals.append(False)  # TODO: Thêm notify field vào StockPortfolio model nếu cần
	
	enriched = holdings_df.copy()
	# Avg Cost hiển thị chia 1000
	enriched["Avg Cost"] = enriched["Avg Cost"].apply(lambda x: x / 1000.0 if x > 0 else 0.0)
	enriched["Current Price"] = cur_prices
	enriched["Current Value"] = current_values
	enriched["P&L"] = pnl_vals
	enriched["P&L %"] = pnl_pcts
	enriched["Trend"] = trends
	enriched["Stop Loss"] = sl_vals
	enriched["Target Price"] = tp_vals
	enriched["Notify"] = notify_vals
	enriched["_portfolio_id"] = portfolio_ids  # Hidden column để lưu portfolio_id
	
	edited = st.data_editor(
		enriched,
		use_container_width=True,
		key="ib_holdings_editor",
		column_config={
			"Quantity": st.column_config.NumberColumn("Quantity", format="%d"),
			"Avg Cost": st.column_config.NumberColumn("Avg Cost (K)", format="%.2f"),
			"Current Price": st.column_config.NumberColumn("Current Price (K)", format="%.2f"),
			"Current Value": st.column_config.NumberColumn("Current Value", format="localized"),
			"P&L": st.column_config.NumberColumn("P&L", format="localized"),
			"P&L %": st.column_config.NumberColumn("P&L %", format="%.1f%%"),
			"Trend": st.column_config.TextColumn("Trend"),
			"Stop Loss": st.column_config.NumberColumn("Stop Loss (K)", format="%.2f"),
			"Target Price": st.column_config.NumberColumn("Target Price (K)", format="%.2f"),
			"Notify": st.column_config.CheckboxColumn("Notify"),
			"_portfolio_id": None,  # Ẩn cột này
		},
		disabled=["Ticker", "Quantity", "Avg Cost", "Current Price", "Current Value", "P&L", "P&L %", "Trend", "_portfolio_id"],
		hide_index=True,
		column_order=["Ticker", "Quantity", "Avg Cost", "Current Price", "Current Value", "P&L", "P&L %", "Trend", "Stop Loss", "Target Price", "Notify"],
	)
	
	if st.button("💾 Save Settings", type="primary"):
		success_count = 0
		error_count = 0
		for _, r in edited.iterrows():
			portfolio_id = r.get("_portfolio_id")
			if not portfolio_id:
				error_count += 1
				continue
			
			# Nhân lại với 1000 để lưu giá trị thực tế
			sl_val = float(r["Stop Loss"] or 0.0) * 1000.0
			tp_val = float(r["Target Price"] or 0.0) * 1000.0
			
			update_data = {}
			if sl_val > 0:
				update_data["stop_loss_price"] = sl_val
			if tp_val > 0:
				update_data["target_price"] = tp_val
			
			if update_data:
				result = api.patch_data(f"/api/v1/stock-portfolios/{int(portfolio_id)}", update_data)
				if result:
					success_count += 1
					# Clear cache để reload
					get_portfolio_by_ticker.clear()
				else:
					error_count += 1
		
		if success_count > 0:
			st.success(f"Saved {success_count} portfolio setting(s).")
		if error_count > 0:
			st.warning(f"Failed to save {error_count} portfolio setting(s).")
		if success_count > 0:
			st.rerun()

st.divider()

# --- Watchlist ---
st.subheader("Watchlist")
with st.form("watchlist_add_form", clear_on_submit=True):
	c1, c2, c3 = st.columns([2, 2, 1])
	with c1:
		wl_ticker = st.text_input("Ticker to watch")
	with c2:
		wl_buy = st.number_input("Desired Buy Price (VND)", min_value=0, step=1000, format="%d")
	with c3:
		sub = st.form_submit_button("Add")
	if sub and wl_ticker:
		ticker_upper = wl_ticker.upper()
		# Tạo watchlist qua API
		watchlist_data = {
			"ticker": ticker_upper,
			"buy_price": float(wl_buy),
			"notify_enabled": False
		}
		result = api.post_data("/api/v1/watchlists/", watchlist_data)
		if result:
			st.success("Added to watchlist.")
			load_watchlist.clear()  # Clear cache
			st.rerun()
		else:
			st.warning(f"Failed to add {ticker_upper} to watchlist. It may already exist.")

# Load watchlist từ API
watchlist_data = load_watchlist()
wl_df = pd.DataFrame(watchlist_data) if watchlist_data else pd.DataFrame(columns=["id", "ticker", "buy_price", "notify_enabled"])

if not wl_df.empty:
	# Enrich với current price và các chỉ số
	wl_cur_prices = []
	wl_trends = []
	wl_pct_changes = []
	wl_notify_vals = []
	wl_ids = []
	
	for _, row in wl_df.iterrows():
		watchlist_id = row.get("id")
		ticker = row.get("ticker")
		buy_price = float(row.get("buy_price", 0))  # Giá trị thực tế VND
		price = get_realtime_price(ticker) or 0.0  # Giá trị thực tế VND
		
		wl_ids.append(watchlist_id)
		# Hiển thị chia 1000
		wl_cur_prices.append(price / 1000.0 if price > 0 else 0.0)
		
		# Tính % change từ buy price
		if buy_price > 0 and price > 0:
			pct_change = ((price - buy_price) / buy_price * 100)
			if pct_change > 0:
				wl_trends.append(f"🔼 +{pct_change:.1f}%")
			elif pct_change < 0:
				wl_trends.append(f"🔽 {pct_change:.1f}%")
			else:
				wl_trends.append("➡️ 0.0%")
			wl_pct_changes.append(pct_change)
		else:
			wl_trends.append("➡️ -")
			wl_pct_changes.append(0.0)
		
		# Notification từ API
		wl_notify_vals.append(bool(row.get("notify_enabled", False)))
	
	wl_enriched = wl_df.copy()
	# Buy Price hiển thị chia 1000
	wl_enriched["Buy Price"] = wl_enriched["buy_price"].apply(lambda x: x / 1000.0 if x > 0 else 0.0)
	wl_enriched["Current Price"] = wl_cur_prices
	wl_enriched["Trend"] = wl_trends
	wl_enriched["% Change"] = wl_pct_changes
	wl_enriched["Notify"] = wl_notify_vals
	wl_enriched["_watchlist_id"] = wl_ids
	
	wl_edited = st.data_editor(
		wl_enriched,
		use_container_width=True,
		key="ib_watchlist_editor",
		num_rows="dynamic",
		column_config={
			"ticker": st.column_config.TextColumn("Ticker"),
			"Buy Price": st.column_config.NumberColumn("Buy Price (K)", format="%.2f"),
			"Current Price": st.column_config.NumberColumn("Current Price (K)", format="%.2f"),
			"Trend": st.column_config.TextColumn("Trend"),
			"% Change": st.column_config.NumberColumn("% Change", format="%.1f%%"),
			"Notify": st.column_config.CheckboxColumn("Notify"),
			"_watchlist_id": None,  # Ẩn cột
		},
		disabled=["ticker", "Current Price", "Trend", "% Change", "_watchlist_id"],
		hide_index=True,
		column_order=["ticker", "Buy Price", "Current Price", "Trend", "% Change", "Notify"],
	)
	
	# Lưu watchlist settings (buy_price và notify_enabled)
	if st.button("💾 Save Watchlist Settings", type="primary"):
		success_count = 0
		error_count = 0
		for _, r in wl_edited.iterrows():
			watchlist_id = r.get("_watchlist_id")
			if not watchlist_id:
				error_count += 1
				continue
			
			# Nhân Buy Price lại với 1000 để lưu giá trị thực tế
			buy_price_val = float(r["Buy Price"] or 0.0) * 1000.0
			notify_enabled = bool(r["Notify"])
			
			update_data = {
				"buy_price": buy_price_val,
				"notify_enabled": notify_enabled
			}
			
			result = api.patch_data(f"/api/v1/watchlists/{int(watchlist_id)}", update_data)
			if result:
				success_count += 1
				load_watchlist.clear()  # Clear cache
			else:
				error_count += 1
		
		if success_count > 0:
			st.success(f"Saved {success_count} watchlist setting(s).")
		if error_count > 0:
			st.warning(f"Failed to save {error_count} watchlist setting(s).")
		if success_count > 0:
			st.rerun()
	
	# Xóa watchlist items (nếu cần)
	# Note: Streamlit data_editor không có built-in delete, cần thêm button riêng nếu cần
else:
	st.info("Watchlist is empty. Add tickers above to monitor.")


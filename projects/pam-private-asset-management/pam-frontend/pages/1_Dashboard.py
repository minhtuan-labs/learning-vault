import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from utils import auth
from services.pam_backend_api import get_data, post_data

# --- Cấu hình trang ---
st.set_page_config(
	page_title="My PAM | Dashboard",
	page_icon="📊",
	layout="wide"
)


# Khởi tạo session
auth.initialize_session()

# --- Kiểm tra xác thực ---
if not auth.is_authenticated():
	st.warning("Please login to access this page.")
	st.stop()

# --- CSS Styling ---
st.markdown("""
<style>
	.dashboard-container {
		background-color: #0e1117;
		color: #ffffff;
		padding: 20px;
	}
	
	.metric-card {
		background-color: #1e1e1e;
		padding: 20px;
		border-radius: 10px;
		border-left: 4px solid #00d4aa;
		margin: 10px 0;
	}
	
	.asset-card {
		background-color: #1e1e1e;
		padding: 15px;
		border-radius: 8px;
		margin: 10px 0;
		border-left: 4px solid;
	}
	
	.cash-card { border-left-color: #ff6b6b; }
	.stock-card { border-left-color: #4ecdc4; }
	.fund-card { border-left-color: #45b7d1; }
	.saving-card { border-left-color: #96ceb4; }
	
	.profit-positive { color: #00d4aa; }
	.profit-negative { color: #ff6b6b; }
	
	.total-assets {
		font-size: 2.5rem;
		font-weight: bold;
		color: #00d4aa;
	}
	
	.asset-percentage {
		font-size: 1.2rem;
		font-weight: bold;
	}
</style>
""", unsafe_allow_html=True)

# --- Header ---
col_title, col_refresh = st.columns([4, 1])
with col_title:
	st.title("📊 Asset Portfolio")
with col_refresh:
	if st.button("🔄", help="Refresh dashboard data", key="refresh_header"):
		st.rerun()

# --- Hàm lấy dữ liệu ---
@st.cache_data(ttl=300)  # Cache 5 phút
def get_portfolio_data():
	"""Lấy dữ liệu portfolio từ API - tính toán dựa trên trades và transactions"""
	try:
		# Lấy danh sách assets
		assets = get_data("/api/v1/assets/")
		if not assets:
			return None, None, None, None, None, None, None
		
		# Lấy tất cả stock trades
		stock_trades = get_data("/api/v1/trades/stock")
		stock_trades = stock_trades if stock_trades else []
		
		# Lấy tất cả fund trades  
		fund_trades = get_data("/api/v1/trades/fund")
		fund_trades = fund_trades if fund_trades else []
		
		# Lấy tất cả transactions (cash flow)
		transactions = []
		for asset in assets:
			if asset.get('asset_type') == 'cash':
				try:
					asset_transactions = get_data(f"/api/v1/assets/{asset['id']}/transactions/")
					if asset_transactions:
						transactions.extend(asset_transactions)
				except:
					pass
		
		# Lấy saving details
		saving_details = []
		for asset in assets:
			if asset.get('asset_type') == 'savings':
				try:
					asset_savings = get_data(f"/api/v1/assets/{asset['id']}/savings/")
					if asset_savings:
						saving_details.append(asset_savings)
				except:
					pass
		
		return assets, stock_trades, fund_trades, transactions, saving_details
	except Exception as e:
		st.error(f"Error fetching data: {e}")
		return None, None, None, None, None

@st.cache_data(ttl=300)
def calculate_asset_values(stock_trades, fund_trades, transactions, saving_details):
	"""Tính toán giá trị tài sản dựa trên trades và transactions"""
	
	# 1. Tính Cash (từ transactions)
	cash_total = 0
	for transaction in transactions:
		if transaction.get('transaction_type') in ['deposit', 'stock_sell', 'fund_sell', 'dividend_income']:
			cash_total += float(transaction.get('amount', 0))
		elif transaction.get('transaction_type') in ['withdrawal', 'stock_buy', 'fund_buy', 'fee']:
			cash_total -= float(transaction.get('amount', 0))
	
	# 2. Tính Stock Portfolio (từ stock trades)
	stock_portfolios = {}
	for trade in stock_trades:
		ticker = trade.get('ticker', '')
		if ticker not in stock_portfolios:
			stock_portfolios[ticker] = {'quantity': 0, 'cost_basis': 0}
		
		if trade.get('trade_type') == 'buy':
			stock_portfolios[ticker]['quantity'] += float(trade.get('quantity', 0))
			stock_portfolios[ticker]['cost_basis'] += float(trade.get('quantity', 0)) * float(trade.get('price', 0))
		elif trade.get('trade_type') == 'sell':
			stock_portfolios[ticker]['quantity'] -= float(trade.get('quantity', 0))
			stock_portfolios[ticker]['cost_basis'] -= float(trade.get('quantity', 0)) * float(trade.get('price', 0))
	
	# Tính giá trị hiện tại stock (giả sử giá không đổi - sẽ cần API giá thực tế)
	stock_total = 0
	stock_details = []
	for ticker, data in stock_portfolios.items():
		if data['quantity'] > 0:
			# Giả sử giá hiện tại = giá mua cuối (cần API giá thực tế)
			current_price = data['cost_basis'] / data['quantity'] if data['quantity'] > 0 else 0
			current_value = data['quantity'] * current_price
			stock_total += current_value
			stock_details.append({
				'ticker': ticker,
				'quantity': data['quantity'],
				'cost_basis': data['cost_basis'],
				'current_value': current_value,
				'profit_loss': current_value - data['cost_basis']
			})
	
	# 3. Tính Fund Portfolio (tương tự stock)
	fund_portfolios = {}
	for trade in fund_trades:
		ticker = trade.get('ticker', '')
		if ticker not in fund_portfolios:
			fund_portfolios[ticker] = {'quantity': 0, 'cost_basis': 0}
		
		if trade.get('trade_type') == 'buy':
			fund_portfolios[ticker]['quantity'] += float(trade.get('quantity', 0))
			fund_portfolios[ticker]['cost_basis'] += float(trade.get('quantity', 0)) * float(trade.get('price', 0))
		elif trade.get('trade_type') == 'sell':
			fund_portfolios[ticker]['quantity'] -= float(trade.get('quantity', 0))
			fund_portfolios[ticker]['cost_basis'] -= float(trade.get('quantity', 0)) * float(trade.get('price', 0))
	
	fund_total = 0
	fund_details = []
	for ticker, data in fund_portfolios.items():
		if data['quantity'] > 0:
			current_price = data['cost_basis'] / data['quantity'] if data['quantity'] > 0 else 0
			current_value = data['quantity'] * current_price
			fund_total += current_value
			fund_details.append({
				'ticker': ticker,
				'quantity': data['quantity'],
				'cost_basis': data['cost_basis'],
				'current_value': current_value,
				'profit_loss': current_value - data['cost_basis']
			})
	
	# 4. Tính Savings
	saving_total = 0
	saving_details_list = []
	for saving in saving_details:
		if saving:  # Kiểm tra saving không None
			if not saving.get('is_matured', False):
				# Chưa đáo hạn, tính giá trị đáo hạn (Est. Maturity)
				initial_amount = float(saving.get('initial_amount', 0))
				interest_rate = float(saving.get('interest_rate_pa', 0))
				term_months = float(saving.get('term_months', 0))
				# Tính giá trị đáo hạn: P * (1 + r/100 * t/12)
				maturity_value = initial_amount * (1 + (interest_rate / 100) * (term_months / 12))
				saving_total += maturity_value
				saving_details_list.append({
					'bank_code': saving.get('bank_code', ''),
					'initial_amount': saving.get('initial_amount', 0),
					'current_value': maturity_value,  # Dùng giá trị đáo hạn
					'interest_earned': maturity_value - float(saving.get('initial_amount', 0))
				})
			else:
				# Đã đáo hạn, dùng matured_amount
				matured_amount = float(saving.get('matured_amount', 0))
				saving_total += matured_amount
				saving_details_list.append({
					'bank_code': saving.get('bank_code', ''),
					'initial_amount': saving.get('initial_amount', 0),
					'current_value': matured_amount,
					'interest_earned': matured_amount - float(saving.get('initial_amount', 0))
				})
	
	return {
		'cash_total': cash_total,
		'stock_total': stock_total,
		'fund_total': fund_total,
		'saving_total': saving_total,
		'stock_details': stock_details,
		'fund_details': fund_details,
		'saving_details': saving_details_list
	}

# --- Lấy dữ liệu ---
data = get_portfolio_data()
if not data or not data[0]:
	st.warning("Không có dữ liệu tài sản. Vui lòng thêm tài sản trước.")
	st.stop()

assets, stock_trades, fund_trades, transactions, saving_details = data

# Tính toán giá trị tài sản
asset_values = calculate_asset_values(stock_trades, fund_trades, transactions, saving_details)

cash_total = asset_values['cash_total']
stock_total = asset_values['stock_total'] 
fund_total = asset_values['fund_total']
saving_total = asset_values['saving_total']

total_assets = cash_total + stock_total + fund_total + saving_total

# --- Layout chính ---
col1, col2 = st.columns([1, 1])

with col1:
	st.markdown("### 📈 Asset Overview")
	
	# Biểu đồ tròn
	if total_assets > 0:
		# Chuẩn bị dữ liệu cho biểu đồ với màu sắc tương phản rõ ràng
		asset_data = {
			'Asset Type': ['Cash', 'Stocks', 'Funds', 'Savings'],
			'Value': [cash_total, stock_total, fund_total, saving_total],
			'Colors': ['#ff6b6b', '#4ecdc4', '#f39c12', '#9b59b6']  # Red, Teal, Orange, Purple
		}
		
		# Tạo biểu đồ tròn
		fig = go.Figure(data=[go.Pie(
			labels=asset_data['Asset Type'],
			values=asset_data['Value'],
			hole=0.4,
			marker_colors=asset_data['Colors'],
			textinfo='label+percent',
			textfont_size=12
		)])
		
		fig.update_layout(
			title="Asset Allocation",
			title_font_size=16,
			showlegend=True,
			height=400,
			paper_bgcolor='rgba(0,0,0,0)',
			plot_bgcolor='rgba(0,0,0,0)',
			font=dict(color='white')
		)
		
		st.plotly_chart(fig, use_container_width=True)
	
	# Thống kê tổng quan
	st.markdown("#### 📊 Summary Statistics")
	
	# Row 1: Total Assets (full width)
	st.metric(
		label="Total Assets",
		value=f"{total_assets:,.0f} VND",
		delta=None
	)
	
	# Row 2: Asset Types và Growth (2 columns)
	col1_1, col1_2 = st.columns(2)
	
	with col1_1:
		st.metric(
			label="Asset Types",
			value=len([x for x in [cash_total, stock_total, fund_total, saving_total] if x > 0]),
			delta=None
		)
	
	with col1_2:
		# Tính tỷ lệ tăng trưởng (giả sử)
		growth_rate = 0  # Sẽ tính toán dựa trên dữ liệu lịch sử
		st.metric(
			label="Growth",
			value=f"{growth_rate:+.1f}%",
			delta=None
		)

with col2:
	st.markdown("### 💰 Asset Details")
	
	# Card Cash
	if cash_total > 0:
		st.markdown(f"""
		<div class="asset-card cash-card">
			<h4>💰 Cash</h4>
			<p><strong>Allocation:</strong> {(cash_total/total_assets*100):.1f}%</p>
			<p><strong>Value:</strong> {cash_total:,.0f} VND</p>
		</div>
		""", unsafe_allow_html=True)
	
	# Card Stocks
	if stock_total > 0:
		st.markdown(f"""
		<div class="asset-card stock-card">
			<h4>📈 Stocks</h4>
			<p><strong>Allocation:</strong> {(stock_total/total_assets*100):.1f}%</p>
			<p><strong>Value:</strong> {stock_total:,.0f} VND</p>
		</div>
		""", unsafe_allow_html=True)
	
	# Card Funds
	if fund_total > 0:
		st.markdown(f"""
		<div class="asset-card fund-card">
			<h4>🏦 Funds</h4>
			<p><strong>Allocation:</strong> {(fund_total/total_assets*100):.1f}%</p>
			<p><strong>Value:</strong> {fund_total:,.0f} VND</p>
		</div>
		""", unsafe_allow_html=True)
	
	# Card Savings
	if saving_total > 0:
		st.markdown(f"""
		<div class="asset-card saving-card">
			<h4>💳 Savings</h4>
			<p><strong>Allocation:</strong> {(saving_total/total_assets*100):.1f}%</p>
			<p><strong>Value:</strong> {saving_total:,.0f} VND</p>
		</div>
		""", unsafe_allow_html=True)

# --- Bảng chi tiết ---
st.markdown("---")
st.markdown("### 📋 Asset Details Table")

# Tạo DataFrame cho bảng chi tiết - sum up theo loại asset
asset_details = []

# Tính tổng cho từng loại asset
stock_total_cost = sum(stock['cost_basis'] for stock in asset_values['stock_details'])
stock_total_estimated = sum(stock['current_value'] for stock in asset_values['stock_details'])
stock_total_pnl = stock_total_estimated - stock_total_cost
stock_total_pnl_pct = (stock_total_pnl / stock_total_cost * 100) if stock_total_cost > 0 else 0

fund_total_cost = sum(fund['cost_basis'] for fund in asset_values['fund_details'])
fund_total_estimated = sum(fund['current_value'] for fund in asset_values['fund_details'])
fund_total_pnl = fund_total_estimated - fund_total_cost
fund_total_pnl_pct = (fund_total_pnl / fund_total_cost * 100) if fund_total_cost > 0 else 0

saving_total_cost = sum(saving['initial_amount'] for saving in asset_values['saving_details'])
saving_total_estimated = sum(saving['current_value'] for saving in asset_values['saving_details'])
saving_total_pnl = saving_total_estimated - saving_total_cost
saving_total_pnl_pct = (saving_total_pnl / saving_total_cost * 100) if saving_total_cost > 0 else 0

# Thêm Stock summary
if stock_total_cost > 0:
	asset_details.append({
		'Type': 'Stock',
		'Ticker': f"{len(asset_values['stock_details'])} positions",
		'Quantity': sum(stock['quantity'] for stock in asset_values['stock_details']),
		'Cost Basis': stock_total_cost,
		'Estimated Value': stock_total_estimated,
		'P&L': stock_total_pnl,
		'P&L %': stock_total_pnl_pct
	})

# Thêm Fund summary
if fund_total_cost > 0:
	asset_details.append({
		'Type': 'Fund',
		'Ticker': f"{len(asset_values['fund_details'])} positions",
		'Quantity': sum(fund['quantity'] for fund in asset_values['fund_details']),
		'Cost Basis': fund_total_cost,
		'Estimated Value': fund_total_estimated,
		'P&L': fund_total_pnl,
		'P&L %': fund_total_pnl_pct
	})

# Thêm Savings summary
if saving_total_cost > 0:
	asset_details.append({
		'Type': 'Savings',
		'Ticker': f"{len(asset_values['saving_details'])} accounts",
		'Quantity': len(asset_values['saving_details']),
		'Cost Basis': saving_total_cost,
		'Estimated Value': saving_total_estimated,
		'P&L': saving_total_pnl,
		'P&L %': saving_total_pnl_pct
	})

# Thêm Cash summary
if cash_total > 0:
	asset_details.append({
		'Type': 'Cash',
		'Ticker': 'CASH',
		'Quantity': 1,
		'Cost Basis': cash_total,
		'Estimated Value': cash_total,
		'P&L': 0,
		'P&L %': 0.0
	})

if asset_details:
	df = pd.DataFrame(asset_details)
	st.dataframe(
		df,
		use_container_width=True,
		column_config={
			"Quantity": st.column_config.NumberColumn("Quantity", format="localized"),
			"Cost Basis": st.column_config.NumberColumn("Cost Basis", format="localized"),
			"Estimated Value": st.column_config.NumberColumn("Estimated Value", format="localized"),
			"P&L": st.column_config.NumberColumn("P&L", format="localized"),
			"P&L %": st.column_config.NumberColumn("P&L %", format="%.1f%%"),
		}
	)
else:
	st.info("No assets recorded yet.")

# --- Action Buttons ---
st.markdown("---")
st.markdown("### 🚀 Quick Actions")

# Add Asset buttons
col1, col2, col3 = st.columns(3)

with col1:
	if st.button("📈 Add Stock Trade", type="primary", use_container_width=True):
		st.switch_page("pages/2_Stock_Trade.py")

with col2:
	if st.button("🏦 Add Fund Trade", type="primary", use_container_width=True):
		st.switch_page("pages/3_Fund_Trade.py")

with col3:
	if st.button("💳 Add Saving", type="primary", use_container_width=True):
		st.switch_page("pages/5_Saving.py")

# Other actions
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
	if st.button("💰 Cash Flow", use_container_width=True):
		st.switch_page("pages/4_Cash_Flow.py")

with col2:
	if st.button("📊 View Reports", use_container_width=True):
		st.info("Reports feature will be developed")

with col3:
	if st.button("⚙️ Settings", use_container_width=True):
		st.info("Settings feature will be developed")

# --- Footer ---
st.markdown("---")
st.markdown("*Dashboard last updated: " + datetime.now().strftime("%d/%m/%Y %H:%M") + "*")


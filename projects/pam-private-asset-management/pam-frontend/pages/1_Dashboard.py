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
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
	st.title("📊 Danh mục tài sản")
with col2:
	st.selectbox("Tiểu khoản", ["Tất cả"], key="sub_account")
with col3:
	if st.button("🔄", help="Refresh"):
		st.rerun()

# --- Hàm lấy dữ liệu ---
@st.cache_data(ttl=300)  # Cache 5 phút
def get_portfolio_data():
	"""Lấy dữ liệu portfolio từ API"""
	try:
		# Lấy danh sách assets
		assets = get_data("/api/v1/assets/")
		if not assets:
			return None, None, None, None, None
		
		# Phân loại assets theo type
		cash_assets = [a for a in assets if a.get('asset_type') == 'cash']
		stock_assets = [a for a in assets if a.get('asset_type') == 'stocks']
		fund_assets = [a for a in assets if a.get('asset_type') == 'funds']
		saving_assets = [a for a in assets if a.get('asset_type') == 'savings']
		
		return assets, cash_assets, stock_assets, fund_assets, saving_assets
	except Exception as e:
		st.error(f"Error fetching data: {e}")
		return None, None, None, None, None

@st.cache_data(ttl=300)
def get_asset_details(asset_id):
	"""Lấy chi tiết asset"""
	try:
		return get_data(f"/api/v1/assets/{asset_id}")
	except:
		return None

# --- Lấy dữ liệu ---
assets, cash_assets, stock_assets, fund_assets, saving_assets = get_portfolio_data()

if not assets:
	st.warning("Không có dữ liệu tài sản. Vui lòng thêm tài sản trước.")
	st.stop()

# --- Tính toán tổng quan ---
def calculate_total_value(asset_list):
	"""Tính tổng giá trị của danh sách assets"""
	total = 0
	for asset in asset_list:
		if asset.get('current_value'):
			total += float(asset['current_value'])
	return total

# Tính tổng giá trị từng loại
cash_total = calculate_total_value(cash_assets)
stock_total = calculate_total_value(stock_assets)
fund_total = calculate_total_value(fund_assets)
saving_total = calculate_total_value(saving_assets)

total_assets = cash_total + stock_total + fund_total + saving_total

# --- Layout chính ---
col1, col2 = st.columns([1, 1])

with col1:
	st.markdown("### 📈 Tổng quan tài sản")
	
	# Biểu đồ tròn
	if total_assets > 0:
		# Chuẩn bị dữ liệu cho biểu đồ
		asset_data = {
			'Loại tài sản': ['Tiền mặt', 'Cổ phiếu', 'Quỹ', 'Tiết kiệm'],
			'Giá trị': [cash_total, stock_total, fund_total, saving_total],
			'Màu sắc': ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
		}
		
		# Tạo biểu đồ tròn
		fig = go.Figure(data=[go.Pie(
			labels=asset_data['Loại tài sản'],
			values=asset_data['Giá trị'],
			hole=0.4,
			marker_colors=asset_data['Màu sắc'],
			textinfo='label+percent',
			textfont_size=12
		)])
		
		fig.update_layout(
			title="Phân bổ tài sản",
			title_font_size=16,
			showlegend=True,
			height=400,
			paper_bgcolor='rgba(0,0,0,0)',
			plot_bgcolor='rgba(0,0,0,0)',
			font=dict(color='white')
		)
		
		st.plotly_chart(fig, use_container_width=True)
	
	# Thống kê tổng quan
	st.markdown("#### 📊 Thống kê tổng quan")
	col1_1, col1_2, col1_3 = st.columns(3)
	
	with col1_1:
		st.metric(
			label="Tổng tài sản",
			value=f"{total_assets:,.0f} VNĐ",
			delta=None
		)
	
	with col1_2:
		st.metric(
			label="Số loại tài sản",
			value=len([x for x in [cash_total, stock_total, fund_total, saving_total] if x > 0]),
			delta=None
		)
	
	with col1_3:
		# Tính tỷ lệ tăng trưởng (giả sử)
		growth_rate = 0  # Sẽ tính toán dựa trên dữ liệu lịch sử
		st.metric(
			label="Tăng trưởng",
			value=f"{growth_rate:+.1f}%",
			delta=None
		)

with col2:
	st.markdown("### 💰 Chi tiết từng loại tài sản")
	
	# Card Tiền mặt
	if cash_total > 0:
		st.markdown(f"""
		<div class="asset-card cash-card">
			<h4>💰 Tiền mặt</h4>
			<p><strong>Tỷ trọng:</strong> {(cash_total/total_assets*100):.1f}%</p>
			<p><strong>Giá trị:</strong> {cash_total:,.0f} VNĐ</p>
		</div>
		""", unsafe_allow_html=True)
	
	# Card Cổ phiếu
	if stock_total > 0:
		st.markdown(f"""
		<div class="asset-card stock-card">
			<h4>📈 Cổ phiếu</h4>
			<p><strong>Tỷ trọng:</strong> {(stock_total/total_assets*100):.1f}%</p>
			<p><strong>Giá trị:</strong> {stock_total:,.0f} VNĐ</p>
		</div>
		""", unsafe_allow_html=True)
	
	# Card Quỹ
	if fund_total > 0:
		st.markdown(f"""
		<div class="asset-card fund-card">
			<h4>🏦 Quỹ</h4>
			<p><strong>Tỷ trọng:</strong> {(fund_total/total_assets*100):.1f}%</p>
			<p><strong>Giá trị:</strong> {fund_total:,.0f} VNĐ</p>
		</div>
		""", unsafe_allow_html=True)
	
	# Card Tiết kiệm
	if saving_total > 0:
		st.markdown(f"""
		<div class="asset-card saving-card">
			<h4>💳 Tiết kiệm</h4>
			<p><strong>Tỷ trọng:</strong> {(saving_total/total_assets*100):.1f}%</p>
			<p><strong>Giá trị:</strong> {saving_total:,.0f} VNĐ</p>
		</div>
		""", unsafe_allow_html=True)

# --- Bảng chi tiết ---
st.markdown("---")
st.markdown("### 📋 Bảng chi tiết tài sản")

# Tạo DataFrame cho bảng
asset_details = []
for asset in assets:
	if asset.get('current_value', 0) > 0:
		asset_type_map = {
			'cash': 'Tiền mặt',
			'stocks': 'Cổ phiếu', 
			'funds': 'Quỹ',
			'savings': 'Tiết kiệm'
		}
		
		asset_details.append({
			'Loại': asset_type_map.get(asset.get('asset_type'), asset.get('asset_type')),
			'Tên': asset.get('name', 'N/A'),
			'Giá trị hiện tại': f"{float(asset.get('current_value', 0)):,.0f} VNĐ",
			'Mô tả': asset.get('description', ''),
			'Ngày tạo': asset.get('created_at', '')[:10] if asset.get('created_at') else 'N/A'
		})

if asset_details:
	df = pd.DataFrame(asset_details)
	st.dataframe(df, use_container_width=True)
else:
	st.info("Chưa có tài sản nào được ghi nhận.")

# --- Nút hành động ---
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
	if st.button("➕ Thêm tài sản", type="primary"):
		st.switch_page("pages/2_Stock_Trade.py")

with col2:
	if st.button("📊 Xem báo cáo"):
		st.info("Tính năng báo cáo sẽ được phát triển")

with col3:
	if st.button("⚙️ Cài đặt"):
		st.info("Tính năng cài đặt sẽ được phát triển")

with col4:
	if st.button("🔄 Làm mới"):
		st.rerun()

# --- Footer ---
st.markdown("---")
st.markdown("*Dashboard được cập nhật lần cuối: " + datetime.now().strftime("%d/%m/%Y %H:%M") + "*")


import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta
import json
import base64


def _get_cookie_manager():
	"""Safe cookie manager getter - sử dụng session state để cache và tránh duplicate key"""
	# Sử dụng session state để cache cookie manager
	if 'cookie_manager' not in st.session_state:
		try:
			# Sử dụng fixed key để tránh tạo nhiều instances
			st.session_state['cookie_manager'] = stx.CookieManager(key="pam_cookie_manager")
		except Exception as e:
			# Nếu không thể tạo cookie manager, lưu None
			st.session_state['cookie_manager'] = None
			# Chỉ log warning thay vì error để tránh spam
			if hasattr(st, 'warning'):
				st.warning(f"Cookie manager initialization failed: {e}")
	
	return st.session_state.get('cookie_manager')


def initialize_session():
	"""Khởi tạo session từ cookie nếu có - cải thiện để tránh mất session khi refresh"""
	# Luôn kiểm tra cookie trước, ngay cả khi đã có session state
	cookie_manager = _get_cookie_manager()
	if cookie_manager:
		try:
			cookie_token = cookie_manager.get('auth_token')
			
			# Nếu có token trong cookie và chưa có trong session state
			if cookie_token and 'auth_token' not in st.session_state:
				if _is_token_valid(cookie_token):
					st.session_state['auth_token'] = cookie_token
				else:
					# Token hết hạn, xóa cookie
					cookie_manager.delete('auth_token')
			
			# Nếu có session state nhưng không có cookie, đồng bộ lại
			elif 'auth_token' in st.session_state and not cookie_token:
				session_token = st.session_state['auth_token']
				if _is_token_valid(session_token):
					# Khôi phục cookie từ session
					expires_at = datetime.now() + timedelta(days=30)
					cookie_manager.set('auth_token', session_token, expires_at=expires_at)
				else:
					# Session token hết hạn, xóa session
					del st.session_state['auth_token']
			
			# Nếu cả hai đều có nhưng khác nhau, ưu tiên cookie
			elif (cookie_token and 'auth_token' in st.session_state and 
				  cookie_token != st.session_state['auth_token']):
				if _is_token_valid(cookie_token):
					st.session_state['auth_token'] = cookie_token
				else:
					# Cookie token hết hạn, xóa cả hai
					cookie_manager.delete('auth_token')
					if 'auth_token' in st.session_state:
						del st.session_state['auth_token']
						
		except Exception as e:
			# Log lỗi nhưng không crash app
			pass


def _is_token_valid(token: str) -> bool:
	"""Kiểm tra token có còn hợp lệ không"""
	try:
		# Decode JWT token để kiểm tra expiration
		parts = token.split('.')
		if len(parts) != 3:
			return False
		
		# Decode payload
		payload = parts[1]
		# Add padding if needed
		payload += '=' * (4 - len(payload) % 4)
		decoded = base64.urlsafe_b64decode(payload)
		payload_data = json.loads(decoded)
		
		# Kiểm tra expiration
		exp = payload_data.get('exp')
		if exp:
			exp_time = datetime.fromtimestamp(exp)
			return datetime.now() < exp_time
		return True
	except Exception:
		return False


def is_authenticated():
	"""Kiểm tra user có đăng nhập và token còn hợp lệ không - cải thiện cho refresh"""
	# Luôn gọi initialize_session để đồng bộ cookie và session
	initialize_session()
	
	token = st.session_state.get('auth_token')
	if not token:
		return False
	
	# Kiểm tra token expiration
	if not _is_token_valid(token):
		# Token hết hạn, clear session nhưng không logout (để tránh loop)
		if 'auth_token' in st.session_state:
			del st.session_state['auth_token']
		cookie_manager = _get_cookie_manager()
		if cookie_manager:
			try:
				cookie_manager.delete('auth_token')
			except:
				pass
		return False
	
	return True


def login(token: str):
	"""Lưu token vào session và cookie - cải thiện persistence"""
	st.session_state['auth_token'] = token
	
	# Lưu vào cookie với expiration dài hơn (fallback nếu cookie manager fail)
	cookie_manager = _get_cookie_manager()
	if cookie_manager:
		try:
			# Cookie expiration 30 ngày, JWT token 24h
			expires_at = datetime.now() + timedelta(days=30)
			cookie_manager.set('auth_token', token, expires_at=expires_at)
		except Exception:
			# Cookie manager fail, nhưng session vẫn hoạt động
			pass
	else:
		# Nếu không có cookie manager, ít nhất session state vẫn hoạt động
		pass


def logout():
	"""Đăng xuất và xóa session/cookie"""
	if 'auth_token' in st.session_state:
		del st.session_state['auth_token']
	
	# Xóa cookie (fallback nếu cookie manager fail)
	cookie_manager = _get_cookie_manager()
	if cookie_manager:
		try:
			cookie_manager.delete('auth_token')
		except Exception:
			# Cookie manager fail, nhưng session vẫn được clear
			pass
	
	# Clear cookie manager khỏi session state để tránh conflict
	if 'cookie_manager' in st.session_state:
		del st.session_state['cookie_manager']
	
	# Rerun để refresh page
	try:
		st.rerun()
	except st.errors.StreamlitAPIException:
		pass


def debug_session_state():
	"""Debug function để kiểm tra trạng thái session và cookie"""
	if st.checkbox("🔍 Debug Session State"):
		st.write("**Session State:**")
		st.write(f"- auth_token in session: {'auth_token' in st.session_state}")
		if 'auth_token' in st.session_state:
			token = st.session_state['auth_token']
			st.write(f"- Token length: {len(token) if token else 0}")
			st.write(f"- Token valid: {_is_token_valid(token) if token else False}")
		
		st.write("**Cookie Manager State:**")
		st.write(f"- cookie_manager in session: {'cookie_manager' in st.session_state}")
		
		st.write("**Cookie State:**")
		cookie_manager = _get_cookie_manager()
		if cookie_manager:
			try:
				cookie_token = cookie_manager.get('auth_token')
				st.write(f"- Cookie token exists: {cookie_token is not None}")
				if cookie_token:
					st.write(f"- Cookie token length: {len(cookie_token)}")
					st.write(f"- Cookie token valid: {_is_token_valid(cookie_token)}")
			except Exception as e:
				st.write(f"- Cookie error: {e}")
		else:
			st.write("- Cookie manager not available")
		
		# Thêm button để clear cookie manager nếu cần
		if st.button("🔄 Reset Cookie Manager"):
			if 'cookie_manager' in st.session_state:
				del st.session_state['cookie_manager']
			st.rerun()


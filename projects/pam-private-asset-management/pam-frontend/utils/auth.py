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
	
	cookie_manager = st.session_state.get('cookie_manager')
	
	# Nếu cookie manager bị None, thử tạo lại
	if cookie_manager is None:
		try:
			st.session_state['cookie_manager'] = stx.CookieManager(key="pam_cookie_manager")
			cookie_manager = st.session_state['cookie_manager']
		except Exception:
			# Vẫn fail, giữ None
			pass
	
	return cookie_manager


# Simplified approach - chỉ dùng session state với fallback đơn giản


def initialize_session():
	"""Đơn giản hóa - chỉ sync cookie và session state"""
	cookie_manager = _get_cookie_manager()
	
	if cookie_manager:
		try:
			cookie_token = cookie_manager.get('auth_token')
			session_token = st.session_state.get('auth_token')
			
			# Nếu có cookie và không có session, restore từ cookie
			if cookie_token and not session_token:
				if _is_token_valid(cookie_token):
					st.session_state['auth_token'] = cookie_token
				else:
					cookie_manager.delete('auth_token')
			
			# Nếu có session và không có cookie, sync vào cookie
			elif session_token and not cookie_token:
				if _is_token_valid(session_token):
					expires_at = datetime.now() + timedelta(days=30)
					cookie_manager.set('auth_token', session_token, expires_at=expires_at)
				else:
					del st.session_state['auth_token']
			
			# Nếu cả hai đều có, ưu tiên cookie
			elif cookie_token and session_token and cookie_token != session_token:
				if _is_token_valid(cookie_token):
					st.session_state['auth_token'] = cookie_token
				elif _is_token_valid(session_token):
					expires_at = datetime.now() + timedelta(days=30)
					cookie_manager.set('auth_token', session_token, expires_at=expires_at)
				else:
					cookie_manager.delete('auth_token')
					del st.session_state['auth_token']
					
		except Exception:
			# Cookie fail, không làm gì
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
		# Token hết hạn, clear session và cookie
		_clear_auth_session()
		return False
	
	return True


def _clear_auth_session():
	"""Helper function để clear session và cookie"""
	if 'auth_token' in st.session_state:
		del st.session_state['auth_token']
	
	cookie_manager = _get_cookie_manager()
	if cookie_manager:
		try:
			cookie_manager.delete('auth_token')
		except:
			pass


def login(token: str):
	"""Đơn giản hóa - chỉ lưu session và cookie"""
	st.session_state['auth_token'] = token
	
	cookie_manager = _get_cookie_manager()
	if cookie_manager:
		try:
			expires_at = datetime.now() + timedelta(days=30)
			cookie_manager.set('auth_token', token, expires_at=expires_at)
		except Exception:
			# Cookie fail, session vẫn hoạt động
			pass


def logout():
	"""Đơn giản hóa - chỉ clear session và cookie"""
	if 'auth_token' in st.session_state:
		del st.session_state['auth_token']
	
	cookie_manager = _get_cookie_manager()
	if cookie_manager:
		try:
			cookie_manager.delete('auth_token')
		except Exception:
			pass
	
	# Clear cookie manager khỏi session state
	if 'cookie_manager' in st.session_state:
		del st.session_state['cookie_manager']
	
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
			st.write(f"- Token preview: {token[:20] + '...' if token else 'None'}")
		
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
					st.write(f"- Cookie token preview: {cookie_token[:20] + '...' if cookie_token else 'None'}")
			except Exception as e:
				st.write(f"- Cookie error: {e}")
		else:
			st.write("- Cookie manager not available")
		
		# Thêm button để clear cookie manager nếu cần
		col1, col2, col3 = st.columns(3)
		with col1:
			if st.button("🔄 Reset Cookie Manager"):
				if 'cookie_manager' in st.session_state:
					del st.session_state['cookie_manager']
				st.rerun()
		
		with col2:
			if st.button("🧪 Test Cookie Set"):
				cookie_manager = _get_cookie_manager()
				if cookie_manager:
					try:
						cookie_manager.set('test_cookie', 'test_value')
						st.success("Cookie set successful!")
					except Exception as e:
						st.error(f"Cookie set failed: {e}")
				else:
					st.error("No cookie manager available")
		
		with col3:
			if st.button("🧪 Test Cookie Get"):
				cookie_manager = _get_cookie_manager()
				if cookie_manager:
					try:
						test_value = cookie_manager.get('test_cookie')
						st.write(f"Test cookie value: {test_value}")
					except Exception as e:
						st.error(f"Cookie get failed: {e}")
				else:
					st.error("No cookie manager available")
		
		# Thêm thông tin về browser và environment
		st.write("**Environment Info:**")
		st.write(f"- Streamlit version: {st.__version__}")
		st.write(f"- Current page: {st.get_option('server.headless')}")
		
		# Force sync button
		if st.button("🔄 Force Sync Session"):
			initialize_session()
			st.rerun()


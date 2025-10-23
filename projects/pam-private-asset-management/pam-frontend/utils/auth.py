import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta


@st.cache_resource
def get_cookie_manager():
	return stx.CookieManager()


cookies = get_cookie_manager()


def initialize_session():
	if 'auth_token' not in st.session_state:
		st.session_state['auth_token'] = cookies.get('auth_token')


def is_authenticated():
	return st.session_state.get('auth_token') is not None


def login(token: str):
	st.session_state['auth_token'] = token
	expires_at = datetime.now() + timedelta(days=30)
	cookies.set('auth_token', token, expires_at=expires_at)


def logout():
	if 'auth_token' in st.session_state:
		del st.session_state['auth_token']
	cookies.delete('auth_token')
	try:
		st.rerun()
	except st.errors.StreamlitAPIException:
		pass


import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from streamlit_cookies_manager.cookie_manager import CookiesNotReady


cookies = EncryptedCookieManager(
	password="my_super_secret_pam_cookie_key"
)


def initialize_session():
	if 'auth_token' not in st.session_state:
		try:
			st.session_state['auth_token'] = cookies.get('auth_token')
		except CookiesNotReady:
			st.session_state['auth_token'] = None


def is_authenticated():
	return st.session_state.get('auth_token') is not None


def login(token: str):
    st.session_state['auth_token'] = token
    try:
        cookies['auth_token'] = token
        cookies.save()
    except CookiesNotReady:
        pass


def logout():
    st.session_state['auth_token'] = None
    try:
        if 'auth_token' in cookies:
            del cookies['auth_token']
            cookies.save()
    except CookiesNotReady:
        pass


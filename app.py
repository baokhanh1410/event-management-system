import streamlit as st
from src.connection import get_session
from src.auth import authenticate_user, register_new_guest_user

# ============================================================
# CONFIGURATION & STATE INITIALIZATION
# ============================================================

# Configure Streamlit page
st.set_page_config(page_title="Event Management", page_icon="🎫", layout="wide")

# Initialize authentication state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# ============================================================
# MAIN UI RENDERING
# ============================================================

if not st.session_state.authenticated:
    st.title("🔐 Event Management System")
    st.warning("Please select the **Login** page on the left menu to Login or Register.")
else:
    # Interface upon successful login
    st.title(f"👋 Welcome {st.session_state.user_info['role']}!")
    st.info("👈 Please select the functional modules on the Sidebar to get started.")
    st.success("System is operating normally. You can view events, mark attendance, or manage finances depending on your permissions.")
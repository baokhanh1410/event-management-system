import streamlit as st
from src.connection import get_session
from src.auth import authenticate_user, register_new_guest_user

# ============================================================
# INITIALIZATION & SECURITY
# ============================================================

# Initialize login state if not exists
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

st.title("🔐 Login / Register")

# ============================================================
# AUTHENTICATED VIEW
# ============================================================

if st.session_state.authenticated:
    st.success(f"You have successfully logged in with {st.session_state.user_info['role']} role!")
    
    st.write("### Account Information")
    user_info = st.session_state.user_info
    st.write(f"- **User ID:** {user_info.get('user_id')}")
    st.write(f"- **Role:** {user_info.get('role')}")
    if user_info.get('guest_id'):
        st.write(f"- **Guest ID:** {user_info.get('guest_id')}")
    
    st.divider()
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.rerun()

# ============================================================
# LOGIN / REGISTER FORMS
# ============================================================

else:
    tab1, tab2 = st.tabs(["Login", "Register Account (Guest)"])
    
    with tab1:
        # Secure login form
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                session = get_session()
                user_data = authenticate_user(session, username, password)
                session.close()
                
                if user_data:
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_data
                    st.success("Login successful! Please select a feature from the left sidebar.")
                    st.rerun() # Reload page to enter the system
                else:
                    st.error("Incorrect username or password!")
                    
    with tab2:
        st.info("Account registration for Guests.")
        with st.form("signup_form"):
            new_username = st.text_input("New Username *")
            new_password = st.text_input("Password *", type="password")
            new_name = st.text_input("Full Name *")
            new_email = st.text_input("Email *")
            new_phone = st.text_input("Phone Number *")
            signup_submit = st.form_submit_button("Register")
            
            if signup_submit:
                if not (new_username and new_password and new_name and new_email and new_phone):
                    st.error("Please fill in all fields!")
                else:
                    session = get_session()
                    success, msg = register_new_guest_user(session, new_username, new_password, new_name, new_email, new_phone)
                    session.close()
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

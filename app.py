import streamlit as st
from src.connection import get_session
from src.crud import get_all_events, create_event 
from src.auth import authenticate_user

# Cấu hình trang Streamlit
st.set_page_config(page_title="Event Management", page_icon="🎫", layout="wide")

# Khởi tạo trạng thái đăng nhập
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Đăng nhập hệ thống")
    
    # Form đăng nhập an toàn
    with st.form("login_form"):
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")
        submit = st.form_submit_button("Đăng nhập")
        
        if submit:
            session = get_session()
            user_data = authenticate_user(session, username, password)
            session.close()
            
            if user_data:
                st.session_state.authenticated = True
                st.session_state.user_info = user_data
                st.success("Đăng nhập thành công! Hãy chọn tính năng ở thanh bên trái (Sidebar).")
                st.rerun() # Load lại trang để vào hệ thống
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu!")
else:
    # Giao diện khi đã đăng nhập thành công
    st.title(f"👋 Chào mừng {st.session_state.user_info['role']}!")
    st.info("👈 Hãy chọn các module chức năng trên thanh Sidebar để bắt đầu.")
    
    if st.button("Đăng xuất"):
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.rerun()
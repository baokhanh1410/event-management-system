import streamlit as st
from src.connection import get_session
from src.auth import authenticate_user, register_new_guest_user

# Khởi tạo trạng thái đăng nhập nếu chưa có
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

st.title("🔐 Đăng nhập / Đăng ký")

if st.session_state.authenticated:
    st.success(f"Bạn đã đăng nhập thành công với quyền {st.session_state.user_info['role']}!")
    
    st.write("### Thông tin tài khoản")
    user_info = st.session_state.user_info
    st.write(f"- **User ID:** {user_info.get('user_id')}")
    st.write(f"- **Quyền (Role):** {user_info.get('role')}")
    if user_info.get('guest_id'):
        st.write(f"- **Guest ID:** {user_info.get('guest_id')}")
    
    st.divider()
    if st.button("Đăng xuất"):
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.rerun()

else:
    tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký tài khoản (Guest)"])
    
    with tab1:
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
                    
    with tab2:
        st.info("Đăng ký tài khoản dành cho Khách mời (Guest).")
        with st.form("signup_form"):
            new_username = st.text_input("Tên đăng nhập mới *")
            new_password = st.text_input("Mật khẩu *", type="password")
            new_name = st.text_input("Họ và Tên *")
            new_email = st.text_input("Email *")
            new_phone = st.text_input("Số điện thoại *")
            signup_submit = st.form_submit_button("Đăng ký")
            
            if signup_submit:
                if not (new_username and new_password and new_name and new_email and new_phone):
                    st.error("Vui lòng điền đầy đủ thông tin!")
                else:
                    session = get_session()
                    success, msg = register_new_guest_user(session, new_username, new_password, new_name, new_email, new_phone)
                    session.close()
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

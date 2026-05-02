import streamlit as st
from src.connection import get_session
from src.auth import authenticate_user, register_new_guest_user

# Cấu hình trang Streamlit
st.set_page_config(page_title="Event Management", page_icon="🎫", layout="wide")

# Khởi tạo trạng thái đăng nhập
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Hệ thống Quản lý Sự kiện")
    st.warning("Vui lòng chọn trang **Login** ở menu bên trái để Đăng nhập hoặc Đăng ký.")
else:
    # Giao diện khi đã đăng nhập thành công
    st.title(f"👋 Chào mừng {st.session_state.user_info['role']}!")
    st.info("👈 Hãy chọn các module chức năng trên thanh Sidebar để bắt đầu.")
    st.success("Hệ thống hoạt động bình thường. Bạn có thể xem các sự kiện, đánh dấu tham dự, hoặc quản lý tài chính tùy thuộc vào quyền hạn của bạn.")
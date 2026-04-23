import streamlit as st
import datetime
from src.connection import get_session
from src.crud import get_all_events, create_event
from src.auth import has_permission

# 1. BẢO MẬT: Kiểm tra login
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Vui lòng đăng nhập ở trang chủ trước khi truy cập!")
    st.stop()

st.title("📅 Quản lý Lịch trình Sự kiện")
session = get_session()

# 2. KIỂM TRA QUYỀN XEM (view_events)
if has_permission('view_events'):
    st.subheader("Danh sách Sự kiện")
    try:
        events_df = get_all_events(session)
        if not events_df.empty:
            st.dataframe(events_df, use_container_width=True, hide_index=True)
        else:
            st.info("Hiện chưa có sự kiện nào trong hệ thống.")
    except Exception as e:
        st.error(f"Lỗi khi tải danh sách: {e}")
else:
    st.error("🚫 Bạn không có quyền xem danh sách sự kiện.")

# 3. KIỂM TRA QUYỀN TẠO (create_events - khớp với ảnh của Khánh)
if has_permission('create_events'):
    st.divider()
    st.subheader("➕ Thêm Sự kiện Mới")
    
    with st.form("add_event_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Tên sự kiện")
            date = st.date_input("Ngày tổ chức", min_value=datetime.date.today())
            time_start = st.time_input("Giờ bắt đầu")
            category = st.selectbox("Thể loại", ['Conference', 'Workshop', 'Seminar', 'Concert'])
            
        with col2:
            venue_id = st.number_input("Mã Địa điểm (Venue ID)", min_value=1, step=1)
            org_id = st.number_input("Mã Ban tổ chức (Organizer ID)", min_value=1, step=1)
            time_end = st.time_input("Giờ kết thúc")
            price = st.number_input("Giá vé cơ bản ($)", min_value=0.0, step=5.0)
        submit_btn = st.form_submit_button("Lưu sự kiện")
        
        if submit_btn:
            # Format thời gian chính xác cho MySQL DATETIME
            start_dt = f"{date} {time_start}"
            end_dt = f"{date} {time_end}"
            
            # Gọi CRUD xử lý (đã có bẫy lỗi từ Trigger check xung đột lịch)
            success, msg = create_event(session, name, start_dt, end_dt, venue_id, org_id, category, price)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
else:
    # Nếu là Staff không có quyền tạo, có thể hiện lời nhắc nhẹ
    st.info("💡 Lưu ý: Bạn chỉ có quyền xem, không có quyền thêm sự kiện mới.")

session.close()
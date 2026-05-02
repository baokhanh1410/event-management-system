import streamlit as st
import datetime
import pandas as pd
from src.connection import get_session
from src.crud import get_all_events, create_event, get_event_by_id, update_event, get_categories, create_registration, get_guest_profile, get_events_list, get_guest_registered_events, get_available_events_for_guest
from src.auth import has_permission
from src.ml_models import get_recommended_events

# 1. BẢO MẬT: Kiểm tra login
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Vui lòng đăng nhập ở trang chủ trước khi truy cập!")
    st.stop()

st.title("📅 Quản lý Lịch trình Sự kiện")
session = get_session()
if session is None:
    st.error("❌ Không thể kết nối database. Vui lòng kiểm tra cấu hình.")
    st.stop()

# Hiển thị thông báo thành công từ lần rerun trước
if 'success_msg' in st.session_state:
    st.success(st.session_state['success_msg'])
    del st.session_state['success_msg']

# Load categories once
categories_df = get_categories(session)
category_options = categories_df['category_name'].tolist()
category_mapping = dict(zip(categories_df['category_name'], categories_df['category_id']))

# 2. KIỂM TRA QUYỀN XEM (view_public_events)
# if has_permission('view_public_events'):
st.subheader("Danh sách Sự kiện")
try:
    events_df = get_all_events(session)
    if not events_df.empty:
        display_df = events_df.copy()
        display_df = display_df[['event_id', 'event_name', 'categories', 'event_date', 'venue_name', 'organizer_name', 'status', 'base_price']]
        display_df.columns = ['ID', 'Tên sự kiện', 'Thể loại', 'Ngày tổ chức', 'Địa điểm', 'Ban tổ chức', 'Trạng thái', 'Giá vé ($)']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("Hiện chưa có sự kiện nào trong hệ thống.")
except Exception as e:
    st.error(f"Lỗi khi tải danh sách: {e}")
# else:
#     st.error("🚫 Bạn không có quyền xem danh sách sự kiện.")

# 3. ĐĂNG KÝ SỰ KIỆN CHO GUEST
if st.session_state.user_info.get('role') == 'Guest' and st.session_state.user_info.get('guest_id'):
    guest_id = st.session_state.user_info['guest_id']
    
    # --- My Events Section ---
    st.divider()
    st.subheader("📌 Sự kiện tôi đã tham gia")
    try:
        my_events_df = get_guest_registered_events(session, guest_id)
        if not my_events_df.empty:
            my_display = my_events_df[['event_id', 'event_name', 'categories', 'event_date', 'venue_name', 'organizer_name', 'status', 'base_price']].copy()
            my_display.columns = ['ID', 'Tên sự kiện', 'Thể loại', 'Ngày tổ chức', 'Địa điểm', 'Ban tổ chức', 'Trạng thái', 'Giá vé ($)']
            st.dataframe(my_display, use_container_width=True, hide_index=True)
        else:
            st.info("Bạn chưa đăng ký sự kiện nào. Hãy xem phần Gợi ý bên dưới để tham gia!")
    except Exception as e:
        st.error(f"Lỗi khi tải danh sách: {e}")
    
    # --- XGBoost Recommendation Section ---
    st.divider()
    st.subheader("🌟 Gợi ý Dành Riêng Cho Bạn")
    
    @st.cache_data(ttl=3600)
    def fetch_recommendations(gid):
        temp_session = get_session()
        try:
            return get_recommended_events(temp_session, gid)
        finally:
            temp_session.close()

    with st.spinner("Đang tìm kiếm sự kiện phù hợp..."):
        try:
            rec_df = fetch_recommendations(guest_id)
        except Exception as e:
            st.error(f"Không thể tải gợi ý: {e}")
            rec_df = pd.DataFrame()
            
    if not rec_df.empty:
        display_rec = rec_df[['event_name', 'categories', 'event_date', 'venue_name', 'base_price']].copy()
        display_rec.columns = ['Tên sự kiện', 'Thể loại', 'Ngày tổ chức', 'Địa điểm', 'Giá vé ($)']
        st.dataframe(display_rec, use_container_width=True, hide_index=True)
    else:
        st.info("Hiện tại chưa có gợi ý nào mới cho bạn.")

    st.divider()
    st.subheader("🎯 Đăng ký tham gia Sự kiện")
    profile = get_guest_profile(session, guest_id)
    
    if profile:
        with st.form("guest_registration_form"):
            st.info("Thông tin của bạn đã được điền tự động.")
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Họ và Tên", value=profile['name'], disabled=True)
                st.text_input("Email", value=profile['email'], disabled=True)
            with col2:
                st.text_input("Số điện thoại", value=profile['phone'], disabled=True)
                events_list_df = get_available_events_for_guest(session, guest_id)
                if not events_list_df.empty:
                    guest_event_options = dict(zip(events_list_df['event_name'], events_list_df['event_id']))
                    selected_event_name = st.selectbox("Chọn sự kiện tham gia", list(guest_event_options.keys()))
                else:
                    st.info("Bạn đã tham gia tất cả sự kiện hiện có.")
                    guest_event_options = {}
                    selected_event_name = None
                
            submit_reg = st.form_submit_button("Xác nhận Đăng ký")
            if submit_reg:
                if selected_event_name:
                    selected_event_id = guest_event_options[selected_event_name]
                    success, msg = create_registration(session, selected_event_id, guest_id)
                    if success:
                        st.session_state['success_msg'] = "🎉 " + msg
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Không có sự kiện nào để đăng ký.")

# 4. KIỂM TRA QUYỀN TẠO (create_events)
if has_permission('manage_event'):
    st.divider()
    st.subheader("➕ Thêm Sự kiện Mới")
    with st.form("add_event_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Tên sự kiện")
            date = st.date_input("Ngày tổ chức", min_value=datetime.date.today())
            time_start = st.time_input("Giờ bắt đầu")
            category_names = st.multiselect("Thể loại", category_options)
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
            category_ids = [category_mapping[c] for c in category_names]
            success, msg = create_event(session, name, start_dt, end_dt, venue_id, org_id, category_ids, price)
            if success:
                st.session_state['success_msg'] = msg
                st.rerun()
            else:
                st.error(msg)
else:
    # Nếu là Staff không có quyền tạo, có thể hiện lời nhắc
    st.info("💡 Lưu ý: Bạn chỉ có quyền xem, không có quyền thêm sự kiện mới.")

# 5. CHỈNH SỬA SỰ KIỆN
if has_permission('manage_event'):
    st.divider()
    st.subheader("✏️ Chỉnh sửa Sự kiện")

    edit_event_id = st.number_input("Nhập Event ID cần chỉnh sửa", min_value=1, step=1, key="edit_eid")
    load_btn = st.button("Tải thông tin sự kiện")

    if load_btn:
        event_df = get_event_by_id(session, edit_event_id)
        if event_df.empty:
            st.warning("Không tìm thấy sự kiện với ID này.")
        else:
            st.session_state['edit_event_data'] = event_df.iloc[0].to_dict()

    if 'edit_event_data' in st.session_state:
        data = st.session_state['edit_event_data']
        with st.form("edit_event_form"):
            col1, col2 = st.columns(2)
            with col1:
                edit_name = st.text_input("Tên sự kiện", value=str(data.get('event_name', '')))
                edit_date = st.date_input("Ngày tổ chức", value=pd.Timestamp(data['event_date']).date(), min_value=datetime.date(2000, 1, 1))
                edit_time_start = st.time_input("Giờ bắt đầu", value=pd.Timestamp(data['event_date']).time())
                edit_category_names = st.multiselect(
                    "Thể loại",
                    category_options,
                    default=[cat for cat in category_options if category_mapping[cat] in data.get('category_ids', [])]
                )
            with col2:
                edit_venue_id = st.number_input("Mã Địa điểm (Venue ID)", min_value=1, step=1, value=int(data['venue_id']))
                edit_org_id = st.number_input("Mã Ban tổ chức (Organizer ID)", min_value=1, step=1, value=int(data['organizer_id']))
                edit_time_end = st.time_input("Giờ kết thúc", value=pd.Timestamp(data['end_time']).time())
                edit_price = st.number_input("Giá vé cơ bản ($)", min_value=0.0, step=5.0, value=float(data['base_price']))
            update_btn = st.form_submit_button("Cập nhật sự kiện")
            if update_btn:
                start_dt = f"{edit_date} {edit_time_start}"
                end_dt = f"{edit_date} {edit_time_end}"
                edit_category_ids = [category_mapping[c] for c in edit_category_names]
                success, msg = update_event(session, int(data['event_id']), edit_name, start_dt, end_dt, edit_venue_id, edit_org_id, edit_category_ids, edit_price)
                if success:
                    st.session_state['success_msg'] = msg
                    del st.session_state['edit_event_data']
                    st.rerun()
                else:
                    st.error(msg)

session.close()
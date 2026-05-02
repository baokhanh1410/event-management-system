import streamlit as st
import pandas as pd
from src.connection import get_session
from src.crud import (
    get_events_list, get_guests_list,
    get_registrations_by_event, create_registration,
    check_in_guest, get_attendance_summary,
    get_guest_registered_events, get_guest_own_registrations
)
from src.auth import has_permission

# ============================================================
# BẢO MẬT: Kiểm tra đăng nhập
# ============================================================
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Vui lòng đăng nhập ở trang chủ trước khi truy cập!")
    st.stop()

st.title("📋 Quản lý Điểm danh & Đăng ký")
session = get_session()
if session is None:
    st.error("❌ Không thể kết nối database. Vui lòng kiểm tra cấu hình.")
    st.stop()

# Hiển thị thông báo thành công từ lần rerun trước
if 'att_success_msg' in st.session_state:
    st.success(st.session_state['att_success_msg'])
    del st.session_state['att_success_msg']

# ============================================================
# LOAD DỮ LIỆU DÙNG CHUNG
# ============================================================
user_role = st.session_state.user_info.get('role')
current_guest_id = st.session_state.user_info.get('guest_id')

if user_role == 'Guest' and current_guest_id:
    events_df = get_guest_registered_events(session, current_guest_id)
else:
    events_df = get_events_list(session)

event_options = {f"{row['event_id']} - {row['event_name']}": row['event_id'] for _, row in events_df.iterrows()} if not events_df.empty else {}

# ============================================================
# TABS LAYOUT
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs(["📋 Danh sách Đăng ký", "✅ Check-in", "➕ Đăng ký mới", "📊 Thống kê"])

# ============================================================
# TAB 1: DANH SÁCH ĐĂNG KÝ
# ============================================================
with tab1:
    st.subheader("Danh sách đăng ký theo sự kiện")

    if not event_options:
        st.info("Chưa có sự kiện nào trong hệ thống.")
    else:
        selected_event_1 = st.selectbox(
            "Chọn sự kiện", options=list(event_options.keys()), key="tab1_event"
        )
        event_id = event_options[selected_event_1]

        if user_role == 'Guest' and current_guest_id:
            reg_df = get_guest_own_registrations(session, event_id, current_guest_id)
        else:
            reg_df = get_registrations_by_event(session, event_id)
        if reg_df.empty:
            st.info("Chưa có đăng ký nào cho sự kiện này.")
        else:
            # Format cột attendance_status cho dễ đọc
            display_df = reg_df.copy()
            display_df['attendance_status'] = display_df['attendance_status'].map(
                {1: '✅ Đã check-in', 0: '⏳ Chưa check-in'}
            )
            display_df.columns = ['Reg ID', 'Tên khách', 'Email', 'SĐT', 'Ngày ĐK', 'Trạng thái', 'Đánh giá']
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Thống kê nhanh
            total = len(reg_df)
            checked = reg_df['attendance_status'].sum()
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Tổng đăng ký", total)
            col_b.metric("Đã check-in", int(checked))
            col_c.metric("Tỉ lệ", f"{(checked/total*100):.1f}%" if total > 0 else "0%")

# ============================================================
# TAB 2: CHECK-IN KHÁCH MỜI (Phân quyền: attendance_checkin)
# ============================================================
with tab2:
    if not has_permission('attendance_checkin'):
        st.info("💡 Bạn không có quyền thực hiện check-in.")
    elif not event_options:
        st.info("Chưa có sự kiện nào trong hệ thống.")
    else:
        st.subheader("Check-in khách mời")
        selected_event_2 = st.selectbox(
            "Chọn sự kiện", options=list(event_options.keys()), key="tab2_event"
        )
        event_id_2 = event_options[selected_event_2]

        # Lấy danh sách khách CHƯA check-in
        reg_df_2 = get_registrations_by_event(session, event_id_2)
        pending = reg_df_2[reg_df_2['attendance_status'] == 0] if not reg_df_2.empty else pd.DataFrame()

        if pending.empty:
            st.success("🎉 Tất cả khách đã check-in hoặc chưa có đăng ký!")
        else:
            st.write(f"**{len(pending)} khách chưa check-in:**")
            for idx, row in pending.iterrows():
                col_name, col_btn = st.columns([3, 1])
                col_name.write(f"🧑 **{row['guest_name']}** ({row['guest_email']})")
                if col_btn.button("✅ Check-in", key=f"checkin_{row['registration_id']}"):
                    success, msg = check_in_guest(session, int(row['registration_id']))
                    if success:
                        st.session_state['att_success_msg'] = f"✅ {row['guest_name']} — {msg}"
                        st.rerun()
                    else:
                        st.error(msg)

# ============================================================
# TAB 3: ĐĂNG KÝ MỚI (Phân quyền: register_guests)
# ============================================================
with tab3:
    if not has_permission('register_guests'):
        st.info("💡 Bạn không có quyền đăng ký khách mời.")
    elif not event_options:
        st.info("Chưa có sự kiện nào trong hệ thống.")
    else:
        st.subheader("Đăng ký khách mời cho sự kiện")
        guests_df = get_guests_list(session)
        guest_options = {f"{row['guest_id']} - {row['guest_name']}": row['guest_id'] for _, row in guests_df.iterrows()} if not guests_df.empty else {}

        if not guest_options:
            st.warning("Chưa có khách mời nào trong hệ thống.")
        else:
            with st.form("register_guest_form"):
                selected_event_3 = st.selectbox(
                    "Chọn sự kiện", options=list(event_options.keys()), key="tab3_event"
                )
                selected_guest = st.selectbox(
                    "Chọn khách mời", options=list(guest_options.keys()), key="tab3_guest"
                )
                submit_reg = st.form_submit_button("📝 Đăng ký")

                if submit_reg:
                    eid = event_options[selected_event_3]
                    gid = guest_options[selected_guest]
                    success, msg = create_registration(session, eid, gid)
                    if success:
                        st.session_state['att_success_msg'] = msg
                        st.rerun()
                    else:
                        st.error(msg)

# ============================================================
# TAB 4: THỐNG KÊ ATTENDANCE
# ============================================================
with tab4:
    if user_role == 'Guest':
        st.info("💡 Bạn không có quyền xem thống kê.")
    else:
        st.subheader("Thống kê tỉ lệ tham dự")

        try:
            summary_df = get_attendance_summary(session)
            if summary_df.empty:
                st.info("Chưa có dữ liệu thống kê.")
            else:
                # Metrics cards tổng quan
                col1, col2, col3 = st.columns(3)
                col1.metric("🎪 Tổng sự kiện", len(summary_df))
                col2.metric("📝 Tổng đăng ký", int(summary_df['total_registrations'].sum()))
                avg_rate = summary_df.loc[summary_df['total_registrations'] > 0, 'attendance_rate'].mean()
                col3.metric("📊 Tỉ lệ tham dự", f"{avg_rate:.1f}%" if pd.notna(avg_rate) else "N/A")

                # Bảng chi tiết
                st.divider()
                display_summary = summary_df.copy()
                display_summary['attendance_rate'] = display_summary['attendance_rate'].apply(lambda x: f"{x:.1f}%")
                display_summary.columns = ['Event ID', 'Tên sự kiện', 'Ngày', 'Địa điểm', 'Tổng ĐK', 'Đã check-in', 'Tỉ lệ (%)']
                st.dataframe(display_summary, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Lỗi khi tải thống kê: {e}")

# ============================================================
# ĐÓNG SESSION
# ============================================================
session.close()

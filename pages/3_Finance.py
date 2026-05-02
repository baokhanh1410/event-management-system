import streamlit as st
import pandas as pd
from src.connection import get_session
from src.crud import get_finance_summary, get_finance_by_event, update_finance, get_events_list
from src.auth import has_permission

# ============================================================
# BẢO MẬT: Kiểm tra đăng nhập & phân quyền
# ============================================================
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Vui lòng đăng nhập ở trang chủ trước khi truy cập!")
    st.stop()

if not has_permission('manage_finance') and not has_permission('view_analytics'):
    st.error("🚫 Bạn không có quyền truy cập trang Tài chính.")
    st.stop()

st.title("💰 Quản lý Tài chính Sự kiện")
session = get_session()
if session is None:
    st.error("❌ Không thể kết nối database. Vui lòng kiểm tra cấu hình.")
    st.stop()

# Hiển thị thông báo thành công từ lần rerun trước
if 'fin_success_msg' in st.session_state:
    st.success(st.session_state['fin_success_msg'])
    del st.session_state['fin_success_msg']

# ============================================================
# LOAD DỮ LIỆU TÀI CHÍNH
# ============================================================
try:
    finance_df = get_finance_summary(session)
except Exception as e:
    st.error(f"Lỗi khi tải dữ liệu tài chính: {e}")
    session.close()
    st.stop()

# ============================================================
# TABS LAYOUT
# ============================================================
if has_permission('manage_finance'):
    tab1, tab2, tab3 = st.tabs(["📊 Tổng quan", "📋 Chi tiết", "✏️ Chỉnh sửa"])
else:
    tab1, tab2 = st.tabs(["📊 Tổng quan", "📋 Chi tiết"])

# ============================================================
# TAB 1: TỔNG QUAN — KPI Cards & Biểu đồ
# ============================================================
with tab1:
    st.subheader("Tổng quan Tài chính")

    if finance_df.empty:
        st.info("Chưa có dữ liệu tài chính trong hệ thống.")
    else:
        # --- KPI Metric Cards ---
        total_budget = finance_df['planned_budget'].sum()
        total_cost = finance_df['actual_cost'].sum()
        total_revenue = finance_df['revenue'].sum()
        total_profit = finance_df['profit'].sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📋 Tổng Ngân sách", f"${total_budget:,.2f}")
        col2.metric("💸 Tổng Chi phí", f"${total_cost:,.2f}")
        col3.metric("💵 Tổng Doanh thu", f"${total_revenue:,.2f}")
        col4.metric(
            "📈 Lợi nhuận ròng",
            f"${total_profit:,.2f}",
            delta=f"{'Lãi' if total_profit >= 0 else 'Lỗ'}",
            delta_color="normal" if total_profit >= 0 else "inverse"
        )

        st.divider()

        # --- Bar Chart: Planned vs Actual (Top 15 events) ---
        st.subheader("So sánh Ngân sách Dự kiến vs Chi phí Thực tế")
        top_n = min(15, len(finance_df))
        chart_df = finance_df.nlargest(top_n, 'planned_budget')[['event_name', 'planned_budget', 'actual_cost']].copy()
        chart_df = chart_df.set_index('event_name')
        chart_df.columns = ['Ngân sách Dự kiến', 'Chi phí Thực tế']
        st.bar_chart(chart_df)

        st.divider()

        # --- Bar Chart: Revenue vs Cost ---
        st.subheader("So sánh Doanh thu vs Chi phí")
        rev_chart = finance_df.nlargest(top_n, 'revenue')[['event_name', 'revenue', 'actual_cost']].copy()
        rev_chart = rev_chart.set_index('event_name')
        rev_chart.columns = ['Doanh thu', 'Chi phí Thực tế']
        st.bar_chart(rev_chart)

        # --- Thống kê tổng hợp ---
        st.divider()
        st.subheader("Thống kê tổng hợp")
        stat_col1, stat_col2, stat_col3 = st.columns(3)

        profitable_count = (finance_df['profit'] > 0).sum()
        loss_count = (finance_df['profit'] <= 0).sum()
        avg_variance = finance_df['variance'].mean()

        stat_col1.metric("✅ Sự kiện có lãi", f"{profitable_count}/{len(finance_df)}")
        stat_col2.metric("❌ Sự kiện lỗ/hòa", f"{loss_count}/{len(finance_df)}")
        stat_col3.metric("📊 Variance TB", f"${avg_variance:,.2f}")

# ============================================================
# TAB 2: CHI TIẾT — Bảng dữ liệu đầy đủ
# ============================================================
with tab2:
    st.subheader("Chi tiết Tài chính theo Sự kiện")

    if finance_df.empty:
        st.info("Chưa có dữ liệu tài chính.")
    else:
        display_df = finance_df[['event_id', 'event_name', 'event_date', 'status',
                                  'planned_budget', 'actual_cost', 'revenue', 'variance', 'profit']].copy()
        display_df.columns = ['ID', 'Tên sự kiện', 'Ngày', 'Trạng thái',
                               'Ngân sách DK ($)', 'Chi phí TT ($)', 'Doanh thu ($)',
                               'Chênh lệch ($)', 'Lợi nhuận ($)']

        # Highlight: dùng Pandas Styler
        def highlight_finance(val):
            if isinstance(val, (int, float)):
                if val < 0:
                    return 'color: #ff4b4b'
                elif val > 0:
                    return 'color: #21c354'
            return ''

        styled_df = display_df.style.map(
            highlight_finance, subset=['Chênh lệch ($)', 'Lợi nhuận ($)']
        )
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # --- Tổng kết cuối bảng ---
        st.divider()
        sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
        sum_col1.metric("Tổng Ngân sách", f"${display_df['Ngân sách DK ($)'].sum():,.2f}")
        sum_col2.metric("Tổng Chi phí", f"${display_df['Chi phí TT ($)'].sum():,.2f}")
        sum_col3.metric("Tổng Doanh thu", f"${display_df['Doanh thu ($)'].sum():,.2f}")
        sum_col4.metric("Tổng Lợi nhuận", f"${display_df['Lợi nhuận ($)'].sum():,.2f}")

# ============================================================
# TAB 3: CHỈNH SỬA — Chỉ Admin (manage_finance)
# ============================================================
if has_permission('manage_finance'):
    with tab3:
        st.subheader("Chỉnh sửa Tài chính Sự kiện")

        events_list = get_events_list(session)
        if events_list.empty:
            st.info("Chưa có sự kiện nào.")
        else:
            event_options = {f"{row['event_id']} - {row['event_name']}": row['event_id']
                            for _, row in events_list.iterrows()}

            selected = st.selectbox("Chọn sự kiện", list(event_options.keys()), key="fin_event_select")
            selected_eid = event_options[selected]

            load_btn = st.button("📥 Tải thông tin tài chính")
            if load_btn:
                fin_data = get_finance_by_event(session, selected_eid)
                if fin_data:
                    st.session_state['edit_finance'] = fin_data
                else:
                    st.warning("Sự kiện này chưa có dữ liệu tài chính.")

            if 'edit_finance' in st.session_state:
                data = st.session_state['edit_finance']
                with st.form("edit_finance_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_budget = st.number_input("Ngân sách Dự kiến ($)",
                                                      min_value=0.0, step=100.0,
                                                      value=data['planned_budget'])
                    with col2:
                        new_cost = st.number_input("Chi phí Thực tế ($)",
                                                    min_value=0.0, step=100.0,
                                                    value=data['actual_cost'])

                    st.caption("💡 Doanh thu được tính tự động: Số khách check-in × Giá vé cơ bản")

                    update_btn = st.form_submit_button("💾 Cập nhật")
                    if update_btn:
                        success, msg = update_finance(session, data['finance_id'],
                                                       new_budget, new_cost)
                        if success:
                            st.session_state['fin_success_msg'] = msg
                            del st.session_state['edit_finance']
                            st.rerun()
                        else:
                            st.error(msg)

# ============================================================
# ĐÓNG SESSION
# ============================================================
session.close()

import streamlit as st
import pandas as pd
from src.connection import get_session
from src.crud import get_finance_summary, get_finance_by_event, update_finance, get_events_list
from src.auth import has_permission

# ============================================================
# SECURITY & INITIALIZATION
# ============================================================

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login on the home page before accessing this section!")
    st.stop()

if not has_permission('manage_finance') and not has_permission('view_analytics'):
    st.error("🚫 You do not have permission to access the Finance page.")
    st.stop()

st.title("💰 Event Finance Management")
session = get_session()
if session is None:
    st.error("❌ Cannot connect to the database. Please check your configuration.")
    st.stop()

# Display success messages from the previous rerun
if 'fin_success_msg' in st.session_state:
    st.success(st.session_state['fin_success_msg'])
    del st.session_state['fin_success_msg']

# ============================================================
# LOAD FINANCE DATA
# ============================================================

try:
    finance_df = get_finance_summary(session)
except Exception as e:
    st.error(f"Error loading finance data: {e}")
    session.close()
    st.stop()

# ============================================================
# TABS LAYOUT
# ============================================================

if has_permission('manage_finance'):
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📋 Details", "✏️ Edit"])
else:
    tab1, tab2 = st.tabs(["📊 Overview", "📋 Details"])

# ============================================================
# TAB 1: OVERVIEW — KPI Cards & Charts
# ============================================================

with tab1:
    st.subheader("Financial Overview")

    if finance_df.empty:
        st.info("There is no financial data in the system yet.")
    else:
        # --- KPI Metric Cards ---
        total_budget = finance_df['planned_budget'].sum()
        total_cost = finance_df['actual_cost'].sum()
        total_revenue = finance_df['revenue'].sum()
        total_profit = finance_df['profit'].sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📋 Total Planned Budget", f"${total_budget:,.2f}")
        col2.metric("💸 Total Actual Cost", f"${total_cost:,.2f}")
        col3.metric("💵 Total Revenue", f"${total_revenue:,.2f}")
        col4.metric(
            "📈 Net Profit",
            f"${total_profit:,.2f}",
            delta=f"{'Profit' if total_profit >= 0 else 'Loss'}",
            delta_color="normal" if total_profit >= 0 else "inverse"
        )

        st.divider()

        # --- Bar Chart: Planned vs Actual (Top 15 events) ---
        st.subheader("Planned Budget vs Actual Cost Comparison")
        top_n = min(15, len(finance_df))
        chart_df = finance_df.nlargest(top_n, 'planned_budget')[['event_name', 'planned_budget', 'actual_cost']].copy()
        chart_df = chart_df.set_index('event_name')
        chart_df.columns = ['Planned Budget', 'Actual Cost']
        st.bar_chart(chart_df)

        st.divider()

        # --- Bar Chart: Revenue vs Cost ---
        st.subheader("Revenue vs Actual Cost Comparison")
        rev_chart = finance_df.nlargest(top_n, 'revenue')[['event_name', 'revenue', 'actual_cost']].copy()
        rev_chart = rev_chart.set_index('event_name')
        rev_chart.columns = ['Revenue', 'Actual Cost']
        st.bar_chart(rev_chart)

        # --- Aggregate Statistics ---
        st.divider()
        st.subheader("Aggregate Statistics")
        stat_col1, stat_col2, stat_col3 = st.columns(3)

        profitable_count = (finance_df['profit'] > 0).sum()
        loss_count = (finance_df['profit'] <= 0).sum()
        avg_variance = finance_df['variance'].mean()

        stat_col1.metric("✅ Profitable Events", f"{profitable_count}/{len(finance_df)}")
        stat_col2.metric("❌ Loss/Breakeven Events", f"{loss_count}/{len(finance_df)}")
        stat_col3.metric("📊 Avg Variance", f"${avg_variance:,.2f}")

# ============================================================
# TAB 2: DETAILS — Full Data Table
# ============================================================

with tab2:
    st.subheader("Financial Details by Event")

    if finance_df.empty:
        st.info("There is no financial data yet.")
    else:
        display_df = finance_df[['event_id', 'event_name', 'event_date', 'status',
                                  'planned_budget', 'actual_cost', 'revenue', 'variance', 'profit']].copy()
        display_df.columns = ['ID', 'Event Name', 'Date', 'Status',
                               'Planned Budget ($)', 'Actual Cost ($)', 'Revenue ($)',
                               'Variance ($)', 'Profit ($)']

        # Highlight using Pandas Styler
        def highlight_finance(val):
            if isinstance(val, (int, float)):
                if val < 0:
                    return 'color: #ff4b4b'
                elif val > 0:
                    return 'color: #21c354'
            return ''

        styled_df = display_df.style.map(
            highlight_finance, subset=['Variance ($)', 'Profit ($)']
        )
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # --- Bottom Table Summary ---
        st.divider()
        sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
        sum_col1.metric("Total Budget", f"${display_df['Planned Budget ($)'].sum():,.2f}")
        sum_col2.metric("Total Cost", f"${display_df['Actual Cost ($)'].sum():,.2f}")
        sum_col3.metric("Total Revenue", f"${display_df['Revenue ($)'].sum():,.2f}")
        sum_col4.metric("Total Profit", f"${display_df['Profit ($)'].sum():,.2f}")

# ============================================================
# TAB 3: EDIT — Admins Only (Permissions Required)
# ============================================================

if has_permission('manage_finance'):
    with tab3:
        st.subheader("Edit Event Finance")

        events_list = get_events_list(session)
        if events_list.empty:
            st.info("There are no events yet.")
        else:
            event_options = {f"{row['event_id']} - {row['event_name']}": row['event_id']
                            for _, row in events_list.iterrows()}

            selected = st.selectbox("Select Event", list(event_options.keys()), key="fin_event_select")
            selected_eid = event_options[selected]

            load_btn = st.button("📥 Load Finance Information")
            if load_btn:
                fin_data = get_finance_by_event(session, selected_eid)
                if fin_data:
                    st.session_state['edit_finance'] = fin_data
                else:
                    st.warning("This event does not have financial data yet.")

            if 'edit_finance' in st.session_state:
                data = st.session_state['edit_finance']
                with st.form("edit_finance_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_budget = st.number_input("Planned Budget ($)",
                                                      min_value=0.0, step=100.0,
                                                      value=data['planned_budget'])
                    with col2:
                        new_cost = st.number_input("Actual Cost ($)",
                                                    min_value=0.0, step=100.0,
                                                    value=data['actual_cost'])

                    st.caption("💡 Revenue is calculated automatically: Checked-in Guests × Base Price")

                    update_btn = st.form_submit_button("💾 Update")
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
# SESSION CLEANUP
# ============================================================

session.close()

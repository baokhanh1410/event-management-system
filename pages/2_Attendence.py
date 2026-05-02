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
# SECURITY & INITIALIZATION
# ============================================================

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login on the home page before accessing this section!")
    st.stop()

st.title("📋 Attendance & Registration Management")
session = get_session()
if session is None:
    st.error("❌ Cannot connect to the database. Please check your configuration.")
    st.stop()

# Display success messages from the previous rerun
if 'att_success_msg' in st.session_state:
    st.success(st.session_state['att_success_msg'])
    del st.session_state['att_success_msg']

# ============================================================
# LOAD SHARED DATA
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

tab1, tab2, tab3, tab4 = st.tabs(["📋 Registration List", "✅ Check-in", "➕ New Registration", "📊 Statistics"])

# ============================================================
# TAB 1: REGISTRATION LIST
# ============================================================

with tab1:
    st.subheader("Registration List by Event")

    if not event_options:
        st.info("There are no events in the system yet.")
    else:
        selected_event_1 = st.selectbox(
            "Select Event", options=list(event_options.keys()), key="tab1_event"
        )
        event_id = event_options[selected_event_1]

        if user_role == 'Guest' and current_guest_id:
            reg_df = get_guest_own_registrations(session, event_id, current_guest_id)
        else:
            reg_df = get_registrations_by_event(session, event_id)
        if reg_df.empty:
            st.info("No registrations found for this event.")
        else:
            # Format attendance_status for readability
            display_df = reg_df.copy()
            display_df['attendance_status'] = display_df['attendance_status'].map(
                {1: '✅ Checked-in', 0: '⏳ Pending'}
            )
            display_df.columns = ['Reg ID', 'Guest Name', 'Email', 'Phone', 'Reg Date', 'Status', 'Rating']
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Quick Statistics
            total = len(reg_df)
            checked = reg_df['attendance_status'].sum()
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Total Registrations", total)
            col_b.metric("Checked-in", int(checked))
            col_c.metric("Rate", f"{(checked/total*100):.1f}%" if total > 0 else "0%")

# ============================================================
# TAB 2: GUEST CHECK-IN (Permissions Required)
# ============================================================

with tab2:
    if not has_permission('attendance_checkin'):
        st.info("💡 You do not have permission to perform check-ins.")
    elif not event_options:
        st.info("There are no events in the system yet.")
    else:
        st.subheader("Guest Check-in")
        selected_event_2 = st.selectbox(
            "Select Event", options=list(event_options.keys()), key="tab2_event"
        )
        event_id_2 = event_options[selected_event_2]

        # Get list of guests who haven't checked in yet
        reg_df_2 = get_registrations_by_event(session, event_id_2)
        pending = reg_df_2[reg_df_2['attendance_status'] == 0] if not reg_df_2.empty else pd.DataFrame()

        if pending.empty:
            st.success("🎉 All guests have checked in or there are no registrations!")
        else:
            st.write(f"**{len(pending)} guests pending check-in:**")
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
# TAB 3: NEW REGISTRATION (Permissions Required)
# ============================================================

with tab3:
    if not has_permission('register_guests'):
        st.info("💡 You do not have permission to register guests.")
    elif not event_options:
        st.info("There are no events in the system yet.")
    else:
        st.subheader("Register Guest for Event")
        guests_df = get_guests_list(session)
        guest_options = {f"{row['guest_id']} - {row['guest_name']}": row['guest_id'] for _, row in guests_df.iterrows()} if not guests_df.empty else {}

        if not guest_options:
            st.warning("There are no guests in the system yet.")
        else:
            with st.form("register_guest_form"):
                selected_event_3 = st.selectbox(
                    "Select Event", options=list(event_options.keys()), key="tab3_event"
                )
                selected_guest = st.selectbox(
                    "Select Guest", options=list(guest_options.keys()), key="tab3_guest"
                )
                submit_reg = st.form_submit_button("📝 Register")

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
# TAB 4: ATTENDANCE STATISTICS
# ============================================================

with tab4:
    if user_role == 'Guest':
        st.info("💡 You do not have permission to view statistics.")
    else:
        st.subheader("Attendance Rate Statistics")

        try:
            summary_df = get_attendance_summary(session)
            if summary_df.empty:
                st.info("No statistical data available yet.")
            else:
                # Metrics cards overview
                col1, col2, col3 = st.columns(3)
                col1.metric("🎪 Total Events", len(summary_df))
                col2.metric("📝 Total Registrations", int(summary_df['total_registrations'].sum()))
                avg_rate = summary_df.loc[summary_df['total_registrations'] > 0, 'attendance_rate'].mean()
                col3.metric("📊 Avg Attendance Rate", f"{avg_rate:.1f}%" if pd.notna(avg_rate) else "N/A")

                # Detailed Table
                st.divider()
                display_summary = summary_df.copy()
                display_summary['attendance_rate'] = display_summary['attendance_rate'].apply(lambda x: f"{x:.1f}%")
                display_summary.columns = ['Event ID', 'Event Name', 'Date', 'Venue', 'Total Reg', 'Checked-in', 'Rate (%)']
                st.dataframe(display_summary, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error loading statistics: {e}")

# ============================================================
# SESSION CLEANUP
# ============================================================

session.close()

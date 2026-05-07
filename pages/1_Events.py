import streamlit as st
import datetime
import pandas as pd
from src.connection import get_session
from src.crud import get_all_events, create_event, get_event_by_id, update_event, get_categories, create_registration, get_guest_profile, get_events_list, get_guest_registered_events, get_available_events_for_guest
from src.auth import has_permission
from src.ml_models import get_recommended_events

# ============================================================
# SECURITY & INITIALIZATION
# ============================================================

# Check login status
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login on the home page before accessing this section!")
    st.stop()

st.title("📅 Event Schedule Management")
session = get_session()
if session is None:
    st.error("❌ Cannot connect to the database. Please check your configuration.")
    st.stop()

# Display success messages from the previous rerun
if 'success_msg' in st.session_state:
    st.success(st.session_state['success_msg'])
    del st.session_state['success_msg']

# Load categories once
categories_df = get_categories(session)
category_options = categories_df['category_name'].tolist()
category_mapping = dict(zip(categories_df['category_name'], categories_df['category_id']))

# ============================================================
# EVENT LISTING
# ============================================================

st.subheader("Event List")
try:
    events_df = get_all_events(session)
    if not events_df.empty:
        display_df = events_df.copy()
        display_df = display_df[['event_id', 'event_name', 'categories', 'event_date', 'venue_name', 'organizer_name', 'status', 'base_price']]
        display_df.columns = ['ID', 'Event Name', 'Category', 'Date', 'Venue', 'Organizer', 'Status', 'Base Price ($)']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("There are no events in the system yet.")
except Exception as e:
    st.error(f"Error loading list: {e}")

# ============================================================
# GUEST REGISTRATION & RECOMMENDATIONS
# ============================================================

if st.session_state.user_info.get('role') == 'Guest' and st.session_state.user_info.get('guest_id'):
    guest_id = st.session_state.user_info['guest_id']
    
    # --- My Events Section ---
    st.divider()
    st.subheader("📌 Events I Have Joined")
    try:
        my_events_df = get_guest_registered_events(session, guest_id)
        if not my_events_df.empty:
            my_display = my_events_df[['event_id', 'event_name', 'categories', 'event_date', 'venue_name', 'organizer_name', 'status', 'base_price']].copy()
            my_display.columns = ['ID', 'Event Name', 'Category', 'Date', 'Venue', 'Organizer', 'Status', 'Base Price ($)']
            st.dataframe(my_display, use_container_width=True, hide_index=True)
        else:
            st.info("You haven't registered for any events. Check out the Recommendations below to join!")
    except Exception as e:
        st.error(f"Error loading list: {e}")
    
    # --- XGBoost Recommendation Section ---
    st.divider()
    st.subheader("🌟 Recommendations Just For You")
    
    def fetch_recommendations(gid):
        temp_session = get_session()
        try:
            return get_recommended_events(temp_session, gid)
        finally:
            temp_session.close()

    with st.spinner("Finding suitable events..."):
        try:
            rec_df = fetch_recommendations(guest_id)
        except Exception as e:
            st.error(f"Cannot load recommendations: {e}")
            rec_df = pd.DataFrame()
            
    if not rec_df.empty:
        display_rec = rec_df[['event_name', 'categories', 'event_date', 'venue_name', 'base_price']].copy()
        display_rec.columns = ['Event Name', 'Category', 'Date', 'Venue', 'Base Price ($)']
        st.dataframe(display_rec, use_container_width=True, hide_index=True)
    else:
        st.info("There are currently no new recommendations for you.")

    # --- Event Registration Form ---
    st.divider()
    st.subheader("🎯 Register for an Event")
    profile = get_guest_profile(session, guest_id)
    
    if profile:
        with st.form("guest_registration_form"):
            st.info("Your information has been filled in automatically.")
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Full Name", value=profile['name'], disabled=True)
                st.text_input("Email", value=profile['email'], disabled=True)
            with col2:
                st.text_input("Phone Number", value=profile['phone'], disabled=True)
                events_list_df = get_available_events_for_guest(session, guest_id)
                if not events_list_df.empty:
                    guest_event_options = dict(zip(events_list_df['event_name'], events_list_df['event_id']))
                    selected_event_name = st.selectbox("Select an event to join", list(guest_event_options.keys()))
                else:
                    st.info("You have joined all available events.")
                    guest_event_options = {}
                    selected_event_name = None
                
            submit_reg = st.form_submit_button("Confirm Registration")
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
                    st.error("There are no events available for registration.")

# ============================================================
# ADD NEW EVENT (Permissions Required)
# ============================================================

if has_permission('manage_event'):
    st.divider()
    st.subheader("➕ Add New Event")
    with st.form("add_event_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Event Name")
            date = st.date_input("Event Date", min_value=datetime.date.today())
            time_start = st.time_input("Start Time")
            category_names = st.multiselect("Category", category_options)
        with col2:
            venue_id = st.number_input("Venue ID", min_value=1, step=1)
            org_id = st.number_input("Organizer ID", min_value=1, step=1)
            time_end = st.time_input("End Time")
            price = st.number_input("Base Price ($)", min_value=0.0, step=5.0)
        submit_btn = st.form_submit_button("Save Event")
        if submit_btn:
            # Format precise time for MySQL DATETIME
            start_dt = f"{date} {time_start}"
            end_dt = f"{date} {time_end}"
            # Call CRUD to process (errors caught via Trigger checking for schedule conflicts)
            category_ids = [category_mapping[c] for c in category_names]
            success, msg = create_event(session, name, start_dt, end_dt, venue_id, org_id, category_ids, price)
            if success:
                st.session_state['success_msg'] = msg
                st.rerun()
            else:
                st.error(msg)
else:
    # If it's a Staff without create permission, show a reminder
    st.info("💡 Note: You only have permission to view, not to add new events.")

# ============================================================
# EDIT EVENT (Permissions Required)
# ============================================================

if has_permission('manage_event'):
    st.divider()
    st.subheader("✏️ Edit Event")

    edit_event_id = st.number_input("Enter Event ID to Edit", min_value=1, step=1, key="edit_eid")
    load_btn = st.button("Load Event Information")

    if load_btn:
        event_df = get_event_by_id(session, edit_event_id)
        if event_df.empty:
            st.warning("No event found with this ID.")
        else:
            st.session_state['edit_event_data'] = event_df.iloc[0].to_dict()

    if 'edit_event_data' in st.session_state:
        data = st.session_state['edit_event_data']
        with st.form("edit_event_form"):
            col1, col2 = st.columns(2)
            with col1:
                edit_name = st.text_input("Event Name", value=str(data.get('event_name', '')))
                edit_date = st.date_input("Event Date", value=pd.Timestamp(data['event_date']).date(), min_value=datetime.date(2000, 1, 1))
                edit_time_start = st.time_input("Start Time", value=pd.Timestamp(data['event_date']).time())
                edit_category_names = st.multiselect(
                    "Category",
                    category_options,
                    default=[cat for cat in category_options if category_mapping[cat] in data.get('category_ids', [])]
                )
            with col2:
                edit_venue_id = st.number_input("Venue ID", min_value=1, step=1, value=int(data['venue_id']))
                edit_org_id = st.number_input("Organizer ID", min_value=1, step=1, value=int(data['organizer_id']))
                edit_time_end = st.time_input("End Time", value=pd.Timestamp(data['end_time']).time())
                edit_price = st.number_input("Base Price ($)", min_value=0.0, step=5.0, value=float(data['base_price']))
            update_btn = st.form_submit_button("Update Event")
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

# ============================================================
# SESSION CLEANUP
# ============================================================

session.close()
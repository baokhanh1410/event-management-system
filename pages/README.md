# Pages Directory - UI Layer (Streamlit)

This directory contains the user interface pages for the Event Management System, built with [Streamlit](https://streamlit.io/). Each file represents a different page/tab within the application.

## Files and Functionality

### `0_Login.py`
This is the entry point of the application, handling user authentication and registration.
*   **Login Tab:** Allows existing users (Admin, Staff, or Guest) to authenticate securely. Uses `authenticate_user()` from `src.auth`.
*   **Guest Signup Tab:** Allows new users to create a "Guest" account. Uses `register_new_guest_user()` from `src.auth`.
*   **Session State:** Manages the user's login state and displays their details (User ID, Role, Guest ID) upon successful login.

### `1_Events.py`
This page is dedicated to Event scheduling and management. Features change dynamically based on the logged-in user's role.
*   **Public View:** Displays all available events in a dataframe (ID, Name, Category, Date, Venue, Organizer, Status, Price).
*   **Guest Features:** 
    *   **My Events:** Shows events the guest has successfully registered for.
    *   **Recommendations:** Uses the XGBoost Machine Learning model (`get_recommended_events` from `src.ml_models`) to suggest upcoming events based on the guest's profile.
    *   **Registration Form:** Allows guests to register for events.
*   **Admin/Staff Features (Create):** Form to create a new event (Name, Date, Category, Venue, Organizer, Times, Price). Uses `create_event()` from `src.crud`.
*   **Admin/Staff Features (Edit):** Form to update an existing event's details based on Event ID.

### `2_Attendence.py`
This page manages guest registrations and check-ins.
*   **Tab 1 - Registration List:** Displays the list of registered guests for a selected event. Guests can only see their own registrations.
*   **Tab 2 - Check-in:** Allows authorized staff (with `attendance_checkin` permission) to mark guests as "Checked-in" upon arrival.
*   **Tab 3 - New Registration:** Allows authorized staff to manually register a guest for an event.
*   **Tab 4 - Statistics:** Displays attendance metrics and check-in rates across different events (Admin/Staff only).

### `3_Finance.py`
This page handles the financial aspects of the events. Access is restricted to users with `manage_finance` or `view_analytics` permissions.
*   **Tab 1 - Overview:** Displays KPI cards (Total Budget, Cost, Revenue, Net Profit) and bar charts comparing planned budget vs. actual cost, and revenue vs. cost.
*   **Tab 2 - Details:** Shows a comprehensive data table with financial metrics per event. Highlights profit (green) and loss (red) using conditional formatting.
*   **Tab 3 - Edit:** Allows users with `manage_finance` permission to update the "Planned Budget" and "Actual Cost" for an event. (Revenue is automatically calculated based on check-ins).

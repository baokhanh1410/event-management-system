# Event Management System (EMS)

A comprehensive Event Management platform focusing on organizing, financial tracking, and utilizing Data Science to enhance user experience. Built with Streamlit, Python, MySQL, and XGBoost.

## Student Information
- **Name:** Nguyễn Bảo Khánh
- **ID:** 11247178
- **Class:** DS66B
- **University:** National Economics University (NEU)
- **Major:** Data Science
- **Subject:** Final Project - Introduction to Databases
- **Lecturer:** Trần Hùng - DatCom Lab

## Features
- **Event Lifecycle Management:** Create, edit, and coordinate events.
- **Registration & Attendance:** Guest registration and real-time check-in tracking.
- **Financial Tracking:** Monitor projected budget vs. actual costs.
- **Role-Based Access Control (RBAC):** Distinct permissions for Admin, Staff, Organizer and Guest.
- **ML Integration:** XGBoost-based recommendation system to suggest relevant events to users.
- **Database Optimization:** Index, Views, Triggers, Stored Procedures to optimize database performance and data integrity.

## Tech Stack
- **Frontend/UI:** Streamlit
- **Backend/Logic:** Python
- **Database:** MySQL
- **Data Science:** XGBoost, Scikit-Learn

## Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Database:**
   Ensure MySQL is running.
   Create .env file and add the following information:
   ```
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=your_host
   DB_PORT=your_port
   DB_NAME=event_management
   ```
   Running `python setup.py` (windows) or `./setup.py` (macos/linux) will setupp all the tables, data, users and permissions into the database.

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Default Users:**
   - Username: `admin` | Password: `admin123` | Role: Admin
   - Username: `staff01` | Password: `staff123` | Role: Staff
   - Username: `organizer01` | Password: `organizer123` | Role: Organizer
   - Username: `guest01` | Password: `guest123` | Role: Guest
   - Username: `guest02` | Password: `guest123` | Role: Guest
   - Username: `guest03` | Password: `guest123` | Role: Guest
   - Username: `guest04` | Password: `guest123` | Role: Guest
   - Username: `guest05` | Password: `guest123` | Role: Guest

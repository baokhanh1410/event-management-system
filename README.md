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

1. **Clone the repository:**
   ```bash
   git clone https://github.com/baokhanh1410/event-management-system
   ```

2. **Set up Virtual Environment (Recommended):**
   The use of virtual environments helps avoid library conflicts between projects.

   **Windows:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   **macOS/Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database:**
   Ensure MySQL is running.
   Create .env file at the root of the project and add the following information:
   ```
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=your_host
   DB_PORT=your_port
   DB_NAME=event_management
   ```
   Running `python setup.py` (windows) or `./setup.py` (macos/linux) will setup all the tables, data, users and permissions into the database.

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

6. **Default Users:**
| Username | Password | Role |
| :--- | :--- | :--- |
| `admin` | `admin123` | Admin |
| `staff01` | `staff123` | Staff |
| `organizer01` | `organizer123` | Organizer |
| `guest01` | `guest123` | Guest |
| `guest02` | `guest123` | Guest |
| `guest03` | `guest123` | Guest |
| `guest04` | `guest123` | Guest |
| `guest05` | `guest123` | Guest |

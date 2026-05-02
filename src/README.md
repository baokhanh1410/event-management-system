# Src Directory - Backend Logic & Utilities

This directory contains the core Python backend modules that handle database connections, data manipulation (CRUD), authentication, machine learning, and data generation.

## Files and Functionality

### `auth.py`
Handles all user authentication, authorization, and security features.
*   `hash_password()` & `verify_password()`: Utility functions utilizing `bcrypt` to securely hash and verify passwords.
*   `authenticate_user()`: Validates user credentials against the database and retrieves user details, role, and a list of authorized permissions.
*   `register_new_guest_user()`: Handles the registration flow for new "Guest" users, inserting records into both the `guests` and `users` tables securely.
*   `has_permission()`: Checks if the currently logged-in user possesses a specific permission required to perform an action or view a page.

### `connection.py`
Manages the SQLAlchemy connection to the MySQL database.
*   `get_db_engine()`: Reads database credentials from environment variables (`.env` file) and creates a singleton SQLAlchemy engine.
*   `get_session()`: Provides a SQLAlchemy session object (`Session()`) used by other modules to execute SQL queries and transactions.

### `crud.py`
Contains all Create, Read, Update, and Delete operations. It interacts directly with the database using SQLAlchemy raw text queries and Pandas.
*   **Event Management:** Functions like `get_all_events()`, `create_event()`, `get_event_by_id()`, and `update_event()` to manage the lifecycle of events.
*   **Attendance & Registration:** Functions like `get_available_events_for_guest()`, `get_registrations_by_event()`, `create_registration()`, and `check_in_guest()` (which calls the stored procedure) to handle guest participation.
*   **Finance Management:** Functions like `get_finance_summary()`, `get_finance_by_event()`, and `update_finance()` to track budgets and costs.
*   **Data Preparation:** `get_data_for_recommendation()` gathers historical registration and attendance data used to train the machine learning model.

### `ml_models.py`
Contains the Machine Learning recommendation engine logic.
*   `preprocess_features()`: Prepares the dataset by applying One-Hot Encoding to event categories.
*   `train_xgboost_recommender()`: Trains an `XGBClassifier` (XGBoost) model using historical data to predict the likelihood of a guest attending an event.
*   `get_recommended_events()`: Uses the trained model to predict attendance probabilities for upcoming events the guest hasn't registered for yet, returning the top N recommendations.

### `sample_data.py`
A utility script used to generate dummy data for the application using the `Faker` library.
*   `generate_seed_data()`: Programmatically creates realistic sample data (venues, organizers, events, guests, etc.) and writes the corresponding `INSERT` SQL statements to `sql/seed.sql`. It also handles logic to make prices, budgets, and attendance rates somewhat realistic.
*   `insert_seed_data()`: Reads `sql/seed.sql` and executes the statements in batches to populate the database directly.

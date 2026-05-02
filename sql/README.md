# SQL Directory - Database Schema and Seed Data

This directory contains the SQL files used to define the database structure and populate it with initial sample data for the Event Management System.

## Files and Functionality

### `schema.sql`
This file contains the complete definition of the database schema, including tables, relationships, indexes, stored procedures, and views.
*   **Tables:** Defines tables for `events`, `categories`, `event_categories`, `guests`, `organizers`, `registrations`, `venues`, `event_finance`, `roles`, `permissions`, `role_permissions`, and `users`.
*   **Indexes & Foreign Keys:** Sets up necessary indexing for query optimization and foreign key constraints to maintain data integrity.
*   **Stored Procedures:**
    * `sp_check_in_guest`: Contains logic to securely mark a guest as "Checked-in" while preventing duplicate check-ins or checking in non-existent registrations.
*   **Views:**
    *   `vw_event_attendance_summary`: Aggregates registration and attendance data to provide a summary of total registrations and attendance rates per event.
    *   `vw_finance_summary`: Aggregates financial data, calculating actual costs and revenues based on check-ins and registrations, and computes the profit and variance for each event.

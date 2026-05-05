# SQL Directory - Database Schema and Seed Data

This directory contains the SQL files used to define the database structure and populate it with initial sample data for the Event Management System. This document details the architecture, tables, business logic, and optimization objects within the database.

---

## 1. Database Architecture Overview

The database is highly normalized and logically divided into three main modules for scalability and easy maintenance:
1. **Core Module:** Stores static and foundational data (Events, Categories, Guests, Organizers).
2. **Attendance & Finance Module:** Manages user interactions, attendance tracking, and financial metrics (Revenue, Costs).
3. **RBAC Module (Role-Based Access Control):** Implements a many-to-many security model for system access.

---

## 2. Detailed Table Structures

### 2.1. Core Tables
*   **`events`**: The central table storing event details.
    *   Uses an `ENUM` type for `status` ('Upcoming', 'Ongoing', 'Completed', 'Cancelled') to ensure data consistency.
    *   Stores `base_price` and establishes strict links to `venue_id` and `organizer_id`.
*   **`categories` & `event_categories`**: Manages event types. Since an event can have multiple categories and vice versa, `event_categories` acts as a junction table to resolve the many-to-many relationship.
*   **`guests`**: Stores attendee information (name, email, phone number).
*   **`organizers`**: Stores details about event partners and organizing entities.

### 2.2. Attendance & Finance Tables
*   **`venues`**: Stores location details. *(Note: The `capacity` column is specifically designed for future integration with triggers to prevent overbooking).*
*   **`registrations`**: Records guest event sign-ups.
    *   Tracks registration history, `attendance_status` (check-in state), and post-event `feedback_rating`.
*   **`event_finance`**: Manages the event budget. Stores `planned_budget` and `actual_cost` for automated financial reporting.

### 2.3. RBAC Tables (Role-Based Access Control)
The system uses a standard, highly secure Role-Based Access Control model:
*   **`users`**: Login credentials containing `password_hash` for security. It can be linked to a `guest_id` if the user is a registered guest.
*   **`roles`**: Defines user groups (e.g., Admin, Staff, Organizer, Guest).
*   **`permissions`**: Lists specific system actions (e.g., `create_event`, `delete_user`).
*   **`role_permissions`**: A junction table mapping multiple permissions to multiple roles.

---

## 3. Indexing Strategy (Query Optimization)

The system is optimized for query performance by applying `INDEX` on columns frequently used in `WHERE` clauses, filtering, or `ORDER BY`:

*   **Event Search Optimization:** `events_event_name_index` and `events_event_date_index`.
*   **Venue & Time Reporting:** The composite index `events_venue_id_event_date_index` drastically speeds up queries checking event schedules at specific venues on specific dates.
*   **Guest Search:** `guests_guest_name_index` and `guests_guest_email_index`.
*   **Attendance Tracking:** `registrations_registration_date_index` and `registrations_attendance_status_index` ensure lightning-fast data retrieval for statistical dashboards.
*   **Login & Authorization:** Indexes on `username` and `permission_name` to speed up authentication processes.

---

## 4. Stored Procedures (Business Logic)

### `sp_check_in_guest(p_registration_id)`
This stored procedure encapsulates the core business logic for guest check-ins at events securely at the database level.
*   **Data Integrity:** Validates if the `registration_id` exists. If not, it throws an error (`SIGNAL SQLSTATE '45000'`).
*   **Fraud & Duplicate Prevention:** Checks the current `attendance_status`. If the guest has already checked in, it blocks the process and returns an error to prevent duplicate entries.
*   **Execution:** Only when the above conditions are met does it update the `attendance_status` to `1`.

---

## 5. Views (Reporting & Analytics)

The database provides two pre-configured views acting as Data Marts, allowing the Frontend/Backend to retrieve complex reports easily without writing complex `JOIN` queries.

### `vw_event_attendance_summary`
Provides a real-time overview of event participation:
*   Aggregates event name, date, and venue.
*   Calculates **Total Registrations** (`total_registrations`).
*   Calculates **Actual Checked-in Guests** (`checked_in_count`).
*   Computes the **Attendance Rate** (`attendance_rate` in %) with safe division handling to prevent 'Divide by Zero' errors.

### `vw_finance_summary`
Automatically calculates Profit and Loss (P&L) metrics for each event based on registrations and check-ins:
*   **Actual Cost:** Calculated as (Checked-in Guests * `base_price`).
*   **Revenue:** Calculated as (Total Registrations * `base_price`).
*   **Variance:** `planned_budget` - `actual_cost` (The difference between the initial budget and costs incurred by attendees).
*   **Profit:** Automatically computed based on (`Revenue` - `Actual Cost`).

---

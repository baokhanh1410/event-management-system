-- ============================================================
-- CORE TABLES
-- ============================================================

-- events
CREATE TABLE `events`(
    `event_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `event_name` VARCHAR(255) NOT NULL,
    `event_date` DATETIME NOT NULL,
    `end_time` DATETIME NOT NULL,
    `venue_id` BIGINT UNSIGNED NOT NULL,
    `status` ENUM('Upcoming', 'Ongoing', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Upcoming',
    `base_price` DECIMAL(8, 2) NOT NULL,
    `organizer_id` BIGINT UNSIGNED NOT NULL
);
ALTER TABLE `events` ADD INDEX `events_event_name_index`(`event_name`);
ALTER TABLE `events` ADD INDEX `events_event_date_index`(`event_date`);
ALTER TABLE `events` ADD INDEX `events_venue_id_event_date_index`(`venue_id`, `event_date`);
ALTER TABLE `events` ADD INDEX `events_venue_id_index`(`venue_id`);

-- categories
CREATE TABLE `categories`(
    `category_id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `category_name` VARCHAR(50) NOT NULL
);

-- event_categories
CREATE TABLE `event_categories`(
    `event_id` BIGINT UNSIGNED NOT NULL,
    `category_id` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`event_id`, `category_id`)
);

-- guests
CREATE TABLE `guests`(
    `guest_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `guest_name` VARCHAR(255) NOT NULL,
    `guest_email` VARCHAR(255) NOT NULL,
    `phone_number` VARCHAR(16) NOT NULL
);
ALTER TABLE `guests` ADD INDEX `guests_guest_name_index`(`guest_name`);
ALTER TABLE `guests` ADD INDEX `guests_guest_email_index`(`guest_email`);

-- organizers
CREATE TABLE `organizers`(
    `organizer_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `organizer_name` VARCHAR(255) NOT NULL,
    `address` VARCHAR(255) NOT NULL,
    `phone_number` VARCHAR(16) NOT NULL
);

-- ============================================================
-- ATTENDANCE & FINANCE TABLES
-- ============================================================

-- registrations
CREATE TABLE `registrations`(
    `registration_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `event_id` BIGINT UNSIGNED NOT NULL,
    `guest_id` BIGINT UNSIGNED NOT NULL,
    `registration_date` DATETIME NOT NULL,
    `attendance_status` BOOLEAN NOT NULL,
    `feedback_rating` INT NOT NULL
);
ALTER TABLE `registrations` ADD INDEX `registrations_registration_date_index`(`registration_date`);
ALTER TABLE `registrations` ADD INDEX `registrations_attendance_status_index`(`attendance_status`);

-- venues
CREATE TABLE `venues`(
    `venue_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `venue_name` VARCHAR(255) NOT NULL,
    `venue_address` VARCHAR(255) NOT NULL,
    `capacity` INT NOT NULL COMMENT 'Use for trigger'
);

-- event_finance
CREATE TABLE `event_finance`(
    `finance_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `event_id` BIGINT UNSIGNED NOT NULL,
    `planned_budget` DECIMAL(15, 2) NOT NULL,
    `actual_cost` DECIMAL(15, 2) NOT NULL
);

-- ============================================================
-- RBAC TABLES (Role-Based Access Control)
-- ============================================================

-- roles 
CREATE TABLE `roles`(
    `role_id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `role_name` VARCHAR(50) NOT NULL
);

-- permissions
CREATE TABLE `permissions`(
    `permission_id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `permission_name` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL
);
ALTER TABLE `permissions` ADD INDEX `permissions_permission_name_index`(`permission_name`);

-- role_permissions (junction table for many-to-many RBAC)
CREATE TABLE `role_permissions`(
    `role_id` INT UNSIGNED NOT NULL,
    `permission_id` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`role_id`, `permission_id`)
);

-- users
CREATE TABLE `users`(
    `user_id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(255) NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `role_id` INT UNSIGNED NOT NULL,
    `guest_id` BIGINT UNSIGNED NULL
);
ALTER TABLE `users` ADD INDEX `users_username_index`(`username`);

-- ============================================================
-- FOREIGN KEYS
-- ============================================================

ALTER TABLE `users` ADD CONSTRAINT `users_role_id_foreign` FOREIGN KEY(`role_id`) REFERENCES `roles`(`role_id`);
ALTER TABLE `users` ADD CONSTRAINT `users_guest_id_foreign` FOREIGN KEY(`guest_id`) REFERENCES `guests`(`guest_id`);
ALTER TABLE `registrations` ADD CONSTRAINT `registrations_guest_id_foreign` FOREIGN KEY(`guest_id`) REFERENCES `guests`(`guest_id`);
ALTER TABLE `registrations` ADD CONSTRAINT `registrations_event_id_foreign` FOREIGN KEY(`event_id`) REFERENCES `events`(`event_id`);
ALTER TABLE `event_finance` ADD CONSTRAINT `event_finance_event_id_foreign` FOREIGN KEY(`event_id`) REFERENCES `events`(`event_id`);
ALTER TABLE `events` ADD CONSTRAINT `events_organizer_id_foreign` FOREIGN KEY(`organizer_id`) REFERENCES `organizers`(`organizer_id`);
ALTER TABLE `events` ADD CONSTRAINT `events_venue_id_foreign` FOREIGN KEY(`venue_id`) REFERENCES `venues`(`venue_id`);
ALTER TABLE `role_permissions` ADD CONSTRAINT `role_permissions_role_id_foreign` FOREIGN KEY(`role_id`) REFERENCES `roles`(`role_id`);
ALTER TABLE `role_permissions` ADD CONSTRAINT `role_permissions_permission_id_foreign` FOREIGN KEY(`permission_id`) REFERENCES `permissions`(`permission_id`);
ALTER TABLE `event_categories` ADD CONSTRAINT `event_categories_event_id_foreign` FOREIGN KEY(`event_id`) REFERENCES `events`(`event_id`);
ALTER TABLE `event_categories` ADD CONSTRAINT `event_categories_category_id_foreign` FOREIGN KEY(`category_id`) REFERENCES `categories`(`category_id`);

-- ============================================================
-- STORED PROCEDURES
-- ============================================================

-- Stored Procedure: Guest Check-in Logic
DELIMITER //
CREATE PROCEDURE sp_check_in_guest(IN p_registration_id BIGINT UNSIGNED)
BEGIN
    DECLARE v_exists INT DEFAULT 0;
    DECLARE v_already_checked_in INT DEFAULT 0;

    -- Check if registration exists
    SELECT COUNT(*) INTO v_exists
    FROM registrations
    WHERE registration_id = p_registration_id;

    IF v_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot find registration with this ID.';
    END IF;

    -- Check if already checked in
    SELECT attendance_status INTO v_already_checked_in
    FROM registrations
    WHERE registration_id = p_registration_id;

    IF v_already_checked_in = 1 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Guest has already checked in.';
    END IF;

    -- Execute check-in
    UPDATE registrations
    SET attendance_status = 1
    WHERE registration_id = p_registration_id;
END //
DELIMITER ;

-- ============================================================
-- TRIGGERS
-- ============================================================

-- Trigger: Enforce Event Capacity
DELIMITER //
CREATE TRIGGER trg_enforce_capacity
BEFORE INSERT ON registrations
FOR EACH ROW
BEGIN
    DECLARE v_capacity INT;
    DECLARE v_current_registrations INT;

    -- Get venue capacity for the event
    SELECT v.capacity INTO v_capacity
    FROM events e
    JOIN venues v ON e.venue_id = v.venue_id
    WHERE e.event_id = NEW.event_id;

    -- Get current registration count
    SELECT COUNT(*) INTO v_current_registrations
    FROM registrations
    WHERE event_id = NEW.event_id;

    -- Check if capacity is reached
    IF v_current_registrations >= v_capacity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Event capacity reached.';
    END IF;
END //
DELIMITER ;

-- ============================================================
-- VIEWS
-- ============================================================

-- View: Event Attendance Summary
CREATE VIEW vw_event_attendance_summary AS
SELECT
    e.event_id,
    e.event_name,
    e.event_date,
    v.venue_name,
    COUNT(r.registration_id) AS total_registrations,
    SUM(CASE WHEN r.attendance_status = 1 THEN 1 ELSE 0 END) AS checked_in_count,
    ROUND(
        CASE
            WHEN COUNT(r.registration_id) = 0 THEN 0
            ELSE (SUM(CASE WHEN r.attendance_status = 1 THEN 1 ELSE 0 END) / COUNT(r.registration_id)) * 100
        END, 2
    ) AS attendance_rate
FROM events e
JOIN venues v ON e.venue_id = v.venue_id
LEFT JOIN registrations r ON e.event_id = r.event_id
GROUP BY e.event_id, e.event_name, e.event_date, v.venue_name
ORDER BY e.event_date DESC;

-- View: Finance Summary
CREATE OR REPLACE VIEW vw_finance_summary AS
SELECT
    f.finance_id,
    e.event_id,
    e.event_name,
    e.event_date,
    e.status,
    f.planned_budget,
    f.actual_cost,
    ROUND(
        COALESCE(COUNT(r.registration_id), 0) * e.base_price, 2
    ) AS revenue,
    ROUND(f.planned_budget - f.actual_cost, 2) AS variance,
    ROUND(
        (COALESCE(COUNT(r.registration_id), 0) * e.base_price) - f.actual_cost, 2
    ) AS profit
FROM event_finance f
JOIN events e ON f.event_id = e.event_id
LEFT JOIN registrations r ON e.event_id = r.event_id
GROUP BY f.finance_id, e.event_id, e.event_name, e.event_date, e.status, e.base_price, f.planned_budget, f.actual_cost
ORDER BY e.event_date DESC;
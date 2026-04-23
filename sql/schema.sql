# events
CREATE TABLE `events`(
    `event_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `event_name` VARCHAR(255) NOT NULL,
    `event_date` DATETIME NOT NULL,
    `venue_id` BIGINT UNSIGNED NOT NULL,
    `category` VARCHAR(50) NOT NULL,
    `status` ENUM('Upcoming', 'Ongoing', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Upcoming',
    `base_price` DECIMAL(8, 2) NOT NULL,
    `organizer_id` BIGINT UNSIGNED NOT NULL
);
ALTER TABLE `events` ADD INDEX `events_event_name_index`(`event_name`);
ALTER TABLE `events` ADD INDEX `events_event_date_index`(`event_date`);
ALTER TABLE `events` ADD INDEX `events_venue_id_event_date_index`(`venue_id`, `event_date`);
ALTER TABLE `events` ADD INDEX `events_venue_id_index`(`venue_id`);

# guests
CREATE TABLE `guests`(
    `guest_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `guest_name` VARCHAR(255) NOT NULL,
    `guest_email` VARCHAR(255) NOT NULL,
    `phone_number` VARCHAR(16) NOT NULL
);
ALTER TABLE `guests` ADD INDEX `guests_guest_name_index`(`guest_name`);
ALTER TABLE `guests` ADD INDEX `guests_guest_email_index`(`guest_email`);

# organizers
CREATE TABLE `organizers`(
    `organizer_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `organizer_name` VARCHAR(255) NOT NULL,
    `address` VARCHAR(255) NOT NULL,
    `phone_number` VARCHAR(16) NOT NULL
);

# registrations
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

# venues
CREATE TABLE `venues`(
    `venue_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `venue_name` VARCHAR(255) NOT NULL,
    `venue_address` VARCHAR(255) NOT NULL,
    `capacity` INT NOT NULL COMMENT 'Use for trigger'
);

# event_finance
CREATE TABLE `event_finance`(
    `finance_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `event_id` BIGINT UNSIGNED NOT NULL,
    `planned_budget` DECIMAL(15, 2) NOT NULL,
    `actual_cost` DECIMAL(15, 2) NOT NULL,
    `revenue` DECIMAL(15, 2) NOT NULL
);

# users
CREATE TABLE `users`(
    `user_id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(255) NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `role_id` INT UNSIGNED NOT NULL
);
ALTER TABLE `users` ADD INDEX `users_username_index`(`username`);

# roles
CREATE TABLE `roles`(
    `role_id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `role_name` VARCHAR(50) NOT NULL,
    `permission_id` INT UNSIGNED NOT NULL
);

# permissions
CREATE TABLE `permissions`(
    `permission_id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `permission_name` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL
);
ALTER TABLE `permissions` ADD INDEX `permissions_permission_name_index`(`permission_name`);

# foreign_keys
ALTER TABLE `users` ADD CONSTRAINT `users_role_id_role_id_foreign` FOREIGN KEY(`role_id`) REFERENCES `roles`(`role_id`);
ALTER TABLE `registrations` ADD CONSTRAINT `registrations_guest_id_foreign` FOREIGN KEY(`guest_id`) REFERENCES `guests`(`guest_id`);
ALTER TABLE `roles` ADD CONSTRAINT `roles_permission_id_foreign` FOREIGN KEY(`permission_id`) REFERENCES `permissions`(`permission_id`);
ALTER TABLE `registrations` ADD CONSTRAINT `registrations_event_id_foreign` FOREIGN KEY(`event_id`) REFERENCES `events`(`event_id`);
ALTER TABLE `event_finance` ADD CONSTRAINT `event_finance_event_id_foreign` FOREIGN KEY(`event_id`) REFERENCES `events`(`event_id`);
ALTER TABLE `events` ADD CONSTRAINT `events_organizer_id_foreign` FOREIGN KEY(`organizer_id`) REFERENCES `organizers`(`organizer_id`);
ALTER TABLE `events` ADD CONSTRAINT `events_venue_id_foreign` FOREIGN KEY(`venue_id`) REFERENCES `venues`(`venue_id`);
-- This file will be executed automatically when MariaDB container starts
-- It creates the database and user if they don't exist

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS microblog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user if not exists
CREATE USER IF NOT EXISTS 'microblog_user'@'%' IDENTIFIED BY 'microblog_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON microblog_db.* TO 'microblog_user'@'%';

-- Refresh privileges
FLUSH PRIVILEGES;

-- Use the database
USE microblog_db;

-- Add any initial data here if needed
-- For example:
-- INSERT INTO city (name) VALUES ('Madrid'), ('Barcelona'), ('Valencia');
-- INSERT INTO neighborhood (name) VALUES ('Centro'), ('Malasaña'), ('Chueca');

SHOW TABLES;

-- Health Chatbot Database Initialization
-- This script is automatically executed when the MySQL container starts

-- Set character set and collation
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Use the health_chatbot database
USE health_chatbot;

-- Source the main schema file
SOURCE /docker-entrypoint-initdb.d/001_create_tables.sql;

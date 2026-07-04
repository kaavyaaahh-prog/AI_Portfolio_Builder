-- ============================================================
-- AI Portfolio Builder - Database Schema
-- Run this once to create the database and all required tables.
-- Usage:  mysql -u root -p < database/schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS ai_portfolio_builder;
USE ai_portfolio_builder;

-- ------------------------------------------------------------
-- Table: users
-- Stores student login/registration details and OTP info
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,       -- bcrypt hashed password
    otp VARCHAR(6) DEFAULT NULL,
    otp_expiry DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- Table: resume
-- Stores uploaded resume file path and extracted text
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS resume (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    resume_file VARCHAR(255) NOT NULL,
    resume_text LONGTEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Table: portfolio
-- Stores the AI generated / edited portfolio content
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS portfolio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(150),
    title VARCHAR(150),
    about TEXT,
    career_objective TEXT,
    education TEXT,          -- stored as JSON text
    skills TEXT,              -- stored as JSON text
    projects TEXT,            -- stored as JSON text
    certificates TEXT,        -- stored as JSON text
    achievements TEXT,        -- stored as JSON text
    github VARCHAR(255),
    linkedin VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(150),
    status ENUM('draft', 'published') DEFAULT 'draft',
    portfolio_url VARCHAR(255),
    theme VARCHAR(50) DEFAULT 'midnight',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- MIGRATION NOTE (run this ONLY if your database already
-- existed before the "theme" feature was added):
--
--   ALTER TABLE portfolio ADD COLUMN theme VARCHAR(50) DEFAULT 'midnight';
--
-- New databases created with this schema.sql already have the
-- column, so you do not need to run the line above.
-- ------------------------------------------------------------

-- ------------------------------------------------------------
-- Table: ats_score
-- Stores AI generated ATS resume score results
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ats_score (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    score INT NOT NULL,
    strengths TEXT,
    weaknesses TEXT,
    suggestions TEXT,
    keywords TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

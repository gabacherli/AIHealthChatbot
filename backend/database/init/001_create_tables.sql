-- Health Chatbot Database Schema
-- Version: 001
-- Description: Initial schema creation with users, patient-professional relationships, and audit logs

-- Create users table (streamlined - removed unused phone and date_of_birth fields)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),

    -- Professional-specific fields
    specialty VARCHAR(100),
    license_number VARCHAR(50),
    organization VARCHAR(200),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Indexes
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create patient_professional_relationships table (streamlined - removed unused start_date and end_date fields)
CREATE TABLE IF NOT EXISTS patient_professional_relationships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    professional_id INT NOT NULL,
    relationship_type VARCHAR(50) NOT NULL DEFAULT 'primary',
    status VARCHAR(20) NOT NULL DEFAULT 'active',

    -- Permissions
    can_view_documents BOOLEAN DEFAULT TRUE,
    can_add_notes BOOLEAN DEFAULT TRUE,
    can_request_tests BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Metadata
    notes TEXT,
    created_by_id INT,

    -- Foreign keys
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (professional_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_id) REFERENCES users(id) ON DELETE SET NULL,

    -- Indexes
    INDEX idx_patient_id (patient_id),
    INDEX idx_professional_id (professional_id),
    INDEX idx_relationship_type (relationship_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),

    -- Unique constraint to prevent duplicate relationships
    UNIQUE KEY unique_patient_professional (patient_id, professional_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    details JSON,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,

    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_resource_type (resource_type),
    INDEX idx_resource_id (resource_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add constraints to ensure data integrity
ALTER TABLE users
ADD CONSTRAINT chk_role CHECK (role IN ('patient', 'professional'));

ALTER TABLE patient_professional_relationships
ADD CONSTRAINT chk_relationship_type CHECK (relationship_type IN ('primary_care', 'nurse', 'specialist', 'other')),
ADD CONSTRAINT chk_status CHECK (status IN ('active', 'inactive', 'pending', 'terminated'));

ALTER TABLE audit_logs
ADD CONSTRAINT chk_resource_type CHECK (resource_type IN ('document', 'relationship', 'user', 'chat', 'upload'));

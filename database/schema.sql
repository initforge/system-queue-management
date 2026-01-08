-- =====================================================
-- QUEUE MANAGEMENT SYSTEM - MINIMAL DATABASE SCHEMA
-- =====================================================
-- Version: 5.0 (Production-Ready Minimal)
-- Tables: 9 (reduced from 27)
-- Purpose: Only essential tables for actual UI features

-- =====================================================
-- CLEANUP
-- =====================================================

DROP TABLE IF EXISTS 
    staff_schedules, shifts, ticket_complaints, staff_performance,
    queue_tickets, counters, services, users, departments
CASCADE;

DROP TYPE IF EXISTS user_role, ticket_status, ticket_priority, shift_type, shift_status CASCADE;

-- =====================================================
-- EXTENSIONS & TYPES
-- =====================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE user_role AS ENUM ('admin', 'manager', 'staff');
CREATE TYPE ticket_status AS ENUM ('waiting', 'called', 'completed', 'no_show');
CREATE TYPE ticket_priority AS ENUM ('normal', 'high', 'elderly', 'disabled', 'vip');
CREATE TYPE shift_type AS ENUM ('morning', 'afternoon', 'night');
CREATE TYPE shift_status AS ENUM ('scheduled', 'confirmed', 'cancelled', 'completed');

-- =====================================================
-- CORE TABLES
-- =====================================================

-- Departments (simplified)
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    code VARCHAR(10) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users (simplified)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    full_name VARCHAR(100) NOT NULL,
    role user_role DEFAULT 'staff',
    department_id INTEGER REFERENCES departments(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Services
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    service_code VARCHAR(20) UNIQUE,
    estimated_duration INTEGER DEFAULT 15,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Counters
CREATE TABLE counters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    number INTEGER NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    assigned_staff_id INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- QUEUE TICKETS (with integrated rating)
-- =====================================================

CREATE TABLE queue_tickets (
    id SERIAL PRIMARY KEY,
    ticket_number VARCHAR(20) UNIQUE NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20),
    customer_email VARCHAR(100),
    
    service_id INTEGER NOT NULL REFERENCES services(id),
    department_id INTEGER NOT NULL REFERENCES departments(id),
    staff_id INTEGER REFERENCES users(id),
    counter_id INTEGER REFERENCES counters(id),
    
    status ticket_status DEFAULT 'waiting',
    priority ticket_priority DEFAULT 'normal',
    queue_position INTEGER,
    form_data JSONB,
    notes TEXT,
    estimated_wait_time INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    called_at TIMESTAMP,
    served_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Rating (simplified to overall only)
    overall_rating INTEGER CHECK (overall_rating BETWEEN 1 AND 5),
    review_comments TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- PERFORMANCE & COMPLAINTS
-- =====================================================

-- Staff performance (for Hiệu suất tab)
CREATE TABLE staff_performance (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    department_id INTEGER NOT NULL REFERENCES departments(id),
    date DATE NOT NULL,
    tickets_served INTEGER DEFAULT 0,
    avg_service_time NUMERIC(5,2) DEFAULT 0,
    total_rating_score INTEGER DEFAULT 0,
    rating_count INTEGER DEFAULT 0,
    avg_rating NUMERIC(3,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

-- Ticket complaints (for Khiếu nại tab)
CREATE TABLE ticket_complaints (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES queue_tickets(id),
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20),
    customer_email VARCHAR(100),
    complaint_text TEXT NOT NULL,
    rating INTEGER,
    status VARCHAR(20) DEFAULT 'waiting',
    assigned_to INTEGER REFERENCES users(id),
    manager_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- =====================================================
-- SCHEDULE (for Ca làm việc tabs)
-- =====================================================

-- Shifts
CREATE TABLE shifts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    shift_type shift_type NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Staff schedules
CREATE TABLE staff_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    staff_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    manager_id INTEGER NOT NULL REFERENCES users(id),
    shift_id UUID NOT NULL REFERENCES shifts(id),
    scheduled_date DATE NOT NULL,
    status shift_status DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES
-- =====================================================

CREATE INDEX idx_queue_tickets_status ON queue_tickets(status);
CREATE INDEX idx_queue_tickets_department ON queue_tickets(department_id);
CREATE INDEX idx_queue_tickets_created ON queue_tickets(created_at);
CREATE INDEX idx_users_department ON users(department_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_services_department ON services(department_id);
CREATE INDEX idx_complaints_status ON ticket_complaints(status);
CREATE INDEX idx_staff_schedules_date ON staff_schedules(scheduled_date);
CREATE INDEX idx_staff_schedules_staff ON staff_schedules(staff_id);

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE 'MINIMAL DATABASE SCHEMA CREATED!';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE 'Tables: 9 (reduced from 27)';
    RAISE NOTICE '  - departments, users, services, counters';
    RAISE NOTICE '  - queue_tickets, staff_performance, ticket_complaints';
    RAISE NOTICE '  - shifts, staff_schedules';
    RAISE NOTICE '';
    RAISE NOTICE 'Removed: activity_logs, daily_login_logs, ai_conversations,';
    RAISE NOTICE '         staff_notifications, leave_requests, shift_exchanges,';
    RAISE NOTICE '         staff_checkins, staff_attendance, and 10 more';
    RAISE NOTICE '=====================================================';
END $$;
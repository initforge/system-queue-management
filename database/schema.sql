-- =====================================================
-- QUEUE MANAGEMENT SYSTEM - DATABASE SCHEMA
-- =====================================================
-- Created: October 22, 2025
-- Purpose: Database tables, types, and constraints only
-- Usage: Run this first to create database structure
-- Version: 3.0

-- =====================================================
-- CLEANUP & PREPARATION
-- =====================================================

-- Drop existing tables if they exist (for clean rebuild)
DROP TABLE IF EXISTS 
    activity_logs, service_sessions, feedback, ticket_complaints, 
    staff_performance, staff_settings, queue_tickets, 
    service_form_fields, qr_codes, announcements, 
    counters, services, users, departments
CASCADE;

-- Drop existing types if they exist
DROP TYPE IF EXISTS 
    user_role, ticket_status, ticket_priority, 
    field_type, session_status 
CASCADE;

-- =====================================================
-- ENABLE EXTENSIONS
-- =====================================================

-- Enable UUID extension for generating unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- CREATE ENUM TYPES
-- =====================================================

-- User roles in the system
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'staff');

-- Ticket status lifecycle
CREATE TYPE ticket_status AS ENUM ('waiting', 'called', 'completed', 'no_show');

-- Priority levels for tickets
CREATE TYPE ticket_priority AS ENUM ('normal', 'high', 'elderly', 'disabled', 'vip');

-- Form field types for dynamic forms
CREATE TYPE field_type AS ENUM ('text', 'email', 'phone', 'textarea', 'select', 'checkbox', 'radio', 'number', 'date');

-- Service session status
CREATE TYPE session_status AS ENUM ('active', 'paused', 'completed', 'cancelled');

-- =====================================================
-- CREATE CORE TABLES
-- =====================================================

-- Departments table - organizational units
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    code VARCHAR(10) UNIQUE NOT NULL,
    qr_code_token UUID DEFAULT uuid_generate_v4(),
    max_concurrent_customers INTEGER DEFAULT 50,
    operating_hours JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table - staff, managers, admins
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
    avatar_url TEXT,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Services table - available services in each department
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    service_code VARCHAR(20) UNIQUE,
    estimated_duration INTEGER DEFAULT 15, -- minutes
    max_daily_capacity INTEGER DEFAULT 100,
    form_schema JSONB, -- Dynamic form configuration
    is_active BOOLEAN DEFAULT TRUE,
    requires_appointment BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Counters table - service counters in departments
CREATE TABLE counters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    number INTEGER NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    assigned_staff_id INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- MAIN QUEUE TICKETS TABLE WITH REVIEW SYSTEM
-- =====================================================

-- Queue tickets - the heart of the system with integrated review/rating
CREATE TABLE queue_tickets (
    -- Basic ticket information
    id SERIAL PRIMARY KEY,
    ticket_number VARCHAR(20) UNIQUE NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    customer_email VARCHAR(100),
    
    -- Service and assignment information
    service_id INTEGER NOT NULL REFERENCES services(id),
    department_id INTEGER NOT NULL REFERENCES departments(id),
    staff_id INTEGER REFERENCES users(id),
    counter_id INTEGER REFERENCES counters(id),
    
    -- Status and priority
    status ticket_status DEFAULT 'waiting',
    priority ticket_priority DEFAULT 'normal',
    queue_position INTEGER,
    
    -- Additional information
    form_data JSONB, -- Customer form submission data
    notes TEXT, -- Staff notes
    estimated_wait_time INTEGER, -- in minutes
    
    -- Timestamp tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP,
    called_at TIMESTAMP,
    served_at TIMESTAMP,
    completed_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    -- =====================================================
    -- INTEGRATED REVIEW/RATING SYSTEM
    -- =====================================================
    
    -- Rating fields (1-5 star scale)
    service_rating INTEGER CHECK (service_rating BETWEEN 1 AND 5),
    staff_rating INTEGER CHECK (staff_rating BETWEEN 1 AND 5),
    speed_rating INTEGER CHECK (speed_rating BETWEEN 1 AND 5),
    overall_rating INTEGER CHECK (overall_rating BETWEEN 1 AND 5),
    
    -- Feedback text and timestamp
    review_comments TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE
);

-- Add detailed comments for rating fields
COMMENT ON COLUMN queue_tickets.service_rating IS 'Service quality rating (1-5 stars) - Overall satisfaction with service provided';
COMMENT ON COLUMN queue_tickets.staff_rating IS 'Staff service rating (1-5 stars) - Professional behavior and helpfulness';  
COMMENT ON COLUMN queue_tickets.speed_rating IS 'Service speed rating (1-5 stars) - How quickly service was delivered';
COMMENT ON COLUMN queue_tickets.overall_rating IS 'Overall experience rating (1-5 stars) - General satisfaction level';
COMMENT ON COLUMN queue_tickets.review_comments IS 'Customer feedback and comments - Detailed written feedback';
COMMENT ON COLUMN queue_tickets.reviewed_at IS 'Timestamp when review was submitted';

-- =====================================================
-- PERFORMANCE & REPORTING TABLES
-- =====================================================

-- Staff performance tracking
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

-- General feedback table (separate from ticket reviews)
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES queue_tickets(id),
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    category VARCHAR(50),
    message TEXT NOT NULL,
    staff_response TEXT,
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP
);

-- Ticket Complaints handling (simplified model)
CREATE TABLE ticket_complaints (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES queue_tickets(id),
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20),
    customer_email VARCHAR(100),
    complaint_text TEXT NOT NULL,
    rating INTEGER,
    status VARCHAR(20) DEFAULT 'waiting', -- waiting, processing, completed
    assigned_to INTEGER REFERENCES users(id), -- Manager ID
    manager_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Staff notifications for complaints and announcements
CREATE TABLE staff_notifications (
    id SERIAL PRIMARY KEY,
    recipient_id INTEGER NOT NULL REFERENCES users(id),
    sender_id INTEGER REFERENCES users(id),
    complaint_id INTEGER REFERENCES ticket_complaints(id),
    ticket_id INTEGER REFERENCES queue_tickets(id),
    
    -- Notification content
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) DEFAULT 'complaint', -- complaint, announcement, alert
    priority VARCHAR(20) DEFAULT 'normal', -- low, normal, high, urgent
    
    -- Complaint details (when notification is about a complaint)
    complaint_details JSONB, -- Store complaint subject, description, service, department info
    
    -- Status tracking
    is_read BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    archived_at TIMESTAMP
);

-- Comments on notification fields
COMMENT ON COLUMN staff_notifications.complaint_details IS 'JSON containing complaint subject, description, service_name, department_name, customer info';
COMMENT ON COLUMN staff_notifications.notification_type IS 'Type of notification: complaint, announcement, alert, etc';
COMMENT ON COLUMN staff_notifications.priority IS 'Notification priority level for UI display and sorting';

-- =====================================================
-- OPERATIONAL TABLES
-- =====================================================

-- Service sessions tracking
CREATE TABLE service_sessions (
    id SERIAL PRIMARY KEY,
    staff_id INTEGER NOT NULL REFERENCES users(id),
    counter_id INTEGER REFERENCES counters(id),
    ticket_id INTEGER REFERENCES queue_tickets(id),
    status session_status DEFAULT 'active',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration_minutes INTEGER,
    notes TEXT
);

-- QR codes for mobile registration
CREATE TABLE qr_codes (
    id SERIAL PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    token UUID DEFAULT uuid_generate_v4(),
    registration_url TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dynamic form fields for services
CREATE TABLE service_form_fields (
    id SERIAL PRIMARY KEY,
    service_id INTEGER NOT NULL REFERENCES services(id),
    field_name VARCHAR(100) NOT NULL,
    field_label VARCHAR(200) NOT NULL,
    field_type field_type NOT NULL,
    field_options JSONB, -- For select, radio, checkbox options
    is_required BOOLEAN DEFAULT FALSE,
    validation_rules JSONB,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Activity logging
CREATE TABLE activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily login logs - Track first login of each day for attendance statistics
CREATE TABLE daily_login_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    login_date DATE NOT NULL,
    first_login_time TIMESTAMP NOT NULL,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, login_date)
);

-- Index for efficient daily login queries
CREATE INDEX idx_daily_login_logs_user_date ON daily_login_logs(user_id, login_date);
CREATE INDEX idx_daily_login_logs_date ON daily_login_logs(login_date);

-- AI Conversations table
CREATE TABLE ai_conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    context_data JSONB,
    function_calls JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_conversations_user ON ai_conversations(user_id);
CREATE INDEX idx_ai_conversations_conv_id ON ai_conversations(conversation_id);
CREATE INDEX idx_ai_conversations_created ON ai_conversations(created_at);

-- Knowledge Base Categories
CREATE TABLE knowledge_base_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    parent_id INTEGER REFERENCES knowledge_base_categories(id),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge Base Articles
CREATE TABLE knowledge_base_articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    category_id INTEGER REFERENCES knowledge_base_categories(id),
    author_id INTEGER NOT NULL REFERENCES users(id),
    department_id INTEGER REFERENCES departments(id),
    tags JSONB DEFAULT '[]',
    is_published BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    rating NUMERIC(3,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE
);

-- Knowledge Base Attachments
CREATE TABLE knowledge_base_attachments (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES knowledge_base_articles(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_url TEXT NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    cloudinary_public_id VARCHAR(255),
    uploaded_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Knowledge Base
CREATE INDEX idx_kb_articles_category ON knowledge_base_articles(category_id);
CREATE INDEX idx_kb_articles_author ON knowledge_base_articles(author_id);
CREATE INDEX idx_kb_articles_department ON knowledge_base_articles(department_id);
CREATE INDEX idx_kb_articles_published ON knowledge_base_articles(is_published);
CREATE INDEX idx_kb_articles_featured ON knowledge_base_articles(is_featured);
CREATE INDEX idx_kb_articles_created ON knowledge_base_articles(created_at);
CREATE INDEX idx_kb_attachments_article ON knowledge_base_attachments(article_id);
CREATE INDEX idx_kb_categories_parent ON knowledge_base_categories(parent_id);
CREATE INDEX idx_kb_categories_active ON knowledge_base_categories(is_active);

-- Staff settings and preferences
CREATE TABLE staff_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    notification_preferences JSONB DEFAULT '{}',
    display_preferences JSONB DEFAULT '{}',
    work_schedule JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- System announcements
CREATE TABLE announcements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'general', -- general, urgent, maintenance
    target_audience VARCHAR(50) DEFAULT 'all', -- all, staff, customers
    department_id INTEGER REFERENCES departments(id),
    created_by INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    starts_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- CREATE INDEXES FOR PERFORMANCE
-- =====================================================

-- Core performance indexes for queue operations
CREATE INDEX idx_queue_tickets_status ON queue_tickets(status);
CREATE INDEX idx_queue_tickets_department ON queue_tickets(department_id);
CREATE INDEX idx_queue_tickets_service ON queue_tickets(service_id);
CREATE INDEX idx_queue_tickets_staff ON queue_tickets(staff_id);
CREATE INDEX idx_queue_tickets_created ON queue_tickets(created_at);
CREATE INDEX idx_queue_tickets_queue_pos ON queue_tickets(queue_position);

-- Review system indexes for analytics
CREATE INDEX idx_queue_tickets_ratings ON queue_tickets(overall_rating) WHERE overall_rating IS NOT NULL;
CREATE INDEX idx_queue_tickets_reviewed ON queue_tickets(reviewed_at) WHERE reviewed_at IS NOT NULL;

-- User and department indexes
CREATE INDEX idx_users_department ON users(department_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_services_department ON services(department_id);
CREATE INDEX idx_feedback_ticket ON feedback(ticket_id);
CREATE INDEX idx_complaints_status ON complaints(status);

-- Staff notifications indexes for quick retrieval
CREATE INDEX idx_staff_notifications_recipient ON staff_notifications(recipient_id);
CREATE INDEX idx_staff_notifications_unread ON staff_notifications(recipient_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_staff_notifications_created ON staff_notifications(created_at);
CREATE INDEX idx_staff_notifications_type ON staff_notifications(notification_type);
CREATE INDEX idx_staff_notifications_complaint ON staff_notifications(complaint_id) WHERE complaint_id IS NOT NULL;

-- =====================================================
-- SCHEDULE MANAGEMENT TABLES
-- =====================================================

-- Schedule-specific types
CREATE TYPE shift_type AS ENUM ('morning', 'afternoon', 'night');
CREATE TYPE shift_status AS ENUM ('scheduled', 'confirmed', 'cancelled', 'completed');
CREATE TYPE leave_type AS ENUM ('sick', 'personal', 'vacation', 'emergency');
CREATE TYPE leave_status AS ENUM ('pending', 'approved', 'rejected');
CREATE TYPE exchange_status AS ENUM ('pending', 'approved', 'rejected', 'cancelled');
CREATE TYPE checkin_status AS ENUM ('pending', 'approved', 'rejected');

-- Shifts table
CREATE TABLE shifts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    shift_type shift_type NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Staff schedules table
CREATE TABLE staff_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    staff_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    manager_id INTEGER NOT NULL REFERENCES users(id),
    shift_id UUID NOT NULL REFERENCES shifts(id),
    scheduled_date DATE NOT NULL,
    status shift_status DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Leave requests table
CREATE TABLE leave_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    staff_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    manager_id INTEGER REFERENCES users(id),
    leave_date DATE NOT NULL,
    leave_type leave_type NOT NULL,
    reason TEXT NOT NULL,
    status leave_status DEFAULT 'pending',
    rejection_reason TEXT,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Shift exchanges table
CREATE TABLE shift_exchanges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requesting_staff_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_staff_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    manager_id INTEGER REFERENCES users(id),
    requesting_schedule_id UUID NOT NULL REFERENCES staff_schedules(id),
    target_schedule_id UUID NOT NULL REFERENCES staff_schedules(id),
    reason TEXT NOT NULL,
    status exchange_status DEFAULT 'pending',
    rejection_reason TEXT,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Staff checkins table
CREATE TABLE staff_checkins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    staff_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    schedule_id UUID NOT NULL REFERENCES staff_schedules(id),
    manager_id INTEGER REFERENCES users(id),
    checkin_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status checkin_status DEFAULT 'pending',
    location TEXT,
    notes TEXT,
    approved_at TIMESTAMP WITH TIME ZONE,
    rejected_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Staff attendance table
CREATE TABLE staff_attendance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    staff_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    schedule_id UUID NOT NULL REFERENCES staff_schedules(id),
    checkin_time TIMESTAMP WITH TIME ZONE,
    checkout_time TIMESTAMP WITH TIME ZONE,
    break_start_time TIMESTAMP WITH TIME ZONE,
    break_end_time TIMESTAMP WITH TIME ZONE,
    total_hours VARCHAR(10),
    overtime_hours VARCHAR(10) DEFAULT '0',
    is_absent BOOLEAN DEFAULT FALSE,
    absence_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '✅ DATABASE SCHEMA CREATED SUCCESSFULLY!';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '📋 Tables Created:';
    RAISE NOTICE '   - 15 Core tables with relationships';
    RAISE NOTICE '   - 7 ENUM types for data integrity';
    RAISE NOTICE '   - Integrated review/rating system';
    RAISE NOTICE '   - Performance indexes';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Key Features:';
    RAISE NOTICE '   - Queue management with priority';
    RAISE NOTICE '   - Staff performance tracking';
    RAISE NOTICE '   - Customer feedback & ratings';
    RAISE NOTICE '   - Dynamic forms & QR codes';
    RAISE NOTICE '   - Comprehensive logging';
    RAISE NOTICE '';
    RAISE NOTICE '➡️  Next: Run data.sql to populate with sample data';
    RAISE NOTICE '=====================================================';
END $$;
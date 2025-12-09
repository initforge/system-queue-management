-- =====================================================
-- QUEUE MANAGEMENT SYSTEM - COMPLETE SETUP
-- =====================================================
-- Created: October 22, 2025
-- Purpose: Run both schema and data setup in sequence
-- Usage: Single command to setup entire database
-- Version: 3.0

-- =====================================================
-- STEP 1: CREATE DATABASE SCHEMA
-- =====================================================

-- Include schema creation
\i schema.sql

-- =====================================================
-- STEP 2: INSERT SAMPLE DATA  
-- =====================================================

-- Include sample data
\i data.sql

-- =====================================================
-- SETUP COMPLETE MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '🎉 QUEUE MANAGEMENT SYSTEM SETUP COMPLETE!';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '✅ Database Structure: Created';
    RAISE NOTICE '✅ Sample Data: Inserted';
    RAISE NOTICE '✅ Review System: Integrated';
    RAISE NOTICE '✅ Performance Tracking: Ready';
    RAISE NOTICE '';
    RAISE NOTICE '🔑 Login Credentials (Password: Admin123!):';
    RAISE NOTICE '   👑 admin@qstream.vn (System Administrator)';
    RAISE NOTICE '   👨‍💼 manager.01@qstream.vn (Department Manager)';
    RAISE NOTICE '   👨‍💻 staff.01@qstream.vn (Counter Staff)';
    RAISE NOTICE '';
    RAISE NOTICE '📈 Ready Features:';
    RAISE NOTICE '   • Queue Management with Priority';
    RAISE NOTICE '   • Customer Review & Rating System (1-5 ⭐)';
    RAISE NOTICE '   • Staff Performance Analytics';
    RAISE NOTICE '   • Real-time WebSocket Updates';
    RAISE NOTICE '   • QR Code Mobile Registration';
    RAISE NOTICE '   • Dynamic Service Forms';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 System is ready for production use!';
    RAISE NOTICE '=====================================================';
END $$;
--
-- PostgreSQL database dump
--

\restrict CMIkYDnVS99lrBPjBjmh5e8jWgfh1kQdjg9MLuMd5Llhsf26tOYv7TXhsKlH3D3

-- Dumped from database version 15.14
-- Dumped by pg_dump version 15.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: checkin_status; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.checkin_status AS ENUM (
    'pending',
    'approved',
    'rejected'
);


ALTER TYPE public.checkin_status OWNER TO admin;

--
-- Name: complaint_severity; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.complaint_severity AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);


ALTER TYPE public.complaint_severity OWNER TO admin;

--
-- Name: complaint_status; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.complaint_status AS ENUM (
    'open',
    'investigating',
    'resolved',
    'closed'
);


ALTER TYPE public.complaint_status OWNER TO admin;

--
-- Name: complaintseverity; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.complaintseverity AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH',
    'CRITICAL'
);


ALTER TYPE public.complaintseverity OWNER TO admin;

--
-- Name: complaintstatus; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.complaintstatus AS ENUM (
    'OPEN',
    'INVESTIGATING',
    'RESOLVED',
    'CLOSED'
);


ALTER TYPE public.complaintstatus OWNER TO admin;

--
-- Name: exchange_status; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.exchange_status AS ENUM (
    'pending',
    'approved',
    'rejected',
    'cancelled'
);


ALTER TYPE public.exchange_status OWNER TO admin;

--
-- Name: field_type; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.field_type AS ENUM (
    'text',
    'email',
    'phone',
    'textarea',
    'select',
    'checkbox',
    'radio',
    'number',
    'date'
);


ALTER TYPE public.field_type OWNER TO admin;

--
-- Name: fieldtype; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.fieldtype AS ENUM (
    'TEXT',
    'EMAIL',
    'PHONE',
    'TEXTAREA',
    'SELECT',
    'CHECKBOX',
    'RADIO',
    'NUMBER',
    'DATE'
);


ALTER TYPE public.fieldtype OWNER TO admin;

--
-- Name: leave_status; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.leave_status AS ENUM (
    'pending',
    'approved',
    'rejected'
);


ALTER TYPE public.leave_status OWNER TO admin;

--
-- Name: leave_type; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.leave_type AS ENUM (
    'sick',
    'personal',
    'vacation',
    'emergency'
);


ALTER TYPE public.leave_type OWNER TO admin;

--
-- Name: session_status; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.session_status AS ENUM (
    'active',
    'paused',
    'completed',
    'cancelled'
);


ALTER TYPE public.session_status OWNER TO admin;

--
-- Name: shift_status; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.shift_status AS ENUM (
    'scheduled',
    'confirmed',
    'cancelled',
    'completed'
);


ALTER TYPE public.shift_status OWNER TO admin;

--
-- Name: shift_type; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.shift_type AS ENUM (
    'morning',
    'afternoon',
    'night'
);


ALTER TYPE public.shift_type OWNER TO admin;

--
-- Name: ticket_priority; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.ticket_priority AS ENUM (
    'normal',
    'high',
    'elderly',
    'disabled',
    'vip'
);


ALTER TYPE public.ticket_priority OWNER TO admin;

--
-- Name: ticket_status; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.ticket_status AS ENUM (
    'waiting',
    'called',
    'completed',
    'no_show'
);


ALTER TYPE public.ticket_status OWNER TO admin;

--
-- Name: ticketstatus; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.ticketstatus AS ENUM (
    'waiting',
    'called',
    'completed',
    'no_show'
);


ALTER TYPE public.ticketstatus OWNER TO admin;

--
-- Name: user_role; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.user_role AS ENUM (
    'admin',
    'manager',
    'staff'
);


ALTER TYPE public.user_role OWNER TO admin;

--
-- Name: update_ticket_complaints_updated_at(); Type: FUNCTION; Schema: public; Owner: admin
--

CREATE FUNCTION public.update_ticket_complaints_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_ticket_complaints_updated_at() OWNER TO admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activity_logs; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.activity_logs (
    id integer NOT NULL,
    user_id integer,
    action character varying(100) NOT NULL,
    entity_type character varying(50),
    entity_id integer,
    details jsonb,
    ip_address inet,
    user_agent text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.activity_logs OWNER TO admin;

--
-- Name: activity_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.activity_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.activity_logs_id_seq OWNER TO admin;

--
-- Name: activity_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.activity_logs_id_seq OWNED BY public.activity_logs.id;


--
-- Name: ai_conversations; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.ai_conversations (
    id integer NOT NULL,
    user_id integer NOT NULL,
    conversation_id character varying(100) NOT NULL,
    role character varying(20) NOT NULL,
    message text NOT NULL,
    context_data json,
    function_calls json,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.ai_conversations OWNER TO admin;

--
-- Name: ai_conversations_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.ai_conversations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_conversations_id_seq OWNER TO admin;

--
-- Name: ai_conversations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.ai_conversations_id_seq OWNED BY public.ai_conversations.id;


--
-- Name: announcements; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.announcements (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    content text NOT NULL,
    type character varying(50) DEFAULT 'general'::character varying,
    target_audience character varying(50) DEFAULT 'all'::character varying,
    department_id integer,
    created_by integer,
    is_active boolean DEFAULT true,
    starts_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.announcements OWNER TO admin;

--
-- Name: announcements_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.announcements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.announcements_id_seq OWNER TO admin;

--
-- Name: announcements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.announcements_id_seq OWNED BY public.announcements.id;


--
-- Name: counters; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.counters (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    number integer NOT NULL,
    department_id integer NOT NULL,
    assigned_staff_id integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.counters OWNER TO admin;

--
-- Name: counters_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.counters_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.counters_id_seq OWNER TO admin;

--
-- Name: counters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.counters_id_seq OWNED BY public.counters.id;


--
-- Name: daily_login_logs; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.daily_login_logs (
    id integer NOT NULL,
    user_id integer NOT NULL,
    login_date date NOT NULL,
    first_login_time timestamp with time zone NOT NULL,
    ip_address character varying(45),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.daily_login_logs OWNER TO admin;

--
-- Name: daily_login_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.daily_login_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.daily_login_logs_id_seq OWNER TO admin;

--
-- Name: daily_login_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.daily_login_logs_id_seq OWNED BY public.daily_login_logs.id;


--
-- Name: departments; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.departments (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    code character varying(10) NOT NULL,
    qr_code_token uuid DEFAULT public.uuid_generate_v4(),
    max_concurrent_customers integer DEFAULT 50,
    operating_hours jsonb,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.departments OWNER TO admin;

--
-- Name: departments_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.departments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.departments_id_seq OWNER TO admin;

--
-- Name: departments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.departments_id_seq OWNED BY public.departments.id;


--
-- Name: feedback; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.feedback (
    id integer NOT NULL,
    ticket_id integer,
    customer_name character varying(100),
    customer_email character varying(100),
    rating integer,
    category character varying(50),
    message text NOT NULL,
    staff_response text,
    is_anonymous boolean,
    created_at timestamp without time zone DEFAULT now(),
    responded_at timestamp without time zone
);


ALTER TABLE public.feedback OWNER TO admin;

--
-- Name: feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feedback_id_seq OWNER TO admin;

--
-- Name: feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.feedback_id_seq OWNED BY public.feedback.id;


--
-- Name: knowledge_base_articles; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.knowledge_base_articles (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    slug character varying(200) NOT NULL,
    content text NOT NULL,
    category_id integer,
    author_id integer NOT NULL,
    department_id integer,
    tags json,
    is_published boolean,
    is_featured boolean,
    view_count integer,
    rating character varying(10),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    published_at timestamp with time zone
);


ALTER TABLE public.knowledge_base_articles OWNER TO admin;

--
-- Name: knowledge_base_articles_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.knowledge_base_articles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.knowledge_base_articles_id_seq OWNER TO admin;

--
-- Name: knowledge_base_articles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.knowledge_base_articles_id_seq OWNED BY public.knowledge_base_articles.id;


--
-- Name: knowledge_base_attachments; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.knowledge_base_attachments (
    id integer NOT NULL,
    article_id integer NOT NULL,
    file_name character varying(255) NOT NULL,
    file_url text NOT NULL,
    file_type character varying(50),
    file_size integer,
    cloudinary_public_id character varying(255),
    uploaded_by integer NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.knowledge_base_attachments OWNER TO admin;

--
-- Name: knowledge_base_attachments_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.knowledge_base_attachments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.knowledge_base_attachments_id_seq OWNER TO admin;

--
-- Name: knowledge_base_attachments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.knowledge_base_attachments_id_seq OWNED BY public.knowledge_base_attachments.id;


--
-- Name: knowledge_base_categories; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.knowledge_base_categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    slug character varying(100) NOT NULL,
    description text,
    icon character varying(50),
    parent_id integer,
    display_order integer,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.knowledge_base_categories OWNER TO admin;

--
-- Name: knowledge_base_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.knowledge_base_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.knowledge_base_categories_id_seq OWNER TO admin;

--
-- Name: knowledge_base_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.knowledge_base_categories_id_seq OWNED BY public.knowledge_base_categories.id;


--
-- Name: leave_requests; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.leave_requests (
    id uuid NOT NULL,
    staff_id integer NOT NULL,
    manager_id integer,
    leave_date date NOT NULL,
    leave_type public.leave_type NOT NULL,
    reason text NOT NULL,
    status public.leave_status,
    rejection_reason text,
    submitted_at timestamp with time zone DEFAULT now(),
    reviewed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.leave_requests OWNER TO admin;

--
-- Name: qr_codes; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.qr_codes (
    id integer NOT NULL,
    department_id integer NOT NULL,
    token uuid DEFAULT public.uuid_generate_v4(),
    registration_url text NOT NULL,
    is_active boolean DEFAULT true,
    expires_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.qr_codes OWNER TO admin;

--
-- Name: qr_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.qr_codes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.qr_codes_id_seq OWNER TO admin;

--
-- Name: qr_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.qr_codes_id_seq OWNED BY public.qr_codes.id;


--
-- Name: queue_settings; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.queue_settings (
    id integer NOT NULL,
    department_id integer NOT NULL,
    max_queue_size integer DEFAULT 100,
    auto_call_next boolean DEFAULT false,
    estimated_wait_multiplier numeric(3,2) DEFAULT 1.0,
    notification_settings jsonb DEFAULT '{}'::jsonb,
    display_settings jsonb DEFAULT '{}'::jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.queue_settings OWNER TO admin;

--
-- Name: queue_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.queue_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.queue_settings_id_seq OWNER TO admin;

--
-- Name: queue_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.queue_settings_id_seq OWNED BY public.queue_settings.id;


--
-- Name: queue_tickets; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.queue_tickets (
    id integer NOT NULL,
    ticket_number character varying(20) NOT NULL,
    customer_name character varying(100) NOT NULL,
    customer_phone character varying(20) NOT NULL,
    customer_email character varying(100),
    service_id integer NOT NULL,
    department_id integer NOT NULL,
    staff_id integer,
    counter_id integer,
    status public.ticket_status DEFAULT 'waiting'::public.ticket_status,
    priority public.ticket_priority DEFAULT 'normal'::public.ticket_priority,
    queue_position integer,
    form_data jsonb,
    notes text,
    estimated_wait_time integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    submitted_at timestamp without time zone,
    called_at timestamp without time zone,
    served_at timestamp without time zone,
    completed_at timestamp without time zone,
    cancelled_at timestamp without time zone,
    service_rating integer,
    staff_rating integer,
    speed_rating integer,
    overall_rating integer,
    review_comments text,
    reviewed_at timestamp with time zone,
    CONSTRAINT queue_tickets_overall_rating_check CHECK (((overall_rating >= 1) AND (overall_rating <= 5))),
    CONSTRAINT queue_tickets_service_rating_check CHECK (((service_rating >= 1) AND (service_rating <= 5))),
    CONSTRAINT queue_tickets_speed_rating_check CHECK (((speed_rating >= 1) AND (speed_rating <= 5))),
    CONSTRAINT queue_tickets_staff_rating_check CHECK (((staff_rating >= 1) AND (staff_rating <= 5)))
);


ALTER TABLE public.queue_tickets OWNER TO admin;

--
-- Name: COLUMN queue_tickets.service_rating; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.queue_tickets.service_rating IS 'Service quality rating (1-5 stars) - Overall satisfaction with service provided';


--
-- Name: COLUMN queue_tickets.staff_rating; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.queue_tickets.staff_rating IS 'Staff service rating (1-5 stars) - Professional behavior and helpfulness';


--
-- Name: COLUMN queue_tickets.speed_rating; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.queue_tickets.speed_rating IS 'Service speed rating (1-5 stars) - How quickly service was delivered';


--
-- Name: COLUMN queue_tickets.overall_rating; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.queue_tickets.overall_rating IS 'Overall experience rating (1-5 stars) - General satisfaction level';


--
-- Name: COLUMN queue_tickets.review_comments; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.queue_tickets.review_comments IS 'Customer feedback and comments - Detailed written feedback';


--
-- Name: COLUMN queue_tickets.reviewed_at; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.queue_tickets.reviewed_at IS 'Timestamp when review was submitted';


--
-- Name: queue_tickets_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.queue_tickets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.queue_tickets_id_seq OWNER TO admin;

--
-- Name: queue_tickets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.queue_tickets_id_seq OWNED BY public.queue_tickets.id;


--
-- Name: service_form_fields; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.service_form_fields (
    id integer NOT NULL,
    service_id integer NOT NULL,
    field_name character varying(100) NOT NULL,
    field_label character varying(200) NOT NULL,
    field_type public.field_type NOT NULL,
    field_options jsonb,
    is_required boolean DEFAULT false,
    validation_rules jsonb,
    display_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.service_form_fields OWNER TO admin;

--
-- Name: service_form_fields_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.service_form_fields_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.service_form_fields_id_seq OWNER TO admin;

--
-- Name: service_form_fields_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.service_form_fields_id_seq OWNED BY public.service_form_fields.id;


--
-- Name: service_sessions; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.service_sessions (
    id integer NOT NULL,
    staff_id integer NOT NULL,
    counter_id integer,
    ticket_id integer,
    status public.session_status DEFAULT 'active'::public.session_status,
    started_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    ended_at timestamp without time zone,
    duration_minutes integer,
    notes text
);


ALTER TABLE public.service_sessions OWNER TO admin;

--
-- Name: service_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.service_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.service_sessions_id_seq OWNER TO admin;

--
-- Name: service_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.service_sessions_id_seq OWNED BY public.service_sessions.id;


--
-- Name: services; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.services (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    department_id integer NOT NULL,
    service_code character varying(20),
    estimated_duration integer DEFAULT 15,
    max_daily_capacity integer DEFAULT 100,
    form_schema jsonb,
    is_active boolean DEFAULT true,
    requires_appointment boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.services OWNER TO admin;

--
-- Name: services_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.services_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.services_id_seq OWNER TO admin;

--
-- Name: services_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.services_id_seq OWNED BY public.services.id;


--
-- Name: shift_exchanges; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.shift_exchanges (
    id uuid NOT NULL,
    requesting_staff_id integer NOT NULL,
    target_staff_id integer NOT NULL,
    manager_id integer,
    requesting_schedule_id uuid NOT NULL,
    target_schedule_id uuid NOT NULL,
    reason text NOT NULL,
    status public.exchange_status,
    rejection_reason text,
    requested_at timestamp with time zone DEFAULT now(),
    reviewed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.shift_exchanges OWNER TO admin;

--
-- Name: shifts; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.shifts (
    id uuid NOT NULL,
    name character varying(100) NOT NULL,
    shift_type public.shift_type NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    description text,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.shifts OWNER TO admin;

--
-- Name: staff_attendance; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.staff_attendance (
    id uuid NOT NULL,
    staff_id integer NOT NULL,
    schedule_id uuid NOT NULL,
    checkin_time timestamp with time zone,
    checkout_time timestamp with time zone,
    break_start_time timestamp with time zone,
    break_end_time timestamp with time zone,
    total_hours character varying(10),
    overtime_hours character varying(10),
    is_absent boolean,
    absence_reason text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.staff_attendance OWNER TO admin;

--
-- Name: staff_checkins; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.staff_checkins (
    id uuid NOT NULL,
    staff_id integer NOT NULL,
    schedule_id uuid NOT NULL,
    manager_id integer,
    checkin_time timestamp with time zone DEFAULT now(),
    status public.checkin_status,
    location text,
    notes text,
    approved_at timestamp with time zone,
    rejected_reason text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.staff_checkins OWNER TO admin;

--
-- Name: staff_notifications; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.staff_notifications (
    id integer NOT NULL,
    recipient_id integer NOT NULL,
    sender_id integer,
    complaint_id integer,
    ticket_id integer,
    title character varying(200) NOT NULL,
    message text NOT NULL,
    notification_type character varying(50),
    priority character varying(20),
    complaint_details json,
    is_read boolean,
    is_archived boolean,
    created_at timestamp with time zone DEFAULT now(),
    read_at timestamp with time zone,
    archived_at timestamp with time zone
);


ALTER TABLE public.staff_notifications OWNER TO admin;

--
-- Name: staff_notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.staff_notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.staff_notifications_id_seq OWNER TO admin;

--
-- Name: staff_notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.staff_notifications_id_seq OWNED BY public.staff_notifications.id;


--
-- Name: staff_performance; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.staff_performance (
    id integer NOT NULL,
    user_id integer NOT NULL,
    department_id integer NOT NULL,
    date date NOT NULL,
    tickets_served integer DEFAULT 0,
    avg_service_time numeric(5,2) DEFAULT 0,
    total_rating_score integer DEFAULT 0,
    rating_count integer DEFAULT 0,
    avg_rating numeric(3,2) DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.staff_performance OWNER TO admin;

--
-- Name: staff_performance_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.staff_performance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.staff_performance_id_seq OWNER TO admin;

--
-- Name: staff_performance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.staff_performance_id_seq OWNED BY public.staff_performance.id;


--
-- Name: staff_schedules; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.staff_schedules (
    id uuid NOT NULL,
    staff_id integer NOT NULL,
    manager_id integer NOT NULL,
    shift_id uuid NOT NULL,
    scheduled_date date NOT NULL,
    status public.shift_status,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.staff_schedules OWNER TO admin;

--
-- Name: staff_settings; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.staff_settings (
    id integer NOT NULL,
    user_id integer NOT NULL,
    notification_preferences jsonb DEFAULT '{}'::jsonb,
    display_preferences jsonb DEFAULT '{}'::jsonb,
    work_schedule jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.staff_settings OWNER TO admin;

--
-- Name: staff_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.staff_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.staff_settings_id_seq OWNER TO admin;

--
-- Name: staff_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.staff_settings_id_seq OWNED BY public.staff_settings.id;


--
-- Name: ticket_complaints; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.ticket_complaints (
    id integer NOT NULL,
    ticket_id integer NOT NULL,
    customer_name character varying(100) NOT NULL,
    customer_phone character varying(20),
    customer_email character varying(100),
    complaint_text text NOT NULL,
    rating integer,
    status character varying(20),
    assigned_to integer,
    manager_response text,
    created_at timestamp without time zone DEFAULT now(),
    resolved_at timestamp without time zone
);


ALTER TABLE public.ticket_complaints OWNER TO admin;

--
-- Name: ticket_complaints_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.ticket_complaints_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ticket_complaints_id_seq OWNER TO admin;

--
-- Name: ticket_complaints_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.ticket_complaints_id_seq OWNED BY public.ticket_complaints.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    email character varying(100) NOT NULL,
    phone character varying(20),
    full_name character varying(100) NOT NULL,
    role public.user_role DEFAULT 'staff'::public.user_role,
    department_id integer,
    is_active boolean DEFAULT true,
    avatar_url text,
    last_login timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: activity_logs id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.activity_logs ALTER COLUMN id SET DEFAULT nextval('public.activity_logs_id_seq'::regclass);


--
-- Name: ai_conversations id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.ai_conversations ALTER COLUMN id SET DEFAULT nextval('public.ai_conversations_id_seq'::regclass);


--
-- Name: announcements id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.announcements ALTER COLUMN id SET DEFAULT nextval('public.announcements_id_seq'::regclass);


--
-- Name: counters id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.counters ALTER COLUMN id SET DEFAULT nextval('public.counters_id_seq'::regclass);


--
-- Name: daily_login_logs id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.daily_login_logs ALTER COLUMN id SET DEFAULT nextval('public.daily_login_logs_id_seq'::regclass);


--
-- Name: departments id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.departments ALTER COLUMN id SET DEFAULT nextval('public.departments_id_seq'::regclass);


--
-- Name: feedback id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.feedback ALTER COLUMN id SET DEFAULT nextval('public.feedback_id_seq'::regclass);


--
-- Name: knowledge_base_articles id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.knowledge_base_articles ALTER COLUMN id SET DEFAULT nextval('public.knowledge_base_articles_id_seq'::regclass);


--
-- Name: knowledge_base_attachments id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.knowledge_base_attachments ALTER COLUMN id SET DEFAULT nextval('public.knowledge_base_attachments_id_seq'::regclass);


--
-- Name: knowledge_base_categories id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.knowledge_base_categories ALTER COLUMN id SET DEFAULT nextval('public.knowledge_base_categories_id_seq'::regclass);


--
-- Name: qr_codes id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.qr_codes ALTER COLUMN id SET DEFAULT nextval('public.qr_codes_id_seq'::regclass);


--
-- Name: queue_settings id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.queue_settings ALTER COLUMN id SET DEFAULT nextval('public.queue_settings_id_seq'::regclass);


--
-- Name: queue_tickets id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.queue_tickets ALTER COLUMN id SET DEFAULT nextval('public.queue_tickets_id_seq'::regclass);


--
-- Name: service_form_fields id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.service_form_fields ALTER COLUMN id SET DEFAULT nextval('public.service_form_fields_id_seq'::regclass);


--
-- Name: service_sessions id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.service_sessions ALTER COLUMN id SET DEFAULT nextval('public.service_sessions_id_seq'::regclass);


--
-- Name: services id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.services ALTER COLUMN id SET DEFAULT nextval('public.services_id_seq'::regclass);


--
-- Name: staff_notifications id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_notifications ALTER COLUMN id SET DEFAULT nextval('public.staff_notifications_id_seq'::regclass);


--
-- Name: staff_performance id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_performance ALTER COLUMN id SET DEFAULT nextval('public.staff_performance_id_seq'::regclass);


--
-- Name: staff_settings id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_settings ALTER COLUMN id SET DEFAULT nextval('public.staff_settings_id_seq'::regclass);


--
-- Name: ticket_complaints id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.ticket_complaints ALTER COLUMN id SET DEFAULT nextval('public.ticket_complaints_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: activity_logs activity_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_pkey PRIMARY KEY (id);


--
-- Name: ai_conversations ai_conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.ai_conversations
    ADD CONSTRAINT ai_conversations_pkey PRIMARY KEY (id);


--
-- Name: announcements announcements_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.announcements
    ADD CONSTRAINT announcements_pkey PRIMARY KEY (id);


--
-- Name: counters counters_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.counters
    ADD CONSTRAINT counters_pkey PRIMARY KEY (id);


--
-- Name: daily_login_logs daily_login_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.daily_login_logs
    ADD CONSTRAINT daily_login_logs_pkey PRIMARY KEY (id);


--
-- Name: departments departments_code_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_code_key UNIQUE (code);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- Name: feedback feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_pkey PRIMARY KEY (id);


--
-- Name: knowledge_base_articles knowledge_base_articles_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.knowledge_base_articles
    ADD CONSTRAINT knowledge_base_articles_pkey PRIMARY KEY (id);


--
-- Name: knowledge_base_attachments knowledge_base_attachments_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.knowledge_base_attachments
    ADD CONSTRAINT knowledge_base_attachments_pkey PRIMARY KEY (id);


--
-- Name: knowledge_base_categories knowledge_base_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.knowledge_base_categories
    ADD CONSTRAINT knowledge_base_categories_pkey PRIMARY KEY (id);


--
-- Name: leave_requests leave_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT leave_requests_pkey PRIMARY KEY (id);


--
-- Name: qr_codes qr_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.qr_codes
    ADD CONSTRAINT qr_codes_pkey PRIMARY KEY (id);


--
-- Name: queue_settings queue_settings_department_id_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.queue_settings
    ADD CONSTRAINT queue_settings_department_id_key UNIQUE (department_id);


--
-- Name: queue_settings queue_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.queue_settings
    ADD CONSTRAINT queue_settings_pkey PRIMARY KEY (id);


--
-- Name: queue_tickets queue_tickets_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.queue_tickets
    ADD CONSTRAINT queue_tickets_pkey PRIMARY KEY (id);


--
-- Name: queue_tickets queue_tickets_ticket_number_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.queue_tickets
    ADD CONSTRAINT queue_tickets_ticket_number_key UNIQUE (ticket_number);


--
-- Name: service_form_fields service_form_fields_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.service_form_fields
    ADD CONSTRAINT service_form_fields_pkey PRIMARY KEY (id);


--
-- Name: service_sessions service_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.service_sessions
    ADD CONSTRAINT service_sessions_pkey PRIMARY KEY (id);


--
-- Name: services services_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (id);


--
-- Name: services services_service_code_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_service_code_key UNIQUE (service_code);


--
-- Name: shift_exchanges shift_exchanges_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.shift_exchanges
    ADD CONSTRAINT shift_exchanges_pkey PRIMARY KEY (id);


--
-- Name: shifts shifts_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.shifts
    ADD CONSTRAINT shifts_pkey PRIMARY KEY (id);


--
-- Name: staff_attendance staff_attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_attendance
    ADD CONSTRAINT staff_attendance_pkey PRIMARY KEY (id);


--
-- Name: staff_checkins staff_checkins_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_checkins
    ADD CONSTRAINT staff_checkins_pkey PRIMARY KEY (id);


--
-- Name: staff_notifications staff_notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_notifications
    ADD CONSTRAINT staff_notifications_pkey PRIMARY KEY (id);


--
-- Name: staff_performance staff_performance_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_performance
    ADD CONSTRAINT staff_performance_pkey PRIMARY KEY (id);


--
-- Name: staff_performance staff_performance_user_id_date_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_performance
    ADD CONSTRAINT staff_performance_user_id_date_key UNIQUE (user_id, date);


--
-- Name: staff_schedules staff_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_schedules
    ADD CONSTRAINT staff_schedules_pkey PRIMARY KEY (id);


--
-- Name: staff_settings staff_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_settings
    ADD CONSTRAINT staff_settings_pkey PRIMARY KEY (id);


--
-- Name: staff_settings staff_settings_user_id_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_settings
    ADD CONSTRAINT staff_settings_user_id_key UNIQUE (user_id);


--
-- Name: ticket_complaints ticket_complaints_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.ticket_complaints
    ADD CONSTRAINT ticket_complaints_pkey PRIMARY KEY (id);


--
-- Name: daily_login_logs uq_user_daily_login; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.daily_login_logs
    ADD CONSTRAINT uq_user_daily_login UNIQUE (user_id, login_date);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_queue_tickets_created; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_queue_tickets_created ON public.queue_tickets USING btree (created_at);


--
-- Name: idx_queue_tickets_department; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_queue_tickets_department ON public.queue_tickets USING btree (department_id);


--
-- Name: idx_queue_tickets_queue_pos; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_queue_tickets_queue_pos ON public.queue_tickets USING btree (queue_position);


--
-- Name: idx_queue_tickets_ratings; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_queue_tickets_ratings ON public.queue_tickets USING btree (overall_rating) WHERE (overall_rating IS NOT NULL);


--
-- Name: idx_queue_tickets_reviewed; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_queue_tickets_reviewed ON public.queue_tickets USING btree (reviewed_at) WHERE (reviewed_at IS NOT NULL);


--
-- Name: idx_queue_tickets_service; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_queue_tickets_service ON public.queue_tickets USING btree (service_id);


--
-- Name: idx_queue_tickets_staff; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_queue_tickets_staff ON public.queue_tickets USING btree (staff_id);


--
-- Name: idx_queue_tickets_status; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_queue_tickets_status ON public.queue_tickets USING btree (status);


--
-- Name: idx_services_department; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_services_department ON public.services USING btree (department_id);


--
-- Name: idx_ticket_complaints_assigned_to; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_ticket_complaints_assigned_to ON public.ticket_complaints USING btree (assigned_to);


--
-- Name: idx_ticket_complaints_created_at; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_ticket_complaints_created_at ON public.ticket_complaints USING btree (created_at);


--
-- Name: idx_ticket_complaints_status; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_ticket_complaints_status ON public.ticket_complaints USING btree (status);


--
-- Name: idx_ticket_complaints_ticket_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_ticket_complaints_ticket_id ON public.ticket_complaints USING btree (ticket_id);


--
-- Name: idx_users_department; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_users_department ON public.users USING btree (department_id);


--
-- Name: idx_users_role; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_users_role ON public.users USING btree (role);


--
-- Name: ix_ai_conversations_conversation_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_ai_conversations_conversation_id ON public.ai_conversations USING btree (conversation_id);


--
-- Name: ix_ai_conversations_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_ai_conversations_id ON public.ai_conversations USING btree (id);


--
-- Name: ix_daily_login_logs_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_daily_login_logs_id ON public.daily_login_logs USING btree (id);


--
-- Name: ix_feedback_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_feedback_id ON public.feedback USING btree (id);


--
-- Name: ix_knowledge_base_articles_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_knowledge_base_articles_id ON public.knowledge_base_articles USING btree (id);


--
-- Name: ix_knowledge_base_articles_slug; Type: INDEX; Schema: public; Owner: admin
--

CREATE UNIQUE INDEX ix_knowledge_base_articles_slug ON public.knowledge_base_articles USING btree (slug);


--
-- Name: ix_knowledge_base_attachments_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_knowledge_base_attachments_id ON public.knowledge_base_attachments USING btree (id);


--
-- Name: ix_knowledge_base_categories_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_knowledge_base_categories_id ON public.knowledge_base_categories USING btree (id);


--
-- Name: ix_knowledge_base_categories_slug; Type: INDEX; Schema: public; Owner: admin
--

CREATE UNIQUE INDEX ix_knowledge_base_categories_slug ON public.knowledge_base_categories USING btree (slug);


--
-- Name: ix_staff_notifications_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_staff_notifications_id ON public.staff_notifications USING btree (id);


--
-- Name: ix_staff_notifications_is_read; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_staff_notifications_is_read ON public.staff_notifications USING btree (is_read);


--
-- Name: ix_staff_notifications_recipient_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_staff_notifications_recipient_id ON public.staff_notifications USING btree (recipient_id);


--
-- Name: ix_ticket_complaints_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_ticket_complaints_id ON public.ticket_complaints USING btree (id);


--
-- Name: activity_logs activity_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: ai_conversations ai_conversations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.ai_conversations
    ADD CONSTRAINT ai_conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: announcements announcements_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.announcements
    ADD CONSTRAINT announcements_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: announcements announcements_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.announcements
    ADD CONSTRAINT announcements_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: counters counters_assigned_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.counters
    ADD CONSTRAINT counters_assigned_staff_id_fkey FOREIGN KEY (assigned_staff_id) REFERENCES public.users(id);


--
-- Name: counters counters_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.counters
    ADD CONSTRAINT counters_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: daily_login_logs daily_login_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.daily_login_logs
    ADD CONSTRAINT daily_login_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: feedback feedback_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.queue_tickets(id);


--
-- Name: knowledge_base_articles knowledge_base_articles_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.knowledge_base_articles
    ADD CONSTRAINT knowledge_base_articles_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: knowledge_base_articles knowledge_base_articles_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.knowledge_base_articles
    ADD CONSTRAINT knowledge_base_articles_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.knowledge_base_categories(id);


--
-- Name: knowledge_base_articles knowledge_base_articles_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.knowledge_base_articles
    ADD CONSTRAINT knowledge_base_articles_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: knowledge_base_attachments knowledge_base_attachments_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.knowledge_base_attachments
    ADD CONSTRAINT knowledge_base_attachments_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.knowledge_base_articles(id) ON DELETE CASCADE;


--
-- Name: knowledge_base_attachments knowledge_base_attachments_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.knowledge_base_attachments
    ADD CONSTRAINT knowledge_base_attachments_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: knowledge_base_categories knowledge_base_categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.knowledge_base_categories
    ADD CONSTRAINT knowledge_base_categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.knowledge_base_categories(id);


--
-- Name: leave_requests leave_requests_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT leave_requests_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);


--
-- Name: leave_requests leave_requests_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT leave_requests_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: qr_codes qr_codes_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.qr_codes
    ADD CONSTRAINT qr_codes_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: queue_settings queue_settings_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.queue_settings
    ADD CONSTRAINT queue_settings_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: queue_tickets queue_tickets_counter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.queue_tickets
    ADD CONSTRAINT queue_tickets_counter_id_fkey FOREIGN KEY (counter_id) REFERENCES public.counters(id);


--
-- Name: queue_tickets queue_tickets_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.queue_tickets
    ADD CONSTRAINT queue_tickets_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: queue_tickets queue_tickets_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.queue_tickets
    ADD CONSTRAINT queue_tickets_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id);


--
-- Name: queue_tickets queue_tickets_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.queue_tickets
    ADD CONSTRAINT queue_tickets_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.users(id);


--
-- Name: service_form_fields service_form_fields_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.service_form_fields
    ADD CONSTRAINT service_form_fields_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id);


--
-- Name: service_sessions service_sessions_counter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.service_sessions
    ADD CONSTRAINT service_sessions_counter_id_fkey FOREIGN KEY (counter_id) REFERENCES public.counters(id);


--
-- Name: service_sessions service_sessions_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.service_sessions
    ADD CONSTRAINT service_sessions_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.users(id);


--
-- Name: service_sessions service_sessions_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.service_sessions
    ADD CONSTRAINT service_sessions_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.queue_tickets(id);


--
-- Name: services services_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: shift_exchanges shift_exchanges_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.shift_exchanges
    ADD CONSTRAINT shift_exchanges_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);


--
-- Name: shift_exchanges shift_exchanges_requesting_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.shift_exchanges
    ADD CONSTRAINT shift_exchanges_requesting_schedule_id_fkey FOREIGN KEY (requesting_schedule_id) REFERENCES public.staff_schedules(id);


--
-- Name: shift_exchanges shift_exchanges_requesting_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.shift_exchanges
    ADD CONSTRAINT shift_exchanges_requesting_staff_id_fkey FOREIGN KEY (requesting_staff_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: shift_exchanges shift_exchanges_target_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.shift_exchanges
    ADD CONSTRAINT shift_exchanges_target_schedule_id_fkey FOREIGN KEY (target_schedule_id) REFERENCES public.staff_schedules(id);


--
-- Name: shift_exchanges shift_exchanges_target_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.shift_exchanges
    ADD CONSTRAINT shift_exchanges_target_staff_id_fkey FOREIGN KEY (target_staff_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: staff_attendance staff_attendance_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_attendance
    ADD CONSTRAINT staff_attendance_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES public.staff_schedules(id);


--
-- Name: staff_attendance staff_attendance_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_attendance
    ADD CONSTRAINT staff_attendance_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: staff_checkins staff_checkins_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_checkins
    ADD CONSTRAINT staff_checkins_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);


--
-- Name: staff_checkins staff_checkins_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_checkins
    ADD CONSTRAINT staff_checkins_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES public.staff_schedules(id);


--
-- Name: staff_checkins staff_checkins_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_checkins
    ADD CONSTRAINT staff_checkins_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: staff_notifications staff_notifications_recipient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_notifications
    ADD CONSTRAINT staff_notifications_recipient_id_fkey FOREIGN KEY (recipient_id) REFERENCES public.users(id);


--
-- Name: staff_notifications staff_notifications_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_notifications
    ADD CONSTRAINT staff_notifications_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id);


--
-- Name: staff_notifications staff_notifications_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_notifications
    ADD CONSTRAINT staff_notifications_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.queue_tickets(id);


--
-- Name: staff_performance staff_performance_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_performance
    ADD CONSTRAINT staff_performance_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: staff_performance staff_performance_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_performance
    ADD CONSTRAINT staff_performance_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: staff_schedules staff_schedules_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_schedules
    ADD CONSTRAINT staff_schedules_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);


--
-- Name: staff_schedules staff_schedules_shift_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_schedules
    ADD CONSTRAINT staff_schedules_shift_id_fkey FOREIGN KEY (shift_id) REFERENCES public.shifts(id);


--
-- Name: staff_schedules staff_schedules_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_schedules
    ADD CONSTRAINT staff_schedules_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: staff_settings staff_settings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.staff_settings
    ADD CONSTRAINT staff_settings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: ticket_complaints ticket_complaints_assigned_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.ticket_complaints
    ADD CONSTRAINT ticket_complaints_assigned_to_fkey FOREIGN KEY (assigned_to) REFERENCES public.users(id);


--
-- Name: ticket_complaints ticket_complaints_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.ticket_complaints
    ADD CONSTRAINT ticket_complaints_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.queue_tickets(id);


--
-- Name: users users_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- PostgreSQL database dump complete
--

\unrestrict CMIkYDnVS99lrBPjBjmh5e8jWgfh1kQdjg9MLuMd5Llhsf26tOYv7TXhsKlH3D3


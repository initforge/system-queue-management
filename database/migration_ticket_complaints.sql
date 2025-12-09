-- Migration for ticket_complaints table
-- This creates the ticket complaints system for manager dashboard

CREATE TABLE IF NOT EXISTS ticket_complaints (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES queue_tickets(id) ON DELETE CASCADE,
    customer_name VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20),
    complaint_text TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    status VARCHAR(50) NOT NULL DEFAULT 'waiting' CHECK (status IN ('waiting', 'processing', 'completed')),
    assigned_to INTEGER REFERENCES users(id) ON DELETE SET NULL,
    manager_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_ticket_complaints_status ON ticket_complaints(status);
CREATE INDEX IF NOT EXISTS idx_ticket_complaints_assigned_to ON ticket_complaints(assigned_to);
CREATE INDEX IF NOT EXISTS idx_ticket_complaints_created_at ON ticket_complaints(created_at);
CREATE INDEX IF NOT EXISTS idx_ticket_complaints_ticket_id ON ticket_complaints(ticket_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_ticket_complaints_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_update_ticket_complaints_updated_at
    BEFORE UPDATE ON ticket_complaints
    FOR EACH ROW
    EXECUTE FUNCTION update_ticket_complaints_updated_at();

-- Insert some sample data for testing
INSERT INTO ticket_complaints (ticket_id, customer_name, customer_phone, complaint_text, rating, status, assigned_to) VALUES
(1, 'Nguyễn Văn A', '0123456789', 'Thời gian chờ quá lâu, nhân viên không thân thiện', 2, 'waiting', 2),
(2, 'Trần Thị B', '0987654321', 'Dịch vụ tốt nhưng cần cải thiện thời gian xử lý', 4, 'waiting', 2),
(3, 'Lê Văn C', '0345678901', 'Rất hài lòng với dịch vụ, nhân viên nhiệt tình', 5, 'completed', 2);

COMMIT;
// Schedule API Service
// Handles API calls for schedule management

import { ApiClient } from './client';

const api = new ApiClient();
const SCHEDULE_API_BASE = '/schedule';

class ScheduleAPIService {
    
    // Get all shifts
    async getShifts() {
        try {
            return await api.get(`${SCHEDULE_API_BASE}/shifts`);
        } catch (error) {
            console.error('Error fetching shifts:', error);
            throw error;
        }
    }

    // Bulk schedule operations
    async bulkCreateSchedules(schedules) {
        try {
            return await api.post(`${SCHEDULE_API_BASE}/bulk`, { schedules });
        } catch (error) {
            console.error('Error bulk creating schedules:', error);
            throw error;
        }
    }
    
    // Schedule CRUD operations
    async getWeeklySchedule(startDate, staffId = null) {
        try {
            const params = new URLSearchParams({ start_date: startDate });
            if (staffId) {
                params.append('staff_id', staffId);
            }
            
            return await api.get(`${SCHEDULE_API_BASE}/week?${params}`);
        } catch (error) {
            console.error('Error fetching weekly schedule:', error);
            throw error;
        }
    }

    async createSchedule(scheduleData) {
        try {
            return await api.post(`${SCHEDULE_API_BASE}/`, scheduleData);
        } catch (error) {
            console.error('Error creating schedule:', error);
            throw error;
        }
    }

    async updateSchedule(scheduleId, scheduleData) {
        try {
            return await api.put(`${SCHEDULE_API_BASE}/${scheduleId}`, scheduleData);
        } catch (error) {
            console.error('Error updating schedule:', error);
            throw error;
        }
    }

    async deleteSchedule(scheduleId) {
        try {
            return await api.delete(`${SCHEDULE_API_BASE}/${scheduleId}`);
        } catch (error) {
            console.error('Error deleting schedule:', error);
            throw error;
        }
    }

    // Leave Request operations
    async getLeaveRequests(statusFilter = null, staffId = null) {
        try {
            const params = new URLSearchParams();
            if (statusFilter) params.append('status_filter', statusFilter);
            if (staffId) params.append('staff_id', staffId);
            
            return await api.get(`${SCHEDULE_API_BASE}/leave-requests?${params}`);
        } catch (error) {
            console.error('Error fetching leave requests:', error);
            throw error;
        }
    }

    async createLeaveRequest(leaveRequestData) {
        try {
            return await api.post(`${SCHEDULE_API_BASE}/leave-requests`, leaveRequestData);
        } catch (error) {
            console.error('Error creating leave request:', error);
            throw error;
        }
    }

    async updateLeaveRequest(requestId, updateData) {
        try {
            return await api.put(`${SCHEDULE_API_BASE}/leave-requests/${requestId}`, updateData);
        } catch (error) {
            console.error('Error updating leave request:', error);
            throw error;
        }
    }

    async deleteLeaveRequest(requestId) {
        try {
            return await api.delete(`${SCHEDULE_API_BASE}/leave-requests/${requestId}`);
        } catch (error) {
            console.error('Error deleting leave request:', error);
            throw error;
        }
    }

    // Check-in operations
    async getCheckins(statusFilter = null) {
        try {
            const params = statusFilter ? `?status_filter=${statusFilter}` : '';
            return await api.get(`${SCHEDULE_API_BASE}/checkins${params}`);
        } catch (error) {
            console.error('Error fetching checkins:', error);
            throw error;
        }
    }

    async createCheckin(checkinData) {
        try {
            return await api.post(`${SCHEDULE_API_BASE}/checkins`, checkinData);
        } catch (error) {
            console.error('Error creating checkin:', error);
            throw error;
        }
    }

    async updateCheckin(checkinId, updateData) {
        try {
            return await api.put(`${SCHEDULE_API_BASE}/checkins/${checkinId}`, updateData);
        } catch (error) {
            console.error('Error updating checkin:', error);
            throw error;
        }
    }

    // Shift Exchange operations
    async getShiftExchanges(statusFilter = null) {
        try {
            const params = statusFilter ? `?status_filter=${statusFilter}` : '';
            return await api.get(`${SCHEDULE_API_BASE}/shift-exchanges${params}`);
        } catch (error) {
            console.error('Error fetching shift exchanges:', error);
            throw error;
        }
    }

    async createShiftExchange(exchangeData) {
        try {
            return await api.post(`${SCHEDULE_API_BASE}/shift-exchanges`, exchangeData);
        } catch (error) {
            console.error('Error creating shift exchange:', error);
            throw error;
        }
    }

    async updateShiftExchange(exchangeId, updateData) {
        try {
            return await api.put(`${SCHEDULE_API_BASE}/shift-exchanges/${exchangeId}`, updateData);
        } catch (error) {
            console.error('Error updating shift exchange:', error);
            throw error;
        }
    }

    // Staff Pool operations
    async getStaffPool(departmentId = null) {
        try {
            const params = departmentId ? `?department_id=${departmentId}` : '';
            return await api.get(`${SCHEDULE_API_BASE}/staff-pool${params}`);
        } catch (error) {
            console.error('Error fetching staff pool:', error);
            throw error;
        }
    }

    // Attendance operations
    async getAttendanceRecords(startDate, endDate, staffId = null) {
        try {
            const params = new URLSearchParams({
                start_date: startDate,
                end_date: endDate
            });
            if (staffId) params.append('staff_id', staffId);
            
            return await api.get(`${SCHEDULE_API_BASE}/attendance?${params}`);
        } catch (error) {
            console.error('Error fetching attendance records:', error);
            throw error;
        }
    }

    async createAttendanceRecord(attendanceData) {
        try {
            return await api.post(`${SCHEDULE_API_BASE}/attendance`, attendanceData);
        } catch (error) {
            console.error('Error creating attendance record:', error);
            throw error;
        }
    }

    // Stats and analytics
    async getScheduleStats(startDate, endDate, departmentId = null) {
        try {
            const params = new URLSearchParams({
                start_date: startDate,
                end_date: endDate
            });
            if (departmentId) params.append('department_id', departmentId);
            
            return await api.get(`${SCHEDULE_API_BASE}/stats?${params}`);
        } catch (error) {
            console.error('Error fetching schedule stats:', error);
            throw error;
        }
    }

    // Staff Statistics
    async getStaffStatistics(staffId, startDate = null, endDate = null) {
        try {
            const params = new URLSearchParams();
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);
            
            const queryString = params.toString();
            return await api.get(`${SCHEDULE_API_BASE}/staff-statistics/${staffId}${queryString ? '?' + queryString : ''}`);
        } catch (error) {
            console.error('Error fetching staff statistics:', error);
            throw error;
        }
    }

    // Department Statistics
    async getDepartmentStatistics(startDate = null, endDate = null) {
        try {
            const params = new URLSearchParams();
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);
            
            const queryString = params.toString();
            return await api.get(`${SCHEDULE_API_BASE}/department-statistics${queryString ? '?' + queryString : ''}`);
        } catch (error) {
            console.error('Error fetching department statistics:', error);
            throw error;
        }
    }

    // Helper methods for common operations
    
    // Get current week schedule
    async getCurrentWeekSchedule(staffId = null) {
        const today = new Date();
        const monday = new Date(today.setDate(today.getDate() - today.getDay() + 1));
        const startDate = monday.toISOString().split('T')[0];
        
        return this.getWeeklySchedule(startDate, staffId);
    }

    // Get next week schedule
    async getNextWeekSchedule(staffId = null) {
        const today = new Date();
        const nextMonday = new Date(today.setDate(today.getDate() - today.getDay() + 8));
        const startDate = nextMonday.toISOString().split('T')[0];
        
        return this.getWeeklySchedule(startDate, staffId);
    }

    // Submit staff check-in request
    async submitCheckinRequest(location = '', notes = '') {
        return this.createCheckin({
            request_time: new Date().toISOString(),
            location,
            notes
        });
    }

    // Quick leave request submission
    async submitLeaveRequest(startDate, endDate, leaveType, reason) {
        return this.createLeaveRequest({
            start_date: startDate,
            end_date: endDate,
            leave_type: leaveType,
            reason
        });
    }

    // Approve/Reject leave request (Manager only)
    async reviewLeaveRequest(requestId, action, notes = '') {
        return this.updateLeaveRequest(requestId, {
            status: action, // 'approved' or 'rejected'
            notes
        });
    }

    // Approve/Reject check-in (Manager only)
    async reviewCheckin(checkinId, action, notes = '') {
        return this.updateCheckin(checkinId, {
            status: action, // 'approved' or 'rejected'  
            notes
        });
    }
}

// Create singleton instance
const scheduleAPI = new ScheduleAPIService();

export default scheduleAPI;
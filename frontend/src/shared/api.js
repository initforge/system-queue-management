
import { useState, useCallback } from 'react';

// Use backend URL directly since we have CORS enabled
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
console.log('API_BASE_URL loaded:', API_BASE_URL);

class ApiService {
  // Helper method for making requests
  async makeRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    console.log('API makeRequest - URL:', url, 'endpoint:', endpoint, 'API_BASE_URL:', API_BASE_URL);
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'API request failed');
      }

      return data;
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Authentication
  async login(email, password) {
    return this.makeRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async logout() {
    localStorage.removeItem('token');
    return { success: true };
  }

  async getProfile() {
    return this.makeRequest('/auth/me');
  }

  async updateProfile(userData) {
    return this.makeRequest('/auth/me', {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  // Departments
  async getDepartments(includeInactive = false) {
    return this.makeRequest(`/departments?include_inactive=${includeInactive}`);
  }

  async getDepartment(id) {
    return this.makeRequest(`/departments/${id}`);
  }

  async getDepartmentByCode(code) {
    return this.makeRequest(`/departments/code/${code}`);
  }

  // Services
  async getDepartmentServices(departmentId) {
    return this.makeRequest(`/services?department_id=${departmentId}`);
  }

  async getService(serviceId) {
    return this.makeRequest(`/services/${serviceId}`);
  }

  async getAllServices() {
    return this.makeRequest('/services');
  }

  // Tickets
  async createTicket(ticketData) {
    return this.makeRequest('/tickets', {
      method: 'POST',
      body: JSON.stringify(ticketData),
    });
  }

  async getTicket(ticketId) {
    return this.makeRequest(`/tickets/${ticketId}`);
  }

  async getTicketStatus(ticketId) {
    return this.makeRequest(`/tickets/${ticketId}/status`);
  }

  async cancelTicket(ticketId) {
    return this.makeRequest(`/tickets/${ticketId}/cancel`, {
      method: 'POST'
    });
  }

  async getTicketByNumber(ticketNumber) {
    return this.makeRequest(`/tickets/number/${ticketNumber}`);
  }

  async getDepartmentQueue(departmentId, status = null) {
    const params = status ? `?status=${status}` : '';
    return this.makeRequest(`/tickets/department/${departmentId}${params}`);
  }

  async updateTicketStatus(ticketId, status) {
    return this.makeRequest(`/tickets/${ticketId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  async getNextTicket() {
    return this.makeRequest('/tickets/next', {
      method: 'POST',
    });
  }

  // Dashboard (Admin/Manager)
  async getDashboardStats() {
    return this.makeRequest('/dashboard/stats');
  }

  // QR Codes
  async getQRCode(serviceId) {
    return this.makeRequest(`/qr-codes/service/${serviceId}`);
  }

  // Feedback & Complaints
  async submitFeedback(feedbackData) {
    return this.makeRequest('/feedback/submit', {
      method: 'POST',
      body: JSON.stringify(feedbackData),
    });
  }

  async submitComplaint(complaintData) {
    return this.makeRequest('/feedback/complaint', {
      method: 'POST',
      body: JSON.stringify(complaintData),
    });
  }

  async getFeedbackList(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        params.append(key, value);
      }
    });
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.makeRequest(`/feedback/list${query}`);
  }

  async getComplaintList(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        params.append(key, value);
      }
    });
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.makeRequest(`/feedback/complaints${query}`);
  }

  async resolveComplaint(complaintId, resolutionNotes) {
    return this.makeRequest(`/manager/complaints/${complaintId}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ response: resolutionNotes || '' }),
    });
  }

  async getFeedbackStats(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        params.append(key, value);
      }
    });
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.makeRequest(`/feedback/stats${query}`);
  }

  // Health check
  async healthCheck() {
    return fetch(`${API_BASE_URL}/health`).then(r => r.json());
  }

  // ===== STAFF APIs =====
  async getStaffQueue() {
    return this.makeRequest('/staff/queue');
  }

  async callNextTicket() {
    return this.makeRequest('/staff/queue/call-next', { method: 'POST' });
  }

  async startServingTicket(ticketId) {
    return this.makeRequest(`/staff/tickets/${ticketId}/serve`, { method: 'PUT' });
  }

  async completeTicket(ticketId, completionData) {
    return this.makeRequest(`/staff/tickets/${ticketId}/complete`, {
      method: 'PUT',
      body: JSON.stringify(completionData)
    });
  }

  async getStaffPerformanceToday() {
    return this.makeRequest('/staff/performance/today');
  }

  async getStaffPerformanceHistory(days = 7) {
    return this.makeRequest(`/staff/performance/history?days=${days}`);
  }

  // ===== MANAGER APIs =====
  async getDepartmentStats(departmentId, period = 'today') {
    return this.makeRequest(`/manager/stats/${departmentId}?period=${period}`);
  }

  async getStaffPerformanceList(departmentId) {
    return this.makeRequest(`/manager/staff/performance/${departmentId}`);
  }

  async getManagerComplaintList(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        params.append(key, value);
      }
    });
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.makeRequest(`/manager/complaints${query}`);
  }

  async resolveManagerComplaint(complaintId, resolutionNotes) {
    return this.makeRequest(`/manager/complaints/${complaintId}/resolve`, {
      method: 'PUT',
      body: JSON.stringify({ resolution_notes: resolutionNotes })
    });
  }

  async generateReport(reportData) {
    return this.makeRequest('/manager/reports/generate', {
      method: 'POST',
      body: JSON.stringify(reportData)
    });
  }

  // ===== ADMIN APIs =====
  async getSystemStats() {
    return this.makeRequest('/admin/stats/system');
  }

  async getAllUsers(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        params.append(key, value);
      }
    });
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.makeRequest(`/admin/users${query}`);
  }

  async createUser(userData) {
    return this.makeRequest('/admin/users', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  }

  async updateUser(userId, userData) {
    return this.makeRequest(`/admin/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData)
    });
  }

  async deleteUser(userId) {
    return this.makeRequest(`/admin/users/${userId}`, { method: 'DELETE' });
  }

  async getAllDepartments() {
    return this.makeRequest('/admin/departments');
  }

  async getSystemConfig() {
    return this.makeRequest('/admin/config/system');
  }

  async updateSystemConfig(configData) {
    return this.makeRequest('/admin/config/system', {
      method: 'PUT',
      body: JSON.stringify(configData)
    });
  }

  async getSecurityLogs(limit = 50) {
    return this.makeRequest(`/admin/logs/security?limit=${limit}`);
  }

  async getAllBranches() {
    return this.makeRequest('/admin/branches');
  }
}

const apiService = new ApiService();

// Custom Admin Dashboard Hook
export const useAdminDashboard = () => {
  const [departments, setDepartments] = useState([]);
  const [users, setUsers] = useState([]);
  const [systemStats, setSystemStats] = useState(null);
  const [loading, setLoading] = useState({
    departments: false,
    users: false,
    stats: false
  });
  const [error, setError] = useState(null);

  // Fetch departments
  const fetchDepartments = useCallback(async () => {
    setLoading(prev => ({ ...prev, departments: true }));
    setError(null);
    try {
      const response = await apiService.getAllDepartments();
      setDepartments(response);
    } catch (err) {
      setError(`Error fetching departments: ${err.message}`);
      console.error('Failed to fetch departments:', err);
    } finally {
      setLoading(prev => ({ ...prev, departments: false }));
    }
  }, []);

  // Fetch all users
  const fetchUsers = useCallback(async () => {
    setLoading(prev => ({ ...prev, users: true }));
    setError(null);
    try {
      const response = await apiService.getAllUsers();
      setUsers(response);
    } catch (err) {
      setError(`Error fetching users: ${err.message}`);
      console.error('Failed to fetch users:', err);
    } finally {
      setLoading(prev => ({ ...prev, users: false }));
    }
  }, []);

  // Fetch system stats
  const fetchSystemStats = useCallback(async () => {
    setLoading(prev => ({ ...prev, stats: true }));
    setError(null);
    try {
      const response = await apiService.getSystemStats();
      setSystemStats(response);
    } catch (err) {
      setError(`Error fetching system stats: ${err.message}`);
      console.error('Failed to fetch system stats:', err);
    } finally {
      setLoading(prev => ({ ...prev, stats: false }));
    }
  }, []);

  // Create a new department
  const createDepartment = async (departmentData) => {
    setLoading(prev => ({ ...prev, departments: true }));
    setError(null);
    try {
      const response = await apiService.makeRequest('/admin/departments', {
        method: 'POST',
        body: JSON.stringify(departmentData)
      });
      // Update departments list
      fetchDepartments();
      return response;
    } catch (err) {
      setError(`Error creating department: ${err.message}`);
      console.error('Failed to create department:', err);
      throw err;
    } finally {
      setLoading(prev => ({ ...prev, departments: false }));
    }
  };

  // Update a department
  const updateDepartment = async (departmentId, departmentData) => {
    setLoading(prev => ({ ...prev, departments: true }));
    setError(null);
    try {
      const response = await apiService.makeRequest(`/admin/departments/${departmentId}`, {
        method: 'PUT',
        body: JSON.stringify(departmentData)
      });
      // Update departments list
      fetchDepartments();
      return response;
    } catch (err) {
      setError(`Error updating department: ${err.message}`);
      console.error('Failed to update department:', err);
      throw err;
    } finally {
      setLoading(prev => ({ ...prev, departments: false }));
    }
  };

  // Delete a department
  const deleteDepartment = async (departmentId) => {
    setLoading(prev => ({ ...prev, departments: true }));
    setError(null);
    try {
      await apiService.makeRequest(`/admin/departments/${departmentId}`, {
        method: 'DELETE'
      });
      // Update departments list
      fetchDepartments();
      return true;
    } catch (err) {
      setError(`Error deleting department: ${err.message}`);
      console.error('Failed to delete department:', err);
      throw err;
    } finally {
      setLoading(prev => ({ ...prev, departments: false }));
    }
  };

  // Create a user
  const createUser = async (userData) => {
    setLoading(prev => ({ ...prev, users: true }));
    setError(null);
    try {
      const response = await apiService.createUser(userData);
      // Update users list
      fetchUsers();
      return response;
    } catch (err) {
      setError(`Error creating user: ${err.message}`);
      console.error('Failed to create user:', err);
      throw err;
    } finally {
      setLoading(prev => ({ ...prev, users: false }));
    }
  };

  // Update a user
  const updateUser = async (userId, userData) => {
    setLoading(prev => ({ ...prev, users: true }));
    setError(null);
    try {
      const response = await apiService.updateUser(userId, userData);
      // Update users list
      fetchUsers();
      return response;
    } catch (err) {
      setError(`Error updating user: ${err.message}`);
      console.error('Failed to update user:', err);
      throw err;
    } finally {
      setLoading(prev => ({ ...prev, users: false }));
    }
  };

  // Delete a user
  const deleteUser = async (userId) => {
    setLoading(prev => ({ ...prev, users: true }));
    setError(null);
    try {
      await apiService.deleteUser(userId);
      // Update users list
      fetchUsers();
      return true;
    } catch (err) {
      setError(`Error deleting user: ${err.message}`);
      console.error('Failed to delete user:', err);
      throw err;
    } finally {
      setLoading(prev => ({ ...prev, users: false }));
    }
  };

  // Return all the necessary data and functions
  return {
    departments,
    users,
    systemStats,
    loading,
    error,
    fetchDepartments,
    fetchUsers,
    fetchSystemStats,
    createDepartment,
    updateDepartment,
    deleteDepartment,
    createUser,
    updateUser,
    deleteUser
  };
};

export default apiService;

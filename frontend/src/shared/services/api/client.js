// API Client - Axios instance with interceptors
import axios from 'axios';

// Direct backend URL in development (no nginx proxy)
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      const { status, data } = error.response;
      
      if (status === 401) {
        // Unauthorized - clear token and redirect to login
        localStorage.removeItem('token');
        window.location.href = '/';
      }
      
      console.error('API Error:', {
        status,
        message: data.detail || data.message || 'Unknown error',
        url: error.config.url,
      });
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// Export ApiClient class for compatibility
export class ApiClient {
  async get(url, config) {
    const response = await apiClient.get(url, config);
    return response.data;
  }

  async post(url, data, config) {
    const response = await apiClient.post(url, data, config);
    return response.data;
  }

  async put(url, data, config) {
    const response = await apiClient.put(url, data, config);
    return response.data;
  }

  async delete(url, config) {
    const response = await apiClient.delete(url, config);
    return response.data;
  }

  async patch(url, data, config) {
    const response = await apiClient.patch(url, data, config);
    return response.data;
  }

  async postFormData(url, formData, config) {
    const response = await apiClient.post(url, formData, {
      ...config,
      headers: {
        ...config?.headers,
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Manager-specific methods
  async resolveComplaint(complaintId, resolutionNotes) {
    return this.post(`manager/complaints/${complaintId}/resolve`, {
      response: resolutionNotes || ''
    });
  }
}

export default apiClient;

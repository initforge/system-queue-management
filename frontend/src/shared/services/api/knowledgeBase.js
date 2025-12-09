// Knowledge Base API Service
import { ApiClient } from './client';

const api = new ApiClient();
const KB_API_BASE = '/knowledge-base';

class KnowledgeBaseAPIService {
    // Categories
    async getCategories(includeInactive = false) {
        try {
            const params = includeInactive ? '?include_inactive=true' : '';
            return await api.get(`${KB_API_BASE}/categories${params}`);
        } catch (error) {
            console.error('Error fetching categories:', error);
            throw error;
        }
    }

    async createCategory(categoryData) {
        try {
            return await api.post(`${KB_API_BASE}/categories`, categoryData);
        } catch (error) {
            console.error('Error creating category:', error);
            throw error;
        }
    }

    // Articles
    async getArticles(filters = {}) {
        try {
            const params = new URLSearchParams();
            if (filters.categoryId) params.append('category_id', filters.categoryId);
            if (filters.departmentId) params.append('department_id', filters.departmentId);
            if (filters.publishedOnly !== undefined) params.append('published_only', filters.publishedOnly);
            if (filters.featured !== undefined) params.append('featured', filters.featured);
            if (filters.search) params.append('search', filters.search);
            if (filters.limit) params.append('limit', filters.limit);
            if (filters.offset) params.append('offset', filters.offset);
            
            const queryString = params.toString();
            return await api.get(`${KB_API_BASE}/articles${queryString ? '?' + queryString : ''}`);
        } catch (error) {
            console.error('Error fetching articles:', error);
            throw error;
        }
    }

    async getArticle(articleId) {
        try {
            return await api.get(`${KB_API_BASE}/articles/${articleId}`);
        } catch (error) {
            console.error('Error fetching article:', error);
            throw error;
        }
    }

    async createArticle(articleData) {
        try {
            return await api.post(`${KB_API_BASE}/articles`, articleData);
        } catch (error) {
            console.error('Error creating article:', error);
            throw error;
        }
    }

    async updateArticle(articleId, articleData) {
        try {
            return await api.put(`${KB_API_BASE}/articles/${articleId}`, articleData);
        } catch (error) {
            console.error('Error updating article:', error);
            throw error;
        }
    }

    async deleteArticle(articleId) {
        try {
            return await api.delete(`${KB_API_BASE}/articles/${articleId}`);
        } catch (error) {
            console.error('Error deleting article:', error);
            throw error;
        }
    }

    async uploadAttachment(articleId, file) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const apiClient = new ApiClient();
            return await apiClient.postFormData(`${KB_API_BASE}/articles/${articleId}/upload`, formData);
        } catch (error) {
            console.error('Error uploading attachment:', error);
            throw error;
        }
    }

    // Search
    async searchArticles(query, limit = 20) {
        try {
            return await api.get(`${KB_API_BASE}/search?q=${encodeURIComponent(query)}&limit=${limit}`);
        } catch (error) {
            console.error('Error searching articles:', error);
            throw error;
        }
    }
}

const knowledgeBaseAPI = new KnowledgeBaseAPIService();
export default knowledgeBaseAPI;


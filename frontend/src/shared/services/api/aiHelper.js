// AI Helper API Service
import { ApiClient } from './client';

const api = new ApiClient();
const AI_HELPER_API_BASE = '/ai-helper';

class AIHelperAPIService {
    async sendMessage(message, conversationId = null, context = null) {
        try {
            return await api.post(`${AI_HELPER_API_BASE}/chat`, {
                message,
                conversation_id: conversationId,
                context
            });
        } catch (error) {
            console.error('Error sending message to AI:', error);
            throw error;
        }
    }

    async getConversations(conversationId = null, limit = 50) {
        try {
            const params = new URLSearchParams({ limit: limit.toString() });
            if (conversationId) params.append('conversation_id', conversationId);
            
            return await api.get(`${AI_HELPER_API_BASE}/conversations?${params}`);
        } catch (error) {
            console.error('Error fetching conversations:', error);
            throw error;
        }
    }

    async getContext() {
        try {
            return await api.get(`${AI_HELPER_API_BASE}/context`);
        } catch (error) {
            console.error('Error fetching context:', error);
            throw error;
        }
    }
}

const aiHelperAPI = new AIHelperAPIService();
export default aiHelperAPI;


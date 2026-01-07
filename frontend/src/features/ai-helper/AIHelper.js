import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion } from 'framer-motion';
import aiHelperAPI from '../../shared/services/api/aiHelper';
import MessageList from './components/MessageList';
import ContextPanel from './components/ContextPanel';
import ApiKeyModal from './components/ApiKeyModal';

const GEMINI_API_KEY_STORAGE = 'gemini_api_key';

const AIHelper = ({ role = 'staff' }) => {
  const [messages, setMessages] = useState([]);
  const [messageInput, setMessageInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [context, setContext] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const messagesEndRef = useRef(null);

  // Load API key from LocalStorage on mount
  useEffect(() => {
    const savedApiKey = localStorage.getItem(GEMINI_API_KEY_STORAGE);
    if (savedApiKey) {
      setApiKey(savedApiKey);
    } else {
      // Show modal if no API key is saved
      setShowApiKeyModal(true);
    }
  }, []);
  const [suggestedQuestions] = useState([
    'Hôm nay tôi đã phục vụ bao nhiêu khách?',
    'Lịch làm việc tuần này của tôi?',
    'Hướng dẫn gọi phiếu và phục vụ khách?',
    ...(role === 'manager' ? [
      'Tình hình hàng đợi hôm nay thế nào?',
      'Có bao nhiêu ca làm việc tuần này?'
    ] : [])
  ]);

  // Load context on mount
  useEffect(() => {
    const loadContext = async () => {
      try {
        const ctx = await aiHelperAPI.getContext();
        setContext(ctx);
      } catch (error) {
        console.error('Error loading context:', error);
      }
    };
    loadContext();
  }, []);

  // Load conversation history if conversationId exists (only on mount or conversationId change)
  useEffect(() => {
    if (conversationId && messages.length === 0) {
      const loadHistory = async () => {
        try {
          const history = await aiHelperAPI.getConversations(conversationId);
          // Sort messages by created_at to ensure correct order
          const sortedHistory = (history || []).sort((a, b) => {
            const timeA = new Date(a.created_at || 0).getTime();
            const timeB = new Date(b.created_at || 0).getTime();
            return timeA - timeB;
          });
          setMessages(sortedHistory);
        } catch (error) {
          console.error('Error loading conversation history:', error);
        }
      };
      loadHistory();
    }
  }, [conversationId, messages.length]); // Added messages.length to dependencies

  // Auto scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSendMessage = useCallback(async () => {
    if (!messageInput.trim() || loading) return;

    // Check if API key exists
    if (!apiKey) {
      setShowApiKeyModal(true);
      setMessages(prev => [
        ...prev,
        {
          id: Date.now(),
          role: 'assistant',
          message: 'Vui lòng cung cấp API key để sử dụng AI Helper. Nhấp vào "Cấu hình API Key" ở bên phải.',
          created_at: new Date().toISOString()
        }
      ]);
      return;
    }

    const userMessage = messageInput.trim();
    setMessageInput('');
    setLoading(true);

    // Add user message to UI immediately
    const tempUserMessage = {
      id: Date.now(),
      role: 'user',
      message: userMessage,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMessage]);

    try {
      const response = await aiHelperAPI.sendMessage(
        userMessage,
        conversationId,
        context,
        apiKey
      );

      // Add assistant response to UI
      if (response && response.message) {
        const assistantMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          message: response.message,
          created_at: new Date().toISOString()
        };
        setMessages(prev => [...prev, assistantMessage]);
      }

      // Update conversation ID if new conversation
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      let errorMessage = 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại.';

      // Handle specific error cases
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('API key')) {
        errorMessage = 'API key không hợp lệ. Vui lòng kiểm tra lại API key trong cài đặt.';
        setShowApiKeyModal(true);
      } else if (error.message?.includes('API key is required')) {
        errorMessage = 'Vui lòng cung cấp API key để sử dụng AI Helper.';
        setShowApiKeyModal(true);
      } else if (error.response?.status === 429) {
        // Rate limit error
        errorMessage = '⚠️ Bạn đã vượt quá giới hạn sử dụng API (Rate Limit).\n\n' +
          'Vui lòng:\n' +
          '1. Đợi vài phút rồi thử lại\n' +
          '2. Kiểm tra quota tại: https://ai.dev/usage?tab=rate-limit\n' +
          '3. Nâng cấp gói API nếu cần thiết';
      } else if (error.response?.data?.message) {
        // Check if it's a rate limit message from backend
        const backendMessage = error.response.data.message;
        if (backendMessage.includes('quota') || backendMessage.includes('rate limit') || backendMessage.includes('429')) {
          errorMessage = '⚠️ Bạn đã vượt quá giới hạn sử dụng API (Rate Limit).\n\n' +
            'Vui lòng đợi vài phút rồi thử lại hoặc kiểm tra quota tại: https://ai.dev/usage?tab=rate-limit';
        } else {
          errorMessage = backendMessage;
        }
      } else if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string' && (detail.includes('quota') || detail.includes('rate limit') || detail.includes('429'))) {
          errorMessage = '⚠️ Bạn đã vượt quá giới hạn sử dụng API (Rate Limit).\n\n' +
            'Vui lòng đợi vài phút rồi thử lại hoặc kiểm tra quota tại: https://ai.dev/usage?tab=rate-limit';
        } else {
          errorMessage = typeof detail === 'string' ? detail : JSON.stringify(detail);
        }
      }

      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          message: errorMessage,
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  }, [messageInput, conversationId, context, loading, apiKey]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestedQuestion = (question) => {
    setMessageInput(question);
  };

  const handleAddContext = useCallback((contextType) => {
    // This can be expanded to fetch additional context data
    console.log('Adding context:', contextType);
    // For now, just notify user
    setMessages(prev => [
      ...prev,
      {
        id: Date.now(),
        role: 'assistant',
        message: `Đã thêm ngữ cảnh: ${contextType}. Bạn có thể hỏi về ${contextType} ngay bây giờ.`,
        created_at: new Date().toISOString()
      }
    ]);
  }, []);

  const handleApiKeyConfirm = useCallback((newApiKey) => {
    setApiKey(newApiKey);
    localStorage.setItem(GEMINI_API_KEY_STORAGE, newApiKey);
    setShowApiKeyModal(false);
    setMessages(prev => [
      ...prev,
      {
        id: Date.now(),
        role: 'assistant',
        message: 'API key đã được lưu thành công! Bạn có thể bắt đầu sử dụng AI Helper ngay bây giờ.',
        created_at: new Date().toISOString()
      }
    ]);
  }, []);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="mb-4 pb-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <span className="mr-2">🤖</span>
              AI Helper
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              Trợ lý thông minh giúp bạn làm việc hiệu quả hơn
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4 min-h-0">
        {/* Main Chat Area */}
        <div className="lg:col-span-3 flex flex-col bg-white rounded-xl border border-gray-200 overflow-hidden">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && !loading && (
              <div className="h-full flex items-center justify-center">
                <div className="text-center max-w-md">
                  <div className="text-5xl mb-4">🤖</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    Chào mừng đến với AI Helper!
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Tôi có thể giúp bạn với các câu hỏi về hệ thống, lịch làm việc, thống kê và nhiều hơn nữa.
                  </p>
                  {suggestedQuestions.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700 mb-2">
                        Câu hỏi gợi ý:
                      </p>
                      {suggestedQuestions.map((question, index) => (
                        <motion.button
                          key={index}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => handleSuggestedQuestion(question)}
                          className="w-full text-left px-4 py-2 bg-blue-50 hover:bg-blue-100 rounded-lg text-sm text-blue-700 border border-blue-200 transition-colors"
                        >
                          {question}
                        </motion.button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
            <MessageList messages={messages} loading={loading} />
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4 bg-gray-50">
            <div className="flex space-x-2">
              <textarea
                value={messageInput}
                onChange={(e) => setMessageInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Nhập câu hỏi của bạn..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={2}
                disabled={loading}
              />
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSendMessage}
                disabled={loading || !messageInput.trim()}
                className={`px-6 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg font-medium transition-all ${loading || !messageInput.trim()
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:from-blue-600 hover:to-blue-700'
                  }`}
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                ) : (
                  'Gửi'
                )}
              </motion.button>
            </div>
          </div>
        </div>

        {/* Context Panel */}
        <div className="lg:col-span-1">
          <ContextPanel
            context={context}
            onAddContext={handleAddContext}
            onOpenApiKeyModal={() => setShowApiKeyModal(true)}
          />
        </div>
      </div>

      {/* API Key Modal */}
      <ApiKeyModal
        isOpen={showApiKeyModal}
        onClose={() => {
          // Only allow closing if API key is already set
          if (apiKey) {
            setShowApiKeyModal(false);
          }
        }}
        onConfirm={handleApiKeyConfirm}
        currentApiKey={apiKey}
        allowClose={!!apiKey} // Only allow closing if API key exists
      />
    </div>
  );
};

export default AIHelper;


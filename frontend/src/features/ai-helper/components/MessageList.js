import React from 'react';
import { motion } from 'framer-motion';
const MessageList = ({ messages, loading }) => {
  if (loading && messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
          <p className="text-gray-500 text-sm">Đang tải...</p>
        </div>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center text-gray-500">
          <div className="text-4xl mb-4">🤖</div>
          <p className="text-lg font-medium mb-2">Chào mừng đến với AI Helper!</p>
          <p className="text-sm">Hãy đặt câu hỏi để bắt đầu trò chuyện</p>
        </div>
      </div>
    );
  }

  // Sort messages by created_at to ensure correct chronological order
  const sortedMessages = [...messages].sort((a, b) => {
    const timeA = new Date(a.created_at || 0).getTime();
    const timeB = new Date(b.created_at || 0).getTime();
    return timeA - timeB;
  });

  return (
    <div className="space-y-4 overflow-y-auto">
      {sortedMessages.map((message, index) => {
        const isUser = message.role === 'user';

        return (
          <motion.div
            key={message.id || index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${isUser
                ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white'
                : 'bg-gray-100 text-gray-900'
                }`}
            >
              <div className="text-sm whitespace-pre-wrap break-words">
                {message.message}
              </div>
              {message.created_at && (
                <div
                  className={`text-xs mt-2 ${isUser ? 'text-blue-100' : 'text-gray-500'
                    }`}
                >
                  {new Date(message.created_at).toLocaleTimeString('vi-VN', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              )}
            </div>
          </motion.div>
        );
      })}
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex justify-start"
        >
          <div className="bg-gray-100 rounded-2xl px-4 py-3">
            <div className="flex space-x-2">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default MessageList;


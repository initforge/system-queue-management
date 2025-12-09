import React from 'react';
import { motion } from 'framer-motion';

const ArticleViewer = ({ article, onBack, onEdit, canEdit = false }) => {
  if (!article) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>Không tìm thấy bài viết</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <button
          onClick={onBack}
          className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span>Quay lại</span>
        </button>
        {canEdit && (
          <button
            onClick={() => onEdit(article)}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Chỉnh sửa
          </button>
        )}
      </div>

      {/* Article Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl shadow-lg border border-gray-200 p-8"
      >
        {/* Title */}
        <h1 className="text-3xl font-bold text-gray-900 mb-4">{article.title}</h1>

        {/* Metadata */}
        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-6 pb-6 border-b">
          {article.category_name && (
            <div className="flex items-center space-x-2">
              <span className="text-gray-400">📁</span>
              <span>{article.category_name}</span>
            </div>
          )}
          {article.author_name && (
            <div className="flex items-center space-x-2">
              <span className="text-gray-400">✍️</span>
              <span>{article.author_name}</span>
            </div>
          )}
          {article.created_at && (
            <div className="flex items-center space-x-2">
              <span className="text-gray-400">📅</span>
              <span>{new Date(article.created_at).toLocaleDateString('vi-VN')}</span>
            </div>
          )}
          {article.view_count !== undefined && (
            <div className="flex items-center space-x-2">
              <span className="text-gray-400">👁️</span>
              <span>{article.view_count} lượt xem</span>
            </div>
          )}
        </div>

        {/* Tags */}
        {article.tags && article.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-6">
            {article.tags.map((tag, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}

        {/* Content */}
        <div
          className="prose prose-lg max-w-none"
          dangerouslySetInnerHTML={{
            __html: article.content.replace(/\n/g, '<br />')
          }}
        />

        {/* Attachments */}
        {article.attachments && article.attachments.length > 0 && (
          <div className="mt-8 pt-6 border-t">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">📎 Tệp đính kèm</h3>
            <div className="space-y-2">
              {article.attachments.map((attachment) => (
                <a
                  key={attachment.id}
                  href={attachment.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-3 p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <span className="text-2xl">📄</span>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{attachment.file_name}</div>
                    {attachment.file_size && (
                      <div className="text-sm text-gray-500">
                        {(attachment.file_size / 1024).toFixed(2)} KB
                      </div>
                    )}
                  </div>
                  <span className="text-blue-600">Tải xuống</span>
                </a>
              ))}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default ArticleViewer;


import React from 'react';
import { motion } from 'framer-motion';

const SearchResults = ({ results, onArticleClick, loading }) => {
  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
        <p className="text-gray-500 text-sm">Đang tìm kiếm...</p>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <div className="text-4xl mb-4">🔍</div>
        <p className="text-lg">Không tìm thấy kết quả</p>
        <p className="text-sm mt-2">Thử tìm kiếm với từ khóa khác</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="text-sm text-gray-600 mb-4">
        Tìm thấy <strong>{results.length}</strong> kết quả
      </div>
      {results.map((article, index) => (
        <motion.div
          key={article.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
          onClick={() => onArticleClick(article)}
          className="p-4 bg-white rounded-xl border border-gray-200 hover:shadow-md cursor-pointer transition-all"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{article.title}</h3>
              <p className="text-sm text-gray-600 line-clamp-2 mb-3">{article.content}</p>
              <div className="flex items-center space-x-4 text-xs text-gray-500">
                {article.category_name && (
                  <span className="flex items-center space-x-1">
                    <span>📁</span>
                    <span>{article.category_name}</span>
                  </span>
                )}
                {article.view_count !== undefined && (
                  <span className="flex items-center space-x-1">
                    <span>👁️</span>
                    <span>{article.view_count}</span>
                  </span>
                )}
              </div>
            </div>
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default SearchResults;


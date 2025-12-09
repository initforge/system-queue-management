import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../shared/AuthContext';
import knowledgeBaseAPI from '../../shared/services/api/knowledgeBase';
import ArticleViewer from './components/ArticleViewer';
import SearchResults from './components/SearchResults';
import VideoModal from './components/VideoModal';
import FAQSection from './components/FAQSection';

const KnowledgeBase = ({ role = 'staff' }) => {
  const { user } = useAuth();
  const [categories, setCategories] = useState([]);
  const [articles, setArticles] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [loading, setLoading] = useState(true);
  const [featuredArticles, setFeaturedArticles] = useState([]);
  const [videoModalOpen, setVideoModalOpen] = useState(false);
  const [selectedVideoUrl, setSelectedVideoUrl] = useState(null);
  const [showFAQ, setShowFAQ] = useState(false);

  const isManager = role === 'manager' || user?.role === 'manager' || user?.role === 'admin';

  // Default video URL (can be managed by manager)
  const defaultVideoUrl = 'https://www.youtube.com/embed/dQw4w9WgXcQ'; // Replace with actual video

  // Load categories
  const loadCategories = useCallback(async () => {
    try {
      const data = await knowledgeBaseAPI.getCategories();
      setCategories(data || []);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  }, []);

  // Load articles
  const loadArticles = useCallback(async (categoryId = null, featured = null) => {
    try {
      setLoading(true);
      const filters = {
        publishedOnly: !isManager,
        limit: 50
      };
      
      if (categoryId) filters.categoryId = categoryId;
      if (featured !== null) filters.featured = featured;
      if (user?.department_id) filters.departmentId = user.department_id;

      const data = await knowledgeBaseAPI.getArticles(filters);
      setArticles(data || []);
    } catch (error) {
      console.error('Error loading articles:', error);
    } finally {
      setLoading(false);
    }
  }, [isManager, user?.department_id]);

  // Load featured articles
  const loadFeaturedArticles = useCallback(async () => {
    try {
      const filters = {
        publishedOnly: true,
        featured: true,
        limit: 5
      };
      const data = await knowledgeBaseAPI.getArticles(filters);
      setFeaturedArticles(data || []);
    } catch (error) {
      console.error('Error loading featured articles:', error);
    }
  }, []);

  // Search articles
  const handleSearch = useCallback(async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    try {
      const results = await knowledgeBaseAPI.searchArticles(query);
      setSearchResults(results || []);
    } catch (error) {
      console.error('Error searching articles:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, []);

  // Handle category selection
  const handleCategorySelect = (categoryId) => {
    setSelectedCategory(categoryId);
    setSelectedArticle(null);
    setSearchQuery('');
    setSearchResults([]);
    loadArticles(categoryId);
  };

  // Handle article selection
  const handleArticleSelect = async (article) => {
    try {
      // Load full article details
      const fullArticle = await knowledgeBaseAPI.getArticle(article.id);
      setSelectedArticle(fullArticle);
    } catch (error) {
      console.error('Error loading article:', error);
      setSelectedArticle(article);
    }
  };

  // Handle search input
  const handleSearchInput = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    
    if (query.trim()) {
      handleSearch(query);
    } else {
      setSearchResults([]);
      setIsSearching(false);
    }
  };

  // Initial load
  useEffect(() => {
    loadCategories();
    loadArticles(null, null);
    loadFeaturedArticles();
  }, [loadCategories, loadArticles, loadFeaturedArticles]);

  // Show article viewer if article selected
  if (selectedArticle) {
    return (
      <ArticleViewer
        article={selectedArticle}
        onBack={() => {
          setSelectedArticle(null);
          if (selectedCategory) {
            loadArticles(selectedCategory);
          }
        }}
        onEdit={() => {
          // TODO: Implement edit functionality
          console.log('Edit article:', selectedArticle);
        }}
        canEdit={isManager}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <span className="mr-2">📚</span>
            {isManager ? 'Quản lý kiến thức' : 'Kiến thức'}
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Tài liệu, hướng dẫn và thông tin nội bộ
          </p>
        </div>
        {isManager && (
          <button
            onClick={() => {
              // TODO: Implement create article
              console.log('Create new article');
            }}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            + Tạo bài viết
          </button>
        )}
      </div>

      {/* Search Bar */}
      <div className="relative">
        <input
          type="text"
          value={searchQuery}
          onChange={handleSearchInput}
          placeholder="Tìm kiếm bài viết..."
          className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Search Results */}
      {(searchQuery || searchResults.length > 0 || isSearching) && (
        <SearchResults
          results={searchResults}
          onArticleClick={handleArticleSelect}
          loading={isSearching}
        />
      )}

      {/* Main Content */}
      {!searchQuery && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Categories Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-4 sticky top-4">
              <h3 className="font-semibold text-gray-900 mb-4">Danh mục</h3>
              <div className="space-y-2">
                <button
                  onClick={() => handleCategorySelect(null)}
                  className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                    selectedCategory === null
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  Tất cả
                </button>
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => handleCategorySelect(category.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
                      selectedCategory === category.id
                        ? 'bg-blue-100 text-blue-700 font-medium'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <span>{category.icon}</span>
                    <span>{category.name}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Articles List */}
          <div className="lg:col-span-3">
            {/* Featured Articles */}
            {featuredArticles.length > 0 && selectedCategory === null && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <span className="mr-2">⭐</span>
                  Bài viết nổi bật
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {featuredArticles.map((article) => (
                    <motion.div
                      key={article.id}
                      whileHover={{ scale: 1.02 }}
                      onClick={() => handleArticleSelect(article)}
                      className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200 cursor-pointer hover:shadow-md transition-all"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-semibold text-gray-900 line-clamp-2">{article.title}</h4>
                        <span className="text-xl">⭐</span>
                      </div>
                      {article.category_name && (
                        <span className="text-xs text-blue-700 bg-blue-100 px-2 py-1 rounded">
                          {article.category_name}
                        </span>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Articles List */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                {selectedCategory
                  ? categories.find((c) => c.id === selectedCategory)?.name || 'Bài viết'
                  : 'Tất cả bài viết'}
              </h3>
              
              {loading ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
                  <p className="text-gray-500 text-sm">Đang tải...</p>
                </div>
              ) : articles.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <div className="text-4xl mb-4">📝</div>
                  <p>Không có bài viết nào</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Video Guide Button */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
                          <span className="text-2xl">📹</span>
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900 mb-1">Video hướng dẫn</h4>
                          <p className="text-sm text-gray-600">Xem video hướng dẫn sử dụng hệ thống</p>
                        </div>
                      </div>
                      <button
                        onClick={() => {
                          setSelectedVideoUrl(defaultVideoUrl);
                          setVideoModalOpen(true);
                        }}
                        className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium flex items-center space-x-2"
                      >
                        <span>▶️</span>
                        <span>Xem video</span>
                      </button>
                    </div>
                  </motion.div>

                  {/* FAQ Toggle Button */}
                  <motion.button
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    onClick={() => setShowFAQ(!showFAQ)}
                    className="w-full p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border-2 border-purple-200 hover:shadow-md transition-all text-left"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">❓</span>
                        <div>
                          <h4 className="font-semibold text-gray-900">Câu hỏi thường gặp (FAQ)</h4>
                          <p className="text-sm text-gray-600">Xem các câu hỏi và câu trả lời phổ biến</p>
                        </div>
                      </div>
                      <svg
                        className={`w-5 h-5 text-gray-500 transition-transform ${showFAQ ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </motion.button>

                  {/* FAQ Section */}
                  {showFAQ && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                    >
                      <FAQSection />
                    </motion.div>
                  )}

                  {/* Articles List */}
                  {articles.map((article, index) => (
                    <motion.div
                      key={article.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      onClick={() => handleArticleSelect(article)}
                      className="p-6 bg-white rounded-xl border border-gray-200 hover:shadow-md cursor-pointer transition-all"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h4 className="text-lg font-semibold text-gray-900">{article.title}</h4>
                            {article.is_featured && (
                              <span className="text-yellow-500">⭐</span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                            {article.content.replace(/[#*]/g, '').substring(0, 150)}...
                          </p>
                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            {article.category_name && (
                              <span className="flex items-center space-x-1">
                                <span>📁</span>
                                <span>{article.category_name}</span>
                              </span>
                            )}
                            {article.author_name && (
                              <span className="flex items-center space-x-1">
                                <span>✍️</span>
                                <span>{article.author_name}</span>
                              </span>
                            )}
                            {article.view_count !== undefined && (
                              <span className="flex items-center space-x-1">
                                <span>👁️</span>
                                <span>{article.view_count}</span>
                              </span>
                            )}
                          </div>
                          {article.tags && article.tags.length > 0 && (
                            <div className="flex flex-wrap gap-2 mt-3">
                              {article.tags.slice(0, 3).map((tag, tagIndex) => (
                                <span
                                  key={tagIndex}
                                  className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                                >
                                  #{tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                        <svg className="w-5 h-5 text-gray-400 ml-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Video Modal */}
      <VideoModal
        isOpen={videoModalOpen}
        onClose={() => setVideoModalOpen(false)}
        videoUrl={selectedVideoUrl}
        title="Video hướng dẫn sử dụng hệ thống"
      />
    </div>
  );
};

export default KnowledgeBase;


import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const NotFound = () => {

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-800 via-blue-900 to-indigo-900">
      {/* Gentle Background */}
      <div className="absolute inset-0">
        <motion.div 
          className="absolute inset-0"
          animate={{ 
            background: [
              'radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.15) 0%, transparent 50%)',
              'radial-gradient(circle at 80% 50%, rgba(29, 78, 216, 0.2) 0%, transparent 50%)',
              'radial-gradient(circle at 50% 80%, rgba(59, 130, 246, 0.18) 0%, transparent 50%)'
            ]
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      {/* Main Content */}
      <div className="min-h-screen flex items-center justify-center p-4 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="max-w-lg w-full bg-white/85 backdrop-blur-lg rounded-3xl shadow-2xl border border-blue-200/40 p-8 text-center"
        >
          {/* Animated 404 Icon */}
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: [0.8, 1.1, 1] }}
            transition={{ duration: 1.5 }}
            className="mb-6"
          >
            <div className="w-32 h-32 mx-auto bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-full flex items-center justify-center shadow-xl">
              <motion.div
                animate={{ rotate: [0, 5, -5, 0] }}
                transition={{ duration: 3, repeat: Infinity }}
                className="text-center"
              >
                <div className="text-3xl font-bold">404</div>
                <div className="text-xs opacity-90">Not Found</div>
              </motion.div>
            </div>
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-3xl font-bold text-blue-800 mb-3"
          >
            Trang không tồn tại
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-blue-700 mb-8 leading-relaxed"
          >
            Xin lỗi, trang bạn đang tìm kiếm không tồn tại hoặc đã được di chuyển. 
            Hãy quay về trang chủ để tiếp tục sử dụng dịch vụ.
          </motion.p>
          
          {/* Action Buttons */}
          <div className="flex flex-col space-y-4">
            <Link to="/">
              <motion.button
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-white rounded-2xl font-semibold shadow-lg transition-all duration-300 flex items-center justify-center space-x-3"
              >
                <span className="text-xl">🏠</span>
                <span>Quay về trang chủ</span>
              </motion.button>
            </Link>
            
            <Link to="/display">
              <motion.button
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                className="w-full px-6 py-4 border-2 border-blue-400 bg-white/70 text-blue-800 rounded-2xl font-semibold hover:bg-blue-50 transition-all duration-300 flex items-center justify-center space-x-3"
              >
                <span className="text-xl">📱</span>
                <span>Truy cập hệ thống xếp hàng</span>
              </motion.button>
            </Link>

            <Link to="/login">
              <motion.button
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                className="w-full px-6 py-4 border-2 border-indigo-400 bg-white/70 text-indigo-800 rounded-2xl font-semibold hover:bg-indigo-50 transition-all duration-300 flex items-center justify-center space-x-3"
              >
                <span className="text-xl">🔐</span>
                <span>Đăng nhập quản lý</span>
              </motion.button>
            </Link>
          </div>
        </motion.div>
      </div>

      {/* Decorative Elements */}
      <motion.div
        className="absolute top-16 left-12 text-4xl opacity-30"
        animate={{ 
          rotate: [0, 10, -10, 0],
          scale: [1, 1.1, 1]
        }}
        transition={{ duration: 6, repeat: Infinity }}
      >
        ⚠️
      </motion.div>
      
      <motion.div
        className="absolute top-1/3 right-16 text-3xl opacity-25"
        animate={{ 
          y: [0, -15, 0],
          rotate: [0, 15, -15, 0]
        }}
        transition={{ duration: 8, repeat: Infinity, delay: 2 }}
      >
        🔍
      </motion.div>
      
      <motion.div
        className="absolute bottom-20 left-16 text-3xl opacity-30"
        animate={{ 
          x: [0, 15, -15, 0],
          rotate: [0, -10, 10, 0]
        }}
        transition={{ duration: 7, repeat: Infinity, delay: 1 }}
      >
        🏠
      </motion.div>
    </div>
  );
};

export default NotFound;
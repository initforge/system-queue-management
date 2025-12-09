import React from 'react';
import { motion } from 'framer-motion';

const ContextPanel = ({ context, onAddContext }) => {
  if (!context) {
    return (
      <div className="bg-gray-50 rounded-xl p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Ngữ cảnh</h3>
        <p className="text-xs text-gray-500">Đang tải...</p>
      </div>
    );
  }

  const quickActions = [
    { label: 'Thêm ngữ cảnh hàng đợi', action: 'queue' },
    { label: 'Thêm ngữ cảnh lịch làm việc', action: 'schedule' },
    { label: 'Thêm ngữ cảnh hiệu suất', action: 'performance' }
  ];

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
      <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
        <span className="mr-2">🔍</span>
        Ngữ cảnh hiện tại
      </h3>
      
      <div className="space-y-2 mb-4">
        {context.user && (
          <div className="text-xs">
            <span className="font-medium text-gray-700">Người dùng:</span>{' '}
            <span className="text-gray-600">{context.user.full_name}</span>
          </div>
        )}
        {context.department && (
          <div className="text-xs">
            <span className="font-medium text-gray-700">Phòng ban:</span>{' '}
            <span className="text-gray-600">{context.department.name}</span>
          </div>
        )}
        {context.user?.role && (
          <div className="text-xs">
            <span className="font-medium text-gray-700">Vai trò:</span>{' '}
            <span className="text-gray-600">
              {context.user.role === 'manager' ? 'Quản lý' : 'Nhân viên'}
            </span>
          </div>
        )}
      </div>

      {onAddContext && (
        <div className="border-t border-blue-200 pt-3 mt-3">
          <p className="text-xs font-medium text-gray-700 mb-2">Thêm ngữ cảnh:</p>
          <div className="space-y-2">
            {quickActions.map((action, index) => (
              <motion.button
                key={action.action}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onAddContext(action.action)}
                className="w-full text-left px-3 py-2 bg-white rounded-lg text-xs text-gray-700 hover:bg-blue-100 transition-colors border border-blue-200"
              >
                + {action.label}
              </motion.button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ContextPanel;


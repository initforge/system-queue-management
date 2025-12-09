import React from 'react';
import { useDraggable } from '@dnd-kit/core';
import { motion } from 'framer-motion';
import { CSS } from '@dnd-kit/utilities';

const StaffCard = ({ staff, isDragging = false }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging: isDraggingState
  } = useDraggable({
    id: `staff-${staff.id}`,
    data: {
      type: 'staff',
      staff: staff
    }
  });

  const style = {
    transform: CSS.Translate.toString(transform),
    opacity: isDraggingState ? 0.5 : 1,
  };

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={`
        bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-3 
        cursor-grab active:cursor-grabbing shadow-md hover:shadow-lg transition-all
        ${isDraggingState ? 'ring-2 ring-blue-400 ring-offset-2' : ''}
      `}
    >
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center flex-shrink-0">
          <span className="text-white text-sm font-semibold">
            {staff.full_name?.charAt(0) || staff.username?.charAt(0) || 'U'}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold text-gray-900 truncate">
            {staff.full_name || staff.username || 'Nhân viên'}
          </div>
          {staff.email && (
            <div className="text-xs text-gray-500 truncate">{staff.email}</div>
          )}
        </div>
      </div>
      {isDraggingState && (
        <div className="absolute inset-0 bg-blue-100 bg-opacity-50 rounded-xl flex items-center justify-center pointer-events-none">
          <span className="text-blue-600 font-semibold">Đang di chuyển...</span>
        </div>
      )}
    </motion.div>
  );
};

export default StaffCard;


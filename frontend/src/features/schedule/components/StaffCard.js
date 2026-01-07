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

  // Extract username from email (e.g., staff.01@qstream.vn -> staff.01)
  const getUsername = () => {
    if (staff.username) return staff.username;
    if (staff.email) return staff.email.split('@')[0];
    return staff.full_name || `User #${staff.id}`;
  };

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`
        bg-gradient-to-r from-blue-100 to-indigo-100 border border-blue-300 rounded-lg p-2 
        cursor-grab active:cursor-grabbing shadow-sm hover:shadow-md transition-all
        ${isDraggingState ? 'ring-2 ring-blue-400' : ''}
      `}
    >
      <div className="flex items-center space-x-2">
        <div className="w-7 h-7 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center flex-shrink-0">
          <span className="text-white text-xs font-bold">
            {getUsername().charAt(0).toUpperCase()}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-xs font-semibold text-gray-800 break-words" title={getUsername()}>
            {getUsername()}
          </div>
          {staff.full_name && (
            <div className="text-[10px] text-gray-500 truncate">
              {staff.full_name}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default StaffCard;

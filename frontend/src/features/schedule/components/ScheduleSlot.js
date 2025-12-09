import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { motion, AnimatePresence } from 'framer-motion';
import StaffCard from './StaffCard';

const ScheduleSlot = ({ 
  day, 
  shift, 
  schedules, 
  isToday = false,
  onRemoveStaff = null 
}) => {
  const slotId = `${day.date}-${shift.id}`;
  const schedule = schedules?.find(s => 
    s.scheduled_date === day.date && s.shift_id === shift.id
  );
  const staff = schedule?.staff;

  const {
    setNodeRef,
    isOver,
    active
  } = useDroppable({
    id: slotId,
    data: {
      day: day.date,
      shiftId: shift.id,
      shiftType: shift.shift_type,
      existingSchedule: schedule
    }
  });

  const isActive = active && active.id?.startsWith('staff-');
  const canDrop = isOver && isActive && (!staff || active.data.current?.staff?.id !== staff.id);
  const isConflict = isOver && isActive && staff && active.data.current?.staff?.id !== staff.id;

  // Shift type colors
  const getShiftColors = (shiftType) => {
    switch (shiftType) {
      case 'morning':
        return {
          bg: 'bg-gradient-to-br from-yellow-50 to-amber-50',
          border: 'border-yellow-200',
          text: 'text-yellow-700',
          accent: 'bg-yellow-400'
        };
      case 'afternoon':
        return {
          bg: 'bg-gradient-to-br from-orange-50 to-red-50',
          border: 'border-orange-200',
          text: 'text-orange-700',
          accent: 'bg-orange-400'
        };
      case 'night':
        return {
          bg: 'bg-gradient-to-br from-indigo-50 to-purple-50',
          border: 'border-indigo-200',
          text: 'text-indigo-700',
          accent: 'bg-indigo-400'
        };
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          text: 'text-gray-700',
          accent: 'bg-gray-400'
        };
    }
  };

  const colors = getShiftColors(shift.shift_type);

  return (
    <div
      ref={setNodeRef}
      className={`
        relative min-h-[120px] p-2 rounded-lg border-2 transition-all
        ${colors.bg} ${colors.border}
        ${isToday ? 'ring-2 ring-blue-400 ring-offset-1' : ''}
        ${canDrop ? 'ring-2 ring-green-400 ring-offset-2 bg-green-50' : ''}
        ${isConflict ? 'ring-2 ring-red-400 ring-offset-2 bg-red-50' : ''}
        ${isOver && isActive ? 'scale-105' : ''}
      `}
    >
      {/* Shift Label */}
      <div className="flex items-center justify-between mb-1">
        <div className={`text-xs font-semibold ${colors.text} px-2 py-1 rounded`}>
          {shift.name}
        </div>
        {isToday && (
          <div className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded-full">
            Hôm nay
          </div>
        )}
      </div>

      {/* Time Range */}
      <div className="text-xs text-gray-600 mb-2">
        {shift.start_time?.substring(0, 5)} - {shift.end_time?.substring(0, 5)}
      </div>

      {/* Staff Assignment */}
      <AnimatePresence mode="wait">
        {staff ? (
          <motion.div
            key={`schedule-${schedule.id}`}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="relative"
          >
            <div className={`
              bg-white rounded-lg p-2 border border-blue-200 shadow-sm
              ${isConflict ? 'border-red-300 bg-red-50' : ''}
            `}>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-white text-xs font-semibold">
                    {staff.full_name?.charAt(0) || staff.username?.charAt(0) || 'U'}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-semibold text-gray-900 truncate">
                    {staff.full_name || staff.username || 'Nhân viên'}
                  </div>
                </div>
                {onRemoveStaff && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onRemoveStaff(schedule.id);
                    }}
                    className="text-red-500 hover:text-red-700 text-xs px-1"
                    title="Xóa ca"
                  >
                    ×
                  </button>
                )}
              </div>
            </div>
            {isConflict && (
              <div className="absolute inset-0 bg-red-100 bg-opacity-75 rounded-lg flex items-center justify-center">
                <span className="text-red-700 text-xs font-semibold">Xung đột!</span>
              </div>
            )}
          </motion.div>
        ) : (
          <motion.div
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className={`
              text-xs text-gray-400 text-center py-4 rounded border-2 border-dashed
              ${canDrop ? 'border-green-400 bg-green-100' : 'border-gray-300'}
              ${isOver && !staff ? 'bg-blue-50' : ''}
            `}
          >
            {canDrop ? 'Thả vào đây' : isConflict ? 'Xung đột ca!' : 'Trống'}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Drop Indicator */}
      {isOver && canDrop && !staff && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="absolute inset-0 bg-green-200 bg-opacity-30 rounded-lg border-2 border-green-400 border-dashed pointer-events-none flex items-center justify-center"
        >
          <span className="text-green-700 font-semibold">Thả vào đây</span>
        </motion.div>
      )}
    </div>
  );
};

export default ScheduleSlot;


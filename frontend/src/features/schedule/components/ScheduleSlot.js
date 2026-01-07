import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { motion, AnimatePresence } from 'framer-motion';

const ScheduleSlot = ({
  day,
  shift,
  schedules,
  isToday = false,
  onRemoveStaff = null
}) => {
  const slotId = `${day.date}-${shift.id}`;
  const slotSchedules = (schedules || []).filter(s =>
    s.scheduled_date === day.date && s.shift_id === shift.id
  );

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
      existingSchedules: slotSchedules
    }
  });

  const isActive = active && active.id?.startsWith('staff-');
  const isDuplicate = isActive && slotSchedules.some(s => `staff-${s.staff_id}` === active.id);
  const canDrop = isOver && isActive && !isDuplicate;

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
        ${canDrop ? 'ring-2 ring-green-400 ring-offset-2 bg-green-50 scale-[1.02]' : ''}
        ${isOver && isDuplicate ? 'ring-2 ring-red-400 ring-offset-2 bg-red-50' : ''}
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

      {/* Staff Assignments List */}
      <div className="space-y-1.5 overflow-y-auto max-h-[120px] scrollbar-hide">
        <AnimatePresence>
          {slotSchedules.map((schedule) => {
            const staff = schedule.staff;
            const username = staff?.username || staff?.full_name || (staff?.email ? staff.email.split('@')[0] : `User #${staff?.id || '?'}`);

            return (
              <motion.div
                key={`schedule-${schedule.id}`}
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="group relative bg-white rounded-md p-1.5 border border-blue-100 shadow-sm hover:border-blue-300 transition-all"
              >
                <div className="flex items-center space-x-1.5">
                  <div className="w-5 h-5 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-[9px] font-bold uppercase">
                      {username.charAt(0)}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-[11px] font-bold text-gray-800 truncate" title={username}>
                      {username}
                    </div>
                  </div>
                  {onRemoveStaff && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onRemoveStaff(schedule.id);
                      }}
                      className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600 transition-opacity"
                      title="Xóa khỏi ca"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {slotSchedules.length === 0 && (
          <div className={`
            text-[10px] text-gray-400 text-center py-4 rounded border-2 border-dashed
            ${canDrop ? 'border-green-400 bg-green-50 text-green-600' : 'border-gray-200'}
          `}>
            {canDrop ? 'Thả vào đây' : isOver && isDuplicate ? 'Đã có mặt' : 'Trống'}
          </div>
        )}
      </div>

      {/* Drop Indicator Overlay */}
      {isOver && canDrop && (
        <div className="absolute inset-0 bg-blue-500 bg-opacity-10 rounded-lg pointer-events-none flex items-center justify-center">
          <div className="bg-white px-2 py-1 rounded shadow-sm text-[10px] font-bold text-blue-600">
            Thêm nhân viên
          </div>
        </div>
      )}
    </div>
  );
};

export default ScheduleSlot;


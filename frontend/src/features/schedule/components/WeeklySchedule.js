import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragOverlay } from '@dnd-kit/core';
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import { motion } from 'framer-motion';
import { useAuth } from '../../../shared/AuthContext';
import scheduleAPI from '../../../shared/services/api/schedule';
import { ApiClient } from '../../../shared/services/api/client';
import StaffCard from './StaffCard';
import ScheduleSlot from './ScheduleSlot';
import { format, startOfWeek, addDays, isSameDay } from 'date-fns';

const api = new ApiClient();

const WeeklySchedule = ({ departmentId, managerId, onScheduleChange }) => {
  const { user } = useAuth();
  const [weekStartDate, setWeekStartDate] = useState(() => {
    const today = new Date();
    return startOfWeek(today, { weekStartsOn: 1 });
  });

  const [shifts, setShifts] = useState([]);
  const [staffList, setStaffList] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [draggedItem, setDraggedItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hasChanges, setHasChanges] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredStaff = useMemo(() => {
    return staffList.filter(staff => {
      const search = searchTerm.toLowerCase();
      return (
        (staff.full_name && staff.full_name.toLowerCase().includes(search)) ||
        (staff.username && staff.username.toLowerCase().includes(search)) ||
        (staff.email && staff.email.toLowerCase().includes(search))
      );
    });
  }, [staffList, searchTerm]);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Generate week dates (Monday to Sunday)
  const weekDays = useMemo(() => {
    const days = [];
    for (let i = 0; i < 7; i++) {
      const date = addDays(weekStartDate, i);
      days.push({
        date: format(date, 'yyyy-MM-dd'),
        dateObj: date,
        dayName: format(date, 'EEE'),
        dayNumber: format(date, 'dd'),
        isToday: isSameDay(date, new Date())
      });
    }
    return days;
  }, [weekStartDate]);

  // Load shifts
  const loadShifts = useCallback(async () => {
    try {
      const response = await scheduleAPI.getShifts();
      setShifts(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Error loading shifts:', error);
      // Fallback to default shifts if API fails
      setShifts([
        {
          id: '550e8400-e29b-41d4-a716-446655440001',
          name: 'Ca Sáng',
          shift_type: 'morning',
          start_time: '07:00:00',
          end_time: '15:00:00'
        },
        {
          id: '550e8400-e29b-41d4-a716-446655440002',
          name: 'Ca Chiều',
          shift_type: 'afternoon',
          start_time: '15:00:00',
          end_time: '23:00:00'
        },
        {
          id: '550e8400-e29b-41d4-a716-446655440003',
          name: 'Ca Tối',
          shift_type: 'night',
          start_time: '23:00:00',
          end_time: '07:00:00'
        }
      ]);
    }
  }, []);

  // Load staff list
  const loadStaffList = useCallback(async () => {
    try {
      console.log('🔍 Loading staff list from manager/staff...');
      const response = await api.get('manager/staff');
      console.log('📊 Staff API response:', response);
      const staffArray = Array.isArray(response) ? response : (response?.data || []);
      console.log('👥 Staff array to set:', staffArray);
      setStaffList(staffArray);
    } catch (error) {
      console.error('❌ Error loading staff:', error);
      setStaffList([]);
    }
  }, []);

  const [originalSchedules, setOriginalSchedules] = useState([]);

  // Load weekly schedules
  const loadWeeklySchedules = useCallback(async () => {
    try {
      setLoading(true);
      const startDateStr = format(weekStartDate, 'yyyy-MM-dd');
      const response = await scheduleAPI.getWeeklySchedule(startDateStr);

      const schedulesArray = Array.isArray(response) ? response : [];

      console.log('📅 Weekly Schedule RAW Response:', response);
      const transformed = schedulesArray.map(s => ({
        id: s.id,
        staff_id: s.staff_id,
        shift_id: s.shift_id,
        scheduled_date: s.scheduled_date,
        status: s.status,
        notes: s.notes,
        staff: {
          id: s.staff_id,
          full_name: s.staff_name || 'Unknown',
          username: s.staff_username || s.staff_name || `User #${s.staff_id}`,
          email: s.staff_email || ''
        }
      }));
      console.log('🔄 Transformed Schedules:', transformed);

      setSchedules(transformed);
      setOriginalSchedules(JSON.parse(JSON.stringify(transformed))); // Deep copy
      setHasChanges(false);
      if (onScheduleChange) {
        onScheduleChange(false);
      }
    } catch (error) {
      console.error('Error loading weekly schedules:', error);
      setSchedules([]);
      setOriginalSchedules([]);
    } finally {
      setLoading(false);
    }
  }, [weekStartDate, onScheduleChange]);

  useEffect(() => {
    loadShifts();
    loadStaffList();
  }, [loadShifts, loadStaffList]);

  useEffect(() => {
    loadWeeklySchedules();
  }, [loadWeeklySchedules]);

  // Handle drag start
  const handleDragStart = (event) => {
    const { active } = event;
    setDraggedItem(active);
  };

  // Handle drag end
  const handleDragEnd = async (event) => {
    const { active, over } = event;
    setDraggedItem(null);

    if (!over) return;

    const activeId = active.id.toString();
    const overId = over.id.toString();

    // Handle dropping staff card into schedule slot
    if (activeId.startsWith('staff-') && overId.includes('-')) {
      const staffId = parseInt(activeId.replace('staff-', ''));
      // overId format: "2026-01-05-uuid-with-dashes"
      // Date is first 10 chars (YYYY-MM-DD), shiftId is everything after
      const date = overId.substring(0, 10);
      const shiftId = overId.substring(11); // Skip the date and the dash after it

      const staff = staffList.find((s) => s.id === staffId);
      if (!staff) return;

      // Check if this staff is already in THIS specific slot
      const existingInSlot = schedules.find(
        (s) => s.scheduled_date === date &&
          s.shift_id === shiftId &&
          s.staff_id === staffId
      );

      if (existingInSlot) {
        return; // Already in this slot
      }

      // Optional: Check if staff is scheduled elsewhere on same date (optional, but good for "ràng buộc")
      const existingOnDate = schedules.find(
        (s) => s.scheduled_date === date && s.staff_id === staffId
      );

      if (existingOnDate) {
        if (!window.confirm(`${staff.full_name} đã có lịch trong ngày ${date} tại ca khác. Bạn vẫn muốn gán thêm?`)) {
          return;
        }
      }

      // Add new schedule locally
      const newSchedule = {
        id: `temp-${Date.now()}`,
        staff_id: staffId,
        shift_id: shiftId,
        scheduled_date: date,
        status: 'scheduled',
        staff: {
          id: staffId,
          full_name: staff.full_name,
          username: staff.username,
          email: staff.email
        }
      };

      setSchedules((prev) => [...prev, newSchedule]);
      setHasChanges(true);
      if (onScheduleChange) {
        onScheduleChange(true);
      }
    }

    // Handle removing schedule (drag back to pool)
    if (activeId.startsWith('schedule-') && overId === 'staff-pool') {
      const scheduleId = activeId.replace('schedule-', '');
      setSchedules((prev) => prev.filter((s) => s.id.toString() !== scheduleId));
      setHasChanges(true);
      if (onScheduleChange) {
        onScheduleChange(true);
      }
    }
  };

  // Remove staff from schedule
  const handleRemoveStaff = useCallback((scheduleId) => {
    setSchedules((prev) => prev.filter((s) => s.id.toString() !== scheduleId.toString()));
    setHasChanges(true);
    if (onScheduleChange) {
      onScheduleChange(true);
    }
  }, [onScheduleChange]);

  // Save schedule
  const handleSaveSchedule = async () => {
    try {
      setLoading(true);

      // 1. Identify deletions: original IDs that are NOT in current schedules
      const currentIds = new Set(schedules.map(s => s.id.toString()));
      const toDelete = originalSchedules.filter(s => !currentIds.has(s.id.toString()));

      // 2. Identify additions: schedules with 'temp-' IDs
      const newSchedules = schedules.filter((s) => s.id.toString().startsWith('temp-'));

      // Perform deletions
      for (const schedule of toDelete) {
        try {
          await scheduleAPI.deleteSchedule(schedule.id);
        } catch (err) {
          console.error(`Failed to delete schedule ${schedule.id}:`, err);
        }
      }

      // Perform additions
      if (newSchedules.length > 0) {
        const schedulesToSave = newSchedules.map((schedule) => ({
          staff_id: parseInt(schedule.staff_id), // Ensure it's an integer
          shift_id: schedule.shift_id,
          scheduled_date: schedule.scheduled_date,
          manager_id: managerId || user?.id,
          notes: schedule.notes || ""
        }));

        // Use bulk endpoint
        try {
          await scheduleAPI.bulkCreateSchedules(schedulesToSave);
        } catch (bulkError) {
          console.warn('Bulk create failed, trying individual creates:', bulkError);
          for (const scheduleData of schedulesToSave) {
            await scheduleAPI.createSchedule(scheduleData);
          }
        }
      }

      alert('Đã cập nhật lịch làm việc thành công!');
      // Reload to get updated data with real IDs
      await loadWeeklySchedules();
    } catch (error) {
      console.error('Error saving schedule:', error);
      alert('Lỗi khi lưu lịch làm việc. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  // Navigate weeks
  const goToPreviousWeek = () => {
    setWeekStartDate((prev) => addDays(prev, -7));
  };

  const goToNextWeek = () => {
    setWeekStartDate((prev) => addDays(prev, 7));
  };

  const goToCurrentWeek = () => {
    setWeekStartDate(startOfWeek(new Date(), { weekStartsOn: 1 }));
  };

  // Get schedules for a specific day and shift
  const getSchedulesForSlot = useCallback((date, shiftId) => {
    return schedules.filter(
      (s) => s.scheduled_date === date && s.shift_id === shiftId
    );
  }, [schedules]);

  if (loading && schedules.length === 0 && shifts.length === 0 && staffList.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Đang tải lịch làm việc...</p>
        </div>
      </div>
    );
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="space-y-6">
        {/* Header with week navigation */}
        <div className="flex items-center justify-between bg-white rounded-xl p-4 shadow-md">
          <div className="flex items-center space-x-4">
            <h2 className="text-2xl font-bold text-gray-900">Lịch làm việc tuần</h2>
            <div className="flex items-center space-x-2">
              <button
                onClick={goToPreviousWeek}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <button
                onClick={goToCurrentWeek}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
              >
                Tuần này
              </button>
              <button
                onClick={goToNextWeek}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              {format(weekStartDate, 'dd MMM')} - {format(addDays(weekStartDate, 6), 'dd MMM yyyy')}
            </div>
            {hasChanges && (
              <motion.button
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                onClick={handleSaveSchedule}
                disabled={loading}
                className="px-6 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 flex items-center space-x-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Đang lưu...</span>
                  </>
                ) : (
                  <>
                    <span>💾</span>
                    <span>Xác nhận lịch tuần</span>
                  </>
                )}
              </motion.button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-8 gap-4">
          {/* Staff Pool Sidebar */}
          <div className="col-span-1">
            <div className="sticky top-4 bg-white rounded-xl p-4 shadow-md border border-gray-200">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Nhân viên</h3>

              {/* Search Staff */}
              <div className="mb-3">
                <input
                  type="text"
                  placeholder="Tìm nhân viên..."
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              <div
                id="staff-pool"
                className="space-y-2"
              >
                {filteredStaff.map((staff) => (
                  <StaffCard key={staff.id} staff={staff} />
                ))}
                {filteredStaff.length === 0 && (
                  <div className="text-xs text-gray-500 text-center py-4">
                    {staffList.length === 0 ? 'Không có nhân viên' : 'Không tìm thấy nhân viên'}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Calendar Grid */}
          <div className="col-span-7">
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-4">
              {/* Day Headers */}
              <div className="grid grid-cols-7 gap-2 mb-4">
                {weekDays.map((day) => (
                  <div
                    key={day.date}
                    className={`text-center font-semibold py-2 rounded-lg ${day.isToday
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-700'
                      }`}
                  >
                    <div className="text-xs">{day.dayName}</div>
                    <div className="text-sm">{day.dayNumber}</div>
                  </div>
                ))}
              </div>

              {/* Shift Rows */}
              <div className="space-y-4">
                {shifts.map((shift) => (
                  <div key={shift.id} className="space-y-2">
                    <div className="flex items-center space-x-2 mb-2">
                      <div className="w-24 text-sm font-semibold text-gray-700">
                        {shift.name}
                      </div>
                      <div className="text-xs text-gray-500">
                        {shift.start_time?.substring(0, 5)} - {shift.end_time?.substring(0, 5)}
                      </div>
                    </div>
                    <div className="grid grid-cols-7 gap-2">
                      {weekDays.map((day) => {
                        const slotSchedules = getSchedulesForSlot(day.date, shift.id);

                        return (
                          <ScheduleSlot
                            key={`${day.date}-${shift.id}`}
                            day={day}
                            shift={shift}
                            schedules={slotSchedules}
                            isToday={day.isToday}
                            onRemoveStaff={handleRemoveStaff}
                          />
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      <DragOverlay>
        {draggedItem && draggedItem.id.toString().startsWith('staff-') && (
          <div className="opacity-50">
            <StaffCard
              staff={staffList.find((s) => s.id === parseInt(draggedItem.id.toString().replace('staff-', ''))) || {}}
              isDragging={true}
            />
          </div>
        )}
      </DragOverlay>
    </DndContext>
  );
};

export default WeeklySchedule;

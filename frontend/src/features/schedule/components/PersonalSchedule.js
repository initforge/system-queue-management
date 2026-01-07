import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../../shared/AuthContext';
import scheduleAPI from '../../../shared/services/api/schedule';
import { format, startOfWeek, addDays, isSameDay } from 'date-fns';

const PersonalSchedule = () => {
  const { user } = useAuth();
  const [currentWeek, setCurrentWeek] = useState(startOfWeek(new Date(), { weekStartsOn: 1 }));
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);

  // Generate week days (Monday to Sunday)
  const weekDays = useMemo(() => {
    const days = [];
    for (let i = 0; i < 7; i++) {
      const date = addDays(currentWeek, i);
      days.push({
        date: format(date, 'yyyy-MM-dd'),
        dayName: format(date, 'EEE'),
        dayNumber: format(date, 'dd'),
        isToday: isSameDay(date, new Date())
      });
    }
    return days;
  }, [currentWeek]);



  // Load personal schedule
  const loadPersonalSchedule = useCallback(async () => {
    if (!user) return;

    try {
      setLoading(true);
      const startDate = format(currentWeek, 'yyyy-MM-dd');
      const schedulesData = await scheduleAPI.getWeeklySchedule(startDate, user.id);

      // Transform API response to component format
      const transformedSchedules = (Array.isArray(schedulesData) ? schedulesData : []).map(s => ({
        id: s.id,
        scheduled_date: s.scheduled_date,
        shift_id: s.shift_id,
        shift: {
          id: s.shift_id,
          name: s.shift_name,
          shift_type: s.shift_type,
          start_time: s.start_time,
          end_time: s.end_time
        },
        status: s.status,
        notes: s.notes
      }));

      setSchedules(transformedSchedules);
    } catch (error) {
      console.error('Error loading personal schedule:', error);
      setSchedules([]);
    } finally {
      setLoading(false);
    }
  }, [currentWeek, user]);

  useEffect(() => {
    loadPersonalSchedule();
  }, [loadPersonalSchedule]);

  // Real-time updates via WebSocket
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token || !user) return;

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsBaseUrl = process.env.REACT_APP_WS_URL || `${wsProtocol}//${window.location.hostname}:8000/ws`;
    const wsUrl = `${wsBaseUrl}/api/v1/schedule/ws/${user.id}?token=${token}`;
    let ws;
    let reconnectTimeout;

    const connect = () => {
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('PersonalSchedule WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'schedule_updated' || data.type === 'bulk_update') {
            console.log('Schedule updated, refreshing...');
            loadPersonalSchedule();
          }
        } catch (e) {
          console.error('WebSocket message parse error:', e);
        }
      };

      ws.onclose = () => {
        console.log('PersonalSchedule WebSocket disconnected, reconnecting...');
        reconnectTimeout = setTimeout(connect, 3000);
      };

      ws.onerror = (error) => {
        console.error('PersonalSchedule WebSocket error:', error);
      };
    };

    connect();

    return () => {
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, [user, loadPersonalSchedule]);

  // Get shift for a specific date
  const getShiftForDate = (date) => {
    return schedules.find(s => s.scheduled_date === date);
  };

  // Shift type colors
  const getShiftColors = (shiftType) => {
    switch (shiftType) {
      case 'morning':
        return {
          bg: 'bg-gradient-to-br from-yellow-100 to-amber-100',
          border: 'border-yellow-300',
          text: 'text-yellow-800',
          icon: '🌅'
        };
      case 'afternoon':
        return {
          bg: 'bg-gradient-to-br from-orange-100 to-red-100',
          border: 'border-orange-300',
          text: 'text-orange-800',
          icon: '☀️'
        };
      case 'night':
        return {
          bg: 'bg-gradient-to-br from-indigo-100 to-purple-100',
          border: 'border-indigo-300',
          text: 'text-indigo-800',
          icon: '🌙'
        };
      default:
        return {
          bg: 'bg-gray-100',
          border: 'border-gray-300',
          text: 'text-gray-800',
          icon: '📅'
        };
    }
  };

  // Navigate weeks
  const goToPreviousWeek = () => {
    setCurrentWeek(prev => addDays(prev, -7));
  };

  const goToNextWeek = () => {
    setCurrentWeek(prev => addDays(prev, 7));
  };

  const goToCurrentWeek = () => {
    setCurrentWeek(startOfWeek(new Date(), { weekStartsOn: 1 }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <span className="ml-4 text-gray-600">Đang tải lịch làm việc...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Week Navigation */}
      <div className="flex items-center justify-between bg-white rounded-xl p-4 shadow-md">
        <div className="flex items-center space-x-4">
          <button
            onClick={goToPreviousWeek}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
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
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <div className="text-lg font-semibold text-gray-900">
          {format(currentWeek, 'dd MMM')} - {format(addDays(currentWeek, 6), 'dd MMM yyyy')}
        </div>
      </div>

      {/* Schedule Timeline */}
      <div className="bg-white rounded-xl p-6 shadow-md">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Lịch làm việc của tôi</h2>

        <div className="space-y-4">
          {weekDays.map(day => {
            const schedule = getShiftForDate(day.date);
            const colors = schedule ? getShiftColors(schedule.shift?.shift_type) : null;

            return (
              <motion.div
                key={day.date}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className={`
                  rounded-xl p-4 border-2 transition-all
                  ${schedule
                    ? `${colors.bg} ${colors.border}`
                    : 'bg-gray-50 border-gray-200'
                  }
                  ${day.isToday ? 'ring-2 ring-blue-400 ring-offset-2' : ''}
                `}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 flex-1">
                    <div className={`
                      text-center min-w-[80px]
                      ${day.isToday ? 'text-blue-600 font-bold' : 'text-gray-700'}
                    `}>
                      <div className="text-sm">{day.dayName}</div>
                      <div className="text-xl">{day.dayNumber}</div>
                    </div>

                    {schedule ? (
                      <motion.div
                        initial={{ scale: 0.9 }}
                        animate={{ scale: 1 }}
                        className="flex-1 flex items-center space-x-4"
                      >
                        <div className="text-2xl">{colors.icon}</div>
                        <div className="flex-1">
                          <div className={`text-lg font-semibold ${colors.text}`}>
                            {schedule.shift?.name || 'Ca làm việc'}
                          </div>
                          <div className="text-sm text-gray-600">
                            {schedule.shift?.start_time?.substring(0, 5)} - {schedule.shift?.end_time?.substring(0, 5)}
                          </div>
                        </div>
                        {schedule.notes && (
                          <div className="text-sm text-gray-600 italic">
                            {schedule.notes}
                          </div>
                        )}
                      </motion.div>
                    ) : (
                      <div className="flex-1 text-gray-400 text-center py-2">
                        Không có ca làm việc
                      </div>
                    )}
                  </div>

                  {schedule && day.isToday && (
                    <div className="ml-4">
                      <span className="px-3 py-1 bg-blue-500 text-white text-xs rounded-full font-medium">
                        Hôm nay
                      </span>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default PersonalSchedule;




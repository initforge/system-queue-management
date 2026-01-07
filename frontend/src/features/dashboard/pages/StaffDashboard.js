import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../../shared/AuthContext';
import { useWebSocket } from '../../../shared/WebSocketContext';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertModal, ConfirmModal } from '../../../shared/components/ui/ProfessionalModal';
import { ApiClient } from '../../../shared/services/api/client';
import ScheduleManagement from '../../schedule/ScheduleManagement';
import AIHelper from '../../ai-helper/AIHelper';


// API client
const api = new ApiClient();

// Animation components
const FadeIn = ({ children, className = "", delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
    className={className}
  >
    {children}
  </motion.div>
);

const ScaleIn = ({ children, className = "", delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.5, delay }}
    className={className}
  >
    {children}
  </motion.div>
);

// Notification Card Component with expand feature
const NotificationCard = ({ notification, index, onMarkAsRead }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleCardClick = () => {
    if (!notification.isRead && onMarkAsRead) {
      onMarkAsRead(notification.id);
    }
    setIsExpanded(!isExpanded);
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      onClick={handleCardClick}
      className={`border rounded-xl p-4 hover:shadow-md transition-shadow cursor-pointer ${notification.type === 'complaint_notification' || notification.type === 'complaint'
        ? 'bg-gradient-to-r from-red-50 to-orange-50 border-red-200'
        : notification.type === 'success'
          ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200'
          : 'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200'
        } ${!notification.isRead ? 'ring-2 ring-blue-200' : 'opacity-90'}`}
    >
      <div className="flex items-start space-x-4">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${notification.type === 'complaint_notification' || notification.type === 'complaint'
          ? 'bg-gradient-to-br from-red-400 to-orange-500'
          : notification.type === 'success'
            ? 'bg-gradient-to-br from-green-400 to-emerald-500'
            : 'bg-gradient-to-br from-blue-400 to-indigo-500'
          }`}>
          <span className="text-white text-lg">
            {notification.type === 'complaint_notification' || notification.type === 'complaint' ? '🚩' :
              notification.type === 'success' ? '✅' :
                notification.type === 'warning' ? '⚠️' : '💡'}
          </span>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <h4 className="font-semibold text-gray-800">
                {notification.title || 'Thông báo hệ thống'}
              </h4>
              {!notification.isRead && (
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              )}
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-500">
                {notification.time || new Date().toLocaleTimeString('vi-VN')}
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setIsExpanded(!isExpanded);
                }}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg
                  className={`w-4 h-4 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
          </div>

          {/* Collapsed view */}
          {!isExpanded && (
            <p className="text-gray-700 leading-relaxed line-clamp-2">
              {notification.message?.length > 100
                ? notification.message.substring(0, 100) + '...'
                : notification.message}
            </p>
          )}

          {/* Expanded view */}
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-3"
            >
              <p className="text-gray-700 leading-relaxed">
                {notification.message}
              </p>

              {(notification.type === 'complaint_notification' || notification.type === 'complaint') && notification.complaintDetails && (
                <div className="bg-white bg-opacity-50 rounded-lg p-4 space-y-2">
                  <h5 className="font-medium text-gray-800 mb-3">Chi tiết khiếu nại:</h5>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <span className="text-sm text-gray-600">Khách hàng:</span>
                      <p className="font-medium">{notification.complaintDetails.customer_name}</p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Số điện thoại:</span>
                      <p className="font-medium">{notification.complaintDetails.customer_phone}</p>
                    </div>
                    <div className="md:col-span-2">
                      <span className="text-sm text-gray-600">Mã vé:</span>
                      <p className="font-medium text-blue-600">#{notification.complaintDetails.ticket_number}</p>
                    </div>
                    <div className="md:col-span-2">
                      <span className="text-sm text-gray-600">Nội dung khiếu nại:</span>
                      <p className="font-medium bg-gray-50 p-2 rounded mt-1">
                        {notification.complaintDetails.content}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {notification.action && (
                <button className="mt-3 px-4 py-2 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition-colors">
                  {notification.action}
                </button>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

// Skeleton Loading Components để tránh flickering (inline sử dụng)

// Real-time wait counter component with WebSocket sync
const RealTimeCounter = ({ createdAt, ticketId }) => {
  const [waitTime, setWaitTime] = useState('00:00');

  useEffect(() => {
    if (!createdAt) return;

    let intervalId;

    const updateWaitTime = () => {
      const now = new Date();
      const created = new Date(createdAt);
      const elapsedMs = now - created;
      const elapsedMinutes = Math.floor(elapsedMs / 60000);
      const elapsedSeconds = Math.floor((elapsedMs % 60000) / 1000);

      // Giống homepage: tự đếm không cần WebSocket/refresh
      if (elapsedMinutes >= 10) {
        setWaitTime(">10p");
        if (intervalId) {
          clearInterval(intervalId);
          intervalId = null;
        }
        return;
      } else {
        setWaitTime(`${elapsedMinutes}:${elapsedSeconds.toString().padStart(2, '0')}`);
      }
    };

    updateWaitTime(); // Initial update
    intervalId = setInterval(updateWaitTime, 1000); // Tự đếm mỗi giây như homepage

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [createdAt]); // Chỉ phụ thuộc vào createdAt, không cần WebSocket

  return (
    <span className="font-mono text-sm tracking-wider text-gray-600">
      {waitTime}
    </span>
  );
};

const StaffDashboard = () => {
  const { user, logout } = useAuth();
  const { socket, isConnected } = useWebSocket();
  const [activeTab, setActiveTab] = useState('queue');
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [currentTicket, setCurrentTicket] = useState(null);

  // Modal states
  const [showNotificationModal, setShowNotificationModal] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [ticketToComplete, setTicketToComplete] = useState(null);
  const [ticketToCancel, setTicketToCancel] = useState(null);

  // Data states
  const [queueData, setQueueData] = useState([]);
  const [performanceData, setPerformanceData] = useState({
    todayStats: { ticketsServed: 0, avgServiceTime: 0, avgRating: 0 },
    weeklyStats: [],
    rankingPosition: 1,
    totalStaff: 4,
    ratingDistribution: [] // Add real rating distribution
  });
  const [departmentInfo, setDepartmentInfo] = useState({
    name: 'Đang tải...',
    code: ''
  });
  const [staffSettings, setStaffSettings] = useState({
    theme: 'light',
    notifications: true,
    language: 'vi',
    displayMode: 'compact'
  });

  // Additional states
  const [notifications, setNotifications] = useState([]);
  const [showProfessionalNotificationModal, setShowProfessionalNotificationModal] = useState(false);
  const [overviewStats, setOverviewStats] = useState({
    shiftStatus: 'ready',
    waitingCount: 0,
    servedToday: 0,
    averageRating: 0
  });

  // Chat states


  // Handle notifications
  const handleNotification = useCallback((data) => {
    setNotifications(prev => [data, ...prev.slice(0, 4)]);
    setNotificationMessage(data.message);
  }, []);

  // Handle ticket updates from WebSocket
  const handleTicketUpdate = useCallback((data) => {
    if (data.type === 'queue_update') {
      setQueueData(data.queue || []);
    } else if (data.type === 'current_ticket_update') {
      setCurrentTicket(data.ticket);
    } else if (data.type === 'stats_update') {
      setOverviewStats(prev => ({
        ...prev,
        ...data.stats
      }));
    }
  }, []);

  // Handle new messages from WebSocket
  const handleNewMessage = useCallback((data) => {
    // Logic for new messages would go here if chat was enabled
  }, []);

  // Load notifications from API
  // TODO: NOTIFICATIONS FEATURE - ĐANG TẠM NGƯNG PHÁT TRIỂN
  // CHỈ ĐƯỢC PHÁT TRIỂN KHI CÓ LỆNH RÕ RÀNG TỪ USER
  /*
  const loadNotifications = useCallback(async () => {
    try {
      // console.log('🔔 Loading notifications for staff...');
      // const response = await api.get('staff/notifications?limit=10');
      // console.log('🔔 Raw API response:', response);
      
      // if (!response) {
      //   console.log('🔔 No response from API');
      //   return;
      // }
      
      // const notifications = response?.notifications || [];
      // console.log('🔔 Extracted notifications array:', notifications);
      
      // Format notifications for UI compatibility
      // const formattedNotifications = notifications.map(notification => ({
      //   id: notification.id,
      //   type: notification.notification_type,
      //   title: notification.title,
      //   message: notification.message,
      //   time: notification.time,
      //   complaintDetails: notification.complaint_details,
      //   isRead: notification.is_read,
      //   created_at: notification.created_at
      // }));
      
      // console.log('🔔 Formatted notifications:', formattedNotifications);
      // console.log('🔔 Setting notifications state...');
      // setNotifications(formattedNotifications);
      // console.log('🔔 Notifications state updated!');
      
      // TEMPORARY: Set empty notifications to prevent UI errors
      setNotifications([]);
    } catch (error) {
      console.error("❌ Error loading notifications:", error);
      setNotifications([]); // Fallback to empty array
    }
  }, []);
  */

  // Mark notification as read
  // TODO: NOTIFICATIONS FEATURE - ĐANG TẠM NGƯNG PHÁT TRIỂN  
  const markNotificationAsRead = useCallback(async (notificationId) => {
    try {
      // await api.patch(`staff/notifications/${notificationId}/read`);
      // // Update local state
      // setNotifications(prev => prev.map(notification =>
      //   notification.id === notificationId
      //     ? { ...notification, isRead: true }
      //     : notification
      // ));
      console.log("Notifications feature temporarily disabled");
    } catch (error) {
      console.error("Error marking notification as read:", error);
    }
  }, []);

  // Load dashboard data with real-time database query - SMOOTH NO-FLICKER VERSION
  const loadDashboardData = useCallback(async () => {
    if (!user) return;

    // Chỉ track lần đầu load thôi, không loading khi refresh

    try {
      // Real-time query tickets with status "waiting" and "called" from database
      const queueResponse = await api.get('staff/queue');

      // Backend should return both waiting and called tickets for this staff
      const allTickets = Array.isArray(queueResponse) ? queueResponse : [];

      setQueueData(allTickets);

      // Get current ticket being served (status "called")
      const currentResponse = await api.get('staff/current-ticket');
      setCurrentTicket(currentResponse?.current_ticket || null);

      // Load notifications from database  
      // TODO: NOTIFICATIONS DISABLED - await loadNotifications();

      // Load department info (chỉ load lần đầu)
      if (isInitialLoad) {
        const deptResponse = await api.get('staff/department');
        setDepartmentInfo(deptResponse || { name: 'Phòng Ban', code: '' });
      }

      // Update overview stats with real-time data
      const overviewResponse = await api.get('staff/dashboard/overview');
      setOverviewStats({
        shiftStatus: 'ready',
        waitingCount: allTickets.filter(ticket => ticket.status === 'waiting').length,
        servedToday: overviewResponse?.completed_today || 0,
        averageRating: overviewResponse?.average_rating || 0,
        completed_today: overviewResponse?.completed_today || 0,
        average_rating: overviewResponse?.average_rating || 0
      });

      if (activeTab === 'performance') {
        // GỌI API MỚI CHO PERFORMANCE DATA VỚI DỮ LIỆU THẬT TỪ DATABASE  
        const perfResponse = await api.get('staff/performance/weekly');

        // Load rating distribution from database
        const ratingsResponse = await api.get('staff/performance/ratings-distribution');

        // Cập nhật với dữ liệu thật từ overviewResponse (đã có todayStats)
        setPerformanceData({
          todayStats: {
            ticketsServed: overviewResponse?.todayStats?.ticketsServed || overviewResponse?.completed_today || 0,
            complaints: overviewResponse?.todayStats?.complaints || 0,
            avgRating: overviewResponse?.todayStats?.avgRating || overviewResponse?.average_rating || 0.0
          },
          rankingPosition: overviewResponse?.rankingPosition || perfResponse?.ranking || 1,
          totalStaff: overviewResponse?.totalStaff || 4,
          weeklyChart: perfResponse?.weeklyChart || [], // Real chart data
          ratingDistribution: ratingsResponse?.ratingDistribution || [] // Real rating data
        });
      }

    } catch (error) {
      console.error("Error loading dashboard data:", error);
      if (isInitialLoad) {
        setQueueData([]);
        setCurrentTicket(null);
        setDepartmentInfo({ name: 'Phòng Ban', code: '' });
        setOverviewStats({
          shiftStatus: 'ready',
          waitingCount: 0,
          servedToday: 0,
          averageRating: 0,
          completed_today: 0,
          average_rating: 0
        });
      }
    } finally {
      if (isInitialLoad) {
        setIsInitialLoad(false); // Đánh dấu đã load xong lần đầu
      }
    }
  }, [user, activeTab, isInitialLoad]);

  // Load chat rooms
  // TODO: Chat feature sẽ được phát triển sau - đang comment tạm thời
  // Khi nào cần phát triển tính năng chat thì uncomment và implement backend endpoint
  const loadChatRooms = useCallback(async () => {
    // Chat feature disabled
  }, []);



  // Handle ticket actions
  const callNextTicket = async () => {
    // Check if staff is already serving someone (any ticket with status "called")
    const calledTicket = queueData.find(ticket => ticket.status === 'called');
    if (calledTicket) {
      setShowNotificationModal(true);
      setNotificationMessage("Bạn vẫn đang phục vụ một khách hàng! Vui lòng hoàn thành hoặc hủy trước khi gọi khách tiếp theo.");
      return;
    }

    try {
      // Call next ticket: waiting -> called - FIX: dùng POST thay vì PUT
      const response = await api.post('staff/queue/call-next');

      if (response?.id) {
        // Update current ticket being served
        setCurrentTicket(response);
        setShowNotificationModal(true);
        setNotificationMessage(`Đã gọi khách hàng ${response.ticket_number}`);

        // Refresh dashboard to update queue table and current ticket display
        await loadDashboardData();
      } else {
        setShowNotificationModal(true);
        setNotificationMessage("Không có khách hàng trong hàng đợi!");
      }
    } catch (error) {
      setShowNotificationModal(true);
      setNotificationMessage(
        error.response?.data?.detail || error.response?.data?.message || error.message || "Có lỗi xảy ra khi gọi khách hàng!"
      );
    } finally {
      // Refresh data sau khi gọi
      loadDashboardData();
    }
  };

  const completeTicket = async (ticket) => {
    // Find the ticket that is currently being served (status "called")
    const ticketToProcess = ticket || queueData.find(t => t.status === 'called');
    if (!ticketToProcess) {
      setShowNotificationModal(true);
      setNotificationMessage("Không có vé nào đang được phục vụ để hoàn thành!");
      return;
    }

    setTicketToComplete(ticketToProcess);
    setShowCompleteModal(true);
  };

  const confirmCompleteTicket = async () => {
    if (!ticketToComplete) return;

    try {
      // Complete ticket: called -> completed
      await api.put(`staff/tickets/${ticketToComplete.id}/complete`);

      // Clear current ticket and refresh dashboard
      setCurrentTicket(null);
      setShowCompleteModal(false);
      setTicketToComplete(null);
      setShowNotificationModal(true);
      setNotificationMessage(`Đã hoàn thành phục vụ khách hàng ${ticketToComplete.ticket_number}! Khách hàng sẽ được chuyển đến trang đánh giá.`);

      // Refresh dashboard immediately to show updated data
      await loadDashboardData();

      // Note: When ticket status becomes "completed", customer at /waiting/{ticketId} 
      // will be automatically redirected to /review/{ticketId} via WebSocket or polling

    } catch (error) {
      console.error("Error completing ticket:", error);
      setShowNotificationModal(true);
      setNotificationMessage(
        error.response?.data?.detail || "Có lỗi xảy ra khi hoàn thành vé!"
      );
    } finally {
      // Reset modal states
      setTicketToComplete(null);
      setShowCompleteModal(false);
    }
  };

  const cancelTicket = (ticket) => {
    // Find the ticket to cancel - either passed ticket or current called ticket
    const ticketToProcess = ticket || queueData.find(t => t.status === 'called');
    if (!ticketToProcess) {
      setShowNotificationModal(true);
      setNotificationMessage("Không có vé nào để hủy!");
      return;
    }

    setTicketToCancel(ticketToProcess);
    setShowCancelModal(true);
  };

  const confirmCancelTicket = async () => {
    if (!ticketToCancel) return;

    try {
      // Cancel ticket: waiting/called -> no_show
      await api.put(`staff/tickets/${ticketToCancel.id}/cancel`);

      // Clear current ticket if canceling current served ticket (called status)
      if (ticketToCancel.status === 'called') {
        setCurrentTicket(null);
      }

      setShowCancelModal(false);
      setTicketToCancel(null);
      setShowNotificationModal(true);
      setNotificationMessage(`Đã hủy vé ${ticketToCancel.ticket_number}! Trạng thái: Không có mặt.`);

      // Refresh dashboard immediately to show updated data
      await loadDashboardData();
    } catch (error) {
      console.error("Error canceling ticket:", error);
      setShowNotificationModal(true);
      setNotificationMessage(
        error.response?.data?.detail || "Có lỗi xảy ra khi hủy vé!"
      );
    } finally {
      // Reset modal states
      setTicketToCancel(null);
      setShowCancelModal(false);
    }
  };

  // Handle logout
  const handleLogoutClick = () => {
    setShowLogoutModal(true);
  };

  const confirmLogout = () => {
    logout();
    setShowLogoutModal(false);
  };

  // Handle notification click
  const handleNotificationClick = () => {
    setShowProfessionalNotificationModal(true);
  };

  // Load initial data and setup WebSocket + Online Tracking
  useEffect(() => {
    if (!user) return;

    loadDashboardData();
    loadChatRooms();

    // 🔗 Set staff as online when dashboard loads
    const setOnlineStatus = async () => {
      try {
        await api.post('staff/status/online');
        console.log('Staff set to ONLINE');
      } catch (error) {
        console.error('Error setting online status:', error);
      }
    };
    setOnlineStatus();

    // 🔗 Handle page unload (browser close/refresh)
    const handleBeforeUnload = () => {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
      navigator.sendBeacon(`${apiUrl}/staff/status/offline`, JSON.stringify({}));
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    // Chỉ refresh khi đang ở tab queue và có queue data
    let refreshInterval;
    if (activeTab === 'queue') {
      refreshInterval = setInterval(() => {
        loadDashboardData();
      }, 5000); // Tăng từ 2s lên 5s để giảm flickering
    }

    if (socket) {
      socket.on('notification', handleNotification);
      socket.on('ticket_update', handleTicketUpdate);
      socket.on('new_message', handleNewMessage);

      socket.on('new_ticket_in_department', (data) => {
        if (data.department_id === user.department_id) {
          loadDashboardData();
        }
      });

      socket.on('ticket_status_changed', (data) => {
        if (data.department_id === user.department_id) {
          loadDashboardData();
        }
      });
    }

    return () => {
      // Set staff as offline when component unmounts
      const setOfflineStatus = async () => {
        try {
          await api.post('staff/status/offline');
          console.log('Staff set to OFFLINE');
        } catch (error) {
          console.error('Error setting offline status:', error);
        }
      };
      setOfflineStatus();

      window.removeEventListener('beforeunload', handleBeforeUnload);

      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
      if (socket) {
        socket.off('notification', handleNotification);
        socket.off('ticket_update', handleTicketUpdate);
        socket.off('new_message', handleNewMessage);
        socket.off('new_ticket_in_department');
        socket.off('ticket_status_changed');
      }
    };
  }, [user, socket, activeTab, loadDashboardData, handleNewMessage, loadChatRooms, handleNotification, handleTicketUpdate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-white to-blue-50 font-['Roboto',_sans-serif]">
      {/* Header */}
      <FadeIn className="bg-white/95 backdrop-blur-sm shadow-xl border-b border-blue-100">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <motion.div
                whileHover={{ rotate: 5, scale: 1.05 }}
                className="w-16 h-16 bg-gradient-to-r from-blue-500 to-blue-700 rounded-2xl flex items-center justify-center shadow-lg"
              >
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </motion.div>
              <div>
                <h1 className="text-2xl font-bold text-blue-900">Staff Dashboard</h1>
                <div className="flex items-center space-x-2">
                  <span className="text-blue-600 text-sm">{departmentInfo.name || 'Phòng Khám'}, </span>
                  <span className="font-semibold text-gray-900" style={{ fontFamily: '"Inter", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif' }}>
                    {user?.full_name || user?.username || 'Nhân viên'}
                  </span>
                  <span className="px-3 py-1 bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 text-xs rounded-full font-medium">
                    {user?.role === 'staff' ? 'Nhân viên' :
                      user?.role === 'manager' ? 'Quản lý' :
                        user?.role === 'admin' ? 'Quản trị' : 'Nhân viên'}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* WebSocket Status Indicator */}
              <motion.div
                className="flex items-center space-x-2 px-3 py-2 rounded-full bg-white/80 backdrop-blur border border-gray-200 shadow-sm"
                whileHover={{ scale: 1.05 }}
              >
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
                <span className={`text-xs font-medium ${isConnected ? 'text-green-700' : 'text-red-700'}`}>
                  {isConnected ? 'Kết nối' : 'Offline'}
                </span>
              </motion.div>

              <motion.div className="relative" whileHover={{ scale: 1.05 }}>
                <motion.div
                  whileHover={{ scale: 1.1 }}
                  onClick={handleNotificationClick}
                  className="w-10 h-10 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center cursor-pointer shadow-lg"
                >
                  <span className="text-lg">🔔</span>
                </motion.div>
                {notifications.length > 0 && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-white text-xs flex items-center justify-center">
                    {notifications.length}
                  </span>
                )}
              </motion.div>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleLogoutClick}
                className="px-6 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all"
              >
                Đăng xuất
              </motion.button>
            </div>
          </div>
        </div>
      </FadeIn>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex space-x-4 overflow-x-auto pb-2">
          <TabButton
            active={activeTab === 'queue'}
            onClick={() => setActiveTab('queue')}
            icon="👥"
            text="Quản lý hàng đợi"
          />
          <TabButton
            active={activeTab === 'shift'}
            onClick={() => setActiveTab('shift')}
            icon="🕒"
            text="Ca làm việc"
          />
          <TabButton
            active={activeTab === 'ai-helper'}
            onClick={() => setActiveTab('ai-helper')}
            icon="🤖"
            text="AI Helper"
          />
          <TabButton
            active={activeTab === 'performance'}
            onClick={() => setActiveTab('performance')}
            icon="📊"
            text="Hiệu suất"
          />
        </div>


        {/* Main Content */}
        <div className="mt-6">
          <AnimatePresence mode="wait">
            {/* Queue Management Tab */}
            {activeTab === 'queue' && (
              <motion.div
                key="queue"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <FadeIn className="bg-white/95 backdrop-blur rounded-2xl shadow-xl border border-blue-100 p-8">
                  <h2 className="text-3xl font-bold text-blue-900 mb-8 flex items-center">
                    <span className="text-4xl mr-3">📋</span>
                    Quản lý hàng đợi
                  </h2>

                  {(() => {
                    // Helper variables để tránh gọi find() nhiều lần
                    const waitingTickets = queueData.filter(ticket => ticket.status === 'waiting');
                    const calledTickets = queueData.filter(ticket => ticket.status === 'called');
                    const currentServedTicket = calledTickets[0]; // Chỉ có thể có 1 ticket called

                    return (
                      <>
                        {/* Status Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                          <ScaleIn delay={0.2} className="bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-lg p-4 border border-yellow-200">
                            <div className="flex items-center justify-between mb-2">
                              <h3 className="text-sm font-bold text-yellow-900">Số chờ</h3>
                              <span className="text-lg">⏳</span>
                            </div>
                            <div className="text-xl font-bold text-yellow-600">
                              {isInitialLoad ? (
                                <div className="h-6 bg-yellow-200 rounded animate-pulse w-8"></div>
                              ) : waitingTickets.length}
                            </div>
                            <p className="text-yellow-700 mt-1 text-xs">khách đang chờ</p>
                          </ScaleIn>

                          <ScaleIn delay={0.3} className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                            <div className="flex items-center justify-between mb-2">
                              <h3 className="text-sm font-bold text-blue-900">Đã xử lý</h3>
                              <span className="text-lg">✨</span>
                            </div>
                            <div className="text-xl font-bold text-blue-600">
                              {isInitialLoad ? (
                                <div className="h-6 bg-blue-200 rounded animate-pulse w-8"></div>
                              ) : (overviewStats.completed_today || 0)}
                            </div>
                            <p className="text-blue-700 mt-1 text-xs">hôm nay</p>
                          </ScaleIn>

                          <ScaleIn delay={0.4} className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
                            <div className="flex items-center justify-between mb-2">
                              <h3 className="text-sm font-bold text-purple-900">Đánh giá</h3>
                              <span className="text-lg">⭐</span>
                            </div>
                            <div className="text-xl font-bold text-purple-600">
                              {isInitialLoad ? (
                                <div className="h-6 bg-purple-200 rounded animate-pulse w-12"></div>
                              ) : `${(overviewStats.average_rating || 0).toFixed(1)}/5`}
                            </div>
                            <p className="text-purple-700 mt-1 text-xs">trung bình</p>
                          </ScaleIn>
                        </div>

                        {/* Current Ticket (if any) */}
                        {currentServedTicket && (
                          <FadeIn className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 rounded-2xl p-6 mb-6">
                            <div className="flex items-center justify-between">
                              <div>
                                <h3 className="text-xl font-bold text-gray-900 mb-2 flex items-center">
                                  <span className="text-2xl mr-2">🎫</span>
                                  Đang phục vụ: {currentServedTicket.ticket_number}
                                </h3>
                                <p className="text-gray-700">
                                  <strong>Khách hàng:</strong> {currentServedTicket.customer_name}
                                </p>
                                <p className="text-gray-700">
                                  <strong>Dịch vụ:</strong> {currentServedTicket.service_name}
                                </p>
                                <p className="text-gray-600 text-sm mt-1">
                                  <strong>Được gọi lúc:</strong> {currentServedTicket.called_at ? new Date(currentServedTicket.called_at).toLocaleTimeString() : 'Chưa xác định'}
                                </p>
                              </div>
                              <div className="flex flex-col gap-3">
                                <motion.button
                                  whileHover={{ scale: 1.05 }}
                                  whileTap={{ scale: 0.95 }}
                                  onClick={() => completeTicket()}
                                  disabled={isInitialLoad}
                                  className="px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all disabled:bg-gray-400"
                                >
                                  ✅ Hoàn thành phục vụ
                                </motion.button>
                                <motion.button
                                  whileHover={{ scale: 1.05 }}
                                  whileTap={{ scale: 0.95 }}
                                  onClick={() => cancelTicket()}
                                  disabled={isInitialLoad}
                                  className="px-6 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all disabled:bg-gray-400"
                                >
                                  ❌ Hủy khách
                                </motion.button>
                              </div>
                            </div>
                          </FadeIn>
                        )}
                      </>
                    );
                  })()}

                  {/* Queue Table */}
                  <FadeIn className="bg-white rounded-xl border border-blue-100 overflow-hidden shadow-md">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-gradient-to-r from-blue-50 to-blue-100 text-blue-900">
                          <tr>
                            <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider">STT</th>
                            <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider">Dịch vụ</th>
                            <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider">Trạng thái</th>
                            <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider">Thời gian chờ</th>
                            <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider">Thao tác</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {isInitialLoad ? (
                            // Skeleton Loading cho table
                            [...Array(3)].map((_, i) => (
                              <tr key={i} className="animate-pulse">
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="h-4 bg-gray-200 rounded w-16"></div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="h-4 bg-gray-200 rounded w-24"></div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="h-4 bg-gray-200 rounded w-20"></div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="h-4 bg-gray-200 rounded w-20"></div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="flex space-x-2">
                                    <div className="h-8 bg-gray-200 rounded w-16"></div>
                                    <div className="h-8 bg-gray-200 rounded w-20"></div>
                                  </div>
                                </td>
                              </tr>
                            ))
                          ) : queueData.length === 0 ? (
                            <tr>
                              <td colSpan={5} className="px-6 py-16 text-center">
                                <div className="text-4xl mb-2">📭</div>
                                <p className="text-gray-500">Không có khách hàng đang chờ</p>
                              </td>
                            </tr>
                          ) : (
                            queueData.map((ticket) => {
                              const isWaiting = ticket.status === 'waiting';
                              const isCalled = ticket.status === 'called';

                              return (
                                <tr
                                  key={ticket.id}
                                  className={`transition-colors ${isCalled
                                    ? 'bg-green-50 border-l-4 border-green-500'
                                    : 'hover:bg-blue-50'
                                    }`}
                                >
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`font-semibold ${isCalled ? 'text-green-700' : 'text-gray-900'
                                      }`}>
                                      {ticket.ticket_number}
                                    </span>
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={isCalled ? 'text-green-700' : 'text-gray-900'}>
                                      {ticket.service_name}
                                    </span>
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    {isCalled ? (
                                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                        🎯 Đang phục vụ
                                      </span>
                                    ) : (
                                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                        ⏳ Đang chờ
                                      </span>
                                    )}
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    <RealTimeCounter createdAt={ticket.created_at} ticketId={ticket.id} />
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="flex space-x-2">
                                      {/* Nút Gọi - chỉ hiển thị cho ticket waiting và khi không có currentTicket */}
                                      {isWaiting && !currentTicket && (
                                        <button
                                          onClick={() => callNextTicket(ticket)}
                                          className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
                                        >
                                          📢 Gọi
                                        </button>
                                      )}

                                      {/* Nút Hoàn thành - chỉ hiển thị cho ticket called */}
                                      {isCalled && (
                                        <button
                                          onClick={() => completeTicket(ticket)}
                                          className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600 transition-colors"
                                        >
                                          ✅ Hoàn thành
                                        </button>
                                      )}

                                      {/* Nút Hủy - hiển thị cho cả waiting và called */}
                                      <button
                                        onClick={() => cancelTicket(ticket)}
                                        className="px-3 py-1 bg-gray-500 text-white text-sm rounded hover:bg-gray-600 transition-colors"
                                      >
                                        ❌ Hủy
                                      </button>
                                    </div>
                                  </td>
                                </tr>
                              );
                            })
                          )}
                        </tbody>
                      </table>
                    </div>
                  </FadeIn>

                  {/* Queue Actions */}
                  {(() => {
                    const waitingCount = queueData.filter(ticket => ticket.status === 'waiting').length;
                    const calledCount = queueData.filter(ticket => ticket.status === 'called').length;
                    const hasCalledTicket = calledCount > 0;

                    return (
                      <div className="flex flex-wrap items-center justify-between mt-6 gap-4">
                        <div className="flex gap-4">
                          <div className="bg-yellow-100 rounded-lg px-4 py-2 text-sm border border-yellow-200">
                            <span className="font-semibold text-yellow-800">Đang chờ:</span>
                            <span className="text-yellow-900 ml-1">{waitingCount} khách</span>
                          </div>
                          <div className="bg-green-100 rounded-lg px-4 py-2 text-sm border border-green-200">
                            <span className="font-semibold text-green-800">Đang phục vụ:</span>
                            <span className="text-green-900 ml-1">{calledCount} khách</span>
                          </div>
                        </div>

                        <div className="flex flex-wrap gap-4">
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={callNextTicket}
                            disabled={isInitialLoad || hasCalledTicket}
                            className={`px-6 py-3 rounded-xl font-medium shadow-lg transition-all ${hasCalledTicket || isInitialLoad
                              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                              : 'bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:shadow-xl'
                              }`}
                          >
                            {isInitialLoad ? '⏳ Đang tải...' : '📢 Gọi khách tiếp theo'}
                          </motion.button>

                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => completeTicket()}
                            disabled={isInitialLoad || !hasCalledTicket}
                            className={`px-6 py-3 rounded-xl font-medium shadow-lg transition-all ${!hasCalledTicket || isInitialLoad
                              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                              : 'bg-gradient-to-r from-green-500 to-green-600 text-white hover:shadow-xl'
                              }`}
                          >
                            ✅ Hoàn thành phục vụ
                          </motion.button>

                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => cancelTicket()}
                            disabled={isInitialLoad || !hasCalledTicket}
                            className={`px-6 py-3 rounded-xl font-medium shadow-lg transition-all ${!hasCalledTicket || isInitialLoad
                              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                              : 'bg-gradient-to-r from-red-500 to-red-600 text-white hover:shadow-xl'
                              }`}
                          >
                            ❌ Hủy khách
                          </motion.button>
                        </div>
                      </div>
                    );
                  })()}
                </FadeIn>
              </motion.div>
            )}

            {/* Shift Management Tab */}
            {activeTab === 'shift' && (
              <motion.div
                key="shift"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <ScheduleManagement role="staff" staffId={user?.id} />
              </motion.div>
            )}

            {/* AI Helper Tab */}

            {activeTab === 'ai-helper' && (
              <motion.div
                key="ai-helper"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <FadeIn className="bg-white/95 backdrop-blur rounded-2xl shadow-xl border border-blue-100 p-8 h-[600px]">
                  <AIHelper role="staff" />
                </FadeIn>
              </motion.div>
            )}

            {/* Performance Tab */}
            {activeTab === 'performance' && (
              <motion.div
                key="performance"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <FadeIn className="bg-white/95 backdrop-blur rounded-2xl shadow-xl border border-blue-100 p-8">
                  <h2 className="text-3xl font-bold text-blue-900 mb-8 flex items-center">
                    <span className="text-4xl mr-3">📊</span>
                    Hiệu suất làm việc
                  </h2>

                  {/* Today's Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <ScaleIn delay={0.1} className="bg-gradient-to-r from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold text-green-900">Vé đã phục vụ</h3>
                        <span className="text-2xl">🎫</span>
                      </div>
                      <div className="text-3xl font-bold text-green-600 mb-2">
                        {performanceData?.todayStats?.ticketsServed || 0}
                      </div>
                      <p className="text-green-700 text-sm">vé hôm nay</p>
                    </ScaleIn>

                    <ScaleIn delay={0.2} className="bg-gradient-to-r from-red-50 to-red-100 rounded-xl p-6 border border-red-200">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold text-red-900">Khiếu nại</h3>
                        <span className="text-2xl">🚩</span>
                      </div>
                      <div className="text-3xl font-bold text-red-600 mb-2">
                        {performanceData?.todayStats?.complaints || 0}
                      </div>
                      <p className="text-red-700 text-sm">vụ hôm nay</p>
                    </ScaleIn>

                    <ScaleIn delay={0.3} className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold text-purple-900">Đánh giá TB</h3>
                        <span className="text-2xl">⭐</span>
                      </div>
                      <div className="text-3xl font-bold text-purple-600 mb-2">
                        {(performanceData?.todayStats?.avgRating || 0).toFixed(1)}/5
                      </div>
                      <p className="text-purple-700 text-sm">từ khách hàng</p>
                    </ScaleIn>
                  </div>

                  {/* Ranking */}
                  <FadeIn className="bg-gradient-to-r from-yellow-50 to-orange-100 rounded-xl p-6 border border-orange-200 mb-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-xl font-bold text-orange-900 mb-2">Xếp hạng</h3>
                        <p className="text-orange-700">Bạn đang đứng thứ {performanceData.rankingPosition} trong {performanceData.totalStaff} nhân viên</p>
                        <p className="text-orange-600 text-sm mt-1">
                          Dựa trên: Đánh giá TB → Khiếu nại (ít hơn)
                        </p>
                      </div>
                      <div className="text-6xl">
                        {performanceData.rankingPosition === 1 ? '🥇' :
                          performanceData.rankingPosition === 2 ? '🥈' :
                            performanceData.rankingPosition === 3 ? '🥉' : '📊'}
                      </div>
                    </div>
                  </FadeIn>

                  {/* Performance Charts */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Biểu đồ cột - Tickets theo ngày VỚI DỮ LIỆU THẬT TỪ DATABASE */}
                    <FadeIn className="bg-white rounded-xl border border-gray-200 p-6">
                      <h3 className="text-lg font-bold text-gray-900 mb-4">📊 Vé phục vụ 7 ngày qua</h3>
                      <div className="space-y-3">
                        {/* SỬ DỤNG DỮ LIỆU THẬT TỪ API staff/performance/weekly */}
                        {(performanceData?.weeklyChart || []).length > 0 ? (
                          performanceData.weeklyChart.map((item, index) => (
                            <div key={item.day} className="flex items-center space-x-3">
                              <span className="text-sm w-8 font-medium text-gray-600">{item.day}</span>
                              <div className="flex-1 flex items-center space-x-2">
                                {/* Tickets bar */}
                                <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
                                  <div
                                    className="bg-gradient-to-r from-blue-400 to-blue-600 h-6 rounded-full flex items-center justify-center transition-all duration-1000"
                                    style={{ width: `${Math.min((item.tickets || 0) * 6, 100)}%` }}
                                  >
                                    <span className="text-white text-xs font-semibold">{item.tickets || 0}</span>
                                  </div>
                                </div>
                                {/* Complaints indicator */}
                                {(item.complaints || 0) > 0 && (
                                  <div className="flex items-center space-x-1">
                                    <span className="text-red-500 text-sm">🚩</span>
                                    <span className="text-red-600 text-xs font-semibold">{item.complaints}</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          ))
                        ) : (
                          // Fallback nếu không có dữ liệu
                          <div className="text-center text-gray-500 py-4">
                            <p>Chưa có dữ liệu hiệu suất</p>
                          </div>
                        )}
                      </div>
                      <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
                        <span>📈 Vé phục vụ</span>
                        <span>🚩 Khiếu nại</span>
                      </div>
                    </FadeIn>

                    {/* Biểu đồ tròn - Rating distribution */}
                    <FadeIn className="bg-white rounded-xl border border-gray-200 p-6">
                      <h3 className="text-lg font-bold text-gray-900 mb-4">⭐ Phân bố đánh giá</h3>
                      <div className="flex items-center justify-center space-x-8">
                        {/* Donut chart */}
                        <div className="relative w-32 h-32">
                          <svg className="w-32 h-32 transform -rotate-90">
                            <circle cx="64" cy="64" r="50" stroke="#e5e7eb" strokeWidth="12" fill="transparent" />
                            <circle
                              cx="64" cy="64" r="50"
                              stroke="url(#gradient)"
                              strokeWidth="12"
                              fill="transparent"
                              strokeDasharray={`${(performanceData?.todayStats?.avgRating || 0) * 62.8} 314`}
                              className="transition-all duration-1000"
                            />
                            <defs>
                              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stopColor="#fbbf24" />
                                <stop offset="100%" stopColor="#f59e0b" />
                              </linearGradient>
                            </defs>
                          </svg>
                          <div className="absolute inset-0 flex items-center justify-center">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-yellow-600">
                                {performanceData?.todayStats?.avgRating || '0.0'}
                              </div>
                              <div className="text-xs text-gray-500">/ 5.0</div>
                            </div>
                          </div>
                        </div>

                        {/* Rating breakdown */}
                        <div className="space-y-2">
                          {(performanceData?.ratingDistribution || [
                            { stars: 5, count: 0, color: 'bg-green-400' },
                            { stars: 4, count: 0, color: 'bg-yellow-400' },
                            { stars: 3, count: 0, color: 'bg-orange-400' },
                            { stars: 2, count: 0, color: 'bg-red-400' },
                            { stars: 1, count: 0, color: 'bg-gray-400' }
                          ]).map(item => (
                            <div key={item.stars} className="flex items-center space-x-2 text-sm">
                              <span className="w-8 text-gray-600">{item.stars}⭐</span>
                              <div className="w-16 h-3 bg-gray-200 rounded-full">
                                <div
                                  className={`h-3 rounded-full ${item.color} transition-all duration-1000`}
                                  style={{ width: `${item.count * 4}%` }}
                                ></div>
                              </div>
                              <span className="text-gray-500 text-xs w-6">{item.count}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </FadeIn>
                  </div>
                </FadeIn>
              </motion.div>
            )}


            {/* Old Settings Tab - Removed */}
            {false && activeTab === 'settings' && (
              <motion.div
                key="settings"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <FadeIn className="bg-white/95 backdrop-blur rounded-2xl shadow-xl border border-blue-100 p-8">
                  <h2 className="text-3xl font-bold text-blue-900 mb-8 flex items-center">
                    <span className="text-4xl mr-3">⚙️</span>
                    Cài đặt
                  </h2>

                  <div className="space-y-6">
                    {/* Theme Settings */}
                    <div className="bg-gray-50 rounded-xl p-6">
                      <h3 className="text-lg font-semibold mb-4">Giao diện</h3>
                      <div className="space-y-3">
                        <label className="flex items-center space-x-3">
                          <input
                            type="radio"
                            name="theme"
                            checked={staffSettings.theme === 'light'}
                            onChange={() => setStaffSettings(prev => ({ ...prev, theme: 'light' }))}
                            className="text-blue-500"
                          />
                          <span>Sáng</span>
                        </label>
                        <label className="flex items-center space-x-3">
                          <input
                            type="radio"
                            name="theme"
                            checked={staffSettings.theme === 'dark'}
                            onChange={() => setStaffSettings(prev => ({ ...prev, theme: 'dark' }))}
                            className="text-blue-500"
                          />
                          <span>Tối</span>
                        </label>
                      </div>
                    </div>

                    {/* Notification Settings */}
                    <div className="bg-gray-50 rounded-xl p-6">
                      <h3 className="text-lg font-semibold mb-4">Thông báo</h3>
                      <label className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={staffSettings.notifications}
                          onChange={(e) => setStaffSettings(prev => ({ ...prev, notifications: e.target.checked }))}
                          className="text-blue-500"
                        />
                        <span>Nhận thông báo real-time</span>
                      </label>
                    </div>

                    {/* Language Settings */}
                    <div className="bg-gray-50 rounded-xl p-6">
                      <h3 className="text-lg font-semibold mb-4">Ngôn ngữ</h3>
                      <select
                        value={staffSettings.language}
                        onChange={(e) => setStaffSettings(prev => ({ ...prev, language: e.target.value }))}
                        className="px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500"
                      >
                        <option value="vi">Tiếng Việt</option>
                        <option value="en">English</option>
                      </select>
                    </div>

                    {/* Display Settings */}
                    <div className="bg-gray-50 rounded-xl p-6">
                      <h3 className="text-lg font-semibold mb-4">Hiển thị</h3>
                      <div className="space-y-3">
                        <label className="flex items-center space-x-3">
                          <input
                            type="radio"
                            name="displayMode"
                            checked={staffSettings.displayMode === 'compact'}
                            onChange={() => setStaffSettings(prev => ({ ...prev, displayMode: 'compact' }))}
                            className="text-blue-500"
                          />
                          <span>Gọn</span>
                        </label>
                        <label className="flex items-center space-x-3">
                          <input
                            type="radio"
                            name="displayMode"
                            checked={staffSettings.displayMode === 'comfortable'}
                            onChange={() => setStaffSettings(prev => ({ ...prev, displayMode: 'comfortable' }))}
                            className="text-blue-500"
                          />
                          <span>Thoải mái</span>
                        </label>
                      </div>
                    </div>
                  </div>
                </FadeIn>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Modals */}
      <AlertModal
        isOpen={showNotificationModal}
        onClose={() => setShowNotificationModal(false)}
        title="Thông báo"
        message={notificationMessage}
        type="info"
      />

      <ConfirmModal
        isOpen={showLogoutModal}
        onClose={() => setShowLogoutModal(false)}
        onConfirm={confirmLogout}
        title="Xác nhận đăng xuất"
        message="Bạn có chắc chắn muốn đăng xuất?"
        confirmText="Đăng xuất"
        cancelText="Hủy"
      />

      <ConfirmModal
        isOpen={showCompleteModal}
        onClose={() => setShowCompleteModal(false)}
        onConfirm={confirmCompleteTicket}
        title="Xác nhận hoàn thành"
        message={`Hoàn thành phục vụ cho khách hàng ${ticketToComplete?.ticket_number || ''}?`}
        confirmText="Hoàn thành"
        cancelText="Hủy"
      />

      <ConfirmModal
        isOpen={showCancelModal}
        onClose={() => setShowCancelModal(false)}
        onConfirm={confirmCancelTicket}
        title="Xác nhận hủy vé"
        message={`Hủy vé của khách hàng ${ticketToCancel?.ticket_number || ''}?`}
        confirmText="Hủy vé"
        cancelText="Quay lại"
      />

      {/* Professional Notification Modal for Staff */}
      {showProfessionalNotificationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden border border-gray-100"
          >
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 text-white p-6">
              <div className="flex justify-between items-center">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                    <span className="text-2xl">🔔</span>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold">Thông báo nhân viên</h2>
                    <p className="text-blue-100">Thông báo khiếu nại và công việc</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowProfessionalNotificationModal(false)}
                  className="text-white hover:text-blue-200 transition-colors p-2 rounded-full hover:bg-white hover:bg-opacity-20"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(80vh-140px)]">
              {notifications.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-24 h-24 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-4xl">📭</span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">Chưa có thông báo</h3>
                  <p className="text-gray-500">Tất cả thông báo sẽ được hiển thị tại đây</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-800">
                      Thông báo gần đây ({notifications.length})
                    </h3>
                    <button
                      onClick={() => setNotifications([])}
                      className="text-sm text-gray-500 hover:text-red-600 transition-colors"
                    >
                      Xóa tất cả
                    </button>
                  </div>

                  {notifications.map((notification, index) => (
                    <NotificationCard
                      key={notification.id || index}
                      notification={notification}
                      index={index}
                      onMarkAsRead={markNotificationAsRead}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">
                  Cập nhật lần cuối: {new Date().toLocaleString('vi-VN')}
                </span>
                <button
                  onClick={() => setShowProfessionalNotificationModal(false)}
                  className="px-6 py-2 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-lg hover:from-gray-700 hover:to-gray-800 transition-all"
                >
                  Đóng
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

// Tab Button Component
const TabButton = ({ active, onClick, icon, text }) => (
  <motion.button
    whileHover={{ scale: 1.05 }}
    whileTap={{ scale: 0.95 }}
    onClick={onClick}
    className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors whitespace-nowrap ${active
      ? 'bg-blue-500 text-white shadow-md'
      : 'bg-white text-gray-700 hover:bg-gray-100'
      }`}
  >
    <span className="text-lg">{icon}</span>
    <span>{text}</span>
  </motion.button>
);

export default StaffDashboard;
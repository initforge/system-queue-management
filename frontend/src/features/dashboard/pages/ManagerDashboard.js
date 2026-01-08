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

const ManagerDashboard = () => {
  const { user, logout } = useAuth();
  const { socket } = useWebSocket();
  const [activeTab, setActiveTab] = useState('staff');
  const [loading, setLoading] = useState(false);

  // Modal states
  const [showNotificationModal, setShowNotificationModal] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [notifications, setNotifications] = useState([]);

  // Data states
  const [staffList, setStaffList] = useState([]);
  const [complaintsList, setComplaintsList] = useState([]);
  const [managerName, setManagerName] = useState('Đang tải...');
  const [complaintStats, setComplaintStats] = useState({
    waiting: 0,
    completed: 0
  });
  const [dashboardStats, setDashboardStats] = useState({
    onlineStaff: 0,
    activeTickets: 0,
    averagePerformance: 0
  });
  const [managerSettings, setManagerSettings] = useState({
    theme: 'light',
    notifications: true,
    language: 'vi',
    reportFormat: 'pdf'
  });

  // Add complaint detail modal states
  const [showComplaintDetailModal, setShowComplaintDetailModal] = useState(false);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [showProfessionalNotificationModal, setShowProfessionalNotificationModal] = useState(false);
  const [showResolveConfirmModal, setShowResolveConfirmModal] = useState(false);

  // Function to resolve complaint
  const resolveComplaint = async (complaintId, resolution = '') => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No token found');
        logout();
        return;
      }

      await api.resolveComplaint(complaintId, resolution);

      // Update local state - remove complaint from waiting list
      setComplaintsList(prev => prev.filter(c => c.id !== complaintId));

      setComplaintStats(prev => ({
        waiting: prev.waiting - 1,
        completed: prev.completed + 1
      }));

      setShowComplaintDetailModal(false);
      setSelectedComplaint(null);

      // Show success notification
      handleNotification({
        message: `✅ Khiếu nại #${complaintId} đã được giải quyết thành công`
      });

      // Refresh complaints data
      await loadComplaints();
    } catch (error) {
      console.error('Error resolving complaint:', error);
      if (error.message.includes('401') || error.message.includes('Authentication')) {
        logout();
      } else {
        handleNotification({
          message: `❌ Không thể giải quyết khiếu nại: ${error.message}`
        });
      }
    }
  };

  // Function to handle resolve confirmation
  const handleResolveComplaint = () => {
    setShowResolveConfirmModal(true);
  };

  // Function to confirm resolve action
  const confirmResolveComplaint = () => {
    setShowResolveConfirmModal(false);
    resolveComplaint(selectedComplaint.id);
  };

  // Function to send notification to staff
  const sendNotificationToStaff = async (staffEmail, complaintData) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No token found');
        logout();
        return;
      }

      const notificationData = {
        recipient_email: staffEmail,
        title: 'Khiếu nại từ khách hàng',
        message: `Khách hàng ${complaintData.customer_name} (${complaintData.customer_phone}) đã gửi khiếu nại về vé #${complaintData.ticket_number}:\n\n"${complaintData.content}"\n\nVui lòng kiểm tra và phản hồi.`,
        type: 'complaint_notification',
        customer_name: complaintData.customer_name,
        customer_phone: complaintData.customer_phone,
        ticket_number: complaintData.ticket_number,
        complaint_content: complaintData.content
      };

      const response = await api.post('manager/send-staff-notification', notificationData);

      if (response.ok) {
        const responseData = await response.json();
        handleNotification({
          message: `Đã gửi thông báo cho nhân viên ${responseData.recipient}`
        });
      } else if (response.status === 401) {
        console.error('Authentication failed');
        logout();
      } else {
        console.error('Failed to send notification:', response.status);
        handleNotification({
          message: `Lỗi khi gửi thông báo cho nhân viên`
        });
      }
    } catch (error) {
      console.error("Error sending notification:", error);
      handleNotification({
        message: `Lỗi khi gửi thông báo cho nhân viên`
      });
    }
  };

  // Chat states
  const [chatRooms, setChatRooms] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageInput, setMessageInput] = useState('');
  const [emergencyMode, setEmergencyMode] = useState(false);
  const [emergencyReason, setEmergencyReason] = useState('');

  // Load complaints data
  const loadComplaints = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const data = await api.get('manager/manager-info');

      setComplaintStats({
        waiting: data.waiting_complaints || 0,
        completed: data.completed_complaints || 0
      });
      // Filter out completed complaints as requested
      const activeComplaints = (data.recent_complaints || []).filter(
        complaint => complaint.status !== 'completed'
      );
      setComplaintsList(activeComplaints);
    } catch (error) {
      console.error("Error loading complaints:", error);
    }
  }, []);

  // Load initial data
  useEffect(() => {
    if (user) {
      loadDashboardData();
      // loadChatRooms(); // Commented out to avoid 404 error
    }

    // Setup WebSocket listeners for realtime updates
    if (socket) {
      socket.on('staff_update', handleStaffUpdate);
      socket.on('new_message', handleNewMessage);
      socket.on('notification', handleNotification);
      socket.on('new_complaint', handleNewComplaint);

      return () => {
        socket.off('staff_update', handleStaffUpdate);
        socket.off('new_message', handleNewMessage);
        socket.off('notification', handleNotification);
        socket.off('new_complaint', handleNewComplaint);
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, socket]);

  // Auto-refresh complaints every 30 seconds
  useEffect(() => {
    if (user && activeTab === 'complaints') {
      loadComplaints();

      const interval = setInterval(loadComplaints, 30000); // Refresh every 30 seconds

      return () => clearInterval(interval);
    }
  }, [user, activeTab, loadComplaints]);

  // Update online staff count whenever staffList changes
  useEffect(() => {
    const onlineCount = staffList.filter(staff => staff.status === 'online').length;
    setDashboardStats(prev => ({
      ...prev,
      onlineStaff: onlineCount
    }));
  }, [staffList]);

  // Handle notifications
  const handleNotification = (data) => {
    setNotifications(prev => [data, ...prev].slice(0, 20));
    setShowNotificationModal(true);
    setNotificationMessage(data.message);
  };

  // Handle staff updates from WebSocket
  const handleStaffUpdate = (data) => {
    if (data.type === 'status_change') {
      setStaffList(prev => {
        const updated = prev.map(staff =>
          staff.id === data.staff_id ? { ...staff, status: data.status } : staff
        );
        
        // Update online staff count immediately
        const onlineCount = updated.filter(s => s.status === 'online').length;
        setDashboardStats(prevStats => ({
          ...prevStats,
          onlineStaff: onlineCount
        }));
        
        return updated;
      });
    } else if (data.type === 'performance_update') {
      setStaffList(prev => prev.map(staff =>
        staff.id === data.staff_id ? { ...staff, performance: data.performance } : staff
      ));
    }

    // Refresh full dashboard stats
    loadDashboardData();
  };

  // Handle new messages from WebSocket
  const handleNewMessage = (data) => {
    if (selectedRoom === data.roomId) {
      setMessages(prev => [...prev, data.message]);
    }

    // Update notification count for room
    setChatRooms(prev => prev.map(r => {
      if (r.id === data.roomId && selectedRoom !== data.roomId) {
        return { ...r, unreadCount: (r.unreadCount || 0) + 1 };
      }
      return r;
    }));
  };

  // Handle new complaints
  const handleNewComplaint = (data) => {
    setComplaintsList(prev => [data.complaint, ...prev]);
    handleNotification({
      message: `Khiếu nại mới từ khách hàng: ${data.complaint.customer_name}`
    });
  };

  // Load dashboard data
  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Check if token exists
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No token found, redirecting to login');
        logout();
        return;
      }

      // Load manager info and complaints data using ApiClient
      const managerData = await api.get('manager/manager-info');
      console.log('Manager data loaded:', managerData);
      setManagerName(managerData.manager_name || 'Manager');
      setComplaintStats({
        waiting: managerData.waiting_complaints || 0,
        completed: managerData.completed_complaints || 0
      });
      setComplaintsList(managerData.recent_complaints || []);

      // Cập nhật dashboard stats tổng hợp từ backend
      if (managerData.dashboard_stats) {
        setDashboardStats({
          onlineStaff: managerData.dashboard_stats.online_staff || 0,
          activeTickets: managerData.dashboard_stats.active_tickets || 0,
          averagePerformance: managerData.dashboard_stats.average_performance || 0
        });
      }

      // Load staff list using ApiClient
      const staffData = await api.get('manager/staff');
      const staffArray = Array.isArray(staffData) ? staffData : (staffData.data || staffData.value || []);
      setStaffList(staffArray);

    } catch (error) {
      console.error("Error loading dashboard data:", error);
      // If error contains authentication issues, redirect to login
      if (error.response?.status === 401 || (error.message && error.message.includes('401'))) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  };

  // Load complaints (now handled by loadDashboardData)

  // Load messages for selected room
  const loadMessages = async (roomId) => {
    try {
      const messagesResponse = await api.get(`manager/chat/messages/${roomId}`);
      const messagesArray = Array.isArray(messagesResponse) ? messagesResponse :
        (messagesResponse.data || messagesResponse.value || []);
      setMessages(messagesArray);

      // Mark room as read
      setChatRooms(prev => prev.map(r => {
        if (r.id === roomId) {
          return { ...r, unreadCount: 0 };
        }
        return r;
      }));
    } catch (error) {
      console.error("Error loading messages:", error);
    }
  };

  // Send chat message
  const sendMessage = async () => {
    if (!messageInput.trim() || !selectedRoom) return;

    try {
      await api.post(`manager/chat/messages/${selectedRoom}`, {
        content: messageInput,
        isEmergency: emergencyMode,
        emergencyReason: emergencyMode ? emergencyReason : undefined
      });

      setMessageInput('');
      setEmergencyMode(false);
      setEmergencyReason('');
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  // Handle room selection
  const handleRoomSelect = (roomId) => {
    setSelectedRoom(roomId);
    loadMessages(roomId);
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-white to-gray-200 font-['Roboto',_sans-serif]">
      {/* Header */}
      <FadeIn className="bg-white/95 backdrop-blur-sm shadow-xl border-b border-blue-100">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <motion.div
                whileHover={{ rotate: 5, scale: 1.05 }}
                className="w-16 h-16 bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl flex items-center justify-center shadow-lg"
              >
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </motion.div>
              <div>
                <h1 className="text-2xl font-bold text-blue-900">Manager Dashboard</h1>
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-gray-900" style={{ fontFamily: '"Inter", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif' }}>
                    {managerName || user?.full_name || user?.username || 'Quản lý'}
                  </span>
                  <span className="px-3 py-1 bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 text-xs rounded-full font-medium">
                    Quản lý
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
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
                onClick={handleLogoutClick}
                className="px-6 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl font-medium shadow-lg hover:from-red-600 hover:to-red-700 transition-colors"
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
            active={activeTab === 'staff'}
            onClick={() => setActiveTab('staff')}
            icon="👥"
            text="Quản lý nhân viên"
          />
          <TabButton
            active={activeTab === 'schedule'}
            onClick={() => setActiveTab('schedule')}
            icon="📅"
            text="Quản lý lịch làm việc"
          />
          <TabButton
            active={activeTab === 'ai-helper'}
            onClick={() => setActiveTab('ai-helper')}
            icon="🤖"
            text="AI Helper"
          />
          <TabButton
            active={activeTab === 'complaints'}
            onClick={() => setActiveTab('complaints')}
            icon="🚩"
            text="Khiếu nại"
          />
        </div>

        {/* Main Content */}
        <div className="mt-6">
          <AnimatePresence mode="wait">
            {/* Staff Management Tab */}
            {activeTab === 'staff' && (
              <motion.div
                key="staff"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <FadeIn className="bg-white/95 backdrop-blur rounded-2xl shadow-xl border border-blue-100 p-8">
                  <h2 className="text-3xl font-bold text-blue-900 mb-8 flex items-center">
                    <span className="text-4xl mr-3">👥</span>
                    Quản lý nhân viên
                  </h2>

                  {/* Status Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <ScaleIn delay={0.1} className="bg-gradient-to-r from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-bold text-green-900">Nhân viên online</h3>
                        <span className="text-lg">👤</span>
                      </div>
                      <div className="text-3xl font-bold text-green-600">
                        {loading ? '...' : dashboardStats.onlineStaff}
                      </div>
                      <p className="text-green-700 mt-1">nhân viên</p>
                    </ScaleIn>

                    <ScaleIn delay={0.2} className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-bold text-blue-900">Yêu cầu đang xử lý</h3>
                        <span className="text-lg">🎫</span>
                      </div>
                      <div className="text-3xl font-bold text-blue-600">
                        {loading ? '...' : dashboardStats.activeTickets}
                      </div>
                      <p className="text-blue-700 mt-1">yêu cầu</p>
                    </ScaleIn>

                    <ScaleIn delay={0.3} className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-bold text-purple-900">Hiệu suất trung bình</h3>
                        <span className="text-lg">⭐</span>
                      </div>
                      <div className="text-3xl font-bold text-purple-600">
                        {loading ? '...' : `${dashboardStats.averagePerformance}/5`}
                      </div>
                      <p className="text-purple-700 mt-1">điểm</p>
                    </ScaleIn>
                  </div>

                  {/* Staff Table */}
                  <FadeIn className="bg-white rounded-xl border border-blue-100 overflow-hidden shadow-md">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-gradient-to-r from-blue-50 to-blue-100 text-blue-900">
                          <tr>
                            <th className="px-6 py-4 text-left text-sm font-semibold">Tên nhân viên</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold">Phòng ban</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold">Trạng thái</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold">Hiệu suất</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold">Thao tác</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-blue-50">
                          {loading ? (
                            <tr>
                              <td colSpan={5} className="px-6 py-4 text-center">
                                <div className="flex justify-center items-center">
                                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                                  <span className="ml-2 text-gray-500">Đang tải...</span>
                                </div>
                              </td>
                            </tr>
                          ) : staffList.length === 0 ? (
                            <tr>
                              <td colSpan={5} className="px-6 py-16 text-center">
                                <div className="text-4xl mb-2">👥</div>
                                <p className="text-gray-500">Không có nhân viên nào</p>
                              </td>
                            </tr>
                          ) : (
                            staffList.map((staff) => (
                              <tr key={staff.id} className="hover:bg-blue-50 transition-colors">
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className="font-semibold">{staff.full_name}</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                  {staff.department_name || '-'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className={`px-2 py-1 rounded-full text-xs ${staff.status === 'online' ? 'bg-green-100 text-green-800' :
                                    staff.status === 'busy' ? 'bg-yellow-100 text-yellow-800' :
                                      'bg-gray-100 text-gray-800'
                                    }`}>
                                    {staff.status === 'online' ? 'Online' :
                                      staff.status === 'busy' ? 'Đang bận' :
                                        'Offline'}
                                  </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="flex items-center">
                                    <span className="mr-2">{staff.performance !== undefined ? staff.performance : 0}/5</span>
                                    <div className="w-24 h-2 bg-gray-200 rounded-full">
                                      <div
                                        className="h-full bg-blue-500 rounded-full"
                                        style={{ width: `${(staff.performance || 0) * 20}%` }}
                                      ></div>
                                    </div>
                                  </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="flex space-x-2">
                                    <button
                                      disabled
                                      className="px-4 py-2 bg-gray-100 text-gray-400 text-xs rounded-lg border border-gray-200 cursor-not-allowed italic"
                                    >
                                      Tiếp tục phát triển
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </FadeIn>

                  {/* Quick Actions */}
                  <div className="flex justify-between items-center mt-6">
                    <button
                      onClick={() => loadDashboardData()}
                      className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors flex items-center space-x-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      <span>Làm mới</span>
                    </button>
                  </div>
                </FadeIn>
              </motion.div>
            )}

            {/* Schedule Management Tab */}
            {activeTab === 'schedule' && (
              <motion.div
                key="schedule"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <ScheduleManagement role="manager" />
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
                  <AIHelper role="manager" />
                </FadeIn>
              </motion.div>
            )}

            {/* Old Chat Tab - Removed */}
            {false && activeTab === 'chat' && (
              <motion.div
                key="chat"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <FadeIn className="bg-white/95 backdrop-blur rounded-2xl shadow-xl border border-blue-100 p-8 h-[600px]">
                  <div className="flex h-full">
                    {/* Chat Rooms List */}
                    <div className="w-1/3 border-r border-gray-200 pr-4">
                      <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-bold text-blue-900">Trò chuyện</h2>
                      </div>
                      <div className="space-y-2 overflow-y-auto h-[500px]">
                        {chatRooms.map(room => (
                          <div
                            key={room.id}
                            onClick={() => handleRoomSelect(room.id)}
                            className={`p-3 rounded-lg cursor-pointer flex items-center justify-between ${selectedRoom === room.id ? 'bg-blue-100' : 'hover:bg-gray-100'
                              }`}
                          >
                            <div className="flex items-center space-x-3">
                              <span className="text-xl">{room.type === 'direct' ? '👤' : '👥'}</span>
                              <div>
                                <h3 className="font-medium text-gray-900">{room.name}</h3>
                                <p className="text-xs text-gray-500">{room.lastMessage || 'Chưa có tin nhắn'}</p>
                              </div>
                            </div>
                            {room.unreadCount > 0 && (
                              <span className="bg-blue-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
                                {room.unreadCount}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Chat Area */}
                    <div className="w-2/3 pl-4 flex flex-col">
                      {selectedRoom ? (
                        <>
                          <div className="bg-gray-50 p-3 rounded-lg mb-4">
                            <h3 className="font-bold">
                              {chatRooms.find(r => r.id === selectedRoom)?.name || 'Trò chuyện'}
                            </h3>
                          </div>

                          <div className="flex-grow overflow-y-auto mb-4 space-y-4 p-2">
                            {messages.length === 0 ? (
                              <div className="text-center py-8 text-gray-500">
                                <div className="text-4xl mb-2">💬</div>
                                <p>Chưa có tin nhắn nào</p>
                              </div>
                            ) : (
                              messages.map((msg, index) => (
                                <div key={index} className={`flex ${msg.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}>
                                  <div className={`
                                    ${msg.sender_id === user?.id ?
                                      'bg-blue-500 text-white' :
                                      'bg-white text-gray-800 border border-gray-200'} 
                                    rounded-lg p-3 shadow-sm max-w-xs
                                    ${msg.isEmergency ? 'border-2 border-red-500' : ''}
                                  `}>
                                    {msg.isEmergency && (
                                      <div className="mb-2 text-xs font-bold text-red-600 bg-red-100 p-1 rounded">
                                        KHẨN CẤP: {msg.emergencyReason}
                                      </div>
                                    )}
                                    <p className="text-sm">{msg.content}</p>
                                    <span className={`text-xs ${msg.sender_id === user?.id ? 'text-blue-200' : 'text-gray-500'}`}>
                                      {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                  </div>
                                </div>
                              ))
                            )}
                          </div>

                          <div>
                            {emergencyMode && (
                              <div className="bg-red-100 p-2 rounded-lg mb-2">
                                <div className="flex items-center justify-between">
                                  <span className="text-sm font-bold text-red-700 flex items-center">
                                    <span className="mr-1">🚨</span> Chế độ khẩn cấp
                                  </span>
                                  <button
                                    onClick={() => setEmergencyMode(false)}
                                    className="text-red-700 hover:text-red-900"
                                  >
                                    ✕
                                  </button>
                                </div>
                                <input
                                  type="text"
                                  placeholder="Lý do khẩn cấp (tối đa 100 ký tự)"
                                  value={emergencyReason}
                                  onChange={(e) => setEmergencyReason(e.target.value.substring(0, 100))}
                                  className="w-full p-2 border border-red-300 rounded mt-1"
                                  maxLength={100}
                                />
                              </div>
                            )}

                            <div className="flex space-x-2">
                              <input
                                type="text"
                                placeholder="Nhập tin nhắn... (tối đa 200 ký tự)"
                                value={messageInput}
                                onChange={(e) => setMessageInput(e.target.value.substring(0, 200))}
                                className="flex-grow p-3 border border-gray-300 rounded-lg"
                                maxLength={200}
                                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                              />
                              <button
                                onClick={sendMessage}
                                className="px-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                              >
                                Gửi
                              </button>
                              <button
                                onClick={() => setEmergencyMode(!emergencyMode)}
                                className={`px-4 ${emergencyMode ? 'bg-red-500' : 'bg-gray-500'} text-white rounded-lg hover:opacity-90`}
                              >
                                🚨
                              </button>
                            </div>
                          </div>
                        </>
                      ) : (
                        <div className="flex items-center justify-center h-full text-gray-500">
                          <div className="text-center">
                            <div className="text-6xl mb-4">💬</div>
                            <p>Chọn một cuộc trò chuyện để bắt đầu</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </FadeIn>
              </motion.div>
            )}

            {/* Complaints Tab */}
            {activeTab === 'complaints' && (
              <motion.div
                key="complaints"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <FadeIn className="bg-white/95 backdrop-blur rounded-2xl shadow-xl border border-blue-100 p-8">
                  <h2 className="text-3xl font-bold text-blue-900 mb-8 flex items-center">
                    <span className="text-4xl mr-3">🚩</span>
                    Khiếu nại
                  </h2>

                  {/* Complaint Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <ScaleIn className="bg-gradient-to-r from-red-50 to-red-100 rounded-xl p-6 border border-red-200">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-bold text-red-900">Khiếu nại mới</h3>
                        <span className="text-lg">🔔</span>
                      </div>
                      <div className="text-3xl font-bold text-red-600">
                        {complaintStats.waiting}
                      </div>
                      <p className="text-red-700 mt-1">chưa xử lý</p>
                    </ScaleIn>

                    <ScaleIn className="bg-gradient-to-r from-emerald-50 to-emerald-100 rounded-xl p-6 border border-emerald-200">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-bold text-emerald-900">Đã giải quyết</h3>
                        <span className="text-lg">✅</span>
                      </div>
                      <div className="text-3xl font-bold text-emerald-600">
                        {complaintStats.completed}
                      </div>
                      <p className="text-emerald-700 mt-1">khiếu nại</p>
                    </ScaleIn>
                  </div>

                  {/* Complaints Table */}
                  <FadeIn className="bg-white rounded-xl border border-blue-100 overflow-hidden shadow-md">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-gradient-to-r from-blue-50 to-blue-100 text-blue-900">
                          <tr>
                            <th className="px-6 py-4 text-left text-sm font-semibold">Mã vé</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold">Khách hàng</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold">Tên dịch vụ</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold">Tên phòng ban</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold">Thao tác</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-blue-50">
                          {complaintsList.filter(complaint => complaint.status !== 'completed').length === 0 ? (
                            <tr>
                              <td colSpan={5} className="px-6 py-16 text-center">
                                <div className="text-4xl mb-2">🎉</div>
                                <p className="text-gray-500">Không có khiếu nại nào</p>
                              </td>
                            </tr>
                          ) : (
                            complaintsList.filter(complaint => complaint.status !== 'completed').map((complaint) => (
                              <tr key={complaint.id} className="hover:bg-blue-50 transition-colors">
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className="font-semibold text-blue-600">#{complaint.ticket_number || 'N/A'}</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div>
                                    <div className="font-semibold text-gray-900">{complaint.customer_name || 'N/A'}</div>
                                    {complaint.customer_phone && (
                                      <div className="text-sm text-gray-500">{complaint.customer_phone}</div>
                                    )}
                                  </div>
                                </td>
                                <td className="px-6 py-4">
                                  <div className="max-w-xs">
                                    <div className="font-medium text-gray-900">{complaint.service_name || 'N/A'}</div>
                                    <div className="text-sm text-gray-500 truncate">{complaint.content}</div>
                                  </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="font-medium text-gray-900">{complaint.department_name || 'N/A'}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="flex space-x-2">
                                    <button
                                      onClick={() => {
                                        console.log('Selected complaint data:', complaint); // Debug log
                                        setSelectedComplaint(complaint);
                                        setShowComplaintDetailModal(true);
                                      }}
                                      className="px-3 py-1 bg-indigo-500 text-white text-sm rounded hover:bg-indigo-600 transition-colors"
                                    >
                                      Xem chi tiết
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </FadeIn>
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

                  <div className="space-y-6 max-w-2xl">
                    {/* Language Settings */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Ngôn ngữ</h3>
                      <div className="flex items-center space-x-4">
                        <label className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="radio"
                            checked={managerSettings.language === 'vi'}
                            onChange={() => setManagerSettings({ ...managerSettings, language: 'vi' })}
                          />
                          <span>Tiếng Việt</span>
                        </label>
                        <label className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="radio"
                            checked={managerSettings.language === 'en'}
                            onChange={() => setManagerSettings({ ...managerSettings, language: 'en' })}
                          />
                          <span>Tiếng Anh</span>
                        </label>
                      </div>
                    </div>

                    {/* Notification Settings */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Thông báo</h3>
                      <div className="space-y-3">
                        <label className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={managerSettings.notifications}
                            onChange={() => setManagerSettings({ ...managerSettings, notifications: !managerSettings.notifications })}
                          />
                          <span>Bật thông báo đẩy</span>
                        </label>
                      </div>
                    </div>

                    {/* Report Export Settings */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Xuất báo cáo</h3>
                      <div className="flex items-center space-x-4">
                        <label className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="radio"
                            checked={managerSettings.reportFormat === 'pdf'}
                            onChange={() => setManagerSettings({ ...managerSettings, reportFormat: 'pdf' })}
                          />
                          <span>PDF</span>
                        </label>
                        <label className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="radio"
                            checked={managerSettings.reportFormat === 'excel'}
                            onChange={() => setManagerSettings({ ...managerSettings, reportFormat: 'excel' })}
                          />
                          <span>Excel</span>
                        </label>
                        <label className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="radio"
                            checked={managerSettings.reportFormat === 'json'}
                            onChange={() => setManagerSettings({ ...managerSettings, reportFormat: 'json' })}
                          />
                          <span>JSON</span>
                        </label>
                      </div>
                    </div>

                    {/* User Management */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Quản lý quyền</h3>
                      <button
                        className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                      >
                        Quản lý vai trò nhân viên
                      </button>
                    </div>

                    <div className="pt-4">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="px-6 py-2 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl font-medium shadow-lg hover:from-green-600 hover:to-green-700 transition-colors"
                      >
                        Lưu cài đặt
                      </motion.button>
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

      {/* Complaint Detail Modal */}
      {showComplaintDetailModal && selectedComplaint && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
          >
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-2xl font-bold mb-2">Chi tiết khiếu nại</h2>
                  <p className="text-indigo-100">Mã khiếu nại: #{selectedComplaint.id}</p>
                </div>
                <button
                  onClick={() => setShowComplaintDetailModal(false)}
                  className="text-white hover:text-gray-200 transition-colors"
                >
                  <span className="text-2xl">×</span>
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Customer Information */}
                <div className="bg-blue-50 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-blue-900 mb-4 flex items-center">
                    <span className="text-2xl mr-2">👤</span>
                    Thông tin khách hàng
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Tên khách hàng:</span>
                      <span className="font-semibold">{selectedComplaint.customer_name || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Số điện thoại:</span>
                      <span className="font-semibold">{selectedComplaint.customer_phone || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Mã vé:</span>
                      <span className="font-semibold text-blue-600">#{selectedComplaint.ticket_number || 'N/A'}</span>
                    </div>
                  </div>
                </div>

                {/* Service Information */}
                <div className="bg-green-50 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-green-900 mb-4 flex items-center">
                    <span className="text-2xl mr-2">🏢</span>
                    Thông tin dịch vụ
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Dịch vụ:</span>
                      <span className="font-semibold">{selectedComplaint.service_name || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Phòng ban:</span>
                      <span className="font-semibold">{selectedComplaint.department_name || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Nhân viên phục vụ:</span>
                      <span className="font-semibold text-green-600">{selectedComplaint.staff_name || 'N/A'}</span>
                    </div>
                    {selectedComplaint.staff_email && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Email nhân viên:</span>
                        <span className="font-semibold text-green-600">{selectedComplaint.staff_email}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Complaint Content */}
                <div className="lg:col-span-2 bg-orange-50 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-orange-900 mb-4 flex items-center">
                    <span className="text-2xl mr-2">📝</span>
                    Nội dung khiếu nại
                  </h3>
                  <div className="bg-white rounded-lg p-4 border border-orange-200">
                    <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                      {selectedComplaint.content || 'Không có nội dung'}
                    </p>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="lg:col-span-2 bg-gray-50 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Hành động
                  </h3>
                  <div className="mb-2 text-sm text-gray-600">
                    Status hiện tại: <span className="font-semibold">{selectedComplaint.status}</span>
                  </div>
                  {selectedComplaint.status === 'waiting' && (
                    <div className="flex flex-col sm:flex-row gap-3">
                      <button
                        onClick={handleResolveComplaint}
                        className="px-6 py-2 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg hover:from-green-600 hover:to-green-700 transition-all flex items-center justify-center space-x-2"
                      >
                        <span>✅</span>
                        <span>Giải quyết khiếu nại</span>
                      </button>
                      <button
                        onClick={() => {
                          if (selectedComplaint.staff_email) {
                            sendNotificationToStaff(selectedComplaint.staff_email, selectedComplaint);
                          }
                        }}
                        className="px-6 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all flex items-center justify-center space-x-2"
                        disabled={!selectedComplaint.staff_email}
                      >
                        <span>🔔</span>
                        <span>Gửi thông báo</span>
                      </button>
                    </div>
                  )}
                  {selectedComplaint.status !== 'waiting' && (
                    <div className="text-gray-600 bg-yellow-50 p-4 rounded-lg">
                      ⚠️ Các nút hành động chỉ hiển thị cho khiếu nại có trạng thái "waiting".
                      Khiếu nại này có status: <strong>{selectedComplaint.status}</strong>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Professional Notification Modal */}
      {showProfessionalNotificationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden border border-gray-100"
          >
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-amber-400 via-yellow-500 to-orange-500 text-white p-6">
              <div className="flex justify-between items-center">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                    <span className="text-2xl">🔔</span>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold">Trung tâm thông báo</h2>
                    <p className="text-amber-100">Quản lý thông báo hệ thống</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowProfessionalNotificationModal(false)}
                  className="text-white hover:text-amber-200 transition-colors p-2 rounded-full hover:bg-white hover:bg-opacity-20"
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
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start space-x-4">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-white text-lg">
                            {notification.type === 'complaint_notification' ? '🚩' :
                              notification.type === 'success' ? '✅' :
                                notification.type === 'warning' ? '⚠️' : '💡'}
                          </span>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold text-gray-800">
                              {notification.title || 'Thông báo hệ thống'}
                            </h4>
                            <span className="text-xs text-gray-500">
                              {notification.time || new Date().toLocaleTimeString('vi-VN')}
                            </span>
                          </div>
                          <p className="text-gray-700 leading-relaxed">
                            {notification.message}
                          </p>
                          {notification.action && (
                            <button className="mt-3 px-4 py-2 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition-colors">
                              {notification.action}
                            </button>
                          )}
                        </div>
                      </div>
                    </motion.div>
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

      {/* Custom Resolve Confirmation Modal */}
      {showResolveConfirmModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border border-gray-100"
          >
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-green-400 via-emerald-500 to-teal-500 text-white p-6">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                  <span className="text-2xl">✅</span>
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Xác nhận giải quyết</h2>
                  <p className="text-green-100">Hoàn thành khiếu nại</p>
                </div>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-green-100 to-emerald-200 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">🎯</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  Bạn có chắc chắn muốn giải quyết khiếu nại này?
                </h3>
                <p className="text-gray-600">
                  Khiếu nại #{selectedComplaint?.id} từ khách hàng <strong>{selectedComplaint?.customer_name}</strong> sẽ được đánh dấu là đã hoàn thành.
                </p>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <div className="flex items-start space-x-3">
                  <span className="text-yellow-500 text-lg">⚠️</span>
                  <div>
                    <h4 className="font-semibold text-yellow-800">Lưu ý quan trọng</h4>
                    <p className="text-yellow-700 text-sm">
                      Sau khi xác nhận, khiếu nại sẽ bị xóa khỏi danh sách chờ xử lý và không thể hoàn tác.
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowResolveConfirmModal(false)}
                  className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-colors"
                >
                  Hủy
                </button>
                <button
                  onClick={confirmResolveComplaint}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-medium hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg"
                >
                  Xác nhận giải quyết
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

export default ManagerDashboard;
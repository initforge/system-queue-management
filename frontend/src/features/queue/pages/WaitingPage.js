import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ApiService from '../../../shared/api';
import { useWebSocket } from '../../../shared/WebSocketContext';

const CustomerWaitingPage = () => {
  const { ticketId } = useParams();
  const navigate = useNavigate();
  
  const [ticket, setTicket] = useState(null);
  const [queueInfo, setQueueInfo] = useState({
    position: 0,
    peopleAhead: 0,
    estimatedWait: 0,
    currentServing: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [isNearTurn, setIsNearTurn] = useState(false);
  const [isRedirecting, setIsRedirecting] = useState(false);
  
  // WebSocket for real-time updates
  const { lastMessage, isConnected } = useWebSocket();

  // Load ticket info
  useEffect(() => {
    const fetchTicketInfo = async () => {
      try {
        setLoading(true);
        const response = await ApiService.getTicketStatus(ticketId);
        
        if (!response.success) {
          setError(response.message || 'Không thể tải thông tin vé');
          return;
        }
        
        // Set ticket data from API response
        setTicket({
          id: response.ticket_id,
          ticket_number: response.ticket_number,
          customer_name: response.customer_name,
          status: response.status,
          queue_position: response.queue_position,
          created_at: response.created_at,
          called_at: response.called_at
        });
        
        // Update queue info
        setQueueInfo({
          position: response.queue_position,
          peopleAhead: response.people_ahead,
          estimatedWait: response.estimated_wait || 0,
          currentServing: ''  // Will be added later
        });

        // Check if near turn (2 people or less ahead)
        setIsNearTurn(response.people_ahead <= 1);
        
        // Auto redirect if ticket was completed - go to review page
        if (response.status === 'completed') {
          navigate(`/review/${ticketId}`);
        }
        
      } catch (error) {
        console.error('Error loading ticket:', error);
        setError('Không thể tải thông tin vé. Vui lòng thử lại!');
      } finally {
        setLoading(false);
      }
    };

    if (ticketId) {
      fetchTicketInfo();
      // Check status every 5 seconds for faster response to completion
      const interval = setInterval(fetchTicketInfo, 5000);
      return () => clearInterval(interval);
    }
  }, [ticketId, navigate]);

  // Immediate redirect when status changes to completed
  useEffect(() => {
    if (ticket?.status === 'completed') {
      setIsRedirecting(true);
      // Hiển thị thông báo trong 500ms trước khi chuyển
      setTimeout(() => {
        navigate(`/review/${ticketId}`, { replace: true });
      }, 500);
    }
  }, [ticket?.status, ticketId, navigate]);

  // Timer for elapsed time - real-time counter with >10p limit
  useEffect(() => {
    if (ticket?.created_at) {
      const startTime = new Date(ticket.created_at);
      let intervalId;
      
      console.log('Timer started for ticket created at:', ticket.created_at);
      console.log('Parsed start time:', startTime);
      
      // Update function 
      const updateElapsed = () => {
        const now = new Date();
        const elapsedMs = now - startTime;
        const elapsedMinutes = Math.floor(elapsedMs / 60000);
        const elapsedSeconds = Math.floor((elapsedMs % 60000) / 1000);
        
        // Debug: log elapsed time calculation
        console.log('Elapsed MS:', elapsedMs, 'Minutes:', elapsedMinutes, 'Seconds:', elapsedSeconds);
        
        // Format display: show ">10p" if over 10 minutes and stop timer
        if (elapsedMinutes >= 10) {
          setTimeElapsed(">10p");
          if (intervalId) {
            clearInterval(intervalId);
            intervalId = null;
          }
          return;
        } else {
          setTimeElapsed(`${elapsedMinutes}:${elapsedSeconds.toString().padStart(2, '0')}`);
        }
      };
      
      updateElapsed(); // Initial update
      intervalId = setInterval(updateElapsed, 1000); // Update every second
      
      return () => {
        if (intervalId) {
          clearInterval(intervalId);
        }
      };
    }
  }, [ticket?.created_at]); // Only depend on created_at, not entire ticket object

  // Handle cancel ticket
  const handleCancelTicket = async () => {
    try {
      const response = await ApiService.cancelTicket(ticketId);
      if (response.success) {
        alert('Đã hủy vé thành công');
        navigate('/'); // Redirect to home
      } else {
        alert('Không thể hủy vé: ' + response.message);
      }
    } catch (error) {
      console.error('Cancel ticket error:', error);
      alert('Lỗi khi hủy vé. Vui lòng thử lại!');
    }
  };

  // Show cancel confirmation
  const showCancelConfirmation = () => {
    setShowCancelModal(true);
  };

  // Show called notification
  const showCalledNotification = useCallback(() => {
    // Play sound notification
    if ('Audio' in window) {
      const audio = new Audio('/notification.mp3');
      audio.play().catch(e => console.log('Audio play failed:', e));
    }
    
    // Show browser notification
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Đã đến lượt bạn!', {
        body: `Vui lòng đến quầy số ${ticket?.counter_number || 'được chỉ định'}`,
        icon: '/logo192.png'
      });
    }
    
    // Navigate to called page
    navigate(`/called/${ticketId}`);
  }, [ticket, navigate, ticketId]);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage && lastMessage.data) {
      try {
        // Check if data is valid before parsing
        if (typeof lastMessage.data === 'string' && lastMessage.data !== 'undefined') {
          const message = JSON.parse(lastMessage.data);
          
          if (message.type === 'queue_update' && message.ticket_id === ticketId) {
            setQueueInfo(prev => ({
              ...prev,
              position: message.position,
              peopleAhead: Math.max(0, message.position - 1),
              estimatedWait: message.estimated_wait
            }));
            
            setIsNearTurn(message.position <= 2);
          }
          
          if (message.type === 'ticket_called' && message.ticket_id === ticketId) {
            // Show notification and navigate to called screen
            showCalledNotification();
          }
          
          // Handle ticket completion
          if (message.type === 'ticket_completed' && message.ticket_id === ticketId) {
            // Update ticket status and trigger redirect
            setTicket(prev => ({ ...prev, status: 'completed' }));
            setIsRedirecting(true);
            setTimeout(() => {
              navigate(`/review/${ticketId}`, { replace: true });
            }, 1000);
          }
        }
        
      } catch (error) {
        console.error('Error parsing WebSocket message:', error, 'Data:', lastMessage.data);
      }
    }
  }, [lastMessage, ticketId, showCalledNotification]);

  // Request notification permission
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Đang tải thông tin...</p>
        </div>
      </div>
    );
  }

  // Show redirecting message when service is completed
  if (isRedirecting) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-20 h-20 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-green-600 mb-2">🎉 Dịch vụ hoàn thành!</h1>
          <p className="text-gray-600">Đang chuyển hướng đến trang đánh giá...</p>
          <div className="mt-4 w-32 h-1 bg-gray-200 rounded-full mx-auto overflow-hidden">
            <div className="h-full bg-gradient-to-r from-green-400 to-blue-500 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !ticket) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <svg className="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <h1 className="text-xl font-bold text-gray-900 mb-2">Có lỗi xảy ra</h1>
          <p className="text-gray-600 mb-4">{error || 'Không tìm thấy thông tin vé'}</p>
          <button
            onClick={() => navigate('/service-registration')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Tạo yêu cầu mới
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Đang chờ phục vụ</h1>
                <p className="text-sm text-gray-500">Vui lòng đợi đến lượt của bạn</p>
              </div>
            </div>
            
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {isConnected ? 'Đang kết nối' : 'Mất kết nối'}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Ticket Info Card */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <div className="text-center mb-6">
                <div className="text-6xl font-bold text-blue-600 mb-2">
                  #{ticket.ticket_number}
                </div>
                <p className="text-xl text-gray-900">{ticket.customer_name}</p>
                <p className="text-gray-600">{ticket.service_name}</p>
                <p className="text-sm text-gray-500">{ticket.department_name}</p>
              </div>

              {/* Queue Status */}
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <div className="text-3xl font-bold text-yellow-600 mb-1">{queueInfo.peopleAhead}</div>
                  <p className="text-sm text-yellow-700">Người đang chờ trước</p>
                </div>
                
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-3xl font-bold text-green-600 mb-1">{queueInfo.estimatedWait}</div>
                  <p className="text-sm text-green-700">Phút dự kiến chờ</p>
                </div>
              </div>

              {/* Near Turn Alert */}
              {isNearTurn && (
                <div className="bg-orange-50 border-l-4 border-orange-400 p-4 mb-6">
                  <div className="flex items-center">
                    <svg className="w-6 h-6 text-orange-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    <div>
                      <h3 className="font-medium text-orange-800">Sắp đến lượt bạn!</h3>
                      <p className="text-sm text-orange-700">Vui lòng chuẩn bị giấy tờ và chờ thông báo</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Current Serving */}
              {queueInfo.currentServing && (
                <div className="bg-green-50 p-4 rounded-lg mb-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-green-600">Đang phục vụ</p>
                      <p className="text-lg font-semibold text-green-700">#{queueInfo.currentServing}</p>
                    </div>
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  </div>
                </div>
              )}

              {/* Waiting Time */}
              <div className="text-center text-gray-600">
                <p className="text-sm">Thời gian đã chờ: <span className="font-medium">{timeElapsed} phút</span></p>
                <p className="text-xs mt-1">Cập nhật lúc: {new Date().toLocaleTimeString('vi-VN')}</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Tùy chọn</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <button
                  onClick={() => navigate('/service-registration')}
                  className="flex items-center justify-center p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-all duration-200"
                >
                  <svg className="w-6 h-6 text-gray-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  <div className="text-left">
                    <p className="font-medium text-gray-900">Dịch vụ khác</p>
                    <p className="text-sm text-gray-600">Tạo yêu cầu mới</p>
                  </div>
                </button>

                <button
                  onClick={showCancelConfirmation}
                  className="flex items-center justify-center p-4 border-2 border-gray-200 rounded-lg hover:border-red-500 hover:bg-red-50 transition-all duration-200"
                >
                  <svg className="w-6 h-6 text-gray-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  <div className="text-left">
                    <p className="font-medium text-gray-900">Hủy dịch vụ</p>
                    <p className="text-sm text-gray-600">Xóa khỏi hàng chờ</p>
                  </div>
                </button>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border p-6 sticky top-8">
              <h3 className="font-semibold text-gray-900 mb-4">Thông tin hữu ích</h3>
              
              <div className="space-y-4">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">📋 Giấy tờ cần thiết</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• CMND/CCCD bản gốc</li>
                    <li>• Giấy tờ liên quan đến dịch vụ</li>
                    <li>• Số điện thoại đã đăng ký</li>
                  </ul>
                </div>

                <div className="p-3 bg-green-50 rounded-lg">
                  <h4 className="font-medium text-green-900 mb-2">⏰ Thời gian làm việc</h4>
                  <div className="text-sm text-green-800 space-y-1">
                    <p>Thứ 2 - Thứ 6: 8:00 - 17:00</p>
                    <p>Thứ 7: 8:00 - 12:00</p>
                    <p>Chủ nhật: Nghỉ</p>
                  </div>
                </div>

                <div className="p-3 bg-yellow-50 rounded-lg">
                  <h4 className="font-medium text-yellow-900 mb-2">💡 Lưu ý quan trọng</h4>
                  <ul className="text-sm text-yellow-800 space-y-1">
                    <li>• Vui lòng có mặt khi được gọi</li>
                    <li>• Quá 5 phút sẽ bị hủy tự động</li>
                    <li>• Bật thông báo để không bỏ lỡ</li>
                  </ul>
                </div>

                <div className="p-3 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">📞 Liên hệ hỗ trợ</h4>
                  <div className="text-sm text-gray-700">
                    <p>Hotline: 1900-xxxx</p>
                    <p>Email: support@company.com</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Cancel/Postpone Modal */}
      {showCancelModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Xác nhận hủy dịch vụ</h3>
            
            <div className="mb-6">
              <div className="flex items-center p-4 border border-red-300 rounded-lg bg-red-50">
                <svg className="w-8 h-8 text-red-600 mr-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <p className="font-medium text-red-900">Bạn có chắc chắn muốn hủy dịch vụ?</p>
                  <p className="text-sm text-red-700 mt-1">Ticket #{ticket?.ticket_number} sẽ bị xóa hoàn toàn khỏi hệ thống và bạn sẽ cần đăng ký lại dịch vụ nếu muốn.</p>
                </div>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => setShowCancelModal(false)}
                className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Không, giữ lại
              </button>
              <button
                onClick={() => {
                  setShowCancelModal(false);
                  handleCancelTicket();
                }}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Có, hủy dịch vụ
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomerWaitingPage;
import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import scheduleAPI from '../../shared/services/api/schedule';
import { useAuth } from '../../shared/AuthContext';

const ExpandablePanel = ({ icon, title, children, isExpanded, onToggle }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden"
    >
      {/* Panel Header */}
      <motion.button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors group"
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <div className="flex items-center space-x-3">
          <div className="text-xl group-hover:scale-110 transition-transform">{icon}</div>
          <div className="text-left">
            <h3 className="text-base font-semibold text-gray-900">{title}</h3>
          </div>
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="text-gray-400 group-hover:text-gray-600"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </motion.div>
      </motion.button>

      {/* Panel Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden border-t border-gray-100"
          >
            <div className="p-4">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};


// Leave Request Management Panel
const LeaveRequestPanel = () => {
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadLeaveRequests = useCallback(async () => {
    try {
      setLoading(true);
      const response = await scheduleAPI.getLeaveRequests('pending');
      const requests = Array.isArray(response) ? response : [];
      setLeaveRequests(requests);
    } catch (error) {
      console.error('Error loading leave requests:', error);
      setLeaveRequests([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadLeaveRequests();
    const interval = setInterval(loadLeaveRequests, 30000);
    return () => clearInterval(interval);
  }, [loadLeaveRequests]);

  const [showModal, setShowModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [rejectReason, setRejectReason] = useState('');

  const handleApprove = async (id) => {
    try {
      await scheduleAPI.updateLeaveRequest(id, { status: 'approved' });
      setLeaveRequests(prev => prev.filter(req => req.id !== id));
      await loadLeaveRequests();
    } catch (error) {
      console.error('Error approving leave request:', error);
      alert('Lỗi khi duyệt đơn nghỉ phép. Vui lòng thử lại.');
    }
  };

  const handleReject = (request) => {
    setSelectedRequest(request);
    setShowModal(true);
  };

  const confirmReject = async () => {
    if (selectedRequest && rejectReason.trim()) {
      try {
        await scheduleAPI.updateLeaveRequest(selectedRequest.id, {
          status: 'rejected',
          rejection_reason: rejectReason
        });
        setLeaveRequests(prev => prev.filter(req => req.id !== selectedRequest.id));
        await loadLeaveRequests();
        setShowModal(false);
        setSelectedRequest(null);
        setRejectReason('');
      } catch (error) {
        console.error('Error rejecting leave request:', error);
        alert('Lỗi khi từ chối đơn nghỉ phép. Vui lòng thử lại.');
      }
    }
  };

  const pendingRequests = leaveRequests.filter(req => req.status === 'pending');

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="font-semibold text-gray-900">Đơn xin nghỉ phép</h4>
        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
          {pendingRequests.length} chờ duyệt
        </span>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
          <p className="text-gray-500 text-sm">Đang tải...</p>
        </div>
      ) : pendingRequests.length > 0 ? (
        <div className="space-y-3">
          {pendingRequests.map((request) => (
            <motion.div
              key={request.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-4 bg-gray-50 rounded-xl"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="w-10 h-10 bg-gradient-to-r from-purple-400 to-purple-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm">👤</span>
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">
                        {request.staff?.full_name || request.staff_name || 'Nhân viên'}
                      </div>
                      <div className="text-sm text-gray-500">
                        Nghỉ ngày: {new Date(request.leave_date).toLocaleDateString('vi-VN')}
                      </div>
                    </div>
                  </div>
                  <div className="ml-13">
                    <div className="text-sm text-gray-700 mb-1">
                      <strong>Loại:</strong> {request.leave_type === 'sick' ? 'Nghỉ ốm' :
                        request.leave_type === 'personal' ? 'Việc cá nhân' :
                          request.leave_type === 'vacation' ? 'Nghỉ phép' :
                            request.leave_type === 'emergency' ? 'Khẩn cấp' : request.leave_type}
                    </div>
                    <div className="text-sm text-gray-700 mb-1">
                      <strong>Lý do:</strong> {request.reason}
                    </div>
                    <div className="text-xs text-gray-500">
                      Gửi lúc: {new Date(request.submitted_at).toLocaleString('vi-VN')}
                    </div>
                  </div>
                </div>
                <div className="flex flex-col space-y-2">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleApprove(request.id)}
                    className="px-4 py-2 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 transition-colors text-sm"
                  >
                    ✅ Duyệt
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleReject(request)}
                    className="px-4 py-2 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors text-sm"
                  >
                    ❌ Từ chối
                  </motion.button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">📝</div>
          <p>Không có đơn xin nghỉ nào cần duyệt</p>
        </div>
      )}

      {/* Reject Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-6 max-w-md w-full mx-4"
            >
              <h3 className="text-lg font-semibold mb-4">Từ chối đơn xin nghỉ</h3>
              <p className="text-gray-600 mb-4">
                Bạn có chắc muốn từ chối đơn xin nghỉ của <strong>{selectedRequest?.staff?.full_name || selectedRequest?.staff_name || 'nhân viên'}</strong>?
              </p>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Nhập lý do từ chối..."
                className="w-full p-3 border border-gray-300 rounded-xl resize-none"
                rows={3}
              />
              <div className="flex space-x-3 mt-4">
                <button
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-xl font-medium hover:bg-gray-300 transition-colors"
                >
                  Hủy
                </button>
                <button
                  onClick={confirmReject}
                  className="flex-1 px-4 py-2 bg-red-500 text-white rounded-xl font-medium hover:bg-red-600 transition-colors"
                >
                  Xác nhận từ chối
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Staff Leave Request Form Panel
const StaffLeaveRequestPanel = () => {
  const [leaveForm, setLeaveForm] = useState({
    date: '',
    reason: '',
    type: 'sick' // sick, personal, vacation
  });
  const [myRequests, setMyRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const loadMyRequests = useCallback(async () => {
    try {
      setLoading(true);
      const response = await scheduleAPI.getLeaveRequests();
      const requests = Array.isArray(response) ? response : [];
      setMyRequests(requests);
    } catch (error) {
      console.error('Error loading leave requests:', error);
      setMyRequests([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMyRequests();
  }, [loadMyRequests]);

  const submitLeaveRequest = async () => {
    if (!leaveForm.date || !leaveForm.reason.trim()) {
      alert('Vui lòng điền đầy đủ thông tin!');
      return;
    }

    try {
      setSubmitting(true);
      const leaveDate = leaveForm.date; // Format: YYYY-MM-DD
      await scheduleAPI.createLeaveRequest({
        leave_date: leaveDate,
        leave_type: leaveForm.type,
        reason: leaveForm.reason
      });

      setLeaveForm({ date: '', reason: '', type: 'sick' });
      alert('Đơn xin nghỉ đã được gửi thành công!');
      await loadMyRequests();
    } catch (error) {
      console.error('Error submitting leave request:', error);
      alert('Lỗi khi gửi đơn xin nghỉ. Vui lòng thử lại.');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'approved': return 'Đã duyệt';
      case 'rejected': return 'Bị từ chối';
      default: return 'Chờ duyệt';
    }
  };

  return (
    <div className="space-y-6">
      {/* Request Form */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-xl border border-purple-200">
        <h4 className="font-semibold text-gray-900 mb-4">Tạo đơn xin nghỉ mới</h4>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Ngày nghỉ</label>
            <input
              type="date"
              value={leaveForm.date}
              onChange={(e) => setLeaveForm(prev => ({ ...prev, date: e.target.value }))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Loại nghỉ</label>
            <select
              value={leaveForm.type}
              onChange={(e) => setLeaveForm(prev => ({ ...prev, type: e.target.value }))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            >
              <option value="sick">Nghỉ ốm</option>
              <option value="personal">Việc cá nhân</option>
              <option value="vacation">Nghỉ phép</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Lý do</label>
            <textarea
              value={leaveForm.reason}
              onChange={(e) => setLeaveForm(prev => ({ ...prev, reason: e.target.value }))}
              placeholder="Nhập lý do xin nghỉ..."
              className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              rows={3}
            />
          </div>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={submitLeaveRequest}
            disabled={submitting}
            className={`w-full px-4 py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl font-medium hover:from-purple-600 hover:to-purple-700 transition-colors ${submitting ? 'opacity-50 cursor-not-allowed' : ''
              }`}
          >
            {submitting ? 'Đang gửi...' : '📝 Gửi đơn xin nghỉ'}
          </motion.button>
        </div>
      </div>

      {/* My Requests History */}
      <div>
        <h4 className="font-semibold text-gray-900 mb-4">Lịch sử đơn xin nghỉ</h4>
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto mb-2"></div>
            <p className="text-gray-500 text-sm">Đang tải...</p>
          </div>
        ) : myRequests.length > 0 ? (
          <div className="space-y-3">
            {myRequests.map((request) => (
              <motion.div
                key={request.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 bg-gray-50 rounded-xl border border-gray-200"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-lg">📅</span>
                      <div>
                        <div className="font-medium text-gray-900">
                          Nghỉ ngày: {new Date(request.leave_date).toLocaleDateString('vi-VN')}
                        </div>
                        <div className="text-sm text-gray-500">
                          Gửi lúc: {new Date(request.submitted_at).toLocaleString('vi-VN')}
                        </div>
                      </div>
                    </div>
                    <div className="text-sm text-gray-700 mb-1">
                      <strong>Loại:</strong> {request.leave_type === 'sick' ? 'Nghỉ ốm' :
                        request.leave_type === 'personal' ? 'Việc cá nhân' :
                          request.leave_type === 'vacation' ? 'Nghỉ phép' :
                            request.leave_type === 'emergency' ? 'Khẩn cấp' : request.leave_type}
                    </div>
                    <div className="text-sm text-gray-700">
                      <strong>Lý do:</strong> {request.reason}
                    </div>
                    {request.rejection_reason && (
                      <div className="text-sm text-red-600 mt-1">
                        <strong>Lý do từ chối:</strong> {request.rejection_reason}
                      </div>
                    )}
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(request.status)}`}>
                    {getStatusText(request.status)}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">📝</div>
            <p>Chưa có đơn xin nghỉ nào</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Staff Shift Exchange Panel
const StaffShiftExchangePanel = () => {
  const [exchangeRequests, setExchangeRequests] = useState([
    {
      id: 1,
      fromShift: 'Ca Sáng - Thứ 2 (7:00-15:00)',
      toShift: 'Ca Chiều - Thứ 4 (15:00-23:00)',
      withStaff: 'Trần Thị B',
      status: 'pending',
      reason: 'Có việc đột xuất buổi sáng',
      createdAt: '20/10/2025 14:30'
    }
  ]);

  const availableExchanges = [
    { staff: 'Trần Thị B', shift: 'Ca Chiều - Thứ 4', time: '15:00-23:00' },
    { staff: 'Lê Văn C', shift: 'Ca Sáng - Thứ 6', time: '7:00-15:00' },
  ];

  const requestShiftExchange = (targetStaff, targetShift) => {
    const reason = prompt('Nhập lý do đổi ca:');
    if (!reason) return;

    const newRequest = {
      id: Date.now(),
      fromShift: 'Ca Sáng - Thứ 2 (7:00-15:00)', // Current user's shift
      toShift: targetShift,
      withStaff: targetStaff,
      status: 'pending',
      reason,
      createdAt: new Date().toLocaleString('vi-VN')
    };

    setExchangeRequests(prev => [newRequest, ...prev]);
    alert('Yêu cầu đổi ca đã được gửi!');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'approved': return 'Đã duyệt';
      case 'rejected': return 'Bị từ chối';
      default: return 'Chờ xác nhận';
    }
  };

  return (
    <div className="space-y-6">
      {/* Available Exchanges */}
      <div>
        <h4 className="font-semibold text-gray-900 mb-4">Có thể đổi ca với</h4>
        {availableExchanges.length > 0 ? (
          <div className="space-y-3">
            {availableExchanges.map((exchange, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center justify-between p-4 bg-gradient-to-r from-orange-50 to-yellow-50 rounded-xl border border-orange-200"
              >
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-gradient-to-r from-orange-400 to-orange-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">👤</span>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{exchange.staff}</div>
                    <div className="text-sm text-gray-600">{exchange.shift} ({exchange.time})</div>
                  </div>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => requestShiftExchange(exchange.staff, exchange.shift)}
                  className="px-4 py-2 bg-orange-500 text-white rounded-lg font-medium hover:bg-orange-600 transition-colors"
                >
                  🔄 Đổi ca
                </motion.button>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🔄</div>
            <p>Không có ca nào có thể đổi</p>
          </div>
        )}
      </div>

      {/* Exchange History */}
      <div>
        <h4 className="font-semibold text-gray-900 mb-4">Lịch sử đổi ca</h4>
        {exchangeRequests.length > 0 ? (
          <div className="space-y-3">
            {exchangeRequests.map((request) => (
              <motion.div
                key={request.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 bg-gray-50 rounded-xl border border-gray-200"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 mb-1">
                      Đổi với {request.withStaff}
                    </div>
                    <div className="text-sm text-gray-600">
                      <div>Từ: {request.fromShift}</div>
                      <div>Sang: {request.toShift}</div>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(request.status)}`}>
                    {getStatusText(request.status)}
                  </span>
                </div>
                <div className="text-sm text-gray-700">
                  <strong>Lý do:</strong> {request.reason}
                </div>
                <div className="text-xs text-gray-500 mt-2">
                  Gửi lúc: {request.createdAt}
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🔄</div>
            <p>Chưa có yêu cầu đổi ca nào</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Staff Statistics Panel
const StaffStatisticsPanel = ({ staffId }) => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    on_time_count: 0,
    late_count: 0,
    leave_count: 0
  });
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('3months'); // 'month', '3months', 'all'

  const loadStatistics = useCallback(async () => {
    try {
      setLoading(true);
      const targetStaffId = staffId || user?.id;
      if (!targetStaffId) return;

      let startDate = null;
      let endDate = null;
      const today = new Date();

      switch (dateRange) {
        case 'month':
          startDate = new Date(today.getFullYear(), today.getMonth(), 1);
          endDate = today;
          break;
        case '3months':
          startDate = new Date(today);
          startDate.setMonth(today.getMonth() - 3);
          endDate = today;
          break;
        case 'all':
        default:
          startDate = null;
          endDate = null;
          break;
      }

      const response = await scheduleAPI.getStaffStatistics(
        targetStaffId,
        startDate ? startDate.toISOString().split('T')[0] : null,
        endDate ? endDate.toISOString().split('T')[0] : null
      );
      setStats(response);
    } catch (error) {
      console.error('Error loading staff statistics:', error);
      setStats({ on_time_count: 0, late_count: 0, leave_count: 0 });
    } finally {
      setLoading(false);
    }
  }, [staffId, user?.id, dateRange]);

  useEffect(() => {
    loadStatistics();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadStatistics, 30000);
    return () => clearInterval(interval);
  }, [loadStatistics]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h4 className="font-semibold text-gray-900">Thống kê cá nhân</h4>
        <select
          value={dateRange}
          onChange={(e) => setDateRange(e.target.value)}
          className="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="month">Tháng này</option>
          <option value="3months">3 tháng gần đây</option>
          <option value="all">Tất cả</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
          <p className="text-gray-500 text-sm">Đang tải...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {/* On-time Count */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-green-700 font-medium mb-1">Làm việc đúng giờ</div>
                <div className="text-3xl font-bold text-green-900">{stats.on_time_count}</div>
                <div className="text-xs text-green-600 mt-1">lần</div>
              </div>
              <div className="text-4xl">✅</div>
            </div>
          </motion.div>

          {/* Late Count */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="p-6 bg-gradient-to-r from-orange-50 to-red-50 rounded-xl border border-orange-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-orange-700 font-medium mb-1">Đi trễ</div>
                <div className="text-3xl font-bold text-orange-900">{stats.late_count}</div>
                <div className="text-xs text-orange-600 mt-1">lần</div>
              </div>
              <div className="text-4xl">⏰</div>
            </div>
          </motion.div>

          {/* Leave Count */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-blue-700 font-medium mb-1">Xin nghỉ</div>
                <div className="text-3xl font-bold text-blue-900">{stats.leave_count}</div>
                <div className="text-xs text-blue-600 mt-1">lần</div>
              </div>
              <div className="text-4xl">📝</div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

// Manager Statistics Panel
const ManagerStatisticsPanel = () => {
  const [stats, setStats] = useState({
    most_on_time: { staff_name: '', count: 0 },
    most_late: { staff_name: '', count: 0 },
    most_leave: { staff_name: '', count: 0 }
  });
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('3months');

  const loadStatistics = useCallback(async () => {
    try {
      setLoading(true);
      let startDate = null;
      let endDate = null;
      const today = new Date();

      switch (dateRange) {
        case 'month':
          startDate = new Date(today.getFullYear(), today.getMonth(), 1);
          endDate = today;
          break;
        case '3months':
          startDate = new Date(today);
          startDate.setMonth(today.getMonth() - 3);
          endDate = today;
          break;
        case 'all':
        default:
          startDate = null;
          endDate = null;
          break;
      }

      const response = await scheduleAPI.getDepartmentStatistics(
        startDate ? startDate.toISOString().split('T')[0] : null,
        endDate ? endDate.toISOString().split('T')[0] : null
      );
      setStats({
        most_on_time: response.most_on_time || { staff_name: 'Chưa có dữ liệu', count: 0 },
        most_late: response.most_late || { staff_name: 'Chưa có dữ liệu', count: 0 },
        most_leave: response.most_leave || { staff_name: 'Chưa có dữ liệu', count: 0 }
      });
    } catch (error) {
      console.error('Error loading department statistics:', error);
      setStats({
        most_on_time: { staff_name: 'Lỗi tải dữ liệu', count: 0 },
        most_late: { staff_name: 'Lỗi tải dữ liệu', count: 0 },
        most_leave: { staff_name: 'Lỗi tải dữ liệu', count: 0 }
      });
    } finally {
      setLoading(false);
    }
  }, [dateRange]);

  useEffect(() => {
    loadStatistics();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadStatistics, 30000);
    return () => clearInterval(interval);
  }, [loadStatistics]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h4 className="font-semibold text-gray-900">Thống kê phòng ban</h4>
        <select
          value={dateRange}
          onChange={(e) => setDateRange(e.target.value)}
          className="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="month">Tháng này</option>
          <option value="3months">3 tháng gần đây</option>
          <option value="all">Tất cả</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
          <p className="text-gray-500 text-sm">Đang tải...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Most On-time */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="text-sm text-green-700 font-medium mb-1">Nhân viên đi làm đúng giờ nhất</div>
                <div className="text-lg font-bold text-green-900">{stats.most_on_time.staff_name || 'Chưa có dữ liệu'}</div>
                <div className="text-xs text-green-600 mt-1">{stats.most_on_time.count} lần</div>
              </div>
              <div className="text-3xl">🏆</div>
            </div>
          </motion.div>

          {/* Most Late */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-xl border border-orange-200"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="text-sm text-orange-700 font-medium mb-1">Nhân viên đi trễ nhiều nhất</div>
                <div className="text-lg font-bold text-orange-900">{stats.most_late.staff_name || 'Chưa có dữ liệu'}</div>
                <div className="text-xs text-orange-600 mt-1">{stats.most_late.count} lần</div>
              </div>
              <div className="text-3xl">⚠️</div>
            </div>
          </motion.div>

          {/* Most Leave */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="text-sm text-blue-700 font-medium mb-1">Nhân viên xin nghỉ nhiều nhất</div>
                <div className="text-lg font-bold text-blue-900">{stats.most_leave.staff_name || 'Chưa có dữ liệu'}</div>
                <div className="text-xs text-blue-600 mt-1">{stats.most_leave.count} lần</div>
              </div>
              <div className="text-3xl">📋</div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export {
  ExpandablePanel,
  LeaveRequestPanel,
  StaffLeaveRequestPanel,
  StaffStatisticsPanel,
  ManagerStatisticsPanel,
  StaffShiftExchangePanel
};
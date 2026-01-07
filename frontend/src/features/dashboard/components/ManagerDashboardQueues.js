import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../../../shared/WebSocketContext';
import { ApiClient } from '../../../shared/services/api/client';

const api = new ApiClient();

const DepartmentTicketsMonitor = ({ department, onRefresh }) => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all');
  const { isConnected, socket } = useWebSocket();

  useEffect(() => {
    loadTickets();

    // Set up real-time updates via WebSocket
    if (isConnected && socket) {
      socket.on('ticket_update', handleTicketUpdate);

      return () => {
        socket.off('ticket_update', handleTicketUpdate);
      };
    }
  }, [department.id, isConnected]);

  const handleTicketUpdate = (data) => {
    if (data.ticket && data.ticket.department_id === department.id) {
      if (data.type === 'new_ticket') {
        setTickets(prev => [data.ticket, ...prev]);
      } else if (data.type === 'update_ticket') {
        setTickets(prev => prev.map(t => t.id === data.ticket.id ? data.ticket : t));
      } else if (data.type === 'remove_ticket') {
        setTickets(prev => prev.filter(t => t.id !== data.ticketId));
      }
    }
  };

  const loadTickets = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/tickets/department/${department.id}`);
      setTickets(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error(`Error loading tickets for department ${department.id}:`, error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'WAITING': return 'bg-blue-100 text-blue-800';
      case 'CALLED': return 'bg-yellow-100 text-yellow-800';
      case 'SERVING': return 'bg-green-100 text-green-800';
      case 'COMPLETED': return 'bg-gray-100 text-gray-800';
      case 'CANCELLED': return 'bg-red-100 text-red-800';
      case 'NO_SHOW': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'WAITING': return 'Đang chờ';
      case 'CALLED': return 'Đã gọi';
      case 'SERVING': return 'Đang phục vụ';
      case 'COMPLETED': return 'Hoàn thành';
      case 'CANCELLED': return 'Đã hủy';
      case 'NO_SHOW': return 'Không đến';
      default: return status;
    }
  };

  const filteredTickets = filter === 'all'
    ? tickets
    : tickets.filter(ticket => ticket.status === filter);

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">{department.name}</h3>
          <button
            onClick={loadTickets}
            className="p-1 text-gray-500 hover:text-gray-700"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>

        <div className="flex space-x-2 mt-3 overflow-x-auto pb-1">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1 rounded-full text-xs whitespace-nowrap ${filter === 'all' ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-800'
              }`}
          >
            Tất cả
          </button>
          <button
            onClick={() => setFilter('WAITING')}
            className={`px-3 py-1 rounded-full text-xs whitespace-nowrap ${filter === 'WAITING' ? 'bg-blue-500 text-white' : 'bg-blue-100 text-blue-800'
              }`}
          >
            Đang chờ
          </button>
          <button
            onClick={() => setFilter('CALLED')}
            className={`px-3 py-1 rounded-full text-xs whitespace-nowrap ${filter === 'CALLED' ? 'bg-yellow-500 text-white' : 'bg-yellow-100 text-yellow-800'
              }`}
          >
            Đã gọi
          </button>
          <button
            onClick={() => setFilter('SERVING')}
            className={`px-3 py-1 rounded-full text-xs whitespace-nowrap ${filter === 'SERVING' ? 'bg-green-500 text-white' : 'bg-green-100 text-green-800'
              }`}
          >
            Đang phục vụ
          </button>
          <button
            onClick={() => setFilter('COMPLETED')}
            className={`px-3 py-1 rounded-full text-xs whitespace-nowrap ${filter === 'COMPLETED' ? 'bg-gray-500 text-white' : 'bg-gray-100 text-gray-800'
              }`}
          >
            Hoàn thành
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Số vé</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Khách hàng</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng thái</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Thời gian</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nhân viên</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">Đang tải...</td>
              </tr>
            ) : filteredTickets.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                  Không có vé nào{filter !== 'all' ? ` ở trạng thái "${getStatusLabel(filter)}"` : ''}
                </td>
              </tr>
            ) : (
              filteredTickets.map(ticket => (
                <tr key={ticket.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-blue-700">{ticket.ticket_number}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{ticket.customer_name}</div>
                    {ticket.customer_phone && (
                      <div className="text-sm text-gray-500">{ticket.customer_phone}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(ticket.status)}`}>
                      {getStatusLabel(ticket.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div>
                      Tạo: {new Date(ticket.created_at).toLocaleTimeString('vi-VN')}
                    </div>
                    {ticket.called_at && (
                      <div>
                        Gọi: {new Date(ticket.called_at).toLocaleTimeString('vi-VN')}
                      </div>
                    )}
                    {ticket.completed_at && (
                      <div>
                        Hoàn thành: {new Date(ticket.completed_at).toLocaleTimeString('vi-VN')}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {ticket.staff ? (
                      <div className="text-sm font-medium text-gray-900">{ticket.staff.full_name || ticket.staff.email}</div>
                    ) : (
                      <span className="text-sm text-gray-500">-</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const ManagerDashboardQueues = () => {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadDepartments = async () => {
      setLoading(true);
      try {
        const response = await api.get('/departments');
        setDepartments(Array.isArray(response.data) ? response.data : []);
      } catch (error) {
        console.error('Error loading departments:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDepartments();
  }, []);

  return (
    <div className="space-y-6">
      {loading ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-500">Đang tải dữ liệu...</p>
        </div>
      ) : departments.length === 0 ? (
        <div className="bg-white rounded-xl p-8 text-center">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h14a2 2 0 012 2v14a2 2 0 01-2 2z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01M12 3a9 9 0 100 18 9 9 0 000-18z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Không có phòng ban</h3>
          <p className="text-gray-500">
            Không tìm thấy phòng ban nào trong hệ thống. Vui lòng tạo phòng ban trước.
          </p>
        </div>
      ) : (
        departments.map(department => (
          <DepartmentTicketsMonitor
            key={department.id}
            department={department}
          />
        ))
      )}
    </div>
  );
};

export default ManagerDashboardQueues;
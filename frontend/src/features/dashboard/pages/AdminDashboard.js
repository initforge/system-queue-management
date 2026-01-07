import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import DashboardLayout from '../../../shared/components/DashboardLayout';
import { useAdminDashboard } from '../../../shared/api';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('system');
  const {
    departments,
    users,
    systemStats,
    loading,
    error,
    fetchDepartments,
    fetchUsers,
    fetchSystemStats
  } = useAdminDashboard();

  // WebSocket data placeholders (to be integrated later if needed)
  const wsConnected = false;
  const ticketCount = 0;
  const staffActivity = [];
  const criticalAlerts = [];

  const requestSystemStats = React.useCallback(() => {
    // Implementation for requesting live stats via WS
  }, []);

  const requestStaffActivity = React.useCallback(() => {
    // Implementation for requesting staff logs via WS
  }, []);

  useEffect(() => {
    // Fetch initial data based on active tab
    if (activeTab === 'system') {
      fetchSystemStats();
      requestSystemStats();
    } else if (activeTab === 'users') {
      fetchUsers();
    } else if (activeTab === 'departments') {
      fetchDepartments();
    }
  }, [activeTab, fetchSystemStats, fetchUsers, fetchDepartments, requestSystemStats]);

  // Poll for staff activity when system tab is active
  useEffect(() => {
    if (activeTab === 'system' && wsConnected) {
      const intervalId = setInterval(() => {
        requestStaffActivity();
      }, 30000); // Request staff activity every 30 seconds

      return () => clearInterval(intervalId);
    }
  }, [activeTab, wsConnected, requestStaffActivity]);

  return (
    <DashboardLayout>
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">
          Quản trị hệ thống
        </h1>

        {/* Tab navigation */}
        <div className="mb-6 border-b border-gray-200">
          <ul className="flex flex-wrap -mb-px text-sm font-medium text-center">
            <li className="mr-2">
              <button
                className={`inline-block p-4 rounded-t-lg ${activeTab === 'system'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-600 hover:border-gray-300'
                  }`}
                onClick={() => setActiveTab('system')}
              >
                Thống kê hệ thống
              </button>
            </li>
            <li className="mr-2">
              <button
                className={`inline-block p-4 rounded-t-lg ${activeTab === 'users'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-600 hover:border-gray-300'
                  }`}
                onClick={() => setActiveTab('users')}
              >
                Quản lý người dùng
              </button>
            </li>
            <li className="mr-2">
              <button
                className={`inline-block p-4 rounded-t-lg ${activeTab === 'departments'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-600 hover:border-gray-300'
                  }`}
                onClick={() => setActiveTab('departments')}
              >
                Phòng ban & Dịch vụ
              </button>
            </li>
          </ul>
        </div>

        {/* Tab content */}
        <div className="bg-white shadow-md rounded-lg p-6">
          <AnimatePresence mode="wait">
            {/* System Tab */}
            {activeTab === 'system' && (
              <motion.div
                key="system"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold">Thống kê hệ thống</h2>
                  <div className="flex items-center">
                    {wsConnected ? (
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full flex items-center">
                        <span className="w-2 h-2 bg-green-500 rounded-full mr-1"></span>
                        Đã kết nối thời gian thực
                      </span>
                    ) : (
                      <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded-full flex items-center">
                        <span className="w-2 h-2 bg-gray-500 rounded-full mr-1"></span>
                        Đang kết nối...
                      </span>
                    )}
                  </div>
                </div>

                {criticalAlerts && criticalAlerts.length > 0 && (
                  <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
                    <h3 className="text-red-800 text-sm font-medium mb-2 flex items-center">
                      <i className="fas fa-exclamation-triangle mr-2"></i>
                      Cảnh báo hệ thống
                    </h3>
                    <ul className="space-y-2">
                      {criticalAlerts.map((alert, index) => (
                        <li key={index} className="text-sm text-red-700 flex items-center">
                          <span className="w-1.5 h-1.5 bg-red-600 rounded-full mr-2"></span>
                          {alert.message}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {loading.stats ? (
                  <div className="flex justify-center items-center h-40">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
                  </div>
                ) : error ? (
                  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    <p>{error}</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg border border-blue-200">
                      <p className="text-blue-700 text-sm font-medium">Tổng số vé hôm nay</p>
                      <p className="text-3xl font-bold mt-2">
                        {systemStats?.ticketsToday?.count || '0'}
                      </p>
                      <div className="flex items-center mt-2 text-blue-800 text-sm">
                        <span className="mr-1">
                          <i className={`fas fa-arrow-${systemStats?.ticketsToday?.percentChange >= 0 ? 'up' : 'down'}`}></i>
                        </span>
                        <span>
                          {Math.abs(systemStats?.ticketsToday?.percentChange || 0)}% so với hôm qua
                        </span>
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg border border-green-200">
                      <p className="text-green-700 text-sm font-medium">Nhân viên đang làm việc</p>
                      <p className="text-3xl font-bold mt-2">
                        {systemStats?.activeStaff?.count || '0'}
                      </p>
                      <div className="flex items-center mt-2 text-green-800 text-sm">
                        <span className="mr-1">
                          <i className="fas fa-user-check"></i>
                        </span>
                        <span>
                          Trực tuyến: {systemStats?.activeStaff?.onlinePercent || '0'}%
                        </span>
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-6 rounded-lg border border-yellow-200">
                      <p className="text-yellow-700 text-sm font-medium">Thời gian chờ trung bình</p>
                      <p className="text-3xl font-bold mt-2">
                        {systemStats?.averageWaitTime?.minutes || '0'} phút
                      </p>
                      <div className="flex items-center mt-2 text-yellow-800 text-sm">
                        <span className="mr-1">
                          <i className="fas fa-clock"></i>
                        </span>
                        <span>
                          {systemStats?.averageWaitTime?.changeInMinutes >= 0 ? '+' : ''}
                          {systemStats?.averageWaitTime?.changeInMinutes || '0'} phút so với hôm qua
                        </span>
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg border border-purple-200">
                      <p className="text-purple-700 text-sm font-medium">Mức độ hài lòng</p>
                      <p className="text-3xl font-bold mt-2">
                        {systemStats?.satisfaction?.rating || '0'}
                      </p>
                      <div className="flex items-center mt-2 text-purple-800 text-sm">
                        <span className="mr-1">
                          <i className="fas fa-star"></i>
                        </span>
                        <span>
                          {systemStats?.satisfaction?.reviewCount || '0'} đánh giá hôm nay
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div className="bg-gray-50 rounded-lg p-6 border">
                    <h3 className="text-lg font-medium mb-4">Biểu đồ vé theo thời gian</h3>
                    <div className="h-64 flex items-center justify-center">
                      <p className="text-gray-500">Biểu đồ sẽ được hiển thị ở đây</p>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-6 border">
                    <h3 className="text-lg font-medium mb-4">Phân bố theo phòng ban</h3>
                    <div className="h-64 flex items-center justify-center">
                      <p className="text-gray-500">Biểu đồ sẽ được hiển thị ở đây</p>
                    </div>
                  </div>
                </div>

                {/* Live staff activity section */}
                <div className="bg-gray-50 rounded-lg p-6 border">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium">Hoạt động nhân viên (thời gian thực)</h3>
                    {ticketCount !== null && (
                      <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                        {ticketCount} vé đang được xử lý
                      </span>
                    )}
                  </div>

                  {staffActivity ? (
                    <div className="space-y-3">
                      {staffActivity.recentActivities && staffActivity.recentActivities.map((activity, idx) => (
                        <div key={idx} className="flex items-center p-3 bg-white rounded-lg border border-gray-100">
                          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold mr-3">
                            {activity.staffInitials || 'NV'}
                          </div>
                          <div className="flex-grow">
                            <p className="text-sm font-medium">{activity.action}</p>
                            <p className="text-xs text-gray-500">{activity.timestamp}</p>
                          </div>
                          <div className={`px-2 py-1 rounded-full text-xs ${activity.status === 'success' ? 'bg-green-100 text-green-800' :
                            activity.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                            {activity.department}
                          </div>
                        </div>
                      ))}

                      {(!staffActivity.recentActivities || staffActivity.recentActivities.length === 0) && (
                        <p className="text-center text-gray-500 py-6">
                          Không có hoạt động nào gần đây
                        </p>
                      )}
                    </div>
                  ) : (
                    <div className="text-center text-gray-500 py-8">
                      Đang tải dữ liệu hoạt động...
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {/* Users Tab */}
            {activeTab === 'users' && (
              <motion.div
                key="users"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold">Quản lý người dùng</h2>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    <i className="fas fa-plus mr-2"></i> Thêm người dùng
                  </button>
                </div>

                <div className="flex items-center mb-4 space-x-3">
                  <div className="relative flex-grow">
                    <input
                      type="text"
                      placeholder="Tìm kiếm người dùng..."
                      className="w-full px-4 py-2 pl-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <div className="absolute left-3 top-2.5 text-gray-400">
                      <i className="fas fa-search"></i>
                    </div>
                  </div>

                  <select className="border rounded-lg px-4 py-2">
                    <option>Tất cả vai trò</option>
                    <option>Quản trị viên</option>
                    <option>Quản lý</option>
                    <option>Nhân viên</option>
                  </select>

                  <select className="border rounded-lg px-4 py-2">
                    <option>Tất cả phòng ban</option>
                    <option>Phòng CSKH</option>
                    <option>Phòng tài chính</option>
                    <option>Phòng kỹ thuật</option>
                  </select>
                </div>

                {loading.users ? (
                  <div className="flex justify-center items-center h-40">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
                  </div>
                ) : error ? (
                  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    <p>{error}</p>
                  </div>
                ) : (
                  <>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Người dùng
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Vai trò
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Phòng ban
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Trạng thái
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Hành động
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {users && users.length > 0 ? (
                            users.map((user, index) => {
                              // Get initials for avatar
                              const getInitials = (name) => {
                                return name
                                  .split(' ')
                                  .map(part => part[0])
                                  .join('')
                                  .toUpperCase()
                                  .substring(0, 2);
                              };

                              // Define colors for different roles
                              const roleColors = {
                                admin: 'bg-blue-100 text-blue-800',
                                manager: 'bg-green-100 text-green-800',
                                staff: 'bg-yellow-100 text-yellow-800',
                              };

                              // Convert role for display
                              const roleDisplay = {
                                admin: 'Quản trị viên',
                                manager: 'Quản lý',
                                staff: 'Nhân viên',
                              };

                              const avatarColors = [
                                'bg-blue-100 text-blue-700',
                                'bg-green-100 text-green-700',
                                'bg-yellow-100 text-yellow-700',
                                'bg-purple-100 text-purple-700',
                                'bg-red-100 text-red-700',
                              ];

                              return (
                                <tr key={user.id || index}>
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="flex items-center">
                                      <div className={`w-10 h-10 rounded-full ${avatarColors[index % avatarColors.length]} flex items-center justify-center font-bold mr-3`}>
                                        {getInitials(user.full_name || user.email || 'User')}
                                      </div>
                                      <div>
                                        <p className="font-medium">{user.full_name || 'N/A'}</p>
                                        <p className="text-sm text-gray-500">{user.email}</p>
                                      </div>
                                    </div>
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`px-2 py-1 ${roleColors[user.role] || 'bg-gray-100 text-gray-800'} rounded-full text-xs`}>
                                      {roleDisplay[user.role] || user.role}
                                    </span>
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    {user.department_name || (user.role === 'admin' ? 'Tất cả phòng ban' : 'Chưa phân công')}
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    <span className="flex items-center">
                                      <span className={`h-2.5 w-2.5 rounded-full ${user.is_active ? 'bg-green-500' : 'bg-red-500'} mr-2`}></span>
                                      {user.is_active ? 'Hoạt động' : 'Không hoạt động'}
                                    </span>
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button className="text-blue-600 hover:text-blue-900 mr-3">
                                      <i className="fas fa-edit"></i>
                                    </button>
                                    <button className="text-red-600 hover:text-red-900">
                                      <i className="fas fa-trash-alt"></i>
                                    </button>
                                  </td>
                                </tr>
                              );
                            })
                          ) : (
                            <tr>
                              <td colSpan="5" className="px-6 py-4 text-center">
                                Không tìm thấy người dùng nào
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>

                    <div className="flex justify-between items-center mt-6">
                      <div className="text-sm text-gray-500">
                        {users && users.length > 0
                          ? `Hiển thị 1 - ${users.length} của ${users.length} người dùng`
                          : 'Không có người dùng nào'}
                      </div>

                      {users && users.length > 0 && (
                        <div className="flex space-x-2">
                          <button className="px-3 py-1 border rounded-md bg-gray-100">
                            <i className="fas fa-chevron-left"></i>
                          </button>
                          <button className="px-3 py-1 border rounded-md bg-blue-600 text-white">
                            1
                          </button>
                          <button className="px-3 py-1 border rounded-md">
                            <i className="fas fa-chevron-right"></i>
                          </button>
                        </div>
                      )}
                    </div>
                  </>
                )}
              </motion.div>
            )}

            {/* Departments Tab */}
            {activeTab === 'departments' && (
              <motion.div
                key="departments"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold">Quản lý phòng ban</h2>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    <i className="fas fa-plus mr-2"></i> Thêm phòng ban
                  </button>
                </div>

                {loading.departments ? (
                  <div className="flex justify-center items-center h-40">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
                  </div>
                ) : error ? (
                  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    <p>{error}</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {departments && departments.length > 0 ? (
                      departments.map((department, index) => (
                        <div key={department.id || index} className="bg-white border rounded-lg shadow-sm overflow-hidden">
                          <div className="p-4 border-b bg-gray-50 flex justify-between items-center">
                            <h3 className="font-medium">{department.name}</h3>
                            <div className="flex">
                              <button className="text-blue-600 hover:text-blue-900 mr-3">
                                <i className="fas fa-edit"></i>
                              </button>
                              <button className="text-red-600 hover:text-red-900">
                                <i className="fas fa-trash-alt"></i>
                              </button>
                            </div>
                          </div>
                          <div className="p-4">
                            <div className="mb-4">
                              <p className="text-sm text-gray-500 mb-1">Mã phòng</p>
                              <p className="font-medium">{department.code}</p>
                            </div>
                            <div className="mb-4">
                              <p className="text-sm text-gray-500 mb-1">Số nhân viên</p>
                              <p className="font-medium">{department.staff_count || '0'}</p>
                            </div>
                            <div className="mb-4">
                              <p className="text-sm text-gray-500 mb-1">Vị trí</p>
                              <p className="font-medium">{department.location || 'Chưa cập nhật'}</p>
                            </div>
                            <div>
                              <p className="text-sm text-gray-500 mb-1">Dịch vụ</p>
                              <div className="flex flex-wrap gap-2 mt-2">
                                {department.services && department.services.length > 0 ? (
                                  department.services.map((service, i) => (
                                    <span key={i} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                                      {service.name}
                                    </span>
                                  ))
                                ) : (
                                  <span className="text-sm text-gray-500">Chưa có dịch vụ nào</span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="col-span-3 text-center py-10 text-gray-500">
                        Không có phòng ban nào được tìm thấy
                      </div>
                    )}
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AdminDashboard;
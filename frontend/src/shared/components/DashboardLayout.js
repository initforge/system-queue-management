import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../AuthContext';

const DashboardLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Define navigation items based on user role
  const getNavigationItems = () => {
    const baseItems = [];
    
    if (user) {
      switch (user.role) {
        case 'admin':
          baseItems.push(
            { name: 'Dashboard', path: '/admin', icon: 'fa-tachometer-alt' },
            { name: 'Người dùng', path: '/admin/users', icon: 'fa-users' },
            { name: 'Phòng ban', path: '/admin/departments', icon: 'fa-building' },
            { name: 'Dịch vụ', path: '/admin/services', icon: 'fa-concierge-bell' },
            { name: 'Báo cáo', path: '/admin/reports', icon: 'fa-chart-bar' },
            { name: 'Cấu hình', path: '/admin/settings', icon: 'fa-cog' }
          );
          break;
        case 'manager':
          baseItems.push(
            { name: 'Dashboard', path: '/manager', icon: 'fa-tachometer-alt' },
            { name: 'Nhân viên', path: '/manager/staff', icon: 'fa-user-tie' },
            { name: 'Đánh giá', path: '/manager/feedback', icon: 'fa-star' },
            { name: 'Báo cáo', path: '/manager/reports', icon: 'fa-chart-bar' }
          );
          break;
        case 'staff':
          baseItems.push(
            { name: 'Dashboard', path: '/staff', icon: 'fa-tachometer-alt' },
            { name: 'Hàng đợi', path: '/staff/queue', icon: 'fa-list-ol' },
            { name: 'Vé hiện tại', path: '/staff/current', icon: 'fa-ticket-alt' },
            { name: 'Lịch sử', path: '/staff/history', icon: 'fa-history' }
          );
          break;
        default:
          break;
      }
    }
    
    return baseItems;
  };
  
  const navigationItems = getNavigationItems();
  
  const handleLogout = () => {
    logout();
    navigate('/');
  };
  
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="hidden md:flex w-64 flex-col bg-blue-800 text-white">
        <div className="h-16 flex items-center justify-center bg-blue-900 px-4">
          <div className="w-10 h-10 bg-white rounded-md flex items-center justify-center mr-3">
            <svg className="w-6 h-6 text-blue-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
            </svg>
          </div>
          <h1 className="text-lg font-bold">Hệ Thống Xếp Hàng</h1>
        </div>
        
        <div className="flex-grow overflow-y-auto">
          <nav className="mt-5 px-2">
            {navigationItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-4 py-2 mt-2 text-sm rounded-lg ${
                  location.pathname === item.path
                    ? 'bg-blue-900 text-white'
                    : 'text-blue-100 hover:bg-blue-700'
                }`}
              >
                <i className={`fas ${item.icon} mr-3`}></i>
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
        
        <div className="p-4 border-t border-blue-700">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 rounded-full bg-blue-700 flex items-center justify-center mr-2">
              <span className="text-xs font-bold">
                {user?.name?.charAt(0) || user?.email?.charAt(0) || '?'}
              </span>
            </div>
            <div>
              <p className="text-sm font-medium">{user?.name || user?.email || 'Người dùng'}</p>
              <p className="text-xs text-blue-300">{user?.role === 'admin' ? 'Quản trị viên' : user?.role === 'manager' ? 'Quản lý' : 'Nhân viên'}</p>
            </div>
          </div>
          
          <button
            onClick={handleLogout}
            className="w-full flex items-center px-4 py-2 text-sm text-blue-100 rounded-lg hover:bg-blue-700"
          >
            <i className="fas fa-sign-out-alt mr-3"></i>
            Đăng xuất
          </button>
        </div>
      </div>
      
      {/* Mobile menu */}
      <div className="md:hidden fixed top-0 left-0 right-0 bg-blue-800 z-10">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-white rounded-md flex items-center justify-center mr-2">
              <svg className="w-5 h-5 text-blue-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
              </svg>
            </div>
            <h1 className="text-base font-bold text-white">Hệ Thống Xếp Hàng</h1>
          </div>
          
          {/* Mobile menu button */}
          <button
            className="text-white focus:outline-none"
            onClick={() => {
              const mobileMenu = document.getElementById('mobile-menu');
              mobileMenu.classList.toggle('hidden');
            }}
          >
            <i className="fas fa-bars"></i>
          </button>
        </div>
        
        {/* Mobile menu dropdown */}
        <div id="mobile-menu" className="hidden">
          <nav className="px-2 pt-2 pb-3 space-y-1 bg-blue-800">
            {navigationItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`block px-3 py-2 rounded-md text-sm font-medium ${
                  location.pathname === item.path
                    ? 'bg-blue-900 text-white'
                    : 'text-blue-100 hover:bg-blue-700'
                }`}
              >
                <i className={`fas ${item.icon} mr-2`}></i>
                {item.name}
              </Link>
            ))}
            
            <button
              onClick={handleLogout}
              className="w-full text-left px-3 py-2 rounded-md text-sm font-medium text-blue-100 hover:bg-blue-700"
            >
              <i className="fas fa-sign-out-alt mr-2"></i>
              Đăng xuất
            </button>
          </nav>
        </div>
      </div>
      
      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-gray-100 pt-16 md:pt-0">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
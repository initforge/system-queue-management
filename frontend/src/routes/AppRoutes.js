import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../shared/AuthContext';

// Public pages
import Homepage from '../shared/components/Homepage';
import PublicDisplay from '../features/queue/pages/PublicDisplay';
import ServiceRegistration from '../features/queue/pages/ServiceRegistration';
import WaitingPage from '../features/queue/pages/WaitingPage';
import FeedbackPage from '../features/queue/pages/FeedbackPage';
import Login from '../features/auth/components/Login';
import NotFound from '../shared/components/NotFound';

// Dashboard pages
import StaffDashboard from '../features/dashboard/pages/StaffDashboard';
import ManagerDashboard from '../features/dashboard/pages/ManagerDashboard';
import AdminDashboard from '../features/dashboard/pages/AdminDashboard';

// Protected route component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, isAuthenticated, loading } = useAuth();

  // Show loading state
  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // Redirect to login for unauthorized access
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Check if user has required role
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Homepage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/display" element={<PublicDisplay />} />
      <Route path="/service-registration" element={<ServiceRegistration />} />
      <Route path="/waiting/:ticketId" element={<WaitingPage />} />
      <Route path="/review/:ticketId" element={<FeedbackPage />} />
      
      {/* Protected Routes */}
      <Route 
        path="/staff" 
        element={
          <ProtectedRoute allowedRoles={['staff', 'manager', 'admin']}>
            <StaffDashboard />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/manager" 
        element={
          <ProtectedRoute allowedRoles={['manager', 'admin']}>
            <ManagerDashboard />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/admin" 
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Legacy redirects for old dashboard URLs */}
      <Route path="/dashboard/staff" element={<Navigate to="/staff" replace />} />
      <Route path="/dashboard/manager" element={<Navigate to="/manager" replace />} />
      <Route path="/dashboard/admin" element={<Navigate to="/admin" replace />} />
      
      {/* Redirect to NotFound for unknown routes */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

export default AppRoutes;
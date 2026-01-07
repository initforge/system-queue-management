import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useWebSocket } from '../../../shared/WebSocketContext';
import { motion } from 'framer-motion';
import apiService from '../../../shared/api';

// Enhanced animation components
const PageWrapper = ({ children, className }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    transition={{ duration: 0.4 }}
    className={className}
  >
    {children}
  </motion.div>
);

const FadeIn = ({ children, className, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
    className={className}
  >
    {children}
  </motion.div>
);



const ServiceRegistrationPage = () => {
  const navigate = useNavigate();
  const { deptCode } = useParams();

  const [departments, setDepartments] = useState([]);
  const [services, setServices] = useState([]);
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [selectedService, setSelectedService] = useState(null);
  const [step, setStep] = useState(deptCode ? 2 : 1);
  const [customerInfo, setCustomerInfo] = useState({
    name: '',
    phone: '',
    email: '',
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { joinQueue } = useWebSocket();

  // 🚀 OPTIMIZED loadServices - Move to top level to avoid dependency warning
  const loadServices = async (departmentId) => {
    try {
      setLoading(true);
      console.log('🔍 Đang tải dịch vụ cho phòng ban:', departmentId);

      // Gọi API qua lớp apiService để lấy danh sách tất cả dịch vụ
      const data = await apiService.getAllServices();

      if (data.success && data.services) {
        // Lọc dịch vụ theo phòng ban và format cho UI - limit to 4 services
        const filteredServices = data.services
          .filter(service => service.department_id === departmentId)
          .slice(0, 4) // Limit to 4 services per department
          .map(service => ({
            id: service.id,
            name: service.name,
            description: service.description,
            price: service.price || 'Miễn phí',
            duration: `${service.estimated_duration} phút`
          }));

        setServices(filteredServices);
        console.log(`✅ Đã tải thành công ${filteredServices.length} dịch vụ`);
        setErrors(prev => ({ ...prev, services: null }));
      } else {
        console.error('❌ API trả về lỗi:', data.error || 'Unknown error');
        throw new Error(data.error || 'API response invalid');
      }
    } catch (error) {
      console.error('❌ Lỗi khi gọi API:', error);
      setServices([]);
      setErrors(prev => ({
        ...prev,
        services: 'Không thể tải dịch vụ từ database. Vui lòng kiểm tra kết nối server.'
      }));
    } finally {
      setLoading(false);
    }
  };

  // Load departments on mount from API
  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1'}/departments`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        console.log('Departments loaded from API:', data);
        setDepartments(data);

        if (deptCode) {
          const dept = data.find(d => d.code === deptCode.toUpperCase());
          if (dept) {
            setSelectedDepartment(dept.id);
            loadServices(dept.id);
          }
        }
      } catch (error) {
        console.error('Error loading departments:', error);
        setErrors({ general: 'Không thể kết nối đến server để tải danh sách phòng ban.' });
      } finally {
        setLoading(false);
      }
    };
    fetchDepartments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [deptCode]);

  const handleDepartmentSelect = (deptId) => {
    setSelectedDepartment(deptId);
    setSelectedService(null);
    setServices([]);
    loadServices(deptId);
    setStep(2);
  };

  const handleServiceSelect = (service) => {
    setSelectedService(service);
    setStep(3);
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);

      // Validate required fields
      if (!customerInfo.name || !customerInfo.phone || !selectedDepartment || !selectedService?.id) {
        setErrors({ submit: 'Vui lòng điền đầy đủ thông tin bắt buộc!' });
        return;
      }

      // Prepare API payload
      const ticketPayload = {
        customer_name: customerInfo.name,
        customer_phone: customerInfo.phone,
        customer_email: customerInfo.email || null,
        service_id: selectedService.id,
        department_id: selectedDepartment,
        // priority optional; backend defaults to normal if omitted
        priority: 'normal',
        notes: customerInfo.notes || null,
        form_data: {
          ...customerInfo,
          department_id: selectedDepartment,
          department_name: departments.find(d => d.id === selectedDepartment)?.name,
          service_name: selectedService.name
        }
      };

      console.log('Creating ticket with payload:', ticketPayload);

      // Call real API to create ticket
      const response = await apiService.makeRequest('/tickets/register', {
        method: 'POST',
        body: JSON.stringify(ticketPayload)
      });

      console.log('Ticket created successfully:', response);

      // Extract ticket ID from response
      const ticketId = response.ticket?.id || response.id;

      if (!ticketId) {
        throw new Error('Invalid ticket response: missing ticket ID');
      }

      // Join WebSocket queue if available
      if (joinQueue) {
        // Join by ticket id for real-time updates
        joinQueue(ticketId);
      }

      // Navigate to waiting page with real ticket data
      navigate(`/waiting/${ticketId}`, {
        state: {
          ticket: {
            id: ticketId,
            ticketNumber: response.ticket?.ticket_number || response.ticket_number,
            department: response.department_name,
            service: response.service_name,
            customerInfo: {
              name: response.ticket?.customer_name || response.customer_name,
              phone: response.customer_phone,
              email: response.customer_email
            },
            estimatedWait: response.estimated_wait_time || 15,
            position: response.queue_position || 1,
            status: response.ticket?.status || response.status
          }
        }
      });
    } catch (error) {
      console.error('Error creating ticket:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Không thể tạo vé. Vui lòng thử lại!';
      setErrors({ submit: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  // Service icons mapping
  const serviceIcons = {
    'Khám Tổng Quát': (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    'Khám Chuyên Khoa': (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
      </svg>
    ),
    'Xét Nghiệm': (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
      </svg>
    ),
    'Cấp Giấy Khai Sinh': (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    'Đăng Ký Thường Trú': (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
      </svg>
    ),
    'Mở Tài Khoản': (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
    'Vay Vốn': (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
      </svg>
    ),
    'Báo Cáo Tài Chính': (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    'Kê Khai Thuế': (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
      </svg>
    )
  };

  return (
    <PageWrapper className="min-h-screen bg-gradient-to-br from-cyan-50 via-white to-blue-50 font-['Roboto',_sans-serif] relative">
      {/* Background decoration */}
      <div className="absolute inset-0 opacity-20 pointer-events-none">
        <div className="w-full h-full bg-gradient-to-br from-blue-100/30 to-transparent"></div>
      </div>

      {/* Header with progress bar */}
      <FadeIn className="bg-white/95 backdrop-blur-sm shadow-xl border-b border-blue-100">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <motion.div
                className="w-12 h-12 bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-lg"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </motion.div>
              <div>
                <h1 className="text-2xl font-bold text-blue-900 leading-tight">Đăng ký Dịch vụ</h1>
                <p className="text-blue-600 text-sm">Vui lòng chọn dịch vụ bạn cần sử dụng</p>
              </div>
            </div>

            {/* Modern progress indicator */}
            <div className="flex items-center space-x-2">
              {[1, 2, 3].map((i) => (
                <motion.div
                  key={i}
                  initial={{ scale: 0.8, opacity: 0.5 }}
                  animate={{
                    scale: i <= step ? 1 : 0.8,
                    opacity: i <= step ? 1 : 0.5
                  }}
                  transition={{ duration: 0.3, delay: i * 0.1 }}
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300 ${i <= step
                      ? 'bg-gradient-to-r from-green-500 to-green-600 text-white shadow-lg transform scale-110'
                      : 'bg-gray-200 text-gray-500'
                    }`}
                >
                  {i < step ? '✓' : i}
                </motion.div>
              ))}
            </div>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${(step / 3) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Chọn phòng ban</span>
            <span>Chọn dịch vụ</span>
            <span>Thông tin cá nhân</span>
          </div>
        </div>
      </FadeIn>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Error Message */}
        {errors.general && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 shadow-sm"
          >
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="text-red-800 font-medium">{errors.general}</p>
            </div>
          </motion.div>
        )}

        {/* Step 1: Department Selection */}
        {step === 1 && (
          <FadeIn>
            <div className="bg-white/95 backdrop-blur rounded-2xl shadow-xl border border-blue-100 p-8">
              <motion.h2
                className="text-3xl font-bold text-blue-900 mb-8 text-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                🏢 Chọn Phòng ban
              </motion.h2>
              <div className="grid md:grid-cols-2 gap-6">
                {departments.map((dept, index) => (
                  <motion.div
                    key={dept.id}
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.15 }}
                    whileHover={{
                      scale: 1.03,
                      boxShadow: "0 20px 40px rgba(59, 130, 246, 0.15)"
                    }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleDepartmentSelect(dept.id)}
                    className="p-6 border-2 border-blue-100 rounded-xl hover:border-blue-300 hover:bg-blue-50/50 cursor-pointer transition-all duration-300 group bg-gradient-to-br from-white to-blue-50/30"
                  >
                    <div className="flex items-start space-x-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center group-hover:from-blue-600 group-hover:to-blue-700 transition-colors shadow-lg">
                        <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                        </svg>
                      </div>
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-900 group-hover:text-blue-900 line-height-1.2">{dept.name}</h3>
                        <p className="text-gray-600 mt-2 line-height-1.5">{dept.description}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </FadeIn>
        )}

        {/* Step 2: Service Selection */}
        {step === 2 && (
          <FadeIn>
            <div className="bg-white/95 backdrop-blur rounded-2xl shadow-xl border border-blue-100 p-8">
              <motion.h2
                className="text-3xl font-bold text-blue-900 mb-2 text-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                🎯 {departments.find(d => d.id === selectedDepartment)?.name}
              </motion.h2>
              <p className="text-center text-blue-600 mb-8 text-lg">Chọn dịch vụ bạn cần</p>

              {loading ? (
                <div className="flex justify-center py-16">
                  <motion.div
                    className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  />
                </div>
              ) : (
                <div className="grid lg:grid-cols-2 gap-6">
                  {services.map((service, index) => (
                    <motion.div
                      key={service.id}
                      initial={{ opacity: 0, y: 30 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      whileHover={{
                        scale: 1.02,
                        boxShadow: "0 15px 35px rgba(76, 175, 80, 0.15)"
                      }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleServiceSelect(service)}
                      className="p-6 border-2 border-green-100 rounded-xl hover:border-green-300 hover:bg-green-50/50 cursor-pointer transition-all duration-300 group bg-gradient-to-br from-white to-green-50/30"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center text-white group-hover:from-green-600 group-hover:to-green-700 transition-colors">
                            {serviceIcons[service.name] || (
                              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                              </svg>
                            )}
                          </div>
                          <div>
                            <h3 className="text-xl font-bold text-gray-900 group-hover:text-green-900">{service.name}</h3>
                          </div>
                        </div>
                      </div>

                      <p className="text-gray-600 mb-4 line-height-1.5">{service.description}</p>

                      <div className="flex justify-between items-center pt-4 border-t border-gray-100">
                        <div className="text-right">
                          <div className="text-2xl font-bold text-green-600">{service.price}</div>
                          <div className="text-sm text-gray-500 flex items-center">
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            {service.duration}
                          </div>
                        </div>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          className="px-6 py-2 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg font-medium hover:from-green-600 hover:to-green-700 transition-colors shadow-lg"
                        >
                          Chọn
                        </motion.button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}

              <div className="mt-8 flex justify-center">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setStep(1)}
                  className="px-6 py-3 bg-gray-300 text-gray-700 rounded-xl hover:bg-gray-400 transition-colors font-medium flex items-center space-x-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  <span>Quay lại</span>
                </motion.button>
              </div>
            </div>
          </FadeIn>
        )}

        {/* Step 3: Customer Information */}
        {step === 3 && (
          <FadeIn>
            <div className="bg-white/95 backdrop-blur rounded-2xl shadow-xl border border-blue-100 p-8">
              <motion.h2
                className="text-3xl font-bold text-blue-900 mb-8 text-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                👤 Thông tin khách hàng
              </motion.h2>

              <div className="max-w-2xl mx-auto">
                <div className="space-y-6">
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                  >
                    <label className="block text-sm font-bold text-gray-700 mb-3">
                      Họ và tên *
                    </label>
                    <input
                      type="text"
                      value={customerInfo.name}
                      onChange={(e) => setCustomerInfo({ ...customerInfo, name: e.target.value })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-lg font-medium text-gray-900 hover:border-blue-300"
                      placeholder="Nhập họ và tên đầy đủ"
                    />
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                  >
                    <label className="block text-sm font-bold text-gray-700 mb-3">
                      Số điện thoại *
                    </label>
                    <input
                      type="tel"
                      value={customerInfo.phone}
                      onChange={(e) => setCustomerInfo({ ...customerInfo, phone: e.target.value })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-lg font-medium text-gray-900 hover:border-blue-300"
                      placeholder="Nhập số điện thoại"
                    />
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 }}
                  >
                    <label className="block text-sm font-bold text-gray-700 mb-3">
                      Email
                    </label>
                    <input
                      type="email"
                      value={customerInfo.email}
                      onChange={(e) => setCustomerInfo({ ...customerInfo, email: e.target.value })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-lg font-medium text-gray-900 hover:border-blue-300"
                      placeholder="Nhập email (không bắt buộc)"
                    />
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                  >
                    <label className="block text-sm font-bold text-gray-700 mb-3">
                      Ghi chú
                    </label>
                    <textarea
                      value={customerInfo.notes}
                      onChange={(e) => setCustomerInfo({ ...customerInfo, notes: e.target.value })}
                      rows={4}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-lg font-medium text-gray-900 hover:border-blue-300 resize-none"
                      placeholder="Ghi chú thêm về yêu cầu của bạn (không bắt buộc)"
                    />
                  </motion.div>
                </div>

                {errors.submit && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="mt-6 bg-red-50 border border-red-200 rounded-xl p-4"
                  >
                    <p className="text-red-800 font-medium">{errors.submit}</p>
                  </motion.div>
                )}

                <div className="flex justify-between mt-8 gap-4">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setStep(2)}
                    className="px-6 py-3 bg-gray-300 text-gray-700 rounded-xl hover:bg-gray-400 transition-colors font-medium flex items-center space-x-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    <span>Quay lại</span>
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: loading ? 1 : 1.05 }}
                    whileTap={{ scale: loading ? 1 : 0.95 }}
                    onClick={handleSubmit}
                    disabled={loading || !customerInfo.name || !customerInfo.phone}
                    className="px-8 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl hover:from-green-600 hover:to-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-bold text-lg shadow-lg flex items-center space-x-2"
                  >
                    {loading ? (
                      <>
                        <motion.div
                          className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        />
                        <span>Đang xử lý...</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>Hoàn tất đăng ký</span>
                      </>
                    )}
                  </motion.button>
                </div>
              </div>
            </div>
          </FadeIn>
        )}
      </div>
    </PageWrapper>
  );
};

export default ServiceRegistrationPage;// Updated 10/14/2025 18:17:41

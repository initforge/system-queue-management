import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../shared/AuthContext';
import { motion, AnimatePresence, useMotionValue, useSpring, useTransform } from 'framer-motion';

// Clock Component với CSS animations thuần - không flickering
const AnalogClock = React.memo(({ currentTime }) => {
  const minuteHandRef = useRef(null);
  const secondHandRef = useRef(null);

  useEffect(() => {
    const now = currentTime;
    const minutes = now.getMinutes();
    const seconds = now.getSeconds();

    // Set minute hand position
    if (minuteHandRef.current) {
      const minuteRotation = minutes * 6 + (seconds * 0.1);
      minuteHandRef.current.style.transform = `rotate(${minuteRotation}deg)`;
    }

    // Set second hand initial position và start CSS animation
    if (secondHandRef.current) {
      const secondRotation = seconds * 6;

      // Reset animation và force reflow
      secondHandRef.current.style.animation = 'none';
      void secondHandRef.current.offsetHeight; // Force reflow

      // Set initial rotation
      secondHandRef.current.style.transform = `rotate(${secondRotation}deg)`;

      // Start continuous animation from current position
      secondHandRef.current.style.animation = `secondHandRotate 60s linear infinite`;
      secondHandRef.current.style.animationDelay = `${-seconds}s`;
    }
  }, [currentTime]);

  return (
    <>
      <style>{`
        @keyframes secondHandRotate {
          from {
            transform: rotate(var(--start-rotation, 0deg));
          }
          to {
            transform: rotate(calc(var(--start-rotation, 0deg) + 360deg));
          }
        }
      `}</style>
      <div className="relative w-80 h-80 mx-auto">
        {/* Outer Glow Ring */}
        <motion.div
          className="absolute inset-0 rounded-full bg-gradient-to-br from-blue-500/20 via-indigo-500/20 to-purple-500/20 blur-2xl"
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.3, 0.5, 0.3]
          }}
          transition={{ duration: 4, repeat: Infinity }}
        />

        {/* Clock Face */}
        <div className="relative w-full h-full rounded-full bg-gradient-to-br from-slate-800/90 to-slate-900/90 backdrop-blur-xl border-2 border-white/10 shadow-2xl">
          {/* Clock Numbers */}
          {[12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map((num) => {
            const angle = (num * 30 - 90) * (Math.PI / 180);
            const radius = 140;
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            return (
              <div
                key={num}
                className="absolute text-white font-semibold text-lg"
                style={{
                  left: `calc(50% + ${x}px)`,
                  top: `calc(50% + ${y}px)`,
                  transform: 'translate(-50%, -50%)'
                }}
              >
                {num}
              </div>
            );
          })}

          {/* Minute Markers */}
          {Array.from({ length: 60 }).map((_, i) => {
            const angle = (i * 6 - 90) * (Math.PI / 180);
            const radius = 150;
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            const isHourMarker = i % 5 === 0;
            return (
              <div
                key={i}
                className={`absolute top-1/2 left-1/2 rounded-full bg-white/40`}
                style={{
                  width: isHourMarker ? '4px' : '2px',
                  height: isHourMarker ? '12px' : '6px',
                  left: `calc(50% + ${x}px)`,
                  top: `calc(50% + ${y}px)`,
                  transform: `translate(-50%, -50%) rotate(${i * 6}deg)`,
                  transformOrigin: '0 0'
                }}
              />
            );
          })}

          {/* Center Dot */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full z-20 shadow-lg" />

          {/* Minute Hand ONLY - NO HOUR HAND */}
          <div
            ref={minuteHandRef}
            className="absolute top-1/2 left-1/2 origin-bottom z-10 pointer-events-none"
            style={{
              width: '5px',
              height: '110px',
              marginLeft: '-2.5px',
              marginTop: '-110px',
              transition: 'transform 0.3s linear'
            }}
          >
            <div className="w-full h-full bg-gradient-to-t from-indigo-500 to-indigo-400 rounded-full shadow-lg" />
          </div>

          {/* Second Hand - Pure CSS animation */}
          <div
            ref={secondHandRef}
            className="absolute top-1/2 left-1/2 origin-bottom z-20 pointer-events-none"
            style={{
              width: '2px',
              height: '130px',
              marginLeft: '-1px',
              marginTop: '-130px'
            }}
          >
            <div className="w-full h-full bg-gradient-to-t from-cyan-400 to-cyan-300 rounded-full" />
          </div>
        </div>
      </div>
    </>
  );
});

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentTime, setCurrentTime] = useState(new Date());
  const navigate = useNavigate();
  const { login } = useAuth();
  const containerRef = useRef(null);

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const x = useSpring(useTransform(mouseX, [-0.5, 0.5], [-20, 20]), { damping: 50, stiffness: 100 });
  const y = useSpring(useTransform(mouseY, [-0.5, 0.5], [-20, 20]), { damping: 50, stiffness: 100 });

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const handleMouseMove = (e) => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      mouseX.set((e.clientX - centerX) / rect.width);
      mouseY.set((e.clientY - centerY) / rect.height);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const user = await login({
        email: formData.email,
        password: formData.password
      });

      if (user && user.role) {
        switch (user.role) {
          case 'staff':
            navigate('/staff');
            break;
          case 'manager':
            navigate('/manager');
            break;
          case 'admin':
            navigate('/admin');
            break;
          default:
            navigate('/');
            break;
        }
      }
    } catch (err) {
      setError(err.message || 'Đăng nhập thất bại');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      className="min-h-screen relative overflow-hidden bg-slate-950 flex items-center justify-center p-6"
    >
      {/* Animated Background */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute inset-0"
          style={{
            background: 'radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.12) 0%, transparent 70%)',
            x,
            y
          }}
        />
        <motion.div
          className="absolute inset-0"
          style={{
            background: 'radial-gradient(circle at 30% 70%, rgba(139, 92, 246, 0.08) 0%, transparent 60%)',
            x: useTransform(x, (x) => -x * 0.5),
            y: useTransform(y, (y) => -y * 0.5)
          }}
        />

        {/* Grid Pattern */}
        <div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255, 255, 255, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px'
          }}
        />
      </div>

      {/* Main Content */}
      <div className="relative z-10 max-w-6xl w-full grid lg:grid-cols-2 gap-12 items-center">

        {/* Left Panel - Clock & Information */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="hidden lg:block"
        >
          <div className="space-y-10">
            {/* Animated Clock */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
              animate={{ opacity: 1, scale: 1, rotate: 0 }}
              transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
              className="relative"
            >
              <AnalogClock currentTime={currentTime} />
            </motion.div>

            {/* Time Display */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="text-center space-y-2"
            >
              <div className="text-5xl font-mono font-bold text-white">
                {currentTime.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </div>
              <div className="text-slate-400 text-lg">
                {currentTime.toLocaleDateString('vi-VN', {
                  weekday: 'long',
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric'
                })}
              </div>
            </motion.div>

            {/* System Info */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
              className="space-y-4"
            >
              <h1 className="text-4xl font-bold bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
                Queue Management System
              </h1>
              <p className="text-slate-400 text-lg leading-relaxed">
                Đăng nhập để truy cập vào hệ thống quản lý hàng đợi thông minh
              </p>
            </motion.div>
          </div>
        </motion.div>

        {/* Right Panel - Login Form */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="w-full max-w-md mx-auto lg:mx-0"
        >
          <div className="relative">
            {/* Glass Card */}
            <div className="bg-white/5 backdrop-blur-2xl rounded-3xl border border-white/10 shadow-2xl overflow-hidden">
              <div className="p-10">
                {/* Header */}
                <motion.div
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                  className="text-center mb-8"
                >
                  <motion.div
                    className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl mx-auto mb-4 flex items-center justify-center shadow-lg shadow-blue-500/25"
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ duration: 0.3 }}
                  >
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </motion.div>
                  <h2 className="text-3xl font-bold text-white mb-2">Đăng nhập</h2>
                  <p className="text-slate-400">Vui lòng nhập thông tin của bạn</p>
                </motion.div>

                {/* Error Message */}
                <AnimatePresence>
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95, y: -10 }}
                      animate={{ opacity: 1, scale: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl backdrop-blur-sm"
                    >
                      <div className="flex items-center text-red-400">
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="text-sm">{error}</span>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Email Input */}
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: 0.3 }}
                  >
                    <label htmlFor="email" className="block text-white/90 text-sm font-semibold mb-2">
                      Email
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                        </svg>
                      </div>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-white placeholder-slate-500"
                        placeholder="name@example.com"
                        required
                      />
                    </div>
                  </motion.div>

                  {/* Password Input */}
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                  >
                    <label htmlFor="password" className="block text-white/90 text-sm font-semibold mb-2">
                      Mật khẩu
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                      </div>
                      <input
                        type="password"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-white placeholder-slate-500"
                        placeholder="••••••••"
                        required
                      />
                    </div>
                  </motion.div>

                  {/* Submit Button */}
                  <motion.button
                    type="submit"
                    disabled={isLoading}
                    className={`w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold shadow-lg shadow-blue-500/25 transition-all duration-300 ${isLoading ? 'opacity-70 cursor-not-allowed' : 'hover:shadow-xl hover:shadow-blue-500/40'
                      }`}
                    whileHover={!isLoading ? { scale: 1.02, y: -2 } : {}}
                    whileTap={!isLoading ? { scale: 0.98 } : {}}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.5 }}
                  >
                    {isLoading ? (
                      <div className="flex items-center justify-center">
                        <motion.div
                          className="w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-3"
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        />
                        Đang xử lý...
                      </div>
                    ) : (
                      <div className="flex items-center justify-center">
                        <span>Đăng nhập</span>
                        <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                      </div>
                    )}
                  </motion.button>
                </form>

                {/* Footer Links */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.6, delay: 0.6 }}
                  className="mt-8 text-center text-sm text-slate-400"
                >
                  <a href="#" className="hover:text-blue-400 transition-colors">Quên mật khẩu?</a>
                </motion.div>
              </div>
            </div>

            {/* Decorative Elements */}
            <motion.div
              className="absolute -z-10 -inset-4 bg-gradient-to-r from-blue-500/20 via-indigo-500/20 to-purple-500/20 rounded-3xl blur-2xl"
              animate={{
                opacity: [0.3, 0.5, 0.3],
                scale: [1, 1.05, 1]
              }}
              transition={{ duration: 4, repeat: Infinity }}
            />
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Login;

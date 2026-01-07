import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';

const Homepage = () => {
  const containerRef = useRef(null);
  const [currentTime, setCurrentTime] = useState(new Date());

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const springConfig = { damping: 50, stiffness: 100 };
  const x = useSpring(useTransform(mouseX, [-0.5, 0.5], [-30, 30]), springConfig);
  const y = useSpring(useTransform(mouseY, [-0.5, 0.5], [-30, 30]), springConfig);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const handleMouseMove = (e) => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      const normalizedX = (e.clientX - centerX) / rect.width;
      const normalizedY = (e.clientY - centerY) / rect.height;

      mouseX.set(normalizedX);
      mouseY.set(normalizedY);
    }
  };

  const cards = [
    {
      title: 'Khách hàng',
      description: 'Đăng ký dịch vụ và theo dõi tiến trình trong thời gian thực',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      ),
      gradient: 'from-blue-500/20 via-cyan-500/20 to-teal-500/20',
      borderGradient: 'from-blue-400/40 via-cyan-400/40 to-teal-400/40',
      link: '/display',
      delay: 0.1
    },
    {
      title: 'Nhân viên',
      description: 'Quản lý hàng đợi, xử lý yêu cầu và tương tác với khách hàng',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      gradient: 'from-indigo-500/20 via-purple-500/20 to-pink-500/20',
      borderGradient: 'from-indigo-400/40 via-purple-400/40 to-pink-400/40',
      link: '/login',
      delay: 0.2
    },
    {
      title: 'Quản trị viên',
      description: 'Giám sát hệ thống, phân tích dữ liệu và cấu hình toàn diện',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      gradient: 'from-amber-500/20 via-orange-500/20 to-red-500/20',
      borderGradient: 'from-amber-400/40 via-orange-400/40 to-red-400/40',
      link: '/login',
      delay: 0.3
    }
  ];

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      className="min-h-screen relative overflow-hidden bg-slate-950"
    >
      {/* Animated Gradient Background */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute inset-0"
          style={{
            background: 'radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.15) 0%, transparent 70%)',
            x,
            y
          }}
        />
        <motion.div
          className="absolute inset-0"
          style={{
            background: 'radial-gradient(circle at 30% 70%, rgba(139, 92, 246, 0.1) 0%, transparent 60%)',
            x: useTransform(x, (x) => -x * 0.5),
            y: useTransform(y, (y) => -y * 0.5)
          }}
        />
      </div>

      {/* Grid Pattern Overlay */}
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

      {/* Floating Orbs */}
      {[...Array(3)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full blur-3xl"
          style={{
            width: `${200 + i * 100}px`,
            height: `${200 + i * 100}px`,
            background: `radial-gradient(circle, rgba(${59 + i * 50}, ${130 - i * 30}, 246, 0.1), transparent)`,
            left: `${20 + i * 30}%`,
            top: `${30 + i * 20}%`
          }}
          animate={{
            x: [0, 50, -50, 0],
            y: [0, -30, 30, 0],
            scale: [1, 1.2, 0.9, 1]
          }}
          transition={{
            duration: 20 + i * 5,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      ))}

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="pt-16 pb-12 px-6"
        >
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-12">
              {/* Logo */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="flex items-center space-x-3"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/25">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <div className="text-white font-bold text-lg">QueueFlow</div>
                  <div className="text-slate-400 text-xs">Management System</div>
                </div>
              </motion.div>

              {/* Time Display */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="hidden md:flex items-center space-x-4 px-6 py-3 bg-white/5 backdrop-blur-xl rounded-xl border border-white/10"
              >
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <div className="text-slate-300 text-sm font-mono">
                  {currentTime.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                </div>
              </motion.div>
            </div>

            {/* Hero Section */}
            <div className="max-w-4xl">
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.3 }}
                className="text-6xl md:text-7xl lg:text-8xl font-bold mb-6 leading-tight"
              >
                <span className="bg-gradient-to-r from-white via-blue-100 to-white bg-clip-text text-transparent">
                  Quản lý hàng đợi
                </span>
                <br />
                <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400 bg-clip-text text-transparent">
                  thông minh
                </span>
              </motion.h1>
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.5 }}
                className="text-xl md:text-2xl text-slate-400 font-light leading-relaxed max-w-2xl"
              >
                Nền tảng công nghệ tiên tiến giúp tối ưu hóa trải nghiệm khách hàng
                và nâng cao hiệu quả vận hành doanh nghiệp
              </motion.p>
            </div>
          </div>
        </motion.header>

        {/* Cards Grid */}
        <div className="flex-1 flex items-center justify-center px-6 py-12">
          <div className="max-w-7xl mx-auto w-full">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.7 }}
              className="grid md:grid-cols-3 gap-8"
            >
              {cards.map((card, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 40 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.8 + card.delay, ease: [0.22, 1, 0.36, 1] }}
                >
                  <Link to={card.link}>
                    <motion.div
                      whileHover={{ y: -12, scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="group relative h-full p-8 rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 hover:border-white/20 overflow-hidden cursor-pointer transition-all duration-300"
                    >
                      {/* Animated Gradient Border */}
                      <motion.div
                        className={`absolute inset-0 rounded-2xl bg-gradient-to-r ${card.borderGradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`}
                        style={{
                          padding: '1px',
                          WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
                          WebkitMaskComposite: 'xor',
                          maskComposite: 'exclude'
                        }}
                      />

                      {/* Content */}
                      <div className="relative z-10">
                        {/* Icon */}
                        <motion.div
                          className={`w-16 h-16 rounded-xl bg-gradient-to-br ${card.gradient} flex items-center justify-center text-white mb-6 group-hover:scale-110 transition-transform duration-300`}
                          whileHover={{ rotate: [0, -5, 5, 0] }}
                          transition={{ duration: 0.5 }}
                        >
                          {card.icon}
                        </motion.div>

                        {/* Title */}
                        <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-blue-300 transition-colors">
                          {card.title}
                        </h3>

                        {/* Description */}
                        <p className="text-slate-400 mb-6 leading-relaxed group-hover:text-slate-300 transition-colors">
                          {card.description}
                        </p>

                        {/* CTA */}
                        <div className="flex items-center text-blue-400 font-semibold group-hover:text-blue-300 transition-colors">
                          <span>Khám phá</span>
                          <motion.svg
                            className="w-5 h-5 ml-2"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            animate={{ x: [0, 5, 0] }}
                            transition={{ duration: 1.5, repeat: Infinity }}
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                          </motion.svg>
                        </div>
                      </div>

                      {/* Shine Effect */}
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100"
                        initial={{ x: '-100%' }}
                        whileHover={{ x: '100%' }}
                        transition={{ duration: 0.6 }}
                      />
                    </motion.div>
                  </Link>
                </motion.div>
              ))}
            </motion.div>

            {/* Features Bar */}
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 1.2 }}
              className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6"
            >
              {[
                { label: 'Real-time', value: 'Tức thời' },
                { label: 'Secure', value: 'Bảo mật' },
                { label: 'Scalable', value: 'Mở rộng' },
                { label: 'Analytics', value: 'Phân tích' }
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: 1.3 + index * 0.1 }}
                  className="text-center p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 hover:border-white/20 transition-all"
                >
                  <div className="text-white font-bold text-lg mb-1">{feature.value}</div>
                  <div className="text-slate-400 text-xs">{feature.label}</div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 1.5 }}
          className="px-6 py-8 border-t border-white/10"
        >
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between">
            <p className="text-slate-400 text-sm mb-4 md:mb-0">
              © 2025 QueueFlow. All rights reserved.
            </p>
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <span className="text-green-400 text-sm">Online</span>
              </div>
              <span className="text-slate-500 text-sm">v1.0.0</span>
            </div>
          </div>
        </motion.footer>
      </div>
    </div>
  );
};

export default Homepage;

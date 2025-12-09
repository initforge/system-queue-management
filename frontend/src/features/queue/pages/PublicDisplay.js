import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

const PublicDisplay = () => {
  const navigate = useNavigate();
  const qrRef = useRef(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [floatingElements, setFloatingElements] = useState([]);
  const [isQrHovered, setIsQrHovered] = useState(false);
  const [qrImageUrl, setQrImageUrl] = useState(null);
  
  const serviceRegistrationUrl = `${window.location.origin}/service-registration`;

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Generate floating elements - optimized
  useEffect(() => {
    const generateElements = () => {
      const timeIcons = ['🕐', '⏰', '⏱️', '📅', '🗓️', '📊', '🎯', '⚡'];
      const newElements = Array.from({ length: 12 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 25 + 18,
        delay: Math.random() * 2, // Reduced delay
        duration: Math.random() * 10 + 8, // Faster animations
        opacity: Math.random() * 0.2 + 0.08,
        icon: timeIcons[Math.floor(Math.random() * timeIcons.length)],
        color: `hsla(${170 + Math.random() * 40}, 60%, ${70 + Math.random() * 20}%, 0.5)`
      }));
      setFloatingElements(newElements);
    };

    generateElements();
    const interval = setInterval(generateElements, 20000);
    return () => clearInterval(interval);
  }, []);

  // Generate QR Code URL - Only once on mount
  useEffect(() => {
    const generateQrUrl = () => {
      const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=350x350&data=${encodeURIComponent(serviceRegistrationUrl)}&margin=20&color=0f4c75&bgcolor=ffffff&qzone=3`;
      setQrImageUrl(qrUrl);
    };

    generateQrUrl();
  }, []); // Empty dependency array - only run once

  const handleDirectAccess = () => {
    navigate('/service-registration');
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
        ease: "easeOut"
      }
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      {/* Background Elements */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute inset-0"
          animate={{
            background: [
              'radial-gradient(circle at 20% 20%, rgba(16, 185, 129, 0.08) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(6, 182, 212, 0.06) 0%, transparent 50%)',
              'radial-gradient(circle at 80% 20%, rgba(16, 185, 129, 0.06) 0%, transparent 50%), radial-gradient(circle at 20% 80%, rgba(6, 182, 212, 0.08) 0%, transparent 50%)',
              'radial-gradient(circle at 20% 20%, rgba(16, 185, 129, 0.08) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(6, 182, 212, 0.06) 0%, transparent 50%)'
            ]
          }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
        />

        {/* Floating elements - optimized */}
        <AnimatePresence>
          {floatingElements.map((element) => (
            <motion.div
              key={element.id}
              className="absolute flex items-center justify-center rounded-full pointer-events-none"
              style={{
                left: `${element.x}%`,
                top: `${element.y}%`,
                width: `${element.size}px`,
                height: `${element.size}px`,
                backgroundColor: element.color,
                opacity: element.opacity,
                fontSize: `${element.size * 0.6}px`
              }}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ 
                scale: [0, 1, 0.9, 1, 0],
                y: [0, -40, -80, -120],
                x: [0, Math.random() * 20 - 10],
                opacity: [0, element.opacity, element.opacity, 0]
              }}
              transition={{
                duration: element.duration,
                delay: element.delay,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              {element.icon}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative z-10 pt-8 pb-6 text-center"
      >
        <motion.h1 
          className="text-4xl md:text-6xl font-bold text-emerald-700 mb-4"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          QueueFlow System
        </motion.h1>
        
        {/* Real-time clock display */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="inline-block bg-white/80 backdrop-blur-lg rounded-2xl px-8 py-4 border border-emerald-200/50 shadow-lg"
        >
          <motion.div
            key={`${currentTime.getHours()}-${currentTime.getMinutes()}-${currentTime.getSeconds()}`}
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.3 }}
            className="text-2xl font-mono font-bold text-emerald-800 tracking-wider"
          >
            {currentTime.toLocaleTimeString('vi-VN')} - {currentTime.toLocaleDateString('vi-VN', { weekday: 'long' })}
          </motion.div>
        </motion.div>
      </motion.header>

      {/* Main QR Code Center */}
      <div className="relative z-10 flex items-center justify-center min-h-[60vh] px-6">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="text-center max-w-2xl mx-auto"
        >
          {/* QR Code Container */}
          <motion.div
            variants={itemVariants}
            className="relative mb-8"
            onHoverStart={() => setIsQrHovered(true)}
            onHoverEnd={() => setIsQrHovered(false)}
          >
            <motion.div
              className={`relative inline-block p-6 rounded-3xl transition-all duration-300 cursor-pointer ${
                isQrHovered 
                  ? 'bg-gradient-to-br from-white to-emerald-50 shadow-2xl' 
                  : 'bg-gradient-to-br from-white/95 to-white/85 shadow-xl'
              }`}
              whileHover={{ y: -8, scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {/* QR Code */}
              <motion.div
                className="relative"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                {qrImageUrl ? (
                <img
                  ref={qrRef}
                    src={qrImageUrl}
                  alt="QR Code để truy cập dịch vụ"
                    className="w-72 h-72 md:w-80 md:h-80 mx-auto rounded-2xl shadow-lg"
                    loading="eager"
                  onError={(e) => {
                    e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmZGY0Ii8+PHRleHQgeD0iNTAlIiB5PSI0NSUiIGZvbnQtc2l6ZT0iMjAiIGZpbGw9IiMwZjRjNzUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5RUiBDb2RlPC90ZXh0Pjx0ZXh0IHg9IjUwJSIgeT0iNTUlIiBmb250LXNpemU9IjE0IiBmaWxsPSIjMTBiOTgxIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+UXVldWVGbG93PC90ZXh0Pjwvc3ZnPg==';
                  }}
                />
                ) : (
                  <div className="w-72 h-72 md:w-80 md:h-80 mx-auto rounded-2xl shadow-lg bg-white flex items-center justify-center">
                    <div className="text-emerald-600">Đang tải QR Code...</div>
                  </div>
                )}
                
                {/* Animated border pulse */}
                {isQrHovered && (
                <motion.div
                    className="absolute inset-0 rounded-2xl border-4 border-emerald-400/60"
                    initial={{ opacity: 0, scale: 1 }}
                    animate={{ 
                      opacity: [0, 0.8, 0.6, 0.8, 0],
                      scale: [1, 1.05, 1]
                    }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                )}
              </motion.div>

              {/* Interactive floating icons */}
              <AnimatePresence>
                {isQrHovered && (
                  <>
                    {[
                      { icon: '📱', pos: { top: '-12px', left: '-12px' } },
                      { icon: '⚡', pos: { top: '-12px', right: '-12px' } },
                      { icon: '🎯', pos: { bottom: '-12px', left: '-12px' } },
                      { icon: '✨', pos: { bottom: '-12px', right: '-12px' } }
                    ].map((item, index) => (
                      <motion.div
                        key={index}
                        className="absolute text-2xl pointer-events-none"
                        style={item.pos}
                        initial={{ opacity: 0, scale: 0, rotate: -90 }}
                        animate={{ opacity: 1, scale: 1, rotate: 0 }}
                        exit={{ opacity: 0, scale: 0, rotate: 90 }}
                        transition={{ duration: 0.3, delay: index * 0.05 }}
                      >
                        {item.icon}
                      </motion.div>
                    ))}
                  </>
                )}
              </AnimatePresence>
            </motion.div>
          </motion.div>

          {/* Instructions */}
          <motion.div
            variants={itemVariants}
            className="mb-8"
          >
            <h2 className="text-2xl md:text-3xl font-bold text-emerald-800 mb-4">
              Quét mã QR để truy cập hệ thống
            </h2>
            <p className="text-emerald-700 text-base md:text-lg max-w-lg mx-auto leading-relaxed">
              Sử dụng camera điện thoại để quét mã QR hoặc nhấn nút bên dưới để truy cập trực tiếp
            </p>
          </motion.div>
        </motion.div>
      </div>

      {/* Direct Access Button */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="relative z-10 text-center pb-16"
      >
        <motion.button
          onClick={handleDirectAccess}
          className="px-12 py-4 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-600 hover:via-teal-600 hover:to-cyan-600 text-white text-lg font-bold rounded-2xl shadow-xl transition-all duration-300 border-2 border-white/30"
          whileHover={{ 
            scale: 1.05, 
            y: -4,
            boxShadow: "0 20px 40px rgba(16, 185, 129, 0.4)"
          }}
          whileTap={{ scale: 0.95 }}
        >
          <div className="flex items-center justify-center space-x-3">
            <motion.span
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              🚀
            </motion.span>
            <span>Truy cập trực tiếp hệ thống</span>
            <motion.span
              animate={{ x: [0, 6, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              →
            </motion.span>
          </div>
        </motion.button>
      </motion.div>
    </div>
  );
};

export default PublicDisplay;

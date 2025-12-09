import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import ApiService from '../../../shared/api';

const CustomerFeedbackPage = () => {
  const { ticketId } = useParams();
  const navigate = useNavigate();
  
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState({
    overallRating: 0,
    hasComplaint: false,
    complaintDescription: ''
  });
  const [errors, setErrors] = useState({});
  const [submitted, setSubmitted] = useState(false);

  // Load ticket info
  useEffect(() => {
    const fetchTicket = async () => {
      try {
        const data = await ApiService.getTicketStatus(ticketId);
        setTicket(data);
      } catch (error) {
        console.error('Error loading ticket:', error);
      } finally {
        setLoading(false);
      }
    };
    
    if (ticketId) {
      fetchTicket();
    }
  }, [ticketId]);

  // Handle rating change
  const handleRatingChange = (rating) => {
    setFeedback(prev => ({ ...prev, overallRating: rating }));
    
    // Clear error for this field
    if (errors.overallRating) {
      setErrors(prev => ({ ...prev, overallRating: null }));
    }
  };

  // Validate feedback
  const validateFeedback = () => {
    const newErrors = {};
    
    if (!feedback.overallRating) {
      newErrors.overallRating = 'Vui lòng đánh giá mức độ hài lòng';
    }
    
    if (feedback.hasComplaint && !feedback.complaintDescription.trim()) {
      newErrors.complaintDescription = 'Vui lòng mô tả chi tiết khiếu nại';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Submit feedback
  const handleSubmit = async () => {
    if (!validateFeedback()) return;
    
    try {
      setSubmitting(true);
      
      const feedbackData = {
        ticket_number: ticket.ticket_number,
        overall_rating: feedback.overallRating,
        review_comments: `Đánh giá ${feedback.overallRating} sao từ khách hàng`
      };
      
      // Submit feedback
      await ApiService.submitFeedback(feedbackData);
      
      // If has complaint, submit complaint separately
      if (feedback.hasComplaint) {
        const complaintData = {
          ticket_number: ticket.ticket_number,
          complaint_text: feedback.complaintDescription,
          customer_name: ticket.customer_name,
          customer_email: ticket.customer_email
        };
        await ApiService.submitComplaint(complaintData);
      }
      
      setSubmitted(true);
      
    } catch (error) {
      console.error('Error submitting feedback:', error);
      setErrors({ 
        submit: 'Có lỗi xảy ra khi gửi đánh giá. Vui lòng thử lại!' 
      });
    } finally {
      setSubmitting(false);
    }
  };

  // Star rating component with smooth animations
  const StarRating = ({ rating, onRatingChange, error, label }) => {
    const [hoverRating, setHoverRating] = useState(0);
    
    return (
      <div className="mb-6">
        <label className="block text-lg font-semibold text-gray-800 mb-4 text-center">
          {label} <span className="text-red-500">*</span>
        </label>
        <div className="flex justify-center space-x-2 mb-3">
          {[1, 2, 3, 4, 5].map((star) => (
            <motion.button
              key={star}
              type="button"
              onClick={() => onRatingChange(star)}
              onMouseEnter={() => setHoverRating(star)}
              onMouseLeave={() => setHoverRating(0)}
              whileHover={{ scale: 1.2 }}
              whileTap={{ scale: 0.9 }}
              className={`w-12 h-12 transition-all duration-300 ease-out ${
                star <= (hoverRating || rating) 
                  ? 'text-yellow-400 drop-shadow-md' 
                  : 'text-gray-300 hover:text-yellow-200'
              }`}
            >
              <motion.svg 
                fill="currentColor" 
                viewBox="0 0 20 20"
                animate={{ 
                  rotate: star <= (hoverRating || rating) ? [0, 10, 0] : 0 
                }}
                transition={{ duration: 0.3 }}
              >
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </motion.svg>
            </motion.button>
          ))}
        </div>
        <motion.div 
          className="flex justify-between text-sm text-gray-500 mb-2 px-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <span>Rất tệ</span>
          <span className="text-center">Bình thường</span>
          <span>Tuyệt vời</span>
        </motion.div>
        {rating > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mt-2"
          >
            <span className="text-sm font-medium text-blue-600">
              {rating === 1 && "😞 Rất không hài lòng"}
              {rating === 2 && "😐 Không hài lòng"}
              {rating === 3 && "😊 Bình thường"}
              {rating === 4 && "😄 Hài lòng"}
              {rating === 5 && "🌟 Rất hài lòng"}
            </span>
          </motion.div>
        )}
        <AnimatePresence>
          {error && (
            <motion.p 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-red-500 text-sm mt-2 text-center"
            >
              {error}
            </motion.p>
          )}
        </AnimatePresence>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center">
        <motion.div 
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <motion.div 
            className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full mx-auto mb-6"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          />
          <motion.p 
            className="text-gray-600 text-lg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            Đang tải thông tin...
          </motion.p>
        </motion.div>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center">
        <motion.div 
          className="max-w-md mx-auto text-center p-8"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <motion.div 
            className="w-20 h-20 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
          >
            <motion.svg 
              className="w-10 h-10 text-white" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ delay: 0.5, duration: 0.5 }}
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </motion.svg>
          </motion.div>
          
          <motion.h1 
            className="text-3xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent mb-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            Cảm ơn bạn! 🎉
          </motion.h1>
          <motion.p 
            className="text-gray-600 mb-8 text-lg leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            Cảm ơn bạn đã dành thời gian đánh giá dịch vụ của chúng tôi. 
            Phản hồi của bạn sẽ giúp chúng tôi cải thiện chất lượng phục vụ.
          </motion.p>
          
          <motion.div 
            className="space-y-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <motion.button
              onClick={() => navigator.share && navigator.share({
                title: 'Đánh giá dịch vụ',
                text: `Tôi vừa sử dụng dịch vụ ${ticket?.service_name} và đánh giá ${feedback.overallRating}/5 sao!`,
                url: window.location.origin
              })}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all duration-300 shadow-lg hover:shadow-xl font-medium"
            >
              📤 Chia sẻ đánh giá
            </motion.button>
            
            <motion.button
              onClick={() => navigate('/service-registration')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-4 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl hover:from-green-600 hover:to-green-700 transition-all duration-300 shadow-lg hover:shadow-xl font-medium"
            >
              ➕ Tạo yêu cầu mới
            </motion.button>
            
            <motion.button
              onClick={() => navigate('/')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-4 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 hover:border-gray-400 transition-all duration-300 font-medium"
            >
              🏠 Về trang chủ
            </motion.button>
          </motion.div>
        </motion.div>
      </div>
    );
  }

  return (
    <motion.div 
      className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      {/* Header */}
      <motion.div 
        className="bg-white shadow-sm border-b border-gray-100"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="text-center">
            <motion.h1 
              className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              Đánh giá dịch vụ ⭐
            </motion.h1>
            <motion.p 
              className="text-gray-600 mt-2 text-lg"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              Chia sẻ trải nghiệm của bạn để giúp chúng tôi cải thiện
            </motion.p>
          </div>
        </div>
      </motion.div>

      <div className="max-w-3xl mx-auto px-4 py-8">
        {/* Service Summary */}
        {ticket && (
          <motion.div 
            className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-8"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="text-center">
              <motion.div 
                className="w-20 h-20 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.4, type: "spring", stiffness: 200 }}
              >
                <motion.svg 
                  className="w-10 h-10 text-white" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.6 }}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </motion.svg>
              </motion.div>
              <motion.h2 
                className="text-2xl font-bold text-gray-900 mb-3"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                Hoàn thành dịch vụ
              </motion.h2>
              <motion.p 
                className="text-xl text-blue-600 font-semibold mb-2"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                {ticket.service_name}
              </motion.p>
              <motion.p 
                className="text-gray-600 mb-4"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
              >
                {ticket.department_name}
              </motion.p>
              <motion.div 
                className="flex items-center justify-center space-x-4 text-sm text-gray-500 bg-gray-50 rounded-lg py-3 px-6 inline-flex"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
              >
                <span className="font-medium">Mã số: #{ticket.ticket_number}</span>
                <span>•</span>
                <span>{new Date().toLocaleDateString('vi-VN')}</span>
              </motion.div>
            </div>
          </motion.div>
        )}

        {/* Feedback Form */}
        <motion.div 
          className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <AnimatePresence>
            {errors.submit && (
              <motion.div 
                className="mb-8 bg-red-50 border-l-4 border-red-400 p-4 rounded-r-xl"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <p className="text-red-700 font-medium">{errors.submit}</p>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="space-y-8">
            {/* Đánh giá mức độ hài lòng */}
            <motion.div 
              className="text-center bg-gradient-to-r from-blue-50 to-green-50 rounded-xl p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <StarRating
                rating={feedback.overallRating}
                onRatingChange={(rating) => handleRatingChange(rating)}
                error={errors.overallRating}
                label="Mức độ hài lòng về dịch vụ"
              />
            </motion.div>

            {/* Complaint Section */}
            <motion.div 
              className="border-t border-gray-200 pt-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
            >
              <div className="flex items-center space-x-3 mb-6">
                <motion.input
                  type="checkbox"
                  id="hasComplaint"
                  checked={feedback.hasComplaint}
                  onChange={(e) => setFeedback(prev => ({ 
                    ...prev, 
                    hasComplaint: e.target.checked,
                    complaintDescription: e.target.checked ? prev.complaintDescription : ''
                  }))}
                  className="w-5 h-5 text-red-600 bg-gray-100 border-gray-300 rounded focus:ring-red-500"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                />
                <label htmlFor="hasComplaint" className="text-base font-medium text-gray-700">
                  Tôi có khiếu nại về dịch vụ này
                </label>
              </div>

              <AnimatePresence>
                {feedback.hasComplaint && (
                  <motion.div 
                    className="bg-red-50 border border-red-200 p-6 rounded-xl space-y-6"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div>
                      <label className="block text-base font-medium text-red-700 mb-3">
                        Mô tả chi tiết khiếu nại <span className="text-red-500">*</span>
                      </label>
                      <motion.textarea
                        value={feedback.complaintDescription}
                        onChange={(e) => setFeedback(prev => ({ ...prev, complaintDescription: e.target.value }))}
                        rows="4"
                        className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 text-base ${
                          errors.complaintDescription ? 'border-red-300' : 'border-red-300'
                        }`}
                        placeholder="Vui lòng mô tả chi tiết vấn đề bạn gặp phải..."
                        whileFocus={{ scale: 1.02 }}
                      />
                      <AnimatePresence>
                        {errors.complaintDescription && (
                          <motion.p 
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="text-red-500 text-sm mt-2"
                          >
                            {errors.complaintDescription}
                          </motion.p>
                        )}
                      </AnimatePresence>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Submit Button */}
            <motion.div 
              className="flex justify-end space-x-4 pt-8 border-t border-gray-200"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 }}
            >
              <motion.button
                onClick={() => navigate('/display')}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-8 py-3 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 hover:border-gray-400 transition-all duration-300 font-medium"
              >
                Bỏ qua
              </motion.button>
              <motion.button
                onClick={handleSubmit}
                disabled={submitting}
                whileHover={{ scale: submitting ? 1 : 1.02 }}
                whileTap={{ scale: submitting ? 1 : 0.98 }}
                className="px-8 py-3 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-xl hover:from-green-600 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 font-medium shadow-lg hover:shadow-xl flex items-center"
              >
                {submitting ? (
                  <>
                    <motion.div 
                      className="w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-3"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    />
                    Đang gửi...
                  </>
                ) : (
                  <>
                    <motion.svg 
                      className="w-5 h-5 mr-2" 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                      whileHover={{ x: 2 }}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </motion.svg>
                    Gửi đánh giá
                  </>
                )}
              </motion.button>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default CustomerFeedbackPage;
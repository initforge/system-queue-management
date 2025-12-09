import React, { useState } from 'react';
import { motion } from 'framer-motion';

const FAQSection = ({ faqs = [] }) => {
  const [openIndex, setOpenIndex] = useState(null);

  const defaultFAQs = [
    {
      id: 1,
      question: 'Làm thế nào để xin nghỉ phép?',
      answer: 'Bạn có thể xin nghỉ phép bằng cách vào mục "Ca làm việc" > "Xin nghỉ phép" và điền đầy đủ thông tin yêu cầu.'
    },
    {
      id: 2,
      question: 'Làm sao để xem lịch làm việc của tôi?',
      answer: 'Vào mục "Ca làm việc" để xem lịch làm việc tuần hiện tại và các tuần tiếp theo.'
    },
    {
      id: 3,
      question: 'Tôi có thể đổi ca làm việc không?',
      answer: 'Hiện tại tính năng đổi ca đang được phát triển. Vui lòng liên hệ quản lý để được hỗ trợ.'
    },
    {
      id: 4,
      question: 'Làm thế nào để xem thống kê hiệu suất?',
      answer: 'Vào mục "Ca làm việc" > "Thống kê cá nhân" để xem các thống kê về điểm danh và hiệu suất làm việc.'
    },
    {
      id: 5,
      question: 'AI Helper có thể giúp gì?',
      answer: 'AI Helper có thể trả lời các câu hỏi về hệ thống, hướng dẫn sử dụng, và cung cấp thông tin về lịch làm việc, thống kê của bạn.'
    }
  ];

  const displayFAQs = faqs.length > 0 ? faqs : defaultFAQs;

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
        <span className="mr-2">❓</span>
        Câu hỏi thường gặp (FAQ)
      </h3>
      
      <div className="space-y-3">
        {displayFAQs.map((faq, index) => (
          <motion.div
            key={faq.id || index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="border border-gray-200 rounded-lg overflow-hidden"
          >
            <button
              onClick={() => setOpenIndex(openIndex === index ? null : index)}
              className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <span className="font-medium text-gray-900">{faq.question}</span>
              <motion.svg
                animate={{ rotate: openIndex === index ? 180 : 0 }}
                transition={{ duration: 0.2 }}
                className="w-5 h-5 text-gray-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </motion.svg>
            </button>
            
            {openIndex === index && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="px-4 pb-3 text-gray-600 text-sm"
              >
                {faq.answer}
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default FAQSection;


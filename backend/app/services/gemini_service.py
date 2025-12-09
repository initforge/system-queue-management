"""
Gemini AI Service
Handles interactions with Google Gemini API
"""
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime

from ..core.config import settings

logger = logging.getLogger(__name__)

# Try to import google.generativeai, handle gracefully if not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    logger.warning("google-generativeai package not installed. AI features will be disabled.")
    genai = None
    GEMINI_AVAILABLE = False

class GeminiService:
    def __init__(self):
        """Initialize Gemini client with API key"""
        if not GEMINI_AVAILABLE:
            logger.warning("google-generativeai package not available. AI features will be disabled.")
            self.client = None
            return
            
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not configured. AI features will be disabled.")
            self.client = None
            return
        
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.client = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("Gemini AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            self.client = None
    
    def generate_response(
        self,
        user_message: str,
        context: Dict[str, Any] = None,
        user_role: str = 'staff',
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response based on user message and context
        
        Args:
            user_message: User's input message
            context: Context data (user info, system data, etc.)
            user_role: User role (staff, manager, admin)
            conversation_history: Previous messages in conversation
        
        Returns:
            Dict with 'message', 'sources', 'function_calls' etc.
        """
        if not self.client:
            return {
                "message": "Xin lỗi, dịch vụ AI hiện không khả dụng. Vui lòng liên hệ quản trị viên.",
                "error": "AI service not configured"
            }
        
        try:
            # Build system prompt based on user role
            system_prompt = self._build_system_prompt(user_role, context or {})
            
            # Build messages list for Gemini API
            messages = []
            
            # Add system instruction as first message
            messages.append(system_prompt)
            
            # Add conversation history
            for msg in (conversation_history or [])[-10:]:  # Keep last 10 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role == 'user':
                    messages.append(f"User: {content}")
                elif role == 'assistant':
                    messages.append(f"Assistant: {content}")
            
            # Add current user message
            messages.append(f"User: {user_message}")
            messages.append("Assistant:")
            
            # Join all messages
            full_prompt = "\n".join(messages)
            
            # Generate response using the full prompt
            # Gemini API expects string or list of content parts
            response = self.client.generate_content(full_prompt)
            
            # Extract text from response - handle different response formats
            if hasattr(response, 'text'):
                response_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                response_text = response.candidates[0].content.parts[0].text
            else:
                response_text = str(response)
            
            return {
                "message": response_text,
                "timestamp": datetime.now().isoformat(),
                "model": "gemini-2.0-flash"
            }
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            return {
                "message": f"Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: {str(e)}",
                "error": str(e)
            }
    
    def _build_system_prompt(self, user_role: str, context: Dict) -> str:
        """Build system prompt based on user role and context"""
        base_prompt = f"""Bạn là AI Helper cho hệ thống Quản lý hàng đợi (Queue Management System).

Người dùng hiện tại có vai trò: {user_role}

"""
        
        if user_role == 'manager':
            base_prompt += """Với vai trò Manager, bạn có thể:
- Xem thống kê và dữ liệu của toàn bộ nhân viên trong phòng ban
- Xem lịch làm việc của tất cả nhân viên
- Xem hiệu suất làm việc của nhân viên
- Đưa ra các đề xuất về quản lý và tối ưu hóa

"""
        else:
            base_prompt += """Với vai trò Staff, bạn có thể:
- Xem thông tin cá nhân của chính mình
- Xem lịch làm việc của bản thân
- Xem thống kê hiệu suất của bản thân
- Được hướng dẫn sử dụng hệ thống

"""
        
        base_prompt += """Hãy trả lời một cách thân thiện, chuyên nghiệp và hữu ích bằng tiếng Việt.
Nếu được hỏi về dữ liệu cụ thể, hãy đề xuất sử dụng các function calls nếu cần.
"""
        
        if context:
            base_prompt += f"\nThông tin ngữ cảnh hiện tại:\n"
            if 'user' in context:
                base_prompt += f"- Tên người dùng: {context['user'].get('full_name', 'N/A')}\n"
            if 'department' in context:
                base_prompt += f"- Phòng ban: {context['department'].get('name', 'N/A')}\n"
        
        return base_prompt
    
    def _build_conversation(
        self,
        system_prompt: str,
        history: List[Dict],
        current_message: str
    ) -> str:
        """Build conversation string from history and current message"""
        conversation = system_prompt + "\n\n"
        
        for msg in history[-10:]:  # Keep last 10 messages for context
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'user':
                conversation += f"Người dùng: {content}\n"
            elif role == 'assistant':
                conversation += f"AI: {content}\n"
        
        conversation += f"\nNgười dùng: {current_message}\nAI:"
        
        return conversation

# Singleton instance
gemini_service = GeminiService()


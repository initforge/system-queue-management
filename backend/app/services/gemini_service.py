"""
Gemini AI Service
Handles interactions with Google Gemini API with Function Calling support
"""
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Try to import google.generativeai
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    logger.warning("google-generativeai package not installed. AI features will be disabled.")
    genai = None
    GEMINI_AVAILABLE = False

# Models to try in order (newest to oldest for fallback)
MODELS_TO_TRY = [
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]


class GeminiService:
    """Gemini AI Service with Function Calling support"""
    
    def __init__(self):
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini AI not available")
    
    def generate_response(
        self,
        user_message: str,
        api_key: str,
        context: Dict[str, Any] = None,
        user_role: str = 'staff',
        conversation_history: List[Dict] = None,
        ai_functions=None  # AIFunctions instance for executing functions
    ) -> Dict[str, Any]:
        """Generate AI response with function calling support"""
        
        if not GEMINI_AVAILABLE:
            return {
                "message": "Dịch vụ AI không khả dụng.",
                "error": "AI service not available"
            }
        
        if not api_key or not api_key.strip():
            return {
                "message": "Vui lòng cung cấp API key.",
                "error": "API key required"
            }
        
        # Configure API
        genai.configure(api_key=api_key.strip())
        
        # Build system prompt
        system_prompt = self._build_system_prompt(user_role, context or {})
        
        # Build tools for function calling
        tools = self._build_tools(user_role)
        
        # Try models with fallback
        last_error = None
        
        for model_name in MODELS_TO_TRY:
            try:
                logger.info(f"Trying model: {model_name}")
                
                # TEMPORARILY DISABLED FUNCTION CALLING - AI responds without tools
                # TODO: Fix tool format and re-enable
                model = genai.GenerativeModel(
                    model_name,
                    system_instruction=system_prompt
                    # tools disabled temporarily
                )
                
                # Build chat history
                chat_history = self._build_chat_history(conversation_history)
                
                # Start chat and send message
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(user_message)
                
                # Extract text response (function calling disabled)
                response_text = self._extract_text(response)
                
                logger.info(f"Success with model: {model_name}")
                
                return {
                    "message": response_text,
                    "timestamp": datetime.now().isoformat(),
                    "model": model_name
                }
                
            except Exception as e:
                error_str = str(e)
                logger.warning(f"Model {model_name} failed: {error_str}")
                last_error = error_str
                
                # Retry on rate limit or model not found
                if any(x in error_str.lower() for x in ['429', 'quota', 'rate limit', '404', 'not found']):
                    continue
                break
        
        # All models failed
        return self._handle_error(last_error)
    
    def _build_system_prompt(self, user_role: str, context: Dict) -> str:
        """Build system instruction for the AI"""
        user_info = context.get('user', {})
        department = context.get('department', {})
        
        prompt = f"""Bạn là AI Helper của hệ thống QStream - Quản lý hàng đợi thông minh.

THÔNG TIN NGƯỜI DÙNG:
- Tên: {user_info.get('full_name', 'N/A')}
- Username: {user_info.get('username', 'N/A')}
- Vai trò: {user_role}
- Phòng ban: {department.get('name', 'N/A')}

HỆ THỐNG QSTREAM CÓ CÁC TÍNH NĂNG:
1. Quản lý hàng đợi - Gọi phiếu, phục vụ khách hàng
2. Lịch làm việc - Xem ca làm việc được phân công
3. Hiệu suất - Xem thống kê phục vụ và đánh giá

HƯỚNG DẪN TRẢ LỜI:
- Trả lời thân thiện, ngắn gọn bằng tiếng Việt
- Hướng dẫn người dùng cách sử dụng hệ thống
- Nếu người dùng hỏi về dữ liệu cụ thể (số khách, lịch, hiệu suất), hướng dẫn họ xem trực tiếp trên dashboard hoặc tab tương ứng
- Không bịa số liệu khi không có thông tin
"""
        
        if user_role == 'manager':
            prompt += """
BẠN ĐANG HỖ TRỢ QUẢN LÝ, CÓ THÊM QUYỀN:
- Xem thông tin tất cả nhân viên
- Phân ca làm việc
- Xem báo cáo phòng ban
"""
        
        return prompt
    
    def _build_tools(self, user_role: str):
        """Build tool definitions for function calling"""
        from .ai_functions import TOOL_DECLARATIONS
        
        # Filter tools based on role
        allowed_tools = TOOL_DECLARATIONS.copy()
        
        if user_role != 'manager':
            # Remove manager-only tools for staff
            manager_only = ['get_department_stats', 'get_all_staff_status']
            allowed_tools = [t for t in allowed_tools if t['name'] not in manager_only]
        
        # Return in Gemini API format - list of function declarations
        # Gemini SDK accepts list of dicts directly as tools
        if not allowed_tools:
            return None
        
        return allowed_tools
    
    def _build_chat_history(self, conversation_history: List[Dict] = None) -> List:
        """Build chat history for Gemini"""
        history = []
        
        for msg in (conversation_history or [])[-10:]:
            role = msg.get('role', 'user')
            content = msg.get('content', msg.get('message', ''))
            
            gemini_role = 'user' if role == 'user' else 'model'
            history.append({
                'role': gemini_role,
                'parts': [content]
            })
        
        return history
    
    def _extract_text(self, response) -> str:
        """Extract text from Gemini response"""
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'candidates') and response.candidates:
            parts = response.candidates[0].content.parts
            texts = [p.text for p in parts if hasattr(p, 'text')]
            return '\n'.join(texts) if texts else str(response)
        return str(response)
    
    def _handle_error(self, error: str) -> Dict[str, Any]:
        """Handle errors and return appropriate response"""
        if not error:
            error = "Unknown error"
        
        if '429' in error or 'quota' in error.lower():
            return {
                "message": "⚠️ Đã vượt quá giới hạn API. Vui lòng đợi vài phút rồi thử lại.",
                "error": "RATE_LIMIT_EXCEEDED"
            }
        
        if '403' in error or 'API key' in error:
            return {
                "message": "API key không hợp lệ. Vui lòng kiểm tra lại.",
                "error": "INVALID_API_KEY"
            }
        
        return {
            "message": f"Đã xảy ra lỗi: {error}",
            "error": error
        }


# Service instance
gemini_service = GeminiService()

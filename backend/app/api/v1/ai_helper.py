"""
AI Helper API endpoints
Handles AI-powered chat interactions using Gemini
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
import uuid
import logging
import re

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.services.gemini_service import gemini_service

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[dict] = None
    api_key: Optional[str] = None  # User-provided Gemini API key
    mode: Optional[str] = "sql"  # "sql" or "chat" mode

class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    timestamp: str
    error: Optional[str] = None
    sql_query: Optional[str] = None  # The SQL query executed
    query_result: Optional[list] = None  # Query execution result

@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_data: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send message to AI Helper with SQL generation support"""
    try:
        from app.services.ai_functions import AIFunctions
        from app.utils.sql_validator import SQLValidator
        
        # Get or create conversation ID
        conversation_id = chat_data.conversation_id or str(uuid.uuid4())
        
        # Mode: "sql" or "chat"
        sql_mode = chat_data.mode == "sql"
        
        # For now, without AIConversation model, we maintain conversation in memory
        # You can implement conversation storage later if needed
        history_list = []
        
        # Build context
        context = {
            'user': {
                'id': current_user.id,
                'full_name': current_user.full_name,
                'username': current_user.username,
                'role': current_user.role,
                'department_id': current_user.department_id
            }
        }
        
        if current_user.department:
            context['department'] = {
                'id': current_user.department.id,
                'name': current_user.department.name
            }
        
        # Check API key
        if not chat_data.api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key is required."
            )
        
        # Create AI Functions instance for database queries
        ai_functions = AIFunctions(
            db=db,
            user_id=current_user.id,
            user_role=current_user.role,
            department_id=current_user.department_id
        )
        
        # Generate AI response with optional SQL mode
        response = gemini_service.generate_response(
            user_message=chat_data.message,
            api_key=chat_data.api_key,
            context=context,
            user_role=current_user.role,
            conversation_history=history_list,
            ai_functions=ai_functions,
            sql_mode=sql_mode
        )
        
        sql_query = None
        query_result = None
        ai_raw_response = response.get('message', '')
        
        # If SQL mode, extract and execute query
        if sql_mode:
            sql_query = extract_sql_from_response(ai_raw_response)
            
            # Remove SQL code block from display message
            final_message = remove_sql_block(ai_raw_response)
            
            if sql_query:
                # Validate SQL
                is_valid, error_msg = SQLValidator.validate(sql_query)
                
                if not is_valid:
                    final_message = f"⚠️ Query không hợp lệ: {error_msg}\n\n{final_message}"
                else:
                    # Add LIMIT
                    sql_query = SQLValidator.add_limit(sql_query, max_rows=100)
                    
                    # Execute query
                    try:
                        result = db.execute(text(sql_query)).fetchall()
                        query_result = [dict(row._mapping) for row in result]
                        
                        # Format result into message
                        if query_result:
                            result_text = format_query_result(query_result, chat_data.message)
                            final_message = f"{final_message}\n\n{result_text}"
                        else:
                            final_message = f"{final_message}\n\n📊 Không tìm thấy dữ liệu."
                            
                    except Exception as e:
                        logger.error(f"SQL execution error: {e}")
                        final_message = f"{final_message}\n\n❌ Lỗi truy vấn dữ liệu: {str(e)}"
            else:
                # No SQL query generated, use AI response as-is
                final_message = ai_raw_response
        else:
            # Chat mode, use response as-is
            final_message = ai_raw_response
        
        return ChatResponse(
            message=final_message,
            conversation_id=conversation_id,
            timestamp=response.get('timestamp', ''),
            error=response.get('error'),
            sql_query=sql_query,
            query_result=query_result
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )


def extract_sql_from_response(response_text: str) -> Optional[str]:
    """Extract SQL query from AI response (from ```sql ... ``` blocks)"""
    pattern = r'```sql\s*(.*?)\s*```'
    matches = re.findall(pattern, response_text, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[0].strip()
    return None


def remove_sql_block(response_text: str) -> str:
    """Remove SQL code blocks from response text for cleaner display"""
    # Remove ```sql ... ``` blocks
    pattern = r'```sql\s*.*?\s*```'
    cleaned = re.sub(pattern, '', response_text, flags=re.DOTALL | re.IGNORECASE)
    # Clean up extra newlines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def format_query_result(results: list, user_question: str = "", max_rows: int = 10) -> str:
    """Format query results into beautiful readable text"""
    if not results:
        return "📊 Không có dữ liệu"
    
    # Limit display rows
    display_results = results[:max_rows]
    total = len(results)
    
    # Detect result type and format accordingly
    first_row = results[0]
    
    # Single count/aggregate result
    if len(first_row) == 1 and list(first_row.keys())[0] in ['count', 'total', 'avg', 'sum', 'max', 'min']:
        key = list(first_row.keys())[0]
        value = first_row[key]
        if key == 'count' or key == 'total':
            return f"📊 **Kết quả:** {value} "
        elif key == 'avg':
            return f"📊 **Trung bình:** {value:.2f}"
        else:
            return f"📊 **{key.upper()}:** {value}"
    
    # Multiple rows - format as clean list
    lines = []
    for i, row in enumerate(display_results, 1):
        # Try to find name/title field
        name_field = None
        for key in ['full_name', 'name', 'username', 'ticket_number', 'customer_name']:
            if key in row:
                name_field = key
                break
        
        if name_field:
            # Show name prominently
            name = row[name_field]
            other_fields = [f"{k}: {v}" for k, v in row.items() if k != name_field and v is not None]
            if other_fields:
                lines.append(f"{i}. **{name}** - {', '.join(other_fields)}")
            else:
                lines.append(f"{i}. **{name}**")
        else:
            # Generic format
            fields = [f"{k}: {v}" for k, v in row.items() if v is not None]
            lines.append(f"{i}. {' | '.join(fields)}")
    
    formatted = "📊 **Kết quả:**\n" + "\n".join(lines)
    
    if total > max_rows:
        formatted += f"\n\n_Hiển thị {max_rows}/{total} kết quả_"
    
    return formatted


@router.get("/conversations")
async def get_conversations(
    conversation_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversation history (placeholder - implement with proper storage if needed)"""
    try:
        # Placeholder - conversation history not stored without AIConversation model
        return []
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving conversations"
        )

@router.get("/context")
async def get_context(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get basic context data for AI Helper (data queries via function calling)"""
    try:
        context = {
            "user": {
                "id": current_user.id,
                "full_name": current_user.full_name,
                "username": current_user.username,
                "role": current_user.role,
                "department_id": current_user.department_id
            }
        }
        
        if current_user.department:
            context["department"] = {
                "id": current_user.department.id,
                "name": current_user.department.name
            }
        
        return context
        
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving context"
        )



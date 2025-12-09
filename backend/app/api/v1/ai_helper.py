"""
AI Helper API endpoints
Handles AI-powered chat interactions using Gemini
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, AIConversation
from app.services.gemini_service import gemini_service

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    timestamp: str
    error: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_data: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send message to AI Helper"""
    try:
        # Get or create conversation ID
        conversation_id = chat_data.conversation_id or str(uuid.uuid4())
        
        # Get conversation history
        history = db.query(AIConversation).filter(
            AIConversation.conversation_id == conversation_id,
            AIConversation.user_id == current_user.id
        ).order_by(AIConversation.created_at).all()
        
        history_list = [
            {"role": msg.role, "content": msg.message}
            for msg in history[-10:]  # Last 10 messages
        ]
        
        # Build context
        context = chat_data.context or {}
        if not context.get('user'):
            context['user'] = {
                'id': current_user.id,
                'full_name': current_user.full_name,
                'role': current_user.role,
                'department_id': current_user.department_id
            }
        
        # Generate AI response
        response = gemini_service.generate_response(
            user_message=chat_data.message,
            context=context,
            user_role=current_user.role,
            conversation_history=history_list
        )
        
        # Save user message
        user_msg = AIConversation(
            user_id=current_user.id,
            conversation_id=conversation_id,
            role='user',
            message=chat_data.message,
            context_data=context
        )
        db.add(user_msg)
        
        # Save AI response
        ai_msg = AIConversation(
            user_id=current_user.id,
            conversation_id=conversation_id,
            role='assistant',
            message=response.get('message', ''),
            context_data=context
        )
        db.add(ai_msg)
        db.commit()
        
        return ChatResponse(
            message=response.get('message', ''),
            conversation_id=conversation_id,
            timestamp=response.get('timestamp', ''),
            error=response.get('error')
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )

@router.get("/conversations")
async def get_conversations(
    conversation_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversation history"""
    try:
        query = db.query(AIConversation).filter(
            AIConversation.user_id == current_user.id
        )
        
        if conversation_id:
            query = query.filter(AIConversation.conversation_id == conversation_id)
        
        conversations = query.order_by(AIConversation.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "role": msg.role,
                "message": msg.message,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            }
            for msg in reversed(conversations)
        ]
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
    """Get available context data for AI Helper"""
    try:
        context = {
            "user": {
                "id": current_user.id,
                "full_name": current_user.full_name,
                "role": current_user.role,
                "department_id": current_user.department_id
            }
        }
        
        # Add department info if available
        if current_user.department:
            context["department"] = {
                "id": current_user.department.id,
                "name": current_user.department.name,
                "code": current_user.department.code
            }
        
        return context
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving context"
        )


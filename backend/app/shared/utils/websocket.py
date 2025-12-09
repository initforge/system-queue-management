from fastapi import WebSocket
from typing import Dict, List, Set
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        # Queue WebSocket connections
        self.active_connections: Dict[str, WebSocket] = {}
        self.queue_subscribers: Dict[str, List[str]] = {}  # ticket_id -> [client_ids]
        self.client_tickets: Dict[str, str] = {}  # client_id -> ticket_id
        
        # Schedule WebSocket connections
        self.schedule_connections: Dict[str, Set[WebSocket]] = {
            "managers": set(),
            "staff": set()
        }
        self.connection_info: Dict[WebSocket, Dict] = {}
        
    # ==================== QUEUE WEBSOCKET METHODS ====================
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
    async def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
        # Remove from queue subscriptions
        if client_id in self.client_tickets:
            ticket_id = self.client_tickets[client_id]
            if ticket_id in self.queue_subscribers:
                self.queue_subscribers[ticket_id].remove(client_id)
                if not self.queue_subscribers[ticket_id]:
                    del self.queue_subscribers[ticket_id]
            del self.client_tickets[client_id]
    
    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_text(message)
            except:
                await self.disconnect(client_id)
    
    async def broadcast_to_queue(self, message: str, ticket_id: str):
        if ticket_id in self.queue_subscribers:
            for client_id in self.queue_subscribers[ticket_id][:]:  # Copy to avoid modification during iteration
                await self.send_personal_message(message, client_id)
    
    async def broadcast_to_all(self, message: str):
        for client_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, client_id)
    
    async def join_queue(self, client_id: str, ticket_id: str):
        if ticket_id not in self.queue_subscribers:
            self.queue_subscribers[ticket_id] = []
        
        if client_id not in self.queue_subscribers[ticket_id]:
            self.queue_subscribers[ticket_id].append(client_id)
            
        self.client_tickets[client_id] = ticket_id
        
        # Send initial queue status
        await self.send_queue_update(ticket_id)
    
    async def leave_queue(self, client_id: str):
        if client_id in self.client_tickets:
            ticket_id = self.client_tickets[client_id]
            if ticket_id in self.queue_subscribers:
                self.queue_subscribers[ticket_id].remove(client_id)
                if not self.queue_subscribers[ticket_id]:
                    del self.queue_subscribers[ticket_id]
            del self.client_tickets[client_id]
    
    async def send_queue_update(self, ticket_id: str, position: int = None, estimated_wait: int = None):
        # Send actual queue data
        update_message = {
            "type": "queue_update",
            "ticket_id": ticket_id,
            "position": position,
            "estimated_wait": estimated_wait,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self.broadcast_to_queue(json.dumps(update_message), ticket_id)
    
    async def send_ticket_called(self, ticket_id: str, counter_name: str):
        message = {
            "type": "ticket_called",
            "ticket_id": ticket_id,
            "counter": counter_name,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self.broadcast_to_queue(json.dumps(message), ticket_id)
    
    async def send_queue_status(self, ticket_id: str, status_data: dict):
        message = {
            "type": "queue_status",
            "ticket_id": ticket_id,
            "data": status_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self.broadcast_to_queue(json.dumps(message), ticket_id)

    # ==================== SCHEDULE WEBSOCKET METHODS ====================
    
    async def schedule_connect(self, websocket: WebSocket, user_id: int, user_role: str, department_id: int = None):
        """Connect a new Schedule WebSocket client"""
        await websocket.accept()
        
        # Store connection info
        self.connection_info[websocket] = {
            "user_id": user_id,
            "user_role": user_role,
            "department_id": department_id,
            "connected_at": datetime.now()
        }
        
        # Add to appropriate group
        if user_role in ["manager", "admin"]:
            self.schedule_connections["managers"].add(websocket)
        else:
            self.schedule_connections["staff"].add(websocket)
            
        logger.info(f"Schedule WebSocket connected: User {user_id} ({user_role}) from department {department_id}")
        
        # Send welcome message
        await self.send_schedule_message(websocket, {
            "type": "connection_established",
            "message": "Connected to schedule management system",
            "timestamp": datetime.now().isoformat()
        })
    
    def schedule_disconnect(self, websocket: WebSocket):
        """Disconnect a Schedule WebSocket client"""
        if websocket in self.connection_info:
            user_info = self.connection_info[websocket]
            user_role = user_info.get("user_role")
            user_id = user_info.get("user_id")
            
            # Remove from appropriate group
            if user_role in ["manager", "admin"]:
                self.schedule_connections["managers"].discard(websocket)
            else:
                self.schedule_connections["staff"].discard(websocket)
            
            # Remove connection info
            del self.connection_info[websocket]
            
            logger.info(f"Schedule WebSocket disconnected: User {user_id} ({user_role})")

    async def send_schedule_message(self, websocket: WebSocket, message: dict):
        """Send message to specific schedule connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending schedule message: {e}")
            self.schedule_disconnect(websocket)

    async def broadcast_to_managers(self, message: dict, department_id: int = None):
        """Broadcast message to all managers"""
        disconnected = set()
        
        for websocket in self.schedule_connections["managers"].copy():
            try:
                conn_info = self.connection_info.get(websocket)
                if department_id is None or (conn_info and conn_info.get("department_id") == department_id):
                    await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to manager: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected:
            self.schedule_disconnect(websocket)

    async def broadcast_to_staff(self, message: dict, department_id: int = None, specific_staff: List[int] = None):
        """Broadcast message to staff"""
        disconnected = set()
        
        for websocket in self.schedule_connections["staff"].copy():
            try:
                conn_info = self.connection_info.get(websocket)
                if not conn_info:
                    continue
                    
                # Filter by department if specified
                if department_id is not None and conn_info.get("department_id") != department_id:
                    continue
                
                # Filter by specific staff IDs if specified
                if specific_staff is not None and conn_info.get("user_id") not in specific_staff:
                    continue
                
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to staff: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected:
            self.schedule_disconnect(websocket)

    # Schedule-specific notification methods
    async def notify_schedule_updated(self, schedule_data: dict, department_id: int = None):
        """Notify about schedule updates"""
        message = {
            "type": "schedule_updated",
            "data": schedule_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_to_managers(message, department_id)
        await self.broadcast_to_staff(message, department_id)

    async def notify_leave_request_submitted(self, leave_request_data: dict, department_id: int = None):
        """Notify managers about new leave requests"""
        message = {
            "type": "leave_request_submitted",
            "data": leave_request_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_to_managers(message, department_id)

    async def notify_leave_request_reviewed(self, leave_request_data: dict, staff_id: int):
        """Notify staff about leave request decision"""
        message = {
            "type": "leave_request_reviewed",
            "data": leave_request_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_to_staff(message, specific_staff=[staff_id])

    async def notify_checkin_request(self, checkin_data: dict, department_id: int = None):
        """Notify managers about check-in requests"""
        message = {
            "type": "checkin_request_submitted",
            "data": checkin_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_to_managers(message, department_id)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()

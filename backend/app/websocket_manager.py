from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.queue_subscribers: Dict[str, List[str]] = {}  # ticket_id -> [client_ids]
        self.client_tickets: Dict[str, str] = {}  # client_id -> ticket_id
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Add a new websocket connection to the manager"""
        try:
            self.active_connections[client_id] = websocket
            print(f"Added client {client_id} to active connections")
            print(f"Current active connections: {list(self.active_connections.keys())}")
            return True
        except Exception as e:
            print(f"Error connecting client {client_id}: {str(e)}")
            return False
        
    async def disconnect(self, client_id: str):
        """Remove a websocket connection from the manager"""
        try:
            if client_id in self.active_connections:
                # Get the websocket before removing it
                websocket = self.active_connections[client_id]
                
                # Remove from active connections first
                del self.active_connections[client_id]
                print(f"Removed client {client_id} from active connections")
                
                # Remove from queue subscriptions
                if client_id in self.client_tickets:
                    ticket_id = self.client_tickets[client_id]
                    if ticket_id in self.queue_subscribers:
                        if client_id in self.queue_subscribers[ticket_id]:
                            self.queue_subscribers[ticket_id].remove(client_id)
                        if not self.queue_subscribers[ticket_id]:
                            del self.queue_subscribers[ticket_id]
                    del self.client_tickets[client_id]
                    print(f"Removed client {client_id} from queue {ticket_id}")
                
                # Try to close the websocket connection only if it's still open
                try:
                    # Check WebSocket state before attempting to close
                    # States: CONNECTING=0, OPEN=1, CLOSING=2, CLOSED=3
                    if hasattr(websocket, 'client_state') and hasattr(websocket, 'application_state'):
                        from starlette.websockets import WebSocketState
                        # Only close if not already closing or closed
                        if websocket.client_state != WebSocketState.DISCONNECTED:
                            await websocket.close(code=1000)
                except Exception as e:
                    # Ignore errors when closing - connection may already be closed
                    print(f"WebSocket already closed for client {client_id}: {str(e)}")
                    
                print(f"Current active connections: {list(self.active_connections.keys())}")
                return True
            return False
        except Exception as e:
            print(f"Error disconnecting client {client_id}: {str(e)}")
            return False
    
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
    
    async def send_queue_update(self, ticket_id: str):
        # This would be called when queue status changes
        # You'll implement the actual queue status logic here
        update_message = {
            "type": "queue_update",
            "ticket_id": ticket_id,
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
    
    async def broadcast_queue_update(self, department_id: int):
        """Broadcast queue update to all staff dashboard connections"""
        message = {
            "type": "queue_update",
            "department_id": department_id,
            "action": "new_ticket",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Broadcast to all connected clients (staff dashboard)
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
                print(f"Sent queue update to client {client_id}")
            except Exception as e:
                print(f"Error sending queue update to {client_id}: {str(e)}")

    # Schedule-related methods
    schedule_connections: Dict[int, WebSocket] = {}  # user_id -> websocket
    
    async def schedule_connect(self, websocket: WebSocket, user_id: int, user_role: str, department_id: int = None):
        """Connect a schedule WebSocket"""
        await websocket.accept()
        self.schedule_connections[user_id] = websocket
        print(f"Schedule WebSocket connected for user {user_id} (role: {user_role})")
    
    def schedule_disconnect(self, websocket: WebSocket):
        """Disconnect a schedule WebSocket"""
        user_id_to_remove = None
        for user_id, ws in self.schedule_connections.items():
            if ws == websocket:
                user_id_to_remove = user_id
                break
        if user_id_to_remove:
            del self.schedule_connections[user_id_to_remove]
            print(f"Schedule WebSocket disconnected for user {user_id_to_remove}")
    
    async def send_schedule_message(self, websocket: WebSocket, message: dict):
        """Send a message to a specific schedule WebSocket"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending schedule message: {e}")
    
    async def notify_schedule_updated(self, schedule_data: dict, department_id: int = None):
        """Notify all connected schedule clients about an update"""
        message = {
            "type": "schedule_updated",
            "data": schedule_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        for user_id, websocket in list(self.schedule_connections.items()):
            try:
                await websocket.send_text(json.dumps(message))
                print(f"Sent schedule update to user {user_id}")
            except Exception as e:
                print(f"Error sending schedule update to user {user_id}: {e}")
                # Remove dead connections
                if user_id in self.schedule_connections:
                    del self.schedule_connections[user_id]

# Create a global instance
websocket_manager = WebSocketManager()


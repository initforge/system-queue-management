from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
from typing import List, Dict, Any
import json
import asyncio
from datetime import datetime
import redis.asyncio as redis

from .core.database import create_tables
from .core.config import settings
from .models import Base
from .websocket_manager import websocket_manager

# Redis connection
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL)
    
    # Create database tables
    create_tables()
    
    yield
    
    # Shutdown
    if redis_client:
        await redis_client.close()

# Create FastAPI app
app = FastAPI(
    title="Queue Management System",
    description="Smart Queue Management System for Government Agencies",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://frontend:3000"
]

# Add wildcard origins for development
if settings.DEBUG:
    origins.extend([
        "http://localhost",
        "http://127.0.0.1",
        "http://frontend"
    ])

print("Configured CORS origins:", origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily for debugging
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]
)

# Import and include API router
from .api.v1.api_router import api_router
app.include_router(api_router, prefix="/api/v1")

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    print(f"New WebSocket connection request from client {client_id}")
    
    try:
        # Accept connection first
        await websocket.accept()
        print(f"WebSocket connection accepted for client {client_id}")
        
        # Add to manager
        success = await websocket_manager.connect(websocket, client_id)
        if not success:
            print(f"Failed to add client {client_id} to manager")
            await websocket.close()
            return
            
        print(f"Client {client_id} successfully connected and added to manager")
        
        try:
            # Keep connection alive with message handling loop
            while True:
                # Wait for messages with a timeout to allow for periodic checks
                try:
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                    print(f"Received data from {client_id}: {data}")
                    
                    try:
                        message = json.loads(data)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from {client_id}: {data}")
                        continue
                        
                    msg_type = message.get("type")
                    print(f"Processing message type {msg_type} from {client_id}")
                    
                    if msg_type == "ping":
                        response = {
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket_manager.send_personal_message(
                            json.dumps(response),
                            client_id
                        )
                        
                    elif msg_type == "join_queue":
                        ticket_id = message.get("ticket_id")
                        if ticket_id:
                            success = await websocket_manager.join_queue(client_id, ticket_id)
                            if success:
                                response = {
                                    "type": "joined",
                                    "ticket_id": ticket_id
                                }
                                await websocket_manager.send_personal_message(
                                    json.dumps(response),
                                    client_id
                                )
                    
                except asyncio.TimeoutError:
                    # No message received in 60 seconds, connection is still alive
                    # Send a keep-alive ping from server
                    try:
                        await websocket.send_text(json.dumps({
                            "type": "server_ping",
                            "timestamp": datetime.now().isoformat()
                        }))
                    except:
                        # Connection is dead, break out of loop
                        print(f"Failed to send keep-alive to {client_id}")
                        break
                    continue
                
        except WebSocketDisconnect:
            print(f"Client {client_id} disconnected normally")
            
        except Exception as e:
            print(f"Error in message loop for {client_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected during setup")
        
    except Exception as e:
        print(f"Error in connection setup for {client_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        print(f"Cleaning up connection for {client_id}")
        await websocket_manager.disconnect(client_id)

# Utility function to broadcast queue updates
async def broadcast_queue_update(ticket_id: str, update_data: dict):
    """Broadcast real-time updates to queue subscribers"""
    message = json.dumps({
        "type": "queue_update",
        "ticket_id": ticket_id,
        "data": update_data,
        "timestamp": datetime.now().isoformat()
    })
    await websocket_manager.broadcast_to_queue(message, ticket_id)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Queue Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# API router already included above

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';

// ================== SCHEDULE WEBSOCKET SERVICE ==================
class ScheduleWebSocketService {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.listeners = {};
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.currentUser = null;
    }

    connect(userId, token) {
        try {
            this.currentUser = { id: userId, token };
            // Connect directly to backend WebSocket endpoint
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsBaseUrl = process.env.REACT_APP_WS_URL || `${wsProtocol}//localhost:8000/ws`;
            const wsUrl = `${wsBaseUrl}/${userId}`;
            
            console.log('Connecting to WebSocket:', wsUrl);
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = (event) => {
                console.log('Schedule WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000;
                
                this.send({
                    type: 'auth',
                    token: token
                });
                
                this.emit('connected', event);
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('Schedule WebSocket message received:', data);
                    
                    switch (data.type) {
                        case 'schedule_updated':
                            this.emit('scheduleUpdated', data.data);
                            break;
                        case 'shift_assigned_to_you':
                            this.emit('shiftAssigned', data.data);
                            break;
                        case 'leave_request_submitted':
                            this.emit('leaveRequestSubmitted', data.data);
                            break;
                        case 'leave_request_reviewed':
                            this.emit('leaveRequestReviewed', data.data);
                            break;
                        case 'shift_exchange_requested':
                            this.emit('shiftExchangeRequested', data.data);
                            break;
                        case 'shift_exchange_received':
                            this.emit('shiftExchangeReceived', data.data);
                            break;
                        case 'checkin_request_submitted':
                            this.emit('checkinRequestSubmitted', data.data);
                            break;
                        case 'checkin_approved':
                            this.emit('checkinApproved', data.data);
                            break;
                        case 'pong':
                            // No action needed for pong messages
                            break;
                        default:
                            this.emit('message', data);
                            break;
                    }
                } catch (error) {
                    console.error('Error parsing schedule WebSocket message:', error);
                }
            };

            this.ws.onclose = (event) => {
                console.log('Schedule WebSocket disconnected:', event.code, event.reason);
                this.isConnected = false;
                this.emit('disconnected', event);
                
                // Attempt to reconnect if not a normal closure
                if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    this.reconnectDelay *= 1.5; // Exponential backoff
                    console.log(`Reconnecting in ${Math.round(this.reconnectDelay / 1000)} seconds...`);
                    
                    setTimeout(() => {
                        this.connect(this.currentUser.id, this.currentUser.token);
                    }, this.reconnectDelay);
                }
            };

            this.ws.onerror = (error) => {
                console.error('Schedule WebSocket error:', error);
                this.emit('error', error);
            };
        } catch (error) {
            console.error('Error connecting to schedule WebSocket:', error);
        }
    }

    disconnect() {
        if (this.ws) {
            this.isConnected = false;
            try {
                this.ws.close(1000, 'Disconnected by user');
            } catch (e) {
                console.error('Error while disconnecting WebSocket:', e);
            }
        }
    }

    send(message) {
        if (this.ws && this.isConnected) {
            try {
                this.ws.send(JSON.stringify(message));
            } catch (e) {
                console.error('Error sending WebSocket message:', e);
            }
        } else {
            console.warn('WebSocket not connected, cannot send message');
        }
    }

    // Simple event emitter implementation
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
        return () => this.off(event, callback);
    }

    off(event, callback) {
        if (!this.listeners[event]) return;
        this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }

    emit(event, data) {
        if (!this.listeners[event]) return;
        this.listeners[event].forEach(callback => {
            try {
                callback(data);
            } catch (e) {
                console.error(`Error in ${event} event handler:`, e);
            }
        });
    }

    getStatus() {
        return {
            isConnected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            currentUser: this.currentUser
        };
    }
}

// Create singleton instance
export const scheduleWebSocketService = new ScheduleWebSocketService();

const WebSocketContext = createContext();

export const WebSocketProvider = ({ children }) => {
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState(null);
    const [error, setError] = useState(null);
    const ws = useRef(null);
    const clientId = useRef(Math.random().toString(36).substring(7));
    const reconnectTimeoutRef = useRef(null);
    const isConnectingRef = useRef(false);
    const shouldReconnectRef = useRef(true);
    const pingIntervalRef = useRef(null);

    const cleanup = useCallback(() => {
        // Clear reconnect timeout
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }

        // Clear ping interval
        if (pingIntervalRef.current) {
            clearInterval(pingIntervalRef.current);
            pingIntervalRef.current = null;
        }

        // Close WebSocket
        if (ws.current) {
            try {
                // Remove event handlers before closing to prevent reconnection
                ws.current.onopen = null;
                ws.current.onclose = null;
                ws.current.onerror = null;
                ws.current.onmessage = null;
                
                if (ws.current.readyState === WebSocket.OPEN || ws.current.readyState === WebSocket.CONNECTING) {
                    ws.current.close(1000, 'Component unmounted');
                }
            } catch (e) {
                console.error('Error closing WebSocket:', e);
            }
            ws.current = null;
        }
    }, []);

    const connect = useCallback(() => {
        // Prevent multiple simultaneous connection attempts
        if (isConnectingRef.current || !shouldReconnectRef.current) {
            return;
        }

        // Close existing connection
        cleanup();

        isConnectingRef.current = true;

        try {
            // Connect directly to backend WebSocket endpoint  
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = process.env.REACT_APP_WS_URL || `${wsProtocol}//localhost:8000/ws`;
            const wsPath = `${wsUrl}/${clientId.current}`;
            
            console.log('Connecting to WebSocket:', wsPath);
            
            ws.current = new WebSocket(wsPath);
            
            ws.current.onopen = () => {
                isConnectingRef.current = false;
                setIsConnected(true);
                setError(null);
                console.log('WebSocket connected successfully');

                // Start sending ping messages to keep connection alive
                pingIntervalRef.current = setInterval(() => {
                    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
                        try {
                            ws.current.send(JSON.stringify({ type: 'ping' }));
                        } catch (e) {
                            console.error('Failed to send ping:', e);
                        }
                    }
                }, 30000); // Send ping every 30 seconds
            };

            ws.current.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    setLastMessage(message);
                    if (message.type !== 'pong') {
                        console.log('Received message:', message);
                    }
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };

            ws.current.onclose = (event) => {
                isConnectingRef.current = false;
                setIsConnected(false);
                
                // Clear ping interval
                if (pingIntervalRef.current) {
                    clearInterval(pingIntervalRef.current);
                    pingIntervalRef.current = null;
                }

                console.log('WebSocket closed:', event.code, event.reason);

                // Only attempt reconnection if not a normal closure and component is still mounted
                if (shouldReconnectRef.current && event.code !== 1000) {
                    console.log('Attempting to reconnect in 5 seconds...');
                    reconnectTimeoutRef.current = setTimeout(() => {
                        connect();
                    }, 5000);
                }
            };

            ws.current.onerror = (event) => {
                isConnectingRef.current = false;
                console.error('WebSocket error occurred');
                setError('WebSocket connection failed');
                setIsConnected(false);
            };
            
        } catch (error) {
            isConnectingRef.current = false;
            setError('Failed to connect to WebSocket');
            console.error('WebSocket connection error:', error);
            
            if (shouldReconnectRef.current) {
                reconnectTimeoutRef.current = setTimeout(() => {
                    connect();
                }, 5000);
            }
        }
    }, [cleanup]);

    useEffect(() => {
        shouldReconnectRef.current = true;
        connect();

        return () => {
            shouldReconnectRef.current = false;
            cleanup();
        };
    }, [connect, cleanup]);

    const sendMessage = (message) => {
        if (ws.current && isConnected) {
            ws.current.send(JSON.stringify(message));
        } else {
            console.error('WebSocket is not connected');
        }
    };

    const joinQueue = (ticketId) => {
        sendMessage({
            type: 'join_queue',
            ticket_id: ticketId
        });
    };

    const pingServer = () => {
        sendMessage({
            type: 'ping'
        });
    };

    const value = {
        isConnected,
        lastMessage,
        error,
        sendMessage,
        joinQueue,
        pingServer
    };

    return (
        <WebSocketContext.Provider value={value}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = () => {
    const context = useContext(WebSocketContext);
    if (!context) {
        throw new Error('useWebSocket must be used within a WebSocketProvider');
    }
    return context;
};

// Ticket WebSocket hook for real-time ticket updates
export const useTicketWebSocket = (ticketId) => {
  const { isConnected, lastMessage, sendMessage } = useWebSocket();
  const [ticketUpdates, setTicketUpdates] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(null);
  
  // Connect to WebSocket for ticket updates
  useEffect(() => {
    if (!isConnected || !ticketId) return;
    
    // Subscribe to ticket-specific topic
    sendMessage({ 
      action: 'subscribe', 
      topics: [`ticket.${ticketId}`]
    });
    
    // Cleanup on unmount
    return () => {
      sendMessage({ 
        action: 'unsubscribe', 
        topics: [`ticket.${ticketId}`]
      });
    };
  }, [isConnected, ticketId, sendMessage]);
  
  // Process ticket updates from WebSocket
  useEffect(() => {
    if (!lastMessage || !ticketId) return;
    
    try {
      // Check if the message is relevant to this ticket
      if (lastMessage.id === ticketId || lastMessage.ticket_id === ticketId) {
        setLastUpdate(lastMessage);
        setTicketUpdates(prev => [...prev, lastMessage]);
      }
    } catch (error) {
      console.error('Error handling ticket update:', error);
    }
  }, [lastMessage, ticketId]);
  
  // Method to explicitly request a status update
  const requestUpdate = useCallback(() => {
    if (isConnected && ticketId) {
      sendMessage({
        action: 'request',
        topic: `ticket.${ticketId}`
      });
    }
  }, [isConnected, sendMessage, ticketId]);
  
  return {
    ticketUpdates,
    lastUpdate,
    requestUpdate
  };
};

// Queue WebSocket hook for real-time queue updates
export const useQueueWebSocket = (staffId, departmentId) => {
  const { isConnected, lastMessage, sendMessage } = useWebSocket();
  const [queueData, setQueueData] = useState({
    waiting: [],
    called: [],
    serving: [],
    completed: []
  });
  const [queueStats, setQueueStats] = useState({
    totalWaiting: 0,
    averageWaitTime: 0,
    maxWaitTime: 0
  });
  const [lastUpdate, setLastUpdate] = useState(null);
  
  // Subscribe to queue updates
  useEffect(() => {
    if (!isConnected) return;
    
    const topics = [];
    if (staffId) {
      topics.push(`staff.${staffId}.queue`);
    }
    
    if (departmentId) {
      topics.push(`department.${departmentId}.queue`);
    }
    
    if (topics.length > 0) {
      sendMessage({
        action: 'subscribe',
        topics
      });
      
      // Initial request for data
      if (staffId) {
        sendMessage({
          action: 'request',
          topic: `staff.${staffId}.queue`
        });
      } else if (departmentId) {
        sendMessage({
          action: 'request',
          topic: `department.${departmentId}.queue`
        });
      }
    }
    
    // Cleanup on unmount
    return () => {
      if (topics.length > 0) {
        sendMessage({
          action: 'unsubscribe',
          topics
        });
      }
    };
  }, [isConnected, staffId, departmentId, sendMessage]);
  
  // Handle queue update messages
  useEffect(() => {
    if (!lastMessage) return;
    
    try {
      if ((staffId && lastMessage.staff_id === staffId) || 
          (departmentId && lastMessage.department_id === departmentId)) {
            
        setLastUpdate(lastMessage);
        
        // Update queue data if provided
        if (lastMessage.queue) {
          setQueueData(prev => ({
            ...prev,
            ...lastMessage.queue
          }));
        }
        
        // Update stats if provided
        if (lastMessage.stats) {
          setQueueStats(prev => ({
            ...prev,
            ...lastMessage.stats
          }));
        }
      }
    } catch (error) {
      console.error('Error handling queue update:', error);
    }
  }, [lastMessage, staffId, departmentId]);
  
  // Method to request latest queue data
  const refreshQueue = useCallback(() => {
    if (isConnected) {
      if (staffId) {
        sendMessage({
          action: 'request',
          topic: `staff.${staffId}.queue`
        });
      } else if (departmentId) {
        sendMessage({
          action: 'request',
          topic: `department.${departmentId}.queue`
        });
      }
    }
  }, [isConnected, sendMessage, staffId, departmentId]);
  
  return {
    queueData,
    queueStats,
    lastUpdate,
    refreshQueue
  };
};

// Admin WebSocket hook for system monitoring
export const useAdminWebSocket = () => {
  const { isConnected, lastMessage, sendMessage } = useWebSocket();
  const [systemUpdates, setSystemUpdates] = useState({
    ticketCount: null,
    staffActivity: null,
    userLogins: [],
    criticalAlerts: []
  });

  // Subscribe to admin-specific channels
  useEffect(() => {
    if (isConnected) {
      // Subscribe to admin-specific topics
      sendMessage({ 
        action: 'subscribe', 
        topics: [
          'admin.system.stats',
          'admin.staff.activity',
          'admin.security.alerts'
        ]
      });
      
      // Cleanup on unmount
      return () => {
        sendMessage({ 
          action: 'unsubscribe', 
          topics: [
            'admin.system.stats',
            'admin.staff.activity',
            'admin.security.alerts'
          ]
        });
      };
    }
  }, [isConnected, sendMessage]);

  // Handle incoming messages
  useEffect(() => {
    if (!lastMessage?.data) return;
    
    try {
      const data = JSON.parse(lastMessage.data);
      
      // Handle different message types
      switch (data.topic) {
        case 'admin.system.stats':
          setSystemUpdates(prev => ({
            ...prev,
            ticketCount: data.payload.ticketCount,
            // Other system stats...
          }));
          break;
        
        case 'admin.staff.activity':
          setSystemUpdates(prev => ({
            ...prev,
            staffActivity: data.payload
          }));
          break;
          
        case 'admin.security.alerts':
          if (data.payload.critical) {
            setSystemUpdates(prev => ({
              ...prev,
              criticalAlerts: [...prev.criticalAlerts, data.payload]
            }));
          }
          break;
          
        case 'admin.user.login':
          setSystemUpdates(prev => ({
            ...prev,
            userLogins: [data.payload, ...prev.userLogins].slice(0, 10) // Keep last 10 logins
          }));
          break;
          
        default:
          // Ignore other messages
          break;
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }, [lastMessage]);

  // Request latest system stats
  const requestSystemStats = useCallback(() => {
    if (isConnected) {
      sendMessage({ 
        action: 'request', 
        topic: 'admin.system.stats'
      });
    }
  }, [isConnected, sendMessage]);

  // Request staff activity
  const requestStaffActivity = useCallback(() => {
    if (isConnected) {
      sendMessage({ 
        action: 'request', 
        topic: 'admin.staff.activity'
      });
    }
  }, [isConnected, sendMessage]);

  return {
    ...systemUpdates,
    connected: isConnected,
    requestSystemStats,
    requestStaffActivity
  };
};

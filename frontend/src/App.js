import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';

// Import routes
import AppRoutes from './routes/AppRoutes';

// Shared providers (contexts)
import { AuthProvider } from './shared/AuthContext';
import { WebSocketProvider } from './shared/WebSocketContext';

function App() {
  return (
    <Router>
      <AuthProvider>
        <WebSocketProvider>
          <AppRoutes />
        </WebSocketProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;

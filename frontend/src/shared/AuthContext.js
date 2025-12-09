import React, { createContext, useContext, useReducer, useEffect } from 'react';

const AuthContext = createContext();

const initialState = {
    user: null,
    isAuthenticated: false,
    loading: true,
    error: null
};

const authReducer = (state, action) => {
    switch (action.type) {
        case 'LOGIN_SUCCESS':
            return {
                ...state,
                user: action.payload,
                isAuthenticated: true,
                loading: false,
                error: null
            };
        case 'LOGIN_FAILURE':
            return {
                ...state,
                user: null,
                isAuthenticated: false,
                loading: false,
                error: action.payload
            };
        case 'LOGOUT':
            return {
                ...state,
                user: null,
                isAuthenticated: false,
                loading: false,
                error: null
            };
        case 'SET_LOADING':
            return {
                ...state,
                loading: action.payload
            };
        case 'CLEAR_ERROR':
            return {
                ...state,
                error: null
            };
        default:
            return state;
    }
};

export const AuthProvider = ({ children }) => {
    const [state, dispatch] = useReducer(authReducer, initialState);

    useEffect(() => {
        // Check if user is already logged in
        const token = localStorage.getItem('token');
        const userStr = localStorage.getItem('user');
        
        if (token && userStr && userStr !== 'undefined' && userStr !== 'null') {
            try {
                const user = JSON.parse(userStr);
                dispatch({
                    type: 'LOGIN_SUCCESS',
                    payload: user
                });
            } catch (error) {
                console.error('Failed to parse user from localStorage:', error);
                // Clear invalid data
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                dispatch({ type: 'SET_LOADING', payload: false });
            }
        } else {
            dispatch({ type: 'SET_LOADING', payload: false });
        }
    }, []);

    const login = async (credentials) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            
            // Direct backend URL (no nginx proxy)
            const response = await fetch('http://localhost:8000/api/v1/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: credentials.email,
                    password: credentials.password
                }),
            });

            const data = await response.json();

            if (response.ok && data.access_token) {
                // Create user object from new response format
                const user = {
                    id: data.user_id,
                    email: credentials.email,
                    role: data.user_role
                };
                
                // Store JWT token and user information
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('user', JSON.stringify(user));
                
                dispatch({
                    type: 'LOGIN_SUCCESS',
                    payload: user
                });

                return user; // Return user data for role-based routing
            } else {
                dispatch({
                    type: 'LOGIN_FAILURE',
                    payload: data.detail || 'Đăng nhập thất bại'
                });
                throw new Error(data.detail || 'Đăng nhập thất bại');
            }
        } catch (error) {
            dispatch({
                type: 'LOGIN_FAILURE',
                payload: error.message || 'Lỗi kết nối mạng'
            });
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        dispatch({ type: 'LOGOUT' });
    };

    const clearError = () => {
        dispatch({ type: 'CLEAR_ERROR' });
    };

    const value = {
        ...state,
        login,
        logout,
        clearError
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

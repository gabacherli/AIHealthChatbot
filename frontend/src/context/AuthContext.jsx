import React, { createContext, useState, useContext, useEffect } from 'react';
import { authService } from '../services/api';

// Create the authentication context
const AuthContext = createContext();

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

// Provider component that wraps the app and makes auth object available to any child component that calls useAuth()
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on initial load
    const checkLoggedIn = () => {
      if (authService.isAuthenticated()) {
        setUser({
          role: authService.getRole()
        });
      }
      setLoading(false);
    };

    checkLoggedIn();
  }, []);

  // Login function
  const login = async (username, password) => {
    try {
      console.log('AuthContext: Attempting login');
      const data = await authService.login(username, password);
      console.log('AuthContext: Login successful, setting user');
      setUser({
        role: data.role
      });
      return { success: true };
    } catch (error) {
      console.error('AuthContext: Login failed', error);
      return { success: false, error: error.msg || 'Login failed' };
    }
  };

  // Logout function
  const logout = () => {
    authService.logout();
    setUser(null);
  };

  // Get token function
  const getToken = () => {
    return authService.getToken();
  };

  // Context values to be provided
  const value = {
    user,
    login,
    logout,
    getToken,
    isAuthenticated: !!user,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

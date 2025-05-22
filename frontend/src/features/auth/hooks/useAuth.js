import { createContext, useState, useContext, useEffect } from 'react';
import authService from '../services/authService';

// Create the authentication context
const AuthContext = createContext();

/**
 * Custom hook to use the auth context
 * @returns {Object} - The auth context
 */
export const useAuth = () => useContext(AuthContext);

/**
 * Provider component that wraps the app and makes auth object available
 */
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

  /**
   * Login function
   * @param {string} username - The username
   * @param {string} password - The password
   * @returns {Object} - The login result
   */
  const login = async (username, password) => {
    try {
      const data = await authService.login(username, password);
      setUser({
        role: data.role
      });
      return { success: true };
    } catch (error) {
      return { success: false, error: error.msg || 'Login failed' };
    }
  };

  /**
   * Logout function
   */
  const logout = () => {
    authService.logout();
    setUser(null);
  };

  // Context values to be provided
  const value = {
    user,
    login,
    logout,
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

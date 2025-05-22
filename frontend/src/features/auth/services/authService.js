import api from '../../../services/api';

/**
 * Authentication service for handling user authentication
 */
const authService = {
  /**
   * Login a user
   * @param {string} username - The username
   * @param {string} password - The password
   * @returns {Promise} - The login response
   */
  login: async (username, password) => {
    try {
      const response = await api.post('/auth/login', { username, password });
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('role', response.data.role);
      return response.data;
    } catch (error) {
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  /**
   * Logout a user
   */
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
  },

  /**
   * Check if a user is authenticated
   * @returns {boolean} - Whether the user is authenticated
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },

  /**
   * Get the user's role
   * @returns {string|null} - The user's role
   */
  getRole: () => {
    return localStorage.getItem('role');
  }
};

export default authService;

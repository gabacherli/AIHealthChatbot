import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to add the auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Authentication services
export const authService = {
  login: async (username, password) => {
    try {
      console.log('Attempting login with:', { username });
      const response = await api.post('/auth/login', { username, password });
      console.log('Login response:', response.data);
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('role', response.data.role);
      return response.data;

    } catch (error) {
      console.error('Login error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
  },
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
  getRole: () => {
    return localStorage.getItem('role');
  }
};

// Chat services
export const chatService = {
  sendMessage: async (question) => {
    try {
      console.log('Sending chat message:', { question });
      const response = await api.post('/chat', { question });
      console.log('Chat response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Chat error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  }
};

export default api;

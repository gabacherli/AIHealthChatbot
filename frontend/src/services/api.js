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

// Document services
export const documentService = {
  uploadDocument: async (formData) => {
    try {
      // Use a different config for file uploads
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      };

      const response = await axios.post(
        'http://localhost:5000/api/documents/upload',
        formData,
        config
      );

      return response.data;
    } catch (error) {
      console.error('Document upload error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  listDocuments: async () => {
    try {
      const response = await api.get('/documents/list');
      return response.data;
    } catch (error) {
      console.error('List documents error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  downloadDocument: async (filename) => {
    try {
      // Use direct window.open for file downloads
      window.open(`http://localhost:5000/api/documents/download/${filename}`, '_blank');
      return true;
    } catch (error) {
      console.error('Document download error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  deleteDocument: async (filename) => {
    try {
      const response = await api.delete(`/documents/delete/${filename}`);
      return response.data;
    } catch (error) {
      console.error('Document delete error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  searchDocuments: async (query, filters = {}) => {
    try {
      const response = await api.post('/documents/search', { query, filters });
      return response.data;
    } catch (error) {
      console.error('Document search error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  }
};

export default api;

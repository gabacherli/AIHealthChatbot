import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  // Don't set default Content-Type - let each request set its own
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
      const response = await api.post('/auth/login', { username, password }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
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
  },
  getToken: () => {
    return localStorage.getItem('token');
  }
};

// Chat services
export const chatService = {
  sendMessage: async (question) => {
    try {
      console.log('Sending chat message:', { question });
      const response = await api.post('/chat', { question }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
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
      // Use the configured api instance for file uploads
      const response = await api.post('/documents/upload', formData, {
        headers: {
          // Don't set Content-Type for multipart/form-data - let browser set it with boundary
          // Authorization header is automatically added by the api interceptor
        }
      });

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
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      // Use fetch with proper authentication
      const response = await fetch(`http://localhost:5000/api/documents/download/${filename}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(`Download failed: ${response.status} ${response.statusText}`);
      }

      // Get the blob and create download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      // Create temporary link and trigger download
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();

      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      return true;
    } catch (error) {
      console.error('Document download error:', error);
      throw error.response ? error.response.data : { msg: error.message || 'Network error' };
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
      const response = await api.post('/documents/search', { query, filters }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Document search error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  }
};

export default api;

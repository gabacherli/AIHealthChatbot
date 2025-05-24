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
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('role', response.data.role);
      localStorage.setItem('user_id', response.data.user_id);
      localStorage.setItem('username', response.data.username);
      localStorage.setItem('full_name', response.data.full_name);
      return response.data;

    } catch (error) {
      console.error('Login error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    localStorage.removeItem('full_name');
  },
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
  getRole: () => {
    return localStorage.getItem('role');
  },
  getToken: () => {
    return localStorage.getItem('token');
  },
  getUserId: () => {
    return localStorage.getItem('user_id');
  },
  getUsername: () => {
    return localStorage.getItem('username');
  },
  getFullName: () => {
    return localStorage.getItem('full_name');
  }
};

// Chat services
export const chatService = {
  sendMessage: async (question) => {
    try {
      const response = await api.post('/chat', { question }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
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
  },

  // Get patient's shared documents with sharing status
  getPatientSharedDocuments: async (patientId) => {
    try {
      const response = await api.get(`/documents/patients/${patientId}/shared`);
      return response.data;
    } catch (error) {
      console.error('Get patient shared documents error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  // Get all patient documents accessible to a professional
  getProfessionalPatientDocuments: async (professionalId, patientId = null) => {
    try {
      const params = patientId ? { patient_id: patientId } : {};
      const response = await api.get(`/documents/professionals/${professionalId}/patient-documents`, { params });
      return response.data;
    } catch (error) {
      console.error('Get professional patient documents error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  // Check document access permissions
  checkDocumentAccess: async (documentId) => {
    try {
      const response = await api.get(`/documents/access-check/${documentId}`);
      return response.data;
    } catch (error) {
      console.error('Check document access error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  // Get document audit logs
  getDocumentAuditLogs: async (documentId, days = 30) => {
    try {
      const response = await api.get(`/documents/audit/${documentId}`, {
        params: { days }
      });
      return response.data;
    } catch (error) {
      console.error('Get document audit logs error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  // Get patient access summary
  getPatientAccessSummary: async (patientId, days = 30) => {
    try {
      const response = await api.get(`/documents/patients/${patientId}/access-summary`, {
        params: { days }
      });
      return response.data;
    } catch (error) {
      console.error('Get patient access summary error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  // Log document access manually
  logDocumentAccess: async (documentId, accessType, success = true) => {
    try {
      const response = await api.post('/documents/log-access', {
        document_id: documentId,
        access_type: accessType,
        success: success
      }, {
        headers: { 'Content-Type': 'application/json' }
      });
      return response.data;
    } catch (error) {
      console.error('Log document access error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  }
};

// Relationship services
export const relationshipService = {
  // Create a new patient-professional relationship
  createRelationship: async (relationshipData) => {
    try {
      const response = await api.post('/relationships/', relationshipData, {
        headers: { 'Content-Type': 'application/json' }
      });
      return response.data;
    } catch (error) {
      console.error('Create relationship error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  // Get a specific relationship by ID
  getRelationship: async (relationshipId) => {
    try {
      const response = await api.get(`/relationships/${relationshipId}`);
      return response.data;
    } catch (error) {
      console.error('Get relationship error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  // Update a relationship
  updateRelationship: async (relationshipId, updateData) => {
    try {
      const response = await api.put(`/relationships/${relationshipId}`, updateData, {
        headers: { 'Content-Type': 'application/json' }
      });
      return response.data;
    } catch (error) {
      console.error('Update relationship error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  // Delete/terminate a relationship
  deleteRelationship: async (relationshipId, reason = null) => {
    try {
      const response = await api.delete(`/relationships/${relationshipId}`, {
        data: reason ? { reason } : {},
        headers: { 'Content-Type': 'application/json' }
      });
      return response.data;
    } catch (error) {
      console.error('Delete relationship error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  // Get all patients for a professional
  getProfessionalPatients: async (professionalId, status = 'active') => {
    try {
      const response = await api.get(`/relationships/professionals/${professionalId}/patients`, {
        params: { status }
      });
      return response.data;
    } catch (error) {
      console.error('Get professional patients error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  // Get all professionals for a patient
  getPatientProfessionals: async (patientId, status = 'active') => {
    try {
      const response = await api.get(`/relationships/patients/${patientId}/professionals`, {
        params: { status }
      });
      return response.data;
    } catch (error) {
      console.error('Get patient professionals error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  // Search for healthcare professionals
  searchProfessionals: async (query, specialty = null, organization = null) => {
    try {
      const params = { q: query };
      if (specialty) params.specialty = specialty;
      if (organization) params.organization = organization;

      const response = await api.get('/relationships/search/professionals', { params });
      return response.data;
    } catch (error) {
      console.error('Search professionals error:', error);
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  }
};

export default api;

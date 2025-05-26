import api from '../../../services/api';

/**
 * Enhanced chat service for handling chat functionality with document retrieval
 */
const chatService = {
  /**
   * Send a message to the chatbot with optional patient context
   * @param {string} question - The question to send
   * @param {number|null} patientId - Optional patient ID for healthcare professionals
   * @returns {Promise} - The enhanced chat response with sources and metadata
   */
  sendMessage: async (question, patientId = null) => {
    try {
      const requestData = { question };

      // Add patient_id for healthcare professionals
      if (patientId) {
        requestData.patient_id = patientId;
      }

      const response = await api.post('/chat', requestData);
      return response.data;
    } catch (error) {
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  },

  /**
   * Get list of patients available for healthcare professionals
   * @returns {Promise} - List of accessible patients
   */
  getAvailablePatients: async () => {
    try {
      const response = await api.get('/chat/patients');
      return response.data;
    } catch (error) {
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  }
};

export default chatService;

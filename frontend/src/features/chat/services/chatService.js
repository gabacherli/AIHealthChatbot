import api from '../../../services/api';

/**
 * Chat service for handling chat functionality
 */
const chatService = {
  /**
   * Send a message to the chatbot
   * @param {string} question - The question to send
   * @returns {Promise} - The chat response
   */
  sendMessage: async (question) => {
    try {
      const response = await api.post('/chat', { question });
      return response.data;
    } catch (error) {
      throw error.response ? error.response.data : { msg: 'Network error' };
    }
  }
};

export default chatService;

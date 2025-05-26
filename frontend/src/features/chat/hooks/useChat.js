import { useState } from 'react';
import chatService from '../services/chatService';

/**
 * Custom hook for chat functionality
 * @returns {Object} - Chat state and functions
 */
export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  /**
   * Send a message to the chatbot with optional patient context
   * @param {string} message - The message to send
   * @param {number|null} patientId - Optional patient ID for healthcare professionals
   * @returns {Promise} - The result of sending the message
   */
  const sendMessage = async (message, patientId = null) => {
    if (!message.trim() || loading) {
      return { success: false };
    }

    const userMessage = {
      id: Date.now(),
      text: message,
      sender: 'user',
      timestamp: new Date().toISOString(),
      patientContext: patientId ? { patientId } : null
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await chatService.sendMessage(message.trim(), patientId);

      const botMessage = {
        id: Date.now() + 1,
        text: response.answer || response.msg || 'Sorry, I could not process your request.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
        sources: response.sources || [],
        metadata: response.metadata || {},
        hasContext: (response.sources && response.sources.length > 0) || false,
        patientContext: patientId ? { patientId } : null
      };

      setMessages(prev => [...prev, botMessage]);
      return { success: true, response };
    } catch (error) {
      console.error('Error sending message:', error);

      const errorMessage = {
        id: Date.now() + 1,
        text: error.error || error.msg || 'Sorry, there was an error processing your request. Please try again.',
        sender: 'bot',
        isError: true,
        timestamp: new Date().toISOString(),
        patientContext: patientId ? { patientId } : null
      };

      setMessages(prev => [...prev, errorMessage]);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Clear all messages
   */
  const clearMessages = () => {
    setMessages([]);
  };

  /**
   * Get messages with enhanced context information
   */
  const getMessagesWithContext = () => {
    return messages.map(msg => ({
      ...msg,
      hasDocumentContext: msg.hasContext || (msg.sources && msg.sources.length > 0),
      sourcesCount: msg.sources ? msg.sources.length : 0
    }));
  };

  return {
    messages: getMessagesWithContext(),
    loading,
    sendMessage,
    clearMessages
  };
};

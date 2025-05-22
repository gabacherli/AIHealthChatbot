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
   * Send a message to the chatbot
   * @param {string} message - The message to send
   * @returns {Promise} - The result of sending the message
   */
  const sendMessage = async (message) => {
    if (!message.trim() || loading) {
      return { success: false };
    }
    
    const userMessage = {
      text: message,
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    
    try {
      const response = await chatService.sendMessage(message.trim());
      
      const botMessage = {
        text: response.answer,
        sender: 'bot',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, botMessage]);
      return { success: true };
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        text: 'Sorry, there was an error processing your request. Please try again.',
        sender: 'bot',
        isError: true,
        timestamp: new Date().toISOString()
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

  return {
    messages,
    loading,
    sendMessage,
    clearMessages
  };
};

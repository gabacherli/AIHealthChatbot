import React, { useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useAuth } from '../../../auth/hooks/useAuth';
import ReactMarkdown from 'react-markdown';
import './MessageList.css';

/**
 * Message list component for displaying chat messages
 */
const MessageList = ({ messages }) => {
  const { user } = useAuth();
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  /**
   * Scroll to the bottom of the message list
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="messages-container">
      {messages.length === 0 ? (
        <div className="welcome-message">
          <h3>Welcome to the Health Chatbot!</h3>
          <p>
            {user?.role === 'professional'
              ? 'Ask any medical questions to get detailed clinical insights.'
              : 'Ask any health-related questions for easy-to-understand answers.'}
          </p>
        </div>
      ) : (
        messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.sender} ${msg.isError ? 'error' : ''}`}
          >
            <div className="message-content">
              {msg.sender === 'bot' ? (
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              ) : (
                msg.text
              )}
            </div>
            <div className="message-timestamp">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};

MessageList.propTypes = {
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      text: PropTypes.string.isRequired,
      sender: PropTypes.oneOf(['user', 'bot']).isRequired,
      timestamp: PropTypes.string.isRequired,
      isError: PropTypes.bool
    })
  ).isRequired
};

export default MessageList;

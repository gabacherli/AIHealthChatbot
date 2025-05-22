import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import './ChatInput.css';

/**
 * Chat input component for sending messages
 */
const ChatInput = ({ onSendMessage, loading }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  /**
   * Auto-resize the textarea based on content
   */
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      // Reset to default height
      textarea.style.height = '40px';

      // Calculate the scroll height and add a small buffer
      const newHeight = Math.min(textarea.scrollHeight, 150);

      // Only update if height needs to change
      if (newHeight > 40) {
        textarea.style.height = `${newHeight}px`;
      }
    }
  }, [input]);

  /**
   * Handle form submission
   * @param {Event} e - The form event
   */
  const handleSubmit = (e) => {
    e.preventDefault();

    if (!input.trim() || loading) return;

    onSendMessage(input);
    setInput('');
  };

  /**
   * Handle key press events
   * @param {KeyboardEvent} e - The keyboard event
   */
  const handleKeyDown = (e) => {
    // Submit on Enter without Shift key
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your health question here..."
        disabled={loading}
        rows="1"
        className="chat-textarea"
      />
      <button type="submit" disabled={loading || !input.trim()}>
        {loading ? 'Sending...' : 'Send'}
      </button>
    </form>
  );
};

ChatInput.propTypes = {
  onSendMessage: PropTypes.func.isRequired,
  loading: PropTypes.bool
};

export default ChatInput;

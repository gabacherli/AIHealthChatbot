import React from 'react';
import { useAuth } from '../../features/auth/hooks/useAuth';
import { useChat } from '../../features/chat/hooks/useChat';
import MessageList from '../../features/chat/components/MessageList';
import ChatInput from '../../features/chat/components/ChatInput';
import './ChatPage.css';

/**
 * Chat page component
 */
const ChatPage = () => {
  const { user } = useAuth();
  const { messages, loading, sendMessage } = useChat();

  return (
    <div className="chat-page">
      <div className="chat-header">
        <h2>Health Chatbot</h2>
        <div className="user-role">
          Logged in as: <span>{user?.role || 'User'}</span>
        </div>
      </div>
      
      <MessageList messages={messages} />
      
      <ChatInput onSendMessage={sendMessage} loading={loading} />
    </div>
  );
};

export default ChatPage;

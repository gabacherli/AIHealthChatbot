import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../features/auth/hooks/useAuth';
import './Header.css';

/**
 * Header component for the application
 */
const Header = () => {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="logo">
        <Link to="/">Health Chatbot</Link>
      </div>
      
      {isAuthenticated && (
        <nav className="nav">
          <Link to="/chat">Chat</Link>
          <button className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </nav>
      )}
    </header>
  );
};

export default Header;

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Layout.css';

const Layout = ({ children }) => {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout">
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
      
      <main className="main-content">
        {children}
      </main>
      
      <footer className="footer">
        <p>&copy; {new Date().getFullYear()} Health Chatbot. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Layout;

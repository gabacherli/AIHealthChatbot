import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Layout.css';

const Layout = ({ children }) => {
  const { isAuthenticated, logout, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Function to check if a link is active
  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <div className="layout">
      <header className="header">
        <div className="logo">
          <Link to="/">Health Chatbot</Link>
        </div>

        {isAuthenticated && (
          <nav className="nav">
            <Link to="/chat" className={isActive('/chat')}>Chat</Link>
            <Link to="/documents" className={isActive('/documents')}>Documents</Link>
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
        {user && <p className="user-role">Logged in as: {user.role}</p>}
      </footer>
    </div>
  );
};

export default Layout;

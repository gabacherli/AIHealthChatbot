import React from 'react';
import './Footer.css';

/**
 * Footer component for the application
 */
const Footer = () => {
  return (
    <footer className="footer">
      <p>&copy; {new Date().getFullYear()} Health Chatbot. All rights reserved.</p>
    </footer>
  );
};

export default Footer;

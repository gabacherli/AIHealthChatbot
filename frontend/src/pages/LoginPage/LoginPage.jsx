import React from 'react';
import LoginForm from '../../features/auth/components/LoginForm';
import './LoginPage.css';

/**
 * Login page component
 */
const LoginPage = () => {
  return (
    <div className="login-page">
      <div className="login-card">
        <h2>Health Chatbot Login</h2>
        <LoginForm />
      </div>
    </div>
  );
};

export default LoginPage;

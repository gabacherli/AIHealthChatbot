import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Components
import Login from './components/Login';
import Chat from './components/Chat';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import ProfessionalDashboard from './components/ProfessionalDashboard';
import PatientDashboard from './components/PatientDashboard';

// Pages
import DocumentsPage from './pages/DocumentsPage';

// Context
import { AuthProvider } from './context/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/chat"
              element={
                <ProtectedRoute>
                  <Chat />
                </ProtectedRoute>
              }
            />
            <Route
              path="/documents"
              element={
                <ProtectedRoute>
                  <DocumentsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/professional"
              element={
                <ProtectedRoute>
                  <ProfessionalDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/patient"
              element={
                <ProtectedRoute>
                  <PatientDashboard />
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route path="*" element={<Navigate to="/chat" replace />} />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  );
}

export default App;

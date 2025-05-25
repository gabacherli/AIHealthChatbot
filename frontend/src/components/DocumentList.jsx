import React, { useState, useEffect } from 'react';
import { documentService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './DocumentList.css';

const DocumentList = ({ onDocumentDeleted }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    fetchDocuments();
  }, []);

  // Expose refresh method globally
  useEffect(() => {
    window.refreshDocumentList = fetchDocuments;
    return () => {
      delete window.refreshDocumentList;
    };
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await documentService.listDocuments();
      setDocuments(response.documents || []);
      setError('');
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (filename) => {
    try {
      await documentService.downloadDocument(filename);
    } catch (err) {
      console.error('Error downloading document:', err);
      setError('Failed to download document. Please try again.');
    }
  };

  const handleDelete = async (filename) => {
    if (window.confirm(`Are you sure you want to delete ${filename}?`)) {
      try {
        await documentService.deleteDocument(filename);
        setDocuments(documents.filter(doc => doc !== filename));

        if (onDocumentDeleted) {
          onDocumentDeleted(filename);
        }
      } catch (err) {
        console.error('Error deleting document:', err);
        setError('Failed to delete document. Please try again.');
      }
    }
  };

  if (loading) {
    return <div className="document-list-loading">Loading documents...</div>;
  }

  return (
    <div className="document-list">
      <h3>Uploaded Documents</h3>

      {error && <div className="document-list-error">{error}</div>}

      {documents.length === 0 ? (
        <div className="no-documents">
          <p>No documents have been uploaded yet.</p>
        </div>
      ) : (
        <ul className="documents">
          {documents.map((filename, index) => (
            <li key={index} className="document-item">
              <div className="document-name">
                <i className="document-icon"></i>
                {filename}
              </div>

              <div className="document-actions">
                <button
                  onClick={() => handleDownload(filename)}
                  className="action-button download-button"
                  title="Download document"
                >
                  Download
                </button>

                {user?.role === 'professional' && (
                  <button
                    onClick={() => handleDelete(filename)}
                    className="action-button delete-button"
                    title="Delete document"
                  >
                    Delete
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      <button
        onClick={fetchDocuments}
        className="refresh-button"
        title="Refresh document list"
      >
        Refresh List
      </button>
    </div>
  );
};

export default DocumentList;

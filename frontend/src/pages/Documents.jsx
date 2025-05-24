import React, { useState } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import DocumentList from '../components/DocumentList';
import './Documents.css';

const Documents = () => {
  const [refreshKey, setRefreshKey] = useState(0);
  
  const handleUploadSuccess = () => {
    // Trigger a refresh of the document list
    setRefreshKey(prevKey => prevKey + 1);
  };
  
  const handleDocumentDeleted = () => {
    // No need to do anything special here as DocumentList handles its own state
  };
  
  return (
    <div className="documents-page">
      <h2>Document Management</h2>
      
      <div className="documents-container">
        <div className="upload-section">
          <DocumentUpload onUploadSuccess={handleUploadSuccess} />
        </div>
        
        <div className="list-section">
          <DocumentList 
            key={refreshKey} 
            onDocumentDeleted={handleDocumentDeleted} 
          />
        </div>
      </div>
    </div>
  );
};

export default Documents;

import React, { useState } from 'react';
import { documentService } from '../services/api';
import './DocumentUpload.css';

const DocumentUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    // Check file type
    const allowedTypes = [
      'text/plain', 
      'application/pdf', 
      'image/png', 
      'image/jpeg', 
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'text/csv',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel'
    ];
    
    if (!allowedTypes.includes(file.type)) {
      setError('File type not supported. Please upload a PDF, TXT, DOCX, PNG, JPG, CSV, or XLSX file.');
      return;
    }

    // Check file size (max 16MB)
    if (file.size > 16 * 1024 * 1024) {
      setError('File size exceeds the 16MB limit.');
      return;
    }

    setUploading(true);
    setProgress(10);

    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', file);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress((prevProgress) => {
          const newProgress = prevProgress + 10;
          return newProgress >= 90 ? 90 : newProgress;
        });
      }, 500);

      // Upload the file
      const response = await documentService.uploadDocument(formData);
      
      clearInterval(progressInterval);
      setProgress(100);
      
      // Reset form
      setFile(null);
      setUploading(false);
      
      // Notify parent component
      if (onUploadSuccess) {
        onUploadSuccess(response);
      }
      
      // Reset progress after a delay
      setTimeout(() => setProgress(0), 1000);
      
    } catch (error) {
      console.error('Error uploading document:', error);
      setError(error.msg || 'Failed to upload document. Please try again.');
      setUploading(false);
      setProgress(0);
    }
  };

  return (
    <div className="document-upload">
      <h3>Upload Document</h3>
      
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="file-input-container">
          <input
            type="file"
            onChange={handleFileChange}
            disabled={uploading}
            id="file-upload"
            className="file-input"
          />
          <label htmlFor="file-upload" className="file-label">
            {file ? file.name : 'Choose a file'}
          </label>
        </div>
        
        {progress > 0 && (
          <div className="progress-container">
            <div 
              className="progress-bar" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        )}
        
        {error && <div className="error-message">{error}</div>}
        
        <button 
          type="submit" 
          disabled={!file || uploading}
          className="upload-button"
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </form>
      
      <div className="upload-info">
        <p>Supported file types: PDF, TXT, DOCX, PNG, JPG, CSV, XLSX</p>
        <p>Maximum file size: 16MB</p>
      </div>
    </div>
  );
};

export default DocumentUpload;

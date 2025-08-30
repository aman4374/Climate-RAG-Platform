import React, { useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

const DocumentUploader = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const uploadFile = async (file) => {
    setUploading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({
          type: 'success',
          text: `Successfully uploaded ${file.name}: ${data.message}`
        });
        if (onUploadSuccess) {
          onUploadSuccess();
        }
      } else {
        setMessage({
          type: 'error',
          text: data.detail || 'Upload failed'
        });
      }
    } catch (err) {
      console.error('Upload error:', err);
      setMessage({
        type: 'error',
        text: 'Failed to upload file. Please try again.'
      });
    } finally {
      setUploading(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      uploadFile(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      uploadFile(files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  return (
    <div>
      <div 
        className={`upload-area ${dragOver ? 'dragover' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => document.getElementById('file-input').click()}
      >
        {uploading ? (
          <div className="loading">
            <p>Uploading and processing document...</p>
          </div>
        ) : (
          <>
            <div className="upload-text">
              <p>📄 Drop files here or click to browse</p>
              <p style={{ fontSize: '0.9rem', color: '#9ca3af' }}>
                Supports PDF, DOCX, and TXT files
              </p>
            </div>
            <input
              id="file-input"
              type="file"
              className="file-input"
              accept=".pdf,.docx,.txt"
              onChange={handleFileSelect}
              disabled={uploading}
            />
          </>
        )}
      </div>

      {message && (
        <div className={message.type === 'success' ? 'success' : 'error'}>
          {message.text}
        </div>
      )}

      <div style={{ marginTop: '15px', fontSize: '0.9rem', color: '#6b7280' }}>
        <p><strong>Supported sources:</strong></p>
        <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
          <li>IPCC Assessment Reports</li>
          <li>UNFCCC Documents</li>
          <li>National Climate Policies</li>
          <li>Research Papers (PDF)</li>
          <li>Government Reports</li>
        </ul>
      </div>
    </div>
  );
};

export default DocumentUploader;
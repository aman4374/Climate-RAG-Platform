import React, { useState, useEffect } from 'react';
import './App.css';
import ChatInterface from './components/ChatInterface';
import DocumentUploader from './components/DocumentUploader';
import DataSourceManager from './components/DataSourceManager';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [stats, setStats] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      await Promise.all([loadStats(), loadDocuments()]);
    } catch (err) {
      setError('Failed to load initial data');
      console.error('Error loading initial data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/status`);
      if (!response.ok) throw new Error('Failed to load stats');
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const loadDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/documents`);
      if (!response.ok) throw new Error('Failed to load documents');
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (err) {
      console.error('Error loading documents:', err);
    }
  };

  const handleDocumentUploaded = () => {
    // Refresh data after successful upload
    loadInitialData();
  };

  if (loading) {
    return (
      <div className="App">
        <div className="loading">
          <p>Loading Climate Policy Intelligence Platform...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="header">
        <h1>Climate Policy Intelligence Platform</h1>
        <p>AI-powered analysis of climate policy documents</p>
      </header>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      <div className="main-content">
        <div className="chat-section">
          <ChatInterface />
        </div>

        <div className="sidebar">
          <div className="upload-section">
            <h3 className="section-title">Upload Documents</h3>
            <DocumentUploader onUploadSuccess={handleDocumentUploaded} />
          </div>

          <div className="data-sources-section">
            <DataSourceManager onUpdateComplete={handleDocumentUploaded} />
          </div>

          <div className="documents-section">
            <h3 className="section-title">Knowledge Base Status</h3>
            
            {stats && (
              <div className="stats">
                <div className="stats-item">
                  <span className="stats-label">Total Chunks:</span>
                  <span className="stats-value">{stats.total_chunks}</span>
                </div>
                <div className="stats-item">
                  <span className="stats-label">Documents Processed:</span>
                  <span className="stats-value">{stats.documents_processed}</span>
                </div>
                <div className="stats-item">
                  <span className="stats-label">Status:</span>
                  <span className="stats-value">{stats.status}</span>
                </div>
              </div>
            )}

            <h4 style={{marginTop: '20px', marginBottom: '10px'}}>Documents ({documents.length})</h4>
            <div className="document-list">
              {documents.length === 0 ? (
                <p style={{color: '#6b7280', textAlign: 'center', padding: '20px'}}>
                  No documents uploaded yet
                </p>
              ) : (
                documents.map((doc, index) => (
                  <div key={index} className="document-item">
                    <div className="document-name">{doc.filename}</div>
                    <div className="document-info">
                      {doc.chunks} chunks • {doc.file_type}
                      {doc.source && (
                        <span className="document-source"> • {doc.source}</span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
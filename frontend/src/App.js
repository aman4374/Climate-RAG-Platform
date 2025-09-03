// import React, { useState, useEffect } from 'react';
// import './App.css';
// import ChatInterface from './components/ChatInterface';
// import DocumentUploader from './components/DocumentUploader';
// import DataSourceManager from './components/DataSourceManager';

// const API_BASE_URL = 'http://localhost:8000';

// function App() {
//   const [stats, setStats] = useState(null);
//   const [documents, setDocuments] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);

//   useEffect(() => {
//     loadInitialData();
//   }, []);

//   const loadInitialData = async () => {
//     try {
//       setLoading(true);
//       await Promise.all([loadStats(), loadDocuments()]);
//     } catch (err) {
//       setError('Failed to load initial data');
//       console.error('Error loading initial data:', err);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const loadStats = async () => {
//     try {
//       const response = await fetch(`${API_BASE_URL}/status`);
//       if (!response.ok) throw new Error('Failed to load stats');
//       const data = await response.json();
//       setStats(data);
//     } catch (err) {
//       console.error('Error loading stats:', err);
//     }
//   };

//   const loadDocuments = async () => {
//     try {
//       const response = await fetch(`${API_BASE_URL}/documents`);
//       if (!response.ok) throw new Error('Failed to load documents');
//       const data = await response.json();
//       setDocuments(data.documents || []);
//     } catch (err) {
//       console.error('Error loading documents:', err);
//     }
//   };

//   const handleDocumentUploaded = () => {
//     // Refresh data after successful upload
//     loadInitialData();
//   };

//   if (loading) {
//     return (
//       <div className="App">
//         <div className="loading">
//           <p>Loading Climate Policy Intelligence Platform...</p>
//         </div>
//       </div>
//     );
//   }

//   return (
//     <div className="App">
//       <header className="header">
//         <h1>Climate Policy Intelligence Platform</h1>
//         <p>AI-powered analysis of climate policy documents</p>
//       </header>

//       {error && (
//         <div className="error">
//           {error}
//         </div>
//       )}

//       <div className="main-content">
//         <div className="chat-section">
//           <ChatInterface />
//         </div>

//         <div className="sidebar">
//           <div className="upload-section">
//             <h3 className="section-title">Upload Documents</h3>
//             <DocumentUploader onUploadSuccess={handleDocumentUploaded} />
//           </div>

//           <div className="data-sources-section">
//             <DataSourceManager onUpdateComplete={handleDocumentUploaded} />
//           </div>

//           <div className="documents-section">
//             <h3 className="section-title">Knowledge Base Status</h3>
            
//             {stats && (
//               <div className="stats">
//                 <div className="stats-item">
//                   <span className="stats-label">Total Chunks:</span>
//                   <span className="stats-value">{stats.total_chunks}</span>
//                 </div>
//                 <div className="stats-item">
//                   <span className="stats-label">Documents Processed:</span>
//                   <span className="stats-value">{stats.documents_processed}</span>
//                 </div>
//                 <div className="stats-item">
//                   <span className="stats-label">Status:</span>
//                   <span className="stats-value">{stats.status}</span>
//                 </div>
//               </div>
//             )}

//             <h4 style={{marginTop: '20px', marginBottom: '10px'}}>Documents ({documents.length})</h4>
//             <div className="document-list">
//               {documents.length === 0 ? (
//                 <p style={{color: '#6b7280', textAlign: 'center', padding: '20px'}}>
//                   No documents uploaded yet
//                 </p>
//               ) : (
//                 documents.map((doc, index) => (
//                   <div key={index} className="document-item">
//                     <div className="document-name">{doc.filename}</div>
//                     <div className="document-info">
//                       {doc.chunks} chunks • {doc.file_type}
//                       {doc.source && (
//                         <span className="document-source"> • {doc.source}</span>
//                       )}
//                     </div>
//                   </div>
//                 ))
//               )}
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }

// export default App; 

import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  Upload, 
  FileText, 
  BarChart3, 
  Settings, 
  MessageSquare, 
  BookOpen, 
  Globe, 
  TrendingUp, 
  Filter,
  Download,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock,
  Send,
  Mic,
  Plus,
  Star,
  Eye,
  Zap
} from 'lucide-react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

const ClimateIntelligencePlatform = () => {
  const [activeTab, setActiveTab] = useState('chat');
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m your Climate Policy AI assistant. I can help you find information from climate policy documents. What would you like to know?',
      timestamp: new Date(),
      sources: []
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [searchHistory, setSearchHistory] = useState([
    'What are the economic impacts of carbon pricing?',
    'Climate policy implementation strategies',
    'Carbon emission reduction targets'
  ]);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      await Promise.all([loadStats(), loadDocuments()]);
    } catch (err) {
      setError('Failed to load initial data');
      console.error('Error loading initial data:', err);
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

  const handleSendMessage = async () => {
    if (!query.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date(),
      sources: []
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    const currentQuery = query;
    setQuery('');

    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: currentQuery }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from server');
      }

      const data = await response.json();
      
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.response || 'I apologize, but I couldn\'t generate a response at this time.',
        timestamp: new Date(),
        sources: data.sources || []
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Add to search history if not already present
      if (!searchHistory.includes(currentQuery)) {
        setSearchHistory(prev => [currentQuery, ...prev.slice(0, 4)]);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: 'I apologize, but I encountered an error while processing your request. Please make sure the backend server is running.',
        timestamp: new Date(),
        sources: []
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setError(null);
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload file');
      }

      const data = await response.json();
      console.log('File uploaded successfully:', data);
      
      // Refresh documents list
      await loadInitialData();
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      console.error('Error uploading file:', err);
      setError('Failed to upload file. Please try again.');
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const ChatInterface = () => (
    <div className="flex flex-col h-full">
      {/* Chat Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Climate Policy Assistant</h2>
            <p className="text-sm text-gray-600">Ask questions about climate policies, reports, and data</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="flex items-center text-sm text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              {stats ? `${stats.documents_processed} documents ready` : 'Loading...'}
            </span>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-3xl rounded-lg p-4 ${
              message.type === 'user' 
                ? 'bg-blue-600 text-white ml-8' 
                : 'bg-white border border-gray-200 mr-8'
            }`}>
              <div className="whitespace-pre-wrap">{message.content}</div>
              
              {message.sources && message.sources.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <p className="text-sm font-medium text-gray-700 mb-2">Sources:</p>
                  <div className="space-y-2">
                    {message.sources.map((source, idx) => (
                      <div key={idx} className="flex items-center justify-between bg-gray-50 p-2 rounded text-sm">
                        <div className="flex items-center space-x-2">
                          <FileText className="w-4 h-4 text-gray-500" />
                          <span className="font-medium">{source.filename || source.title || 'Document'}</span>
                        </div>
                        {source.score && (
                          <span className="text-blue-600 font-medium">{Math.round(source.score * 100)}% relevant</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="mt-2 text-xs opacity-70">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg p-4 mr-8">
              <div className="flex items-center space-x-2">
                <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
                <span className="text-gray-600">Searching climate documents...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 p-6">
        {/* Search History */}
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">Recent searches:</p>
          <div className="flex flex-wrap gap-2">
            {searchHistory.map((search, idx) => (
              <button
                key={idx}
                onClick={() => setQuery(search)}
                className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded-full transition-colors"
              >
                {search}
              </button>
            ))}
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask about climate policies, carbon pricing, emissions data..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!query.trim() || isLoading}
            className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );

  const DocumentsInterface = () => (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">Document Library</h2>
          <p className="text-gray-600">Manage and monitor climate policy documents</p>
        </div>
        <div className="flex items-center space-x-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".pdf,.txt,.docx,.doc"
            style={{ display: 'none' }}
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Documents</span>
          </button>
          <button 
            onClick={loadInitialData}
            className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 mr-2" />
            {error}
          </div>
        </div>
      )}

      {/* Documents Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {documents.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No documents uploaded yet</p>
            <p className="text-sm text-gray-400 mt-1">Upload some climate policy documents to get started</p>
          </div>
        ) : (
          documents.map((doc, index) => (
            <div key={index} className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <span className="text-sm font-medium text-gray-900">{doc.file_type || 'Document'}</span>
                </div>
                <div className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                  processed
                </div>
              </div>
              
              <h3 className="font-semibold text-gray-900 mb-2">{doc.filename}</h3>
              
              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <div className="flex justify-between">
                  <span>Text Chunks:</span>
                  <span className="font-medium">{doc.chunks}</span>
                </div>
                {doc.source && (
                  <div className="flex justify-between">
                    <span>Source:</span>
                    <span className="font-medium">{doc.source}</span>
                  </div>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                <button className="flex-1 bg-blue-50 text-blue-600 py-2 px-3 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium">
                  <Eye className="w-4 h-4 inline mr-1" />
                  View Details
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );

  const AnalyticsInterface = () => (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-gray-900">Analytics Dashboard</h2>
        <p className="text-gray-600">Monitor system performance and usage patterns</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Documents</p>
              <p className="text-2xl font-semibold text-gray-900">{stats?.documents_processed || 0}</p>
            </div>
            <div className="bg-blue-50 p-3 rounded-lg">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Chunks</p>
              <p className="text-2xl font-semibold text-gray-900">{stats?.total_chunks || 0}</p>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <BookOpen className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">System Status</p>
              <p className="text-2xl font-semibold text-gray-900">{stats?.status || 'Unknown'}</p>
            </div>
            <div className="bg-purple-50 p-3 rounded-lg">
              <CheckCircle className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Sessions</p>
              <p className="text-2xl font-semibold text-gray-900">1</p>
            </div>
            <div className="bg-orange-50 p-3 rounded-lg">
              <Zap className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-green-500 rounded-lg flex items-center justify-center">
                  <Globe className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">Climate Policy Intelligence</h1>
                  <p className="text-sm text-gray-600">AI-Powered Climate Document Analysis</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm">
                <div className={`w-2 h-2 rounded-full ${stats ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                <span className="text-gray-600">{stats ? 'System Online' : 'Loading...'}</span>
              </div>
              <button className="bg-gray-100 text-gray-700 p-2 rounded-lg hover:bg-gray-200">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="px-6">
          <div className="flex space-x-8">
            {[
              { id: 'chat', label: 'AI Assistant', icon: MessageSquare },
              { id: 'documents', label: 'Documents', icon: FileText },
              { id: 'analytics', label: 'Analytics', icon: BarChart3 }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1">
        {activeTab === 'chat' && (
          <div className="h-[calc(100vh-180px)]">
            <ChatInterface />
          </div>
        )}
        {activeTab === 'documents' && <DocumentsInterface />}
        {activeTab === 'analytics' && <AnalyticsInterface />}
      </main>
    </div>
  );
};

export default ClimateIntelligencePlatform;
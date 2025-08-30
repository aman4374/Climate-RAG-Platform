import React, { useState, useRef, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!currentQuestion.trim() || loading) return;

    const question = currentQuestion.trim();
    setCurrentQuestion('');
    setLoading(true);
    setError(null);

    // Add user message
    const userMessage = {
      type: 'user',
      content: question,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          max_results: 5
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from server');
      }

      const data = await response.json();

      // Add assistant message
      const assistantMessage = {
        type: 'assistant',
        content: data.answer,
        sources: data.sources || [],
        confidence_score: data.confidence_score,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      console.error('Error querying:', err);
      setError('Failed to get response. Please try again.');
      
      // Add error message
      const errorMessage = {
        type: 'assistant',
        content: 'Sorry, I encountered an error while processing your question. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: '#6b7280', marginTop: '50px' }}>
            <h3>Welcome to the Climate Policy Intelligence Platform</h3>
            <p>Ask questions about climate policies, IPCC reports, or any uploaded documents.</p>
            <div style={{ margin: '20px 0' }}>
              <p><strong>Example questions:</strong></p>
              <ul style={{ textAlign: 'left', display: 'inline-block' }}>
                <li>What are the key findings of the latest IPCC report?</li>
                <li>How do carbon pricing mechanisms work?</li>
                <li>What are the main climate adaptation strategies?</li>
                <li>What is the current status of renewable energy globally?</li>
              </ul>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} className={`message ${message.type}`}>
            <div className="message-header">
              {message.type === 'user' ? 'You' : 'Climate AI Assistant'}
            </div>
            <div className="message-content">
              {message.content}
            </div>
            
            {message.sources && message.sources.length > 0 && (
              <div className="sources">
                <div className="sources-title">Sources:</div>
                {message.sources.slice(0, 3).map((source, idx) => (
                  <div key={idx} className="source-item">
                    📄 {source.filename} 
                    {source.page_number && ` (Page ${source.page_number})`}
                    <span style={{ float: 'right' }}>
                      {(source.relevance_score * 100).toFixed(1)}% match
                    </span>
                  </div>
                ))}
                {message.confidence_score && (
                  <div style={{ fontSize: '0.8rem', color: '#6b7280', marginTop: '8px' }}>
                    Confidence: {(message.confidence_score * 100).toFixed(1)}%
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="message-header">Climate AI Assistant</div>
            <div className="message-content">
              <div className="loading">Analyzing documents and generating response...</div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        {error && (
          <div className="error" style={{ marginBottom: '10px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <input
              type="text"
              value={currentQuestion}
              onChange={(e) => setCurrentQuestion(e.target.value)}
              placeholder="Ask a question about climate policy..."
              disabled={loading}
            />
            <button 
              type="submit" 
              className="btn-primary"
              disabled={loading || !currentQuestion.trim()}
            >
              {loading ? 'Asking...' : 'Ask'}
            </button>
            {messages.length > 0 && (
              <button 
                type="button" 
                className="btn-secondary"
                onClick={clearChat}
                disabled={loading}
              >
                Clear
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
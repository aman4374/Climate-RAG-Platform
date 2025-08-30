import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

const DataSourceManager = ({ onUpdateComplete }) => {
  const [sources, setSources] = useState({});
  const [fetching, setFetching] = useState(false);
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSourcesStatus();
  }, []);

  const loadSourcesStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/sources/status`);
      if (response.ok) {
        const data = await response.json();
        setSources(data.sources);
      }
    } catch (err) {
      console.error('Error loading sources status:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchFromSources = async () => {
    setFetching(true);
    setMessage(null);

    try {
      const response = await fetch(`${API_BASE_URL}/fetch-sources`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({
          type: 'success',
          text: `Successfully fetched documents. Total chunks: ${data.stats.total_documents}`
        });
        if (onUpdateComplete) {
          onUpdateComplete();
        }
      } else {
        setMessage({
          type: 'error',
          text: data.detail || 'Failed to fetch from sources'
        });
      }
    } catch (err) {
      console.error('Fetch sources error:', err);
      setMessage({
        type: 'error',
        text: 'Failed to fetch from sources. Please try again.'
      });
    } finally {
      setFetching(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading sources...</div>;
  }

  return (
    <div className="data-sources-section">
      <h3 className="section-title">Climate Data Sources</h3>
      
      <div className="sources-list">
        {Object.entries(sources).map(([sourceName, sourceConfig]) => (
          <div key={sourceName} className="source-item">
            <div className="source-header">
              <span className="source-name">
                {sourceName.toUpperCase()}
              </span>
              <span className={`source-status ${sourceConfig.enabled ? 'enabled' : 'disabled'}`}>
                {sourceConfig.enabled ? '●' : '○'}
              </span>
            </div>
            <div className="source-info">
              Priority: {sourceConfig.priority} | 
              {sourceConfig.enabled ? ' Active' : ' Disabled'}
            </div>
          </div>
        ))}
      </div>

      <button 
        onClick={fetchFromSources}
        className="btn-primary"
        disabled={fetching}
        style={{ width: '100%', marginTop: '15px' }}
      >
        {fetching ? 'Fetching Documents...' : 'Fetch Latest Documents'}
      </button>

      {message && (
        <div className={message.type === 'success' ? 'success' : 'error'}>
          {message.text}
        </div>
      )}

      <div style={{ marginTop: '15px', fontSize: '0.8rem', color: '#6b7280' }}>
        <p><strong>Automated Sources:</strong></p>
        <ul style={{ margin: '5px 0', paddingLeft: '15px' }}>
          <li>IPCC Assessment Reports</li>
          <li>UNFCCC Documents & NDCs</li>
          <li>World Bank Climate Reports</li>
          <li>IEA Energy Outlooks</li>
          <li>Latest Climate Research (ArXiv)</li>
        </ul>
      </div>
    </div>
  );
};

export default DataSourceManager;
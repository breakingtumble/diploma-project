import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getMarketplaceConfigs, deleteMarketplaceConfig } from '../services/api';

const MarketplaceConfigs = () => {
  const [configs, setConfigs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchConfigs = async () => {
      try {
        const data = await getMarketplaceConfigs();
        setConfigs(data);
        setLoading(false);
      } catch (err) {
        if (err.message === 'Authentication failed' || err.message === 'No authentication token found') {
          navigate('/login');
        } else {
          setError(err.message || 'Failed to load configurations');
        }
        setLoading(false);
      }
    };
    fetchConfigs();
  }, [navigate]);

  const handleCreate = () => {
    navigate('/marketplace-configs/new');
  };

  const handleDelete = async (name) => {
    if (window.confirm(`Are you sure you want to delete configuration '${name}'?`)) {
      try {
        await deleteMarketplaceConfig(name);
        setConfigs((prev) => prev.filter((c) => c.name !== name));
      } catch (err) {
        alert(err.message || 'Failed to delete configuration');
      }
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}>
        <div>
          <h1 className="text-3xl font-extrabold text-gray-800 mb-1">Marketplace Configurations</h1>
          <p className="text-gray-600 text-base max-w-xl">
            Here you can <span className="font-semibold text-blue-700">edit</span>, <span className="font-semibold text-red-600">delete</span>, or <span className="font-semibold text-green-600">create</span> marketplace configurations. Click a configuration name to edit its details.
          </p>
        </div>
        <button
          onClick={handleCreate}
          style={{
            background: '#2563eb',
            color: '#fff',
            fontWeight: 700,
            fontSize: '1.1rem',
            padding: '0.75rem 2rem',
            borderRadius: 8,
            border: 'none',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
            cursor: 'pointer',
            transition: 'background 0.2s',
            marginRight: 48,
          }}
        >
          Create New Configuration
        </button>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24, width: '100%', alignItems: 'center' }}>
        {configs.length === 0 ? (
          <div className="text-gray-500 text-center py-8">No configurations found.</div>
        ) : (
          configs.map((config) => (
            <div
              key={config.name}
              style={{
                border: '2px solid #222',
                borderRadius: '20px',
                padding: '24px 40px',
                margin: '16px 0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                minWidth: '800px',
                maxWidth: '100%',
                background: '#fff',
                boxShadow: '0 2px 16px rgba(0,0,0,0.07)',
                cursor: 'pointer',
                transition: 'box-shadow 0.2s',
              }}
              onClick={() => navigate(`/marketplace-configs/${config.name}`)}
            >
              <span style={{ fontSize: '1.3em', fontWeight: 500, width: 350, flexShrink: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', display: 'inline-block', color: '#2563eb' }}>
                {config.name}
              </span>
              <span style={{ fontSize: '1em', color: '#888', marginLeft: 16, marginRight: 32, whiteSpace: 'nowrap' }}>
                Click to edit
              </span>
              <button
                onClick={e => { e.stopPropagation(); navigate(`/marketplace-configs/${config.name}`); }}
                style={{
                  border: '2px solid #2563eb',
                  borderRadius: '12px',
                  padding: '8px 24px',
                  fontSize: '1em',
                  background: 'white',
                  color: '#2563eb',
                  cursor: 'pointer',
                  fontWeight: 600,
                  marginRight: 12,
                  transition: 'background 0.2s, color 0.2s',
                }}
                title="Edit configuration"
              >
                Edit
              </button>
              <button
                onClick={e => { e.stopPropagation(); handleDelete(config.name); }}
                style={{
                  border: '2px solid #d32f2f',
                  borderRadius: '12px',
                  padding: '8px 18px',
                  fontSize: '1em',
                  background: 'white',
                  color: '#d32f2f',
                  cursor: 'pointer',
                  fontWeight: 600,
                  transition: 'background 0.2s, color 0.2s',
                }}
                title="Delete configuration"
              >
                &#128465;
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MarketplaceConfigs; 
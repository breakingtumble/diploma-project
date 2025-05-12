import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createMarketplaceConfig } from '../services/api';

const templateConfig = {
  name: "",
  fields: [
    {
      name: "",
      html_div_class: "",
      html_element_in_div_type: "",
      html_element_in_div_class: [""]
    },
    {
      name: "",
      html_div_class: "",
      html_element_in_div_type: "",
      html_element_in_div_class: [""]
    }
  ],
  marketplace_url: [""]
};

const NewMarketplaceConfig = () => {
  const navigate = useNavigate();
  const [jsonInput, setJsonInput] = useState(JSON.stringify(templateConfig, null, 2));
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      let parsedConfig;
      try {
        parsedConfig = JSON.parse(jsonInput);
      } catch (err) {
        setError('Invalid JSON format');
        setLoading(false);
        return;
      }
      await createMarketplaceConfig(parsedConfig);
      navigate('/marketplace-configs');
    } catch (err) {
      setError('Failed to create configuration');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', minHeight: '100vh', background: '#fff' }}>
      <div style={{ width: '100%', maxWidth: 900, margin: '0 auto', background: '#fff', borderRadius: 16, boxShadow: '0 4px 32px rgba(0,0,0,0.10)', padding: '2.5rem 2.5rem 2rem 2.5rem', marginTop: 32 }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: 24, color: '#222' }}>Create New Configuration</h1>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <label htmlFor="jsonInput" style={{ fontSize: '1.1rem', fontWeight: 500, color: '#444', marginBottom: 8 }}>
              Configuration JSON
            </label>
            <textarea
              id="jsonInput"
              value={jsonInput}
              onChange={(e) => setJsonInput(e.target.value)}
              style={{ width: '100%', minHeight: 320, maxHeight: 600, padding: 12, borderRadius: 8, border: '1.5px solid #bbb', fontFamily: 'monospace', fontSize: 16, resize: 'vertical', background: '#fafbfc' }}
              spellCheck="false"
            />
          </div>
          <div style={{ display: 'flex', gap: 20, marginTop: 16 }}>
            <button
              type="submit"
              disabled={loading}
              style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 8, padding: '0.75rem 2rem', fontWeight: 700, fontSize: '1.1rem', cursor: 'pointer', boxShadow: '0 2px 8px rgba(0,0,0,0.04)', opacity: loading ? 0.7 : 1 }}
            >
              {loading ? 'Creating...' : 'Create Configuration'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/marketplace-configs')}
              style={{ background: '#eee', color: '#222', border: 'none', borderRadius: 8, padding: '0.75rem 2rem', fontWeight: 700, fontSize: '1.1rem', cursor: 'pointer' }}
            >
              Cancel
            </button>
          </div>
          {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
        </form>
      </div>
    </div>
  );
};

export default NewMarketplaceConfig; 
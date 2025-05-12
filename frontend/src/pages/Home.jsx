import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function Home() {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const [marketplaces, setMarketplaces] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("/api/marketplace-configs/short")
      .then(res => res.json())
      .then(data => setMarketplaces(data));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await axios.post("/api/products/by_url", { url });
      navigate(`/product/${res.data.id}`, { state: res.data });
    } catch (err) {
      setError("Failed to fetch product. Please check the URL.");
    }
  };

  return (
    <div style={{ width: '100%', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={{ width: '100%', maxWidth: 600, textAlign: 'center', marginTop: 64 }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '2rem', color: '#222' }}>Parse product</h1>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <input
            type="text"
            placeholder="Enter product URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            style={{
              width: '100%',
              maxWidth: 500,
              padding: '1rem',
              fontSize: '1.2rem',
              border: '3px solid #222',
              borderRadius: 0,
              marginBottom: '1rem',
              outline: 'none',
              background: '#fff',
              transition: 'border 0.2s',
            }}
            required
          />
          <button type="submit" style={{
            padding: '0.7rem 2rem',
            fontSize: '1.1rem',
            background: '#0094FF',
            color: '#fff',
            border: 'none',
            borderRadius: 8,
            cursor: 'pointer',
            transition: 'background 0.2s',
          }}>Parse</button>
        </form>
        {error && <div style={{ color: '#d32f2f', marginTop: '1rem', fontWeight: 'bold' }}>{error}</div>}
      </div>
      {/* Marketplace cards horizontal scroll */}
      {marketplaces.length > 0 && (
        <>
          <div style={{
            width: '100%',
            textAlign: 'center',
            fontWeight: 600,
            fontSize: '1.3rem',
            color: '#222',
            marginTop: 80,
            marginBottom: 12,
            letterSpacing: 0.2,
          }}>
            Available marketplaces to parse
          </div>
          <div style={{
            width: '100%',
            overflowX: 'auto',
            padding: '0 0 16px 0',
          }}>
            <div style={{
              display: 'flex',
              flexDirection: 'row',
              gap: 24,
              minWidth: 400,
              padding: '0 30px',
              justifyContent: marketplaces.length < 6 ? 'center' : 'flex-start',
            }}>
              {marketplaces.map((m, idx) => (
                <div key={idx} style={{
                  minWidth: 260,
                  maxWidth: 320,
                  background: '#fff',
                  borderRadius: 12,
                  boxShadow: '0 2px 16px rgba(0,0,0,0.07)',
                  padding: '1.2rem 1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}>
                  <div style={{ fontWeight: 700, fontSize: '1.1rem', color: '#222', marginBottom: 16, textAlign: 'center' }}>{m.name}</div>
                  <a
                    href={m.marketplace_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'block',
                      background: '#0094FF',
                      color: '#fff',
                      padding: '0.7rem 1.2rem',
                      borderRadius: 8,
                      textDecoration: 'none',
                      fontWeight: 600,
                      textAlign: 'center',
                      marginTop: 15,
                      width: '100%',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                      transition: 'background 0.2s',
                    }}
                  >
                    Go to Marketplace
                  </a>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
} 
import { useNavigate } from "react-router-dom";

export default function NotFound() {
  const navigate = useNavigate();
  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <h1 style={{ fontSize: '4rem', color: '#0094FF', marginBottom: '1rem' }}>404</h1>
      <h2 style={{ fontSize: '2rem', color: '#222', marginBottom: '2rem' }}>Page Not Found</h2>
      <button
        onClick={() => navigate('/')}
        style={{
          background: '#0094FF',
          color: '#fff',
          border: 'none',
          borderRadius: 8,
          padding: '0.7rem 2rem',
          fontSize: '1.1rem',
          cursor: 'pointer',
        }}
      >
        Go Home
      </button>
    </div>
  );
} 
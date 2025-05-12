import { Link, useNavigate } from "react-router-dom";
import HomeIcon from "./HomeIcon";

function SubscriptionsIcon({ width = 32, height = 32 }) {
  // Bell icon for subscriptions
  return (
    <svg width={width} height={height} viewBox="0 0 24 24" fill="none">
      <path d="M12 22c1.1 0 2-.9 2-2h-4a2 2 0 0 0 2 2zm6-6V11c0-3.07-1.63-5.64-5-6.32V4a1 1 0 1 0-2 0v.68C7.63 5.36 6 7.92 6 11v5l-1.29 1.29A1 1 0 0 0 6 19h12a1 1 0 0 0 .71-1.71L18 16z" stroke="#0094FF" strokeWidth="2" fill="none"/>
    </svg>
  );
}

export default function Sidebar() {
  const navigate = useNavigate();
  return (
    <div style={{
      width: 50,
      minWidth: 50,
      maxWidth: 50,
      height: '100vh',
      background: '#fff',
      borderRight: '3px solid #bdbdbd',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'flex-start',
    }}>
      <Link to="/" style={{ margin: '2rem 0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <HomeIcon width={40} height={40} />
      </Link>
      <button
        onClick={() => navigate('/subscriptions')}
        style={{
          marginTop: '1rem',
          background: 'none',
          border: 'none',
          color: '#0094FF',
          cursor: 'pointer',
          padding: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
        title="My Subscriptions"
        aria-label="My Subscriptions"
      >
        <SubscriptionsIcon width={32} height={32} />
      </button>
      {/* More buttons can be added here */}
    </div>
  );
} 
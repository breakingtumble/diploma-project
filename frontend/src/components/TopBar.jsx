import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate, useLocation, Link } from "react-router-dom";

export default function TopBar() {
  const [username, setUsername] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Helper to get auth headers
  function getAuthHeaders() {
    const token = localStorage.getItem("access_token");
    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  }

  // Logout function
  function handleLogout() {
    localStorage.removeItem("access_token");
    setUsername(null);
    setIsAdmin(false);
    window.location.reload();
  }

  // Check auth status on mount and on every route change
  useEffect(() => {
    async function checkAuth() {
      try {
        const headers = getAuthHeaders();
        const res = await axios.get("/api/protected", {
          withCredentials: true,
          headers,
        });
        setUsername(res.data.username);
        setIsAdmin(res.data.role === "admin");
        console.log("User role:", res.data.role); // Debug log
      } catch (err) {
        console.error("Auth check error:", err); // Debug log
        setUsername(null);
        setIsAdmin(false);
      }
    }
    checkAuth();
  }, [location]);

  // Also poll every 10s in case of background login/logout
  useEffect(() => {
    async function checkAuth() {
      try {
        const headers = getAuthHeaders();
        const res = await axios.get("/api/protected", {
          withCredentials: true,
          headers,
        });
        setUsername(res.data.username);
        setIsAdmin(res.data.role === "admin");
        console.log("User role (poll):", res.data.role); // Debug log
      } catch (err) {
        console.error("Auth check error (poll):", err); // Debug log
        setUsername(null);
        setIsAdmin(false);
      }
    }
    const interval = setInterval(checkAuth, 10000);
    return () => clearInterval(interval);
  }, []);

  const navButtonStyle = {
    background: 'transparent',
    color: '#222',
    border: 'none',
    borderRadius: 8,
    padding: '0.5rem 1rem',
    fontSize: '1rem',
    cursor: 'pointer',
    textDecoration: 'none',
    marginRight: '1rem',
  };

  const activeNavButtonStyle = {
    ...navButtonStyle,
    color: '#0094FF',
    fontWeight: 'bold',
  };

  return (
    <div style={{
      width: '100%',
      minWidth: 0,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      height: 60,
      borderBottom: '1px solid #eee',
      background: '#fff',
      padding: '0 1rem',
      position: 'sticky',
      top: 0,
      zIndex: 10,
      boxSizing: 'border-box',
      maxWidth: '100vw',
      overflowX: 'auto',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 16,
      }}>
        <Link 
          to="/" 
          style={location.pathname === '/' ? activeNavButtonStyle : navButtonStyle}
        >
          My Home
        </Link>
        {username && (
          <Link 
            to="/subscriptions" 
            style={location.pathname === '/subscriptions' ? activeNavButtonStyle : navButtonStyle}
          >
            My Subscriptions
          </Link>
        )}
        {isAdmin && (
          <Link 
            to="/marketplace-configs" 
            style={location.pathname.startsWith('/marketplace-configs') ? activeNavButtonStyle : navButtonStyle}
          >
            Configurations
          </Link>
        )}
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 16,
      }}>
        {username ? (
          <>
            <span style={{ fontWeight: 500, color: '#222', whiteSpace: 'nowrap' }}>Welcome, {username}!</span>
            <button
              onClick={handleLogout}
              style={{
                background: '#eee',
                color: '#222',
                border: 'none',
                borderRadius: 8,
                padding: '0.5rem 1.5rem',
                fontSize: '1rem',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                maxWidth: '100%',
                marginLeft: 8,
              }}
            >
              Log out
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => navigate('/login')}
              style={{
                background: '#0094FF',
                color: '#fff',
                border: 'none',
                borderRadius: 8,
                padding: '0.5rem 1.5rem',
                fontSize: '1rem',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                maxWidth: '100%',
              }}
            >
              Log in
            </button>
            <button
              onClick={() => navigate('/register')}
              style={{
                background: 'transparent',
                color: '#0094FF',
                border: 'none',
                borderRadius: 8,
                padding: '0.5rem 1.5rem',
                fontSize: '1rem',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                maxWidth: '100%',
                textDecoration: 'underline',
              }}
            >
              Register
            </button>
          </>
        )}
      </div>
    </div>
  );
} 
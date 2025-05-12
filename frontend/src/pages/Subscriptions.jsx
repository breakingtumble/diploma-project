import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import SubscriptionCard from "../components/SubscriptionCard";

export default function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 6; // Number of items per page
  const navigate = useNavigate();
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const toastTimeout = useRef(null);

  // Redirect to login if not authenticated (in useEffect)
  useEffect(() => {
    if (!localStorage.getItem("access_token")) {
      navigate("/login");
    }
  }, [navigate]);

  // Optionally, prevent rendering if not authenticated
  if (!localStorage.getItem("access_token")) {
    return null;
  }

  useEffect(() => {
    async function fetchSubscriptions() {
      setLoading(true);
      setError("");
      const token = localStorage.getItem("access_token");
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        // First get the list of subscriptions
        const res = await axios.get("/api/subscriptions", {
          withCredentials: true,
          headers: { Authorization: `Bearer ${token}` },
          params: { page: currentPage, per_page: itemsPerPage }
        });
        
        // Then fetch the latest data for each subscription
        const updatedSubscriptions = await Promise.all(
          res.data.items.map(async (subscription) => {
            try {
              const productRes = await axios.get(`/api/products/${subscription.id}`);
              return productRes.data;
            } catch (err) {
              console.error(`Failed to fetch product ${subscription.id}:`, err);
              return subscription; // Fallback to original data if fetch fails
            }
          })
        );
        
        setSubscriptions(updatedSubscriptions);
        setTotalPages(Math.ceil(res.data.total / itemsPerPage));
      } catch (err) {
        if (err.response && (err.response.status === 401 || err.response.status === 403)) {
          navigate("/login");
        } else {
          setError("Failed to load subscriptions");
        }
      } finally {
        setLoading(false);
      }
    }
    fetchSubscriptions();
  }, [currentPage, navigate]);

  function showSuccessToast(message) {
    setToastMessage(message);
    setShowToast(true);
    if (toastTimeout.current) clearTimeout(toastTimeout.current);
    toastTimeout.current = setTimeout(() => setShowToast(false), 3000);
  }

  const handleUnsubscribe = async (id) => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }
    try {
      await axios.delete("/api/subscriptions", {
        withCredentials: true,
        headers: { Authorization: `Bearer ${token}` },
        params: { product_id: id }
      });
      setSubscriptions(subs => subs.filter(p => p.id !== id));
      showSuccessToast("Unsubscribed successfully!");
    } catch (err) {
      if (err.response && (err.response.status === 401 || err.response.status === 403)) {
        navigate("/login");
      } else {
        setError("Failed to unsubscribe");
      }
    }
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const renderPagination = () => {
    const pages = [];
    for (let i = 1; i <= totalPages; i++) {
      pages.push(
        <button
          key={i}
          onClick={() => handlePageChange(i)}
          style={{
            padding: '0.5rem 1rem',
            margin: '0 0.25rem',
            borderRadius: 8,
            border: currentPage === i ? '2px solid #0094FF' : '1.5px solid #ccc',
            background: currentPage === i ? '#e3f2fd' : '#fff',
            color: currentPage === i ? '#0094FF' : '#222',
            fontWeight: 600,
            cursor: 'pointer',
            fontSize: '1rem',
            transition: 'all 0.2s',
          }}
        >
          {i}
        </button>
      );
    }
    return pages;
  };

  function truncateName(name) {
    if (!name) return "";
    return name.length > 50 ? name.slice(0, 47) + '...' : name;
  }

  function getPriceInfo(product) {
    const { current_price, price_difference } = product;
    if (typeof current_price !== 'number' || typeof price_difference !== 'number') {
      return { percent: null, color: '#222', text: '' };
    }
    const oldPrice = current_price - price_difference;
    if (oldPrice === 0) {
      return { percent: null, color: '#222', text: '' };
    }
    const percent = ((price_difference / oldPrice) * 100).toFixed(2);
    let color = '#888';
    if (price_difference > 0) color = '#d32f2f';
    else if (price_difference < 0) color = '#388e3c';
    return {
      percent,
      color,
      text: price_difference === 0 ? 'No change' : (price_difference > 0 ? `+${percent}%` : `${percent}%`)
    };
  }

  // Error boundary for unexpected errors
  try {
    return (
      <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-start', gap: 24 }}>
        {/* Toast notification */}
        {showToast && (
          <div style={{
            position: 'fixed',
            top: 32,
            right: 32,
            background: '#222',
            color: '#fff',
            padding: '1rem 2rem',
            borderRadius: 12,
            boxShadow: '0 2px 16px rgba(0,0,0,0.12)',
            zIndex: 1000,
            fontSize: '1.1rem',
            fontWeight: 500,
          }}>
            {toastMessage}
          </div>
        )}
        <h1 style={{ fontSize: '2.5rem', marginBottom: 0, color: '#222', textAlign: 'left', width: '100%', maxWidth: 1200 }}>My Subscriptions</h1>
        <div style={{ width: '100%', maxWidth: 900, margin: '0 auto' }}>
          {/* Headings Row */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            fontWeight: 700,
            fontSize: '1.1rem',
            color: '#222',
            margin: '24px 0 8px 0',
            padding: '24px 40px',
            minWidth: '800px',
            width: '100%',
            boxSizing: 'border-box',
          }}>
            <div style={{ width: 350, flexShrink: 0 }}>Product Name</div>
            <div style={{ minWidth: 120, textAlign: 'right', fontVariantNumeric: 'tabular-nums', flexShrink: 0 }}>Price</div>
            <div style={{ width: 120 }}></div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 32, width: '100%' }}>
            {loading ? (
              <div>Loading...</div>
            ) : error ? (
              <div style={{ color: 'red' }}>{error}</div>
            ) : subscriptions.length === 0 ? (
              <div style={{ color: '#888', textAlign: 'center', width: '100%' }}>No subscriptions yet</div>
            ) : (
              subscriptions.map((product) => (
                <SubscriptionCard
                  key={product.id}
                  product={product}
                  onUnsubscribe={handleUnsubscribe}
                  onClick={() => navigate(`/product/${product.id}`, { state: product })}
                />
              ))
            )}
          </div>
        </div>
        {totalPages > 1 && (
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '2rem', gap: '0.5rem' }}>
            {renderPagination()}
          </div>
        )}
      </div>
    );
  } catch (err) {
    return <div style={{ color: 'red', padding: 40 }}>Unexpected error: {String(err)}</div>;
  }
} 
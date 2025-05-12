import { useLocation, useNavigate, useParams } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import axios from "axios";
import { useState, useEffect, useRef } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function Product() {
  const { state } = useLocation();
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(state || null);
  const [loading, setLoading] = useState(!state);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [priceHistory, setPriceHistory] = useState([]);
  const [period, setPeriod] = useState("1m");
  const [loadingChart, setLoadingChart] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const toastTimeout = useRef(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError("");
      try {
        // Fetch product data
        const productRes = await axios.get(`/api/products/${id}`);
        setProduct(productRes.data);

        // Fetch subscription status
        const token = localStorage.getItem("access_token");
        if (token) {
          try {
            const checkRes = await axios.get("/api/subscriptions/check", {
              withCredentials: true,
              headers: { Authorization: `Bearer ${token}` },
              params: { product_id: productRes.data.id },
            });
            setIsSubscribed(!!checkRes.data.subscribed);
          } catch (err) {
            setIsSubscribed(false);
          }
        }
      } catch (err) {
        setError("Product not found");
      } finally {
        setLoading(false);
      }
    }

    if (id) {
      fetchData();
    }
  }, [id]);

  useEffect(() => {
    async function fetchPriceHistory() {
      if (!product?.id) return;
      
      setLoadingChart(true);
      try {
        const res = await axios.get(`/api/products/${product.id}/price_history`, {
          params: { period },
        });
        setPriceHistory(res.data);
      } catch (err) {
        setPriceHistory([]);
      } finally {
        setLoadingChart(false);
      }
    }
    fetchPriceHistory();
  }, [product?.id, period]);

  function showSuccessToast(message) {
    setToastMessage(message);
    setShowToast(true);
    if (toastTimeout.current) clearTimeout(toastTimeout.current);
    toastTimeout.current = setTimeout(() => setShowToast(false), 3000);
  }

  async function handleSubscribe() {
    setError("");
    setSuccess("");
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }
    try {
      await axios.post(
        "/api/subscriptions",
        { product_id: product.id },
        {
          withCredentials: true,
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setSuccess("Subscribed successfully!");
      setIsSubscribed(true);
      showSuccessToast("Subscribed successfully!");
    } catch (err) {
      if (err.response?.status === 400 && err.response?.data?.detail === "Already subscribed") {
        // If already subscribed, update the UI state
        setIsSubscribed(true);
        setSuccess("Already subscribed");
        showSuccessToast("Already subscribed");
      } else if (err.response && (err.response.status === 401 || err.response.status === 403)) {
        navigate("/login");
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Subscription failed");
      }
    }
  }

  async function handleUnsubscribe() {
    setError("");
    setSuccess("");
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }
    try {
      await axios.delete("/api/subscriptions", {
        withCredentials: true,
        headers: { Authorization: `Bearer ${token}` },
        params: { product_id: product.id },
      });
      setSuccess("Unsubscribed successfully!");
      setIsSubscribed(false);
      showSuccessToast("Unsubscribed successfully!");
    } catch (err) {
      if (err.response && (err.response.status === 401 || err.response.status === 403)) {
        navigate("/login");
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Unsubscribe failed");
      }
    }
  }

  const periodOptions = [
    { label: "7d", value: "7d" },
    { label: "1m", value: "1m" },
    { label: "3m", value: "3m" },
    { label: "1y", value: "1y" },
    { label: "All", value: "all" },
  ];

  // Card style for both chart and info
  const cardStyle = {
    background: '#fff',
    borderRadius: 12,
    boxShadow: '0 2px 16px rgba(0,0,0,0.07)',
    padding: '1rem 2rem',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    minHeight: 300,
    height: '100%',
    flex: 1,
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;
  if (!product) return null;

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-start', gap: 24, position: 'relative' }}>
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
      {/* Product Name */}
      <h1 style={{
        fontSize: '2.5rem',
        marginBottom: 0,
        color: '#222',
        textAlign: 'left',
        width: '100%',
        maxWidth: 1200,
        marginTop: 48,
        marginRight: 220,
        marginLeft: 80,
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
      }}>
        {product.name}
      </h1>
      {/* Cards Row */}
      <div style={{ display: 'flex', alignItems: 'stretch', justifyContent: 'center', gap: 32, width: '100%', maxWidth: 1200 }}>
        {/* Price History Chart */}
        <div style={cardStyle}>
          <div style={{ marginBottom: 16, fontWeight: 600, fontSize: '1.2rem', color: '#222', alignSelf: 'flex-start' }}>Price History</div>
          <div style={{ display: 'flex', gap: 8, marginBottom: 16, alignSelf: 'flex-start' }}>
            {periodOptions.map(opt => (
              <button
                key={opt.value}
                onClick={() => setPeriod(opt.value)}
                style={{
                  padding: '0.3rem 1.1rem',
                  borderRadius: 8,
                  border: period === opt.value ? '2px solid #0094FF' : '1.5px solid #ccc',
                  background: period === opt.value ? '#e3f2fd' : '#fff',
                  color: period === opt.value ? '#0094FF' : '#222',
                  fontWeight: 600,
                  cursor: 'pointer',
                  fontSize: '1rem',
                  transition: 'all 0.2s',
                }}
              >
                {opt.label}
              </button>
            ))}
          </div>
          <div style={{ width: '100%', height: 300 }}>
            {loadingChart ? (
              <div style={{ textAlign: 'center', marginTop: 80 }}>Loading chart...</div>
            ) : priceHistory.length === 0 ? (
              <div style={{ textAlign: 'center', marginTop: 80, color: '#888' }}>No data</div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={priceHistory} margin={{ top: 10, right: 20, left: 0, bottom: 50 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date"
                    tickFormatter={d => d.slice(0, 10)}
                    angle={-35}
                    textAnchor="end"
                    interval={0}
                    minTickGap={20}
                  />
                  <YAxis 
                    dataKey="price"
                    domain={[(dataMin) => Math.floor(dataMin - 10), (dataMax) => Math.ceil(dataMax + 10)]}
                    type="number"
                    allowDecimals={true}
                    scale="linear"
                  />
                  <Tooltip 
                    formatter={(value) => [`${value} ${product.currency}`, 'Price']} 
                    labelFormatter={d => `Date: ${d.slice(0, 10)}`}
                  />
                  <Line type="monotone" dataKey="price" stroke="#0094FF" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 7 }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
        {/* Product Info Card */}
        <div style={{ ...cardStyle, alignItems: 'flex-start', justifyContent: 'flex-start', padding: '1rem 2rem', position: 'relative', display: 'flex', flexDirection: 'column' }}>
          {/* Subscribe/Unsubscribe button in top right of card */}
          <div style={{ position: 'absolute', top: 24, right: 32, zIndex: 2 }}>
            {!loading && isSubscribed ? (
              <button
                onClick={handleUnsubscribe}
                style={{
                  background: '#fff',
                  color: '#d32f2f',
                  border: '2px solid #d32f2f',
                  borderRadius: 8,
                  padding: '0.5rem 1.5rem',
                  fontSize: '1rem',
                  cursor: 'pointer',
                  fontWeight: 600,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
                }}
              >
                Unsubscribe
              </button>
            ) : !loading && (
              <button
                onClick={handleSubscribe}
                style={{
                  background: '#0094FF',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 8,
                  padding: '0.5rem 1.5rem',
                  fontSize: '1rem',
                  cursor: 'pointer',
                  fontWeight: 600,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
                }}
              >
                Subscribe
              </button>
            )}
          </div>
          {/* Product Details */}
          <div style={{ width: '100%', marginTop: '2rem' }}>
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.2rem', color: '#666', marginBottom: '0.5rem' }}>Current Price</h3>
              <div style={{ fontSize: '2rem', fontWeight: 600, color: '#222' }}>
                {product.current_price !== undefined && product.current_price !== null ? 
                  `${product.current_price.toFixed(1)} ${product.currency || ''}` : 
                  '—'}
              </div>
            </div>

            {product.predicted_price !== undefined && product.predicted_price !== null && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', color: '#666', marginBottom: '0.5rem' }}>Predicted Price (next 30 days)</h3>
                <div style={{ fontSize: '2rem', fontWeight: 600, color: '#222' }}>
                  {`${product.predicted_price.toFixed(1)} ${product.currency || ''}`}
                </div>
                {product.change_index !== undefined && product.change_index !== null && (
                  <div style={{ 
                    marginTop: '0.5rem', 
                    fontSize: '1.1rem', 
                    color: product.change_index > 0 ? '#2e7d32' : product.change_index < 0 ? '#d32f2f' : '#666',
                    fontWeight: 500
                  }}>
                    {product.change_index > 0 ? 'Price is likely to increase' : 
                     product.change_index < 0 ? 'Price is likely to decrease' : 
                     'Price is likely to remain stable'}
                  </div>
                )}
              </div>
            )}
          </div>
          <div style={{ width: '100%', marginTop: 'auto' }}>
            <a 
              href={product.url} 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ 
                display: 'block',
                background: '#0094FF',
                color: '#fff',
                padding: '0.75rem 1.5rem',
                borderRadius: 8,
                textDecoration: 'none',
                fontWeight: 600,
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                transition: 'all 0.2s',
                textAlign: 'center',
                maxWidth: '320px',
                width: '100%',
                margin: '24px auto 0 auto'
              }}
            >
              Go to Marketplace
            </a>
          </div>
          <div style={{ marginTop: '2rem', width: '100%' }}>
            {error && <span style={{ color: 'red', marginLeft: 8 }}>{error}</span>}
          </div>
        </div>
      </div>
    </div>
  );
} 
import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const [form, setForm] = useState({ username: "", password: "", email: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    setError("");
    try {
      await axios.post("/api/register/", form);
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    }
  };

  return (
    <div style={{ width: "100vw", height: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#f6f8fa" }}>
      <form onSubmit={handleSubmit} style={{ minWidth: 340, background: '#fff', borderRadius: 16, boxShadow: '0 4px 32px rgba(0,0,0,0.10)', padding: '2.5rem 2.5rem 2rem 2.5rem', display: "flex", flexDirection: "column", gap: 20, alignItems: 'stretch' }}>
        <h2 style={{ textAlign: 'center', marginBottom: 8, fontWeight: 700, fontSize: '2rem', color: '#222' }}>Register</h2>
        <input name="username" placeholder="Username" value={form.username} onChange={handleChange} required style={{ padding: '0.75rem 1rem', borderRadius: 8, border: '1.5px solid #ccc', fontSize: '1.1rem', outline: 'none', marginBottom: 4 }} />
        <input name="email" placeholder="Email" value={form.email} onChange={handleChange} required type="email" style={{ padding: '0.75rem 1rem', borderRadius: 8, border: '1.5px solid #ccc', fontSize: '1.1rem', outline: 'none', marginBottom: 4 }} />
        <input name="password" placeholder="Password" value={form.password} onChange={handleChange} required type="password" style={{ padding: '0.75rem 1rem', borderRadius: 8, border: '1.5px solid #ccc', fontSize: '1.1rem', outline: 'none', marginBottom: 4 }} />
        <button type="submit" style={{ background: '#0094FF', color: '#fff', border: 'none', borderRadius: 8, padding: '0.75rem', fontWeight: 700, fontSize: '1.1rem', cursor: 'pointer', marginTop: 8, marginBottom: 4, boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>Register</button>
        {error && <div style={{ color: "#d32f2f", textAlign: 'center', fontWeight: 500, marginTop: 4 }}>{error}</div>}
      </form>
    </div>
  );
} 
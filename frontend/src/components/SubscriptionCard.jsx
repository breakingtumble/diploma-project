import React from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function getColor(status) {
  if (status === "up") return "red";
  if (status === "down") return "green";
  return "grey";
}

function truncateName(name, maxLength = 30) {
  if (!name) return "No name";
  return name.length > maxLength ? name.slice(0, maxLength - 3) + "..." : name;
}

function getPercent(current_price, price_difference) {
  if (typeof current_price !== 'number' || typeof price_difference !== 'number') return "0";
  const oldPrice = current_price - price_difference;
  if (oldPrice === 0) return "0";
  return ((price_difference / oldPrice) * 100).toFixed(2);
}

export default function SubscriptionCard({ product, onUnsubscribe }) {
  const navigate = useNavigate();
  const percent = getPercent(product.current_price, product.price_difference);
  const percentText = `${product.price_difference > 0 ? "+" : ""}${percent}%`;
  const price = product.current_price !== undefined && product.current_price !== null ? 
    product.current_price.toFixed(2) : 
    "—";
  const currency = product.currency || "";
  const percentColor = getColor(product.status);

  // Color logic for percent badge based on deviation_string
  let percentTextColor = '#888';
  let percentBgColor = '#f0f0f0';
  if (product.deviation_string && product.deviation_string.toLowerCase().includes('risen')) {
    percentTextColor = '#d32f2f';
    percentBgColor = '#ffeaea';
  } else if (product.deviation_string && product.deviation_string.toLowerCase().includes('dropped')) {
    percentTextColor = '#388e3c';
    percentBgColor = '#eaffea';
  }

  const handleUnsubscribe = (e) => {
    e.stopPropagation();
    onUnsubscribe(product.id);
  };

  return (
    <div
      style={{
        border: "2px solid black",
        borderRadius: "20px",
        padding: "24px 40px",
        margin: "16px 0",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        minWidth: "800px",
        cursor: "pointer",
      }}
      onClick={() => navigate(`/product/${product.id}`, { state: product })}
    >
      <span style={{ fontSize: "1.3em", fontWeight: 500, width: 350, flexShrink: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', display: 'inline-block' }}>
        {truncateName(product.name)}
      </span>
      <span style={{ fontSize: "1.1em", minWidth: 120, textAlign: 'right', fontWeight: 600, flexShrink: 0 }}>
        {price} {currency}
      </span>
      <span
        style={{
          display: 'inline-block',
          minWidth: 60,
          padding: '6px 16px',
          borderRadius: 12,
          background: percentBgColor,
          color: percentTextColor,
          fontWeight: 600,
          fontSize: '1em',
          textAlign: 'center',
          marginRight: 0,
        }}
      >
        {percentText}
      </span>
      <button
        style={{
          border: "2px solid #d00",
          borderRadius: "12px",
          padding: "8px 24px",
          fontSize: "1.2em",
          background: "white",
          color: "#d00",
          cursor: "pointer",
        }}
        onClick={handleUnsubscribe}
      >
        Unsubscribe
      </button>
    </div>
  );
} 
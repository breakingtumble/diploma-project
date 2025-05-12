export const getMarketplaceConfigs = async () => {
  const token = localStorage.getItem('access_token');
  console.log('Token from localStorage:', token); // Debug log

  if (!token) {
    throw new Error('No authentication token found');
  }

  const response = await fetch('http://localhost:8000/api/marketplace-configurations', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    credentials: 'include'  // Include cookies if any
  });
  
  console.log('Response status:', response.status); // Debug log
  console.log('Response headers:', Object.fromEntries(response.headers.entries())); // Debug log
  
  if (response.status === 401) {
    throw new Error('Authentication failed');
  }
  if (!response.ok) {
    throw new Error('Failed to fetch configurations');
  }
  return response.json();
};

export const getMarketplaceConfig = async (configName) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('No authentication token found');
  }

  const response = await fetch(`http://localhost:8000/api/marketplace-configurations/${configName}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    credentials: 'include'
  });
  
  if (response.status === 401) {
    throw new Error('Authentication failed');
  }
  if (!response.ok) {
    throw new Error('Failed to fetch configuration');
  }
  return response.json();
};

export const updateMarketplaceConfig = async (configName, config) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('No authentication token found');
  }

  const response = await fetch(`http://localhost:8000/api/marketplace-configurations/${configName}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    credentials: 'include',
    body: JSON.stringify(config)
  });
  
  if (response.status === 401) {
    throw new Error('Authentication failed');
  }
  if (!response.ok) {
    throw new Error('Failed to update configuration');
  }
  return response.json();
};

export const createMarketplaceConfig = async (config) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('No authentication token found');
  }
  const response = await fetch('http://localhost:8000/api/marketplace-configurations', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    credentials: 'include',
    body: JSON.stringify(config)
  });
  if (response.status === 401) {
    throw new Error('Authentication failed');
  }
  if (!response.ok) {
    throw new Error('Failed to create configuration');
  }
  return response.json();
};

export const deleteMarketplaceConfig = async (configName) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('No authentication token found');
  }
  const response = await fetch(`http://localhost:8000/api/marketplace-configurations/${configName}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    credentials: 'include'
  });
  if (response.status === 401) {
    throw new Error('Authentication failed');
  }
  if (response.status === 404) {
    throw new Error('Configuration not found');
  }
  if (!response.ok) {
    throw new Error('Failed to delete configuration');
  }
  return true;
}; 
// apiUtils.js
const BASE_URL = 'https://production2.swancapital.in';

const getAuthToken = () => {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('User not authenticated');
  return token;
};

export const fetchApi = async (endpoint, options = {}) => {
  try {
    const token = getAuthToken();
    
    const response = await fetch(`${BASE_URL}/${endpoint}`, {
      method: options.method || 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
      ...options
    });

    if (!response.ok) {
      const errorMessage = await response.text();
      throw new Error(`Error fetching ${endpoint}: ${errorMessage}`);
    }

    const data = await response.json();
    return data;

  } catch (error) {
    console.error(`Error in ${options.method || 'GET'} ${endpoint}:`, error.message);
    throw error;
  }
};

// Helper functions for GET and POST
export const getData = async (endpoint, options = {}) => {
  return fetchApi(endpoint, { ...options, method: 'GET' });
};

export const postData = async (endpoint, data, options = {}) => {
  return fetchApi(endpoint, {
    ...options,
    method: 'POST',
    body: data
  });
};
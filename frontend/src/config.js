// API Configuration
// In production (Render), REACT_APP_API_URL should be set to backend URL
// In development, defaults to localhost
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Log API configuration (helpful for debugging deployment)
console.log('OmniQuant API Configuration:');
console.log('  Environment:', process.env.NODE_ENV);
console.log('  API Base URL:', API_BASE_URL);
console.log('  REACT_APP_API_URL:', process.env.REACT_APP_API_URL || 'not set');

export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/health`,
  METRICS: `${API_BASE_URL}/metrics`,
  SCAN: `${API_BASE_URL}/scan`,
  QUICK_SCAN: `${API_BASE_URL}/quick_scan`,
  OPPORTUNITIES: `${API_BASE_URL}/opportunities`,
  ALLOCATE: `${API_BASE_URL}/allocate`,
  STRESS_TEST: (id) => `${API_BASE_URL}/stress-test/${id}`,
  MARKET_IMPACT: `${API_BASE_URL}/market-impact`,
  ROOT: API_BASE_URL
};

export default API_BASE_URL;

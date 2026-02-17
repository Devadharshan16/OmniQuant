// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/health`,
  METRICS: `${API_BASE_URL}/metrics`,
  SCAN: `${API_BASE_URL}/scan`,
  QUICK_SCAN: `${API_BASE_URL}/quick_scan`,
  OPPORTUNITIES: `${API_BASE_URL}/opportunities`,
  ALLOCATE: `${API_BASE_URL}/allocate`,
  STRESS_TEST: (id) => `${API_BASE_URL}/stress-test/${id}`,
  ROOT: API_BASE_URL
};

export default API_BASE_URL;

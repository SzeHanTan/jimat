/**
 * API Client Configuration
 * 
 * Configures Axios instance with:
 * - Base URL pointing to FastAPI backend
 * - Default request/response interceptors
 * - Error handling
 */

import axios from 'axios';

// Get API base URL from environment or default to localhost:8000
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create Axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log errors in development
    if (process.env.NODE_ENV === 'development') {
      console.error('API Error:', error.response?.data || error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;

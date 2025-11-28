// =============================================================================
// API SERVICE
// =============================================================================
// Handles all API communication with the backend server.
// Provides functions for analysis, PII extraction, and username analysis.
// =============================================================================

/**
 * API Service
 * 
 * This module provides:
 * - Base API configuration
 * - Main analysis endpoint
 * - PII extraction endpoint
 * - Username analysis endpoint
 * - Health check endpoint
 * 
 * All functions return promises and handle errors consistently.
 */

// =============================================================================
// CONFIGURATION
// =============================================================================

// Base URL for API calls - uses environment variable or defaults to localhost
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Default request timeout in milliseconds
const REQUEST_TIMEOUT = 30000;

// =============================================================================
// ERROR CLASS
// =============================================================================

/**
 * Custom API Error class
 * 
 * Provides consistent error handling with status codes and messages
 */
class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Make a fetch request with timeout and error handling
 * 
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} Response data
 * @throws {ApiError} On request failure
 */
async function fetchWithTimeout(url, options = {}) {
  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    // Parse response
    const data = await response.json();

    // Check for error responses
    if (!response.ok) {
      throw new ApiError(
        data.detail || 'An error occurred',
        response.status,
        data
      );
    }

    return data;
  } catch (error) {
    clearTimeout(timeoutId);

    // Handle abort (timeout)
    if (error.name === 'AbortError') {
      throw new ApiError('Request timed out', 408);
    }

    // Re-throw API errors
    if (error instanceof ApiError) {
      throw error;
    }

    // Handle network errors
    throw new ApiError(
      'Network error - please check your connection',
      0
    );
  }
}

// =============================================================================
// API FUNCTIONS
// =============================================================================

/**
 * Check API health status
 * 
 * @returns {Promise<Object>} Health status object
 */
export async function checkHealth() {
  return fetchWithTimeout(`${API_BASE_URL}/health`);
}

/**
 * Perform main digital footprint analysis
 * 
 * @param {Object} params - Analysis parameters
 * @param {string} params.username - Username to analyze (required)
 * @param {string} [params.email] - Email address (optional)
 * @param {string} [params.phone] - Phone number (optional)
 * @param {string} [params.name] - Full name (optional)
 * @returns {Promise<Object>} Analysis results
 * 
 * @example
 * const results = await analyze({
 *   username: 'john_doe',
 *   email: 'john@example.com'
 * });
 */
export async function analyze({ username, email, phone, name }) {
  // Validate required field
  if (!username || !username.trim()) {
    throw new ApiError('Username is required', 400);
  }

  // Build request body
  const body = {
    username: username.trim(),
  };

  // Add optional fields if provided
  if (email && email.trim()) {
    body.email = email.trim();
  }
  if (phone && phone.trim()) {
    body.phone = phone.trim();
  }
  if (name && name.trim()) {
    body.name = name.trim();
  }

  return fetchWithTimeout(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * Extract PII from text
 * 
 * @param {string} text - Text to analyze
 * @returns {Promise<Object>} Extracted PII data
 * 
 * @example
 * const pii = await extractPII('Contact john@example.com');
 */
export async function extractPII(text) {
  if (!text || !text.trim()) {
    throw new ApiError('Text is required', 400);
  }

  return fetchWithTimeout(`${API_BASE_URL}/extract-pii`, {
    method: 'POST',
    body: JSON.stringify({ text: text.trim() }),
  });
}

/**
 * Analyze a username
 * 
 * @param {string} username - Username to analyze
 * @returns {Promise<Object>} Username analysis results
 * 
 * @example
 * const analysis = await analyzeUsername('john_doe');
 */
export async function analyzeUsername(username) {
  if (!username || !username.trim()) {
    throw new ApiError('Username is required', 400);
  }

  return fetchWithTimeout(`${API_BASE_URL}/analyze-username`, {
    method: 'POST',
    body: JSON.stringify({ username: username.trim() }),
  });
}

// =============================================================================
// DEFAULT EXPORT
// =============================================================================

const api = {
  checkHealth,
  analyze,
  extractPII,
  analyzeUsername,
  ApiError,
};

export default api;

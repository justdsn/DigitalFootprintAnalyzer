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
 * @param {string} params.identifier - Identifier to analyze (required)
 * @param {string} [params.identifier_type] - Optional type (auto-detected if not provided)
 * @returns {Promise<Object>} Analysis results
 * 
 * @example
 * const results = await analyze({
 *   identifier: 'john_doe'
 * });
 */
export async function analyze({ identifier, identifier_type }) {
  // Validate required field
  if (!identifier || !identifier.trim()) {
    throw new ApiError('Identifier is required', 400);
  }

  // Build request body - identifier_type is optional (backend auto-detects)
  const body = {
    identifier: identifier.trim(),
  };
  
  // Only include identifier_type if explicitly provided
  if (identifier_type) {
    body.identifier_type = identifier_type;
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
// SCAN OPTIONS API
// =============================================================================

/**
 * Get available scan options (Light Scan and Deep Scan)
 * 
 * @returns {Promise<Object>} Scan options with details about each scan type
 * 
 * @example
 * const options = await getScanOptions();
 * // Returns: {
 * //   light_scan: { name: "Light Scan", ... },
 * //   deep_scan: { name: "Deep Scan", requires_extension: true, ... }
 * // }
 */
export async function getScanOptions() {
  return fetchWithTimeout(`${API_BASE_URL}/scan-options`);
}

// =============================================================================
// LIGHT SCAN API
// =============================================================================

/**
 * Perform a light scan using Google Dorking to find profiles
 * 
 * @param {string} identifierType - Type of identifier (name, email, username)
 * @param {string} identifierValue - The identifier value to search for
 * @param {string} [location="Sri Lanka"] - Location filter for search
 * @returns {Promise<Object>} Light scan results grouped by platform
 * 
 * @example
 * const results = await lightScan('name', 'John Perera', 'Sri Lanka');
 * // Returns: {
 * //   success: true,
 * //   scan_type: "light",
 * //   total_results: 12,
 * //   platforms: [...],
 * //   ...
 * // }
 */
export async function lightScan(identifierType, identifierValue, location = "Sri Lanka") {
  if (!identifierValue || !identifierValue.trim()) {
    throw new ApiError('Identifier value is required', 400);
  }

  return fetchWithTimeout(`${API_BASE_URL}/light-scan`, {
    method: 'POST',
    body: JSON.stringify({
      identifier_type: identifierType,
      identifier_value: identifierValue.trim(),
      location: location
    }),
  });
}

// =============================================================================
// DEEP SCAN API
// =============================================================================

/**
 * Perform a deep scan (requires browser extension)
 * 
 * @param {string} identifierType - Type of identifier (name, email, username)
 * @param {string} identifierValue - The identifier value to search for
 * @returns {Promise<Object>} Deep scan response (placeholder - requires extension)
 * 
 * @example
 * const result = await deepScan('username', 'john_doe');
 * // Returns: {
 * //   success: false,
 * //   message: "Deep Scan requires the browser extension...",
 * //   extension_required: true,
 * //   ...
 * // }
 */
export async function deepScan(identifierType, identifierValue) {
  if (!identifierValue || !identifierValue.trim()) {
    throw new ApiError('Identifier value is required', 400);
  }

  return fetchWithTimeout(`${API_BASE_URL}/deep-scan`, {
    method: 'POST',
    body: JSON.stringify({
      identifier_type: identifierType,
      identifier_value: identifierValue.trim()
    }),
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
  transliterate,
  correlateProfiles,
  getScanOptions,
  lightScan,
  deepScan,
  ApiError,
};

export default api;


// =============================================================================
// TRANSLITERATION API (Phase 2)
// =============================================================================

/**
 * Transliterate Sinhala text to English variants
 * 
 * @param {string} text - Sinhala text to transliterate
 * @param {boolean} includeVariants - Whether to include spelling variants (default true)
 * @returns {Promise<Object>} Transliteration results
 * 
 * @example
 * const result = await transliterate('සුනිල් පෙරේරා');
 * // Returns: {
 * //   original: 'සුනිල් පෙරේරා',
 * //   is_sinhala: true,
 * //   transliterations: ['sunil perera'],
 * //   variants: ['suneel perera', ...]
 * // }
 */
export async function transliterate(text, includeVariants = true) {
  if (!text || !text.trim()) {
    throw new ApiError('Text is required', 400);
  }

  return fetchWithTimeout(`${API_BASE_URL}/transliterate`, {
    method: 'POST',
    body: JSON.stringify({ 
      text: text.trim(),
      include_variants: includeVariants 
    }),
  });
}


// =============================================================================
// CORRELATION API (Phase 2)
// =============================================================================

/**
 * Correlate profiles across platforms for impersonation detection
 * 
 * @param {Array<Object>} profiles - Array of platform profile objects
 * @returns {Promise<Object>} Correlation results
 * 
 * @example
 * const result = await correlateProfiles([
 *   { platform: 'facebook', username: 'john_doe', name: 'John Doe' },
 *   { platform: 'twitter', username: 'johndoe', name: 'John D' }
 * ]);
 * // Returns: {
 * //   overlaps: [...],
 * //   contradictions: [...],
 * //   impersonation_score: 15,
 * //   impersonation_level: 'low',
 * //   flags: [],
 * //   recommendations: [...]
 * // }
 */
export async function correlateProfiles(profiles) {
  if (!profiles || !Array.isArray(profiles) || profiles.length < 2) {
    throw new ApiError('At least 2 profiles are required', 400);
  }

  // Validate each profile has required fields
  for (const profile of profiles) {
    if (!profile.platform || !profile.username) {
      throw new ApiError('Each profile must have platform and username', 400);
    }
  }

  return fetchWithTimeout(`${API_BASE_URL}/correlate`, {
    method: 'POST',
    body: JSON.stringify({ profiles }),
  });
}

// =============================================================================
// BACKGROUND SERVICE WORKER
// =============================================================================
// Orchestrates deep scan operations across multiple social media platforms.
// Handles communication between content scripts, popup, and backend API.
// =============================================================================

import { sendToBackend, getApiUrl } from '../lib/api.js';

// =============================================================================
// CONSTANTS
// =============================================================================

const SUPPORTED_PLATFORMS = {
  facebook: {
    name: 'Facebook',
    emoji: '📘',
    searchUrlPattern: 'https://www.facebook.com/search/people/?q=',
    profileUrlPattern: /facebook\.com\/(?!search|login|help|groups|pages|marketplace|watch|gaming|events)([a-zA-Z0-9.]+)/
  },
  instagram: {
    name: 'Instagram',
    emoji: '📷',
    searchUrlPattern: 'https://www.instagram.com/',
    profileUrlPattern: /instagram\.com\/([a-zA-Z0-9._]+)/
  },
  linkedin: {
    name: 'LinkedIn',
    emoji: '💼',
    searchUrlPattern: 'https://www.linkedin.com/search/results/people/?keywords=',
    profileUrlPattern: /linkedin\.com\/in\/([a-zA-Z0-9-]+)/
  },
  x: {
    name: 'X (Twitter)',
    emoji: '𝕏',
    searchUrlPattern: 'https://x.com/search?q=',
    profileUrlPattern: /(?:x\.com|twitter\.com)\/([a-zA-Z0-9_]+)/
  }
};

// Configuration constants
const SCAN_CONFIG = {
  MAX_RETRIES: 2,
  RETRY_DELAYS: [3000, 6000], // Exponential backoff: 3s, 6s
  PAGE_LOAD_TIMEOUT: 20000,
  PLATFORM_EXTRACTION_TIMEOUT: 20000,
  CONTENT_SCRIPT_WAIT: 2000
};

// Error type constants
const ERROR_TYPES = {
  AUTH_REQUIRED: 'auth_required',
  TIMEOUT: 'timeout',
  BLOCKED: 'blocked',
  EXTRACTION_FAILED: 'extraction_failed'
};

// Scan state management
let currentScan = null;
let scanResults = {};

// Keep-alive mechanism to prevent service worker from going inactive
let keepAliveInterval = null;

function startKeepAlive() {
  if (keepAliveInterval) return; // Already running
  
  console.log('[Service Worker] Starting keep-alive');
  keepAliveInterval = setInterval(() => {
    // Ping runtime to keep worker alive
    chrome.runtime.getPlatformInfo(() => {
      console.log('[Service Worker] Keep-alive ping');
      if (chrome.runtime.lastError) {
        console.error('[Service Worker] Keep-alive error:', chrome.runtime.lastError);
      }
    });
  }, 20000); // Every 20 seconds
}

function stopKeepAlive() {
  if (keepAliveInterval) {
    console.log('[Service Worker] Stopping keep-alive');
    clearInterval(keepAliveInterval);
    keepAliveInterval = null;
  }
}

// =============================================================================
// MESSAGE HANDLERS
// =============================================================================

/**
 * Handle messages from content scripts and popup
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // Use async wrapper for proper response handling
  handleMessage(message, sender).then(sendResponse).catch(error => {
    console.error('Error handling message:', error);
    sendResponse({ success: false, error: error.message });
  });
  
  // Return true to indicate async response
  return true;
});

/**
 * Handle messages from web app (external)
 */
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  console.log('[Extension] Received message from web app:', message);
  
  if (message.action === 'checkExtension') {
    // Web app checking if extension is installed
    sendResponse({ 
      installed: true, 
      version: chrome.runtime.getManifest().version,
      ready: true
    });
    return true;
  }
  
  if (message.action === 'startDeepScan') {
    // Web app requesting a deep scan
    handleMessage(message, sender)
      .then(result => {
        sendResponse({ success: true, data: result });
      })
      .catch(error => {
        sendResponse({ success: false, error: error.message });
      });
    return true; // Will respond asynchronously
  }
  
  return false;
});

/**
 * Async message handler
 */
async function handleMessage(message, sender) {
  switch (message.action) {
    case 'startDeepScan':
      return await startDeepScan(message.data);
    
    case 'getScanStatus':
      return getScanStatus();
    
    case 'cancelScan':
      return cancelScan();
    
    case 'profileDataExtracted':
      return handleProfileData(message.data, sender);
    
    case 'searchResultsExtracted':
      return handleSearchResults(message.data, sender);
    
    case 'authenticationRequired':
      return handleAuthenticationRequired(message.data, sender);
    
    case 'contentScriptReady':
      return handleContentScriptReady(message.data, sender);
    
    case 'getApiUrl':
      return { success: true, url: await getApiUrl() };
    
    case 'sendToBackend':
      return await sendToBackend(message.endpoint, message.data);
    
    default:
      return { success: false, error: 'Unknown action' };
  }
}

// =============================================================================
// DEEP SCAN ORCHESTRATION
// =============================================================================

/**
 * Start a deep scan for the given identifier
 * @param {Object} data - Scan parameters
 * @param {string} data.identifierType - Type of identifier (name, email, username)
 * @param {string} data.identifierValue - The identifier value to search
 * @param {string[]} data.platforms - Platforms to scan
 * @returns {Object} Scan initiation result
 */
async function startDeepScan(data) {
  const { identifierType, identifierValue, platforms } = data;
  
  if (!identifierValue) {
    return { success: false, error: 'Identifier value is required' };
  }
  
  if (currentScan && currentScan.status === 'in_progress') {
    return { success: false, error: 'A scan is already in progress' };
  }
  
  // Initialize scan state
  currentScan = {
    id: generateScanId(),
    identifierType: identifierType || 'username',
    identifierValue,
    platforms: platforms || Object.keys(SUPPORTED_PLATFORMS),
    status: 'in_progress',
    startTime: Date.now(),
    progress: 0,
    currentPlatform: null,
    completedPlatforms: [],
    results: {}
  };
  
  scanResults = {};
  
  // Start keep-alive mechanism
  startKeepAlive();
  
  try {
    // Notify popup of scan start
    notifyPopup('scanStarted', { scanId: currentScan.id });
    
    // Start scanning each platform
    for (const platform of currentScan.platforms) {
      if (currentScan.status !== 'in_progress') {
        break; // Scan was cancelled
      }
      
      currentScan.currentPlatform = platform;
      await scanPlatform(platform, identifierValue, identifierType);
      currentScan.completedPlatforms.push(platform);
      currentScan.progress = (currentScan.completedPlatforms.length / currentScan.platforms.length) * 100;
      
      // Notify popup of progress
      notifyPopup('scanProgress', {
        platform,
        progress: currentScan.progress,
        completedPlatforms: currentScan.completedPlatforms
      });
    }
    
    // Finalize scan
    if (currentScan.status === 'in_progress') {
      currentScan.status = 'completed';
      currentScan.endTime = Date.now();
      currentScan.results = scanResults;
      
      // Send results to backend
      try {
        const backendResponse = await sendToBackend('/api/deep-scan/analyze', {
          scan_id: currentScan.id,
          identifier_type: currentScan.identifierType,
          identifier_value: currentScan.identifierValue,
          platforms_scanned: currentScan.completedPlatforms,
          results: scanResults,
          scan_duration_ms: currentScan.endTime - currentScan.startTime
        });
        
        currentScan.backendAnalysis = backendResponse;
      } catch (error) {
        console.error('Failed to send results to backend:', error);
        currentScan.backendError = error.message;
      }
      
      // Notify popup of completion
      notifyPopup('scanCompleted', {
        scanId: currentScan.id,
        results: currentScan.results,
        analysis: currentScan.backendAnalysis
      });
    }
    
  } finally {
    // Always stop keep-alive when scan ends
    stopKeepAlive();
  }
  
  return { success: true, scanId: currentScan.id };
}

/**
 * Scan a specific platform for the identifier
 * @param {string} platform - Platform key
 * @param {string} identifier - Value to search
 * @param {string} identifierType - Type of identifier
 * @param {number} retryCount - Current retry attempt (default 0)
 */
async function scanPlatform(platform, identifier, identifierType, retryCount = 0) {
  const platformConfig = SUPPORTED_PLATFORMS[platform];
  if (!platformConfig) return;
  
  console.log(`[Scan] Starting scan for ${platform} with identifier: ${identifier} (attempt ${retryCount + 1})`);
  
  // Build search query based on identifier type
  let searchQuery = identifier;
  if (identifierType === 'email') {
    // Extract username part of email for searching
    searchQuery = identifier.split('@')[0];
  }
  // Note: Names will be URL-encoded when building the search URL
  
  // Initialize platform results (if first attempt)
  if (retryCount === 0) {
    scanResults[platform] = {
      platform: platformConfig.name,
      emoji: platformConfig.emoji,
      status: 'scanning',
      profiles: [],
      searchResults: [],
      errors: [],
      startTime: Date.now()
    };
    
    // Notify web app that platform scan started
    notifyWebApp('platformStarted', {
      platform: platformConfig.name,
      platformKey: platform,
      emoji: platformConfig.emoji
    });
    
    // Notify popup about platform scan start
    notifyPopup('platformScanStarted', {
      platform,
      platformName: platformConfig.name,
      emoji: platformConfig.emoji
    });
  }
  
  let tab = null;
  
  try {
    // Determine URL and navigation strategy based on platform
    let targetUrl;
    let needsInteractiveSearch = false;
    
    if (platform === 'instagram') {
      // Instagram requires interactive search
      targetUrl = 'https://www.instagram.com/';
      needsInteractiveSearch = true;
    } else {
      // Other platforms support direct search URLs
      targetUrl = platformConfig.searchUrlPattern + encodeURIComponent(searchQuery);
    }
    
    console.log(`[Scan] Opening tab for ${platform}: ${targetUrl}`);
    
    // Create new tab in background (not active)
    tab = await chrome.tabs.create({ 
      url: targetUrl, 
      active: false 
    });
    
    console.log(`[Scan] Tab created for ${platform}, ID: ${tab.id}`);
    
    // Wait for page to load using tab listener
    const pageLoaded = await waitForTabLoad(tab.id, SCAN_CONFIG.PAGE_LOAD_TIMEOUT);
    
    if (!pageLoaded) {
      throw new Error('Page load timeout');
    }
    
    // Additional wait for content script injection
    await new Promise(resolve => setTimeout(resolve, SCAN_CONFIG.CONTENT_SCRIPT_WAIT));
    
    // Check authentication status
    try {
      const authCheck = await chrome.tabs.sendMessage(tab.id, {
        action: 'checkAuthentication'
      });
      
      if (!authCheck.authenticated) {
        const errorData = {
          error_type: ERROR_TYPES.AUTH_REQUIRED,
          message: `You are not logged into ${platformConfig.name}`,
          suggestion: `Please log into ${platformConfig.name} and try again`,
          loginUrl: authCheck.loginUrl || platformConfig.searchUrlPattern.split('/search')[0]
        };
        
        scanResults[platform].status = ERROR_TYPES.AUTH_REQUIRED;
        scanResults[platform].errors.push(errorData);
        
        console.log(`[Scan] Authentication required for ${platform}`);
        return; // Don't retry auth errors
      }
    } catch (authError) {
      console.warn(`[Scan] Could not check authentication for ${platform}:`, authError);
      // Continue anyway - might still work
    }
    
    // Handle Instagram's interactive search
    if (needsInteractiveSearch) {
      try {
        console.log(`[Scan] Performing interactive search on ${platform}`);
        await chrome.tabs.sendMessage(tab.id, {
          action: 'performSearch',
          query: searchQuery
        });
        
        // Wait for search to complete
        await new Promise(resolve => setTimeout(resolve, 3000));
      } catch (searchError) {
        console.error(`[Scan] Interactive search failed for ${platform}:`, searchError);
        throw new Error(`Interactive search failed: ${searchError.message}`);
      }
    } else {
      // Send message to content script to extract results
      try {
        console.log(`[Scan] Sending extraction message to tab ${tab.id}`);
        await chrome.tabs.sendMessage(tab.id, {
          action: 'extractSearchResults',
          query: identifier,
          identifierType
        });
      } catch (msgError) {
        console.error(`[Scan] Failed to send message to ${platform} tab:`, msgError);
        throw new Error(`Failed to communicate with content script: ${msgError.message}`);
      }
    }
    
    // Wait for content script to extract and send results
    await waitForPlatformResults(platform, SCAN_CONFIG.PLATFORM_EXTRACTION_TIMEOUT);
    
    // Check if extraction was successful
    const hasAuthError = scanResults[platform].errors.some(e => 
      typeof e === 'object' && e.error_type === ERROR_TYPES.AUTH_REQUIRED
    );
    
    if (hasAuthError) {
      // Don't retry auth errors - user needs to log in
      return;
    }
    
    // Check if we have retryable errors
    const hasRetryableError = scanResults[platform].errors.some(e => 
      typeof e === 'object' && 
      (e.error_type === ERROR_TYPES.EXTRACTION_FAILED || e.error_type === ERROR_TYPES.TIMEOUT)
    );
    
    if (scanResults[platform].status === 'timeout' || 
        (hasRetryableError && retryCount < SCAN_CONFIG.MAX_RETRIES)) {
      throw new Error('Extraction failed or timed out');
    }
    
  } catch (error) {
    console.error(`[Scan] Error scanning ${platform} (attempt ${retryCount + 1}):`, error);
    
    const errorData = {
      error_type: ERROR_TYPES.EXTRACTION_FAILED,
      message: `Failed to scan ${platformConfig.name}: ${error.message}`,
      suggestion: 'Please check your internet connection and try again'
    };
    
    // Retry logic
    if (retryCount < SCAN_CONFIG.MAX_RETRIES && error.message !== 'Page load timeout') {
      const delay = SCAN_CONFIG.RETRY_DELAYS[retryCount];
      console.log(`[Scan] Retrying ${platform} in ${delay}ms...`);
      
      // Close the current tab
      if (tab && tab.id) {
        try {
          await chrome.tabs.remove(tab.id);
        } catch (closeError) {
          console.warn(`[Scan] Could not close tab for retry:`, closeError);
        }
      }
      
      // Wait before retry
      await new Promise(resolve => setTimeout(resolve, delay));
      
      // Retry the scan
      return await scanPlatform(platform, identifier, identifierType, retryCount + 1);
    } else {
      // Max retries reached or non-retryable error
      scanResults[platform].status = 'error';
      scanResults[platform].errors.push(errorData);
    }
  } finally {
    // Always close the tab after extraction, even if there was an error
    if (tab && tab.id) {
      try {
        await chrome.tabs.remove(tab.id);
        console.log(`[Scan] Closed tab for ${platform}`);
      } catch (closeError) {
        console.warn(`[Scan] Could not close tab for ${platform}:`, closeError);
      }
    }
  }
  
  // Mark as completed if still scanning
  if (scanResults[platform].status === 'scanning') {
    scanResults[platform].status = 'completed';
  }
  
  // Calculate duration
  scanResults[platform].endTime = Date.now();
  scanResults[platform].duration = scanResults[platform].endTime - scanResults[platform].startTime;
  
  // Notify web app that platform scan completed
  notifyWebApp('platformCompleted', {
    platform: platformConfig.name,
    platformKey: platform,
    emoji: platformConfig.emoji,
    count: scanResults[platform].profiles.length + scanResults[platform].searchResults.length,
    duration: scanResults[platform].duration,
    status: scanResults[platform].status,
    errors: scanResults[platform].errors
  });
  
  // Notify popup about platform scan completion
  notifyPopup('platformScanCompleted', {
    platform,
    platformName: platformConfig.name,
    emoji: platformConfig.emoji,
    status: scanResults[platform].status,
    profilesFound: scanResults[platform].profiles.length,
    searchResultsFound: scanResults[platform].searchResults.length,
    errors: scanResults[platform].errors
  });
  
  console.log(`[Scan] Completed ${platform} scan in ${scanResults[platform].duration}ms`);
}

/**
 * Wait for tab to complete loading
 * @param {number} tabId - Tab ID
 * @param {number} timeout - Maximum wait time in ms
 * @returns {Promise<boolean>} True if loaded, false if timeout
 */
function waitForTabLoad(tabId, timeout = 20000) {
  return new Promise((resolve) => {
    const startTime = Date.now();
    let isResolved = false;
    
    const listener = (updatedTabId, changeInfo, tab) => {
      if (updatedTabId === tabId && changeInfo.status === 'complete') {
        if (!isResolved) {
          isResolved = true;
          chrome.tabs.onUpdated.removeListener(listener);
          console.log(`[Scan] Tab ${tabId} loaded successfully`);
          resolve(true);
        }
      }
    };
    
    chrome.tabs.onUpdated.addListener(listener);
    
    // Timeout fallback
    setTimeout(() => {
      if (!isResolved) {
        isResolved = true;
        chrome.tabs.onUpdated.removeListener(listener);
        console.warn(`[Scan] Tab ${tabId} load timeout after ${timeout}ms`);
        resolve(false);
      }
    }, timeout);
    
    // Also check if tab is already complete
    chrome.tabs.get(tabId, (tab) => {
      if (chrome.runtime.lastError) {
        if (!isResolved) {
          isResolved = true;
          chrome.tabs.onUpdated.removeListener(listener);
          resolve(false);
        }
        return;
      }
      
      if (tab.status === 'complete' && !isResolved) {
        isResolved = true;
        chrome.tabs.onUpdated.removeListener(listener);
        console.log(`[Scan] Tab ${tabId} was already loaded`);
        resolve(true);
      }
    });
  });
}

/**
 * Wait for platform results with timeout
 */
function waitForPlatformResults(platform, timeout) {
  return new Promise((resolve) => {
    const startTime = Date.now();
    
    const checkResults = () => {
      const elapsed = Date.now() - startTime;
      
      if (scanResults[platform]?.status !== 'scanning') {
        console.log(`[Scan] ${platform} results received after ${elapsed}ms`);
        resolve();
        return;
      }
      
      if (elapsed > timeout) {
        console.warn(`[Scan] ${platform} timed out after ${elapsed}ms`);
        scanResults[platform].status = 'timeout';
        scanResults[platform].errors.push(`Extraction timed out after ${timeout}ms`);
        resolve();
        return;
      }
      
      setTimeout(checkResults, 500);
    };
    
    checkResults();
  });
}

/**
 * Handle extracted profile data from content scripts
 */
function handleProfileData(data, sender) {
  const { platform, profile } = data;
  
  if (!scanResults[platform]) {
    scanResults[platform] = {
      platform: SUPPORTED_PLATFORMS[platform]?.name || platform,
      emoji: SUPPORTED_PLATFORMS[platform]?.emoji || '🔍',
      status: 'completed',
      profiles: [],
      searchResults: [],
      errors: []
    };
  }
  
  scanResults[platform].profiles.push(profile);
  scanResults[platform].status = 'completed';
  
  return { success: true };
}

/**
 * Handle extracted search results from content scripts
 */
function handleSearchResults(data, sender) {
  const { platform, results } = data;
  
  if (!scanResults[platform]) {
    scanResults[platform] = {
      platform: SUPPORTED_PLATFORMS[platform]?.name || platform,
      emoji: SUPPORTED_PLATFORMS[platform]?.emoji || '🔍',
      status: 'completed',
      profiles: [],
      searchResults: [],
      errors: []
    };
  }
  
  scanResults[platform].searchResults = results;
  scanResults[platform].status = 'completed';
  
  return { success: true };
}

/**
 * Handle authentication required notification from content scripts
 */
function handleAuthenticationRequired(data, sender) {
  const { platform, platformName, loginUrl, message } = data;
  
  console.log(`[Auth] Authentication required for ${platformName}`);
  
  if (scanResults[platform]) {
    scanResults[platform].status = 'auth_required';
    scanResults[platform].errors.push({
      error_type: 'auth_required',
      message: message || `Please log into ${platformName}`,
      suggestion: `Click here to log in to ${platformName}`,
      loginUrl: loginUrl
    });
  }
  
  // Notify popup and web app
  notifyPopup('authenticationRequired', {
    platform,
    platformName,
    loginUrl,
    message
  });
  
  notifyWebApp('authenticationRequired', {
    platform,
    platformName,
    loginUrl,
    message
  });
  
  return { success: true };
}

/**
 * Handle content script readiness signal
 */
function handleContentScriptReady(data, sender) {
  const { platform, platformName, authenticated, url, loginUrl } = data;
  
  console.log(`[ContentScript] ${platformName} content script ready. Authenticated: ${authenticated}`);
  
  if (!authenticated && loginUrl) {
    console.log(`[ContentScript] ${platformName} requires authentication: ${loginUrl}`);
  }
  
  return { success: true };
}

// =============================================================================
// SCAN STATUS & CONTROL
// =============================================================================

/**
 * Get current scan status
 */
function getScanStatus() {
  if (!currentScan) {
    return { success: true, status: 'idle', scan: null };
  }
  
  return {
    success: true,
    status: currentScan.status,
    scan: {
      id: currentScan.id,
      identifierType: currentScan.identifierType,
      identifierValue: currentScan.identifierValue,
      platforms: currentScan.platforms,
      progress: currentScan.progress,
      currentPlatform: currentScan.currentPlatform,
      completedPlatforms: currentScan.completedPlatforms,
      results: currentScan.status === 'completed' ? currentScan.results : null,
      analysis: currentScan.backendAnalysis
    }
  };
}

/**
 * Cancel the current scan
 */
function cancelScan() {
  if (!currentScan || currentScan.status !== 'in_progress') {
    return { success: false, error: 'No scan in progress' };
  }
  
  currentScan.status = 'cancelled';
  currentScan.endTime = Date.now();
  
  // Stop keep-alive when scan is cancelled
  stopKeepAlive();
  
  notifyPopup('scanCancelled', { scanId: currentScan.id });
  
  return { success: true };
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Generate a unique scan ID
 */
function generateScanId() {
  return 'DS-' + Date.now().toString(36).toUpperCase() + Math.random().toString(36).substring(2, 7).toUpperCase();
}

/**
 * Send notification to popup and web app
 */
function notifyPopup(event, data) {
  // Send to extension popup
  chrome.runtime.sendMessage({ event, data }).catch(() => {
    // Popup might be closed, ignore error
  });
  
  // Send to web app content script
  chrome.tabs.query({ url: ['http://localhost:3000/*', 'http://localhost:*/*'] }).then(tabs => {
    tabs.forEach(tab => {
      chrome.tabs.sendMessage(tab.id, { event, data }).catch(() => {
        // Content script might not be loaded, ignore error
      });
    });
  });
}

/**
 * Send notification specifically to web app
 */
function notifyWebApp(event, data) {
  // Send to web app content script
  chrome.tabs.query({ url: ['http://localhost:3000/*', 'http://localhost:*/*'] }).then(tabs => {
    tabs.forEach(tab => {
      chrome.tabs.sendMessage(tab.id, {
        action: 'webappEvent',
        event,
        data
      }).catch((error) => {
        console.warn(`Could not send event to web app tab ${tab.id}:`, error.message);
      });
    });
  }).catch(err => {
    console.warn('Could not query web app tabs:', err);
  });
}

// =============================================================================
// EXTENSION LIFECYCLE
// =============================================================================

/**
 * Handle extension installation/update
 */
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('Digital Footprint Analyzer extension installed');
    // Set default settings
    chrome.storage.local.set({
      apiUrl: 'http://localhost:8000',
      enableNotifications: true
    });
  } else if (details.reason === 'update') {
    console.log('Digital Footprint Analyzer extension updated to version', chrome.runtime.getManifest().version);
  }
});

/**
 * Keep service worker alive during scans
 */
chrome.alarms.create('keepAlive', { periodInMinutes: 0.5 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'keepAlive' && currentScan?.status === 'in_progress') {
    console.log('Keeping service worker alive during scan');
  }
});
